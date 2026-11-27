# W12 CHI@DET Showdown post mortem (2026-11-26)

Contest: $30K Huddle, single entry, 6,792 entries, 1,497 paid (22%). Our lineup 127.90, rank 2,940; winner 174.15 (Gibbs CPT 74.55, St. Brown, Swift, Odunze, Bates, Ahmed). Final CHI 39 - DET 35.

## Projections (anchored T-2h run 2026_w12_market_20261126T160705Z) vs actual
| Player | Projected | Actual |
|---|---|---|
| Game total | 56.4 (CHI 28.9, DET 27.5; p75 37 / 34) | 74 (both teams above p75) |
| Goff pass yds | 296 | 300, 1 TD |
| C. Williams pass yds | 275 | 345, 2 TD |
| St. Brown rec yds | 90 | 150 |
| Odunze rec yds | 57 | 87, 2 TD |
| LaPorta rec yds | 52 | 44, 1 TD |
| Gibbs rush / rec yds | 106 / 40 | 205 / 42, 3 TD |
| Swift rush / rec yds | 53 / 19 | 65 / 97, 1 TD |
| Ahmed rush / rec yds | 10 / 3 | 50 / 17 |

The player medians were close on the QBs; the misses are the shootout (74 points vs 56 projected) plus Swift's receiving role (97 yds vs 19). Every big miss is an upside miss in the same direction, which is one game-script draw, not a share or identity error.

## Lineup construction: the real miss
- Gibbs was our **#1 projected player** (24.1 DK points) and was in **none** of our top-3 lineups. The builder ranks by holdout top-1% (large-field GPP objective). QB + pass-catcher stacks have more variance than an RB captain, so they win on top-1% while losing on mean: our entry (Goff CPT stack) held mean 93.8 vs 98.2-98.9 for the best Gibbs lineups.
- Re-run with `APEX_SD_OBJ=mean` (#94) on the same sims: top lineup Gibbs CPT + C. Williams, Goff, LaPorta, Santos, TeSlaa, mean 98.9. Its actual score from the known players: 136.3 + Santos + TeSlaa (not on the screenshot), so roughly 145-155 vs our 127.9.
- Contest type matters: a single-entry field paying 22% rewards a strong mean; the top-1% objective was built for 150-max GPPs.

## Rule from here (until the ledger decides)
- Single entry or fields paying >= 20%: `APEX_SD_OBJ=mean`. Large multi-entry GPPs: top1, with at least one mean-objective lineup in the set.
- Every Showdown entry goes into `showdown_ledger.csv` with the alternative objective's lineup and both actual scores, so the objective choice is graded on results, not one game.
