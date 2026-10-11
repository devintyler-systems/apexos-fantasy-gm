"""Sunday betting options from refresh-B sims + STALE Thursday book lines (every price is reference only; break-even prices are the actionable output).
Probabilities used for decisions are 50/50 blends of model and book no-vig (shrinks the model's known level bias); gaps are bias-centered per market.
Windows (US Eastern kickoff): 1 PM = 17:00Z, 4 PM = 20:05/20:25Z, SNF = 00:20Z, Monday = 00:15Z next day. PHI@JAX started 13:30Z and is excluded.
Usage: APEX_ENV=market APEX_MANUAL_OUT=... python sunday_bets.py  -> OUT/sunday_bets.pkl and prints markdown"""
import itertools, numpy as np, pandas as pd, os, sys
from paths import OUT, NFLV
import run_all as R
from params import SCHED, is_neutral, norm_name, SEASON
Em = pd.read_csv(OUT + "edges_all_rows.csv")
WINDOW = {"CHI@GB": "1PM", "CIN@MIA": "1PM", "LV@NE": "1PM", "MIN@NO": "1PM", "CLE@NYJ": "1PM", "IND@PIT": "1PM", "HOU@TEN": "1PM", "NYG@WAS": "1PM",
          "DEN@LAC": "4PM", "DET@ARI": "4PM", "SF@SEA": "4PM", "BAL@ATL": "SNF", "BUF@LA": "MNF"}
Em = Em[Em.game.isin(WINDOW)].copy(); Em["key"] = Em.player.map(norm_name); Em["window"] = Em.game.map(WINDOW)
COUNT = ["rec", "rec_yds", "rush_yds", "rush_att", "pass_yds", "pass_cmp", "pass_att"]
st = pd.read_parquet(NFLV + f"stats_player_week_{SEASON}.parquet"); st = st[(st.week <= 4) & (st.season_type == "REG")].copy(); st["key"] = st.player_display_name.map(norm_name)
COL = {"rec": "receptions", "rec_yds": "receiving_yards", "rush_yds": "rushing_yards", "rush_att": "carries", "pass_yds": "passing_yards", "pass_cmp": "completions", "pass_att": "attempts"}
PL = {"rec": "targets", "rec_yds": "targets", "rush_yds": "carries", "rush_att": "carries", "pass_yds": "attempts", "pass_cmp": "attempts", "pass_att": "attempts"}
dec = lambda a: 1 + (100 / -a if a < 0 else a / 100)
def fair_amer(p):
    p = float(np.clip(p, 1e-4, 1 - 1e-4)); return int(round(-100 * p / (1 - p))) if p >= .5 else int(round(100 * (1 - p) / p))
SKIP = {"tyler huntley", "tyson bagent", "jalon daniels", "case keenum"}      # backup QBs priced by books but not identity-adjusted in the engine
# ---- sims for every unstarted game (refresh-B configuration)
sims = {}
for g in SCHED.itertuples():
    gk = f"{g.away}@{g.home}"
    if gk not in WINDOW: continue
    R.run_game(g.away, g.home, neutral=is_neutral(g.away, g.home)); d = R.STORE.pop((g.away, g.home))
    Tt = np.maximum(d["A"]["td"] + d["H"]["td"] + d["A"]["dtd"] + d["H"]["dtd"], 1)
    sims[gk] = dict(pl={norm_name(p["player"]): p for t in (g.away, g.home) for p in d["players"][t]}, Tt=Tt)
# ---- non-TD props
bias = (Em[Em.is_main_line & (Em.side == "over") & Em.market.isin(COUNT)].assign(g=lambda x: x.model_p - x.novig_p)).groupby("market").g.median()
rows = []
for (gm, k, mk), g in Em[Em.is_main_line & Em.market.isin(COUNT)].groupby(["game", "key", "market"]):
    ov = g[g.side == "over"]; un = g[g.side == "under"]
    if not len(ov) or k in SKIP: continue
    line = float(ov.line.iloc[0]); feeds = int(ov.book.nunique()); mo = float(ov.model_p.iloc[0]); nv = float(ov.novig_p.mean()); pa = float(ov.p_active.iloc[0])
    gap = mo - nv; gc = gap - bias[mk]; lean = "OVER" if gc > 0 else "UNDER"
    pm, pb = (mo, nv) if lean == "OVER" else (1 - mo, 1 - nv)
    blend = 0.5 * pm + 0.5 * pb
    b = (ov if lean == "OVER" else un)
    if not len(b): continue
    bb = b.sort_values("odds", ascending=False).iloc[0]
    lg = st[(st.key == k) & (st[PL[mk]] > 0)]; n = len(lg); hits = int((lg[COL[mk]] > line).sum()); avg = float(lg[COL[mk]].mean()) if n else np.nan
    agree = n >= 3 and ((lean == "OVER" and hits / n >= 0.5 and avg >= line) or (lean == "UNDER" and hits / n <= 0.5 and avg <= line))
    kneel = (mk == "rush_yds" and line <= 2.5)                      # quarterback kneel-down / scramble lines are not a real market
    sup0 = (abs(gc) >= 0.08) and (np.sign(gap) == np.sign(gc)) and pa >= 0.9 and feeds >= (4 if mk in ("rec", "rush_att", "pass_att", "pass_cmp") else 3) and agree and not kneel
    big = abs(gap) >= 0.30                                          # model and book 30+ points apart: usually a role or news difference, so investigate instead of betting
    sup = sup0 and not big
    rows.append(dict(window=WINDOW[gm], game=gm, player=ov.player.iloc[0], team=ov.team.iloc[0], key=k, market=mk, line=line, lean=lean, model_side=pm, book_side=pb, blend=blend, gap=gap, gap_c=gc, price=int(bb.odds), book=bb.book,
                     ev_ref=blend * (dec(bb.odds) - 1) - (1 - blend), fair=fair_amer(blend), feeds=feeds, games=n, hits=hits, avg=avg, pa=pa, supported=sup, big_watch=(sup0 and big), rule_eligible=(mk == "rush_yds")))
P = pd.DataFrame(rows)
# ---- TD shots
tdr = []
for gm, g0 in Em[Em.market.isin(["anytime_td", "first_td"])].groupby("game"):
    for mk, g1 in g0.groupby("market"):
        A = g1.groupby("key").agg(player=("player", "first"), team=("team", "first"), model=("model_p", "first"), vigin=("imp_vig_in", "median"), nv=("novig_p", "median"), feeds=("book", "nunique"), pa=("p_active", "first")).reset_index()
        A = A[~A.key.isin(SKIP)]
        A["ratio"] = (A.model / A.model.sum()) / (A.vigin / A.vigin.sum())
        bb = g1.sort_values("odds", ascending=False).groupby("key").first()
        A["price"] = A.key.map(bb.odds).astype(int); A["book"] = A.key.map(bb.book)
        A["blend"] = 0.5 * A.model + 0.5 * A.nv; A["ev_ref"] = A.blend * (A.price.map(dec) - 1) - (1 - A.blend); A["fair"] = A.blend.map(fair_amer)
        A["market"] = mk; A["game"] = gm; A["window"] = WINDOW[gm]; tdr.append(A)
T = pd.concat(tdr)
pd.to_pickle((P, T, bias), OUT + "sunday_bets.pkl")
print("bias", bias.round(3).to_dict()); print(len(P), "props;", int(P.supported.sum()), "supported;", len(T), "TD rows")

# ================= TD shot flags, parlays =================
PJ = pd.read_csv(sorted(__import__("glob").glob("../../runs/weekly/2026_w05_market_20261011T16*"))[0] + "/projections.csv"); PJ["key"] = PJ.player.map(norm_name)
car = st[st.carries > 0].groupby("key").carries.agg(["mean", "size"]); tg = st[st.targets > 0].groupby("key").targets.agg(["mean", "size"])
def up(k):
    r = PJ[PJ.key == k]
    if not len(r): return ""
    r = r.iloc[0]; o = []
    if k in car.index and r.rush_att_mean >= 3 and car.loc[k, "size"] >= 2 and r.rush_att_mean >= 1.4 * car.loc[k, "mean"]: o.append(f"{r.rush_att_mean:.0f} proj carries vs {car.loc[k,'mean']:.0f}")
    if k in tg.index and r.tgt_mean >= 2 and tg.loc[k, "size"] >= 2 and r.tgt_mean >= 1.4 * tg.loc[k, "mean"]: o.append(f"{r.tgt_mean:.1f} proj targets vs {tg.loc[k,'mean']:.1f}")
    if k not in car.index and r.rush_att_mean >= 3: o.append("no 2026 carries on record")
    if k not in tg.index and r.tgt_mean >= 2: o.append("no 2026 targets on record")
    if r.pos == "RB" and r.tgt_mean > 0 and r.rec_td_mean / max(r.tgt_mean, 1e-9) > 0.05: o.append("RB receiving-TD rate above 5% per target")
    return "UPPER-RANGE: " + "; ".join(o) if o else ""
TH = pd.read_csv("../../runs/weekly/2026_w05_market_20261008T230223Z/projections.csv"); TH["key"] = TH.player.map(norm_name); TH = TH.drop_duplicates("key").set_index("key")
def moved(k):
    if k not in TH.index: return "no Thursday projection"
    a = TH.loc[k]; b = PJ[PJ.key == k]
    if not len(b): return "not in refresh B"
    b = b.iloc[0]; o = []
    if abs(b.any_td_pct - a.any_td_pct) >= 0.03: o.append(f"anytime TD {100*a.any_td_pct:.0f}% to {100*b.any_td_pct:.0f}%")
    for c, lab in (("tgt_mean", "targets"), ("rush_att_mean", "carries")):
        x, y = a[c], b[c]
        if pd.notna(x) and pd.notna(y) and abs(y - x) >= 0.6 and abs(y - x) / max(x, 1) >= 0.12: o.append(f"{lab} {x:.1f} to {y:.1f}")
    if abs(b.p_active - a.p_active) >= 0.1: o.append(f"availability {a.p_active:.2f} to {b.p_active:.2f}")
    return "; ".join(o)
T["flag"] = T.key.map(up)
T["moved"] = T.key.map(moved)
BIGK = set(P[P.gap.abs() >= 0.30].key)      # model and book 30+ points apart on any prop: the same role difference applies to his touchdown price
T["bigdis"] = T.key.isin(BIGK)
P["moved"] = P.key.map(moved)
P["supported_raw"] = P.supported; P["supported"] = P.supported & (P.moved == "")
_u = PJ.drop_duplicates("key").set_index("key"); T["tgt"] = T.key.map(_u.tgt_mean).fillna(0); T["car"] = T.key.map(_u.rush_att_mean).fillna(0)
T["real_role"] = (T.tgt >= 4) | (T.car >= 8)
T.to_pickle(OUT + "sunday_td.pkl"); P.to_pickle(OUT + "sunday_props_moved.pkl")
# leg arrays
def legarr(gm, k, kind, mk=None, line=None, lean=None):
    pl = sims[gm]["pl"][k]; m = pl["mask"]
    if kind == "atd": a = (pl["rush_td"] + pl["rec_td"]) >= 1
    else: x = pl[{"rec": "rec", "rec_yds": "rec_yds", "rush_yds": "rush_yds", "rush_att": "rush_att", "pass_yds": "pass_yds", "pass_cmp": "pass_cmp", "pass_att": "pass_att"}[mk]]; a = (x > line) if lean == "OVER" else (x < line)
    return a, m
legs = []
S = P[P.supported & ~P.key.isin(SKIP) & (P.blend >= 0.55) & (P.pa >= 0.97)].copy(); S["absgc"] = S.gap_c.abs()
for r in S.itertuples(): legs.append(dict(window=r.window, game=r.game, key=r.key, name=r.player, label=f"{r.player} {r.lean} {r.line:g} {r.market}", kind="prop", mk=r.market, line=r.line, lean=r.lean, blend=r.blend, price=r.price, book=r.book, score=r.absgc, up=""))
Z = T[(T.market == "anytime_td") & (T.pa >= 0.97) & (T.ratio >= 1.2) & (T.ratio <= 3.0) & (T.price >= 120) & (T.model >= 0.15) & T.real_role & (T.flag == "") & (T.moved == "") & ~T.bigdis].copy()
for r in Z.itertuples(): legs.append(dict(window=r.window, game=r.game, key=r.key, name=r.player, label=f"{r.player} Anytime TD", kind="atd", mk="atd", line=None, lean=None, blend=r.blend, price=r.price, book=r.book, score=r.ratio - 1, up=r.flag))
L = pd.DataFrame(legs)
out = []
def combos(univ, sizes=(2, 3, 4)):
    res = []
    for n in sizes:
        for c in itertools.combinations(range(len(univ)), n):
            ls = [univ.iloc[i] for i in c]
            if len({x["name"] for x in ls}) < n: continue                      # one leg per player
            blend = 1.0; pay = 1.0
            for g in {x.game for x in ls}:
                gl = [x for x in ls if x.game == g]
                arrs = [legarr(g, x.key, x.kind, x.mk, x.line, x.lean) for x in gl]
                m = np.ones_like(arrs[0][1], dtype=bool)
                for a, mm in arrs: m &= mm
                if m.sum() < 500: blend = 0; break
                j = np.ones(m.sum(), bool)
                for a, mm in arrs: j &= a[m]
                marg = np.prod([a[m].mean() for a, mm in arrs]); corr = (j.mean() / marg) if marg > 0 else 1.0
                blend *= np.prod([x.blend for x in gl]) * (corr if len(gl) > 1 else 1.0)
            for x in ls: pay *= dec(x.price)
            if blend <= 0: continue
            res.append(dict(n=n, legs=" + ".join(x.label for x in ls), games="/".join(sorted({x.game for x in ls})), joint=blend, payout=pay, fair=fair_amer(blend), ev0=blend * (pay - 1) - (1 - blend), ev20=blend * (0.8 * (pay - 1)) - (1 - blend),
                            ups="; ".join(sorted({x.up for x in ls if x.up}))))
    return pd.DataFrame(res)
PAR = {}
for w, g in list(L.groupby("window")) + [("ALL", L)]:
    u = g.sort_values("score", ascending=False)
    u = pd.concat([u[u.kind == "prop"].head(6), u[u.kind == "atd"].head(4)]) if w != "ALL" else pd.concat([u[u.kind == "prop"].head(7), u[u.kind == "atd"].head(5)])
    if len(u) < 2: continue
    PAR[w] = combos(u.reset_index(drop=True), ((2, 3, 4) if w == "ALL" else (2, 3)) if len(u) >= 4 else (2,))
pd.to_pickle((L, PAR), OUT + "sunday_parlays.pkl")
print({w: len(v) for w, v in PAR.items()}, "legs", len(L))
