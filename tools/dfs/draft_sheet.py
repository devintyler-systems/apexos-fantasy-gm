"""Draft cheat sheet for a custom-scoring best-ball/draft contest from fresh joint simulations.

APEX_SEASON=2026 APEX_TARGET_WEEK=12 APEX_ENV=market [APEX_MANUAL_OUT=... APEX_STATUS_OVERLAY=... APEX_ANCHOR_XLSX=...] \
  python tools/dfs/draft_sheet.py CHI@DET,PHI@DAL,KC@BUF OUT.csv [--ns 20000]
Scoring (contest "The Free Bird", 2026 Thanksgiving): 0.5/rec, 0.1/rush+rec yd, 6/rush or rec TD, 0.04/pass yd, 4/pass TD, -1/INT, -2/fumble lost.
Engine fp = 0.04 py + 4 ptd - 2 int + 0.1 yds + 6 TD + 1.0 rec - 2 fl, so contest = fp + int - 0.5 rec. Inactive draws score 0.
Per player: mean, median, P90, P(top-12 among all slate players in the same draw), p_active; plus QB-teammate correlations.
"""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine", "weekly")
sys.path.insert(0, HERE); os.chdir(HERE)
import run_all as R

games = [tuple(g.split("@")) for g in sys.argv[1].split(",")]
out = sys.argv[2]; ns = int(sys.argv[sys.argv.index("--ns") + 1]) if "--ns" in sys.argv else 20000
rows, mats, qbs = [], [], {}
for a, h in games:
    R.run_game(a, h, neutral=False, ns=ns); d = R.STORE.pop((a, h))
    for t in (a, h):
        for p in d["players"][t]:
            if p["pos"] not in ("QB", "RB", "WR", "TE"): continue
            f = p["fp"] + p.get("pass_int", 0) - 0.5 * p["rec"]
            f = np.where(p["mask"], f, 0.0)
            if f.mean() < 1.0: continue
            rows.append(dict(player=p["player"], pos=p["pos"], team=t, game=f"{a}@{h}", p_active=p["p_active"], mean=f.mean(), median=np.median(f), p90=np.percentile(f, 90)))
            mats.append(f)
            if p["pos"] == "QB" and (t not in qbs or f.mean() > qbs[t][1].mean()): qbs[t] = (len(rows) - 1, f)
M = np.vstack(mats); D = pd.DataFrame(rows)
rk = (-M).argsort(axis=0).argsort(axis=0)
D["p_top12"] = (rk < 12).mean(axis=1)
D["p_top3"] = (rk < 3).mean(axis=1)
D["qb_corr"] = [np.corrcoef(M[i], qbs[r.team][1])[0, 1] if r.team in qbs and r.pos != "QB" else np.nan for i, r in D.iterrows()]
D = D.sort_values("mean", ascending=False).reset_index(drop=True)
D.round(3).to_csv(out, index=False)
pd.set_option("display.width", 200); print(D.head(50).round(2).to_string())
