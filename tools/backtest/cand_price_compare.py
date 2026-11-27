"""Candidate vs baseline on the priced sets, with the rising-role subset (DECISIONS #89 addendum; generalises gl5_price_compare.py).

  python tools/backtest/cand_price_compare.py BASE_A CAND_A BASE_B CAND_B
Needs var/bt/odds_{td,yds,early}_{TAG}.pkl for every tag (odds_price_eval.py td / yds, odds_early_eval.py).
Rising role = last-3 offense-snap share minus the season mean (weeks < W) >= 0.10, the R-40 trigger (td_miss_diagnosis.features).
Engine probabilities are not fitted to outcomes, so engine-alone scores are out of sample by construction; the blend weight is leave-one-season-out.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import odds_price_eval as ope  # noqa: E402
import td_miss_diagnosis as tmd  # noqa: E402
from odds_price_eval import ll, br, REPO  # noqa: E402
from odds_early_eval import cboot  # noqa: E402

BT = os.path.join(REPO, "var", "bt"); GRID = np.round(np.arange(0, 1.001, .02), 2)


def loso_blend(t):
    out = np.empty(len(t))
    for S in (2023, 2024, 2025):
        tr, te = t[t.season != S], (t.season == S).values
        w = GRID[int(np.argmin([ll(tr.book + x * (tr.eng - tr.book), tr.y) for x in GRID]))]
        out[te] = (t.book + w * (t.eng - t.book)).values[te]
    return out


def table(t):
    t = t.assign(lb=loso_blend(t)); rows = []
    for S in (2023, 2024, 2025, "all"):
        g = t if S == "all" else t[t.season == S]
        rows.append(dict(season=S, n=len(g), eng_ll=ll(g.eng, g.y), lb_ll=ll(g.lb, g.y), w02_ll=ll(g.book + .2 * (g.eng - g.book), g.y), book_ll=ll(g.book, g.y),
                         eng_br=br(g.eng, g.y), lb_br=br(g.lb, g.y)))
    return pd.DataFrame(rows).set_index("season")


def diff(B, C, label):
    tb, tc = table(B), table(C); d = (tc - tb)[["eng_ll", "lb_ll", "w02_ll", "eng_br", "lb_br"]]
    print(f"\n{label}: n {len(B)}; base levels (eng / loso-blend / book, all): {tb.loc['all', 'eng_ll']:.5f} / {tb.loc['all', 'lb_ll']:.5f} / {tb.loc['all', 'book_ll']:.5f}"
          f"; cand eng {tc.loc['all', 'eng_ll']:.5f}\ncand minus base (negative = candidate better)\n" + d.round(5).to_string())


def early(tag, rise):
    E = pd.read_pickle(os.path.join(BT, f"odds_early_{tag}.pkl")); E = E[E.healthy & E.xmove.notna()]
    out = {}
    for nm, g in (("gap 5-10", E[(E.gap >= .05) & (E.gap < .10)]), ("gap 5-10, rising role", E[(E.gap >= .05) & (E.gap < .10) & E.di.isin(rise)])):
        lo = cboot(g, "xmove") if len(g) else (np.nan, np.nan); pl = np.where(g.y == 1, ope.pay(g.best_e), -1.0)
        out[nm] = dict(n=len(g), rel_move=round(100 * g.xmove.mean(), 2) if len(g) else np.nan, rel_90=tuple(np.round(100 * np.array(lo), 2)), roi=round(100 * pl.mean(), 1) if len(g) else np.nan)
    out["early LL eng / 50-50 / book"] = (round(ll(E.eng, E.y), 5), round(ll(.5 * (E.eng + E.b_e), E.y), 5), round(ll(E.b_e, E.y), 5))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]; D = ope.engine(a[0])
    need = set()
    for t in a:
        for k in ("td", "yds", "early"): need |= set(pd.read_pickle(os.path.join(BT, f"odds_{k}_{t}.pkl")).di)
    F = tmd.features(D, need); rise = set(F.index[F.role_chg >= .10])
    print(f"rising-role player-games (last-3 snap share >= season mean + 10 pts): {len(rise)} of {len(F)}")
    for base, cand in zip(a[0::2], a[1::2]):
        print(f"\n################ {cand} vs {base}")
        for mk in ("player_rush_yds", "player_reception_yds"):
            B = pd.read_pickle(os.path.join(BT, f"odds_yds_{base}.pkl")); C = pd.read_pickle(os.path.join(BT, f"odds_yds_{cand}.pkl"))
            key = ["di", "market", "point"]; B, C = B[B.market == mk].sort_values(key).reset_index(drop=True), C[C.market == mk].sort_values(key).reset_index(drop=True)
            assert (B[key].values == C[key].values).all(), "line sets differ"
            diff(B, C, f"{mk} main line, over")
            m = B.di.isin(rise).values; diff(B[m].reset_index(drop=True), C[m].reset_index(drop=True), f"{mk}, rising-role subset")
        B = pd.read_pickle(os.path.join(BT, f"odds_td_{base}.pkl")).rename(columns={"cons": "book"}); C = pd.read_pickle(os.path.join(BT, f"odds_td_{cand}.pkl")).rename(columns={"cons": "book"})
        assert (B.di.values == C.di.values).all()
        diff(B, C, "anytime TD"); m = B.di.isin(rise).values; diff(B[m].reset_index(drop=True), C[m].reset_index(drop=True), "anytime TD, rising-role subset")
        print("\n2025 early, healthy:\n base", early(base, rise), "\n cand", early(cand, rise))
