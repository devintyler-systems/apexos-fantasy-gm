# Data dictionary: intake_2026_w09_w11

**manifest.csv**: one row per received file.
- `doc_id`: D001…, in receipt order.
- `sha256`: hash of the file.
- `batch`: receipt batch label.
- `received_utc`: time received.
- `bytes`, `pages`: size and page count.
- `text_pages` / `ocr_pages` / `empty_pages`: page counts by extraction method.
- `extraction_method`, `extraction_status`: ok / partial / failed / duplicate.
- `duplicate_of`: doc_id of the earlier identical file, if any.
- `pdf_*`: PDF metadata.
- `publisher`, `evidence_family`: F01–F18. Several documents can share one family, and those documents are not independent.
- `subject`, `info_cutoff`: the source's stated as-of time.
- `weeks`, `season`, `layout`: parse notes.
- `limitations`: known gaps.

Metadata only: no document content and no prices.

**schedule_w09_w11.csv**
- `game_key` = `<season>_<week>_<away>_<home>`.
- `kickoff_utc`: ESPN scoreboard time.
- `status`: ESPN status at retrieval.
- `archived_apex_prediction`: `none_in_repo` for W9 and W10.

**retro/coverage_matrix_games.csv**: one row per W9/W10 game.
- `act_*`: final results.
- `line_*`: nflverse closing lines. `spread_line` > 0 means the home team is favoured.
- `proj_*`: market-anchored replay.
- `model_proj_*`: model-only replay.
- `home_win_prob`: replay probability.
- Margin = home − away.

**retro/replay_games.csv**, **retro/replay_teams.csv**, **retro/replay_players.csv**
- Long format with columns `week` and `track` (model / market).
- Players: `*_mean`, `*_p25`, `*_p75` are engine projections. Actuals come from nflverse `stats_player_week` (`passing_yards`, …).
- `played` = took ≥1 offensive snap, or recorded a carry or target.
- `fp_act` = actual points under the engine's formula (`sim.py fp`).
- `ev_pts` = engine expected points including availability.
- `naive_*` = the player's per-game average in the same season, in games played before the target week.

**retro/replay_summary.json**
- Metrics: bias = mean(proj − actual), MAE, RMSE.
- Brier and log loss on the home win (ties excluded).
- `iqr_cov` = share of actuals inside [P25, P75].
- Keys: `games|<week or pooled>|<track>`, `teams|pooled|<track>`, `players|pooled|<track>`.
