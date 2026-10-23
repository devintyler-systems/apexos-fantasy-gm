# Thursday scorecard: NE @ CHI, Week 7 2026 (final CHI 30, NE 24)

Graded with `engine/weekly/pick_grade.py` against nflverse (week 7 box scores, final) using the sims behind `TNF_NE_CHI_2026_W07.md` (frozen runs `2026_w07_*_20261022T2249*`). Prices are the best of six books in the 23:43Z prop sheet, 1 unit flat per line; no touchdown prices exist, so touchdown legs are graded on probability only. One game: every group below is a direction, not a result.

## The answer

The published list went **11 of 22 (50%)** against 58.8% expected, **+0.43 units** on the 18 lines with a price (line shopping across six books carries it). Three findings matter more than the record:

1. **Pulling the pass-volume unders was right: they went 1 of 6.** Maye 321 yards and 24 completions (our line 20.5), Williams 308 yards and 33 attempts. Both quarterbacks threw for 2 touchdowns; the six-book price on Williams over 1.5 (-150 to -167, about 59%) beat our 36%.
2. **Gating the CHI running-back lines was wrong: all four would have won, +3.33 units.** Swift over 14.5 carries (22), Swift over 62.5 yards (78), Roschon Johnson under 7.5 carries (2) and under 27.5 yards (13). I pulled them because our Johnson number (4.3 carries) disagreed with the books (6.5 to 7.5) and Rotowire (33.7 yards). Johnson got 2 carries and 13 yards: our projection was closer than both. The gate came from reading model-versus-market disagreement as model error. This is four correlated bets in one game script (CHI ran 30 times, NE trailed in carries), so it is not proof the model is right on promoted backs, but it removes the evidence for the gate. The gate stays for Week 8 only if the promotion-shrinkage backtest says so; it is not justified by this game.
3. **Receiving props were fine this week: PLAY receiving 7 of 11 (63.6%, +1.76 units); the suppressed LEAN receiving lines went 6 of 11.** One week against W6's 35%; the W6 finding stands as a rule only with more weeks.

## Groups

| Group | Lines | Hit | Units at best price | Expected (shrunk) |
|---|---|---|---|---|
| Published (22: 19 PLAY, 3 LEAN) | 22 | 11 (50%) | +0.43 (18 priced) | 58.8% |
| Rush PLAY/LEAN kept (Maye rush attempts and yards unders won; Stevenson yards under won; Henderson attempts and yards overs lost) | 5 | 3 (60%) | -0.26 (4 priced) | |
| Receiving PLAY, thin | 11 | 7 (63.6%) | +1.76 | 58.9% |
| Pass-volume unders (pulled) | 6 | 1 (16.7%) | -1.07 (3 priced) | |
| CHI RB rush lines (gated out) | 4 | 4 (100%) | +3.33 | |
| Suppressed receiving LEAN | 11 | 6 (54.5%) | | |

Misses worth a line each: Henderson (3 carries, 9 yards; projection 7.8 and 35) because NE threw 31 and ran 17 times; Loveland (7 catches, 69 yards on 12 targets) and Raridon (56 yards) beat the thin receiving unders.

## Game and team level

| | Model market-anchored | Model-only | Market | Actual |
|---|---|---|---|---|
| CHI / NE points | 26.7 / 23.7 | 23.6 / 23.0 | CHI -3.0, total 50.5 | 30 / 24 |
| Winner | CHI 58% (correct) | NE 46% (wrong) | | CHI by 6 |

Total 54 vs 50.5 (market-anchored 50.4, model-only 46.6). Team pass attempts NE 31 / CHI 33 vs 29.1 / 30.7 projected; passing yards 321 / 308 vs 238 / 238; rush attempts NE 17 / CHI 30 vs 27.6 / 31.3; rush yards 70 / 116 vs 126 / 142. Both offenses were far more pass-efficient (10.4 and 9.3 yards per attempt) than the 8.3 and 7.5 projected.

## Touchdowns

Swift anytime TD (65.3%) scored. Of 15 players on the board, 6 scored against 3.8 predicted (Swift, Stevenson, Burden, Loveland, Raridon, Maye on a rushing TD); the 0.10 to 0.20 bin scored 2 of 6. Passing-TD ladder: Williams 2 (our 2+ 36%) and Maye 2 (our 2+ 53%) both hit; sum of 1+ probabilities 1.6 vs 2 actual, 2+ 0.9 vs 2.

## Model vs the Rotowire (Sleeper) benchmark, the 16 to 17 NE/CHI skill players it covers

| | Ours | Rotowire | Actual mean |
|---|---|---|---|
| Receiving yards MAE (n=16) | 24.6 | 25.0 | 39.3 |
| Receptions MAE (n=15) | 1.56 | 1.55 | 3.1 |
| Rush yards MAE (n=5) | 12.1 | 17.3 | 27.0 |
| Rush attempts MAE (n=5) | 3.4 | 4.5 | 7.4 |
| Skill TDs, 17 players (5 scored) | 4.7 expected | 5.0 expected | |
| QB passing yards | 220, 222 | 282, 234 | 321, 308 |

Both under-project receiving volume this game (actual mean 39.3 yards vs 28 and 33). Rotowire was closer on Maye's passing yards (282 vs our 220); we were closer on every rushing line. n is 5 to 17 per row.

## What this changes

- Pass-volume and passing-yardage unders stay off the list: 1 of 6 here, and W6's -10.5 passing-yards bias, now two weeks of evidence for a league-level correction (DECISIONS #41, week 8 backtest).
- The RB-out gate is not supported by this game; its only justification (Johnson at 4.3 carries against 7 for the books) was the model being right. Decision for Week 8: rebuild it as a backtest, not a publishing rule (DECISIONS #43).
- The Williams touchdown disagreement resolved in the books' favour: the engine's QB 2+ passing-TD probability for a team at a 27-point implied total looks low (36% for 27 points). Check the QB passing-TD ladder across W4 to W7 before Sunday.
