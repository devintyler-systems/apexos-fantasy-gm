# Reference scripts (Week 6)

One-off pick-grading scripts used for `POSTMORTEM_2026_W06.md`. They hard-code the Week 6 scratch paths (`S=`), the sim directories (`sx7`, `sx8`, `sx10`) and the ESPN box score file for Monday night, so they are a method reference, not a tool. Turn them into `engine/weekly/pick_grade.py` (week and run directories as arguments, ESPN box-score fallback for games nflverse has not posted) in the first Week 7 session.

- `w06_grade_picks.py`: grades every screened single line (PLAY / LEAN / all), the top-30 prop lists, anytime TD calibration and the QB passing-TD ladder against box scores.
- `w06_grade_parlays.py`: rebuilds the published 2/3/4-leg parlay tickets from the sims and grades each leg.
