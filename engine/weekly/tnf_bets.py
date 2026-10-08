"""TB@DAL: vig-neutral anytime/first-TD share comparison, single-bet EV at the best book price, and joint-simulation parlay prices for 2-4 leg anytime-TD combos.
Model numbers only; EV is 'if the model is right' and the model has NOT beaten the books on anytime TD (Week 4: log loss 0.4422 vs 0.4373).
Usage: APEX_ENV=market python tnf_bets.py AWAY HOME  -> prints markdown tables and writes OUT/bets_AWAY_HOME.pkl"""
import sys, itertools, numpy as np, pandas as pd
from paths import OUT
import run_all as R
from params import is_neutral, norm_name
AWAY, HOME = sys.argv[1], sys.argv[2]; GAME = f"{AWAY}@{HOME}"
E = pd.read_csv("../../var/out_market/edges_all_rows.csv"); E = E[E.game == GAME].copy(); E["key"] = E.player.map(norm_name)
R.run_game(AWAY, HOME, neutral=is_neutral(AWAY, HOME), ns=20000); d = R.STORE.pop((AWAY, HOME))
Ttot = np.maximum(d["A"]["td"] + d["H"]["td"] + d["A"]["dtd"] + d["H"]["dtd"], 1)
pl = {norm_name(p["player"]): p for t in (AWAY, HOME) for p in d["players"][t]}
dec = lambda a: 1 + (100 / -a if a < 0 else a / 100)
am = lambda x: f"{int(x):+d}"
def tab(mk):
    x = E[E.market == mk]; rows = []
    for k, g in x.groupby("key"):
        if k not in pl or "emari demercado" == k: continue
        p = pl[k]; m = p["mask"]; tdc = p["rush_td"] + p["rec_td"]
        mp = float((tdc[m] >= 1).mean()) if mk == "anytime_td" else float((tdc[m] / Ttot[m]).mean())
        b = g.sort_values("odds", ascending=False).iloc[0]
        rows.append(dict(key=k, player=g.player.iloc[0], team=pl[k]["team"] if "team" in pl[k] else "", pos=p["pos"], pa=float(p["p_active"]), model=mp, vigin=float(g.imp_vig_in.median()), best=int(b.odds), book=b.book, feeds=int(g.book.nunique())))
    T = pd.DataFrame(rows); T["share_model"] = T.model / T.model.sum(); T["share_book"] = T.vigin / T.vigin.sum(); T["ratio"] = T.share_model / T.share_book
    T["ev_best"] = T.model * (np.array([dec(a) for a in T.best]) - 1) - (1 - T.model); T["be_prob"] = [1 / dec(a) for a in T.best]
    return T.sort_values("ratio", ascending=False)
A, F = tab("anytime_td"), tab("first_td")
print("ANYTIME sum model %.2f, sum book vig-in %.2f, (implied book overround vs model total %.0f%%)" % (A.model.sum(), A.vigin.sum(), 100 * (A.vigin.sum() / A.model.sum() - 1)))
print("FIRST sum model %.3f, sum book vig-in %.3f" % (F.model.sum(), F.vigin.sum()))
pd.set_option("display.width", 250)
print(A[["player", "pos", "pa", "model", "vigin", "best", "book", "feeds", "ratio", "ev_best", "be_prob"]].round(3).to_string(index=False))
print(F[["player", "pa", "model", "vigin", "best", "book", "feeds", "ratio", "ev_best"]].head(14).round(3).to_string(index=False))
# parlays: joint from sims, legs = anytime TD at best price
U = A[(A.pa >= 0.9) & (A.model >= 0.09) & (A.feeds >= 4)].copy(); keys = list(U.key); price = dict(zip(U.key, U.best)); prob_m = dict(zip(U.key, U.model))
atd = {k: ((pl[k]["rush_td"] + pl[k]["rec_td"]) >= 1) for k in keys}; msk = {k: pl[k]["mask"] for k in keys}
rows = []
for n in (2, 3, 4):
    for combo in itertools.combinations(keys, n):
        m = np.ones_like(msk[keys[0]], dtype=bool)
        for k in combo: m &= msk[k]
        j = np.ones(m.sum(), dtype=bool)
        for k in combo: j &= atd[k][m]
        jp = float(j.mean()); naive = float(np.prod([prob_m[k] for k in combo])); pay = float(np.prod([dec(price[k]) for k in combo]))
        rows.append(dict(n=n, legs=" + ".join(U[U.key == k].player.iloc[0] for k in combo), joint=jp, naive_model=naive, corr=jp / naive if naive else np.nan, payout_dec=pay, american=(pay - 1) * 100 if pay >= 2 else -100 / (pay - 1),
                         ev_naive_payout=jp * (pay - 1) - (1 - jp), breakeven_payout_cut=1 - (1 / jp - 1) / (pay - 1) if jp > 0 else np.nan))
P = pd.DataFrame(rows); P.to_pickle(OUT + f"bets_{AWAY}_{HOME}.pkl"); A.to_pickle(OUT + f"bets_atd_{AWAY}_{HOME}.pkl"); F.to_pickle(OUT + f"bets_ftd_{AWAY}_{HOME}.pkl")
for n in (2, 3, 4):
    print(f"\nTOP {n}-LEG by EV at naive (multiplied) payout:"); print(P[P.n == n].sort_values("ev_naive_payout", ascending=False).head(6)[["legs", "joint", "naive_model", "corr", "american", "ev_naive_payout", "breakeven_payout_cut"]].round(3).to_string(index=False))
