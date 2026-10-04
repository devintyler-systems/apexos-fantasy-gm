---
name: grade-and-backtest
description: Tuesday freeze-and-grade of last week's frozen runs and candidate-change backtests (weeks 4-12, seasons 2023-25). Use before promoting any model or calibration change.
---
# Grade and backtest

1. `fetch` (current season) so actuals are in.
2. For each frozen run of the finished week: `python -m engine.weekly.cli grade runs/weekly/<run_id>`; commit `grade.json` and `grade_players.csv`.
3. Report MAE, bias, P25-P75 coverage, TD log loss and Brier, team RMSE and winner hit rate, by track. Compare to the backtest baseline in `contracts/weekly/grading.v0.1.yaml`.
4. Candidate change: `engine/weekly/bt_variant.sh <tag>` then `compare_bt.py`/`eval_variants.py`. Promote only if the promotion_rule holds. Record evidence in `docs/weekly/DECISIONS.md`.
5. Refits (`apex-weekly fit availability|team|player|calibration`) happen on the scheduled refit day only; the diff of `config/weekly/*` goes in the PR.
