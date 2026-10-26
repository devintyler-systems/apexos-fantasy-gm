# Week 7 Sunday postmortem (12 Sunday games, plus Thursday for reference)

Scope: every Sunday game (PIT@NO through KC@SEA). DAL@PHI (Monday) is not graded here. Sources: the last frozen run before each kickoff (12:11Z for PIT@NO, 15:50Z for the 1:00 PM games, 18:39Z for the 4 PM games, 22:55Z for KC@SEA), the per-window screened-line dumps, nflverse box scores, and the 2023-25 backtest.
No book prices exist, so every number is a hit rate against the posted line at an assumed -110, never ROI. Nothing here changes a frozen run; nothing in this document is a model change.

## 1. Scorecard

| Measure | Result |
|---|---|
| Winners, market-anchored track (Sunday) | 8 of 12 (the SF@ATL, TB@CAR, NYG@HOU and MIA@NYJ picks lost) |
| Winners, model-only track (Sunday) | 7 of 12 |
| Winners, DK line (13 final games incl. Thursday) | 9 of 13; market-anchored 9 of 13; model-only 8 of 13 |
| Margin MAE (13 games): market-anchored / line / model-only | 9.85 / 9.88 / 11.05 |
| Total MAE: market-anchored / line / model-only | 10.21 / 10.04 / 10.38 |
| Team-points RMSE: market-anchored / line / model-only | 9.04 / 9.01 / 9.61 |
| **Must-plays (9)** | **2 of 9** (Young, Love hit; Kamara, Rodgers, Brown, Murray, K. Williams, Nix, Walker missed) |
| Published PLAY lines, 1 PM + 4 PM + SNF | 10 of 17 (rush and pass 3 of 8, receiving 7 of 9) |
| Every screened line, chosen side (402 lines, p_active 0.9+) | 55% hit against 61% predicted raw and 56% shrunk |
| Highest-chance parlays | all lost: every top ticket carried Brown or Murray (both missed) or Kittle (no TD) |
| Anytime TD, top 30 | 40% scored against 46% predicted; overall 47 scorers against 43.7 predicted |

Read this as a bad week for the single-line picks and an ordinary week for the projections. Player means were close to unbiased (section 2); the picks are where it went wrong.

## 2. Projection accuracy was fine; the selection was not

Players with p_active above 0.5, market-anchored track, frozen pre-kickoff:

| Stat | Projected mean | Actual mean | Bias | MAE |
|---|---|---|---|---|
| QB pass yards | 220 | 227 | -6 | 52 |
| QB completions | 20.2 | 20.5 | -0.3 | 4.0 |
| QB pass TDs | 1.36 | 1.38 | -0.01 | 0.74 |
| RB rush yards | 32.8 | 34.2 | -1.4 | 21.9 |
| RB carries | 7.5 | 7.9 | -0.4 | 3.5 |
| WR receiving yards | 28.9 | 26.6 | +2.3 | 20.0 |
| TE receiving yards | 19.9 | 18.4 | +1.5 | 13.7 |

Against the naive per-game average: receiving yards MAE 21.4 vs 22.9 (better), receptions 1.41 vs 1.51, passing yards 62.0 vs 67.5, rush yards 30.1 vs 29.4 (worse), completions correlation 0.23 vs 0.41 (worse). Team volume: pass attempts 33.5 projected vs 31.6 actual (the 2026 under-projection reversed this week), rush attempts 26.5 vs 27.5.

## 3. Where we are still missing, ranked by what it cost, with a fix for each

### F1. The raw single-line probability is over-confident exactly where it disagrees most with the line (cost: the whole card)
- 402 screened lines: raw model 61%, shrunk 56%, actual 55%. Brier: raw 0.2515 (worse than a 50% coin at 0.2500), shrunk 0.2455. The 50/50 shrink is right (best weight 0.5), but it is flat.
- By distance of the model mean from the line (|mean - line| / line): up to 10% (n=148) raw 57%, hit 56%; 10-25% (n=130) raw 61%, hit 59%; **over 25% (n=124) raw 66%, hit 49%**.
- By raw probability: 0.65-0.70 hit 59%, 0.70-0.75 hit 66%, 0.75-0.80 hit 64%, 0.80-0.85 hit 63%, 0.85 and above hit 60%. Above about 0.70 the model carries no more information; calibrated ceiling is about 62%.
- The must-plays were the largest gaps on the card. That is why they lost together.
- Fix: replace the flat shrink with a gap-aware one (weight 1.0 up to 10% gap, 0.75 to 25%, 0.25 beyond), cap any published probability at 65%, and flag any line with a gap over 25% as MODEL-GAP (the AGENT_INSTRUCTIONS rule that I could not apply without prices: a posted line is a usable 50% anchor). Fit the three weights on graded history, not on this one week. Need: an archive of every window's screened lines graded the next week (kept outside the repo; only the aggregated calibration table is committed).

### F2. Rush yards: distributions too narrow, hit rate 46%
- 2023-25 backtest, 2,052 running-back rows: P25-P75 interval holds 44% (target 50%); P10-P90 holds 75% (target 80%). This week it held 33%.
- Rescaling the stored quantiles about the mean, the best scale is 1.2 for running backs (every season: 1.1, 1.2, 1.2) and 1.1 for quarterback rush yards; receiving and passing are fine at 1.0.
- Of the 54 rush-yard lines screened this week, the chosen side hit 46%; the best shrink weight for that market is 0 (no information beyond the line). Rush attempts hit 63%.
- Fix: widen RB rush-yard dispersion by 1.2 and QB rush yards by 1.1 in the sim; add interval coverage and pinball loss to the promotion metrics (the current rule is blind to dispersion). Interim rule starting now: rush-yard lines are LEAN at most; rush attempts keep their current treatment.

### F3. Mobile quarterbacks make rush-yard unders fragile
- Bo Nix rush yards UNDER 10.5 (6 of 6 in his log) rushed for 73; Kyler Murray UNDER 25.5 rushed for 39 on 5 carries. Young and Love hit.
- Fix: a heavy-tailed quarterback rush model (one scramble breaks the under) and a cap: no must-play on a quarterback rush under.

### F4. Parlay concentration
- Every high-chance 2- and 3-leg ticket shared Brown O11.5 or Murray U25.5. Arithmetic was correct; the portfolio was one bet.
- Fix: a construction rule (a leg appears in at most 2 of the published tickets, and the report prints "lose together if X misses"). Build and unit-test it before Week 8.

### F5. Availability: healthy scratches, and a returning player with no projection
- 14% of players at p_active 1.00 did not play (276 players). Six with projected usage logged no snap: Gainwell, Dillon, Estime, Mullings, Bam Knight, Kaleb Johnson. AJ Dillon was a published downgrade line.
- Josh Jacobs (GB) had 7 targets and 11 carries and had no projection row (we withheld the GB backfield; correct call, but we had no price for the miss).
- The official inactive list never reached us before kickoff: ESPN carries injuries (5 names per team) and nflverse `roster INA` lagged the league by hours (PIT@NO's inactives arrived by 15:31Z; the 1 PM teams had none at 16:21Z).
- Fixes: (a) a returning-player prior (last season's role times a rust factor) instead of silence; (b) fit P(inactive | depth rank, recent usage) from the `roster INA` history and discount fringe players; (c) a faster inactives source (see section 5).

### F6. Game script and volume, not forecastable pregame
- TB passed 11 times and ran 49 times (258 yards) in a 43-13 win; ARI threw 48 times; LA ran 38 times; MIA 41; SEA 41 (trailing KC ran). Pass attempts correlate 0.32 with projection, rush attempts 0.14; RMSE 7.5 vs standard deviation 7.8 (the same finding as W6).
- Upsets came from turnovers and touchdowns we cannot price: SF 4 turnovers (0.3 projected), CAR 3 (0.6), CIN 5 offensive TDs (2.6 projected), TB 4 offensive TDs (1.9).
- Fix: do not publish volume lines (rush attempts, pass attempts) as must-plays in games where the market spread is above 6 points; prefer per-opportunity stats. No model change.

### F7. Game-level: model-only adds no information the line lacks
- 13 games: model-only margin MAE 11.05 vs line 9.88. Backtest, 438 games: 9.91 vs 9.35, blend weight on the model 0.0. A rating-side re-tune (EPA target, recency, penalties, QB EPA) did not close it (DECISIONS #49).
- Next candidates need new information: quarterback-aware offense ratings with availability, injury-weighted unit strength, preseason priors if a source exists.

### F8. Touchdown board: calibrated overall, not yet on the tails
- 0.2-0.4 bins under-predicted by 9 points (24% predicted, 33% scored; 34% vs 44%); running backs 21% predicted vs 28%, wide receivers 14% vs 11.5%; top 30 at 46% vs 40%. In W6 the 0.1-0.2 bin was over-predicted. Direction flips by week; this is noise until the W9 review aggregates W4-W9.

## 4. What did not turn out to be a problem

- Tail receivers looked over-projected (+47% at within-team rank 4-9). The 2023-25 backtest shows +1% to +5% at those ranks. Noise; no fix proposed.
- Team points: market-anchored and the line were within 0.04 RMSE of each other. The anchor is working.
- Lamar Jackson Out was correct (Huntley started); a late ESPN drop of his name was a post-kickoff list artifact.

## 5. Decisions I need from you, and what I need you to find

1. **A price source** (an Odds API key, or timestamped DraftKings/FanDuel prop prices exported at each window). Without it, every calibration above rests on an assumed -110. This is the highest-value input.
2. **A faster official-inactives source**: any feed that publishes the NFL's 90-minute inactive list in a machine-readable form (a paid feed, or a page you know I can read). Right now we publish before the league's list reaches us.
3. **Josh Jacobs**: his status (reinstated, role) and, if you know it, any other returning or exempt players for Week 8.
4. **Approval to archive graded lines** outside the repo each week so the gap-aware shrink (F1) can be fit on four-plus weeks of data instead of one. I will keep only aggregated tables in the repo.

## 6. Work queue (each item needs its own weeks 4-12 backtest and a DECISIONS entry)

| # | Item | Test |
|---|---|---|
| 1 | Gap-aware shrink and 65% cap (F1) | graded-history Brier by gap and market |
| 2 | RB rush-yard dispersion 1.2, QB rush 1.1 (F2/F3) | coverage and pinball loss, three seasons |
| 3 | Returning-player prior and healthy-scratch discount (F5) | availability calibration table; unprojected-usage count |
| 4 | Parlay portfolio rule (F4) | unit test |
| 5 | Quarterback share 0.93 to about 0.975 with the dispersion change (previously queued) | all metrics plus coverage |
| 6 | QB-aware team ratings (F7) | `game_bt.py` beats the line in all three seasons |
