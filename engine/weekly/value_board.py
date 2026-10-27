"""Confidence and value board from price_odds output: calibrated probability and expected value at the best available price.

Usage: python value_board.py PRICE_OUT_DIR   (the directory holding edges_all_rows.csv from price_odds.py)
For every (player, market, side, line): model probability, the books' de-vigged probability (mean across books; one-sided touchdown markets use price_odds's flat-haircut estimate), the blend
final_p = book + 0.5 x (model - book) (the weight that scored best against real prices in Week 7, DECISIONS #53), the best price across books, and EV = final_p x payout - (1 - final_p).
Flags: GAP = the model is 15+ points from the book (Sunday: lines 25+ points off hit 49%), >85 = the model is above the 85 percent ceiling, est = one-sided price with an estimated de-vig.
This ranks lines; it is not a bet instruction. Passing yards is excluded from the confidence list (the model's Brier was 0.297 against the books' 0.251 in Week 7)."""
import sys

import numpy as np
import pandas as pd


def build(path):
    e = pd.read_csv(path + "/edges_all_rows.csv"); e["line"] = e.line.fillna(-1)
    pay = lambda a: np.where(np.asarray(a, float) < 0, 100 / (-np.asarray(a, float)), np.asarray(a, float) / 100)
    key = ["player", "team", "market", "side", "line"]
    g = e.groupby(key).agg(model_p=("model_p", "first"), book_p=("novig_p", "mean"), nb=("book", "nunique"), pa=("p_active", "first"), main=("is_main_line", "max"), gapflag=("model_gap_flag", "max"),
                           ceil=("model_gt_85_suppress", "max"), best_odds=("odds", "max"), est=("novig_method", lambda s: s.str.startswith("Estimated").any())).reset_index()
    bk = e.loc[e.groupby(key).odds.idxmax(), key + ["book"]].rename(columns={"book": "best_book"})
    g = g.merge(bk, on=key)
    g["final_p"] = g.book_p + 0.5 * (g.model_p - g.book_p); g["gap"] = g.model_p - g.book_p
    g["ev"] = g.final_p * pay(g.best_odds) - (1 - g.final_p)
    return g[g.pa >= 0.9]


def fmt(df, n):
    out = []
    for i, r in enumerate(df.head(n).itertuples(), 1):
        sd = "yes" if r.side == "yes" else r.side[0].upper(); ln = "" if r.line == -1 else f" {r.line:g}"
        out.append(f"| {i} | {r.player} {r.team} | {r.market} {sd}{ln} | {r.final_p * 100:.0f}% | {r.model_p * 100:.0f}/{r.book_p * 100:.0f} | {r.best_odds:+.0f} {r.best_book} | {r.ev * 100:+.0f}% | {'est ' if r.est else ''}{'GAP ' if r.gapflag else ''}{'>85' if r.ceil else ''} |")
    return "\n".join(out)


if __name__ == "__main__":
    g = build(sys.argv[1]); tw = g[~g.market.isin(["anytime_td", "first_td"]) & (g.main == True)]
    print("HIGHEST CONFIDENCE\n" + fmt(tw[tw.market != "pass_yds"].sort_values("final_p", ascending=False), 12))
    print("\nHIGHEST VALUE\n" + fmt(g[(g.market != "pass_yds") & (g.final_p >= .3) & (g.gap.abs() <= .25)].sort_values("ev", ascending=False), 14))
    print("\nANYTIME TD\n" + fmt(g[g.market == "anytime_td"].sort_values("final_p", ascending=False), 14))
