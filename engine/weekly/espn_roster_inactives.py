"""ESPN event-roster `didNotPlay` flags -> manual_out.csv rows (the format APEX_MANUAL_OUT reads), with a timestamped raw snapshot for lead-time checks.

Usage: python espn_roster_inactives.py YYYYMMDD [YYYYMMDD ...] --out var/manual_out.csv [--merge var/manual_out.csv] [--snap var/roster_dnp_snapshots.csv]

ESPN's core API serves, per event and team, `competitions/{id}/competitors/{team}/roster`: every rostered player with `active`, `starter`, `didNotPlay`. For the finished PIT@NO game the
`didNotPlay` set matched nflverse's official inactives 13 of 13 names. BEFORE the league publishes inactives (about 90 minutes before kickoff) the flag is NOT trustworthy (Monday's DAL@PHI carried 9 PHI
names that omitted DeVonta Smith, Dontayvion Wicks and Jalen Hurts, three known Outs), so rows are written only when --min-minutes-to-kickoff allows it (default: kickoff within 100 minutes or already started)
and every call appends a snapshot (as_of, event, team, player ids) so the lead time of the flag can be checked against nflverse `roster INA` afterwards.
Players resolve to nflverse ids through roster_{season}.espn_id; an unresolved id is written with a note and appears in the engine's unmatched report. Nothing is ever marked Active."""
import argparse
import datetime as dt
import json
import os
import urllib.request

import pandas as pd

from paths import NFLV

SB = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={d}"
RO = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{e}/competitions/{e}/competitors/{t}/roster"
ESPN2NV = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        return json.load(r)


def dnp_ids(roster_json):
    """Pure: ESPN roster JSON -> list of playerIds flagged didNotPlay."""
    return [str(e["playerId"]) for e in roster_json.get("entries", []) if e.get("didNotPlay")]


def rows_for(dates, season, now=None, min_minutes=100, snap=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    r = pd.read_parquet(NFLV + f"roster_{season}.parquet"); r = r[r.week == r.week.max()]
    byid = {str(int(x.espn_id)): x for x in r.dropna(subset=["espn_id"]).itertuples()}
    try:      # players the weekly roster file lacks (linemen, practice squad): resolve through the full players table so their unit effects are not silently dropped
        pl = pd.read_parquet(NFLV + "players.parquet").dropna(subset=["espn_id", "gsis_id"])
        for x in pl.itertuples():
            byid.setdefault(str(int(float(x.espn_id))), type("P", (), dict(full_name=x.display_name, position=x.position, gsis_id=x.gsis_id))())
    except Exception:
        pass
    out, snaps, skipped = [], [], []
    for d in dates:
        for ev in _get(SB.format(d=d)).get("events", []):
            ko = dt.datetime.fromisoformat(ev["date"].replace("Z", "+00:00")); minutes = (ko - now).total_seconds() / 60
            comp = ev["competitions"][0]["competitors"]; teams = {c["homeAway"]: ESPN2NV.get(c["team"]["abbreviation"], c["team"]["abbreviation"]) for c in comp}
            game = f"{teams['away']}@{teams['home']}"
            for c in comp:
                ids = dnp_ids(_get(RO.format(e=ev["id"], t=c["team"]["id"])))
                t = ESPN2NV.get(c["team"]["abbreviation"], c["team"]["abbreviation"])
                snaps += [dict(as_of_utc=now.strftime("%Y-%m-%dT%H:%M:%SZ"), game=game, team=t, minutes_to_kickoff=round(minutes), espn_id=i) for i in ids]
                if minutes > min_minutes:
                    skipped.append(game); continue
                for i in ids:
                    p = byid.get(i)
                    out.append(dict(player=p.full_name if p else f"espn:{i}", team=t, pos=p.position if p else "", source="ESPN roster didNotPlay", as_of_utc=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    note="Inactive (game-day roster flag)", gsis_id=p.gsis_id if p else "", game=game, espn_status="DNP"))
    if snap and snaps:
        pd.DataFrame(snaps).to_csv(snap, mode="a", header=not os.path.exists(snap), index=False)
    return pd.DataFrame(out), sorted(set(skipped))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dates", nargs="+"); ap.add_argument("--season", type=int, default=2026); ap.add_argument("--merge"); ap.add_argument("--out", required=True)
    ap.add_argument("--snap"); ap.add_argument("--min-minutes-to-kickoff", type=int, default=100)
    a = ap.parse_args()
    df, skipped = rows_for(a.dates, a.season, min_minutes=a.min_minutes_to_kickoff, snap=a.snap)
    if a.merge and os.path.exists(a.merge):
        m = pd.read_csv(a.merge); df = pd.concat([m, df[~df.gsis_id.isin(m.gsis_id.dropna())]], ignore_index=True) if len(df) else m
    df.to_csv(a.out, index=False)
    print(f"{len(df)} Out rows -> {a.out}; ESPN roster DNP rows added: {int((df.espn_status == 'DNP').sum()) if 'espn_status' in df else 0}; games not yet inside the window (flag untrusted, not used): {','.join(skipped) if skipped else 'none'}")
