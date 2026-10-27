# Week 7 Tuesday grade (all 14 games final, nflverse box scores)

Tools: `postmortem.py 2026 7`, `pick_grade.py 2026 7 --sims <MNF sims>=DAL@PHI`, `game_grade.py 2026 4 5 6 7`. The postmortem wrote grade files into the frozen runs; they were moved out and the runs left untouched. Sunday window sims were not kept, so Sunday single-line grading stands on `POSTMORTEM_2026_W07_SUNDAY.md`; this file adds the game-level grade and Monday night.

## 1. Game level: model-only against the LINE row (`GAME_GRADE_2026_W07.md`)
| Weeks 4-7 (58 games) | winner | margin MAE | total MAE | team-pts RMSE |
|---|---|---|---|---|
| model-only | 58.6% | 8.99 | 10.80 | 8.50 |
| market-anchored | 63.8% | 8.60 | 10.16 | 8.07 |
| line | 61.0% | 8.59 | 10.14 | 8.04 |

Week 7 alone (14 games): model-only 57.1% / margin 11.52 / total 10.49 against the line 71.4% / 10.07 / 10.43. Model-only is still behind the line on margin in three of four weeks (ahead only in week 4) and level on totals this week. It has not reached the DECISIONS #48 target.

Where model-only disagreed with the line on the winner: 12 games over weeks 4-7, model right in 5. In week 7 it disagreed twice and was wrong both times: CIN@BAL (model BAL by 2.7, line CIN by 3, CIN won 35-13) and DAL@PHI (model PHI by 0.6, line DAL by 4.5, DAL won 38-21). Games where the model sat 3+ points from the line: 20, and it was closer to the final margin in 9 (45%). Disagreeing with the line has not paid.

## 2. Monday night, DAL@PHI (DAL 38, PHI 21)
Board of 56 gradable lines (53 PASS, 3 PLAY) in `MNF_FULL_RUN_2026_W07.md`:
- PLAY 1 of 3: Goedert rec U5.5 hit (5); Prescott pass attempts O35.5 missed (27, DAL led and ran 25 times for Williams); Lemon rec yds U38.5 missed (67 on 7 catches, 1 TD). Prescott pass TD U1.5 (extra) missed (3 TDs).
- By confidence: 0.6+ hit 67% (n=9), 0.55-0.60 hit 50% (n=12), 0.50-0.55 hit 47% (n=15). Rank order held, sample is small.
- Anytime TD board (13 players): predicted 3.3 TDs, actual 6; log loss 0.648 against 0.690 for a flat rate. Lamb (2 TDs) was priced at 35-37%.
- Single-line screen (40 lines, pick_grade): 50% hit against 57.7% expected, PLAY 0 of 5 on that screen's labels.
- Game: the model-only track had PHI by 0.6 and 47.0 points; final DAL by 17 and 59 points. Both tracks missed the total.

## 3. The Barkley / Pierce check
| | model | book | actual |
|---|---|---|---|
| Barkley carries / yds | 6.8 / 34 | 15.5 / 63.5 | 7 / 62, 1 TD |
| Pierce carries / yds | 11.3 / 44 | n/a / 18.5 | 14 / 47, 1 TD |

The allocation I called a returning-back artifact was right on carries for both backs; the books were wrong on Barkley's volume (15.5 against 7) and low on Pierce's yards. Barkley's 62 yards on 7 carries was efficiency, which neither the model nor the books had. Elijah Mitchell took 3 carries that the model did not project (and Ertz, projected active, logged no snap). One game does not prove the model's returning-player allocation is good, but it removes the evidence that it is an artifact; the work-queue item "returning-player prior" is downgraded until more cases accumulate. Passing: Prescott 27 attempts / 212 yds against 33.8 / 258 projected (game script), McKee 35 / 211 against 209 projected.

## 4. Open items
Calibration ledger append for MNF, the QB share / pass-yards backtest, and the PHI-backfield question above stay on the work queue. No model or calibration change is made here.
