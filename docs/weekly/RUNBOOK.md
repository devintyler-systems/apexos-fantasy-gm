> Scripts live in `engine/weekly/`; use `apex-weekly` (README.md). Script names below are unchanged.

# APEX Weekly Engine: runbook (as built, v4-nflverse)

All code lives in `/home/user/week4/py` (copy into `engine/` of apexos-fantasy-gm when you scaffold the repo).
Data: `/home/user/week4/nflverse/*.parquet` (re-download each Tuesday and again Friday/Saturday for injuries and depth charts).

## 0. Refresh data (every run)
Download from `https://github.com/nflverse/nflverse-data/releases/download/<tag>/<file>`:
stats_player_week_{season}, snap_counts_{season}, injuries_{season}, depth_charts_{season}, roster_{season}, pbp (play_by_play_{season}),
games.parquet (schedules + lines + weather columns), players.parquet (id crosswalk), stats_team_week_{season}.
Also available and not yet used: ftn_charting_{season}, advstats_week_{rec,rush,pass,def}_{season} (PFR advanced), contracts, officials.

## 1. One-time fits (re-run each offseason, or monthly in-season)
| Script | Output | What it fits |
|---|---|---|
| `fit_availability.py` | `config/availability_by_status*.csv` | P(plays) by report status x practice x position, 2023-26 |
| `fit_team_priors.py` | `config/team_prior_fit.json` | opponent-adjusted ridge shrinkage, prior-season retention, market blend weight (backtest 2016-25) |
| `fit_player_priors.py` | `config/player_prior_fit.json` | share/efficiency shrinkage (k) and last-season weight (a), role tables |
| `backtest_multi.sh` + `calibrate_bt.py` | `config/calibration_params.json` | level calibration from weeks 4-12 of 2023-25 actuals |
| `weather.py` | `config/weather_effects.json`, `out/w4_weather_forecast.csv` | wind/cold effect on totals; kickoff forecast |

## 2. Weekly run
```
./run_pipeline.sh model     # model-only environment (ridge ratings + weather)
./run_pipeline.sh market    # market-anchored environment (nflverse spread/total as team-points prior)
```
Outputs land in `deliverables_model/` and `deliverables_market/`: rankings, TD markets, fair lines, ladders, team/game props,
`Week<N>_<track>_Projections.xlsx`, DFS Classic pool + lineups.
Environment variables: `APEX_SEASON`, `APEX_THROUGH_WEEK`, `APEX_TARGET_WEEK`, `APEX_INJ_WEEK`, `APEX_ROSTER` (v3|v4), `APEX_ENV` (model|market), `APEX_NS`, `APEX_BACKTEST`.

## 3. Grading (Tuesday)
`APEX_SEASON=2026 ...` -> compare frozen projections to `stats_player_week_2026` (see `compare_bt.py` for the metric set: MAE, bias,
TD Brier/log loss, team RMSE). First graded game already in hand: PIT @ CLE (final 24-27).

## 4. Hard-won rules (do not regress)
1. Join on PFR/gsis ids via `players.parquet`, never names. Team codes: nflverse convention.
2. Time-zone audit every timestamp (the odds workbook was Pacific).
3. One availability draw per player (shared across rushing and receiving). QB1 comes from the current depth chart; fill-ins ranked by attempts.
4. Shares are per game played, shrunk with fitted k toward a prior built from last season's role (not league averages).
5. Calibration is by backtest against actual results, never against the market.
6. DK status can lag the NFL report (DeVonta Smith was OUT on the NFL report with a blank DK status): the model's availability governs.
7. Market-anchored environment beat ratings-only in every backtest; keep both tracks, label which one a number comes from.

## 5. Expected opportunity (ffopportunity)
Source is the ffverse/ffopportunity repo, NOT nflverse-data: `https://github.com/ffverse/ffopportunity/releases/download/latest-data/ep_weekly_{season}.parquet` (also `.rds`, `.csv`; stat types weekly / pbp_pass / pbp_rush; seasons 2006-2026).
Backtest (`fit_opportunity.py`, results in `config/opportunity_fit.json`): small gains only. TE target share with snap/air-yard share -8% MSE, RB catch rate -7%, WR catch rate -4%, QB rush TD -5%; yards-per-reception and yards-per-carry got worse. Not wired into the live model.
Share normalization experiment (`APEX_KT` / `APEX_KC` env knobs, star-preserving): fixes the level bias (receiving ratio 1.06 -> 1.00) but worsens MAE (+5%) and TD log loss. Default left unchanged (multiplier calibration).
