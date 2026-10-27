"""Grade a published priced board (the markdown tables written by value_board.py / the MNF full-run report) against nflverse actuals, with real prices.

Usage: python board_grade.py BOARD.md SEASON WEEK [--out report.md]

Parses rows `| Player TEAM | market | side line | confidence | model / book | price book | EV | label | reason |`, joins on normalised name + team,
and reports per label and per market: lines, hit rate, units at the best price (1 unit flat), mean model probability against the de-vigged book
probability, and Brier of both on the side chosen. Pushes are dropped. Read-only; touches no run folder.
"""
import argparse
import re
import sys

import numpy as np
import pandas as pd

from load import norm_name
from paths import NFLV

ACT = {"rec": "receptions", "rec_yds": "receiving_yards", "rush_yds": "rushing_yards", "rush_att": "carries", "pass_att": "attempts",
       "pass_cmp": "completions", "pass_yds": "passing_yards", "pass_td": "passing_tds"}
ROW = re.compile(r"^\|\s*(?P<player>.+?) (?P<team>[A-Z]{2,3}) \|\s*(?P<market>\w+) \|\s*(?P<side>[OU]|yes)\s*(?P<line>[\d.]*)\s*\|\s*(?P<conf>\d+)%\s*\|\s*(?P<model>\d+) / (?P<book>\d+)\s*\|\s*(?P<price>[+-]\d+) (?P<bk>.+?)\s*\|\s*(?P<ev>[+-]?\d+)%\s*\|\s*\*\*(?P<label>\w+)\*\*")


def parse(path):
    rows = []
    for ln in open(path, encoding="utf-8"):
        m = ROW.match(ln.strip())
        if m:
            d = m.groupdict(); d["line"] = float(d["line"]) if d["line"] else np.nan
            d.update(conf=int(d["conf"]) / 100, model=int(d["model"]) / 100, book=int(d["book"]) / 100, price=int(d["price"]), ev=int(d["ev"]) / 100)
            rows.append(d)
    return pd.DataFrame(rows)


def grade(B, season, week):
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); st = st[(st.season_type == "REG") & (st.week == week)].copy()
    st["nkey"] = st.player_display_name.map(norm_name)
    st = st.drop_duplicates(["nkey", "team"]).set_index(["nkey", "team"])
    out = []
    for r in B.itertuples():
        k = (norm_name(r.player), r.team)
        if k not in st.index:
            out.append(np.nan); continue
        s = st.loc[k]
        if r.market == "anytime_td":
            out.append(float((s.rushing_tds + s.receiving_tds) >= 1)); continue
        a = s[ACT[r.market]]
        out.append(np.nan if a == r.line else float((a > r.line) if r.side == "O" else (a < r.line)))
    B = B.copy(); B["hit"] = out
    B["units"] = np.where(B.hit == 1, np.where(B.price < 0, 100 / B.price.abs(), B.price / 100), np.where(B.hit == 0, -1.0, np.nan))
    return B


def summarize(B, by):
    G = B[B.hit.notna()].groupby(by)
    t = G.agg(lines=("hit", "size"), hit=("hit", "mean"), units=("units", "sum"), model_p=("model", "mean"), book_p=("book", "mean"), conf=("conf", "mean"))
    t["roi"] = t.units / t.lines
    t["brier_model"] = G.apply(lambda d: ((d.model - d.hit) ** 2).mean(), include_groups=False)
    t["brier_book"] = G.apply(lambda d: ((d.book - d.hit) ** 2).mean(), include_groups=False)
    return t.round(3)


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("board"); ap.add_argument("season", type=int); ap.add_argument("week", type=int); ap.add_argument("--out")
    a = ap.parse_args(argv)
    B = grade(parse(a.board), a.season, a.week)
    txt = [f"# Board grade: {a.board}, {a.season} week {a.week}", f"rows parsed {len(B)}, graded {int(B.hit.notna().sum())}, unmatched {int(B.hit.isna().sum())}", "",
           "## by label", summarize(B, "label").to_string(), "", "## by market", summarize(B, "market").to_string(), ""]
    B["bin"] = pd.cut(B.conf, [0, .5, .55, .6, .65, 1]).astype(str)
    txt += ["## by confidence", summarize(B, "bin").to_string(), "", "## graded rows", B[["player", "team", "market", "side", "line", "conf", "model", "book", "price", "label", "hit", "units"]].to_string(index=False)]
    s = "\n".join(txt); print(s)
    if a.out: open(a.out, "w").write(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
