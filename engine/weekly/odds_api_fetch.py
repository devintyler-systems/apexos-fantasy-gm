"""Timestamped player-prop price snapshots from The Odds API, written in the workbook schema price_odds.py already reads.

Usage: ODDS_API_KEY=... python odds_api_fetch.py --out var/odds/w07_<label>.csv [--markets ...] [--books draftkings,fanduel,betmgm,bovada,betrivers,betonlineag]
The key is read ONLY from the ODDS_API_KEY environment variable (set it as an environment secret; never paste it into chat or commit it). Output is gitignored (var/): odds files are never committed.
Schema = the operator workbook: game_id, commence_time, in_play, bookmaker, last_update, home_team, away_team, market, label, description, price, point. Timestamps are written in US Pacific
(naive), exactly like the workbook, because price_odds.py applies TZ_OFFSET_H=7. One snapshot per window (Wednesday open, T-90, T-30) turns every graded week into a closing-line-value test."""
import argparse
import datetime as dt
import json
import os
import urllib.parse
import urllib.request

import pandas as pd

BASE = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl"
DEFAULT_MARKETS = ["player_pass_yds", "player_pass_tds", "player_pass_attempts", "player_pass_completions", "player_rush_yds", "player_rush_attempts", "player_receptions", "player_reception_yds",
                   "player_anytime_td", "player_1st_td"]
PT = dt.timedelta(hours=7)      # PDT; price_odds.py adds 7 hours back


def _pt(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc).replace(tzinfo=None) - PT


def flatten(event):
    """Pure: one Odds API event-odds JSON -> workbook rows."""
    rows = []
    for b in event.get("bookmakers", []):
        for m in b.get("markets", []):
            for o in m.get("outcomes", []):
                rows.append(dict(game_id=event["id"], commence_time=_pt(event["commence_time"]), in_play=False, bookmaker=b.get("title", b.get("key")), last_update=_pt(m.get("last_update") or b["last_update"]),
                                 home_team=event["home_team"], away_team=event["away_team"], market=m["key"], label=o["name"], description=o.get("description", ""), price=o["price"], point=o.get("point")))
    return rows


def _get(path, key, **q):
    q["apiKey"] = key
    with urllib.request.urlopen(f"{BASE}{path}?{urllib.parse.urlencode(q)}", timeout=40) as r:
        return json.load(r), dict(r.headers)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--markets", default=",".join(DEFAULT_MARKETS))
    ap.add_argument("--books", default="draftkings,fanduel,betmgm,bovada,betrivers,betonlineag"); ap.add_argument("--week-days", type=int, default=7, help="only events starting within this many days")
    a = ap.parse_args()
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        raise SystemExit("ODDS_API_KEY is not set: add it as an environment secret (not in chat) and start a new session")
    events, _ = _get("/events", key)
    now = dt.datetime.now(dt.timezone.utc); horizon = now + dt.timedelta(days=a.week_days)
    rows, used = [], None
    for ev in events:
        ko = dt.datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))
        if ko < now or ko > horizon:
            continue
        j, hdr = _get(f"/events/{ev['id']}/odds", key, regions="us,us2", markets=a.markets, oddsFormat="american", bookmakers=a.books)
        rows += flatten(j); used = hdr.get("x-requests-remaining", used)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); df.to_csv(a.out, index=False)
    print(f"{len(df)} rows from {df.game_id.nunique() if len(df) else 0} events -> {a.out}; requests remaining: {used}")
