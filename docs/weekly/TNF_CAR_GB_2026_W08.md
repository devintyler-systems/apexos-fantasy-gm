# Thursday night: CAR @ GB, Week 8 2026 (kickoff 8:15 PM ET, 00:15Z Oct 30)

**As of 2026-10-29 21:45Z (5:45 PM ET), T-150 minutes.** Frozen runs `2026_w08_market_20261029T213908Z` and `2026_w08_model_20261029T213915Z` (20,000 correlated simulations per game, both tracks). **Used:** nflverse injuries and depth charts through 14:07Z Thursday, ESPN game-summary explicit Outs (6 names), DraftKings lines via ESPN (open and current, **no prices, no touchdown markets**), NWS kickoff forecast, QB share 0.96 (DECISIONS #59). **Not used:** official NFL.com inactives (published about T-90, 6:45 PM ET; I cannot read them), book prices, a DraftKings salary file (no Showdown lineup: not built, and no salaries). Confidence figures are reliability indexes, not hit probabilities. Agents run: `data-auditor`, `model-qa` (no blocker for this game), `red-team` (10 lines pulled or downgraded, 4 parlay legs dropped).

## The answer
- **Game:** GB 25.0, CAR 21.6 (market-anchored; total 46.6, market GB -3.5 / 46.5). GB wins 58% (fair about -136). Model-only (no lines): GB 24.0, CAR 21.2, GB 58%. The sim sees a coin flip against both numbers: GB covers -3.5 50%, over 46.5 is 49.5%.
- **Published singles (3 PLAY, 3 LEAN), all at an assumed -110:** PLAY Jordan Love pass attempts OVER 34.5, Mitchell Evans receptions UNDER 1.5 (thin), Darren Waller receiving yards OVER 21.5 (thin). LEAN Bryce Young rush yards UNDER 9.5, Jordan Love rush yards UNDER 4.5, Jordan Love completions OVER 21.5. Everything else was pulled or stays inside the market.
- **No pass-yards pick.** Pass yards is the one market where the model trails the books (W7 Brier 0.297 vs 0.251) and both quarterbacks are projected about 10% below their 2026 averages (Young 252 vs 285, Love 250 vs 280). If anything the lean is toward the overs; the market rule keeps it a PASS.
- **Touchdowns:** Chuba Hubbard anytime 44% is the top number (6 TD in 6 games), then Golden 40% **if he plays** (27% unconditional, he is Questionable), Josh Jacobs 38%, Christian Watson 35%, Tucker Kraft 34%. No TD prices exist, so every TD "play at" figure is a model price, not an edge.
- **Biggest uncertainty is Matthew Golden (GB WR, Questionable, 67% active).** If he sits, Watson gains about 1 target and 9 receiving yards, Kraft 7 yards, Jacobs 4 yards (section Scenario). Re-check the 6:45 PM ET inactive list before anything on GB receivers.
- **Josh Jacobs is a no-bet on rushing:** the engine has him at 8.4 carries, the book at 14.5, and his only game back was 11 carries. See the Jacobs section.

## Red-team adjustments (applied to the draft screen)
| Line | Draft | Final | Reason |
|---|---|---|---|
| Love pass attempts O34.5 | PLAY | PLAY | on the side of the known pass-volume under-projection; GB -3.5 is under the 6-point cap; line stamp unverified |
| Evans rec U1.5 | PLAY | PLAY (thin) | receiving PLAY, 10 targets in 6 games; the line moved up (0.5 to 1.5), not toward the model |
| Waller rec yds O21.5 | PLAY | PLAY (thin) | 5/6 season, 23 targets; line moved toward the model 19.5 to 21.5 |
| Young rush yds U9.5 | PLAY | LEAN | DECISIONS #52: no must-play on a QB rush under; CAR guards Lewis and Simpkins Out add scramble risk |
| Love rush yds U4.5 | PLAY | LEAN | #52 rush-yard rule; GB OL Rhyan and Glover Out |
| Love completions O21.5 | PLAY | LEAN | weakest shrunk probability (57%); stale stamp; exposed to Golden |
| Hubbard rush yds U67.5 | PLAY | PULL | the under sits on the known carry under-allocation (12.5 projected vs 16.0 per game actual) |
| Hubbard rec U2.5 | PLAY | PULL | 3/6 season, bare minimum on every gate |
| Etienne rush yds O9.5 | LEAN | PULL | 0 of 2 games, under the 3-game minimum |
| Lloyd rush yds U17.5 | LEAN | PULL | same carry bias; Jacobs' return makes his role unknowable |

Parlays: dropped every leg built on a pulled or LEAN-level rush under, Aggressive #1 (legs conflict, stale line, Golden-exposed) and Aggressive #2 (Jacobs). Kept: Safest #1, Mid-tier #1, Aggressive #3 (Lloyd's touchdown leg is thin).

**Method notes.** (1) The 50/50 shrink is toward 50%, not toward the book's de-vigged probability (DECISIONS #53), so "Shrunk P" is not an edge against a price. (2) Most of the original plays had their lines move toward the model since open, so the value at today's number is smaller than the open number suggests. (3) ESPN line stamps are unreliable (some read after kickoff, some read two days old, Love completions and Waller receptions have not changed since Tuesday); no recency claim is made. (4) The anytime-TD probability is conditional on the player being active; for Golden (67%) multiply by 0.67 if your book does not void the bet.

## Game
| | CAR | GB |
|---|---|---|
| Win probability (market-anchored) | 38% | 58% |
| Mean points (P10-P90) | 21.6 (10-34) | 25.0 (13-38) |
| Plays / pass rate | 64.7 / 63% | 62.8 / 64% |
| Pass attempts / rush attempts | 37.6 / 24.0 | 38.2 / 22.5 |
| Passing yards / rushing yards | 263 / 104 | 261 / 92 |
| Offensive TDs / FGs | 2.2 / 1.8 | 2.8 / 1.6 |
| Sacks taken / interceptions thrown | 3.0 / 0.9 | 2.0 / 0.7 |

Distribution (20,000 sims): GB wins by 1-3 8%, by 4-7 12%, by 8-14 17%, by 15+ about 20%; CAR wins outright 38%. Total over 46.5 49.5%, over 44.5 52.9%, over 48.5 42.8%, 60+ 18.6%, 37 or fewer 28.2%. GB team total over 24.5 47%; CAR over 21.5 48%; GB 30+ 35%; CAR 30+ 22%. Both teams 20+ 42%. Fair moneyline GB -136 / CAR +136.

Environment: 49 F, wind 5 mph, no precipitation (NWS, mid-game hour): no weather adjustment. Both teams on a short week (4 rest days each).

**Offensive lines are the story.** GB is missing C Sean Rhyan and G Travis Glover (engine OL penalty 1.44); CAR is missing G Damien Lewis and G Torricelli Simpkins III (1.40), plus LB Jaelan Phillips and CB Akayleb Evans. Both quarterbacks face a short-handed line, and scramble risk is why the QB-rush unders are LEANs, not PLAYs; the sim carries 3.0 sacks for CAR and 2.0 for GB.

Quarterbacks: Bryce Young (CAR, 98% active, full practice, 43 snaps in Week 7) and Jordan Love (GB, 100%).

## Scenario: Matthew Golden out (re-ran GB with Golden Out)
| GB player | Base | Golden out | Change |
|---|---|---|---|
| Christian Watson rec yds / DK points | 76.6 / 15.8 | 86.0 / 18.0 | +9.5 yds, +1.0 targets, +6 pts anytime TD |
| Tucker Kraft rec yds | 45.4 | 52.2 | +6.8 yds, +0.6 rec, +5 pts anytime TD |
| Josh Jacobs rec yds | 25.6 | 29.4 | +3.8 yds, +0.5 rec |
| Pierre Strong rec yds | 18.1 | 21.6 | +3.5 yds |
| Savion Williams rec yds | 13.9 | 17.7 | +3.8 yds |
| Jordan Love passing | 250 yds | 250 yds | unchanged (team volume does not move) |

## Jacobs: why the engine and the book disagree
Josh Jacobs has one game in 2026 (Week 7, back from the suspension): **11 carries, 7 targets, 5 catches, 52% of snaps**, 65% of GB's running-back carries, no touchdown. Engine: **8.4 carries, 35.9 yards, 3.4 receptions, 38% anytime TD.** DraftKings: 14.5 carries (ESPN DraftKings line), 59.5 yards (open 55.5), 2.5 receptions. A reasonable central number is 11 to 12 carries for 45 to 50 yards: the engine runs low because it shrinks a one-game sample toward last year's role and splits the rest among Lloyd, Johnson and Strong; the book runs high. **Do not bet Jacobs' rushing under (the model's 73% shrunk probability is the bias) and do not take the over at 14.5.** Receiving over 2.5 (model 62%) rests on one game. The returning-player prior is still on the work queue (POSTMORTEM_2026_W07_FULL).

## Player dossier (floor / median / ceiling are P10 / P50 / P90 among simulations in which the player is active; DK points are DraftKings Classic scoring including the 100-yard and 300-yard bonuses)
| Player | Pos | Active | Pass yds (P10-med-P90) | Rush att / yds | Targets | Rec | Rec yds (P10-med-P90) | Anytime TD | First TD | DK pts mean (P10-P90) |
|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young (CAR) | QB | 98% | 155-242-362 | 1.7 / 7 | 0.0 | 0.0 |  | 14% | 3% | 16.4 (7-27) |
| Chuba Hubbard (CAR) | RB | 100% |  | 12.5 / 57 | 3.2 | 2.3 | 0-13-38 | 44% | 11% | 13.2 (6-22) |
| Trevor Etienne (CAR) | RB | 100% |  | 4.4 / 17 | 0.8 | 0.5 |  | 12% | 2% | 3.4 (0-8) |
| AJ Dillon (CAR) | RB | 100% |  | 3.3 / 13 | 0.5 | 0.3 |  | 9% | 2% | 2.4 (0-6) |
| Tetairoa McMillan (CAR) | WR | 100% |  |  | 9.1 | 5.3 | 22-65-132 | 29% | 6% | 15.3 (6-27) |
| Jalen Coker (CAR) | WR | 95% |  |  | 6.9 | 4.2 | 12-46-101 | 22% | 5% | 11.2 (3-21) |
| John Metchie III (CAR) | WR | 100% |  |  | 3.5 | 2.1 | 0-18-54 | 9% | 2% | 5.0 (0-11) |
| Darren Waller (CAR) | TE | 100% |  |  | 5.1 | 3.2 | 5-29-69 | 18% | 4% | 7.8 (2-15) |
| Tommy Tremble (CAR) | TE | 100% |  |  | 4.0 | 2.6 | 0-20-53 | 14% | 3% | 6.0 (1-12) |
| Mitchell Evans (CAR) | TE | 100% |  |  | 1.8 | 1.2 | 0-7-32 | 8% | 2% | 2.9 (0-7) |
| Jordan Love (GB) | QB | 100% | 151-238-365 | 1.1 / 4 | 0.0 | 0.0 |  | 7% | 1% | 17.4 (8-29) |
| Josh Jacobs (GB) | RB | 100% |  | 8.4 / 36 | 4.9 | 3.4 | 4-21-53 | 38% | 9% | 12.3 (5-21) |
| MarShawn Lloyd (GB) | RB | 100% |  | 5.3 / 19 | 2.3 | 1.5 | 0-7-28 | 33% | 8% | 6.9 (1-14) |
| Pierre Strong (GB) | RB | 100% |  | 2.3 / 9 | 3.6 | 2.5 | 0-14-40 | 19% | 4% | 6.4 (2-12) |
| Kaleb Johnson (GB) | RB | 100% |  | 3.3 / 14 | 0.4 | 0.3 |  | 14% | 3% | 2.7 (0-7) |
| Christian Watson (GB) | WR | 100% |  |  | 8.5 | 4.8 | 20-68-143 | 35% | 8% | 15.8 (5-29) |
| Matthew Golden (GB) | WR | 67% |  |  | 7.5 | 4.1 | 13-48-106 | 40% | 9% | 12.9 (4-24) |
| Savion Williams (GB) | WR | 100% |  |  | 2.0 | 1.1 | 0-8-38 | 8% | 2% | 3.3 (0-8) |
| Bo Melton (GB) | WR | 100% |  |  | 1.6 | 0.9 | 0-4-32 | 5% | 1% | 2.3 (0-6) |
| Tucker Kraft (GB) | TE | 100% |  |  | 6.6 | 4.1 | 10-39-88 | 34% | 8% | 11.3 (3-21) |
| Jonnu Smith (GB) | TE | 100% |  |  | 1.7 | 1.0 | 0-5-29 | 7% | 1% | 2.5 (0-7) |

## Singles (all screened lines)
Side is the side the model favours; Model P is before the 50/50 shrink; passing overs include the +0.08 bias shift. 'Season' = games that side cleared the line / games played.
<details><summary>All lines screened</summary>

| Player | Market | Line | Model P(over) | Side | Shrunk P | Season games over / under / n | Active |
|---|---|---|---|---|---|---|---|
| Bo Melton | rec | 0.5 | 56% | OVER | 53% | 3/3/6 | 100% |
| Bo Melton | rec_yds | 2.5 | 53% | OVER | 51% | 3/3/6 | 100% |
| Bryce Young | pass_att | 36.5 | 47% | OVER | 52% | 4/2/6 | 98% |
| Bryce Young | pass_cmp | 22.5 | 48% | OVER | 53% | 4/2/6 | 98% |
| Bryce Young | pass_yds | 253.5 | 44% | OVER | 51% | 5/1/6 | 98% |
| Bryce Young | rush_yds | 9.5 | 24% | UNDER | 63% | 1/4/5 | 98% |
| Brycen Tremayne | rec | 0.5 | 51% | OVER | 51% | 2/1/3 | 100% |
| Brycen Tremayne | rec_yds | 3.5 | 47% | UNDER | 51% | 2/1/3 | 100% |
| Christian Watson | rec | 4.5 | 50% | OVER | 50% | 4/3/7 | 100% |
| Christian Watson | rec_yds | 71.5 | 47% | UNDER | 52% | 3/4/7 | 100% |
| Chuba Hubbard | rec | 2.5 | 39% | UNDER | 55% | 3/3/6 | 100% |
| Chuba Hubbard | rec_yds | 16.5 | 41% | UNDER | 54% | 3/3/6 | 100% |
| Chuba Hubbard | rush_att | 16.5 | 14% | UNDER | 68% | 3/3/6 | 100% |
| Chuba Hubbard | rush_yds | 67.5 | 31% | UNDER | 60% | 3/3/6 | 100% |
| Darren Waller | rec | 2.5 | 60% | OVER | 55% | 3/3/6 | 100% |
| Darren Waller | rec_yds | 21.5 | 63% | OVER | 56% | 5/1/6 | 100% |
| Jalen Coker | rec | 4.5 | 40% | UNDER | 55% | 3/2/5 | 95% |
| Jalen Coker | rec_yds | 61.5 | 34% | UNDER | 58% | 3/2/5 | 95% |
| John Metchie III | rec | 1.5 | 58% | OVER | 54% | 4/0/4 | 100% |
| John Metchie III | rec_yds | 16.5 | 52% | OVER | 51% | 4/0/4 | 100% |
| Jonnu Smith | rec | 0.5 | 60% | OVER | 55% | 4/0/4 | 100% |
| Jonnu Smith | rec_yds | 2.5 | 56% | OVER | 53% | 4/0/4 | 100% |
| Jordan Love | pass_att | 34.5 | 67% | OVER | 62% | 4/3/7 | 100% |
| Jordan Love | pass_cmp | 21.5 | 57% | OVER | 57% | 5/2/7 | 100% |
| Jordan Love | pass_yds | 262.5 | 39% | UNDER | 52% | 5/2/7 | 100% |
| Jordan Love | rush_yds | 4.5 | 27% | UNDER | 62% | 2/3/5 | 100% |
| Josh Jacobs | rec | 2.5 | 62% | OVER | 56% | 1/0/1 | 100% |
| Josh Jacobs | rec_yds | 18.5 | 56% | OVER | 53% | 1/0/1 | 100% |
| Josh Jacobs | rush_att | 14.5 | 3% | UNDER | 73% | 0/1/1 | 100% |
| Josh Jacobs | rush_yds | 59.5 | 14% | UNDER | 68% | 0/1/1 | 100% |
| MarShawn Lloyd | rec | 1.5 | 43% | UNDER | 53% | 4/3/7 | 100% |
| MarShawn Lloyd | rec_yds | 5.5 | 56% | OVER | 53% | 5/2/7 | 100% |
| MarShawn Lloyd | rush_att | 5.5 | 43% | UNDER | 53% | 6/1/7 | 100% |
| MarShawn Lloyd | rush_yds | 17.5 | 42% | UNDER | 54% | 4/3/7 | 100% |
| Matthew Golden | rec | 4.5 | 38% | UNDER | 56% | 5/2/7 | 67% |
| Matthew Golden | rec_yds | 58.5 | 39% | UNDER | 55% | 4/3/7 | 67% |
| Mitchell Evans | rec | 1.5 | 31% | UNDER | 59% | 2/4/6 | 100% |
| Mitchell Evans | rec_yds | 6.5 | 50% | OVER | 50% | 5/1/6 | 100% |
| Savion Williams | rec | 2.5 | 13% | UNDER | 69% | 2/0/2 | 100% |
| Savion Williams | rec_yds | 24.5 | 21% | UNDER | 65% | 2/0/2 | 100% |
| Savion Williams | rush_yds | 3.5 | 20% | UNDER | 65% | 2/0/2 | 100% |
| Tetairoa McMillan | rec | 5.5 | 43% | UNDER | 54% | 2/4/6 | 100% |
| Tetairoa McMillan | rec_yds | 73.5 | 43% | UNDER | 54% | 4/2/6 | 100% |
| Tommy Tremble | rec | 2.5 | 46% | UNDER | 52% | 4/2/6 | 100% |
| Tommy Tremble | rec_yds | 15.5 | 60% | OVER | 55% | 3/3/6 | 100% |
| Trevor Etienne | rush_yds | 9.5 | 61% | OVER | 56% | 0/2/2 | 100% |
| Tucker Kraft | rec | 4.5 | 39% | UNDER | 55% | 3/4/7 | 100% |
| Tucker Kraft | rec_yds | 44.5 | 43% | UNDER | 53% | 3/4/7 | 100% |

</details>


## Touchdown scorers (model probability, fair odds, price to play at)

Anytime counts rushing and receiving TDs (QB rushing included). First TD uses each player's share of simulated touchdowns. Prices below the 'play at' column are not worth taking.

| Player | Pos | Active | 2026 so far | Anytime | Fair | Play at or better | 2+ TD | Fair 2+ | First TD | Fair first |
|---|---|---|---|---|---|---|---|---|---|---|
| Chuba Hubbard (CAR) | RB | 100% | 6 TD / 6 g (18 tgt, 96 car) | 43.6% | +129 | +157 | 10.6% | +839 | 10.8% | +825 |
| Matthew Golden (GB) | WR | 67% | 3 TD / 7 g (69 tgt, 1 car) | 39.6% | +153 | +183 | 8.4% | +1090 | 9.4% | +964 |
| Josh Jacobs (GB) | RB | 100% | 1 TD / 1 g (7 tgt, 11 car) | 37.7% | +165 | +197 | 7.4% | +1250 | 8.9% | +1022 |
| Christian Watson (GB) | WR | 100% | 6 TD / 7 g (56 tgt, 0 car) | 35.4% | +182 | +216 | 6.9% | +1359 | 8.3% | +1104 |
| Tucker Kraft (GB) | TE | 100% | 2 TD / 7 g (43 tgt, 2 car) | 34.0% | +194 | +230 | 5.9% | +1593 | 7.8% | +1177 |
| MarShawn Lloyd (GB) | RB | 100% | 3 TD / 7 g (16 tgt, 54 car) | 32.6% | +207 | +244 | 5.5% | +1718 | 7.5% | +1228 |
| Tetairoa McMillan (CAR) | WR | 100% | 2 TD / 6 g (54 tgt, 0 car) | 29.4% | +241 | +282 | 4.3% | +2239 | 6.5% | +1450 |
| Jalen Coker (CAR) | WR | 95% | 2 TD / 5 g (39 tgt, 0 car) | 22.4% | +347 | +401 | 2.3% | +4336 | 4.7% | +2017 |
| Pierre Strong (GB) | RB | 100% | 0 TD / 2 g (10 tgt, 16 car) | 18.5% | +440 | +505 | 1.6% | +6111 | 3.9% | +2440 |
| Darren Waller (CAR) | TE | 100% | 3 TD / 6 g (23 tgt, 0 car) | 17.5% | +470 | +538 | 1.5% | +6436 | 3.6% | +2649 |
| Tommy Tremble (CAR) | TE | 100% | 2 TD / 6 g (21 tgt, 0 car) | 14.4% | +595 | +678 | 1.0% | +9752 | 2.9% | +3314 |
| Kaleb Johnson (GB) | RB | 100% | 0 TD / 5 g (3 tgt, 28 car) | 13.7% | +628 | +715 | 0.9% | +11596 | 2.9% | +3408 |
| Bryce Young (CAR) | QB | 98% | 1 TD / 6 g (0 tgt, 10 car) | 13.6% | +633 | +721 | 0.9% | +11038 | 2.8% | +3473 |
| Trevor Etienne (CAR) | RB | 100% | 0 TD / 2 g (2 tgt, 7 car) | 11.7% | +755 | +858 | 0.7% | +14288 | 2.4% | +4066 |
| John Metchie III (CAR) | WR | 100% | 1 TD / 4 g (17 tgt, 0 car) | 9.4% | +962 | +1089 | 0.5% | +19702 | 1.9% | +5158 |
| AJ Dillon (CAR) | RB | 100% | 0 TD / 4 g (2 tgt, 17 car) | 8.8% | +1033 | +1169 | 0.4% | +27297 | 1.8% | +5536 |
| Savion Williams (GB) | WR | 100% | 0 TD / 2 g (7 tgt, 4 car) | 8.1% | +1135 | +1283 | 0.2% | +42453 | 1.6% | +6174 |
| Mitchell Evans (CAR) | TE | 100% | 0 TD / 6 g (10 tgt, 1 car) | 8.0% | +1153 | +1304 | 0.3% | +32687 | 1.6% | +6292 |
| Jonnu Smith (GB) | TE | 100% | 0 TD / 4 g (8 tgt, 0 car) | 7.4% | +1243 | +1404 | 0.3% | +34988 | 1.5% | +6642 |
| Jordan Love (GB) | QB | 100% | 1 TD / 7 g (0 tgt, 11 car) | 7.0% | +1321 | +1492 | 0.2% | +39900 | 1.4% | +7040 |
| Brycen Tremayne (CAR) | WR | 100% | 0 TD / 3 g (10 tgt, 0 car) | 6.0% | +1567 | +1767 | 0.1% | +79900 | 0.9% | +10769 |
| Bo Melton (GB) | WR | 100% | 0 TD / 6 g (10 tgt, 0 car) | 6.0% | +1567 | +1767 | 0.1% | +95138 | 1.0% | +9734 |


**Quarterback passing TDs** (not priced in the feed)

| QB | Mean | 1+ | 2+ | 3+ |
|---|---|---|---|---|
| Bryce Young | 1.28 | 74% (-290) | 37% (+168) | 12% (+700) |
| Jordan Love | 1.68 | 83% (-505) | 52% (-108) | 23% (+333) |


**Sneaky TD longshots the model likes** (anytime 8% to 30%, role-based, not price-based): 
Tetairoa McMillan 29% (fair +241, take at +282 or better); Jalen Coker 22% (fair +347, take at +401 or better); Pierre Strong 19% (fair +440, take at +505 or better); Darren Waller 18% (fair +470, take at +538 or better); Tommy Tremble 14% (fair +595, take at +678 or better); Kaleb Johnson 14% (fair +628, take at +715 or better); Bryce Young 14% (fair +633, take at +721 or better); Trevor Etienne 12% (fair +755, take at +858 or better); John Metchie III 9% (fair +962, take at +1089 or better); AJ Dillon 9% (fair +1033, take at +1169 or better); Savion Williams 8% (fair +1135, take at +1283 or better)



## Parlays after the red-team (fair odds from the joint simulation, not book prices)
| Tier | Legs | Hit probability | Fair odds | Play at or better |
|---|---|---|---|---|
| Safest | Jordan Love pass TD 1+ + GB to win | 52.6% | -111 | +113 |
| Mid-tier | Love pass attempts O34.5 + Evans rec U1.5 + CAR +3.5 | 21.7% | +361 | +416 |
| Aggressive | Hubbard anytime TD + Lloyd anytime TD + GB to win (Lloyd leg thin) | 8.0% | +1153 | +1304 |

Dropped: Young U9.5 + Love pass TD 1+; Hubbard U67.5 + Love pass TD 1+; the two other mid-tier tickets that carried pulled legs; Aggressive #1 and #2.

## Line movement since open (DraftKings via ESPN)
| Player | Market | Open | Now |
|---|---|---|---|
| Bryce Young | pass yds | 247.5 | 253.5 |
| Matthew Golden | rec yds | 64.5 | 58.5 |
| Josh Jacobs | rush yds | 55.5 | 59.5 |
| Jordan Love | pass yds | 266.5 | 262.5 |
| Josh Jacobs | rec yds | 14.5 | 18.5 |
| Mitchell Evans | rec | 0.5 | 1.5 |
| MarShawn Lloyd | rush yds | 19.5 | 17.5 |

Golden's receiving line fell 6 yards (his Questionable tag is priced). Jacobs' lines rose on both rushing and receiving: the book is moving toward a bigger role than the engine gives him.

## Fantasy tie-in (SPAMML, touchdown-only scoring; your roster: Watson)
| Player | Team | Pos | SPAMML owner | Projected league pts tonight |
|---|---|---|---|---|
| Jordan Love | GB | QB | Jama | 10.49 |
| Bryce Young | CAR | QB | SHAQ | 8.36 |
| Christian Watson | GB | WR | FLEX | 2.59 |
| Tucker Kraft | GB | TE | Jama | 2.43 |
| Tetairoa McMillan | CAR | WR | CMFM | 2.04 |
| Matthew Golden | GB | WR | H D | 1.98 |
| Jalen Coker | CAR | WR | Cockney | 1.41 |
| Darren Waller | CAR | TE | W  | 1.15 |
| Tommy Tremble | CAR | TE | W  | 0.93 |
| John Metchie III | CAR | WR | W  | 0.60 |
| Savion Williams | GB | WR | W  | 0.50 |
| Mitchell Evans | CAR | TE | W  | 0.50 |
| Jonnu Smith | GB | TE | W  | 0.46 |
| Bo Melton | GB | WR | W  | 0.32 |

Watson is the only player of yours in this game: 35% anytime TD, about 2.6 league points. Nobody from this game beats Diggs or Meyers for a waiver claim. If Golden sits, Watson's expectation rises to about 3.0.

## Known limits
- No book prices: the report cannot say whether any line is +EV; it ranks the model's lean at an assumed -110.
- QB passing yards run about 10% low for these two quarterbacks (model-qa) and RB carries are under-allocated (Hubbard 12.5 vs 16.0, Lloyd 5.3 vs 7.7 per game actual). Both are known, queued items (DECISIONS #52, #58, #59); the report responds by pulling the lines on the biased side, not by changing the model.
- CHI @ SEA has no nflverse injury rows in this run (Monday game); not used here.
- Xavier Smith is projected on LA but is on SF's practice squad (data-auditor); not a CAR/GB issue.

## What I need from you (by 6:45 PM ET)
1. **The official NFL.com inactive list for CAR and GB** (published about 90 minutes before kickoff) and a screenshot or workbook of the DraftKings prices for this game. With them I re-run the game, re-freeze, and price every pick against the real number.
2. Nothing else: no salary file means no Showdown lineup; say the word if you have one.
