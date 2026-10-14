"""Live DraftKings player-prop LINES from ESPN's public core API, in the Odds-API workbook layout that price_odds.py already reads.
Usage: python espn_props.py --week 6 [--games SEA@DEN,HOU@JAX] [--out var/espn_dk_lines.xlsx]
What the feed has (probed 2026-10-14, provider 100 = DraftKings): per athlete and market a `current` and an `open` line (the number) and `lastUpdated`; 14 yardage / count / kicking markets per game.
What it does NOT have: prices (no over/under juice) and no touchdown prices (anytime / first TD come back empty). So:
  * every row is written as Over/Under at an ASSUMED -110 under the bookmaker name 'DraftKings (ESPN line only, price assumed -110)'; downstream de-vig is therefore exactly 50/50 and any
    'edge' is model probability minus 50%, NOT an edge against a real price. Treat the output as a line comparison (model P(over) at the posted number) and a source of line movement,
    never as +EV evidence (postmortem P0 #2).
  * open vs current is written to espn_dk_line_moves.csv so the number can be tracked for closing-line value (compare the line we published with the closing line).
Timestamps follow the workbook convention (US Pacific, price_odds shifts +7h to UTC)."""
import argparse, json, os, sys, urllib.request, gzip
import pandas as pd

BOOK = "DraftKings (ESPN line only, price assumed -110)"
PRICE = -110
SB = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={w}&seasontype=2&dates={y}"
PB = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{e}/competitions/{e}/odds/100/propBets?limit=300&page={p}"
MARKET = {"Total Passing Yards": "player_pass_yds", "Total Receiving Yards": "player_reception_yds", "Total Receptions": "player_receptions", "Total Rushing Yards": "player_rush_yds",
          "Total Carries": "player_rush_attempts", "Total Pass Completions": "player_pass_completions", "Total Passing Attempts": "player_pass_attempts"}
SKIPPED_NOTE = "not priced by price_odds.py: Longest*, Passing Touchdowns, Interceptions, Rush+Rec / Pass+Rush yards, Kicking, 2+/3+ TD, TD scorer markets (no prices)"


def _get(url):
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "apex-weekly"})
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
    return json.loads(gzip.decompress(b) if b[:2] == b"\x1f\x8b" else b)


def market_of(type_name):
    base = type_name.split(" (incl.")[0].strip()
    return MARKET.get(base)


def athlete_id(item):
    ref = (item.get("athlete") or {}).get("$ref", "")
    return ref.split("/athletes/")[1].split("?")[0] if "/athletes/" in ref else None


def parse_items(items, roster_by_espn):
    """Pure function: ESPN propBet items -> rows (player, team, market, line_current, line_open, last_updated_utc). Items without a numeric line, or without a priced market, are dropped."""
    rows = []
    for it in items:
        m = market_of(it["type"]["name"]); a = athlete_id(it)
        cur = ((it.get("current") or {}).get("target") or {}).get("value")
        if m is None or a is None or cur is None or a not in roster_by_espn:
            continue
        p = roster_by_espn[a]; op = ((it.get("open") or {}).get("target") or {}).get("value")
        rows.append(dict(player=p["full_name"], team=p["team"], market=m, line_current=float(cur), line_open=float(op) if op is not None else float(cur), last_updated_utc=it.get("lastUpdated")))
    return pd.DataFrame(rows, columns=["player", "team", "market", "line_current", "line_open", "last_updated_utc"])


def to_odds_api(df, home_full, away_full, commence_utc, fetched_utc):
    """Rows in the Odds-API workbook layout (timestamps US Pacific = UTC - 7h). last_update is the FETCH time: ESPN's lastUpdated is when the line last changed, so an unmoved line would look stale."""
    pt = lambda s: (pd.Timestamp(s).tz_localize(None) - pd.Timedelta(hours=7))
    out = []
    for r in df.itertuples():
        base = dict(game_id="espn", commence_time=pt(commence_utc), in_play=False, bookmaker=BOOK, last_update=pt(fetched_utc), home_team=home_full, away_team=away_full,
                    market=r.market, description=r.player, point=r.line_current)
        out.append(dict(base, label="Over", price=PRICE)); out.append(dict(base, label="Under", price=PRICE))
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--week", type=int, required=True); ap.add_argument("--games", default=""); ap.add_argument("--season", type=int, default=int(os.environ.get("APEX_SEASON", 2026)))
    ap.add_argument("--out", default="espn_dk_lines.xlsx"); a = ap.parse_args(argv)
    from paths import NFLV
    from load import FULL2ABBR
    nv = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX"}
    R = pd.read_parquet(NFLV + f"roster_{a.season}.parquet"); R = R[R.week == R.week.max()].dropna(subset=["espn_id"])
    by = {str(x.espn_id).replace(".0", ""): dict(full_name=x.full_name, team=x.team) for x in R.itertuples()}
    want = {g for g in a.games.split(",") if g}
    import datetime as dt
    fetched = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    sb = _get(SB.format(w=a.week, y=a.season)); frames, moves = [], []
    for ev in sb["events"]:
        comp = ev["competitions"][0]["competitors"]; home = next(c for c in comp if c["homeAway"] == "home")["team"]; away = next(c for c in comp if c["homeAway"] == "away")["team"]
        game = f"{nv.get(away['abbreviation'], away['abbreviation'])}@{nv.get(home['abbreviation'], home['abbreviation'])}"
        if want and game not in want:
            continue
        items, p = [], 1
        while True:
            try:
                d = _get(PB.format(e=ev["id"], p=p))
            except Exception:
                break
            items += d.get("items", [])
            if p >= d.get("pageCount", 1):
                break
            p += 1
        df = parse_items(items, by)
        if df.empty:
            print(game, "no priced prop lines yet"); continue
        frames.append(to_odds_api(df, home["displayName"], away["displayName"], ev["date"], fetched)); moves.append(df.assign(game=game))
        print(game, len(df), "lines,", df.player.nunique(), "players")
    if not frames:
        print("nothing to write"); return 1
    pd.concat(frames, ignore_index=True).to_excel(a.out, index=False)
    mv = pd.concat(moves, ignore_index=True); mv["moved"] = mv.line_current - mv.line_open
    p = os.path.join(os.path.dirname(os.path.abspath(a.out)), "espn_dk_line_moves.csv"); mv.to_csv(p, index=False)
    print(f"-> {a.out} (assumed -110, line only) and {p}; {SKIPPED_NOTE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
