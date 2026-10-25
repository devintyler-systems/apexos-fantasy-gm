"""Official NFL inactives -> manual_out.csv rows (the format APEX_MANUAL_OUT reads).

Usage: python nfl_inactives.py WEEK --merge var/manual_out.csv --out var/manual_out.csv [--season 2026]

nflverse `roster_{season}` carries the game-day designation `INA` (inactive) once the league publishes inactives (about 90 minutes before kickoff, with nflverse lagging by minutes to an hour).
Every INA player of a team playing that week is written as an Out row (source 'nflverse roster INA'). Rows are merged with an existing ESPN Out file: ESPN's feed lists 5 names per team at most, so the
union is strictly more complete; a player already present is kept once. A team with no INA rows has not been published yet and is reported as pending: the caller must say so. Nothing is ever marked Active.
"""
import argparse
import datetime as dt

import pandas as pd

from paths import NFLV


def build(season, week, merge=None):
    r = pd.read_parquet(NFLV + f"roster_{season}.parquet"); r = r[(r.week == week) & (r.status == "INA")]
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == season) & (g.week == week)]
    team_game = {}
    for x in g.itertuples():
        team_game[x.home_team] = f"{x.away_team}@{x.home_team}"; team_game[x.away_team] = f"{x.away_team}@{x.home_team}"
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = r[r.team.isin(team_game)]
    ina = pd.DataFrame(dict(player=r.full_name, team=r.team, pos=r.position, source="nflverse roster INA (official inactives)", as_of_utc=now, note="Inactive (game-day designation)", gsis_id=r.gsis_id,
                            game=r.team.map(team_game), espn_status="INA"))
    pending = sorted(t for t in team_game if t not in set(ina.team))
    if merge:
        m = pd.read_csv(merge)
        ina = pd.concat([m, ina[~ina.gsis_id.isin(m.gsis_id.dropna())]], ignore_index=True)
    return ina, pending


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("week", type=int); ap.add_argument("--season", type=int, default=2026); ap.add_argument("--merge"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    df, pending = build(a.season, a.week, a.merge)
    df.to_csv(a.out, index=False)
    print(f"{len(df)} Out rows -> {a.out}; INA rows from {int((df.espn_status == 'INA').sum())}; teams with no inactives published yet: {','.join(pending) if pending else 'none'}")
