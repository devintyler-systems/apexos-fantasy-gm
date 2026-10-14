# Week 5 post mortem (2026-10-08 Thursday to 2026-10-12 Monday)

Scope: all 15 games, final in nflverse (TB@DAL, PHI@JAX, 11 Sunday games, BAL@ATL, BUF@LA). Per game, the latest frozen run made before kickoff: Thursday base `2026_w05_*_20261008T2302*` (TB@DAL), Sunday 06:58Z (PHI@JAX, started 13:30Z, graded against it), refresh B 16:19Z (every other Sunday game, ESPN Outs applied, 4 PM and SNF inactives not yet posted), refresh C 23:40Z (BUF@LA, with DJ Moore from the DK file). Market-anchored track unless stated. Reproduce the tables with `python engine/weekly/postmortem.py 2026 5`; bet grading used the published documents and stale Thursday reference prices, so ROI is diagnostic only.
Caveats: one week, 15 games, 30 team-games. Anything under about 100 observations is a direction, not a result.

## 1. Headline

The engine did what it was built to do (availability, volume, touchdown rates, yardage level) and the model still has no measurable edge over the market. The honest summary:

1. **Games: no edge.** Market-anchored team-points RMSE 8.54 vs 8.49 for the DraftKings line it is anchored to; model-only 8.76. Winners 9 of 15 for all three. The model-only track adds no information about games.
2. **Props: the books were better than the model on every count and yardage market.** 397 resolved main-line over/under props: log loss model 0.7127, books 0.6897, 50/50 blend 0.6898. The model only helps as a shrinkage partner, never alone.
3. **Players: better than an average, by a little.** Receiving yards MAE 22.3 vs 23.1 for a player's own weeks 1-4 average, receptions 1.51 vs 1.62, passing yards 66.6 vs 71.5 (but passing yards correlation is 0.10: single-game QB passing is mostly noise).
4. **Touchdowns held up.** Anytime TD log loss 0.4245 (n=256), against 0.4422 last week and 0.4373 in the backtest; probabilities summed to 53.9 vs 55 scorers.
5. **Our own output had three defects** (section 3.8): a wrong statement that the model has no QB carries, twelve parlays that shared one losing leg, and every price in every document was 66 to 97 hours old.

## 2. What held up

| Check | Result |
|---|---|
| Availability | p_active in [0.90, 0.99): 49 of 49 played. [0.5, 0.9): 88% played (projected 68%). Players projected out who played: 0. Projected active with real usage who logged no snap: 2 (Gainwell TB, Shepard NYJ). Real usage not in the projection universe: 5 (Keenum CHI relief, Pierce PHI 11 carries, Patrick, Strong, Virgil). |
| DK points (players with projection >= 8, n=140) | projected 13.45, actual 13.51, MAE 6.49, correlation 0.51 |
| Anytime TD (n=256) | log loss 0.4245; sum of probabilities 53.9 vs 55 scorers |
| Level biases | receiving yds +3.0, receptions +0.2, pass yds -4.6, team pass yds +4.8 (all small) |
| Team volume level | pass attempts 32.6 vs 33.8, rush attempts 26.75 vs 26.77, pass TD 1.47 vs 1.50 |
| Freeze process | every run verified intact; DK vs NFL conflict (Moore) found and flagged before kickoff |
| Probability labels | no pick was labeled confident or an edge; 85% cap respected |

## 3. What failed and what we learned

### 3.1 Games
| | Team RMSE | Margin MAE | Total MAE | Winners |
|---|---|---|---|---|
| DraftKings line | 8.49 | 10.40 | 10.17 | 9/15 |
| Market-anchored | 8.54 | 10.44 | 10.25 | 9/15 |
| Model-only | 8.76 | 10.65 | 10.40 | 9/15 |

Actual average total 48.4 against a 44.8 line (+3.6, about 1 standard error of 15 games), so team bias of -1.9 is not a finding. The largest misses were results, not inputs: TB@DAL (DAL -9.5, TB won by 8), HOU@TEN (-23), DET@ARI (-24), CHI@GB (GB won by 24 as a 1.5-point underdog). Margin MAE of about 10.4 is within the usual NFL spread error of 10 to 11 points. Nothing to fix; stop expecting the model-only track to beat the line.

### 3.2 Props against the naive baseline and the books
| Market | n | MAE model | MAE naive avg | MAE 50/50 | Corr model / naive |
|---|---|---|---|---|---|
| Receiving yards | 182 | 22.26 | 23.05 | 22.46 | 0.53 / 0.49 |
| Receptions | 182 | 1.51 | 1.62 | 1.53 | 0.57 / 0.52 |
| Rush yards (RB/WR) | 49 | 24.98 | 24.20 | 23.89 | 0.66 / 0.60 |
| Pass yards | 29 | 66.6 | 71.5 | 65.5 | 0.10 / 0.24 |
| Pass completions | 29 | 4.68 | 5.45 | 4.75 | 0.23 / 0.22 |

Rush yards were over-projected by 4.6 per player (the 30 to 50 yard tier projected 35.9, actual 26.3). Against the books on resolved main lines (Thursday prices, 13 games): log loss by market, model vs books: pass attempts 0.731 vs 0.693, pass completions 0.766 vs 0.702, pass yards 0.770 vs 0.694, receptions 0.684 vs 0.681, receiving yards 0.695 vs 0.692, rush attempts 0.747 vs 0.690, rush yards 0.722 vs 0.692. The model's average over-probability was 0.478 vs 0.499 for books (overs hit 47.4%). The model's passing-count probabilities run 5 to 14 points below the books (pass attempts 0.357 vs 0.498 average over-probability), which the bias-centered gap removes but cannot fix.

### 3.3 Quarterbacks
- **Passing yards are not predictable from our inputs at one game.** Correlation 0.10 (naive 0.24), MAE 66.6. The largest misses are game-script blowouts: Shough NO 96 vs 252 projected, Bagent CHI 87 vs 219 (replaced by Keenum, who threw 19 passes for 108), Nix 123 vs 228, Herbert 121 vs 198, against Maye 374 vs 203, Lawrence 331 vs 203, Love 367 vs 239. Both tails are script, so they are what #11 measured: team pass attempts have actual sd 8.4 and no week-to-week predictability (correlation with the model 0.07, with the naive team average 0.11).
- **QB rushing was in the simulation but not in the published table** (DECISIONS #20). 30 QBs rushed for 671 yards (22.4 each) and 8 TDs; the sim had 14.6 yards and 3.3 TDs. Allen ran 10 times for 121 yards and a TD, Jayden Daniels 9 for 103 and 2, Willis 74, Murray 51. Historically (742 QB-games, 2023-25) yards are 8% under-projected and **rush TDs 27% under-projected in every season** (0.116 vs 0.158), which is what candidate v2 fixes (#19). The DK-points QB bias of -2.9 in the frozen runs was mostly the missing table columns (sim QB rushing is worth about 2.1 DK points per QB).

### 3.4 Touchdowns
- Calibrated in total and by bin on the historical sample (6,668 player-games: bins 0.04/0.07/0.10/0.15/0.21/0.29/0.41/0.58 vs actual 0.053/0.073/0.099/0.156/0.247/0.295/0.423/0.502).
- **Position bias, stable across seasons:** TE 13% low, WR 11% low, RB 8% high, QB rushing 27% low. This week's players the model priced well below the books (share ratio under 0.8: model 0.067, books 0.122, actual 0.147, n=95) show the same direction at the low end. Candidate v2 corrects all four in the backtest (#19).
- Our TD longshot rule (model share at least 1.2 times the books' share, price +120 or longer) hit at the modeled rate but lost at reference prices: this week 48 players, model 0.232, books 0.185, actual 0.167. The vig-neutral share ratio ranks players; it does not measure an edge.
- Of 15 first-TD longshots only CHI@GB Watson (+1300) hit, and the MNF first TD (Adams) was not on our list.

### 3.5 Availability and role
The availability model is the strongest part of the engine this week. What it cannot see is in-game role and designation effects: Lamb (thigh designation) played 34 of 60 snaps and caught 2 for 9, Mumpfield played 6 snaps, Goodson 3, Ty Johnson 14, Kaleb Johnson 9. The existing 0.93 haircut for Questionable players matches the 2023-25 relationship (actual/projected receptions 0.982 for Q/D players who played vs 1.064 for healthy players, a ratio of 0.92); Week 5's 0.77 on 11 players is noise. No change.

### 3.6 Our published bets (143 priced; stale reference prices, flat 1 unit)
| Category | Bets | Hit | Units | Expected hit rate |
|---|---|---|---|---|
| Props | 61 | 37 (60.7%) | +8.97 | 57.6% (blend) |
| Anytime TD shots | 25 | 7 (28.0%) | -6.74 | 27.7% |
| First TD longshots | 15 | 1 | -1.00 | 6.5% |
| Parlays | 42 | 8 (19.0%) | -8.94 | 22.6% (joint) |
| Singles only | 101 | 45 (44.6%) | +1.23 | 43.8% |

- Props that passed all gates: 30 of 47 (63.8%); leans and log-only picks: 7 of 14 (50.0%). Unders 17 of 26, overs 20 of 35. Rush-yard unders 8 of 11 under the 50/50-blend rule, the one place the model was allowed an opinion (small n).
- By window: 4 PM +27.9 units (20 of 26), every other window -35.6 combined. The 4 PM result is one window of luck on top of a sound process; do not read it as edge.
- All 12 mixed-window parlays contained London U5.5 receptions (he had 7). One missed leg erased twelve tickets (section 3.8).
- Calibration of the model's own stated probabilities was fair (props 57.6% expected vs 60.7%, TDs 27.7% vs 28.0%). The model is not mis-stating confidence; it is just not beating prices.
- **Declined picks:** Allen under 244.5 pass yards, 32.5 attempts and 20.5 completions all cashed; Allen under 36.5 rush yards (121) and the Allen anytime TD fade both lost. The rule that a 30-point model-vs-book gap is a role difference and not an edge saved us the two losers and cost us the three winners; it stays.
- Hindsight check: Gibbs anytime TD at -450 (published as a fair price, not a play) hit with 2 TDs.

### 3.7 DFS Showdown (ceiling entries, exploratory, no contest results available)
| Lineup | Actual points | Holdout mean / P99 / P(150+) |
|---|---|---|
| TB@DAL ceiling entry (Lamb CPT) | 60.35 | 89.8 / 156.9 / 1.9% |
| TB@DAL alternate (Prescott CPT, Pickens in) | 84.86 | not given |
| BUF@LA ceiling lineup (Stafford CPT) | 140.38 | 99.5 / 178.6 / 5.5% |
| BUF@LA alternate A (Mumpfield for Ty Johnson) | 129.18 | not given |
| BUF@LA alternate B (Bass for Parkinson) | 152.08 | not given |

The Monday lineup beat its mean by 41 points (Stafford 3 TDs and 383 yards, Nacua 17-138-1, Adams 2 TDs); the Thursday lineup missed its mean by 30 because Lamb, the captain, caught 2 passes. Contest finish, field scores and ownership are not verifiable here (no contest results, no committed salary files). Lesson: the search is mean-and-tail correct inside the model but it has no ownership or injury-designation input, and a captain with a designation (Lamb) or a role-uncertain flex (Mumpfield) is its largest single risk.

### 3.8 Mistakes in our own output
1. **"The model has no QB carries" (Monday document) was wrong.** The sim has QB rushing; the published table dropped it (#20). The advice not to bet Allen's rushing props was right; the reason given was not.
2. **Parlay concentration.** The mixed section reused London U5.5 receptions in every ticket. A leg now appears in at most two published parlays (`sunday_bets.py` `cap_exposure`).
3. **Stale prices throughout.** Every price came from the Thursday workbooks (66 to 97 hours old at use). We labeled them reference and published break-even prices, which was right, but a break-even is only useful next to a live price, and none was available to compare.
4. **Sunday refresh B was frozen after PHI@JAX kicked off**, labeled post-hoc as required; PHI@JAX was graded against the 06:58Z run instead.
5. **The Thursday first-TD "agreement" claim was retracted earlier** (flat 10% haircut gives about 1.2 total probability per game vs a real 14-44% overround); nothing in this week's work reused it.

## 4. What we are not changing (evidence)
- **Team volume dispersion (#11):** Week 5 team pass attempts: sd 8.4, model correlation 0.07, naive team average 0.11; rush attempts: sd 6.65, model 0.18, naive 0.09. The signal is near zero for everyone, so widening the simulated spread would improve interval coverage but not mean accuracy. #11 stands.
- **Questionable/Doubtful haircut:** historical ratio 0.92 already matches 0.93.
- **Anytime-TD calibration curve:** a logit recalibration gave no held-out gain (0.4266 to 0.4282, 0.4749 to 0.4737, 0.4610 to 0.4606).
- **Team points and the market-anchored track:** unbiased within noise; keep.

## 5. Shipped in this change
| Change | Risk | Evidence |
|---|---|---|
| QB rushing published (table, QB sheet, `qb_rush_yds` grading, `dk_points` and `qb_rush_td` sections) | none, additive | #20 |
| `espn_inactives.py`: ESPN Outs to `manual_out.csv`, DK vs NFL conflicts file | none (operator step) | W4 postmortem P0 #1; used by hand twice this week |
| `postmortem.py`: Tuesday tables in one command | none | reproduces every number above |
| Parlay exposure cap in `sunday_bets.py` | none | section 3.8 |
| TD allocation knob `config/weekly/td_params.json` (empty, baseline) plus candidate v2 file | none until adopted | #19 |
| Live runs use the newest full roster for the IR/released and stale-team rules (found by the integration test on the first Week 6 run) | removes a Tuesday-run hole | #23 |
| Tests: ESPN parser, run selection, grade fields | none | `pytest tests/weekly` |

## 6. Proposed next (priority order)
1. **Decide candidate v2 (TD allocation).** It improves TD log loss in all three held-out seasons (0.4558 to 0.4546 matched) and calibrates QB rushing TDs (0.115 to 0.152 vs 0.155) while tying every promotion metric; it fails only because the rule says "beats" on receptions MAE, which TD weights cannot move (1.53343 vs 1.53345). Recommended: adopt, and amend the rule to "no worse than 0.001".
2. **Live odds at T-90 for every window, with both sides of anytime TD.** All Week 5 pricing was 66-97 hours stale, and the feed carries only the "Yes" side of anytime TD, so de-vig is a flat 10% guess (real overround 14 to 44%). Needs an operator-supplied feed or API key (never committed); the converter and pricer already exist.
3. **QB-identity propagation** (Huntley, Bagent, Keenum): receivers and the pass-volume of a backup QB should follow the QB, not the team. Backtest with the 27 slates and `eval_variants.py`.
4. **Role and designation inputs.** Practice participation by day (Wed/Thu/Fri) and snap/route share trend (`snap_counts`, `ftn_charting` are cached, unused) to cut role surprises like Lamb and Mumpfield. Candidate feature: expected snap share by designation, fit on 2023-25.
5. **Kicker and defense for Showdown/Classic.** Kickers use a league-average points-per-FG constant and defenses a points-allowed ladder; field-goal distance and sack/turnover environment need their own model. Candidate: `pbp`-derived FG distance distribution by team.
6. **GPP construction inputs:** ownership (Draft % after lock, proxied by salary and consensus), contest results and field scores, and the Classic salary file for the main slate (none supplied this week). Without them the Showdown and Classic searches optimize against the model only.
7. **CLV tracking:** record the price taken and the closing price for every published bet so that "edge" can be measured against the closing line instead of results.

Next Tuesday: `python engine/weekly/postmortem.py 2026 6`, then grade the frozen runs with the grader agent.

## 7. Method notes
- Frozen runs were not modified. Graded: `grade.py` per run (`grade.json`, `grade_players.csv` written beside each run), the 20,000-sim and 5,000-sim backtests are in `var/out` (not committed) with tags `w5base`, `v1_qbrtd`, `v2_qbrtd_pos`, `base20k`, `v2_20k`.
- Book comparison: `price_odds.py` outputs for BUF@LA and the 13 Sunday games (model_p from the refresh-B or refresh-C sims, stale Thursday prices with `APEX_ODDS_KEEP_STALE=1`), joined to week 5 stats with pushes removed; TB@DAL and PHI@JAX excluded because their prices were pulled before they were priced.
- Bet grading: first-TD results from play-by-play ordered by game seconds remaining; anytime TD counts rushing and receiving only.
- Backtest harness: `bt_vol.sh`-style runs of `backtest_run.py` for 2023-25 weeks 4-12, model track; 2023 needs the 2022 nflverse files.
