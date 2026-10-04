"""Grade a frozen run against nflverse actuals. Writes grade.json + grade_players.csv beside the manifest.

Players are joined on (normalized name, team). Only players with a recorded snap in a FINAL game are graded.
Metric definitions mirror compare_bt.py (the backtest), so live and backtest numbers are comparable.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

from paths import NFLV
from load import norm_name

NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
STATS = ["completions", "passing_yards", "passing_tds", "rushing_yards", "carries", "receptions",
         "receiving_yards", "rushing_tds", "receiving_tds"]
# (name, projection col, actual col, mask on projection frame, low/high quantile cols)
MARKETS = [
    ("rec_yds", "rec_yds_mean", "receiving_yards", lambda P: (P.rec_mean >= 1.0) & (P.pos != "QB"), ("rec_yds_p25", "rec_yds_p75")),
    ("rec", "rec_mean", "receptions", lambda P: (P.rec_mean >= 1.0) & (P.pos != "QB"), ("rec_p25", "rec_p75")),
    ("rush_yds", "rush_yds_mean", "rushing_yards", lambda P: (P.rush_att_mean >= 4) & (P.pos != "QB"), ("rush_yds_p25", "rush_yds_p75")),
    ("pass_yds", "pass_yds_mean", "passing_yards", lambda P: P.pass_yds_mean >= 100, ("pass_yds_p25", "pass_yds_p75")),
    ("pass_cmp", "pass_cmp_mean", "completions", lambda P: P.pass_yds_mean >= 100, ("pass_cmp_p25", "pass_cmp_p75")),
    ("pass_td", "pass_td_mean", "passing_tds", lambda P: P.pass_yds_mean >= 100, ("pass_td_p25", "pass_td_p75")),
]


def _actuals(season, week):
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet")
    st = st[(st.season_type == "REG") & (st.week == week)].copy()
    st["team"] = st.team.replace(NV2T)
    st["nkey"] = st.player_display_name.map(norm_name)
    sn = pd.read_parquet(NFLV + f"snap_counts_{season}.parquet")
    sn = sn[(sn.game_type == "REG") & (sn.week == week) & ((sn.offense_snaps > 0) | (sn.st_snaps > 0) | (sn.defense_snaps > 0))].copy()
    sn["team"] = sn.team.replace(NV2T)
    sn["nkey"] = sn.player.map(norm_name)
    g = pd.read_parquet(NFLV + "games.parquet")
    g = g[(g.season == season) & (g.week == week) & (g.game_type == "REG")].copy()
    g["home_team"] = g.home_team.replace(NV2T)
    g["away_team"] = g.away_team.replace(NV2T)
    final = g[g.home_score.notna()]
    return st, sn, final


def grade(run_dir):
    man = json.load(open(os.path.join(run_dir, "manifest.json")))
    season, week = man["season"], man["week"]
    P = pd.read_csv(os.path.join(run_dir, "projections.csv"))
    P["nkey"] = P.player.map(norm_name)
    st, sn, final = _actuals(season, week)
    final_games = set(zip(final.away_team, final.home_team))
    P = P[[tuple(x.split("@")) in final_games for x in P.game]].copy()
    if P.empty:
        return {"run_id": man["run_id"], "status": "no_final_games", "games_graded": 0}
    played = set(zip(sn.nkey, sn.team))
    P = P[[(a, b) in played for a, b in zip(P.nkey, P.team)]].copy()
    P = P.merge(st[["nkey", "team"] + STATS], on=["nkey", "team"], how="left")
    for c in STATS:
        P[c] = P[c].fillna(0)
    P["actual_td"] = ((P.rushing_tds + P.receiving_tds) >= 1).astype(float)
    out = {"run_id": man["run_id"], "season": season, "week": week, "track": man["track"],
           "status": "graded", "games_graded": int(len(final_games & set(tuple(x.split("@")) for x in P.game))), "markets": {}}
    for name, pc, ac, mask, (lo, hi) in MARKETS:
        d = P[mask(P)]
        if d.empty:
            continue
        err = d[pc] - d[ac]
        inside = ((d[ac] >= d[lo]) & (d[ac] <= d[hi])).mean()
        out["markets"][name] = dict(n=int(len(d)), mae=float(err.abs().mean()), bias=float(err.mean()), p25_p75_coverage=float(inside))
    td = P[(P.pos != "QB") & (P.any_td_pct >= 0.03)]
    if len(td):
        p = np.clip(td.any_td_pct, 0.01, 0.99)
        a = td.actual_td
        out["anytime_td"] = dict(n=int(len(td)), brier=float(np.mean((p - a) ** 2)),
                                 log_loss=float(-np.mean(a * np.log(p) + (1 - a) * np.log(1 - p))),
                                 sum_projected=float(p.sum()), actual_scorers=float(a.sum()))
    env_path = os.path.join(run_dir, "w4_game_environment.csv")
    if os.path.exists(env_path):
        env = pd.read_csv(env_path).merge(final[["away_team", "home_team", "away_score", "home_score"]],
                                          left_on=["away", "home"], right_on=["away_team", "home_team"])
        if len(env):
            ph = np.array([r[f"{r['home']}_pts_mean"] for _, r in env.iterrows()])
            pa = np.array([r[f"{r['away']}_pts_mean"] for _, r in env.iterrows()])
            out["team_points"] = dict(
                n_games=int(len(env)),
                rmse=float(np.sqrt(np.mean(np.r_[(pa - env.away_score) ** 2, (ph - env.home_score) ** 2]))),
                total_bias=float(np.mean((ph + pa) - (env.home_score + env.away_score))),
                winner_hit_rate=float(np.mean(((ph > pa) == (env.home_score > env.away_score)))))
    P.to_csv(os.path.join(run_dir, "grade_players.csv"), index=False)
    with open(os.path.join(run_dir, "grade.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    print(json.dumps(grade(sys.argv[1]), indent=1))
