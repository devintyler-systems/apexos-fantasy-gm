"""Which playing teams have NO rows in the target-week nflverse injury report. The engine treats a missing row as healthy, so a team with zero rows is an
information gap, not a clean bill of health (2026 W5: ARI BUF DEN LA LAC LV PHI SEA SF). Writes injury_report_coverage.csv to OUT."""
import pandas as pd
from paths import OUT, NFLV
from params import SCHED, SEASON, TARGET_WEEK
i = pd.read_parquet(NFLV + f"injuries_{SEASON}.parquet"); i = i[(i.week == TARGET_WEEK) & (i.game_type == "REG")]
rows = []
for g in SCHED.itertuples():
    for t in (g.away, g.home):
        x = i[i.team == t]
        rows.append(dict(game=f"{g.away}@{g.home}", team=t, injury_rows=len(x), out_rows=int((x.report_status == "Out").sum()), has_report=len(x) > 0))
d = pd.DataFrame(rows); d.to_csv(OUT + "injury_report_coverage.csv", index=False)
print("teams with NO injury rows:", d[~d.has_report].team.tolist())
