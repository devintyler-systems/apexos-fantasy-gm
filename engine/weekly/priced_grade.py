"""Grade a priced window (edges_all_rows.csv from price_odds.py) against nflverse actuals. Read-only; prints tables, writes nothing under runs/.

Usage: python priced_grade.py EDGES_CSV SEASON WEEK

Per (game, player, team, market, side, line) it takes the consensus de-vigged book probability (mean over books), the engine probability and the best price, then reports
  1. Brier of the engine, the book and the 50/50 blend (DECISIONS #53) per market, main lines and all lines (each main line appears once, over side, so the 50% hit rate of paired sides is not a result);
  2. blend-weight sweep w in 0..1 (final = book + w x (model - book)) on main lines, overall and per market, and the hit rate of the engine's lean by |gap| bucket;
  3. what the value-board rule would have published (main line, not pass yards, no gap flag, p_active >= .9, EV > 0 at the best price) and its units at 1 unit flat;
  4. anytime TDs: Brier of engine, book and blend, and units of EV > 5% bets (one-sided markets use the flat 10% haircut: estimated prices).
Pushes and players with no logged stat row are dropped. Prices and lines stay in var/; this script prints aggregates only when run with the default outputs.
"""
import sys

import numpy as np
import pandas as pd

from load import norm_name
from paths import NFLV

COL = {"rec": "receptions", "pass_cmp": "completions", "pass_att": "attempts", "rush_att": "carries", "pass_yds": "passing_yards", "rec_yds": "receiving_yards",
       "rush_yds": "rushing_yards", "pass_td": "passing_tds"}
KEY = ["game", "player", "team", "market", "side", "line"]


def actual(st, r):
    k = (norm_name(r.player), r.team)
    if k not in st.index:
        return np.nan
    s = st.loc[k]
    if r.market == "anytime_td":
        return float(s.rushing_tds + s.receiving_tds > 0)
    if r.market == "rush_rec_yds":
        return float(s.rushing_yards + s.receiving_yards)
    if r.market == "first_td" or r.market not in COL:
        return np.nan
    return float(s[COL[r.market]])


def grade(path, season, week):
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet")
    st = st[(st.season_type == "REG") & (st.week == week)].copy(); st["nkey"] = st.player_display_name.map(norm_name)
    st = st.drop_duplicates(["nkey", "team"]).set_index(["nkey", "team"])
    e = pd.read_csv(path); e["line"] = e.line.fillna(-1)
    e["actual"] = [actual(st, r) for r in e.itertuples()]

    def hit(r):
        if np.isnan(r.actual):
            return np.nan
        if r.market == "anytime_td":
            return r.actual if r.side == "yes" else np.nan
        if r.actual == r.line:
            return np.nan
        return float(r.actual > r.line) if r.side == "over" else float(r.actual < r.line)

    e["hit"] = [hit(r) for r in e.itertuples()]
    d = e[e.hit.notna() & (e.p_active >= 0.5)]
    g = d.groupby(KEY).agg(model_p=("model_p", "first"), book_p=("novig_p", "mean"), hit=("hit", "first"), main=("is_main_line", "max"), gap=("model_gap_flag", "max"),
                           pa=("p_active", "first"), best=("odds", "max")).reset_index()
    g["final"] = g.book_p + 0.5 * (g.model_p - g.book_p)
    pay = lambda a: np.where(a < 0, 100 / (-a), a / 100)
    g["units"] = np.where(g.hit == 1, pay(g.best), -1.0)
    g["ev"] = g.final * pay(g.best) - (1 - g.final)
    return e, g


def brier(p, y):
    return float(((p - y) ** 2).mean())


def report(g):
    pd.set_option("display.width", 220)
    nt = g[g.market != "anytime_td"]
    ov = nt[nt.main & (nt.side == "over")].copy()                      # one row per main line
    rows = [dict(market=m, n=len(x), hit_over=x.hit.mean(), model=brier(x.model_p, x.hit), book=brier(x.book_p, x.hit), blend=brier(x.final, x.hit)) for m, x in ov.groupby("market")]
    rows.append(dict(market="ALL main", n=len(ov), hit_over=ov.hit.mean(), model=brier(ov.model_p, ov.hit), book=brier(ov.book_p, ov.hit), blend=brier(ov.final, ov.hit)))
    print("## Brier on the main line (over side), lower is better\n" + pd.DataFrame(rows).round(3).to_string(index=False))
    print("\n## Blend weight sweep, final = book + w x (model - book), main lines")
    for w in (0, .1, .25, .5, .75, 1):
        print(f"w={w}: Brier {brier(ov.book_p + w * (ov.model_p - ov.book_p), ov.hit):.4f}")
    ov["gap_"] = ov.model_p - ov.book_p; ov["lean_hit"] = np.where(ov.gap_ > 0, ov.hit, 1 - ov.hit); ov["ag"] = ov.gap_.abs()
    print("\n## Hit rate of the engine's lean by |model - book| (n, hit)")
    for lo, hi in [(0, .05), (.05, .1), (.1, .15), (.15, .25), (.25, 1)]:
        x = ov[(ov.ag >= lo) & (ov.ag < hi)]
        print(f"|gap| {lo:.2f}-{hi:.2f}: n={len(x)} hit={x.lean_hit.mean():.3f}")
    print(f"all: n={len(ov)} hit={ov.lean_hit.mean():.3f}")
    sel = nt[nt.main & (nt.market != "pass_yds") & (nt.gap == False) & (nt.pa >= .9) & (nt.ev > 0)]
    print(f"\n## Value-board rule picks: n={len(sel)} hit={sel.hit.mean():.3f} units={sel.units.sum():.2f}")
    for s, x in sel.groupby("side"):
        print(f"  {s}: n={len(x)} hit={x.hit.mean():.3f} units={x.units.sum():.2f}")
    t = g[g.market == "anytime_td"]
    if len(t):
        print(f"\n## Anytime TD: n={len(t)} Brier model {brier(t.model_p, t.hit):.4f} book {brier(t.book_p, t.hit):.4f} blend {brier(t.final, t.hit):.4f}; base rate {t.hit.mean():.3f}")
        x = t[t.ev > .05]
        print(f"  EV > 5% (estimated prices): n={len(x)} hit={x.hit.mean():.3f} units={x.units.sum():.2f}")


if __name__ == "__main__":
    e, g = grade(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    print(f"rows {len(e)}, graded consensus lines {len(g)}")
    report(g)
