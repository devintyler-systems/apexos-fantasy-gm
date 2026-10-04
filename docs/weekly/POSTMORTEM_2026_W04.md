# Week 4 post mortem (2026-10-04 Sunday slate)

Scope: 13 completed forward games (IND@WAS, NE@BUF, NYJ@CHI, JAX@CIN, ARI@NYG, LA@PHI, GB@TB, TEN@BAL, DAL@HOU, MIA@MIN, KC@LV, DEN@SF, LAC@SEA).
Excluded: PIT@CLE (already final when first frozen, not a forward projection), DET@CAR and ATL@NO (not played when this was written; rerun after they finish).
Projections graded: frozen runs `2026_w04_*_20261004T155901Z` (refresh B, market and model tracks) and the Saturday freeze for comparison.
Actuals: ESPN box scores. DraftKings points computed from them match the DK contest screen exactly for 12 players and 2 DSTs checked.
Caveats: one slate, 13 games, so team-level statistics are noisy. IND@WAS was graded against refresh B, which was frozen after that game started (it used no week 4 stats and the same inactives as pre-kickoff refresh A).

## 1. Headline

The aggregates were right and the individual outcomes were not. Team points, DraftKings points, touchdown rates and yardage totals were all unbiased, but player-level error was far above our historical level, and the optimizer chose the players most likely to have been over-projected. Three root causes, in order of how much they explain:

1. **Team volume is simulated too tightly.** Pass attempts have a simulated standard deviation of 4.7; real team-games vary by about 6.9 around a team's own average (2023-25). Every player on a team moves with that volume, so we under-priced correlated blow-ups and busts.
2. **The optimizer's curse.** Players the lineups picked were over-projected by 1.5 DK points each (about 10%); players not picked were under-projected by 0.3. The model barely beats salary as a predictor, so a "value" edge over price is mostly noise.
3. **The model's prop "edges" against the market were not real today.** On 868 resolved priced props the market was better calibrated than the model.

## 2. What held up

| Check | Result |
|---|---|
| Team points (market-anchored) | projected 22.5, actual 22.5; RMSE 6.25; total bias -0.1; winners 9/13 (model-only track 10/13) |
| DK points per player (n=114, mean >= 8) | projected 13.32, actual 13.31 |
| Anytime TD (n=232) | sum of probabilities 46.6, actual 45; log loss 0.4422 (backtest 0.4373 market, 0.4427 model) |
| Yardage biases | rec yds +1.2, rec 0.0, rush yds +2.6, pass yds -2.3 (all small) |
| Pass TDs vs market | model log loss 0.647 vs market 0.673 (n=52), the one prop market where the model beat the market |
| Freeze process | QB depth-chart fix and roster/inactive overrides moved the grade slightly in the right direction (rec yds MAE 25.16 to 24.98); no leakage; every run verified intact |

## 3. What failed

### 3.1 Player-level error was unusually large
- Receiving yards MAE 24.98 (n=156). Across the 27 backtest slates (2023-25, weeks 4-12) the mean is 20.40 with sd 1.38, so today is z = +3.3 and worse than every one of them. Receptions MAE 1.82 vs 1.53 (sd 0.08).
- Interval coverage (P25-P75): receiving yards 45%, rushing yards 52%, passing yards 38% (n=26). DK-point tails: 13% of players below their P10 and 12% above P90 (ideal 10/10); 29% below P25 and 27% above P75 (ideal 25/25). Mildly narrow.

### 3.2 Team volume dispersion (the structural finding)
| Quantity | Simulated sd | Observed |
|---|---|---|
| Team pass attempts | 4.7 | 8.7 today; 6.9 team-game sd in 2023-25 weeks 4-12 |
| Team rush attempts | 4.5 | 6.3 today; 6.5 historically |
| Team points | 9.9 | 6.4 today (13 games); about 9 historically, so not a problem |

9 of 26 team-games landed outside the P5-P95 range on pass attempts (ideal: 2.6).
Low: NYJ 15 attempts (projected 28.9), MIA 17 (27.4), SEA 22 (31.4). High: CIN 54 (36.1), LV 52 (30.9), LA 51 (36.9), DAL 45 (35.7), DEN 42 (29.3), MIN 37 (23.7).
Team points were fine, so the issue is how a given scoreline is split between passing and rushing volume, not game totals. Pass volume tails drive the correlated outcomes that decide GPPs.

### 3.3 Our DraftKings lineup (rank 92,013 of 161,764; 112.56 points; winner 234.20)
Projected 161.5; actual 112.56 (-49.0). The model put 3.1% probability on a score this low.

| Player | Projected | Actual | Diff | Draft % | Team pass att (proj / actual) |
|---|---|---|---|---|---|
| G. Wilson | 24.3 | 5.7 | -18.6 | 12.6 | NYJ 28.9 / 15 |
| J. Smith-Njigba | 25.3 | 12.6 | -12.7 | 20.3 | SEA 31.4 / 22 |
| D. Wicks | 14.7 | 4.8 | -9.9 | 20.2 | PHI 30.6 / 27 |
| G. Smith | 17.9 | 8.8 | -9.1 | 2.8 | NYJ 28.9 / 15 |
| C. McCaffrey | 22.9 | 16.0 | -6.9 | 28.1 | SF 26.8 / 30 |
| M. Washington | 14.8 | 12.0 | -2.8 | 4.4 | MIA 27.4 / 17 |
| A. Jones | 18.6 | 16.8 | -1.8 | 26.7 | MIN 23.7 / 37 |
| Packers DST | 9.7 | 8.0 | -1.7 | 7.2 | |
| T. Hockenson | 13.4 | 27.9 | +14.5 | 15.9 | MIN 23.7 / 37 |

- Most of the shortfall is team volume: NYJ passed 15 times (Geno + Wilson: -27.7 combined), SEA 22 (JSN: -12.7). Hockenson's +14.5 came from MIN passing 37 times.
- Wilson's projection implied a 40% share of NYJ targets (13.45 of about 33.8) because Hall, Mitchell and Taylor were out. Historically a team's top target-getter averages 29.6% and exceeds 40% in only 7.6% of team-games; his own 2026 games were 30%, 19% and 36%, and he got 4 of 15 (27%) today. A 40% **mean** share is not supportable.
- All 25 lineups we built: average projected 147.3, average actual 118.7. Across the 25 lineups, projected and actual correlated at -0.49 (top-10 projected averaged 111.2 actual; bottom-10 averaged 132.2). The lineups overlap heavily so this is anecdotal, but it points at the optimizer's curse (3.4).
- The best actual among our 25 was 160.5, from a lineup projected at 140.2.

### 3.4 Optimizer's curse (DFS pool, n=280 non-DST active players)
| Group | n | Projected | Actual | Error |
|---|---|---|---|---|
| In our lineups | 53 | 15.29 | 13.77 | -1.51 |
| Not in our lineups | 227 | 5.17 | 5.48 | +0.31 |

Correlation with actual DK points: model 0.67, DK season average 0.62, salary alone 0.61. MAE: model 4.27, season average 4.58. The model adds only a little over price.

### 3.5 Winning lineup and ownership
Winner 234.20: Prescott, J. Williams (DAL), K. Williams (LA), Lamb, Collins, Flowers, Ertz, Hockenson, Jaguars DST.
- Model mean for that lineup 120.3; its P99 187.1. The real score was above all 20,000 simulations.
- Four pieces came from DAL@HOU (Prescott 21.1, J. Williams 31.3, Lamb 44.3, Collins 33.8 = 130.5 vs a model mean of 63.7), a game that finished 64 points against a model mean of 48.6. DAL threw 45 times.
- Ownership: winner's average 7.1% (1.1% Ertz, 1.5% J. Williams, 1.7% Jaguars, 5.2% Prescott). Ours averaged 15.4%, with four of nine players at 20% or more (McCaffrey 28.1, Jones 26.7, JSN 20.3, Wicks 20.2). We were chalky, and the one contrarian piece (Geno, 2.8%) busted.

### 3.6 Props and parlays
- All 868 resolved priced props: log loss market 0.6154, model raw 0.6415, model bias-centered 0.6398, 50/50 blend 0.6223. Brier 0.2162 / 0.2280 / 0.2272 / 0.2196.
- By market the model beat the market only on pass TDs (n=52); a blend slightly beat the market on rush yards (0.683 vs 0.693, n=116). It lost on receptions, receiving yards, passing yards and anytime TD.
- Flagged edges did not exist: edges >= 5 points (n=240): model 56.9%, market 45.3%, actual 44.2%. Edges >= 10 points (n=116): model 65.4%, market 49.1%, actual 47.4%. Edge bucket above 15 points (n=59): model 69.9%, market 49.7%, actual 45.8%.
- Prices were a 64-hour-old snapshot, which should have helped the model (it knew about later outs), not hurt it.
- Our recommended straight bets: 13-10 (one void: Dulcich had no stat line). Props excluding anytime TD: 9-10. Anytime TDs: 4-0 (probabilities 63-72%; luck, not evidence of an edge). Parlays: 2 of 8 won or would have (the anytime-TD triple; the MIA same-game parlay would pay as a single leg after Dulcich's void).
- The "Top 10 afternoon" list went 4-5 plus one void.

### 3.7 Availability
- Seven players projected with a real role had no box-score line: Dulcich (MIA, 7.6 projected targets), Rice (KC, hamstring, listed Questionable during the game), Nailor (LV, concussion, in-game), Ruckert, Wayne, Bourne, Franklin. For several (Dulcich, Allen, Wayne, Bourne, Ruckert, Franklin) we cannot tell inactive from zero touches without snap counts.
- ESPN's game-summary list gave pre-kickoff inactives for the 1 PM games (posted about 15:30-15:55 UTC) but we ran it only twice, and the 4:05 and 4:25 PM windows were not refreshed after their lists posted.
- Positive: Zay Flowers (modeled 67% to play) played and scored 28.8; the Questionable discount is conservative.

## 4. What we are not changing
- The share-concentration-when-teammates-are-out effect is real but small historically: top-receiver bias goes from -6%/-8% (rec/yds) with no skill players out to +2%/+5% with two out (n=67 top-1 player-weeks), not a large systematic overshoot. Wilson's 40% share is the extreme case, handled by a cap (5.3), not by a model rewrite.
- Team totals and points are calibrated; do not touch the scoring model.
- Anytime-TD probabilities are calibrated; keep.
- Backtest bias by projected rank within a team is slightly **negative** historically (-4% to -10%), so a blanket star shrink would hurt.

## 5. Proposed changes (priority order)

### P0: process (no model risk)
1. **Automate official inactives ingest.** Pull ESPN game-summary injuries at T-90 for every window (1 PM, 4:05, 4:25, SNF, MNF), write `manual_out_*.csv` with a timestamp, rerun affected games, and freeze again. Add a "no stat line" list to grading that flags DNP vs zero.
2. **Stop publishing model-vs-market "edges" and "very confident" parlays.** Until a model variant beats the market out of sample, show the model as a projection and use market lines as the price. Use the model only where it beat the market (pass TDs; rush yards blended). Require market confirmation before any pick is labelled confident.
3. **Grade automatically with an ESPN fallback** when nflverse lags (at 23:46 UTC it was still missing the four late games, 8 teams).

### P1: simulation structure (needs a 2023-25 backtest before promotion)
4. **Widen team pass and rush attempt dispersion** to match nflverse 2023-25 (pass-attempt sd about 6.9, rush about 6.5) and refit the game-script link. Expected effects: wider player tails, higher teammate correlation, better interval coverage; mean accuracy should be unchanged. Promotion test: week 4-12 backtests of 2023-25 with coverage, MAE, TD log loss and DK-point PIT calibration.
5. **Cap effective target share.** Cap a player's mean redistributed share near 33% (single-game share p95 is 0.30; top-getter p90 is 0.385) and spread vacated targets across RB/TE/depth WRs. Validate against the same backtest conditioned on outs.

### P2: DFS construction
6. **Shrink before optimizing.** Pull each player's mean toward a price-and-consensus anchor (DK average, DFF projection) in proportion to the gap and the player's sim uncertainty, then optimize. Evidence: selected players -1.5 each; model-vs-salary correlation 0.67 vs 0.61.
7. **Add ownership and leverage.** We only saw Draft % on the post-lock contest screens. Record it for every contest we enter (we now have 18 players) and build a proxy from salary rank, DFF value and projection rank; add a leverage term so GPP lineups avoid four players at 20%+ ownership.
8. **Optimize for tail, not mean.** GPP lineups should maximize P(score >= a top-0.1% threshold) with the corrected team-volume correlation, and allow 3-4-player game stacks from a single high-total game with a low-owned bring-back. Keep cash lineups on mean (shrunk).

### P3: reporting
9. Label confidence as a reliability index in every output, never as a hit probability; show the market no-vig number beside every model probability.

## 6. Method notes
- Nothing here changes a frozen run. The postmortem scripts read frozen projections and external box scores only; they are scratch analysis and are not part of the pipeline yet.
- Team volume simulated sd comes from rerunning the frozen configuration for the 13 games (market track, same seed); DK-point PIT uses the same simulations.
- Historical comparisons use the 27 saved backtest slates (2023-25, weeks 4-12) and nflverse `stats_team_week` and `stats_player_week`.
