# Post mortem: GB @ LA, Week 12 (Wed 2026-11-25), projections and DK Showdown

**Final:** LA 26, GB 13. Actuals here come from the operator's DraftKings screenshots (nflverse had not published week-12 stats at 04:36Z); the full grade reruns from nflverse on Tuesday.

## 1. Game level
| | Market track | Model-only | Line | Actual |
|---|---|---|---|---|
| Score | LA 23.1, GB 20.6 | LA 25.4, GB 20.0 | LA -2.5, 43.5 | LA 26, GB 13 |
| Margin / total | LA +2.5 / 43.7 | LA +5.4 / 45.4 | +2.5 / 43.5 | LA +13 / 39 |

LA landed inside 3 points; GB was 7.6 under. The miss is market-wide (the line had the same game). Model-only leaned LA more than the market and was closer on the margin, a single game.

## 2. Players (DK points; projection = raw market-track expected points, frozen run 22:34Z)
| Player | Projected | Actual | Line (stat) | Note |
|---|---|---|---|---|
| Jordan Love | 14.3 | 10.6 (FLEX scoring) | 237 pass yds proj; 198, 1 TD, 2 INT | GB passing never got going |
| Christian Watson | 13.5 | 16.5 | 71 yds proj; 4-65-1 | left with an injury (DK "OUT") |
| Matthew Golden | 14.2 | 4.9 | 65 yds proj; 1-39 | biggest miss in our lineup |
| Kyren Williams | 17.4 | 16.5 | 56 rush proj; 46 + TD, 4-19 | on target |
| Colby Parkinson | 10.1 raw / ~7 anchored | 1.9 | 38 yds raw, 24.5 anchored; 2 rec, -1 yd | the market was right, we kept him for salary |
| J. Michael Sturdivant | 1.7 | 0 | punt slot | |
| **Blake Corum** | 10.2 | **31.5** | 8.5 car / 44 yds proj; **184 rush + TD** | RB2 broke out in a 13-point LA win |
| Konata Mumpfield | 5.6 | 10.9 | 27 yds proj; 4-69 | |
| **Brandon McManus (K)** | **not in our pool** | **17.0** (25.5 as CPT) | 4 FG, 2 XP | engine labelled LA's kicker as punter Ethan Evans (defect, fixed) |
| Rams DST | 7.2 | 11.0 | 1 sack, 2 INT, 1 FR, 7-13 PA | |

## 3. Our lineup
Love (CPT), Watson, Golden, K. Williams, Parkinson, Sturdivant: projected 86.5 (best of the anchored 20-lineup set), scored **55.73**, rank 46,341 of 59,453 (14,302 paid; #1 scored 119.15). The two operator-supplied top entries (111.52, 111.37; rank 492 and 501) were built on Corum + McManus (K as CPT or FLEX) + K. Williams + Love/Watson, one with the Rams DST.

## 4. What went wrong, in order of size
1. **One-sided stack on the losing side.** Four GB players (Love CPT + three receivers) needed a GB passing game; GB scored 13 and Love threw 2 INT. The builder ranks lineups by ceiling, which rewards stacking one offense; with a single entry that bet is all-or-nothing. The 20-lineup set had LA-side captains (Stafford, K. Williams); one entry could not carry both scripts.
2. **Kicker identity defect.** `params.kicker()` took the first "K" row for LA, which was the punter. DK's McManus never mapped, so the builder could not select the player who was in both top entries. Fixed (current depth-chart PK1; backtests byte-identical); all 10 Wed-Fri teams now map to the DK kicker.
3. **Backup RB in a blowout.** Corum: 184 yards on a projection of 44. The engine's game script moves team pass/run rates with the margin but keeps each RB's carry share fixed; in a lead the backup's share rises. Test queued (R-41, below).
4. **Ignoring a market signal we had.** Anchoring cut Parkinson from 38 to 24.5 yards; he still made the lineup at $4,400 because the optimizer valued his salary slot. He finished with -1 yard.
5. **No ownership view.** Love 77% owned, K. Williams 57%, Watson 54%: our lineup was chalk. The winners used a 0.8%-owned kicker captain. The builder has no ownership estimate, so it cannot trade a little mean for a lot of leverage in a 59k-entry field.

## 5. What held up
K. Williams (17.4 vs 16.5), Watson (13.5 vs 16.5 despite leaving hurt), LA's team total (23.1 vs 26), Rams DST direction. One game is a sample of one; nothing here changes a model default without the multi-season backtest.

## 6. Changes
| ID | Change | Status |
|---|---|---|
| Fix | Kicker label from the depth chart PK1 (DECISIONS #92) | done, pushed |
| R-41 | RB carry split responds to margin (backup share up when leading by 10+, lead back down), pbp-fitted, weeks 4-12 backtest | queued |
| O-4 | Ownership projection for DFS (salary, projection, field habits) and a leverage term in the Showdown/Classic builders | queued |
| O-5 | Showdown K/DST: model FG count and distance from the sims instead of a flat 3.9 per FG; let K/DST captains compete | queued |
| Rule | Single-entry Showdown: prefer the best lineup that has players from both offenses' upside (one captain-side stack plus the other side's lead RB or K) over the pure one-team ceiling | apply from CHI@DET |
