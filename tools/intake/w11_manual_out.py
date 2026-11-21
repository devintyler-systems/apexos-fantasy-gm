"""Live manual-out file (DECISIONS #61 workaround: the same mechanism as W8 var/ro/manual_out_w8_sun2.csv).

Out if, in the newest full roster week:
  (a) roster status DEV (practice squad) and no slot on the newest depth chart; or
  (b) the player is projected for a team where he has no roster row in that week (moved or released).
Rule (b) needs a finished run (proj_all.pkl). Every row says which rule fired.

python tools/intake/w11_manual_out.py SEASON PROJ_PKL OUT_CSV
"""
import datetime as dt
import re
import sys

import pandas as pd


def norm_name(s):  # copy of engine/weekly/load.py norm_name
    s = str(s).replace("*", "").replace("+", "").strip()
    s = re.sub(r"[.’']", "", s).lower()
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


season, proj, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
N = "var/nflverse/"
R = pd.read_parquet(N + f"roster_{season}.parquet"); R = R[R.game_type == "REG"]
wk = int(R.week.max()); R = R[R.week == wk].copy(); R["team"] = R.team.replace({"LAR": "LA"})
D = pd.read_parquet(N + f"depth_charts_{season}.parquet"); dc_dt = D.dt.max(); D = D[D.dt == dc_dt]
on_dc = set(D.gsis_id.dropna())
R["nkey"] = R.full_name.map(norm_name)
P = pd.read_pickle(proj); P["nkey"] = P.player.map(norm_name)
now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rows = []
dev = R[(R.status == "DEV") & ~R.gsis_id.isin(on_dc) & R.position.isin(["QB", "RB", "FB", "WR", "TE"])]
for r in dev.itertuples():
    rows.append(dict(player=r.full_name, team=r.team, source=f"nflverse roster w{wk} DEV + depth chart {dc_dt}", as_of_utc=now,
                     note="practice squad, no depth-chart slot (DECISIONS #61)"))
live = set(zip(R.nkey, R.team))
for r in P.itertuples():      # every projected row: an earlier manual-out may already have zeroed p_active (circularity bug, 2026-11-20 audit)
    if (r.nkey, r.team) not in live and r.pos in ("QB", "RB", "WR", "TE"):
        rows.append(dict(player=r.player, team=r.team, source=f"nflverse roster w{wk}", as_of_utc=now,
                         note="no week roster row for this team (moved/released)"))
o = pd.DataFrame(rows).drop_duplicates(["player", "team"])
proj_hit = o.merge(P[P.p_active > 0][["player", "team", "tgt_mean", "rush_att_mean"]], on=["player", "team"], how="inner")
o.to_csv(out, index=False)
print(f"roster week {wk}, depth chart {dc_dt}: {len(o)} manual Outs written ({len(proj_hit)} were carrying projections)")
print(proj_hit.sort_values("rush_att_mean", ascending=False).head(15).round(2).to_string(index=False))
