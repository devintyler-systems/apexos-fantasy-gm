"""EXPLORATORY DraftKings Showdown Captain-mode ceiling search for ONE game from the correlated sims. Not part of the validated pipeline: no backtest exists
(AGENTS.md: optimizer changes need a baseline comparison; evaluation plan = grade the lineup against actuals the next Tuesday).
Rules used: 6 players (1 CPT at 1.5x points and the CPT salary, 5 FLEX), salary cap 50000 (DK Showdown standard, NOT stated in the contest text), both teams required.
Selection uses the even-numbered sims, the reported numbers come from the odd-numbered holdout sims, so the selection does not inflate the ceiling it reports.
Usage: APEX_DK_SALARIES=<csv> APEX_ENV=<track> python dfs_showdown.py AWAY HOME [--anchor]"""
import os, sys, itertools, numpy as np, pandas as pd
from paths import OUT
import run_all as R
from params import norm_name, is_neutral, INJ
AWAY, HOME = sys.argv[1], sys.argv[2]; ANCHOR = "--anchor" in sys.argv; ROBUST = "--robust" in sys.argv
CAP = 50000; KFG = 3.9      # kicker: engine has no FG distance, so use the league-average DK value per made FG (approximate)
sal = pd.read_csv(os.environ["APEX_DK_SALARIES"])
sal["nkey"] = sal["Name"].map(norm_name)
fl = sal[sal["Roster Position"] == "FLEX"].set_index(["nkey", "TeamAbbrev"]); cp = sal[sal["Roster Position"] == "CPT"].set_index(["nkey", "TeamAbbrev"])
R.run_game(AWAY, HOME, neutral=is_neutral(AWAY, HOME), ns=20000); d = R.STORE.pop((AWAY, HOME)); A, H = d["A"], d["H"]

def dk(pl, sc=None):
    sc = sc or {}
    py = pl["pass_yds"] * sc.get("pass_yds", 1.0); ry = pl["rush_yds"] * sc.get("rush_yds", 1.0); cy = pl["rec_yds"] * sc.get("rec_yds", 1.0); rc = pl["rec"] * sc.get("rec", 1.0)
    base = 0.04 * pl["pass_yds"] + 4 * pl["pass_td"] - 2 * pl["pass_int"] + 0.1 * (pl["rush_yds"] + pl["rec_yds"]) + 6 * (pl["rush_td"] + pl["rec_td"]) + pl["rec"]
    flost = np.clip((base - pl["fp"]) / 2.0, 0, None)
    return (0.04 * py + 4 * pl["pass_td"] - 1 * pl["pass_int"] + 3 * (py >= 300) + 0.1 * ry + 6 * pl["rush_td"] + 3 * (ry >= 100) + rc + 0.1 * cy + 6 * pl["rec_td"] + 3 * (cy >= 100) - flost)
tier = lambda pa: np.select([pa == 0, pa <= 6, pa <= 13, pa <= 20, pa <= 27, pa <= 34], [10, 7, 4, 1, 0, -1], -4)

# book anchoring: scale a player's simulated yardage/receptions so the active-draw median equals the books' main line (clamped 0.5-2.0). TDs are NOT anchored.
scales = {}
if True:
    E = pd.read_csv(os.environ.get("APEX_EDGES", "../../var/out_market/edges_all_rows.csv"))
    E = E[E.is_main_line & (E.side == "over") & E.market.isin(["pass_yds", "rush_yds", "rec_yds", "rec"])]
    g = E.groupby(["player", "market"]).agg(line=("line", "first"), feeds=("book", "nunique")).reset_index()
    for r in g[g.feeds >= 3].itertuples(): scales[(norm_name(r.player), r.market)] = r.line

def build(anchor):
    arrs, meta = {}, {}
    for t, own, opp in ((AWAY, A, H), (HOME, H, A)):
        for pl in d["players"][t]:
            k = (norm_name(pl["player"]), t)
            if k not in fl.index or pl["p_active"] < 0.03 or pl["mask"].sum() < 200: continue
            m = pl["mask"]; sc = {}
            for mk in ("pass_yds", "rush_yds", "rec_yds", "rec"):
                ln = scales.get((k[0], mk)) if anchor else None
                if ln is not None:
                    med = float(np.median(pl[mk][m]))
                    if med > 0 and ln > 0: sc[mk] = float(np.clip(ln / med, 0.5, 2.0))
            arrs[k] = (dk(pl, sc) * m).astype(np.float32); meta[k] = dict(pos=pl["pos"], p_active=pl["p_active"], scale=sc)
        kk = R.kicker(t)
        if kk is not None:
            k = (norm_name(kk.player), t)
            if k in fl.index: arrs[k] = (KFG * own["fg"] + own["xp_off"] + own["xp_d"]).astype(np.float32); meta[k] = dict(pos="K", p_active=1.0, scale={})
    for t, own, opp in ((AWAY, A, H), (HOME, H, A)):
        k = (norm_name({"DAL": "Cowboys", "TB": "Buccaneers"}.get(t, t)), t)
        if k in fl.index: arrs[k] = (opp["sacks"] + 2 * opp["int_n"] + 2 * opp["fl_n"] + 6 * own["dtd"] + 2 * own["saf"] + tier(opp["off_pts"])).astype(np.float32); meta[k] = dict(pos="DST", p_active=1.0, scale={})
    return arrs, meta
arrs, meta = build(ANCHOR)
arrs_raw, _ = build(False); arrs_anc, meta_anc = build(True)
# eligibility: DK status OUT/IR and model p_active 0 excluded
ok = []
for k in arrs:
    st = str(fl.loc[k, "Status"]) if not isinstance(fl.loc[k], pd.DataFrame) else str(fl.loc[k].iloc[0]["Status"])
    if st in ("OUT", "IR", "O"): continue
    ok.append(k)
mean = {k: float(arrs[k].mean()) for k in ok}
pool = [k for k in ok if mean[k] >= 1.0]
ns = len(next(iter(arrs.values()))); S = np.arange(ns) % 2 == 0; Ho = ~S
assets, X, cost = [], [], []
for k in pool:
    fs = int(fl.loc[k, "Salary"]); cs = int(cp.loc[k, "Salary"])
    assets.append((k, "CPT")); X.append(arrs[k] * 1.5); cost.append(cs)
    assets.append((k, "FLEX")); X.append(arrs[k]); cost.append(fs)
X = np.vstack(X); cost = np.array(cost); team = np.array([a[0][1] == AWAY for a in assets]); pid = np.array([pool.index(a[0]) for a in assets]); iscpt = np.array([a[1] == "CPT" for a in assets])
n = len(pool); cpt_idx = np.where(iscpt)[0]; flex_idx = np.where(~iscpt)[0]
lineups = []
for c in cpt_idx:
    rest = [f for f in flex_idx if pid[f] != pid[c]]
    for comb in itertools.combinations(rest, 5):
        if cost[c] + cost[list(comb)].sum() > CAP: continue
        tm = team[[c, *comb]]
        if tm.all() or (~tm).all(): continue
        lineups.append((c, *comb))
L = np.array(lineups, dtype=np.int32); print("pool", n, "lineups", len(L), flush=True)
mu = X.mean(1); C = np.cov(X[:, S]); 
m_l = mu[L].sum(1); v_l = C[L[:, :, None], L[:, None, :]].sum((1, 2)); proxy = m_l + 2.3 * np.sqrt(np.maximum(v_l, 0))
cand = np.unique(np.concatenate([np.argsort(-proxy)[:30000], np.argsort(-m_l)[:3000]]))
XS, XH = X[:, S], X[:, Ho]; kS = int(0.99 * S.sum()); res = []
for i in range(0, len(cand), 400):
    ix = cand[i:i + 400]; sc = XS[L[ix]].sum(1)         # (chunk, nsims)
    part = np.partition(sc, kS, axis=1)[:, kS:]
    res.append(np.column_stack([ix, sc.mean(1), part.mean(1)]))
res = np.vstack(res); order = np.argsort(-res[:, 2])
rows = []
for j in order[:25]:
    li = int(res[j, 0]); h = XH[L[li]].sum(0); hk = int(0.99 * len(h))
    cap_ = L[li, 0]; flex = L[li, 1:]
    rows.append(dict(rank=len(rows) + 1, captain=f"{assets[cap_][0][0]}", flex=" | ".join(assets[f][0][0] for f in flex), salary=int(cost[L[li]].sum()), search_mean=res[j, 1], search_top1pct=res[j, 2],
                     hold_mean=float(h.mean()), hold_p90=float(np.percentile(h, 90)), hold_p99=float(np.percentile(h, 99)), hold_top1pct_mean=float(np.partition(h, hk)[hk:].mean()), hold_p_ge_150=float((h >= 150).mean()), hold_p_ge_200=float((h >= 200).mean())))
R_ = pd.DataFrame(rows); tag = "anchored" if ANCHOR else "raw"
R_.to_csv(OUT + f"showdown_{AWAY}_{HOME}_{tag}.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(R_.head(8)[["rank", "captain", "flex", "salary", "search_mean", "hold_mean", "hold_p90", "hold_p99", "hold_top1pct_mean", "hold_p_ge_150", "hold_p_ge_200"]].round(1).to_string(index=False))
sc_applied = {a: m["scale"] for a, m in meta.items() if m["scale"]}
if ANCHOR: print("anchoring scales applied:", {f"{k[0]}": {m_: round(v, 2) for m_, v in s.items()} for k, s in sc_applied.items()})

if ROBUST:
    def Xof(ar):
        return np.vstack([ar[k] * (1.5 if r == "CPT" else 1.0) for k, r in assets])
    XR, XA = Xof(arrs_raw), Xof(arrs_anc)
    cands = set()
    for XX in (XR, XA):
        XSx = XX[:, S]; r2 = []
        for i in range(0, len(cand), 400):
            ix = cand[i:i + 400]; sc = XSx[L[ix]].sum(1); part = np.partition(sc, kS, axis=1)[:, kS:]; r2.append(np.column_stack([ix, part.mean(1)]))
        r2 = np.vstack(r2); cands |= set(r2[np.argsort(-r2[:, 1])[:150], 0].astype(int))
    out = []
    for li in cands:
        row = dict(li=li)
        for nm, XX in (("raw", XR), ("anc", XA)):
            h = XX[L[li]][:, Ho].sum(0); hk = int(0.99 * len(h))
            row.update({f"{nm}_mean": float(h.mean()), f"{nm}_p99": float(np.percentile(h, 99)), f"{nm}_top1": float(np.partition(h, hk)[hk:].mean()), f"{nm}_pge150": float((h >= 150).mean() * 100), f"{nm}_pge175": float((h >= 175).mean() * 100)})
        row["worst_top1"] = min(row["raw_top1"], row["anc_top1"]); out.append(row)
    Q = pd.DataFrame(out).sort_values("worst_top1", ascending=False).head(12)
    Q["captain"] = [assets[L[i, 0]][0][0] for i in Q.li]; Q["flex"] = [" | ".join(assets[f][0][0] for f in L[i, 1:]) for i in Q.li]; Q["salary"] = [int(cost[L[i]].sum()) for i in Q.li]
    Q.drop(columns="li").to_csv(OUT + f"showdown_{AWAY}_{HOME}_robust.csv", index=False)
    print(Q[["captain", "flex", "salary", "raw_mean", "anc_mean", "raw_p99", "anc_p99", "raw_top1", "anc_top1", "raw_pge150", "anc_pge150", "raw_pge175", "anc_pge175"]].round(1).to_string(index=False))
