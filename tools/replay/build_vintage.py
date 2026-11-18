"""Build a time-restricted nflverse cache for a hindsight-diagnostic replay of one target week.

python tools/replay/build_vintage.py SEASON WEEK CUTOFF_UTC  -> var/replay_<season>_w<WW>/nflverse
Rules (current season files only; prior seasons are symlinked unchanged):
  games: scores/results blanked for week >= WEEK (lines kept: nflverse lines are CLOSING lines -> market track = close-anchored)
  stats_player_week, stats_team_week, snap_counts, play_by_play, advstats_*, ftn_charting: week < WEEK
  injuries: week <= WEEK (target-week report is pregame; Sunday teams' final report postdates a Thursday cutoff)
  roster: week <= WEEK (nflverse keeps only a sparse roster for past weeks -> roster IR/cut rules inactive; limitation)
  depth_charts: dt <= CUTOFF_UTC (true daily snapshots)
Writes VINTAGE.json describing every restriction.
"""
import json, os, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
season, week, cutoff = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
src = ROOT / "var/nflverse"
dst = ROOT / f"var/replay_{season}_w{week:02d}/nflverse"
dst.mkdir(parents=True, exist_ok=True)
log = {"season": season, "target_week": week, "cutoff_utc": cutoff, "label": "HINDSIGHT DIAGNOSTIC REPLAY (not an original forecast)", "files": {}}
for f in sorted(src.glob("*.parquet")):
    out = dst / f.name
    if out.exists() or out.is_symlink():
        out.unlink()
    if not f.name.endswith(f"_{season}.parquet") and f.name != "games.parquet":
        os.symlink(f, out); continue
    d = pd.read_parquet(f); n0 = len(d)
    wk = "week" if "week" in d.columns else None
    if f.name == "games.parquet":
        m = (d.season == season) & (d.week >= week)
        for c in ("away_score", "home_score", "result", "total", "overtime"):
            if c in d.columns:
                d.loc[m, c] = None
        rule = f"scores blanked season={season} week>={week}"
    elif f.name.startswith("depth_charts"):
        d = d[d.dt <= cutoff]; rule = f"dt<={cutoff} (latest kept {d.dt.max()})"
    elif f.name.startswith(("injuries", "roster")):
        d = d[d[wk] <= week]; rule = f"week<={week}"
    elif wk:
        d = d[d[wk] < week]; rule = f"week<{week}"
    else:
        rule = "unchanged (no week column)"
    d.to_parquet(out, index=False)
    log["files"][f.name] = {"rule": rule, "rows_in": n0, "rows_out": len(d)}
(dst.parent / "VINTAGE.json").write_text(json.dumps(log, indent=1))
print(json.dumps({k: v["rule"] for k, v in log["files"].items()}, indent=0))
