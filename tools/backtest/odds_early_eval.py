"""Early-line test (DECISIONS #85): does the engine beat EARLY 2025 anytime-TD prices, and do prices move toward it by the close?

  python tools/backtest/odds_early_eval.py TAG [TAG ...]      (2025 weeks 4-12; early prices in var/odds_hist/early_2025, close in var/odds_hist)

Early snapshot = Wednesday 17:00Z of the game week (Tuesday 17:00Z kept for the three games pulled first that had a full board), before the first
injury report. Look-ahead control: the backtest engine uses the week's final injury report, so the PRIMARY population is players with no entry
of any kind on that week's nflverse injury report and p_active >= 0.9; the full population is reported as optimistic.
De-vig: p = k_book x implied with k_book = hits / implied on the 2023-24 close prices (out of sample for 2025; pooled k for books absent then),
the same k for early and close so price movement is not a de-vig artifact. Consensus = mean over books. Bets: 1 unit at the best early price.
CLV: per player and book quoting both snapshots, change in de-vigged probability early -> close (k x (implied_close - implied_early)), averaged over books.
"""
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import odds_price_eval as ope  # noqa: E402
from odds_price_eval import ll, br, imp, pay, RNG, REPO, NFLV, norm_name  # noqa: E402

EDIR = os.path.join(REPO, "var", "odds_hist", "early_2025")


def yes_rows(odir, D):
    R = ope.odds_rows(odir, "td"); R = R[(R.market == "player_anytime_td") & (R.side == "yes")]
    M = ope.attach(R, D, ["game_id", "nkey"]).drop_duplicates(["game_id", "book", "di"])
    M["imp"] = imp(M.price); M["season"] = D.loc[M.di, "season"].values; M["y"] = D.loc[M.di, "y"].values
    return M


def cboot(df, col, reps=4000):
    if not len(df): return (np.nan, np.nan)
    g = df.groupby("game_id")[col].agg(["sum", "size"]); s, n = g["sum"].values, g["size"].values
    ix = RNG.integers(0, len(g), size=(reps, len(g)))
    return tuple(np.round(np.percentile(s[ix].sum(1) / n[ix].sum(1), [5, 95]), 4))


def bet_row(name, b):
    lo = ope.boot_ci(b)
    return dict(rule=name, bets=len(b), hit=round(b.y.mean(), 3) if len(b) else np.nan, med_odds=b.best.median() if len(b) else np.nan,
                units=round(b.pl.sum(), 1), roi_pct=round(100 * b.pl.mean(), 1) if len(b) else np.nan, units_90=lo[0], roi_90=lo[1])


def run(tag):
    D = ope.engine(tag); D = D[D.pos.isin(["RB", "WR", "TE"])]
    C = yes_rows(ope.ODIR, D)
    tr = C[C.season.isin([2023, 2024])].groupby("book").agg(h=("y", "sum"), i=("imp", "sum")); k = tr.h / tr.i; k_all = float(tr.h.sum() / tr.i.sum())
    D25 = D[D.season == 2025]
    E = yes_rows(EDIR, D25); C = C[C.season == 2025].copy()
    for X in (E, C):
        X["k"] = X.book.map(k).astype(float).fillna(k_all); X["p"] = np.clip(X.k * X.imp, .005, .99); X["pf"] = X.imp * .90
    print(f"\n=== {tag}: early k from 2023-24 close (pooled {k_all:.3f}):", k.round(3).to_dict())
    print("early books:", E.book.value_counts().to_dict())
    agg = lambda X, s: X.groupby("di").agg(**{f"b_{s}": ("p", "mean"), f"bf_{s}": ("pf", "mean"), f"nb_{s}": ("book", "nunique"), f"best_{s}": ("price", "max")})
    T = agg(E, "e").join(agg(C, "c"), how="left").reset_index()
    T["eng"] = np.clip(D.loc[T.di, "any_td"].values, .005, .99); T["pa"] = D.loc[T.di, "p_active"].values; T["y"] = D.loc[T.di, "y"].values
    T["game_id"] = D.loc[T.di, "game_id"].values; T["week"] = D.loc[T.di, "week"].values; T["nkey"] = D.loc[T.di, "nkey"].values; T["team"] = D.loc[T.di, "team"].values
    inj = pd.read_parquet(NFLV + "injuries_2025.parquet"); inj = inj[inj.season_type == "REG"].copy()
    inj["team"] = inj.team.replace(ope.NV2T); inj["nkey"] = inj.full_name.map(norm_name)
    listed = set(zip(inj.week, inj.team, inj.nkey))
    T["on_report"] = [(w, t, n) in listed for w, t, n in zip(T.week, T.team, T.nkey)]
    T["healthy"] = ~T.on_report & (T.pa >= .9)
    snaps = pd.Series({f[:-5]: __import__("json").load(open(os.path.join(EDIR, f))).get("requested", "")[:10] for f in os.listdir(EDIR)})
    print("early snapshots used (date -> games):", snaps.value_counts().sort_index().to_dict())
    print(f"priced early: {len(T)} player-games; on injury report {int(T.on_report.sum())}; healthy (primary) {int(T.healthy.sum())}; with a close price {int(T.b_c.notna().sum())}")
    # early-vs-close CLV per book
    J = E[["di", "book", "game_id", "imp", "k"]].merge(C[["di", "book", "imp"]], on=["di", "book"], suffixes=("_e", "_c"))
    J["d"] = J.k * (J.imp_c - J.imp_e); mv = J.groupby("di").d.mean()
    T["move"] = T.di.map(mv)
    T["xmove"] = T.move - T.groupby("game_id").move.transform("mean")   # relative to the game's average move (removes the early over-round drift)
    # sensitivity: early over-round runs higher than the close; rescale early k so the early consensus mean equals the close mean on the same players
    s_ = T.b_c.notna(); r_ = float(T.b_c[s_].mean() / T.b_e[s_].mean()); T["b_e2"] = np.clip(T.b_e * r_, .005, .99)
    print(f"early/close de-vig level: mean early {T.b_e[s_].mean():.4f} vs close {T.b_c[s_].mean():.4f}; rescale factor {r_:.3f}")
    T["gap"] = T.eng - T.b_e; T["gap2"] = T.eng - T.b_e2
    for pop, P in (("PRIMARY: healthy, not on the injury report, p_active >= 0.9", T[T.healthy]), ("OPTIMISTIC: every priced player", T)):
        both = P[P.b_c.notna()]
        rows = []
        for nm, p in (("engine", both.eng), ("early book", both.b_e), ("close book", both.b_c), ("early 50/50", .5 * (both.eng + both.b_e)),
                      ("early w0.2", both.b_e + .2 * (both.eng - both.b_e)), ("early flat-0.90 book", both.bf_e),
                      ("early book rescaled", both.b_e2), ("early rescaled w0.2", both.b_e2 + .2 * (both.eng - both.b_e2)), ("close 50/50", .5 * (both.eng + both.b_c))):
            rows.append(dict(model=nm, n=len(both), brier=round(br(p, both.y), 5), logloss=round(ll(p, both.y), 5), mean_p=round(float(np.mean(p)), 4)))
        print(f"\n--- {tag} {pop}\nscores on players with both an early and a close price (hit rate {both.y.mean():.4f})\n" + pd.DataFrame(rows).to_string(index=False))
        P = P.assign(best=P.best_e, pl=np.where(P.y == 1, pay(P.best_e), -1.0))
        B = [bet_row("raw gap >= 5 vs early, best early price", P[P.gap >= .05]),
             bet_row("w0.2 blend, raw gap 5-10 vs early", P[(P.gap >= .05) & (P.gap < .10)]),
             bet_row("live rule at early (w0.5 blended edge >= 5, gap >= 10)", P[P.gap >= .10]),
             bet_row("rescaled early: raw gap >= 5", P[P.gap2 >= .05]),
             bet_row("rescaled early: gap 5-10", P[(P.gap2 >= .05) & (P.gap2 < .10)]),
             bet_row("control: every priced player at early best price", P)]
        if "PRIMARY" in pop:
            Pc = P[P.best_c.notna()].assign(best=lambda x: x.best_c, pl=lambda x: np.where(x.y == 1, pay(x.best_c), -1.0))
            B.append(bet_row("same raw gap >= 5 picks, bet at CLOSE best price", Pc[Pc.gap >= .05]))
        print("bets (90% interval = cluster bootstrap by game)\n" + pd.DataFrame(B).to_string(index=False))
        M = P[P.move.notna()]
        cl = []
        for nm, g in (("engine 5+ over early", M[M.gap >= .05]), ("engine 5-10 over early", M[(M.gap >= .05) & (M.gap < .10)]),
                      ("control: |gap| < 2", M[M.gap.abs() < .02]), ("engine 5+ under early", M[M.gap <= -.05])):
            g = g.assign(tw=(g.move > 0).astype(float))
            cl.append(dict(group=nm, n=len(g), mean_move_pts=round(100 * g.move.mean(), 2), move_90=tuple(np.round(100 * np.array(cboot(g, "move")), 2)),
                           rel_game_pts=round(100 * g.xmove.mean(), 2), rel_90=tuple(np.round(100 * np.array(cboot(g, "xmove")), 2)),
                           share_up=round(g.tw.mean(), 3), share_down=round((g.move < 0).mean(), 3), mean_gap_pts=round(100 * g.gap.mean(), 1)))
        print("CLV: change in de-vigged probability, early -> close (points; + = price moved toward a higher TD chance)\n" + pd.DataFrame(cl).to_string(index=False))
    T.to_pickle(os.path.join(REPO, "var", "bt", f"odds_early_{tag}.pkl"))


if __name__ == "__main__":
    for t in sys.argv[1:]: run(t)
