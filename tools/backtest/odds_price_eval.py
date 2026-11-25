"""P-1b: price backtest player-games against historical book prices (var/odds_hist from odds_backfill.py). Post-sim, no engine change.

  python tools/backtest/odds_price_eval.py td   TAG [TAG ...]            anytime TD: engine vs book vs blend, LOSO blend weight, 5-point rule P&L
  python tools/backtest/odds_price_eval.py yds  TAG [--dir var/odds_hist/yds]   rec/rush/pass yards over-under, information only (DECISIONS #64)

Scope (td): RB/WR/TE in the backtest pickle with an offensive snap that week and a listed book price (same team, same game).
Settlement = rushing + receiving + special-teams + fumble-recovery TDs >= 1 (book rules; the engine models rush + rec only).
Book de-vig (anytime TD is one-sided at every book except barstool):
  mult  : multiplicative, p = k_book x implied, k_book = sum(hits) / sum(implied) for that book over the OTHER two seasons (over-round estimated out of sample)
  flat  : implied x 0.90 (the price_odds.py haircut)
  2way  : yes / (yes + no) where a No price exists (barstool only), else mult
Consensus = mean of the per-book de-vigged probabilities (2way where a No price exists, else mult) (value_board.py book_p). Bets are flat 1 unit at the best listed price across books.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from evaluate import load, SEASONS, NV2T, REPO  # noqa: E402
from load import norm_name  # noqa: E402
from paths import NFLV  # noqa: E402

ODIR = os.path.join(REPO, "var", "odds_hist")
RNG = np.random.default_rng(20261125)
imp = lambda a: np.where(np.asarray(a, float) < 0, -np.asarray(a, float) / (100 - np.asarray(a, float)), 100 / (100 + np.asarray(a, float)))
pay = lambda a: np.where(np.asarray(a, float) < 0, 100 / -np.asarray(a, float), np.asarray(a, float) / 100)
def ll(p, y): p = np.clip(p, .01, .99); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
def br(p, y): return float(np.mean((np.asarray(p) - y) ** 2))


def games():
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[g.season.isin(SEASONS) & (g.game_type == "REG")].copy()
    for c in ("home_team", "away_team"): g[c] = g[c].replace(NV2T)
    return g


def engine(tag):
    D, _ = load(tag); D = D.copy()
    xs = []
    for S in SEASONS:
        st = pd.read_parquet(NFLV + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy()
        st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name); st["season"] = S
        xs.append(st[["season", "week", "nkey", "team", "special_teams_tds", "fumble_recovery_tds"]])
    D = D.merge(pd.concat(xs), on=["season", "week", "nkey", "team"], how="left").fillna({"special_teams_tds": 0, "fumble_recovery_tds": 0})
    D["y"] = ((D.rushing_tds + D.receiving_tds + D.special_teams_tds + D.fumble_recovery_tds) >= 1).astype(float)
    g = games(); m = {}
    for r in g.itertuples():
        m[(r.season, r.week, r.away_team)] = r.game_id; m[(r.season, r.week, r.home_team)] = r.game_id
    D["game_id"] = [m.get(k) for k in zip(D.season, D.week, D.team)]
    return D


def odds_rows(odir, kind):
    rows = []
    for f in sorted(glob.glob(os.path.join(odir, "*.json"))):
        d = json.load(open(f)); ev = d.get("data") or {}
        for b in ev.get("bookmakers", []):
            for mk in b.get("markets", []):
                for o in mk.get("outcomes", []):
                    rows.append(dict(game_id=d["game_id"], book=b["key"], market=mk["key"], player=o.get("description"), side=o["name"].lower(), point=o.get("point"), price=o["price"]))
    R = pd.DataFrame(rows)
    if len(R): R["nkey"] = R.player.astype(str).str.replace(r"\s*\([A-Z]{2,3}\)\s*$", "", regex=True).map(norm_name)
    return R


def attach(R, D, keycols):
    """match book names to pickle players in the same game; alias fallback = same game, same last name and first initial, one candidate."""
    E = D[D.game_id.notna()]
    idx = {(g, k): i for i, g, k in zip(E.index, E.game_id, E.nkey)}
    by_last = {}
    for i, g, k in zip(E.index, E.game_id, E.nkey):
        if k.split(): by_last.setdefault((g, k.split()[-1], k[:1]), []).append(i)
    hit = []
    for g, k in zip(R.game_id, R.nkey):
        i = idx.get((g, k))
        if i is None and k.split():
            c = by_last.get((g, k.split()[-1], k[:1]), []); i = c[0] if len(c) == 1 else None
        hit.append(i)
    R = R.assign(di=hit); n0 = R[keycols].drop_duplicates().shape[0]
    M = R[R.di.notna()].copy(); M["di"] = M.di.astype(int)
    print(f"matched {M[keycols].drop_duplicates().shape[0]} of {n0} book player-markets to pickle players with a snap")
    return M


def boot_ci(df, reps=4000):
    """cluster bootstrap by game: 90% interval for units and ROI."""
    if not len(df): return (np.nan, np.nan), (np.nan, np.nan)
    gs = df.groupby("game_id").agg(u=("pl", "sum"), n=("pl", "size")); u, n = gs.u.values, gs.n.values
    ix = RNG.integers(0, len(gs), size=(reps, len(gs))); U = u[ix].sum(1); N = n[ix].sum(1)
    return tuple(np.percentile(U, [5, 95]).round(1)), tuple((np.percentile(U / N, [5, 95]) * 100).round(1))


def bets(T, rule, label):
    out = []
    for S in list(SEASONS) + ["all"]:
        b = T[rule & ((T.season == S) if S != "all" else True)]
        lo, roi = boot_ci(b)
        out.append(dict(rule=label, season=S, bets=len(b), hit=round(b.y.mean(), 3) if len(b) else np.nan, avg_odds=round(b.best.median(), 0) if len(b) else np.nan,
                        units=round(b.pl.sum(), 1), roi_pct=round(100 * b.pl.mean(), 1) if len(b) else np.nan, units_90=lo, roi_90=roi))
    return out


def loso_w(T, pcol, bcol):
    grid = np.round(np.arange(0, 1.001, .01), 2); rows = []
    for S in SEASONS:
        tr, te = T[T.season != S], T[T.season == S]
        w = grid[int(np.argmin([ll(tr[bcol] + x * (tr[pcol] - tr[bcol]), tr.y) for x in grid]))]
        p = te[bcol] + w * (te[pcol] - te[bcol])
        rows.append(dict(season=S, w_fit=w, ll_held=round(ll(p, te.y), 5), ll_book=round(ll(te[bcol], te.y), 5), ll_w05=round(ll(te[bcol] + .5 * (te[pcol] - te[bcol]), te.y), 5)))
    return pd.DataFrame(rows)


def td(tags):
    for tag in tags:
        D = engine(tag); D = D[D.pos.isin(["RB", "WR", "TE"])]
        R = odds_rows(ODIR, "td"); R = R[R.market == "player_anytime_td"]
        M = attach(R, D, ["game_id", "nkey"])
        M = M.drop_duplicates(["game_id", "book", "di", "side"])
        yes = M[M.side == "yes"].copy(); no = M[M.side == "no"][["game_id", "book", "di", "price"]].rename(columns={"price": "no_price"})
        yes = yes.merge(no, on=["game_id", "book", "di"], how="left")
        yes["imp"] = imp(yes.price); yes["season"] = D.loc[yes.di, "season"].values; yes["y"] = D.loc[yes.di, "y"].values
        # out-of-sample over-round per book
        yes["k"] = np.nan
        for S in SEASONS:
            tr = yes[yes.season != S].groupby("book").agg(h=("y", "sum"), i=("imp", "sum")); k = (tr.h / tr.i)
            sel = yes.season == S
            k_all = float(tr.h.sum() / tr.i.sum()) if len(tr) else np.nan   # book with no other-season rows: pooled factor of the other seasons
            if sel.any() and len(tr): yes.loc[sel, "k"] = yes.loc[sel, "book"].map(k).astype(float).fillna(k_all).values
        yes["p_mult"] = np.clip(yes.k * yes.imp, .005, .99); yes["p_flat"] = yes.imp * .90
        tw = yes.no_price.notna(); yes["p_2way"] = yes.p_mult
        yes.loc[tw, "p_2way"] = yes.imp[tw] / (yes.imp[tw] + imp(yes.no_price[tw]))
        kk = yes.groupby(["season", "book"]).k.first().unstack().round(3)
        print(f"\n=== {tag}: out-of-sample multiplicative factor k per book (hits / implied over the other two seasons; flat haircut = 0.90)\n{kk.to_string()}")
        if tw.any():
            print("barstool two-way: mean(yes+no implied) =", round(float((yes.imp[tw] + imp(yes.no_price[tw])).mean()), 3),
                  "| k implied by two-way (2way/implied) =", round(float((yes.p_2way[tw] / yes.imp[tw]).mean()), 3))
        # per-book scores (each book's rows; engine on the same rows)
        pb = []
        for b, g in yes.groupby("book"):
            pe = D.loc[g.di, "any_td"].values
            for S in list(SEASONS) + ["all"]:
                s = (g.season == S).values if S != "all" else np.ones(len(g), bool)
                if s.sum() < 50: continue
                y = g.y.values[s]
                pb.append(dict(book=b, season=S, n=int(s.sum()), eng_ll=ll(pe[s], y), mult_ll=ll(g.p_mult.values[s], y), flat_ll=ll(g.p_flat.values[s], y),
                               blend_ll=ll(.5 * (pe[s] + g.p_mult.values[s]), y), eng_br=br(pe[s], y), mult_br=br(g.p_mult.values[s], y), blend_br=br(.5 * (pe[s] + g.p_mult.values[s]), y)))
        pb = pd.DataFrame(pb)
        print("\nper book (book = mult de-vig; blend = 50/50 with the engine; lower is better)\n" + pb[pb.season == "all"].round(5).to_string(index=False))
        # consensus per player-game
        T = yes.groupby("di").agg(cons=("p_2way", "mean"), cons_flat=("p_flat", "mean"), cons_2way=("p_2way", "mean"), nb=("book", "nunique"), best=("price", "max"), season=("season", "first"), y=("y", "first"),
                                  game_id=("game_id", "first")).reset_index()
        T["eng"] = np.clip(D.loc[T.di, "any_td"].values, .005, .99); T["pa"] = D.loc[T.di, "p_active"].values; T["pos"] = D.loc[T.di, "pos"].values
        T["blend"] = T.cons + .5 * (T.eng - T.cons)
        rows = []
        for S in list(SEASONS) + ["all"]:
            t = T if S == "all" else T[T.season == S]
            rows.append(dict(season=S, n=len(t), hit=round(t.y.mean(), 4), eng_mean=round(t.eng.mean(), 4), book_mean=round(t.cons.mean(), 4),
                             eng_br=br(t.eng, t.y), book_br=br(t.cons, t.y), blend_br=br(t.blend, t.y), flatbook_br=br(t.cons_flat, t.y),
                             eng_ll=ll(t.eng, t.y), book_ll=ll(t.cons, t.y), blend_ll=ll(t.blend, t.y), flatbook_ll=ll(t.cons_flat, t.y), flatblend_ll=ll(t.cons_flat + .5 * (t.eng - t.cons_flat), t.y)))
        print("\nconsensus (book = mean of per-book mult de-vig; flatbook = mean of 0.90 x implied)\n" + pd.DataFrame(rows).round(5).to_string(index=False))
        print("\nLOSO blend weight (fit w on two seasons, score held-out; final = book + w x (engine - book))")
        print("mult book:\n" + loso_w(T, "eng", "cons").to_string(index=False))
        print("flat book:\n" + loso_w(T, "eng", "cons_flat").to_string(index=False))
        # bets: live rule = blended edge (final_p - book) >= 5 points, w 0.5, p_active >= 0.9, best price
        T["pl"] = np.where(T.y == 1, pay(T.best), -1.0)
        B = []
        for bcol, nm in (("cons", "mult"), ("cons_flat", "flat")):
            fin = T[bcol] + .5 * (T.eng - T[bcol]); act = T.pa >= .9
            B += bets(T, act & (fin - T[bcol] >= .05), f"{nm}: blended edge >= 5 (live rule)")
            B += bets(T, act & (T.eng - T[bcol] >= .05), f"{nm}: raw gap >= 5")
            ev = fin * pay(T.best) - (1 - fin)
            B += bets(T, act & (fin - T[bcol] >= .05) & (ev > 0), f"{nm}: blended edge >= 5 and EV>0 at best price")
        B += bets(T, (T.pa >= .9) & (T.eng - T.cons <= -.05), "control: engine 5+ below book (bet anyway)")
        B += bets(T, T.pa >= .9, "control: every listed player")
        print("\nflat 1-unit bets at best listed price; 90% interval = cluster bootstrap by game\n" + pd.DataFrame(B).to_string(index=False))
        T.to_pickle(os.path.join(REPO, "var", "bt", f"odds_td_{tag}.pkl"))


def cdf_from_q(x, q):
    """P(X <= x) from the pickle's mean-free quantiles (q10, q25, q75, q90; median = midpoint of q25/q75), linear between knots, exponential upper tail."""
    q10, q25, q75, q90 = q; q50 = .5 * (q25 + q75)
    kx = np.array([q10, q25, q50, q75, q90]); kp = np.array([.10, .25, .50, .75, .90])
    kx = np.maximum.accumulate(kx + np.arange(5) * 1e-6)
    if x >= kx[-1]:
        s = max((kx[-1] - kx[-2]) / np.log(2.5), 1.0); return 1 - .10 * np.exp(-(x - kx[-1]) / s)
    if x <= kx[0]:
        return .10 * max(x, 0) / kx[0] if kx[0] > 0 else .10
    return float(np.interp(x, kx, kp))


YMK = {"player_reception_yds": ("rec_yds", "receiving_yards"), "player_rush_yds": ("rush_yds", "rushing_yards"), "player_pass_yds": ("pass_yds", "passing_yards")}


def yds(tag, odir):
    D = engine(tag); R = odds_rows(odir, "yds"); R = R[R.market.isin(YMK) & R.side.isin(["over", "under"]) & R.point.notna()]
    M = attach(R, D, ["game_id", "nkey", "market"]).drop_duplicates(["game_id", "book", "market", "di", "side", "point"])
    w = M.pivot_table(index=["game_id", "book", "market", "di", "point"], columns="side", values="price", aggfunc="first").dropna().reset_index()
    io, iu = imp(w.over), imp(w.under); w["p_book"] = io / (io + iu)
    # main line per player-market = the line most books post (ties: closest to even)
    w["off"] = (w.p_book - .5).abs()
    sc = w.groupby(["di", "market", "point"]).agg(nb=("book", "nunique"), off=("off", "mean")).reset_index().sort_values(["nb", "off"], ascending=[False, True])
    main = sc.drop_duplicates(["di", "market"])[["di", "market", "point"]]
    w = w.merge(main, on=["di", "market", "point"])
    T = w.groupby(["di", "market", "point"]).agg(book=("p_book", "mean"), nb=("book", "nunique"), best_o=("over", "max"), best_u=("under", "max"), game_id=("game_id", "first")).reset_index()
    T["season"] = D.loc[T.di, "season"].values; T["pa"] = D.loc[T.di, "p_active"].values
    T["act"] = [D.at[i, YMK[m][1]] for i, m in zip(T.di, T.market)]
    T["eng"] = [1 - cdf_from_q(pt, [D.at[i, f"{YMK[m][0]}_q{k}"] for k in (10, 25, 75, 90)]) for i, m, pt in zip(T.di, T.market, T.point)]
    T["eng"] = T.eng.clip(.02, .98); T = T[T.act != T.point].copy(); T["y"] = (T.act > T.point).astype(float)
    T["blend"] = .5 * (T.eng + T.book)
    for mk, G in T.groupby("market"):
        rows = []
        for S in list(SEASONS) + ["all"]:
            t = G if S == "all" else G[G.season == S]
            rows.append(dict(season=S, n=len(t), over_rate=round(t.y.mean(), 3), eng_br=br(t.eng, t.y), book_br=br(t.book, t.y), blend_br=br(t.blend, t.y),
                             eng_ll=ll(t.eng, t.y), book_ll=ll(t.book, t.y), blend_ll=ll(t.blend, t.y)))
        print(f"\n=== {tag} {mk} main line, over probability (engine from pickle quantiles; book = two-way no-vig mean)\n" + pd.DataFrame(rows).round(5).to_string(index=False))
        print("LOSO blend weight:\n" + loso_w(G, "eng", "book").to_string(index=False))
        fin = G.book + .5 * (G.eng - G.book); act = G.pa >= .9
        ov = act & (fin - G.book >= .05); un = act & (G.book - fin >= .05)
        Bt = pd.concat([G[ov].assign(pl=np.where(G[ov].y == 1, pay(G[ov].best_o), -1.0), best=G[ov].best_o, yy=G[ov].y),
                        G[un].assign(pl=np.where(G[un].y == 0, pay(G[un].best_u), -1.0), best=G[un].best_u, yy=1 - G[un].y)])
        Bt["y"] = Bt.yy; Bt = Bt.assign(all_=True)
        print("blended edge >= 5 either side, best price (information only):\n" + pd.DataFrame(bets(Bt, Bt.all_, mk)).to_string(index=False))


if __name__ == "__main__":
    if sys.argv[1] == "td": td(sys.argv[2:])
    elif sys.argv[1] == "yds":
        a = sys.argv[2:]; d = a[a.index("--dir") + 1] if "--dir" in a else os.path.join(ODIR, "yds"); tags = [t for t in a if t != "--dir" and t != d]
        for t in tags: yds(t, d)
