"""Backtest the MODEL-ONLY track's game predictions against the betting line.

Usage: python game_bt.py BT_DIR TAG [TAG ...]     # BT_DIR holds btteam_<season>_w<week>_<TAG>.pkl from bt_variant.sh; the first TAG is the baseline

Per tag: margin MAE, total MAE, team-points RMSE and winner accuracy of the model-only team-points means, against the same measures for the nflverse spread_line / total_line over the same games,
and the weight on the model in the MAE-optimal blend of model and line (0.0 means the model adds nothing the line does not already have). A change meant to make the model-only track a better
forecaster than the line has to beat the line row and raise that blend weight, in all three seasons. Reads the cache from APEX_NFLV.
"""
import glob
import re
import sys

import numpy as np
import pandas as pd

from paths import NFLV


def load(bt_dir, tag):
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[g.game_type == "REG"]
    rows = []
    for f in glob.glob(f"{bt_dir}/btteam_*_{tag}.pkl"):
        s, w = re.search(r"btteam_(\d+)_w(\d+)_", f).groups(); t = pd.read_pickle(f); t = t[t.away_pts.notna()][["away", "home", "away_pts", "home_pts"]]
        rows.append(t.assign(season=int(s), week=int(w)))
    b = pd.concat(rows)
    return b.merge(g[["season", "week", "away_team", "home_team", "home_score", "away_score", "spread_line", "total_line"]], left_on=["season", "week", "away", "home"], right_on=["season", "week", "away_team", "home_team"])


def score(m, mg, tt):
    am, at = m.home_score - m.away_score, m.home_score + m.away_score; hl, al = (tt + mg) / 2, (tt - mg) / 2
    return dict(games=len(m), margin_MAE=(mg - am).abs().mean(), total_MAE=(tt - at).abs().mean(), team_pts_RMSE=float(np.sqrt((((hl - m.home_score) ** 2).mean() + ((al - m.away_score) ** 2).mean()) / 2)), winner=((mg > 0) == (am > 0)).mean())


def blend(m, mod, ln, act):
    return min((float(np.abs(w * mod + (1 - w) * ln - act).mean()), round(float(w), 1)) for w in np.arange(0, 1.01, .1))


if __name__ == "__main__":
    bt_dir, tags = sys.argv[1], sys.argv[2:]
    for tag in tags:
        m = load(bt_dir, tag); mm, mt = m.home_pts - m.away_pts, m.home_pts + m.away_pts
        am, at = m.home_score - m.away_score, m.home_score + m.away_score
        print(f"\n== {tag} ==")
        rows = {f"model-only {s}": score(m[m.season == s], mm[m.season == s], mt[m.season == s]) for s in sorted(m.season.unique())}
        rows["model-only ALL"] = score(m, mm, mt); rows["line ALL"] = score(m, m.spread_line, m.total_line)
        print(pd.DataFrame(rows).T.round(3).to_string())
        for s in sorted(m.season.unique()):
            x = m.season == s; print(f"  line {s}: margin MAE {(m.spread_line[x] - am[x]).abs().mean():.3f}  total MAE {(m.total_line[x] - at[x]).abs().mean():.3f}")
        bm, bt_ = blend(m, mm, m.spread_line, am), blend(m, mt, m.total_line, at)
        print(f"blend weight on model: margin {bm[1]} (MAE {bm[0]:.3f} vs line {(m.spread_line - am).abs().mean():.3f}), total {bt_[1]} (MAE {bt_[0]:.3f} vs line {(m.total_line - at).abs().mean():.3f})")
        print(f"mean total bias model minus line: {(mt - m.total_line).mean():+.2f}; correlation of model margin with spread: {np.corrcoef(mm, m.spread_line)[0, 1]:.2f}")
