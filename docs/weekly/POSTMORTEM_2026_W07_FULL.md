# Week 7 full post mortem and Week 8 plan (2026-10-27)

**Answer.** Week 7 was an ordinary week for projections and a bad week for the picks, and the model-only track is not close to beating the line at the game level. Three things are ranked above the rest for Week 8:

1. **Quarterback share is the one calibration error with a clean backtest win.** Raising `qb_share`/`qb_td` from 0.93 to 0.96 cuts the 2023-25 weeks 4-12 passing-yards MAE by 0.45 and pinball loss by 0.22, better in all three seasons, with no change to any receiving, rushing, TD or team metric. Live 2026 bias matches (-9.3 yards, weeks 4-7). It cannot ship under the current promotion rule (the rule's metrics are byte-identical for a QB-only change), so it needs your call on a rule amendment (DECISIONS #58).
2. **Prices at every window decide whether the picks are measurable.** Only the Monday board is gradable with real prices from the repo. Saturday, Sunday and the Thursday window prices live in your workbooks, which I do not have in this environment.
3. **Availability: 22 no-snap incidents among 700 real-role player-games (usage 2 or more) in weeks 4-7; 9 of the 22 repeated an earlier no-snap by the same player** (Gainwell 4 incidents, Bam Knight 4, Demercado 2, Shepard 2, Ertz 2). A trailing-games-played feature is the cheapest fix on the list.

**Framing challenge (once).** "MODEL-ONLY beats MARKET-ANCHORED" is two different goals. At the player level the two tracks are the same model: every market's MAE differs by under 0.3% between tracks (section 3), so there is nothing to win there; the contest is the shared player layer against the books. At the game level market-anchored is the line plus noise, so the real bar is the closing line itself, which no public model clears (nfelo, the best free QB-aware benchmark, sits about 0.1 point from the close per the research below, UNVERIFIED sign convention). A realistic target is closing about half of the 0.63-point margin gap with new information, and reading model-only as an input to a blend, not as a replacement.

## 0. What was and was not used

| Item | Used | Not used / missing |
|---|---|---|
| Frozen runs `runs/weekly/2026_w0{4..7}_*`, last pre-kickoff pair per game | yes, copied to a scratch directory; repo runs untouched | |
| nflverse stats, snaps, schedules, pbp, 2022-26 (fetched 2026-10-27) | yes | `pbp_participation` (2026 not published) |
| Prices (Odds API workbooks, six to nine books) | only what is printed in `MNF_FULL_RUN_2026_W07.md` (best price per line, 58 rows) and the Sunday post mortem's published aggregates | **No workbook, no `ODDS_API_KEY`, no per-book prices for Thursday, Saturday, 9:30, 1 PM, 4 PM, SNF in this environment.** Per-book ROI, best-price units and Brier-vs-book for those windows were not recomputed. |
| Closing lines | ESPN DraftKings `open`/`current` lines fetched post-game (line only, no prices) | Timestamps are unreliable (below), so these are "last line the feed holds", not verified closes. True CLV needs the workbooks or the Odds API history. |
| Inactives | operator-read NFL.com list for Monday (already in the repo) | Sunday T-90 lists were never in the repo; no change to what is known |
| DK salary files | none | Showdown salary-legal optimum cannot be rebuilt; the lineup is graded on DK points only |
| Agents | `general-purpose` (external research) | `data-auditor`, `model-qa`, `red-team`, `grader` were not run: this PR produces no freeze and delivers no plays. They are in the Week 8 checklist. |
| Sunday window sims | not kept (known) | per-line Sunday grading stands on the Sunday post mortem |

## 1. Regrade (what could be regraded)

**Monday night, DAL@PHI, priced board** (`board_grade.py`, 58 rows parsed, 56 graded, best price, 1 unit flat):

| Group | Lines | Hit | Units | Model p | Book p | Brier model / book |
|---|---|---|---|---|---|---|
| PLAY | 3 | 33% | -1.19 | 0.60 | 0.52 | 0.288 / 0.234 |
| PASS (all other) | 53 | 47% | +1.87 | 0.50 | 0.41 | 0.230 / 0.219 |
| Anytime TD | 18 | 33% | +1.62 | 0.19 | 0.21 | 0.168 / 0.165 |
| Receptions | 11 | 45% | -2.37 | 0.64 | 0.54 | 0.304 / 0.242 |
| Receiving yards | 12 | 42% | -2.44 | 0.63 | 0.50 | 0.304 / 0.248 |
| Rush yards + attempts | 9 | 67% | +2.33 | 0.74 | 0.50 | 0.16 / 0.25 |
| Pass yards / completions / attempts | 6 | 67% | +1.55 | | | |

By confidence (book + 0.5 x (model - book)): 0.50-0.55 hit 47% (15), 0.55-0.60 hit 50% (12), above 0.65 hit 75% (8, +3.1 units, all rush or pass lines). The model's own probability on the chosen side is worse than the book's on the side it chose (receptions 0.304 vs 0.242, receiving yards 0.304 vs 0.248): where it disagrees with the book on receiving, the book is right. n is 3 to 18 per row; read as direction only. Rows were appended to `config/weekly/calibration_ledger.csv` as source `board_mnf` (the existing `book_anchor` rows for week 7 are untouched; the ledger's append replaces by week and source, so a new source name was necessary).

**Gate outcomes on Monday (not a model change):** lines blocked as "model 15+ points from book" hit 50% (10, -0.86u): gate fine. Red-team pulls hit 67% (3, +0.86u), downgrades 33% (3, -1.05u): no verdict at this n. "No edge at best price" hit 50% (12, -1.17u): fine.

**Sunday, Thursday:** unchanged from `POSTMORTEM_2026_W07_SUNDAY.md` and `TNF_NE_CHI_2026_W07_SCORECARD.md` (Sunday: must-plays 2 of 9, PLAY 10 of 17, 402 screened lines 55% against 61% raw; Thursday: 11 of 22, +0.43u on 18 priced). I could not add per-book numbers. **Shipped:** tooling only.

## 2. Closing-line value (line only, indicative)

ESPN's `current` line was fetched for all 14 games after final (506 player-market lines; 440 usable at p_active 0.9 or better). Its `last_updated` stamps range from 6,000 minutes before kickoff to 180 minutes after, and the zone is unverified (same issue as DECISIONS #50), so `current` may include in-game numbers. Treat it as indicative.

- Open to current: the line moved on 55% of lines; the move agreed with the model's lean on **54.7%** of the 245 moved lines (the Thursday-to-Sunday workbook test in the Sunday post mortem said 39%; with unverified clocks and different horizons I do not read this as a contradiction or a confirmation).
- Model side hit against the OPEN line 54.5% (n=440), against the last line 49.1%; at a 10%+ gap 56.2% vs open, 50.7% vs last. No evidence of an edge against the last line.
- Pooled MAE against actuals: last line 13.21, open 13.61, model 13.92. By market (model / last line): pass yards 49.4 / 46.0 (bias -15.1 vs -4.8), rush yards 22.5 / 20.1, rush attempts 4.38 / 4.26, receiving yards 21.1 / 20.6, receptions 1.41 / 1.39, completions 3.67 / 3.85 (model better, n=23). **The books are more accurate than the model on every yardage and count market except completions; the margin is largest on pass yards and rush yards.**

Status: **proposed** (needs the Odds API history or the workbooks to settle). Tag: CLV by price is still unmeasured.

## 3. Component audit, weeks 4-7 (4 slates, frozen pre-kickoff runs; `component_audit.py`, market-anchored; model-only within 0.5% on every row)

| Market | n | Proj | Actual | Bias | MAE | Naive MAE | Rank corr model / naive | P25-P75 coverage | Calib. slope |
|---|---|---|---|---|---|---|---|---|---|
| QB pass yards | 118 | 222.7 | 232.0 | **-9.3 (-4.0%)** | 59.8 | 64.9 | 0.25 / 0.29 | 43% | 0.73 |
| QB completions | 118 | 19.9 | 21.3 | **-1.4 (-6.5%)** | 4.77 | 5.35 | 0.25 / 0.25 | 47% | 0.83 |
| QB pass TD | 118 | 1.42 | 1.42 | 0.01 | 0.76 | 0.92 | 0.40 / 0.19 | 77% | 1.12 |
| QB rush yards | 56 | 15.1 | 12.2 | **+2.9 (+24%)** | 10.1 | 11.4 | 0.42 / 0.43 | n/a | 0.40 |
| RB rush yards | 194 | 51.4 | 47.6 | +3.8 (+8%) | 24.6 | 24.2 | 0.65 / 0.62 | **38%** | 0.96 |
| RB carries | 194 | 11.7 | 11.5 | +0.2 | 3.83 | 4.27 | 0.72 / 0.65 | n/a | 1.00 |
| WR receptions | 381 | 3.21 | 3.14 | +0.07 | 1.59 | 1.62 | 0.63 / 0.62 | 66% | 1.02 |
| TE receptions | 188 | 3.30 | 3.08 | +0.22 (+7%) | 1.68 | 1.75 | 0.45 / 0.41 | 61% | 0.73 |
| RB receptions | 171 | 2.34 | 2.43 | -0.09 | 1.46 | 1.62 | 0.35 / 0.28 | 68% | 0.70 |
| WR receiving yards | 381 | 41.4 | 41.1 | +0.3 | 26.0 | 27.5 | 0.55 / 0.47 | 50% | 0.93 |
| TE receiving yards | 188 | 34.2 | 30.0 | **+4.3 (+14%)** | 20.9 | 22.0 | 0.41 / 0.37 | 50% | 0.75 |
| RB receiving yards | 171 | 18.0 | 18.1 | -0.2 | 14.0 | 14.9 | 0.30 / 0.26 | 46% | 0.81 |

Anytime TD (non-QB, 1,263 rows): log loss 0.383 against 0.461 for a flat rate; bins calibrated within sampling error (0.20-0.30 predicted 24.4%, scored 28.3%; 0.30-0.45 predicted 36.3%, scored 39.1%; 0.45+ predicted 56%, scored 53%). Team volume week 7: pass attempts 33.8 projected, 31.5 actual (correlation 0.25), rush attempts 26.3 vs 27.8 (0.07).

Reading it, ranked by what each is worth:

| # | Finding | Evidence | Fix | Worth | Status |
|---|---|---|---|---|---|
| C1 | **QB passing is 4 to 6.5% low in 2026 and in 2024-25 backtests** | bias -9.3 live, -13.0 in 2024 and 2025 backtests, +1.0 in 2023; completions -6.5% | `qb_share` 0.93 to 0.96 (backtest below) | pass yards MAE -0.45, pinball -0.22 | **proposed, backtested** |
| C2 | RB rush yards: P25-P75 holds 38% (target 50%) | W4-7 38%; 2023-25 backtest 44% (Sunday post mortem: best rescale 1.2) | dispersion x1.2 RB, x1.1 QB | pinball/coverage, no mean change | proposed, needs coverage backtest |
| C3 | QB rush yards over-projected 24% with slope 0.40 | n=56, bias +2.9 | scramble/design-run split or shrink toward the QB's own average | QB rush lines only | proposed |
| C4 | TE receiving yards +14%, TE receptions +7%, calibration slope 0.75 | n=188 | TE share multiplier 1.17 (`share_mult.tgt_TE`) may now be high; refit | TE receiving lines | proposed, needs `calibrate_bt.py` |
| C5 | Pass yards rank skill 0.25 (model) vs 0.29 (naive per-game average) | n=111 | the model does not out-rank a player's own average; blend 50/50 gives MAE 60.2 vs 61.4 for the model | QB pass yards edge | proposed |
| C6 | Receptions, receiving yards (WR/RB), carries, pass TD, anytime TD | all beat the naive average on MAE and rank | none | | no action |

Rejected on this evidence: a tail-receiver haircut (already rejected in DECISIONS #52); no new rejections.

## 4. Availability and role

| Event | How we found out, how late | Cost |
|---|---|---|
| Healthy scratches among real-role players (usage 2 or more): 22 of 700 in weeks 4-7 (3.1%); RBs 80% played overall, TEs 96%, WRs 84% | not knowable pregame except through the player's own history | 13 players, 9 of the 22 incidents were repeats: Gainwell (TB) projected 5 to 6.5 usage units and logged no snap in all of weeks 4-7, Bam Knight (ARI) 4 times, Demercado 2, Shepard 2, Ertz 2 |
| Zach Ertz (PHI TE), W7 projected active (8.3 DK points), no snap; NFL.com official list did not name him | inactives list had no signal | MNF showdown lineup carried him (0 points) |
| Josh Jacobs (GB) 7 targets, 11 carries, no row | gated out of lines (#50), prior from last season not yet built | no price on the miss |
| Elijah Mitchell (PHI) 3 carries / 4 targets | not projected | small |
| Barkley active, Pierce backup (MNF) | official NFL.com list, operator-read at T-90; ESPN flag wrongly said inactive | late rerun; model's carries (6.8 / 11.3) closer than books (15.5 / n/a) to actual (7 / 14) |
| Sunday official inactives | never reached us before kickoff; nflverse `roster INA` lags by hours | the whole W7 Sunday availability gap |

Players with p_active 0.99 or better logged a snap 87% of the time (weeks 4-7); the cause is the low-usage tail, not the starters: projected usage above 5 units played 98 to 100%, under 1 unit 56 to 81%. The shipped model does not discount low-usage players with a no-snap history. Fix: **trailing games-played rate** (snaps recorded in the player's last three team games, from `snap_counts`) as a multiplier on p_active for players under 5 usage units, fit on 2023-25 weeks 4-12 before shipping. Worth: removes the ghost-projection rows that inflate the TD board, the pass-catcher share sums and the DFS pool. Status: **proposed**, needs its own backtest (availability calibration table and unprojected-usage count).

Faster inactives: the research found nothing faster than the official NFL.com list at about T-90 (nflverse `roster INA` rows appear hours later; no machine-readable free feed was verified). Keep the operator step; make it mechanical (section 7 checklist) and always run `operator_inactives.py` with an explicit Active list for both teams. **Rejected:** hunting for a faster free feed this week.

## 5. Game level

- Weeks 4-7 (58 games): model-only winner 58.6%, margin MAE 8.99, total MAE 10.80, against the line 61.0% / 8.59 / 10.14 and market-anchored 63.8% / 8.60 / 10.16. Reproduced from `game_grade.py` output; week 7 alone model-only 57.1% / 11.52 / 10.49 vs line 71.4% / 10.07 / 10.43.
- Multi-season baseline reproduced with `team_rating_lab.py`: weeks 4-12 of 2023-25 (393 games) margin MAE **10.12 vs line 9.49**, total 9.66 vs 9.48; blend weight on the model 0.0 for margin, 0.2 for total.
- Model margin has standard deviation 4.6 against 5.8 for the line, and the actual margin regresses on model margin with slope 1.17 (on the line, 1.22): the model's margins are compressed, as are the line's. Scaling model margins by 1.1 to 1.3 does not lower MAE.
- **New test: QB-aware margin adjustment** (`qb_rating_lab.py`). Adjusts the margin by beta x (starter-now EPA/dropback minus the dropback-weighted EPA/dropback of the quarterbacks behind the team's rated games). 88 of 393 games carry a quarterback change (|delta| above 0.05). Beta 20 points per EPA/dropback: margin MAE 10.121 to **10.043** (2023 9.968 to 9.919, 2024 10.121 to 10.023, 2025 10.276 to 10.190); beta 10 and 30 give 10.064 and 10.045; beta 60 worsens to 10.165. Adding a rest-day term (0.3 per day, capped at 4) gives 10.031. Total MAE is flat to worse (9.661 to 9.664 at beta 5). **It recovers about 0.08 of the 0.63 gap, consistently in all three seasons, and still does not beat the line (9.49); the blend weight stays 0.0.** Under DECISIONS #48 it does not ship. Status: **proposed as an input**, rejected as a game-level promotion. A published QB Elo (nfelo) is the next test (`nfeloqb`, free, license UNVERIFIED).
- Week 7 misses: both disagreements with the line were wrong (CIN@BAL, DAL@PHI). The model sat 3 or more points from the line in 20 games and was closer in 9 (45%). Game script drove the volume misses (pass attempts correlation 0.25, rush attempts 0.07 in week 7); this is not forecastable pregame (DECISIONS #40) and nothing new here changes that.

## 6. DFS and Showdown (MNF, DAL@PHI)

Actual DK points (with the 100-yard and 300-yard bonuses) from the nflverse box score:

| Player | Actual | Engine mean (no bonuses) |
|---|---|---|
| Javonte Williams DAL | 24.5 (155 rush yards, 1 TD) | 16.7 |
| CeeDee Lamb DAL | 24.4 (5-74-2) | 17.6 |
| Dak Prescott DAL | 23.3 (212, 3 TD) | 17.7 |
| Makai Lemon PHI | 19.7 (7-67-1) | 9.2 |
| Pickens DAL | 15.7 | 14.6 |
| Barkley PHI | 15.1 | 8.5 |
| McKee PHI | 11.5 | 14.9 |
| Goedert PHI | 9.8 | 12.3 |
| Zach Ertz PHI | **0 (no snap)** | 8.3 |

The published lineup (CPT Lamb 1.5x = 36.6, Prescott 23.3, McKee 11.5, Goedert 9.8, Lemon 19.7, Ertz 0) scored **100.9**. The best six without a salary cap (CPT Williams, Lamb, Prescott, Lemon, Pickens, Barkley) scored 135.0, so the lineup left about 34 points; Ertz alone is 8.3 projected points that went to zero. What must change before this is trusted: (1) the engine's DK projection omits the 100-yard bonus, which Williams hit here; (2) Ertz-type ghost rows (section 4) enter lineups; (3) kicker/defense are approximate; (4) there is no backtest and no ownership. Prior Showdown ceiling lineups also finished below their simulated mean (W5 TB@DAL 60.35 vs mean 89.8). Status: **dfs_showdown.py stays exploratory; do not publish it as a play until a salary-file backtest of at least 4 slates exists.** Salary-legal comparison needs the DK Showdown salary file (not in the environment).

## 7. External benchmarks (sub-agent research, 2026-10-27; every URL in the agent's report; UNVERIFIED rows marked)

| Source | Cost | Use | Verdict |
|---|---|---|---|
| The Odds API (historical event odds, player props from 2023-05) | $30 to $119 per month plans; history costs 10 credits per market per region per call | repeating prices at every window, completions and TD markets, true closes | **ADD** (about 1k credits per snapshot) |
| nfeloqb QB Elo / nfelo ratings (GitHub CSV) | free, license UNVERIFIED | QB term for game ratings, benchmark margin | **TEST** |
| FantasyPros API | Premium $8.99 per month, non-commercial; scraping barred by ToS | consensus benchmark, news clock | **TEST**, drop scraping |
| nflverse `nextgen_stats`, `pfr_advstats` | free | efficiency priors for pass and receiving yards | **TEST** (SumerSports YPRR did not help, #42) |
| Sleeper projections | free, undocumented endpoint, non-commercial | benchmark already archived | keep, ToS risk |
| NWS forecast | free | wired (#39), archive each window | keep |
| `pbp_participation` | free, 2026 unpublished | | skip |
| Pinnacle resellers, Unabated, OddsJam, Action Network | scrapers or sales-gated | | skip |
| Preseason win totals | no free CSV | | skip |

PFF, Numberfire, Sharp Football, Pro Football Reference and Fantasy Footballers were not verified; no claim is made. Target-setting evidence is thin: practitioner data (PFF 2020: 54% of passing-yard props and 53% of receiving-yard props hit the under) and old FiveThirtyEight work (final margins about 13.45 points around the Vegas line against 13.65 for Elo). No peer-reviewed prop-efficiency study was found.

## 8. Process review

- **Inactives timing** is the single largest risk: a wrong ESPN flag drove a published Pierce thesis (#54) until the operator corrected it (#55). The rule "a new source is not used to publish until checked against the official list on a full slate" is right and stays.
- **Line staleness:** `price_odds.py` drops lines over two hours old by design; Sunday prices were three days old, so the Sunday windows had no usable prices. Fix is the repeating feed, not the filter.
- **Gates that helped:** pass-volume unders pulled (they went 1 of 6), model-15-points-from-book blocks (50%, -0.86u), the 85% probability ceiling, the Barkley correction.
- **Gates that suppressed winners:** the RB-out gate on CHI backs (4 of 4 would have won, +3.33u, #43); red-team pulls on Monday (2 of 3 won); the receiving-LEAN suppression (6 of 11 in week 7 after 35% in week 6: inconclusive).
- **Duplicates and correlation:** one-bet-per-script rules (#37) and the parlay rule held; no new problem found. Highest-chance Sunday parlays all lost on a shared Brown/Murray leg (F4, fixed in construction).
- **Process gap found today:** `postmortem.py` docstring advertises an `--out` flag that does not exist and its `grade()` writes into the frozen run folder. This post mortem ran it on a scratch copy via `--runs`. Proposed: make `grade()` take an output directory.

## 9. Backtest: quarterback share (candidate for Week 8, not applied)

`APEX_QB_SHARE` and `APEX_QB_TD` env knobs were added to `sim.py` (default unchanged, byte-identical: the receiving, rushing, TD and team metrics of `eval_candidate.py` are identical to the baseline for both candidates). Model track, 5,000 sims, weeks 4-12, 2023-25 (671 QB games), `eval_qb.py`:

| Tag | Pass yds MAE | Bias | P25-P75 | P10-P90 | Pinball | Completions MAE | Pass TD MAE |
|---|---|---|---|---|---|---|---|
| base 0.93 / 0.95 | 63.67 | -8.0 | 45.3% | 78.2% | 19.79 | 5.030 | 0.935 |
| 0.96 / 0.96 | **63.22** | -1.4 | 47.4% | 79.4% | **19.58** | **5.012** | 0.935 |
| 0.975 / 0.975 | 63.14 | +1.9 | 48.7% | 80.3% | 19.54 | 5.021 | 0.936 |

Per season, 0.96 vs base: MAE -0.16 (2023), -0.65 (2024), -0.57 (2025); pinball -0.09, -0.30, -0.27. 0.975 is no better than 0.96 in 2023 and overshoots it (+11 yards bias). Recommended value **0.96** (bias is -6.4 to -6.7 in 2024-25 and +7.8 in 2023, so 0.96 is the centre). Pass TD MAE is unchanged to the third decimal; `qb_td` 0.95 to 0.96 has no measurable effect and is not worth changing separately. The promotion rule (`grading.v0.1.yaml`: beat rec_yds MAE and TD log loss) cannot see this change, so under a literal reading it fails by a tie. **Decision for Devin:** amend the rule to add "QB-only changes are judged on passing-yards MAE, pinball, completions MAE and P25-P75 coverage, no worse on the existing metrics" (DECISIONS #58). If approved, change `config/weekly/calibration_params.json` `qb_share` to 0.96 in the Week 8 Wednesday run.

## 10. Ranked Week 8 plan

| Rank | Item | Impact | Effort | Backtest | Status |
|---|---|---|---|---|---|
| 1 | `qb_share` 0.96 (pass yards, completions) | high on the worst book market | 1 line + rule amendment | done (section 9) | **needs your call** |
| 2 | Repeating prices at every window (Odds API key as secret, or workbook exports) | unlocks per-book ROI, CLV, per-market shrink fit | key + 1 cron-like step | n/a | needs you |
| 3 | Trailing games-played multiplier on p_active for low-usage players | removes ghost rows (3.1% of real roles, 41% of incidents are repeats) | 1 day | availability calibration + unprojected usage, 3 seasons | proposed |
| 4 | RB rush dispersion x1.2, QB rush x1.1; TE share refit (C2, C4) | coverage 38% to about 50%; TE yards bias 14% | 1 day | coverage + pinball, 3 seasons | proposed |
| 5 | Gap-aware shrink toward the book probability, per-market weights (ledger now holds 3 sources of week 7) | calibration of every published probability | fit needs weeks 8-10 of priced rows | graded-history Brier | proposed, wait for data |
| 6 | QB Elo term in game ratings (`qb_rating_lab.py` result, nfelo test) | at most about 0.08 to 0.15 of the 0.63 gap | 2 days | `game_bt.py`, all three seasons beat the line row (does not today) | proposed as input only |
| 7 | Returning-player prior (Jacobs) | small | 1 day | unprojected-usage count | downgraded (Barkley/Pierce evidence, #57) |
| 8 | DK bonus (100/300) and ghost-row exclusion in projected DK points; Showdown backtest | DFS only | 1 day | salary files, 4 slates | proposed |
| 9 | `postmortem.grade()` output directory; docstring fix | safety | 1 hour | unit test | proposed |

## 11. Week 8 run checklist (Week 8 slate: Thursday Oct 29 to Monday Nov 2; clocks fall back Sunday Nov 1, so Sunday kickoffs are EST, one hour later in UTC than this week)

| When (ET) | Owner | Step |
|---|---|---|
| Tue Oct 27 (now) | Devin | Decide the two calls in section 12; send the prop workbooks or set `ODDS_API_KEY` |
| Wed Oct 28 morning | Claude | `fetch`, QB1 table check, `run --track both`, `data-auditor` and `model-qa`, freeze `2026_w08_*`, post open lines |
| Wed Oct 28 evening | Devin | Workbook export (open) |
| Thu Oct 29 (TNF window), T-3h, T-90 | Devin then Claude | Workbook, NFL.com inactives; operator inactives -> `operator_inactives.py`; rerun the game; `red-team`; publish |
| Fri-Sat Oct 30-31 | Claude | `injury-update` skill, overlay for any designation not in the nflverse feed (DECISIONS #45), Saturday freeze |
| Sun Nov 1 | Devin | Workbook at T-3h before each window; NFL.com inactives at T-90 (EST: 1 PM kickoff = 18:00Z, T-90 = 16:30Z; 4 PM games 21:05Z/21:25Z, T-90 19:35Z/19:55Z; SNF 01:20Z Nov 2, T-90 23:50Z) |
| Sun Nov 1 | Claude | Rerun affected games with explicit Active lists for both teams, `red-team` before every publish; never publish a source not validated against the official list |
| Mon Nov 2 | Both | Same T-90 routine for the Monday game |
| Tue Nov 3 | Claude | `grader`, `postmortem.py --runs <scratch copy>`, `board_grade.py` on every published board, `component_audit.py`, append ledger rows, DECISIONS entry |

## 12. What I need from Devin (exact)

1. **Prop-odds workbooks for Week 7** (Thursday, Saturday, Sunday 9:30/1 PM/4 PM, SNF) so the per-book ROI, best-price units and true CLV can be added to this document; or `ODDS_API_KEY` as an environment secret (never paste it). Without them the Sunday grade stays at the Sunday post mortem's aggregates.
2. **Official NFL.com inactives lists** for Week 7 Sunday (any you saved) to score how late each scratch was found; and, going forward, the T-90 lists each window.
3. **DraftKings Showdown salary file for DAL@PHI** (and each Showdown slate) for a salary-legal lineup grade.
4. **Two calls:** (a) approve the promotion-rule amendment for QB-only changes and `qb_share` 0.96 from the Week 8 Wednesday run; (b) approve building the trailing games-played multiplier and the dispersion/TE refit as the next two backtested changes.

Single next move: reply yes or no on the `qb_share` 0.96 amendment; it is the only change in this document with a complete multi-season backtest behind it.

## Appendix: tools added with this post mortem

`component_audit.py` (market-by-market bias, dispersion, rank skill vs naive), `board_grade.py` (priced markdown board vs actuals), `qb_rating_lab.py` (QB and rest margin adjustment vs line), `eval_qb.py` (QB-market candidate vs baseline), `APEX_QB_SHARE`/`APEX_QB_TD` env knobs in `sim.py` (defaults unchanged). Frozen runs were not modified.
