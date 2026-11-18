"""Replay-only availability proxy (time-correct): write APEX_MANUAL_OUT rows for players the live roster rules would
have removed but a sparse historical roster cannot (IR / long-term absence / released).
OUT if: no row on the target-week injury report AND 0 offensive snaps in each of the team's last 2 played games
AND >=1 offensive snap earlier this season. Uses only the vintage cache (weeks < target). Players whose newest snap
row is for a different team than their stats team are written as traded (Out for the old team).
python tools/replay/availability_proxy.py SEASON WEEK  -> var/replay_<season>_w<WW>/manual_out.csv
"""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
season, week = int(sys.argv[1]), int(sys.argv[2])
R = ROOT / f"var/replay_{season}_w{week:02d}"; N = R / "nflverse"
sn = pd.read_parquet(N / f"snap_counts_{season}.parquet"); sn = sn[(sn.game_type == "REG") & sn.position.isin(["QB", "RB", "FB", "WR", "TE"])]
sn_abs = sn[sn.position != "QB"]  # backup QBs normally take 0 snaps; QB1 comes from the depth chart
inj = pd.read_parquet(N / f"injuries_{season}.parquet"); inj = inj[(inj.week == week)]
on_report = set(inj.full_name)
rows = []
for team, d in sn_abs.groupby("team"):
    tw = sorted(d.week.unique())[-2:]
    for p, x in d.groupby("player"):
        played = x[x.offense_snaps > 0]
        if not len(played) or p in on_report:
            continue
        if not set(tw) & set(played.week):
            rows.append(dict(player=p, team=team, source="replay_availability_proxy", as_of_utc="vintage cutoff",
                             note=f"0 off snaps in team weeks {tw}; last snap week {int(played.week.max())}"))
last = sn[sn.offense_snaps > 0].sort_values("week").groupby("player").tail(1)
for r in last.itertuples():  # traded: most recent snap team differs from an older team -> out for the older team
    for t in set(sn[(sn.player == r.player) & (sn.team != r.team)].team):
        rows.append(dict(player=r.player, team=t, source="replay_availability_proxy", as_of_utc="vintage cutoff", note=f"now on {r.team}"))
o = pd.DataFrame(rows).drop_duplicates(["player", "team"]); o.to_csv(R / "manual_out.csv", index=False)
print(week, len(o), "proxy outs;", o.player.head(12).tolist())
