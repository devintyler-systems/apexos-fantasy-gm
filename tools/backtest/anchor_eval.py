"""DECISIONS #90: market-anchored player projections. Do book lines make better POINT projections than the engine, and does a blend beat both?

  python tools/backtest/anchor_eval.py TAG [TAG ...]
Needs var/bt/odds_yds_{TAG}.pkl and var/bt/odds_td_{TAG}.pkl (odds_price_eval.py yds / td).

Yardage (main lines, closing prices, 2023-25 weeks 4-12): for each player-game with a line, compare as point projections against the actual:
  engine mean; engine median (midpoint of the pickle's P25/P75); the book line itself; the book-implied median = the engine's distribution shape
  shifted until P(over the line) equals the de-vigged book probability (median_book = line + median_eng - Q_eng(1 - p_book)); and blends
  w * engine + (1 - w) * book_median with w fit leave-one-season-out (MAE on the other two seasons). Pushes were dropped upstream (act == line).
Anytime TD: engine, book, leave-one-season-out blend, restated as projection accuracy (Brier, log loss, and mean absolute error of P(TD)).
Coverage: share of projected DK points (skill players, p_active-weighted) held by players with at least one posted line in that game.
"""
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import odds_price_eval as ope  # noqa: E402
from odds_price_eval import ll, br, REPO, SEASONS  # noqa: E402

BT = os.path.join(REPO, "var", "bt")
YMK = {"player_reception_yds": "rec_yds", "player_rush_yds": "rush_yds", "player_pass_yds": "pass_yds"}
GRID = np.round(np.arange(0, 1.001, .05), 2)


def quant(p, q):
    """engine quantile function from the pickle knots (P10, P25, P50 = mid(P25, P75), P75, P90), linear, flat-extrapolated past P10/P90 by slope."""
    q10, q25, q75, q90 = q; q50 = .5 * (q25 + q75)
    kp = np.array([.10, .25, .50, .75, .90]); kx = np.maximum.accumulate(np.array([q10, q25, q50, q75, q90]) + np.arange(5) * 1e-6)
    if p < .10: return max(kx[0] - (kx[1] - kx[0]) / .15 * (.10 - p), 0.0)
    if p > .90: return kx[4] + (kx[4] - kx[3]) / .15 * (p - .90)
    return float(np.interp(p, kp, kx))


def loso_w(t, a, b):
    out = np.empty(len(t)); ws = {}
    for S in SEASONS:
        tr, te = t[t.season != S], (t.season == S).values
        w = GRID[int(np.argmin([np.abs(x * tr[a] + (1 - x) * tr[b] - tr.act).mean() for x in GRID]))]; ws[S] = w
        out[te] = (w * t[a] + (1 - w) * t[b]).values[te]
    return out, ws


def yardage(tag, D):
    T = pd.read_pickle(os.path.join(BT, f"odds_yds_{tag}.pkl")).copy()
    rows, wrows = [], []
    for mk, col in YMK.items():
        t = T[T.market == mk].copy()
        qs = [D.loc[t.di, f"{col}_q{k}"].values for k in (10, 25, 75, 90)]
        t["e_mean"] = D.loc[t.di, col].values; t["e_med"] = .5 * (qs[1] + qs[2])
        t["b_med"] = [pt + me - quant(1 - pb, [a, b, c, d]) for pt, me, pb, a, b, c, d in zip(t.point, t.e_med, t.book, *qs)]
        t["line"] = t.point
        t["bl_mean"], w1 = loso_w(t, "e_mean", "b_med"); t["bl_med"], w2 = loso_w(t, "e_med", "b_med")
        wrows.append(dict(market=mk, w_mean=w1, w_median=w2))
        for S in list(SEASONS) + ["all"]:
            g = t if S == "all" else t[t.season == S]
            r = dict(market=mk.replace("player_", ""), season=S, n=len(g))
            for c in ("e_mean", "e_med", "line", "b_med", "bl_mean", "bl_med"):
                r[c + "_mae"] = round(float((g[c] - g.act).abs().mean()), 2); r[c + "_rmse"] = round(float(np.sqrt(((g[c] - g.act) ** 2).mean())), 2)
            r["bias_e_mean"] = round(float((g.e_mean - g.act).mean()), 2); r["bias_b_med"] = round(float((g.b_med - g.act).mean()), 2)
            rows.append(r)
    R = pd.DataFrame(rows)
    print(f"\n=== {tag} yardage point projections (MAE / RMSE, yards; lower is better)")
    print(R[["market", "season", "n"] + [c for c in R.columns if c.endswith("_mae")] + ["bias_e_mean", "bias_b_med"]].to_string(index=False))
    print(R[["market", "season"] + [c for c in R.columns if c.endswith("_rmse")]].to_string(index=False))
    print("LOSO engine weight by held-out season:", pd.DataFrame(wrows).to_string(index=False))
    return R


def touchdown(tag):
    T = pd.read_pickle(os.path.join(BT, f"odds_td_{tag}.pkl")).rename(columns={"cons": "book"})
    lb = np.empty(len(T)); ws = {}
    for S in SEASONS:
        tr, te = T[T.season != S], (T.season == S).values
        w = GRID[int(np.argmin([ll(x * tr.eng + (1 - x) * tr.book, tr.y) for x in GRID]))]; ws[S] = w
        lb[te] = (w * T.eng + (1 - w) * T.book).values[te]
    T["lb"] = lb; rows = []
    for S in list(SEASONS) + ["all"]:
        g = T if S == "all" else T[T.season == S]
        r = dict(season=S, n=len(g))
        for c in ("eng", "book", "lb"):
            r[c + "_ll"] = round(ll(g[c], g.y), 5); r[c + "_br"] = round(br(g[c], g.y), 5)
        rows.append(r)
    print(f"\n=== {tag} anytime TD as a probability projection (LOSO engine weight {ws})\n" + pd.DataFrame(rows).to_string(index=False))


def coverage(tag, D):
    """uses the raw pre-game pickles (every projected player, not only those who later took a snap), p_active-weighted DK points."""
    Y = pd.read_pickle(os.path.join(BT, f"odds_yds_{tag}.pkl")); Td = pd.read_pickle(os.path.join(BT, f"odds_td_{tag}.pkl"))
    games = set(Y.game_id) & set(Td.game_id)
    key = lambda idx: set(zip(D.loc[list(idx), "game_id"], D.loc[list(idx), "nkey"]))
    yl, tl = key(set(Y.di)), key(set(Td.di))
    g = ope.games(); gid = {}
    for r in g.itertuples(): gid[(r.season, r.week, r.away_team)] = r.game_id; gid[(r.season, r.week, r.home_team)] = r.game_id
    raw = []
    for S in SEASONS:
        for W in range(4, 13):
            P = pd.read_pickle(os.path.join(BT, f"bt_{S}_w{W}_{tag}.pkl")).copy(); P["game_id"] = [gid.get((S, W, t)) for t in P.team]; raw.append(P)
    P = pd.concat(raw, ignore_index=True); P = P[P.game_id.isin(games)].copy()
    P["dk"] = P.p_active * (P.rec + .1 * P.rec_yds + .1 * P.rush_yds + 6 * P.exp_td + .04 * P.pass_yds + 4 * P.pass_td)
    k = list(zip(P.game_id, P.nkey)); P["has_yds"] = [x in yl for x in k]; P["has_td"] = [x in tl for x in k]; P["has_any"] = P.has_yds | P.has_td
    out = []
    for nm, q in (("RB/WR/TE", P[P.pos.isin(["RB", "WR", "TE"])]), ("QB", P[P.pos == "QB"]), ("QB+RB/WR/TE", P[P.pos.isin(["QB", "RB", "WR", "TE"])])):
        tot = q.dk.sum(); top = q.sort_values("dk", ascending=False)
        out.append(dict(group=nm, projected_players=len(q), dk_pts=round(tot), share_any_line=round(q[q.has_any].dk.sum() / tot, 3), share_yds_line=round(q[q.has_yds].dk.sum() / tot, 3),
                        share_td_line=round(q[q.has_td].dk.sum() / tot, 3), players_with_line=int(q.has_any.sum())))
    print(f"\n=== {tag} coverage: projected DK points (p_active-weighted, all projected players) held by players with a posted line, {len(games)} games\n" + pd.DataFrame(out).to_string(index=False))
    q = P[P.pos.isin(["RB", "WR", "TE"])].copy(); q["dk_bucket"] = pd.cut(q.dk, [-1, 2, 5, 10, 15, 100])
    print("RB/WR/TE share of player-games with a yardage line, by projected DK points:", q.groupby("dk_bucket", observed=True).has_yds.mean().round(3).to_dict())
    # TD lines in the TD set exist only for RB/WR/TE with a snap (QB TD lines were not kept); QB coverage counts pass-yds lines only


if __name__ == "__main__":
    for tag in sys.argv[1:]:
        D = ope.engine(tag)
        yardage(tag, D); touchdown(tag); coverage(tag, D)
