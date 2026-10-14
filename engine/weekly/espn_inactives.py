"""Official-inactives ingest (W4 postmortem P0 #1): ESPN game-summary injuries -> manual_out.csv the engine already understands (APEX_MANUAL_OUT).
Usage: python espn_inactives.py YYYYMMDD [YYYYMMDD ...] [--games BUF@LA,CHI@GB] [--dk DKSalaries.csv] [--out var/manual_out.csv]
Rules (hard-won in 2026 W5): ESPN's `injuries` feed lists at most 5 names per team, so a name that is absent proves nothing; only explicit Out rows are written and no player is ever marked
Active. Team codes are nflverse codes (LAR->LA, WSH->WAS). Names resolve to the nflverse roster by normalized name then (team, last name); an unresolved name is written with a note so the
engine's unmatched report shows it. With --dk, any DK status OUT/IR/Q/D that the NFL report disagrees with is written to dk_nfl_conflicts.csv (the NFL report governs; DK is flagged, never trusted)."""
import argparse, datetime as dt, json, os, sys, urllib.request
import pandas as pd
from load import norm_name

ESPN2NV = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
SB = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={d}"
SUM = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={e}"
OUT_STATUS = {"out", "injured reserve", "ir", "suspended"}


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def nv_team(a):
    return ESPN2NV.get(a, a)


def parse_summary(d, as_of):
    """Pure function: one ESPN summary JSON -> list of dict rows (only explicit Out-type statuses)."""
    comp = d.get("header", {}).get("competitions", [{}])[0].get("competitors", [])
    home = next((nv_team(c["team"]["abbreviation"]) for c in comp if c.get("homeAway") == "home"), "")
    away = next((nv_team(c["team"]["abbreviation"]) for c in comp if c.get("homeAway") == "away"), "")
    rows = []
    for t in d.get("injuries", []):
        team = nv_team(t["team"]["abbreviation"])
        for i in t.get("injuries", []):
            if str(i.get("status", "")).strip().lower() not in OUT_STATUS:
                continue
            pos = (i["athlete"].get("position") or {}).get("abbreviation", "") if isinstance(i["athlete"].get("position"), dict) else ""
            rows.append(dict(player=i["athlete"]["displayName"], team=team, pos=pos, game=f"{away}@{home}", espn_status=i["status"],
                             source="ESPN game summary injuries (status Out; feed capped at 5 names per team)", as_of_utc=as_of,
                             note=f"{away} @ {home}: {(i.get('details') or {}).get('type', '')}".strip()))
    return rows


def resolve(rows, roster):
    """Map ESPN names to nflverse roster names (same team). Unresolved names are kept and noted."""
    r = roster.copy(); r["nk"] = r.full_name.map(norm_name)
    out = []
    for x in rows:
        c = r[(r.team == x["team"]) & (r.nk == norm_name(x["player"]))]
        if len(c) == 0:
            ln = norm_name(x["player"]).split(" ")[-1]
            c = r[(r.team == x["team"]) & (r.last_name.map(norm_name) == ln)]
            if len(c) != 1:
                c = c.iloc[0:0]
        if len(c) >= 1:
            x = dict(x, player=c.iloc[0].full_name, pos=c.iloc[0].position or x["pos"], gsis_id=c.iloc[0].gsis_id)
        else:
            x = dict(x, gsis_id="", note=x["note"] + " [UNRESOLVED name: not on the nflverse roster for this team]")
        out.append(x)
    return out


def dk_conflicts(dk_path, injuries, roster):
    """DK status OUT/IR/Q/D vs the NFL report status for the same player; returns conflict rows."""
    dk = pd.read_csv(dk_path)
    if "Status" not in dk.columns:
        return []
    dk = dk[dk["Roster Position"].isin(["FLEX", "UTIL"]) | ~dk["Roster Position"].isin(["CPT"])]
    dk = dk.drop_duplicates(["Name", "TeamAbbrev"]); dk["nk"] = dk.Name.map(norm_name); dk["team"] = dk.TeamAbbrev.map(nv_team)
    inj = injuries.copy(); inj["nk"] = inj.full_name.map(norm_name)
    res = []
    for r in dk[dk.Status.fillna("").astype(str).str.len() > 0].itertuples():
        m = inj[(inj.nk == r.nk) & (inj.team == r.team)]
        nfl = m.report_status.iloc[0] if len(m) and isinstance(m.report_status.iloc[0], str) else "(no row)"
        agree = (r.Status in ("OUT", "O", "IR") and nfl in ("Out",)) or (r.Status == "Q" and nfl == "Questionable") or (r.Status == "D" and nfl == "Doubtful")
        if not agree:
            res.append(dict(player=r.Name, team=r.team, dk_status=r.Status, nfl_report_status=nfl, action="NFL report governs; flag in the deliverable"))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("dates", nargs="+"); ap.add_argument("--games", default=""); ap.add_argument("--dk", default="")
    ap.add_argument("--out", default="manual_out.csv"); ap.add_argument("--season", type=int, default=int(os.environ.get("APEX_SEASON", 2026))); a = ap.parse_args(argv)
    from paths import NFLV
    as_of = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"); want = {g for g in a.games.split(",") if g}
    rows = []
    for d in a.dates:
        for ev in _get(SB.format(d=d)).get("events", []):
            s = _get(SUM.format(e=ev["id"])); rows += [r for r in parse_summary(s, as_of) if not want or r["game"] in want]
    roster = pd.read_parquet(NFLV + f"roster_{a.season}.parquet"); roster = roster[roster.week == roster.week.max()]
    rows = resolve(rows, roster)
    pd.DataFrame(rows, columns=["player", "team", "pos", "source", "as_of_utc", "note", "gsis_id", "game", "espn_status"]).to_csv(a.out, index=False)
    print(f"{len(rows)} Out rows -> {a.out}; unresolved: {sum('UNRESOLVED' in r['note'] for r in rows)}")
    if a.dk:
        inj = pd.read_parquet(NFLV + f"injuries_{a.season}.parquet"); inj = inj[(inj.game_type == "REG") & (inj.week == inj.week.max())]
        c = dk_conflicts(a.dk, inj, roster); p = os.path.join(os.path.dirname(os.path.abspath(a.out)), "dk_nfl_conflicts.csv")
        pd.DataFrame(c, columns=["player", "team", "dk_status", "nfl_report_status", "action"]).to_csv(p, index=False); print(f"{len(c)} DK vs NFL conflicts -> {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
