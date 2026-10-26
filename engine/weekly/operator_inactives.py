"""Operator-read official inactives (NFL.com) -> engine inputs.

Usage: python operator_inactives.py FILE.csv --out-manual var/operator_out.csv --out-status var/operator_status.csv
FILE.csv: team,player (one row per official inactive). Output 1 (manual-out format, with nflverse gsis ids so unit effects work): every listed player as an Out row.
Output 2 (overlay format): every OTHER player of those teams that the nflverse injury report still carries with a game designation or a practice listing becomes `Active` (an official list is complete for the
active roster, so a player not on it plays). Players on injured reserve or the reserve list never appear on the inactive list and are untouched. The operator's list always wins over Sleeper and the ESPN feeds."""
import argparse
import datetime as dt

import pandas as pd

from load import norm_name
from paths import NFLV

ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--season", type=int, default=2026); ap.add_argument("--week", type=int, default=7)
ap.add_argument("--out-manual", required=True); ap.add_argument("--out-status", required=True)
a = ap.parse_args()
inact = pd.read_csv(a.file); inact["nkey"] = inact.player.map(norm_name)
r = pd.read_parquet(NFLV + f"roster_{a.season}.parquet"); r = r[r.week == r.week.max()]; r["nkey"] = r.full_name.map(norm_name)
pl = pd.read_parquet(NFLV + "players.parquet"); pl["nkey"] = pl.display_name.map(norm_name)
now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out, missing = [], []
for x in inact.itertuples():
    m = r[(r.nkey == x.nkey) & (r.team == x.team)]
    if not len(m):
        m = pl[(pl.nkey == x.nkey) & (pl.latest_team == x.team)].rename(columns={"display_name": "full_name", "latest_team": "team"}).assign(position=lambda d: d.position)
    if not len(m):
        missing.append((x.team, x.player)); continue
    m = m.iloc[0]
    out.append(dict(player=m.full_name, team=x.team, pos=m.position, source="NFL.com official inactives (operator)", as_of_utc=now, note="Inactive (official list)", gsis_id=m.gsis_id,
                    game="", espn_status="OFFICIAL_INA"))
pd.DataFrame(out).to_csv(a.out_manual, index=False)
teams = set(inact.team); inj = pd.read_parquet(NFLV + f"injuries_{a.season}.parquet"); inj = inj[(inj.week == a.week) & inj.team.isin(teams)]
keep = inj[~inj.full_name.map(norm_name).isin(set(inact.nkey)) & (inj.report_status != "Out")]      # a player the league report lists Out but who is missing from the inactive list is on a reserve list (IR), not active
act = pd.DataFrame(dict(player=keep.full_name, team=keep.team, pos=keep.position, report_status="Active", source="NFL.com official inactives (operator): not on the list", as_of_utc=now, override=True)).drop_duplicates(["player", "team"])
act.to_csv(a.out_status, index=False)
print(f"{len(out)} official inactives written ({len(missing)} unresolved: {missing}); {len(act)} players cleared to Active: {', '.join(sorted(act.player))}")
