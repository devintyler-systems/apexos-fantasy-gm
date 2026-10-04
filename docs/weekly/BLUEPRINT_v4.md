> **Code location:** this document predates the repo landing. Scripts are now in `engine/weekly/`, fitted parameters in `config/weekly/`, run with the `apex-weekly` CLI (see README.md). Paths below refer to the original scratch layout.

# APEX Weekly Props + DFS Engine: Blueprint v4 (as built, 2026-10-04)

Supersedes v3. v3 was written before the nflverse rebuild, the fitted priors, the availability model, the market-anchored track,
weather, and DFS Classic. This version describes what exists, what was proven, what failed, and what to do next.

---------------------------------------------------------------------------------------------------
## 1. Status at a glance

| Layer | State | Evidence |
|---|---|---|
| Data layer | nflverse-first (weekly logs, snaps, injuries, depth charts, pbp, schedules with lines/weather, id crosswalk) | Reproduces your sportsref totals exactly for Weeks 1-3 (attempts, yards, TDs, sacks, points) |
| Availability | Fitted from 2023-26 injury history x snaps | 2025 holdout Brier 0.0770 vs 0.0798 hand-set |
| Team environment | Two tracks: model-only (opponent-adjusted ridge + weather) and market-anchored (spread/total) | Test 2023-25 RMSE: market 8.97, ridge 9.33, old method 9.40; best blend weight on market = 1.0 |
| Roles and efficiency | Fitted shrinkage with last-season priors | Held-out MSE: shares -14% to -22%, efficiency -1% to -12% |
| Calibration | Set from actual results (2023-25, weeks 4-12), never from the market | QB passing within 1-2%; listed WR/TE receiving 4-5% low; RB carries ~9% low (accepted, see 6) |
| Outputs | Rankings, distributions, TD markets, ladders, team/game props, XLSX, previews | See file list in section 9 |
| DFS | Classic built (cash, stacks, 20-lineup GPP set); Showdown not built | 12-game main slate tested |
| Grading loop | NOT automated (one game graded by hand: PIT @ CLE) | Next build |
| Weather | Historical effect fitted; kickoff forecast pulled | Only NE @ BUF had wind this week |

End-to-end week-4 backtest (2023-25, vs v3): receiving yards MAE 20.40 -> 19.81, receptions MAE 1.60 -> 1.56, TD log loss 0.4506 -> 0.4427
(model-only) / 0.4373 (market-anchored), team points RMSE 9.28 -> 8.96 (market-anchored). Gains are real but modest. Do not oversell them.

---------------------------------------------------------------------------------------------------
## 2. Lessons that must be inherited (numbered; each one cost us something)

Data and parsing
1. Join on ids (gsis/PFR via `players.parquet`), never names. Team codes follow nflverse (LA, GB, KC, LV, NE, NO, SF, TB, WAS).
2. Time-zone audit every timestamp. The odds workbook was Pacific; I called a 1-hour-old snapshot stale because I assumed UTC.
3. Sportsref ".xls" files are HTML; ids sit in `data-append-csv`. Now optional: nflverse reproduces them.
4. The odds workbook orders event names alphabetically, not home/away.
5. nflverse `games.parquet` carries betting lines. Model-only runs must never read current-season line fields; market-anchored runs read them on purpose and say so.
6. The ffopportunity data is in `ffverse/ffopportunity` (release tag `latest-data`, `ep_weekly_{season}.parquet`), not in nflverse-data. Season columns are strings.
7. Older-season depth charts use a different schema (no `dt`). Backtests must fall back to attempts.
8. nflverse updates live: `injuries_2026` already held the Friday report, depth charts were stamped that morning, and the Thursday box score was present by Friday.
9. DraftKings status lags the NFL report (DeVonta Smith was OUT on the NFL report, blank on DK). The NFL report governs.

Roster and availability
10. QB1 comes from the CURRENT depth chart, not Weeks 1-3 attempts. Attempts picked the wrong QB for ATL, MIN and SEA. Fill-ins rank by attempts (CHI: Keenum over the depth-chart QB2).
11. Historical "no designation + Full practice" QBs play only 85.5% because backup QBs are listed in practice reports. A QB1 with no designation gets 98%.
12. Doubtful players play 0.6% of the time; Questionable with Full / Limited / DNP practice play 71% / 67% / 52%; no designation with DNP plays 80%.
13. Shares are per game played (Bowers, G=1, was understated 3x). Games played come from snap counts.
14. One availability draw per player, shared across rushing and receiving. Independent draws understated every questionable RB.

Model mechanics (all found by QA or with/without scenarios)
15. Drive-limited scoring (binomial TDs over 8 chances, FG binomial over 4) gives margin sd about 14. Poisson gave 17.
16. Tie yards to TD counts (+0.11 per passing TD, +0.08 per rushing TD) or points and QB yards are uncorrelated.
17. Receiving variance is set by the Dirichlet concentration (alpha_target 100, alpha_carry 60), calibrated to 2025 weekly logs (median/mean and CV by volume band).
18. The starting QB takes about 93% of team dropbacks (early exits, garbage time): starter pass yards, completions, attempts x0.93, TDs x0.95. Team volumes are already calibrated (attempts 32.8 vs 33.0 actual).
19. Fitted shares sum to 1.16x the target budget and 1.32x the carry budget. Plain normalization compresses stars 14% to 25%.
    A star-preserving normalization fixes the level (receiving ratio 1.06 -> 1.00) but worsens MAE about 5% and TD log loss. Level is not accuracy: we keep the position multipliers.
20. Ratio-level fits do not always survive end-to-end. Yards per carry fit k=500; game-level rush MAE got worse, so k=45 stays. The end-to-end backtest governs.
21. Expected-opportunity data (ffopportunity) plus snap and air-yard share gave only small gains (TE target share -8% MSE, RB catch rate -7%, WR catch rate -4%, QB rush TD -5%; yards per reception and per carry got worse). It is not the fix for the receiving/carry gaps.

Process
22. Never run two pipeline tracks concurrently against one output folder (they overwrite each other). Run sequentially or give each its own output dir.
23. Do not `pkill -f` a script name from a shell whose own command line contains it. Run long jobs in the background and monitor.
24. Calibrate against actual results. Calibrating to the market and calling the remainder "edge" destroys the signal; the market is used only as an environment prior, in a separate track.
25. Ambitious multipliers tuned on 2023-25 are in-sample. 2026 is the first true out-of-sample test. Grade it.

---------------------------------------------------------------------------------------------------
## 3. Architecture: map today's scripts into `apexos-fantasy-gm`

Do not create a third repo. Copy `/home/user/week4/py` into the repo as follows (names are suggestions).

| Today | Repo module | Role |
|---|---|---|
| `prep_nv.py` | `engine/ingestion/nflverse.py` | team/player tables, red zone from pbp, DvP, sacks |
| `load.py`, `names.py` | `engine/normalization/ids.py, teams.py` | team maps, name normalizer, id crosswalk |
| `params.py` | `engine/projections/params.py` | environment, roster build, injuries, depth chart QBs, market/weather modes |
| `fit_availability.py` | `engine/priors/injury_play_rates.py` | empirical play rates |
| `fit_team_priors.py` | `engine/priors/team_strength.py` | ridge shrinkage, retention, market blend weight |
| `fit_player_priors.py`, `fit_opportunity.py` | `engine/priors/player_rates.py` | shares, efficiency, TD rates; opportunity add-ons |
| `sim.py` | `engine/simulation/game_sim.py` | correlated Monte Carlo (20,000 sims per game) |
| `run_all.py`, `build_outputs.py`, `projections_report.py`, `build_projection_tables.py` | `engine/reports/` | outputs, workbook |
| `edges.py`, `edges_list.py`, `top30_lines.py`, `convert_lines.py` | `engine/markets/` | line conversion, de-vig, pricing |
| `dfs_collect.py`, `dfs_classic.py` | `engine/optimizer/dk_classic.py` | DK point distributions and lineups |
| `weather.py` | `engine/ingestion/weather.py` | forecast and historical effect |
| `backtest_run.py`, `backtest_multi.sh`, `calibrate_bt.py`, `compare_bt.py`, `eval_variants.py` | `engine/grading/` | backtest and calibration |
| `qa.py` | `tests/` | invariants and QA |
| `config/*.json,csv` | `config/` | every fitted constant (versioned) |
| `run_pipeline.sh` | `engine/run_week.sh` | one-command weekly run |

Config files (all fitted or measured, never hand-edited without a DECISIONS.md entry): `availability_by_status*.csv`, `team_prior_fit.json`,
`player_prior_fit.json`, `calibration_params.json`, `calibration.json`, `weather_effects.json`, `opportunity_fit.json`.

Runtime switches (environment variables): `APEX_SEASON`, `APEX_THROUGH_WEEK`, `APEX_TARGET_WEEK`, `APEX_INJ_WEEK`, `APEX_ROSTER` (v3|v4),
`APEX_ENV` (model|market), `APEX_NS`, `APEX_BACKTEST`, `APEX_DELIV`, plus experiment knobs `APEX_KT`, `APEX_KC`, `APEX_NOMULT`, `APEX_YPC_K`, `APEX_CATCH_K`.

Storage: Parquet or DuckDB for processed tables; CSV/XLSX only as exports. Every run writes a manifest (below).

Run manifest (add this; not automated yet): season, week, version, track (model|market), as_of_utc, SHA-256 of every input file, source time zones,
git commit, seed, n_sims, config hash, QA results, unmatched names, injury report week and timestamp, depth chart timestamp.

---------------------------------------------------------------------------------------------------
## 4. Data sources (all verified reachable from the cloud environment with Network access = Full)

Primary (free): `https://github.com/nflverse/nflverse-data/releases/download/<tag>/<file>`
- `stats_player/stats_player_week_{y}.parquet`, `stats_team/stats_team_week_{y}.parquet`
- `snap_counts/snap_counts_{y}.parquet`, `injuries/injuries_{y}.parquet`, `depth_charts/depth_charts_{y}.parquet`, `rosters/roster_{y}.parquet`
- `pbp/play_by_play_{y}.parquet`, `schedules/games.parquet` (scores, spread_line, total_line, roof, surface, temp, wind, location)
- `players/players.parquet` (gsis, pfr, pff, espn ids), `ftn_charting/ftn_charting_{y}.parquet`, `pfr_advstats/advstats_week_{rec,rush,pass,def}_{y}.parquet`
- NOT present at these paths: `ff_opportunity`, `nextgen_stats` 2025 files, `participation`, `weekly_rosters`.

Expected opportunity: `https://github.com/ffverse/ffopportunity/releases/download/latest-data/ep_weekly_{y}.parquet` (stat types weekly, pbp_pass, pbp_rush).

Weather: Open-Meteo (batch request, one call for all stadiums; retries with backoff) at kickoff hour (ET to UTC +4 in October).

Authoritative documentation to consult when a path breaks: nflreadr / nflreadpy docs (data dictionaries and `load_*` source), nflfastR docs, the nflverse and ffverse GitHub issue trackers.
When GitHub HTML pages return 403, use WebFetch on the rdrr.io / nflreadr source pages or the pkgdown site.

Inputs you supply: DK salary CSVs (Classic and Showdown), an odds workbook for props, your sportsref exports (optional cross-check), the NFL.com PDF (optional now).
Inputs still missing: official game-day inactives (nflverse updates after games; build a scrape or use the NFL game center the morning of), closing lines for CLV, ownership.

Paid or keyed (decide by budget): The Odds API (props with timestamps and book coverage), PFF (routes, TPRR, pass-block grades). Not required to proceed.

---------------------------------------------------------------------------------------------------
## 5. Weekly cadence (automate; times ET)

| When | Job | Output |
|---|---|---|
| Tue 09:00 | Re-download nflverse. Freeze-and-grade: pull actuals for last week, grade the frozen projections (MAE, bias, TD log loss, calibration, team RMSE). | grading report, leaderboard |
| Tue 14:00 | Re-fit availability and priors; run candidate-change backtests (week 4-12 harness); promote only on a win | backtest report, DECISIONS.md |
| Wed | Midweek run: model-only and market-anchored tracks | rankings, TD lists, XLSX |
| Thu | Grade TNF as soon as the box score posts; rerun the slate | refreshed slate |
| Fri / Sat | Pull Friday injuries + depth charts + lines + weather; rerun both tracks; DFS pool and lineups | priced edges, DFS |
| Sun, 90 min before each window | Official inactives; rerun affected games; late-swap sheet | swaps |
| Sun night / Mon | MNF run; freeze and archive the week | frozen week |

Every run is a new version; nothing is overwritten. Sequential tracks only.

---------------------------------------------------------------------------------------------------
## 6. Model specification (what the sim actually does)

Environment (two tracks, always labeled)
- model-only: opponent-adjusted ridge ratings (lo=8, ld=16, retention 0.40 offense / 0.25 defense of last season's deviation, HFA 1.0) + fitted weather adjustment.
- market-anchored: home pts = (total + spread)/2, away pts = (total - spread)/2 from nflverse schedule lines (spread_line > 0 means home favored). No separate HFA or weather (priced in).
- Neutral sites from `location == Neutral` (IND @ WAS in London).

Game simulation (per game, 20,000 correlated sims, seed fixed)
1. Scoring draw: shared game factor (sd 0.07) and team factors (sd 0.12); TDs ~ Binomial(8, p), FG ~ Binomial(4, p), defensive/ST TDs and safeties added.
2. Script: pass rate shifts 0.0022 per point of margin (cap +/-0.08); plays ~ Normal(mean, 4.0); sacks and attempts follow.
3. Team passing efficiency latent z (loads 0.8 on the scoring team factor); TD split by fitted pass-TD share; yards tied to TD counts.
4. Targets: Dirichlet-multinomial over fitted shares (alpha 100) with per-sim availability; receptions Binomial; per-catch yards Gamma (shape 1.8). Carries: Dirichlet (alpha 60) with the same availability draws; per-carry mixture with explosive runs.
5. TDs allocated by red-zone weighted shares (inside-20 targets, inside-10 carries from pbp, shrunk 8 observations to overall share).
6. QB: starter share 0.93 of dropbacks; backup modeled when the starter is doubtful (efficiency x0.92, INT x1.15).

Roster inputs (fitted)
- Target share: k=5 (WR a=0.75, TE a=0.5), RB k=3 a=0.75; carry share RB k=3 a=0.25, QB k=5 a=1.0; last-season weight halves if the team changed.
- Efficiency (pooled-ratio shrink): catch rate k=160/400/400 (WR/TE/RB), yards per reception 30/120/120, yards per carry 45 (override), TD rates by position.
- Calibration set: other-bucket shares 0.025 (targets) and 0.02 (carries); position multipliers car_RB 1.22, tgt_TE 1.17, tgt_RB 1.05, tgt_WR 1.05.
- Known residuals (documented, accepted): listed WR/TE receiving about 4-5% low, RB carries about 9% low.

Defense and DST: real team sacks from nflverse; takeaways from opponent INT and fumbles-lost rates; PA tiers per DK.

---------------------------------------------------------------------------------------------------
## 7. DFS (DraftKings)

Classic scoring: pass 0.04/yd, 4 TD, -1 INT, +3 at 300 yards; rush 0.1/yd, 6 TD, +3 at 100; receiving 1/rec, 0.1/yd, 6 TD, +3 at 100; fumble lost -1; 2-pt +2.
DST: sack 1, INT 2, fumble recovery 2, TD 6, safety 2, blocked kick 2; points allowed 0:+10, 1-6:+7, 7-13:+4, 14-20:+1, 21-27:0, 28-34:-1, 35+:-4. Roster QB, 2 RB, 3 WR, TE, FLEX, DST; $50,000 cap.
Showdown Captain: 1.5x points and salary, 6 players, kicker scoring XP 1 / FG 3, 4, 5 by distance. (Not built.)

Method: per-player DK point arrays from the sims (zeros when inactive), same-game scenarios aligned, independent across games. Cash = max mean. Stacks = best lineup per game (QB + pass catcher + bring-back).
GPP = 20 lineups built sequentially with stack required, bring-back alternating, uniqueness constraint, and a 40% exposure cap; no DST against your own QB. Report salary, mean, P90, P95.
Rules to keep: exclude DK OUT/IR and anyone our availability puts under 50%; flag DK/NFL status conflicts; use the NFL report.
Missing: ownership (add when supplied), Showdown, contest-type recommendation beyond the simple cash-vs-GPP heuristic.

---------------------------------------------------------------------------------------------------
## 8. Gates (replace "bypass project gates")

Hard gates (block the run)
1. Inventory: expected files, 32 teams, expected game count, 100% id coverage, injury report week = target week, depth chart timestamp recorded.
2. Time-zone audit recorded for every timestamped source.
3. Leakage: no input newer than as_of; model-only runs read no current-season line fields; backtests use only weeks before the target week.
4. Reconciliation: league points scored vs allowed within 5; pass/rush attempts, yards, TDs tie to team totals; nflverse vs any supplied second source within tolerance.
5. Invariants: one availability draw per player; shares sum to the budget; allocated TDs equal drawn TDs; Out players zero volume; QB1 equals depth chart; no player on two teams.
6. Calibration bands: margin sd 13 to 15; total sd 13 to 15; QB-WR1 yards correlation 0.4 to 0.7; points-QB yards correlation 0.15 to 0.35; QB passing p99 under 500; team passing/rushing volume within 3% of actuals in the rolling backtest.
7. Market sanity (QA only): model-only vs market game win-probability correlation at least 0.7; any game more than 15 points apart needs a written reason.

Soft gates (warn): unmatched names above 3%; stale lines (older than 6 hours, after the time-zone audit); thin samples; MODEL-GAP edges above 15 points; DK vs NFL status conflicts.

---------------------------------------------------------------------------------------------------
## 9. Output set (per track, per week)

`Week{N}_Model_Projections.xlsx` (Method, QB, RB, WR_TE, TD Top5 by game, TD Top20), rankings by position, `w4_game_environment.csv` (win prob, fair spread, totals, team totals),
`w4_td_markets.csv`, `w4_player_props_fair_lines.csv`, `w4_player_alt_ladders.csv`, team and game props, injury adjustment log, weather forecast,
`dfs_classic_pool / cash_and_stacks / gpp_lineups / gpp_exposure`, `props_lines.csv` plus `edges_*` when lines are supplied, backtest results, run manifest.
Confidence (1-100): availability x (60% tightness of the middle-50% range + 40% sample/role stability); TD confidence = availability x (50% role stability + 50% red-zone evidence), capped at 85.

---------------------------------------------------------------------------------------------------
## 10. Backlog in order of expected payoff

1. Freeze-and-grade automation (Tuesday). Also the first honest out-of-sample test of every calibration above. Highest priority.
2. Official inactives ingest and Sunday rerun path (moves numbers more than any modeling change).
3. QB-swap-aware environment for the model-only track (team scoring and pass rate adjusted by starter quality; fit from history). The market track already reflects swaps.
4. Showdown Captain optimizer (IND @ WAS file in hand).
5. Run manifest and input hashing automated; tests from section 8 wired to CI.
6. Narrow opportunity add-ons: TE target share with snap and air-yard share, RB/WR catch rate from expected receptions, QB rush TD. Only if the end-to-end backtest confirms.
7. EPA-based team ratings and pace/pass-rate-over-expected; weather multipliers on passing and kicking beyond the totals effect.
8. Closing-line value tracking and bankroll sizing (after 6 to 8 graded weeks).
9. Ownership-aware GPP construction.
10. Defender props (tackles, sacks) after snap and tackle history is ingested.

Promotion rule: any model change must beat the current model on the multi-week backtest (accuracy and calibration, not level alone) and be logged in `DECISIONS.md`.

Expectations: with 3 to 4 weeks of current-season data the distributions are wide and the market is efficient on average. The realistic edge is calibrated probabilities, a few thin-market spots
(receptions, rush yards, alt lines, TD lists), better availability handling than the public, and a process that grades itself. Do not size bets off the model until 6 to 8 weeks of graded history show positive CLV.

---------------------------------------------------------------------------------------------------
## 11. Agent design

Main agent: "APEX Weekly Engine". Subagents: data-auditor (gates 1-5), model-qa (gates 6-7 and calibration page), red-team (tries to break Top plays; checks injuries, stale lines, correlated picks, DK/NFL conflicts), grader (Tuesday).
Skills to create: weekly-ingest, injury-update, sim-run, props-pricing, dfs-classic, dfs-showdown, grade-and-backtest, report-writer, game-preview.
Tools: GitHub MCP, Python (pandas, numpy, scipy, pyarrow, duckdb, pulp, lxml, pdfplumber, openpyxl, requests), WebFetch/WebSearch for documentation lookups, scheduled routines, file delivery, optional Slack/email.
Cloud setting: Network access = Full (verified for nflverse, ffverse, Open-Meteo). Keep Anthropic API keys and any odds API keys in environment secrets, never in files.

---------------------------------------------------------------------------------------------------
## 12. The instructions (system prompt for the new agent)

```
# APEX Weekly Engine: Operating Instructions v4

## 1. Identity and mandate
You are the APEX weekly NFL props and DFS engine for Devin Tyler. You produce calibrated projections, rankings, prop pricing, DFS lineups
and game previews, and you grade yourself every week. Priority: correctness, calibration, reproducibility, speed. Assume Devin's fluency;
never re-explain the repo. Open every response with the answer, then tables.

## 2. Operating principles
1. Run the pipeline; do not describe it. Return files and tables.
2. Everything is versioned and frozen. Never overwrite a run. Record as_of_utc, input hashes, seed, config hash, git commit,
   source time zones, injury-report and depth-chart timestamps.
3. Two environment tracks, always labeled: MODEL-ONLY (ratings + weather) and MARKET-ANCHORED (spread/total). Lines never enter the model-only track.
4. Never fabricate a stat, line, salary, injury status or id. Mark Unknown and widen the band.
5. Join on ids, never names. Report unmatched names every run. Team codes are nflverse codes.
6. The NFL/nflverse injury report governs availability. Flag any DK status conflict; never silently trust DK status.
7. Starting QB comes from the current depth chart; fill-ins rank by attempts. Re-check QB1 on every run.
8. Calibrate against actual results, never against the market. Report both raw and any adjusted number.
9. Challenge once when a request hurts accuracy or bankroll, with one alternative; then comply.
10. No em dashes, no hedging, no menus. Close with the single next best move.

## 3. Weekly runbook (execute in order; log each step; stop on a failed hard gate)
1. Refresh nflverse (stats, snaps, injuries, depth charts, pbp, schedules, players) and weather. Record timestamps.
2. Inventory and gates 1-5. Time-zone audit any supplied file.
3. Refit availability and priors only on the scheduled refit day; otherwise load config.
4. Build the slate from nflverse schedules: neutral sites, played games flagged, lines, injuries, depth-chart QBs.
5. Simulate both tracks sequentially (20,000 correlated sims per game, fixed seed).
6. Gates 6-7. Rerun on failure; never ship a failing run.
7. Outputs per track (section 9 of the blueprint). If lines are supplied: convert to schema, de-vig (two-way exact; one-sided flat 10% labeled
   Estimated), price exact lines only, one best rung per player-market-side, show raw and bias-centered edge, flag MODEL-GAP above 15 points,
   exclude played games and stale lines.
8. If a salary file is supplied: build DK lineups (cash, stacks, 20-lineup GPP with 40% exposure cap) using DK scoring including bonuses.
9. Red-team review of Top plays and lineups before delivery.
10. Freeze and archive the run. Update CHANGELOG, LESSONS, DECISIONS.
11. Tuesday: grade the frozen run against actuals; report MAE, bias, TD log loss, calibration, team RMSE, hit rate by confidence tier, CLV where available.

## 4. Projection rules
- Environment, then plays, pass/rush split, shares, efficiency, TDs. Volume before efficiency.
- Shrinkage constants are fitted, not hand-set; every constant lives in config with its backtest evidence.
- Distributions, not points: median, P25, P75, P90 for every yardage and count stat.
- TDs come from red-zone and goal-line usage and the team TD environment, never from yardage alone.
- Preserve correlations (QB with pass catchers, script with carries, team total with TDs).
- Injuries: with/without scenarios for every Out/Doubtful/Questionable skill player; one availability draw per player.
- Confidence 1-100 is a reliability index, not a hit probability. State this when presenting it.

## 5. Betting logic
- Edge = model probability minus no-vig probability. Minimum edge 3 pts main, 5 pts alt and anytime TD, 7 pts first/last TD.
- Same-game parlays priced from the simulated joint distribution, never multiplied legs.
- Quarter-Kelly capped at 2% per play and 6% per game, shown only if a bankroll is supplied.
- Record the price taken for closing line value.

## 6. Anti-patterns
- Treating 3-4 games as a stable talent signal. Calling a play a lock. Stating over 85% on any single player prop.
- Comparing lines across books at different half-points. Shipping a number you cannot trace to an input file and a version.
- Tuning level to the market. Promoting a model change on level alone (improves bias, hurts accuracy) instead of the multi-week backtest.
- Running tracks concurrently into one folder. Inferring a starter from attempts when a depth chart exists.

## 7. Output standards
State version, track, as_of_utc, injury-report and depth-chart timestamps, and what was and was not used (lines, salaries). Every table row traces to a run version.
```

---------------------------------------------------------------------------------------------------
## 13. Build order from here

Now: grade PIT @ CLE and Sunday's games when they post; build the freeze-and-grade job; add the official-inactives step; rerun the market-anchored track Sunday morning.
Next week: QB-swap-aware environment; Showdown; run manifest and hashing; invariant tests in CI.
Weeks 7-8: narrow opportunity add-ons if they win end to end; EPA ratings; CLV tracking live.
Week 9+: ownership-aware GPP; decide what to automate fully versus what stays human-reviewed.

Definition of done for production: the whole Tuesday-to-Sunday cadence runs from one command or one schedule, every run is reproducible from its manifest,
gates block bad runs, and grading is automatic.
