---
name: weekly-run
description: Run the weekly props + DFS projection pipeline for the target NFL week (fetch data, run both tracks, QA, freeze). Use for Wednesday, Friday/Saturday and Sunday reruns.
---
# Weekly run

1. `python -m engine.weekly.cli fetch --season <S>` (refreshes injuries, depth charts, schedules/lines, snaps, stats).
2. Check the QB1 table for every team against the depth chart; a QB1 with no designation must not be treated as out.
3. `python -m engine.weekly.cli run --season <S> --track both [--dfs]` (DFS needs `APEX_DK_SALARIES`). Sequential only.
4. Launch the `data-auditor` and `model-qa` subagents on the outputs. Do not freeze a failing run.
5. `python -m engine.weekly.cli freeze --season <S> --week <W> --track market` and again for `model`; then `verify`.
6. Open a draft PR adding `runs/weekly/<run_id>/` and a short DECISIONS/CHANGELOG note. State what was and was not used (lines, salaries).
Freeze BEFORE the earliest kickoff in the run, or label the run post-hoc in `--notes`.
