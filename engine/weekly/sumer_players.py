"""SumerSports player tables (routes run, targets per route run, YPRR, aDOT, EPA; WR, TE, and RB rushing and receiving), 2022-2026, with the site's own situational refinements.

How it works: sumersports.com/players/<position>/ renders a table and loads other seasons and refinements through a Next.js server action (`loadMorePlayerStats`, id below) that takes
[position, season, max rows, order, refinement args, min routes or attempts]. The same call works unauthenticated; no key is involved. The action id changes when the site is redeployed: if a call
returns HTTP 404/500 for every input, read the new id from the page's JavaScript (search "loadMorePlayerStats") and update ACTION.
What is free: season-to-date totals for 2022-2026 and the refinements Standard, red zone, late down (3rd/4th), early down, leading, trailing, vs man (`VS_MAN`), vs zone (`VS_ZONE`).
What is not: the 'By Week' control opens a SumerPass banner (no weekly splits), and alignment splits (slot, inline, wide, backfield route %), motion, drops, contested catches and targeted air yards come back
locked (null). Weekly routes therefore come from differencing two snapshots: run `snapshot` every Tuesday and before each window; `routes_by_week()` subtracts consecutive snapshots.
Usage: python sumer_players.py snapshot SEASON WEEK [--out runs/weekly/_benchmarks] [--refinements]
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

import httpx
import pandas as pd

from paths import NFLV, RUNS

ACTION = "7e0154f61fb110c9f56a71c0ce0b32fd371f06a37c"
# QB is omitted: the same call returns HTTP 500 for every input on the quarterback page (its season-to-date table is in the page HTML), and nflverse already has quarterback stats.
POS = {"RB": ("running-back", [{"rushingYards": "DESC"}]),
       "WR": ("wide-receiver", [{"receivingYards": "DESC"}]), "TE": ("tight-end", [{"receivingYards": "DESC"}])}
REFINE = {"standard": {}, "red_zone": {"redZone": True}, "late_down": {"down": [3, 4]}, "early_down": {"down": [1, 2]}, "leading": {"scoreState": ["LEADING"]}, "trailing": {"scoreState": ["TRAILING"]},
          "vs_man": {"manZone": ["VS_MAN"]}, "vs_zone": {"manZone": ["VS_ZONE"]}}
NOT_FOR = {"RB": {"vs_man", "vs_zone"}}      # not offered on the RB page (it takes its own: box counts and run schemes)
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124", "Accept": "text/x-component", "Content-Type": "text/plain;charset=UTF-8", "Origin": "https://sumersports.com"}


def fetch_table(pos, season, refine="standard", rows=400, min_n=1):
    slug, order = POS[pos]
    url = f"https://sumersports.com/players/{slug}/"
    h = dict(H, **{"Next-Action": ACTION, "Referer": url})
    args = [slug, int(season), rows, order, REFINE[refine], min_n]
    r = httpx.post(url, headers=h, content=json.dumps(args), timeout=90, follow_redirects=True)
    if r.status_code != 200:
        raise RuntimeError(f"sumersports {slug} {season} {refine}: HTTP {r.status_code} (action id may have changed)")
    m = re.search(r"\n1:(\[.*\])\s*$", r.text, re.S)
    items = json.loads(m.group(1)) if m else []
    out = []
    for x in items:
        p = x.get("sumerPlayer") or {}
        row = {k: v for k, v in x.items() if k not in ("lockedFields", "sumerPlayer", "sumerTeam", "__typename", "sumerScoreGame", "sumerScoreSeason") and v is not None}
        row.update(name=f"{p.get('footballName', '')} {p.get('lastName', '')}".strip(), team=(x.get("sumerTeam") or {}).get("teamCode"), pos=pos, refinement=refine)
        out.append(row)
    return pd.DataFrame(out)


def snapshot(season, week, out_dir, refinements=False):
    os.makedirs(out_dir, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc); tag = now.strftime("%Y%m%dT%H%MZ"); n = 0
    for pos in POS:
        for ref in (REFINE if refinements else ["standard"]):
            if ref in NOT_FOR.get(pos, ()):
                continue
            df = fetch_table(pos, season, ref)
            if not len(df):
                continue
            df.insert(0, "as_of_utc", now.isoformat(timespec="seconds")); df["through_week"] = week - 1
            d = out_dir if ref == "standard" else NFLV      # only the standard table is committed; refinements stay in the cache
            df.to_csv(os.path.join(d, f"sumer_{pos.lower()}_{ref}_{season}_w{week:02d}_{tag}.csv"), index=False); n += 1
    print(f"{n} tables written (as of {tag})")


def routes_by_week(a_csv, b_csv):
    """Routes run and targets between two snapshots of the same season (b later): per-player increments."""
    a, b = pd.read_csv(a_csv), pd.read_csv(b_csv)
    k = ["name", "team", "pos"]; cols = [c for c in ("routesRun", "receptions", "receivingYards", "receivingTouchdowns") if c in b]
    m = b[k + cols].merge(a[k + cols], on=k, how="left", suffixes=("", "_prev")).fillna(0)
    for c in cols:
        m[c + "_inc"] = m[c] - m[c + "_prev"]
    return m[k + [c + "_inc" for c in cols]]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["snapshot"]); ap.add_argument("season", type=int); ap.add_argument("week", type=int)
    ap.add_argument("--out", default=os.path.join(RUNS, "_benchmarks")); ap.add_argument("--refinements", action="store_true")
    a = ap.parse_args(); snapshot(a.season, a.week, a.out, a.refinements)
