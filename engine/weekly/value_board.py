"""Confidence and value board from price_odds output: calibrated probability and expected value at the best available price.

Usage: python value_board.py PRICE_OUT_DIR   (the directory holding edges_all_rows.csv from price_odds.py)
For every (player, market, side, line): model probability, the books' de-vigged probability (mean across books; one-sided touchdown markets use price_odds's flat-haircut estimate), the blend
final_p = book + w x (model - book) with w per market (DECISIONS #64, owner-approved 2026-11-03: w = 0.5 for touchdown markets, 0 for everything else, because the book beat the engine and the
50/50 blend on every non-touchdown market in the Week 7 Monday and Week 8 late windows), the best price across books, and EV = final_p x payout - (1 - final_p).
Flags: GAP = the model is 15+ points from the book (Sunday: lines 25+ points off hit 49%), >85 = the model is above the 85 percent ceiling, est = one-sided price with an estimated de-vig.
This ranks lines; it is not a bet instruction. Non-touchdown markets are INFORMATION ONLY: they are listed as engine versus book with no PLAY/LEAN label and no EV ranking, until the calibration ledger
holds four priced windows where the blend beats the book for that market (APEX_BLEND_W_NONTD overrides the non-touchdown weight for that test, default 0)."""
import os
import sys

import numpy as np
import pandas as pd


TD_MARKETS = ("anytime_td", "first_td", "pass_td")
W_TD = 0.5
W_NONTD = float(os.environ.get("APEX_BLEND_W_NONTD", 0.0))


def blend_weight(market):
    return W_TD if market in TD_MARKETS else W_NONTD


def build(path):
    e = pd.read_csv(path + "/edges_all_rows.csv"); e["line"] = e.line.fillna(-1)
    pay = lambda a: np.where(np.asarray(a, float) < 0, 100 / (-np.asarray(a, float)), np.asarray(a, float) / 100)
    key = ["player", "team", "market", "side", "line"]
    g = e.groupby(key).agg(model_p=("model_p", "first"), book_p=("novig_p", "mean"), nb=("book", "nunique"), pa=("p_active", "first"), main=("is_main_line", "max"), gapflag=("model_gap_flag", "max"),
                           ceil=("model_gt_85_suppress", "max"), best_odds=("odds", "max"), est=("novig_method", lambda s: s.str.startswith("Estimated").any())).reset_index()
    bk = e.loc[e.groupby(key).odds.idxmax(), key + ["book"]].rename(columns={"book": "best_book"})
    g = g.merge(bk, on=key)
    g["w"] = g.market.map(blend_weight); g["final_p"] = g.book_p + g.w * (g.model_p - g.book_p); g["gap"] = g.model_p - g.book_p
    g["ev"] = g.final_p * pay(g.best_odds) - (1 - g.final_p)
    return g[g.pa >= 0.9]


def fmt(df, n):
    out = []
    for i, r in enumerate(df.head(n).itertuples(), 1):
        sd = "yes" if r.side == "yes" else r.side[0].upper(); ln = "" if r.line == -1 else f" {r.line:g}"
        out.append(f"| {i} | {r.player} {r.team} | {r.market} {sd}{ln} | {r.final_p * 100:.0f}% | {r.model_p * 100:.0f}/{r.book_p * 100:.0f} | {r.best_odds:+.0f} {r.best_book} | {r.ev * 100:+.0f}% | {'est ' if r.est else ''}{'GAP ' if r.gapflag else ''}{'>85' if r.ceil else ''} |")
    return "\n".join(out)


if __name__ == "__main__":
    g = build(sys.argv[1]); td = g[g.market.isin(TD_MARKETS)]; tw = td[(td.main == True) & (td.market == "pass_td")]
    print("TOUCHDOWN MARKETS (blend w=0.5; the only markets labelled for plays)\n" + fmt(td[td.market == "anytime_td"].sort_values("final_p", ascending=False), 14))
    print("\nPASS TD, MAIN LINE\n" + fmt(tw.sort_values("final_p", ascending=False), 10))
    info = g[~g.market.isin(TD_MARKETS) & (g.main == True) & (g.side == "over")].copy(); info["ag"] = info.gap.abs()
    print("\nINFORMATION ONLY, NOT PLAYS (non-touchdown main lines, engine versus book over probability, sorted by size of disagreement; DECISIONS #64)\n" + fmt(info.sort_values("ag", ascending=False), 20))
