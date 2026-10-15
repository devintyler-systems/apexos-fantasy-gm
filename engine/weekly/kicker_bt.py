"""Kicker backtest behind config/weekly/league_spm.json `kicker_env` (DECISIONS #27).

Target: 3*FG + XP per kicker-game, 2023-25 regular season weeks 4-12, kickers with >=3 prior games.
Compares the trailing-8-game average with a model on the game's market implied points, and tests whether kicker
accuracy, kicker FG attempts per game or team FG attempts per game (red-zone stall) add anything. 5-fold CV.
Needs the nflverse cache (play_by_play_{2023..2025}, games).
"""
import os

import numpy as np
import pandas as pd

from paths import NFLV, OUT

YEARS = (2023, 2024, 2025)


def build():
    cols = ["season", "week", "posteam", "play_type", "field_goal_result", "extra_point_result", "kicker_player_name", "season_type"]
    p = pd.concat([pd.read_parquet(f"{NFLV}play_by_play_{y}.parquet", columns=cols) for y in YEARS])
    p = p[p.season_type == "REG"]
    k = p[p.play_type.isin(["field_goal", "extra_point"]) & p.kicker_player_name.notna()].copy()
    k["fga"] = (k.play_type == "field_goal").astype(int)
    k["fgm"] = (k.field_goal_result == "made").astype(int)
    k["xpm"] = (k.extra_point_result == "good").astype(int)
    kg = k.groupby(["season", "week", "posteam", "kicker_player_name"]).agg(fga=("fga", "sum"), fgm=("fgm", "sum"), xpm=("xpm", "sum")).reset_index()
    kg["pts"] = 3 * kg.fgm + kg.xpm
    g = pd.read_parquet(f"{NFLV}games.parquet")
    g = g[g.season.isin(YEARS) & (g.game_type == "REG")]
    h = g.assign(team=g.home_team, imp=(g.total_line + g.spread_line) / 2)
    a = g.assign(team=g.away_team, imp=(g.total_line - g.spread_line) / 2)
    imp = pd.concat([h, a])[["season", "week", "team", "imp"]]
    kg = kg.merge(imp, left_on=["season", "week", "posteam"], right_on=["season", "week", "team"], how="left").sort_values(["kicker_player_name", "season", "week"])
    rows = []
    for _, r in kg[(kg.week >= 4) & (kg.week <= 12)].iterrows():
        prev = kg[(kg.kicker_player_name == r.kicker_player_name) & ((kg.season < r.season) | ((kg.season == r.season) & (kg.week < r.week)))]
        if len(prev) < 3:
            continue
        tm = kg[(kg.posteam == r.posteam) & ((kg.season < r.season) | ((kg.season == r.season) & (kg.week < r.week)))].groupby(["season", "week"]).fga.sum()
        rows.append(dict(y=r.pts, imp=r.imp, k_ppg=prev.pts.tail(8).mean(), k_fga=prev.fga.tail(8).mean(), team_fga=tm.tail(8).mean(),
                         acc=(prev.fgm.sum() + 12 * .84) / (prev.fga.sum() + 12)))
    return pd.DataFrame(rows).dropna()


def cv_mae(d, cols):
    idx = np.arange(len(d)); rng = np.random.default_rng(0); rng.shuffle(idx); folds = np.array_split(idx, 5)
    X = np.c_[np.ones(len(d)), d[cols].values]; pr = np.zeros(len(d))
    for i in range(5):
        tr = np.concatenate([folds[j] for j in range(5) if j != i])
        b = np.linalg.lstsq(X[tr], d.y.values[tr], rcond=None)[0]
        pr[folds[i]] = X[folds[i]] @ b
    return float(np.abs(d.y - pr).mean()), float(np.corrcoef(d.y, pr)[0, 1])


def main():
    d = build()
    out = {"n": len(d), "baseline_trailing8_mae": float(np.abs(d.y - d.k_ppg).mean()), "baseline_trailing8_corr": float(np.corrcoef(d.y, d.k_ppg)[0, 1])}
    for name, cols in [("implied", ["imp"]), ("implied+k_fga", ["imp", "k_fga"]), ("implied+k_fga+acc", ["imp", "k_fga", "acc"]), ("implied+team_fga", ["imp", "team_fga"])]:
        out[name] = dict(zip(("cv_mae", "cv_corr"), cv_mae(d, cols)))
    X = np.c_[np.ones(len(d)), d.imp.values]
    out["fit_intercept_slope"] = [float(x) for x in np.linalg.lstsq(X, d.y.values, rcond=None)[0]]
    print(pd.Series(out).to_string())
    return out


if __name__ == "__main__":
    main()
