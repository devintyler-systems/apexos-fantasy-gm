# Reference Materials

Everything in this folder is **hypothesis input or historical reference**, not an approved contract, algorithm, or data source specification. Per project doctrine, these documents are inputs to design discussion — they do not carry trait weights, projections, xTD constants, or product recommendations into production until each has gone through: definition, source validation, time-availability assessment, baseline comparison, and acceptance test.

| File | Type | Status |
|---|---|---|
| `nfl_td_projection_framework.md` | TD modeling framework (converted from PDF) | hypothesis-source |
| `touchdownos_planning_and_execution_blueprint.md` | Prior TouchdownOS design blueprint — rigorous prior art on scoring-neutral TD probability modeling | design-reference (high value — supersedes framework doc in rigor) |
| `fantasy_football_architect_planning_ideas.md` | Model-stack and architecture brainstorm notes | design-reference |
| `spamml_2025_draft_order.md` | Confirmed 2025 draft order/pick sequence (source for Draft Round Order Map ground truth) | confirmed-evidence |
| `spamml_2025_draft_guide_overall.csv` | 2025 consensus ADP/points/projection data | calibration-reference-only (not a 2026 source) |
| `spamml_week18_final_results_2025.md` | 2025 season final results | historical-reference |

## 2026 Forward-Looking Projections (`data/raw/2026_projections/`)

| File | Source | Status | Role |
|---|---|---|---|
| `sharpfootballanalysis_team_projected_ppg.csv` | Sharp Football Analysis | **APPROVED input** — see Data Source Register 2.7 | Offensive Scheme Quality layer — team implied scoring environment |
| `vegasinsider_team_projected_wins.csv` | VegasInsider | **APPROVED input** — see Data Source Register 2.8 | Team win-total context; secondary scheme-quality signal alongside PPG |

## 2025 Historical Actuals (`data/raw/2025_actuals/`)

All files below are **backtest/calibration reference only** — they describe what already happened in 2025 and must never be used as a 2026 season input. Their role is validating whether ApexOS's derived xTD model and team-environment weighting would have produced good rankings against known 2025 outcomes.

| File | Content | Role |
|---|---|---|
| `teamrankings_2025_ppg.csv` | Team points scored per game | Backtest: team scoring baseline |
| `teamrankings_2025_opponents_ppg.csv` | Team points allowed per game | Backtest: defensive environment / D_O opponent-side signal |
| `teamrankings_2025_FG_attempts_per_game.csv` | Team FG attempts per game | Backtest: kicker opportunity volume |
| `teamrankings_2025_kicking_ppg.csv` | Team kicker fantasy points per game (actual, at 3/1 scoring) | Backtest: kicker model validation — directly comparable to SPAMML kicker scoring |
| `teamrankings_2025_RZ_scores_per_game.csv` | Red zone TDs scored per game | Backtest: RZ opportunity-to-score conversion |
| `teamrankings_2025_RZ_attempts_per_game.csv` | Red zone trip attempts per game | Backtest: RZ opportunity volume |
| `teamrankings_2025_RZ_scoring_pct.csv` | Red zone TD scoring percentage | Backtest: team-level conversion efficiency — the closest available proxy to "individual efficiency" at team level |
| `playerrankings_2025_total_TDs.csv` | Player total TDs, 2025 season (truncated in repo — full file in thread attachment) | Backtest: ground truth for validating projection model against real outcomes |
