"""Multi-season weeks 4-12 candidate-vs-baseline comparison on the promotion-rule metrics (contracts/weekly/grading.v0.1.yaml).

Usage: APEX_OUT=<dir holding bt_{season}_w{week}_{tag}.pkl and btteam_*> python eval_candidate.py BASE_TAG CAND_TAG [CAND_TAG ...]
Backtests come from bt_variant.sh <tag> (env knobs pass through, e.g. APEX_VAC=1). Prints, per tag and per season: rec_yds MAE, rec MAE, rush_yds MAE, TD log loss, team RMSE;
then the candidate minus baseline deltas, the rush yards ratio by projection tier, and the metrics restricted to players whose team had an Out skill player (the case a role change targets).
Players: projected active, with a recorded offensive snap in the game (same scope as grade.py). Negative delta = better.
"""
import sys
import numpy as np
import pandas as pd
import warnings
from load import norm_name
from paths import OUT, NFLV

warnings.filterwarnings("ignore")
NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
SEASONS = (2023, 2024, 2025)
tags = sys.argv[1:]
act, gm = {}, {}
for S in SEASONS:
    st = pd.read_parquet(NFLV + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy(); st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name)
    sn = pd.read_parquet(NFLV + f"snap_counts_{S}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.offense_snaps > 0)].copy(); sn["team"] = sn.team.replace(NV2T); sn["nkey"] = sn.player.map(norm_name)
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == S) & (g.game_type == "REG")].copy()
    g["home_team"] = g.home_team.replace(NV2T); g["away_team"] = g.away_team.replace(NV2T)
    act[S], gm[S] = (st, sn), g
OUTS = {}      # teams with an RB/WR/TE listed Out on the injury report for the week (Out players are dropped from the projection table, so the flag comes from the report)
for S in SEASONS:
    ij = pd.read_parquet(NFLV + f"injuries_{S}.parquet"); ij = ij[(ij.report_status == "Out") & ij.position.isin(["RB", "WR", "TE"])].copy(); ij["team"] = ij.team.replace(NV2T)
    OUTS[S] = {w: set(g.team) for w, g in ij.groupby("week")}
A = ["completions", "passing_yards", "passing_tds", "carries", "rushing_yards", "receptions", "receiving_yards", "rushing_tds", "receiving_tds"]


def load(tag):
    rows, trows = [], []
    for S in SEASONS:
        st, sn = act[S]
        for W in range(4, 13):
            P = pd.read_pickle(OUT + f"bt_{S}_w{W}_{tag}.pkl")
            full = P.copy()
            pl = set(zip(sn[sn.week == W].nkey, sn[sn.week == W].team)); P = P[[(a, b) in pl for a, b in zip(P.nkey, P.team)]]
            P = P.merge(st[st.week == W][["nkey", "team"] + A], on=["nkey", "team"], how="left").fillna(0)
            P["season"], P["week"] = S, W
            P["team_has_out"] = P.team.isin(OUTS[S].get(W, set()))
            rows.append(P)
            T = pd.read_pickle(OUT + f"btteam_{S}_w{W}_{tag}.pkl"); T = T[T.away.notna()].merge(gm[S][gm[S].week == W][["away_team", "home_team", "away_score", "home_score"]], left_on=["away", "home"], right_on=["away_team", "home_team"])
            T["season"] = S; trows.append(T)
    return pd.concat(rows, ignore_index=True), pd.concat(trows, ignore_index=True)


def metrics(D, T):
    sk = D[D.pos != "QB"]; r = {}
    for nm, mask, pc, ac in (("rec_yds", sk.rec >= 1.0, "rec_yds", "receiving_yards"), ("rec", sk.rec >= 1.0, "rec", "receptions"), ("rush_yds", sk.rush_att >= 4, "rush_yds", "rushing_yards"), ("rush_att", sk.rush_att >= 4, "rush_att", "carries")):
        d = sk[mask]; r[nm + "_mae"] = (d[pc] - d[ac]).abs().mean(); r[nm + "_ratio"] = d[ac].sum() / d[pc].sum()
    t = sk[sk.any_td >= 0.03]; p = np.clip(t.any_td, .01, .99); y = ((t.rushing_tds + t.receiving_tds) >= 1).astype(float)
    r["td_ll"] = float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    if T is not None:
        r["team_rmse"] = float(np.sqrt(np.mean(np.r_[(T.away_pts - T.away_score) ** 2, (T.home_pts - T.home_score) ** 2])))
    return r


res, data = {}, {}
for tag in tags:
    D, T = load(tag); data[tag] = (D, T)
    res[tag] = metrics(D, T)
    for S in SEASONS:
        res[f"{tag}:{S}"] = metrics(D[D.season == S], T[T.season == S])
R = pd.DataFrame(res).T
pd.set_option("display.width", 250)
print("ALL SEASONS and per season\n", R.round(4).to_string())
base = tags[0]
for tag in tags[1:]:
    print(f"\nDELTA {tag} - {base} (negative = better for MAE / log loss / RMSE)")
    cols = ["rec_yds_mae", "rec_mae", "rush_yds_mae", "rush_att_mae", "td_ll", "team_rmse"]
    print((R.loc[[tag] + [f"{tag}:{s}" for s in SEASONS], cols].values - R.loc[[base] + [f"{base}:{s}" for s in SEASONS], cols].values).round(4).__repr__())
    print("rows: all, 2023, 2024, 2025; cols:", cols)
    for nm, f in (("team has an Out RB/WR/TE", lambda D: D[D.team_has_out]),):
        d0, d1 = f(data[base][0]), f(data[tag][0])
        m0, m1 = metrics(d0, None), metrics(d1, None)
        print(f"\n{nm}: n={len(d1[d1.pos != 'QB'])}  " + "  ".join(f"{k} {m0[k]:.3f}->{m1[k]:.3f}" for k in ("rec_yds_mae", "rec_mae", "rush_yds_mae", "rush_att_mae", "td_ll")))
for tag in tags:
    D = data[tag][0]; sk = D[(D.pos != "QB") & (D.rush_att >= 4)].copy()
    sk["tier"] = pd.cut(sk.rush_yds, [0, 15, 30, 50, 75, 400])
    print(f"\nrush yards by projection tier ({tag}): actual/projected and mean proj, actual")
    print(sk.groupby("tier", observed=True).agg(n=("rush_yds", "size"), proj=("rush_yds", "mean"), actual=("rushing_yards", "mean")).assign(ratio=lambda x: x.actual / x.proj).round(3).to_string())
