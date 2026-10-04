---
name: game-preview
description: Write a single-game pre-game summary (winner, score, player projections, anytime and first TD) from a frozen run.
---
# Game preview

Read only from `runs/weekly/<run_id>/` (projections.csv, w4_game_environment.csv, w4_td_markets.csv). Never from a fresh unfrozen run.
Give: predicted winner and score (mean and median), team totals, QB/RB/WR/TE lines with P25-P75, top anytime TD with reasoning tied to targets, carries and red-zone share, and first-TD ranking.
State the track, run_id, as_of_utc and any key availability assumption. Confidence is a reliability index, not a hit probability.
