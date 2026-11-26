"""One-time backfill of historical NFL anytime-TD (and optional prop) prices from The Odds API historical endpoints (ROADMAP P-1b).

ODDS_API_KEY must be an environment secret (never pasted or committed). Output goes to var/odds_hist/ (never committed).

  python tools/backtest/odds_backfill.py --check                      # free: lists events + markets for 2 sample games, costs ~0-2 credits
  python tools/backtest/odds_backfill.py --seasons 2023 2024 2025 --weeks 4-12 [--markets player_anytime_td] [--minutes-before 5] [--max-credits 18000]

Per game: GET /v4/historical/sports/americanfootball_nfl/events?date=<kickoff-1h> to find the event id, then
GET /v4/historical/sports/americanfootball_nfl/events/{id}/odds?date=<kickoff - N min>&markets=...&regions=us&oddsFormat=american.
Cost per odds call = 10 x markets returned x regions (empty responses free). The script stops before --max-credits and is resumable (one json per game).
Kickoffs come from nflverse games.parquet (gameday + gametime, US Eastern).
"""
import argparse, datetime as dt, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://api.the-odds-api.com/v4/historical/sports/americanfootball_nfl"
OUTD = ROOT / "var/odds_hist"
NICK = {"ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens", "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys", "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
        "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars", "KC": "Kansas City Chiefs", "LV": "Las Vegas Raiders", "LAC": "Los Angeles Chargers",
        "LA": "Los Angeles Rams", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings", "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
        "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers", "SF": "San Francisco 49ers", "SEA": "Seattle Seahawks", "TB": "Tampa Bay Buccaneers",
        "TEN": "Tennessee Titans", "WAS": "Washington Commanders"}


def get(path, key, **q):
    q["apiKey"] = key
    try:
        with urllib.request.urlopen(f"{BASE}{path}?{urllib.parse.urlencode(q)}", timeout=60) as r:
            return json.load(r), {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:  # never let the URL (it carries the key) reach a traceback
        raise ApiError(f"HTTP {e.code} on {path}: {e.read()[:300]!r}", e.code) from None


class ApiError(SystemExit):
    def __init__(self, msg, code):
        super().__init__(msg); self.code = code


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def games(seasons, weeks):
    g = pd.read_parquet(ROOT / "var/nflverse/games.parquet")
    g = g[g.season.isin(seasons) & g.week.isin(weeks) & (g.game_type == "REG")].copy()
    g["ko"] = [dt.datetime.fromisoformat(f"{d} {t}").replace(tzinfo=ZoneInfo("America/New_York")) for d, t in zip(g.gameday, g.gametime)]
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seasons", type=int, nargs="+", default=[2023, 2024, 2025]); ap.add_argument("--weeks", default="4-12")
    ap.add_argument("--markets", default="player_anytime_td"); ap.add_argument("--minutes-before", type=int, default=5); ap.add_argument("--max-credits", type=int, default=18000)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--early", action="store_true", help="early snapshot: Wednesday 17:00Z of the game week (before the first injury report), Thursday 17:00Z if Wednesday has no market and kickoff is later (DECISIONS #85; Tuesday lists only ~4 DraftKings players for Sunday games)")
    ap.add_argument("--out", default=str(OUTD), help="output folder (default var/odds_hist); event ids are reused from any json under var/odds_hist")
    a = ap.parse_args()
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        raise SystemExit("ODDS_API_KEY is not set (environment secret only)")
    w0, w1 = map(int, a.weeks.split("-")); G = games(a.seasons, range(w0, w1 + 1))
    if a.check:
        G = G.sort_values("ko").iloc[[0, -1]]
    if a.early:   # Wednesday 17:00Z before the week's first game (ET date); Thursday 17:00Z as the fallback when it is still before kickoff
        first = G.groupby(["season", "week"]).ko.transform("min")
        wed = [dt.datetime.combine((k.date() - dt.timedelta(days=(k.weekday() - 2) % 7 or 7)), dt.time(17), tzinfo=dt.timezone.utc) for k in first]
        G = G.assign(snaps=[[t] + ([t + dt.timedelta(days=1)] if t + dt.timedelta(days=1) < ko else []) for t, ko in zip(wed, G.ko)])
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); used = 0
    known = {}  # game_id -> event id from earlier passes (saves the 1-credit events lookup)
    for jf in OUTD.rglob("*.json"):
        try:
            d = json.loads(jf.read_text()); eid = d.get("event_id") or (d.get("data") or {}).get("id")
            if eid: known[d["game_id"]] = eid
        except Exception:
            pass
    for r in G.itertuples():
        f = out / f"{r.game_id}.json"
        if f.exists() and not a.check:
            continue
        eid = None if a.check else known.get(r.game_id)
        if eid is None:
            ev, h = get("/events", key, date=iso(r.ko - dt.timedelta(hours=1)))
            used += int(h.get("x-requests-last", 0) or 0)
            m = [e for e in ev.get("data", []) if e["home_team"] == NICK.get(r.home_team) and e["away_team"] == NICK.get(r.away_team)]
            if not m:
                print("no event", r.game_id); continue
            eid = m[0]["id"]
        if a.check:
            mk, h = get(f"/events/{eid}/markets", key, date=iso(r.ko - dt.timedelta(minutes=a.minutes_before)), regions="us")
            print(r.game_id, json.dumps(mk)[:1500], "| cost", h.get("x-requests-last"), "remaining", h.get("x-requests-remaining")); continue
        if a.early:
            od, h, used_snap = {}, {}, None
            for t in r.snaps:
                try:
                    o2, h2 = get(f"/events/{eid}/odds", key, date=iso(t), markets=a.markets, regions="us", oddsFormat="american")
                except ApiError as e:
                    if e.code in (404, 422): print(r.game_id, iso(t), "no event at this time"); continue
                    raise
                used += int(h2.get("x-requests-last", 0) or 0); h = h2
                if any(b.get("markets") for b in (o2.get("data") or {}).get("bookmakers", [])):
                    od, used_snap = o2, iso(t); break
            if used_snap is None:
                print(r.game_id, "no anytime market at Tue or Wed", "used", used); continue
            f.write_text(json.dumps(dict(game_id=r.game_id, event_id=eid, markets=a.markets, kickoff_utc=iso(r.ko), requested=used_snap,
                                         snapshot=od.get("timestamp"), data=od.get("data"))))
            print(r.game_id, "snap", used_snap, "used", used, "remaining", h.get("x-requests-remaining"))
            if used >= a.max_credits:
                print("credit cap reached; rerun later to resume"); break
            time.sleep(1.0); continue
        od, h = get(f"/events/{eid}/odds", key, date=iso(r.ko - dt.timedelta(minutes=a.minutes_before)), markets=a.markets, regions="us", oddsFormat="american")
        f.write_text(json.dumps(dict(game_id=r.game_id, event_id=eid, markets=a.markets, kickoff_utc=iso(r.ko), snapshot=od.get("timestamp"), data=od.get("data"))))
        used += int(h.get("x-requests-last", 0) or 0)
        print(r.game_id, "cost", h.get("x-requests-last"), "used", used, "remaining", h.get("x-requests-remaining"))
        if used >= a.max_credits:
            print("credit cap reached; rerun later to resume"); break
        time.sleep(1.0)


if __name__ == "__main__":
    main()
