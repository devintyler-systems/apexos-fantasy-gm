# Week 8 full post mortem and Week 9 plan (2026-11-03)

**Answer.** Week 8 projections were fine and the book-edge picks were not. Player projections sit at or slightly better than the naive per-game average on 11 of 12 markets, the touchdown model is tied with the books, and game level was a coin-flip tie with the line (model-only 11 of 14 winners, same as the line). But the board we published against the books lost: **99 lines passing the value-board rule hit 38.4% for -25.1 units, the 20 top-10 over/under lines I published hit 4 of 20 (-12.7 units), and every parlay died on one leg (McKee over 0.5 pass TD; PHI scored 10).** On the 223 main lines of the late window the book's probability beat the engine's (Brier 0.249 against 0.289), and the 50/50 blend of DECISIONS #53 sat in between (0.264) and was worse than the book alone at every weight above zero. Same sign as the Week 7 Monday board (receptions 0.304 vs 0.242).

Ranked for Week 9, in order of return per hour (section 9): (1) stop labelling non-touchdown yardage and count lines as plays against the books until a forward ledger shows otherwise (needs your approval, DECISIONS #63); (2) fix the freeze-to-kickoff gap (a 3-point close move on KC@DEN, SEA's backfield) with a T-90 rerun, which is your input, not code; (3) shrink the spread between quarterbacks on passing yards (post-hoc backtest: MAE 63.22 to 62.29, better in all three seasons; the real knob still has to be built and run); (4) watch, do not change, the tight end and QB-rush biases.

**Framing challenge (once).** "Make MODEL-ONLY beat MARKET-ANCHORED" is measured at the game level, where market-anchored is the line plus noise and the honest bar is the closing line. This week model-only was ahead of the line on margin MAE (10.63 vs 10.82) and level on winners, and five weeks in it is still behind (margin MAE 9.31 vs 9.02, total MAE 10.95 vs 10.36, winners 62.5% vs 64.4%, n=72). At the prop level the two tracks are the same model (every market within 1% across tracks), so there is nothing to win there. The goal that matters for money is whether the shared player layer beats the books on any market. Two priced windows say not yet, except touchdowns where it ties.

## 0. What was and was not used

| Item | Used | Not used / missing |
|---|---|---|
| Frozen runs | last pre-kickoff pair per game (`postmortem.pick_runs`): Thursday `T2139*`, 1 PM `T1730*`, afternoon/SNF/MNF `T1906*`. Graded on a scratch copy; repo runs untouched | |
| Actuals | nflverse `stats_player_week_2026`, `snap_counts_2026`, `games` fetched 2026-11-03, all 14 games final | `pbp_participation` (2026 not published) |
| Prices | operator workbook for the five Sunday-afternoon/night and Monday games: 9 books, snapshot 18:42-18:48Z, 3,971 priced rows, 1,408 graded lines (`var/out_market/edges_all_rows.csv`, never committed) | **No Thursday or 1 PM prices exist in the repo.** Thursday singles graded by hand at an assumed -110; 1 PM graded as model lean against ESPN DraftKings lines at an assumed -110 (a line comparison, not an edge) |
| Closing lines | nflverse `spread_line`/`total_line` (game level only) | no prop closing lines, so no prop CLV |
| Inactives | none were supplied for the late window; the injury workbook and ESPN Outs governed | official NFL.com lists were never pasted. Effects below |
| Agents | none this turn (no freeze, no plays delivered); `grader` not run | `data-auditor`, `model-qa`, `red-team` apply to Week 9 freezes |

## 1. Game level (14 games; `postmortem.py`, `game_grade.py`)

| Predictor, week 8 | winners | margin MAE | total MAE | team-points RMSE | Brier |
|---|---|---|---|---|---|
| Model-only | 11/14 (78.6%) | 10.63 | 11.60 | 10.26 | 0.189 |
| Market-anchored | 10/14 (71.4%) | 11.10 | 11.19 | 10.00 | 0.191 |
| Line (nflverse close) | 11/14 (78.6%) | 10.82 | 11.29 | 9.95 | 0.172 |

Weeks 4-8 pooled (72 games): model-only 62.5% / 9.31 / 10.95 / 8.87, market-anchored 65.3% / 9.09 / 10.36 / 8.48, line 64.4% / 9.02 / 10.36 / 8.44. Per-game table in `GAME_GRADE_2026_W08.md`. The week's misses were scoring environments, not teams: TEN@CIN 79 points (line 45.5), LV@NYJ 71 (46.5), ARI@DAL 63 (54.5), ATL@TB 16 (42.5), CLE@PIT 33 (38.5).

**Stale anchor, one game.** The operator sheet (18:45Z) had KC -1.5 at DEN; the nflverse close is DEN -1.5, a 3-point swing, and DEN won by 4. The market-anchored run (frozen 19:06Z) priced KC as the favourite; KC@DEN kicked at 21:25Z. Cause of the move unverified. Cost: one game the line row got right and the anchored track did not. Fix is operational: a T-90 rerun with fresh lines (section 9, item 2).

## 2. Player projections (frozen pre-kickoff, p_active >= .5, a snap logged; `component_audit.py`)

Week 8 alone, then weeks 4-8 pooled (market-anchored; model-only within 1% on every row):

| Market | n wk8 / pooled | Bias wk8 | Bias pooled | MAE pooled | Naive MAE | Spearman model / naive | P25-P75 coverage | Slope |
|---|---|---|---|---|---|---|---|---|
| QB pass yards | 28 / 146 | **+15.1** | -4.6 (-2.0%) | 61.9 | 67.1 | .19 / .25 | 44% | 0.69 |
| QB completions | 28 / 146 | +1.7 | -0.8 | 5.06 | 5.59 | .20 / .23 | 45% | 0.74 |
| QB pass TD | 28 / 146 | -0.04 | 0.00 | 0.81 | 0.94 | .38 / .20 | 75% | 1.13 |
| QB rush yards | 28 / 84 | +3.5 | **+3.1 (+27%)** | 10.3 | 11.8 | .38 / .35 | n/a | 0.34 |
| RB rush yards | 47 / 241 | -4.2 | +2.2 | 25.7 | 25.6 | .62 / .60 | 35% | 0.94 |
| RB carries | 47 / 241 | -0.9 | 0.0 | 4.11 | 4.45 | .67 / .62 | n/a | 0.96 |
| WR receptions | 92 / 473 | +0.1 | +0.07 | 1.59 | 1.64 | .62 / .59 | 65% | 1.03 |
| TE receptions | 44 / 232 | +0.4 | **+0.26 (+8.4%)** | 1.68 | 1.69 | .43 / .43 | 61% | 0.72 |
| WR rec yards | 92 / 473 | +3.7 | +1.0 | 25.6 | 27.3 | .54 / .46 | 52% | 0.90 |
| TE rec yards | 44 / 232 | -0.5 | **+3.4 (+10.8%)** | 21.3 | 21.5 | .40 / .40 | 49% | 0.75 |
| RB rec yards | 45 / 216 | -0.2 | -0.2 | 14.8 | 15.4 | .23 / .24 | 47% | 0.64 |

- **The quarterback share fix held.** Pooled pass-yards bias is -4.6 (it was -9.3 over weeks 4-7). Week 8's +15 is one standard error on 28 quarterbacks (sd about 91 yards), so it does not argue against it. MAE 61.9 against 67.1 for the naive average, which is the best skill margin on the board.
- **Pass-yards projections are too different from one another.** Slope of actual on projected is 0.69 live and 0.48 in the 2023-25 backtest (0.58 / 0.47 / 0.45 by season), P25-P75 coverage 44% (nominal 50%). The model separates quarterbacks about twice as much as the results support (rank correlation .19). See section 8.
- **Receiving and rushing counts are as good as the naive average or better.** Intervals are too wide for wide receivers (P25-P75 coverage 65% against a 50% nominal) and too narrow for running-back rushing (35%). Not new.
- **Tight ends are over-projected** by 8% on catches and 11% on yards over 232 games, about 1.9 standard errors on each. The multiplier `tgt_TE` 1.17 was fit on 2023-25 weeks 4-12. Watch only.
- **Anytime TD (non-QB, played, 1,565 rows, weeks 4-8):** Brier .1204 against .1453 for a flat rate, log loss .382 against .466. Calibration is good in every bin but one: predicted .244, scored .306 in the .20-.30 bin (n=252, 2.1 standard errors; week 8 alone .241 vs .404 on 47). Mid-probability touchdown players score more than the engine says. High bin .562 predicted, .538 scored.

## 3. Availability and role

- Calibration (week 8, projected-active rows): p .95-.99 played 97.8% (45); p .5-.9 (mean .69) played 84.6% (13); p = 1.0 played 89.4% (283, includes depth players).
- Late window, projected active with p >= .9: **8 of 111 logged no offensive snap, all depth** (Wease, Bachman, Connors, Remigio, VanSumeren, Z. Scott, I. Charles, and SEA's Emanuel Wilson). Questionables: Nacua (81%, 52 snaps), Waddle (67%, 28), Burks (67%, 40) and Bates (67%, 21) all played; the 67% lines were right to project, wrong to read as coin flips.
- **Wilson is the miss that matters.** SEA's RB1 in the engine at p 1.0; he logged no snap. Charbonnet (6 carries, 4 targets) and Jadarian Price (10 carries, 4 targets) were unmodelled, so the engine gave Wilson's workload to the wrong people. I excluded Wilson and Holani from the published picks because of exactly this (DECISIONS #62), so no pick lost on it, but the SEA team totals carry the error.
- Real usage not in any projection: Minshew (ARI, 23 attempts), Fagnano (BAL, 21), Charbonnet, Price, Giddens (IND, 6 carries). Minshew (23 attempts, 188 yards) and Fagnano (21 attempts) were backup quarterbacks; whether they replaced an injured starter was not checked. The running backs are the open DECISIONS #61/#62 defect (active players with no current-season role, or listed on the depth chart but inactive).
- Team volume (14 games): pass attempts 33.1 projected, 31.1 actual (rmse 8.7, correlation .39); rush attempts 26.8 vs 28.5; pass TDs 1.46 vs 1.54, rush TDs 0.91 vs 1.00.

## 4. Prop picks, graded

Method: `priced_grade.py` (new) on the 3,971 priced rows; best price, 1 unit flat, pushes dropped, players with no stat row dropped.

**Late window, Brier by market (main line, over side; lower is better):**

| Market | n | Engine | Book | 50/50 blend |
|---|---|---|---|---|
| Receptions | 57 | .288 | .242 | .262 |
| Receiving yards | 58 | .288 | .250 | .266 |
| Rush yards | 32 | .282 | .249 | .257 |
| Rush attempts | 19 | .296 | .253 | .264 |
| Rush + receiving yards | 17 | .296 | .251 | .265 |
| Pass attempts / completions / yards (10 each) | 30 | .324 / .270 / .293 | .244 / .251 / .250 | .280 / .256 / .268 |
| Pass TDs | 10 | .274 | .275 | .273 |
| **All main lines** | **223** | **.289** | **.249** | **.264** |
| Anytime TD | 101 | .1414 | .1400 | .1400 |

- Weight sweep, final = book + w x (engine - book): w=0 .2490, .1 .2513, .25 .2554, .5 .2642, 1 .2889. Every market except pass TDs is best at w=0.
- The engine's lean (the side it likes more than the book does) hit **40.4%** (n=223). By size of disagreement: under 5 points 42%, 5-10 37%, 10-15 44%, 15-25 39%, over 25 points 37%. Regressing hit on book probability and the gap gives a gap coefficient of -0.60 (standard error 0.24). Games are correlated and this is one window of five games, so read it as no evidence that disagreements carry information, not as proof they are anti-informative.
- **Value-board rule picks** (main, not pass yards, no gap flag, p_active >= .9, EV > 0): 99 lines, 38.4% hit, **-25.1 units**; overs 32.6% (46, -16.1), unders 43.4% (53, -9.0). The 40 highest by shrunk probability hit 40%, -10.2.
- **The lists I published** (best prices as posted): top-10 overs 2 of 10 (Smith-Njigba 118 yards, Dulcich 43; -6.2 units), top-10 unders 2 of 10 (Rachaad White 2 catches, Bo Nix 3 rush attempts; -6.5), top-10 anytime TDs 2 of 10 (Douglas, Diggs; -3.1). SNF-only lists: 8 of 20 (-5.0). Parlays: 2-, 3-, 4- and 6-leg all lost on McKee over 0.5 pass TD (0 passing TDs).
- **Touchdowns:** the bets with EV above 5% at the estimated prices were 25 lines, 5 hit, +26.4 units at average probability .16. That is long-shot variance on a 10% haircut price, not a result.
- Highest-probability touchdowns went 4 of 6 (Swift, Smith-Njigba, Nacua, K. Williams scored; Walker and Stevenson did not).

**Thursday CAR@GB (published singles, assumed -110):** PLAY Love pass attempts over 34.5 hit (41); Evans receptions under 1.5 missed (2); Waller (CAR) receiving yards over 21.5 missed (11 yards on 2 targets). LEAN Young rush yards under 9.5 (0), Love rush yards under 4.5 (0) and Love completions over 21.5 (30) all hit. Touchdowns: Hubbard 44% scored, Jacobs 38% scored, Kraft 34% scored, Watson 35% and Golden 40% did not. No Thursday prices existed to measure units.

**Sunday 1 PM (projections only, no prices):** the engine's lean against 275 ESPN DraftKings lines (model mean vs line, p_active >= .9) hit 56.7%; unders 66.4% (110), overs 50.3% (165); by receptions 60.5% (86), receiving yards 54.0% (87), rush yards 57.4% (47), rush attempts 48.0% (25). Mean absolute error against actuals: engine 18.43, line 18.51. A tie, with the break-even at -110 near 52.4%, so about 4 points of lean value that no one priced; n is too small to promote anything.

## 5. DFS (Showdown, PHI@WAS)

Lineup: Daniels CPT, McKee, Goedert, Lemon, Okonkwo, Stevens at $49,800. Scored **70.5** DraftKings points (projected mean 85.7, P99 150). The best salary-legal lineup in hindsight scored 91.2 (Stevens CPT with Daniels, Barkley, Diggs, White and the Commanders DST at $48,100; DST points approximate), so the lineup was 77% of the ceiling. Stevens (4 field goals, 16 points) was the top scorer on the slate and was in the lineup as a FLEX; the engine's flat 3.9 per field goal values an average kicker, and four made field goals is a tail outcome. The 37-point total (projection 40.0) cut every ceiling. Alternate lineup (Goedert CPT) scored 61.1. Kicker distance is still not modelled.

## 6. Closing-line value

Game level only, and it was one game: KC@DEN (section 1). No prop closing lines exist in the repo for this window; ESPN `current` lines carry unreliable stamps (Week 7 post mortem section 2). CLV by price stays unmeasured until the Odds API history or a second workbook pull at T-5 minutes exists.

## 7. External benchmark

No new research this week. The Week 7 report stands (nfelo is the best free QB-aware benchmark and sits about 0.1 point from the close, sign convention unverified).

## 8. Candidate changes (nothing was applied; all need a backtest and a DECISIONS entry)

1. **Blend weight on non-touchdown props, selection rule (value_board.py), proposed w=0 outside TDs.** Evidence: two priced windows (Week 7 Monday, Week 8 late: 56 and 223 main lines), Brier book < blend < engine in every market, hit 40% on the engine's lean. Cannot be backtested: no historical prices in the repo. It can only be settled forward, which is what `calibration_ledger.csv` is for (`board_late` rows added for week 8, 89 rows, no prices). Cost: an hour. Risk: two windows is thin; a forward ledger of four windows decides. This is a DECISIONS #53 change, so it needs your call.
2. **Quarterback cross-sectional shrink on passing yards.** Backtest pickles (2023-25 weeks 4-12, 671 games, qb_share .96 base): slope .48; shrinking each quarterback's projected yards toward that slate's mean by a factor s lowers MAE 63.22 (s=1) to 62.86 (.9), 62.56 (.8), 62.29 (.7), 62.10 (.6); better in all three seasons at every s (2023 68.03 to 66.81, 2024 62.23 to 61.20, 2025 58.59 to 58.11 at .7). Completions MAE 5.01 to 4.99. This is post-hoc on means; it is not a sim-level change and says nothing about joint consistency with attempts and touchdowns. The implementable version is a stronger shrink of the quarterback efficiency (yards per attempt) prior in the QB layer, then `eval_qb.py` against `q960s`. Falls under `promotion_rule_qb_only`. Gain is about 1.5% of QB pass-yards MAE (compare qb_share's 0.7%), which matters most where the books beat us by the most.
3. **Unmodelled-active and depth-chart-gated availability** (DECISIONS #61, #62): Wilson/Charbonnet/Price this week, 22 no-snap incidents in weeks 4-7. Needs the availability-table backtest named in #61. Larger than item 2 in effect on running-back and team-total error, larger in cost.
4. **Watch only, no change:** TE receiving (+8.4% / +10.8% over 232 games, 1.9 standard errors; refit `tgt_TE` only if it holds at about 330 games, around week 10), QB rushing yards (+27%, 1.9 standard errors; the DFS overlay already scales it), the .20-.30 touchdown bin (2.1 standard errors).

Rejected after review: re-fitting level calibration on live data (bias is inside the noise on every market but the two above); a per-market blend fit on the Week 8 sample alone (n too small); any Week 9 model change shipped without a backtest.

## 9. Ranked Week 9 plan

| # | Item | Why it ranks here | Owner / input | Backtest needed |
|---|---|---|---|---|
| 1 | Publish non-TD props as "engine median vs line" information, not PLAY/LEAN, until the ledger has four priced windows; keep TDs, fantasy projections and DFS as the product | -25 units on the rule's picks, 4/20 on mine, book beats blend in every non-TD market, two windows agree | your approval (DECISIONS #53 change) | forward ledger |
| 2 | T-90 rerun per window with fresh lines and the official inactives pasted | KC@DEN moved 3 points; SEA's backfield (Wilson out, Charbonnet and Price unmodelled); the largest controllable error in the week | you paste the NFL.com lists; I rerun in about 10 minutes | none |
| 3 | QB passing-yards shrink (item 8.2): **built and promoted at 0.7, DECISIONS #65** (the yards-per-attempt version failed; the volume-level shift passed in all three seasons) | done 2026-11-03 | done | weeks 4-12, 2023-25 |
| 4 | Depth-chart-gated p_active (#61) and a trailing-games feature | unmodelled and phantom players cost team totals | me | availability backtest |
| 5 | Ledger: add every priced window as `board_*`; at four windows, fit shrink by market | turns item 1 into a decision rule | me, with your workbooks | none |
| 6 | Kicker distance model for Showdown | Stevens' four field goals; flat 3.9 per field goal | me, low | none |

## 10. Week 9 run checklist (Week 9 slate: Thursday Nov 5 to Monday Nov 9; Eastern time all week)

1. `cli fetch --season 2026`; confirm `games.parquet` has Week 9 lines. 2. Wednesday: refit nothing (refits are scheduled); run both tracks for all games, `data-auditor` and `model-qa`, freeze. 3. Thursday: rerun at T-150 with the injury workbook and ESPN Outs; label every defender CB/SS/FS/S/DE/DT/NT/OLB/ILB (the engine counts literal "DB" as a safety). 4. Each window: pasted NFL.com inactives into `manual_out`, rerun the affected games, new freeze, then price. 5. `red-team` before delivering any play. 6. Tuesday: `grader`, `postmortem.py`, `game_grade.py`, `component_audit.py`, `priced_grade.py`, append ledger rows.

## 11. What I need from Devin

1. **Approve or reject item 1** (non-TD props become information only until four priced windows agree). One word.
2. **Paste the official inactives** about 90 minutes before each window's kickoff. This is the single largest controllable error in the week.
3. **Odds workbook pulls**: one at T-90 and one at T-5 minutes for each window (the second gives prop closing lines and the first week of real CLV). Save Thursday's and the 1 PM window's workbooks if they exist; I have only the late-window file.
4. Whether to spend the time on item 3 (QB shrink) this week or hold until the blend decision is in.

## Appendix: what changed in the repo with this post mortem

`engine/weekly/priced_grade.py` (new, read-only), `docs/weekly/GAME_GRADE_2026_W08.md`, `docs/weekly/POSTMORTEM_2026_W08_FULL.md`, DECISIONS #63, 89 `board_late` rows in `config/weekly/calibration_ledger.csv`. No model, calibration or frozen-run change. Scratch graded copies of the runs were not committed.
