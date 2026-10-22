# Engine gap analysis and roadmap, 2026 Week 7

Scope: where the APEX weekly engine falls short, measured on the 27 backtest slates (weeks 4-12, 2023-25, 7,994 player-games) and the live Week 7 slate. Every number below traces to a DECISIONS entry (#35-#40) or to a script in `engine/weekly/`. Nothing here is a price edge: we have no book prices.

## 1. The answer to "why did we pull those lines"

The engine did not hit a limit; I applied a blanket publishing gate for a defect I had not yet isolated. The defect is now isolated and partly fixed.

- **Found and fixed (DECISIONS #38):** the role priors were indexed by rank among all skill players, including players who are Out, so a promoted backup was priced from the wrong slot. Ranking among players who can play improves receiving yards, receptions, rush yards, rush attempts and TD log loss in all three held-out seasons (rec_yds MAE -0.053, rush_yds MAE -0.139, TD log loss -0.0006). It is now the default.
- **Not closed:** the shrinkage of a promoted backup toward a prior built on 3 games. Roschon Johnson is 4.3 carries / 18 yards in our run, 33.7 yards in the Rotowire feed, 13 carries in the one other game Monangai missed. The RB-out publishing gate stays until the next candidate (promotion-aware shrinkage) or the benchmark archive shows our RB-out rush lines agree with the consensus.
- **What the backtest says about "Out" handling in general:** it is already about right on average. Top projected back's actual/projected carry share is 1.13 on teams with an RB Out and 1.11 on teams without; top-2 WR receptions 1.04 vs 1.06. The sim already renormalizes shares among active players every draw (the `APEX_VAC` candidate moved nothing, #35).

## 2. What the data says is knowable (and what is not)

| Question | Result |
|---|---|
| Can pregame information predict team pass or rush attempts? | Barely. Correlation 0.19 / 0.23. A regression on trailing volume, opponent volume allowed, spread, total, script terms, implied points, wind, cold, dome, rest, home: out-of-sample RMSE 7.61 vs sd 7.80 (pass), 7.15 vs 7.40 (rush). 2-3% of variance. |
| Ceiling if volume were known | Rush attempts -17%, rush yards -13%, receptions -5%, receiving yards -2% MAE. Rushing is the volume-driven market; receiving is a share-and-efficiency market. |
| Does recency (last 3 games, last game, snap share) beat the model? | Not for receiving (+1.1% worse). For rush attempts, yes: -2.5% with last-3 and snaps, -3.0% adding spread and total. The one place a retrain pays. |
| Do sharper shares (concentrate on the top of the depth chart) help? | No. Rejected on the same harness (#38): rec_yds MAE +0.4 to +1.1, rush_yds +0.4 to +0.6. Current shaping is a local optimum. |
| Unprojected players with real usage | 1.9% of targets, 4.2% of carries; 59% of them had no earlier game that season (call-ups, new signings, rookies). |
| League drift | None. 2026 weeks 1-6 are in the 2022-25 range for pass attempts, carries and points. |
| Backup QBs | Fill-ins over-projected about 9% relative to starters (passing yards 218 vs 212, passing TDs 1.34 vs 1.18); 98 fill-in starts had no projection row in the backtest. |

Consequence: the edge does not come from a sharper pace forecast. It comes from (a) calibrated distributions and joint structure, (b) role and availability calls made faster and better than the market, (c) TD concentration, (d) rush-attempt shares, (e) never running on silently missing inputs.

## 3. Where we fall short (ranked by expected value)

1. **No price or closing-line data.** We cannot compute edge, CLV, or learn from the one signal that beats every model: the market. We grade against a naive per-game average and the DK line size of team scores only. Fix: price feed (see section 5, ask 1) plus a line archive frozen with every run.
2. **No independent benchmark.** Fixed going forward: `bench_fetch.py` archives the Rotowire/Sleeper projections and injury status every window; `bench_grade.py` (to write before Tuesday) scores model vs benchmark vs naive vs actual. First read of Week 7: correlation with our market track 0.94 receiving yards, 0.93 receptions, 0.89 rushing, 0.60 passing yards. The disagreements are the research agenda: SF WRs while Evans and Samuel are Questionable (Watkins 38.9 vs 7.7 yards, Cooks 36.6 vs 14.6), IND Mallory (1.4 vs 27.0), TD concentration (Taylor 0.99 vs 0.51 expected TDs, Smith-Njigba 0.92 vs 0.55).
3. **Silent fallbacks.** Weather has been off in the model-only track since scaffolding (`weather.py` was not in the pipeline, hard-coded to week 4, partial stadium table, WAS in London; `WEATHER_ADJ` fell back to `{}`). Fixed with `weather_forecast.py` (NWS), but the class of bug remains: the QA gate must fail a run when an expected input is absent or a fallback fired (weather file, lines file, outs file, injury report for a team). Build `run_completeness.py` and make freeze refuse.
4. **Promotion and role-change shrinkage** (section 1). Next candidate; test on the 103 RB-out team-weeks plus WR/TE equivalents.
5. **Touchdown model.** The W6 bins: 0.10-0.20 predicted 15.0% vs 9.1% actual (n=55), 0.40-0.50 predicted 45.0% vs 16.7% (n=12), 0.60+ 65.8% vs 77.8% (n=9): over-confident in the middle, conservative at the top, and the consensus puts stars higher than we do. Candidate: TD v3 from goal-line and inside-10 usage shares plus ffopportunity expected TDs, fit by position, graded by bin. Do not touch the anytime floor before the Week 9 review.
6. **Rush-attempt share model.** Retrain with recency, snap share and spread/total (the -3% finding).
7. **Distribution and joint calibration.** P25-P75 coverage W6: rec yards 0.55, rush yards 0.44, completions 0.50; parlays hit 9 of 48 vs 14.7 expected. Build a joint-calibration backtest (same-game pair frequencies vs simulated) before publishing parlays as anything but fair-odds estimates.
8. **Backup QB environment** (generic rushing profile, 92% efficiency on the starter's YPA, no model-only discount): factor near 0.91 on yards and TDs, backtested on all metrics.
9. **Information timing.** Official inactives land about 90 minutes before kickoff and the ESPN feed shows 5 names per team. Sleeper's status feed carries a `news_updated` timestamp and is archived each window; use it to flag disagreements with nflverse in the injury audit.

## 4. Data we have, do not use, or could add

| Source | Status | What it adds |
|---|---|---|
| nflverse `nextgen_stats` (passing, receiving, rushing; 200 OK) | not fetched | Separation, cushion, intended air yards share, time to throw, aggressiveness, 8+ defenders in box, rush efficiency: efficiency priors and role, especially for shrinkage of small samples. |
| nflverse `ftn_charting` | fetched every run, not used | Play action, screens, RPO, motion, blitz, rushers, drops: team and QB tendencies, matchup (coverage and rush) features. |
| nflverse `pfr_advstats` | used only for the report tables | Pressure, drops, YAC, broken tackles as efficiency regressors. |
| nflverse `pbp_participation` | 2016-2025 only (2026 returns 404) | Personnel and routes: needs a 2026 substitute; ask 3. |
| ffverse `ffopportunity` expected points | fitted once (small gains), not wired | Expected TDs from usage for the TD v3 candidate. |
| nflverse `draft_picks`, `combine`, `contracts`, `trades`, `weekly_rosters` | not fetched | Rookie and new-team role priors (the 59% of unprojected usage), transaction timing. |
| nflverse `officials` | not fetched | Crew penalty rate: small effect on plays. |
| National Weather Service hourly forecast | now wired | Kickoff wind, temperature, precipitation. |
| Sleeper projections and injury status (Rotowire feed) | now archived | Independent consensus benchmark and a faster news clock. |
| ESPN fantasy API (`kona_player_info`, 200 OK) and FantasyPros consensus pages (200 OK, scraping terms apply) | reachable, not yet read | Second and third benchmarks. |
| The Odds API (401 without key), DraftKings/FanDuel prop prices | not available | Prices, CLV, closing-line learning. See ask 1. |
| Open-Meteo | blocked from this container | Replaced by NWS. |

## 5. What I need from you

1. **A price source.** Any one of: a The Odds API key (player props, with historical snapshots on the paid plan), a recurring export or screenshot of DraftKings/FanDuel player prop prices with timestamps, or access to a data vendor you already pay for. This is the single biggest unlock: it turns every ranked lean into an edge or a no-bet.
2. **Fantrax exports** for Week 7 (My-Roster, All-Available-Players): I could not score your Week 6 lineup without the roster file.
3. **A 2026 personnel/route source**, if you have PFF, FTN, Next Gen or similar exports, or know where Devin pulls route participation. nflverse participation stops at 2025.
4. **DraftKings salary file** (`DKSalaries_classic.csv`) when you want lineups; not committed.

## 6. Next work, in order

| # | Item | Test | When |
|---|---|---|---|
| 1 | `bench_grade.py`, line archive in each freeze, `run_completeness.py` | unit tests; Tuesday W7 benchmark comparison | before Tuesday |
| 2 | Promotion-aware shrinkage for promoted backups | weeks 4-12 backtest incl. RB-out subset; lifts the RB-out gate if it passes | W8 |
| 3 | Rush-attempt share retrain (recency, snaps, spread, total) | weeks 4-12 backtest | W8 |
| 4 | Fetch and test `nextgen_stats` and `ftn_charting` features on receiving yards MAE and TD log loss | stack test first (cheap), then sim | W8-W9 |
| 5 | TD v3 from goal-line usage and expected TDs | TD log loss by bin, all three seasons | W9, with the floor review |
| 6 | Backup-QB factor | all metrics | W9 |
| 7 | Joint-calibration backtest for parlays | same-game pair frequencies | W10 |
| 8 | Extend the backtest harness to include 2026 weeks as a fourth held-out season, so the engine learns from each postmortem under the same promotion rule | `eval_candidate.py` with `SEASONS` including 2026 | W8 |
