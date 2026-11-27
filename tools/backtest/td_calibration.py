"""R-30: leave-one-season-out calibration of anytime-TD probabilities on backtest pickles (post-sim layer, no engine change).

python tools/backtest/td_calibration.py TAG [TAG ...]
For each held-out season, fits on the other two: (a) a logit shift per position (RB/WR/TE), (b) logit slope+shift per position, (c) isotonic on the raw probability
(pooled positions). Scores held-out log loss and Brier vs the raw engine probability. Scope matches evaluate.py: non-QB players with any_td >= 0.03 and a snap.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from evaluate import load, SEASONS
from scipy.optimize import minimize
from sklearn.isotonic import IsotonicRegression

lg = lambda p: np.log(p / (1 - p)); ex = lambda x: 1 / (1 + np.exp(-x))
def ll(p, y): p = np.clip(p, .01, .99); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
def br(p, y): return float(np.mean((p - y) ** 2))

def fit_pos(d, slope):
    par = {}
    for pos, g in d.groupby("pos"):
        x, y = lg(np.clip(g.any_td.values, .01, .99)), g.y.values
        f = (lambda t: ll(ex(t[0] + t[1] * x), y)) if slope else (lambda t: ll(ex(t[0] + x), y))
        par[pos] = minimize(f, [0.0, 1.0] if slope else [0.0], method="Nelder-Mead").x
    return par

def apply_pos(d, par, slope):
    out = np.empty(len(d))
    for i, (pos, p) in enumerate(zip(d.pos, d.any_td)):
        t = par.get(pos, [0.0, 1.0]); x = lg(min(max(p, .01), .99))
        out[i] = ex(t[0] + (t[1] * x if slope else x))
    return out

for tag in sys.argv[1:]:
    D, _ = load(tag); d = D[(D.pos.isin(["RB", "WR", "TE"])) & (D.any_td >= 0.03)].copy()
    d["y"] = ((d.rushing_tds + d.receiving_tds) >= 1).astype(float)
    rows = []
    for S in SEASONS:
        tr, te = d[d.season != S], d[d.season == S]
        r = dict(season=S, n=len(te), raw_ll=ll(te.any_td, te.y), raw_br=br(te.any_td, te.y))
        for nm, sl in (("shift", False), ("slope", True)):
            p = apply_pos(te, fit_pos(tr, sl), sl); r[nm + "_ll"] = ll(p, te.y); r[nm + "_br"] = br(p, te.y)
        iso = IsotonicRegression(out_of_bounds="clip", y_min=.005, y_max=.95).fit(tr.any_td, tr.y); p = iso.predict(te.any_td)
        r["iso_ll"] = ll(p, te.y); r["iso_br"] = br(p, te.y)
        rows.append(r)
    R = pd.DataFrame(rows).set_index("season")
    for m in ("shift", "slope", "iso"):
        R[m + "_dll"] = R[m + "_ll"] - R.raw_ll; R[m + "_dbr"] = R[m + "_br"] - R.raw_br
    print(f"\n{tag} (held-out season; negative = better)\n" + R[["n", "raw_ll", "shift_dll", "slope_dll", "iso_dll", "raw_br", "shift_dbr", "slope_dbr", "iso_dbr"]].round(5).to_string())
    w = R.n / R.n.sum(); print("pooled:", {c: round(float((R[c] * w).sum()), 5) for c in ("shift_dll", "slope_dll", "iso_dll", "shift_dbr", "slope_dbr", "iso_dbr")})
    print("full-sample fit (for live use):", {k: np.round(v, 3).tolist() for k, v in fit_pos(d, True).items()})
