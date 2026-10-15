# Thursday night: SEA @ DEN, Week 6 2026 (market-anchored track, 20,000 correlated simulations)

Frozen runs: `2026_w06_market_20261015T203811Z`, `2026_w06_model_20261015T203819Z` (pre-kickoff). Inputs: nflverse through Week 5, ESPN game-summary Outs (SEA@DEN), DraftKings lines via ESPN (open and current), no prices.

**Read this first.** Lines are DraftKings via ESPN (no prices, no touchdown markets). Singles are screened at an assumed -110 after shrinking the model 50/50 toward the market; a PLAY needs about 61% model probability, active 95%+, and the side hitting in at least half of the player's games this season. Touchdown and parlay prices are FAIR odds from the joint simulation; 'play at' adds a 12% cushion. The W4 and W5 postmortems found no edge over the books on yardage and count props; anytime-TD probabilities are calibrated. Treat everything here as a ranked lean, not a lock.

## Game

| | SEA | DEN |
|---|---|---|
| Win probability | 55% | 40% |
| Mean points (P10-P90) | 21.6 (10-34) | 19.0 (7-31) |

Total 40.6 (P10-P90 23-58). Market: DEN +2.5, total 40.5.

Model-only track: SEA 23.3, DEN 21.9, SEA win 52%.

## Singles (main lines)

Side = the side the model favours; model P is before the 50/50 shrink (passing overs include the +0.08 bias shift); 'season' = games that side cleared the line / games played; 'fair' = fair American price at the shrunk probability; 'move' = line change since open.

| Label | Player | Market | Side | Line | Model P | Shrunk P | Fair | Season | Model-only agrees | Move |
|---|---|---|---|---|---|---|---|---|---|---|
| PLAY | Sam Darnold (SEA) | rush_att | UNDER | 2.5 | 72% | 61% | -157 | 2/3 | yes | +0.0 |
| PLAY | Rashid Shaheed (SEA) | rec | OVER | 1.5 | 71% | 61% | -154 | 3/5 | yes | -1.0 |
| PLAY | Bo Nix (DEN) | rush_att | UNDER | 4.5 | 69% | 60% | -148 | 4/5 | yes | +1.0 |
| PLAY | Bo Nix (DEN) | rush_yds | UNDER | 13.5 | 69% | 59% | -147 | 5/5 | yes | -1.0 |
| PLAY | Bo Nix (DEN) | pass_att | UNDER | 34.5 | 67% | 59% | -142 | 4/5 | yes | +0.0 |
| PLAY | Jaylen Waddle (DEN) | rec | UNDER | 4.5 | 66% | 58% | -137 | 3/5 | yes | +0.0 |
| PLAY | Courtland Sutton (DEN) | rec | UNDER | 3.5 | 64% | 57% | -133 | 5/5 | yes | +0.0 |
| PLAY | Bo Nix (DEN) | pass_cmp | UNDER | 21.5 | 64% | 57% | -132 | 3/5 | yes | +1.0 |
| PLAY | Jaylen Waddle (DEN) | rec_yds | UNDER | 45.5 | 62% | 56% | -127 | 4/5 | yes | -6.0 |
| PLAY | Bo Nix (DEN) | pass_yds | UNDER | 198.5 | 61% | 56% | -125 | 3/5 | yes | -14.0 |
| LEAN | George Holani (SEA) | rush_yds | OVER | 13.5 | 79% | 65% | -182 | 2/5 | yes | +0.0 |
| LEAN | George Holani (SEA) | rush_att | OVER | 4.5 | 77% | 63% | -172 | 2/5 | yes | +0.0 |
| LEAN | J.K. Dobbins (DEN) | rec | UNDER | 1.5 | 77% | 63% | -172 | 1/3 | yes | +0.0 |
| LEAN | Emanuel Wilson (SEA) | rec | UNDER | 1.5 | 70% | 60% | -150 | 1/3 | yes | +0.0 |
| LEAN | Emanuel Wilson (SEA) | rec_yds | UNDER | 9.5 | 65% | 58% | -136 | 1/3 | yes | -1.0 |
| LEAN | Lil'Jordan Humphrey (DEN) | rec | OVER | 0.5 | 65% | 57% | -134 | 1/2 | yes | -1.0 |
| LEAN | Marvin Mims Jr. (DEN) | rec | UNDER | 1.5 | 64% | 57% | -133 | 1/2 | yes | +0.0 |
| LEAN | Tory Horton (SEA) | rec | OVER | 0.5 | 62% | 56% | -128 | 2/2 | yes | +0.0 |
| LEAN | Tory Horton (SEA) | rec_yds | OVER | 1.5 | 61% | 56% | -126 | 2/2 | yes | -6.0 |
| LEAN | Troy Franklin (DEN) | rec_yds | UNDER | 17.5 | 60% | 55% | -123 | 2/4 | yes | -3.0 |
| LEAN | Rashid Shaheed (SEA) | rec_yds | OVER | 20.5 | 60% | 55% | -123 | 2/5 | yes | +0.0 |
| LEAN | Cooper Kupp (SEA) | rec | UNDER | 2.5 | 60% | 55% | -122 | 4/5 | yes | +0.0 |
| LEAN | RJ Harvey (DEN) | rec_yds | UNDER | 22.5 | 59% | 55% | -121 | 1/4 | yes | -3.0 |
| LEAN | Sam Darnold (SEA) | rush_yds | UNDER | 5.5 | 59% | 55% | -120 | 2/3 | yes | +1.0 |
| LEAN | Lil'Jordan Humphrey (DEN) | rec_yds | OVER | 3.5 | 59% | 54% | -119 | 1/2 | yes | -4.0 |
| LEAN | RJ Harvey (DEN) | rec | UNDER | 3.5 | 58% | 54% | -116 | 1/4 | yes | +0.0 |
| LEAN | Sam Darnold (SEA) | pass_cmp | UNDER | 19.5 | 57% | 54% | -116 | 3/4 | yes | -1.0 |
| LEAN | Courtland Sutton (DEN) | rec_yds | UNDER | 31.5 | 57% | 53% | -115 | 4/5 | yes | -4.0 |

10 PLAY, 18 LEAN of 51 priced lines. Everything else was inside the market.

<details><summary>All lines screened</summary>

| Player | Market | Line | Model P(over) | Side | Shrunk P | Season games over / under / n | Active |
|---|---|---|---|---|---|---|---|
| AJ Barner | rec | 2.5 | 56% | OVER | 53% | 2/3/5 | 100% |
| AJ Barner | rec_yds | 26.5 | 51% | OVER | 50% | 1/4/5 | 100% |
| Bo Nix | pass_att | 34.5 | 25% | UNDER | 59% | 1/4/5 | 100% |
| Bo Nix | pass_cmp | 21.5 | 28% | UNDER | 57% | 2/3/5 | 100% |
| Bo Nix | pass_yds | 198.5 | 31% | UNDER | 56% | 2/3/5 | 100% |
| Bo Nix | rush_att | 4.5 | 31% | UNDER | 60% | 1/4/5 | 100% |
| Bo Nix | rush_yds | 13.5 | 31% | UNDER | 59% | 0/5/5 | 100% |
| Cooper Kupp | rec | 2.5 | 40% | UNDER | 55% | 1/4/5 | 100% |
| Cooper Kupp | rec_yds | 21.5 | 55% | OVER | 52% | 2/3/5 | 100% |
| Courtland Sutton | rec | 3.5 | 36% | UNDER | 57% | 0/5/5 | 100% |
| Courtland Sutton | rec_yds | 31.5 | 43% | UNDER | 53% | 1/4/5 | 100% |
| Emanuel Wilson | rec | 1.5 | 30% | UNDER | 60% | 2/1/3 | 100% |
| Emanuel Wilson | rec_yds | 9.5 | 35% | UNDER | 58% | 2/1/3 | 100% |
| Emanuel Wilson | rush_att | 17.5 | 47% | UNDER | 51% | 3/2/5 | 100% |
| Emanuel Wilson | rush_yds | 67.5 | 56% | OVER | 53% | 2/3/5 | 100% |
| Evan Engram | rec | 2.5 | 50% | OVER | 50% | 2/3/5 | 100% |
| Evan Engram | rec_yds | 20.5 | 49% | UNDER | 50% | 2/3/5 | 100% |
| George Holani | rec | 1.5 | 50% | UNDER | 50% | 2/3/5 | 95% |
| George Holani | rec_yds | 10.5 | 49% | UNDER | 51% | 2/3/5 | 95% |
| George Holani | rush_att | 4.5 | 77% | OVER | 63% | 2/3/5 | 95% |
| George Holani | rush_yds | 13.5 | 79% | OVER | 65% | 2/3/5 | 95% |
| J.K. Dobbins | rec | 1.5 | 23% | UNDER | 63% | 2/1/3 | 100% |
| J.K. Dobbins | rec_yds | 3.5 | 45% | UNDER | 53% | 3/0/3 | 100% |
| J.K. Dobbins | rush_att | 13.5 | 53% | OVER | 52% | 2/3/5 | 100% |
| J.K. Dobbins | rush_yds | 48.5 | 53% | OVER | 52% | 2/3/5 | 100% |
| Jaxon Smith-Njigba | rec | 6.5 | 44% | UNDER | 53% | 3/2/5 | 95% |
| Jaxon Smith-Njigba | rec_yds | 92.5 | 49% | UNDER | 50% | 4/1/5 | 95% |
| Jaxon Smith-Njigba | rush_yds | 0.5 | 16% | UNDER | 67% | 1/0/1 | 95% |
| Jaylen Waddle | rec | 4.5 | 34% | UNDER | 58% | 2/3/5 | 100% |
| Jaylen Waddle | rec_yds | 45.5 | 38% | UNDER | 56% | 1/4/5 | 100% |
| Lil'Jordan Humphrey | rec | 0.5 | 65% | OVER | 57% | 1/1/2 | 100% |
| Lil'Jordan Humphrey | rec_yds | 3.5 | 59% | OVER | 54% | 1/1/2 | 100% |
| Marvin Mims Jr. | rec | 1.5 | 36% | UNDER | 57% | 1/1/2 | 100% |
| Marvin Mims Jr. | rec_yds | 9.5 | 43% | UNDER | 53% | 1/1/2 | 100% |
| Marvin Mims Jr. | rush_yds | 1.5 | 13% | UNDER | 69% | 1/0/1 | 100% |
| RJ Harvey | rec | 3.5 | 42% | UNDER | 54% | 3/1/4 | 100% |
| RJ Harvey | rec_yds | 22.5 | 41% | UNDER | 55% | 3/1/4 | 100% |
| RJ Harvey | rush_att | 4.5 | 51% | OVER | 50% | 1/3/4 | 100% |
| RJ Harvey | rush_yds | 14.5 | 52% | OVER | 51% | 2/2/4 | 100% |
| Rashid Shaheed | rec | 1.5 | 71% | OVER | 61% | 3/2/5 | 100% |
| Rashid Shaheed | rec_yds | 20.5 | 60% | OVER | 55% | 2/3/5 | 100% |
| Rashid Shaheed | rush_yds | 1.5 | 24% | UNDER | 63% | 2/0/2 | 100% |
| Sam Darnold | pass_att | 30.5 | 36% | UNDER | 53% | 1/3/4 | 100% |
| Sam Darnold | pass_cmp | 19.5 | 35% | UNDER | 54% | 1/3/4 | 100% |
| Sam Darnold | pass_yds | 222.5 | 47% | OVER | 53% | 1/3/4 | 100% |
| Sam Darnold | rush_att | 2.5 | 28% | UNDER | 61% | 1/2/3 | 100% |
| Sam Darnold | rush_yds | 5.5 | 41% | UNDER | 55% | 1/2/3 | 100% |
| Tory Horton | rec | 0.5 | 62% | OVER | 56% | 2/0/2 | 100% |
| Tory Horton | rec_yds | 1.5 | 61% | OVER | 56% | 2/0/2 | 100% |
| Troy Franklin | rec | 1.5 | 47% | UNDER | 52% | 1/3/4 | 100% |
| Troy Franklin | rec_yds | 17.5 | 40% | UNDER | 55% | 2/2/4 | 100% |

</details>

## Touchdown scorers (model probability, fair odds, price to play at)

Anytime counts rushing and receiving TDs (QB rushing included). First TD uses each player's share of simulated touchdowns. Prices below the 'play at' column are not worth taking.

| Player | Pos | Active | 2026 so far | Anytime | Fair | Play at or better | 2+ TD | Fair 2+ | First TD | Fair first |
|---|---|---|---|---|---|---|---|---|---|---|
| Jaxon Smith-Njigba (SEA) | WR | 95% | 7 TD / 5 g (50 tgt, 1 car) | 42.3% | +137 | +165 | 9.9% | +908 | 12.4% | +709 |
| Emanuel Wilson (SEA) | RB | 100% | 3 TD / 5 g (7 tgt, 73 car) | 39.5% | +153 | +184 | 8.3% | +1098 | 11.5% | +770 |
| J.K. Dobbins (DEN) | RB | 100% | 1 TD / 5 g (6 tgt, 64 car) | 31.4% | +218 | +256 | 5.2% | +1834 | 8.6% | +1059 |
| AJ Barner (SEA) | TE | 100% | 1 TD / 5 g (20 tgt, 1 car) | 24.7% | +305 | +353 | 3.0% | +3228 | 6.5% | +1436 |
| Courtland Sutton (DEN) | WR | 100% | 1 TD / 5 g (25 tgt, 0 car) | 24.4% | +310 | +359 | 2.9% | +3336 | 6.3% | +1477 |
| Jaylen Waddle (DEN) | WR | 100% | 1 TD / 5 g (31 tgt, 2 car) | 22.3% | +348 | +402 | 2.5% | +3940 | 5.7% | +1641 |
| George Holani (SEA) | RB | 95% | 0 TD / 5 g (12 tgt, 26 car) | 21.3% | +370 | +427 | 2.1% | +4563 | 5.5% | +1702 |
| RJ Harvey (DEN) | RB | 100% | 0 TD / 4 g (22 tgt, 15 car) | 20.7% | +383 | +440 | 2.0% | +4838 | 5.2% | +1812 |
| Rashid Shaheed (SEA) | WR | 100% | 1 TD / 5 g (19 tgt, 3 car) | 16.7% | +501 | +573 | 1.4% | +7280 | 4.2% | +2304 |
| Evan Engram (DEN) | TE | 100% | 1 TD / 5 g (17 tgt, 0 car) | 15.7% | +539 | +615 | 1.2% | +8484 | 3.9% | +2464 |
| Cooper Kupp (SEA) | WR | 100% | 1 TD / 5 g (15 tgt, 0 car) | 15.4% | +550 | +628 | 1.1% | +9032 | 3.8% | +2556 |
| Bo Nix (DEN) | QB | 100% | 1 TD / 5 g (0 tgt, 18 car) | 13.7% | +628 | +715 | 0.9% | +11073 | 3.4% | +2835 |
| Troy Franklin (DEN) | WR | 100% | 0 TD / 4 g (6 tgt, 1 car) | 10.0% | +898 | +1018 | 0.4% | +25874 | 2.4% | +4129 |
| Nate Adkins (DEN) | TE | 100% | 2 TD / 2 g (5 tgt, 1 car) | 8.9% | +1017 | +1151 | 0.4% | +26216 | 2.2% | +4549 |
| Tyler Badie (DEN) | RB | 100% | 0 TD / 4 g (7 tgt, 5 car) | 8.6% | +1065 | +1205 | 0.3% | +30203 | 2.0% | +4893 |
| Tory Horton (SEA) | WR | 100% | 1 TD / 2 g (4 tgt, 0 car) | 7.9% | +1163 | +1315 | 0.2% | +40716 | 1.9% | +5255 |
| Marvin Mims Jr. (DEN) | WR | 100% | 0 TD / 2 g (5 tgt, 1 car) | 6.2% | +1506 | +1699 | 0.2% | +47519 | 1.5% | +6523 |
| Sam Darnold (SEA) | QB | 100% | 0 TD / 4 g (0 tgt, 5 car) | 6.0% | +1557 | +1756 | 0.2% | +57043 | 1.4% | +6868 |
| Lil'Jordan Humphrey (DEN) | WR | 100% | 0 TD / 2 g (3 tgt, 0 car) | 5.8% | +1638 | +1846 | 0.1% | +79900 | 1.3% | +7387 |
| Eric Saubert (SEA) | TE | 100% | 1 TD / 2 g (3 tgt, 0 car) | 5.7% | +1647 | +1856 | 0.2% | +48680 | 1.4% | +7280 |

**Quarterback passing TDs** (not priced in the feed)

| QB | Mean | 1+ | 2+ | 3+ |
|---|---|---|---|---|
| Bo Nix | 1.22 | 73% (-269) | 35% (+186) | 11% (+798) |
| Sam Darnold | 1.36 | 76% (-325) | 41% (+145) | 14% (+590) |

**Sneaky TD longshots the model likes** (anytime 8% to 30%, role-based, not price-based): 
AJ Barner 25% (fair +305, take at +353 or better); Courtland Sutton 24% (fair +310, take at +359 or better); Jaylen Waddle 22% (fair +348, take at +402 or better); George Holani 21% (fair +370, take at +427 or better); RJ Harvey 21% (fair +383, take at +440 or better); Rashid Shaheed 17% (fair +501, take at +573 or better); Evan Engram 16% (fair +539, take at +615 or better); Cooper Kupp 15% (fair +550, take at +628 or better); Bo Nix 14% (fair +628, take at +715 or better); Troy Franklin 10% (fair +898, take at +1018 or better); Nate Adkins 9% (fair +1017, take at +1151 or better); Tyler Badie 9% (fair +1065, take at +1205 or better)


## Parlays (same game, joint simulation)

Legs are the model-favoured side of each posted DraftKings line (only legs that cleared the single-bet gate, 3+ games of season support), anytime-TD legs, QB 2+ passing TDs and game legs. Hit probability is the joint simulation after the same 50/50 shrink the singles get; 'Raw sim' is before it. Fair odds, not book prices: a same-game parlay at a book usually pays less than the product of the legs, so only take it at or better than the 'play at' price. 'Uplift' = joint / product of legs (above 1.0 = the legs move together).

### Safest (highest chance to hit)
2 to 3 legs: the highest-probability posted lines, QB 1+ passing TD (the one market where the model beat the books in W4: log loss 0.647 vs 0.673) and game legs.

| Legs | Hit probability | Raw sim | Fair odds | Play at or better | Uplift |
|---|---|---|---|---|---|
| Sam Darnold pass TD 1+ + Bo Nix pass TD 1+ | 56.1% | 56.1% | -128 | -100 | 1.01 |
| J.K. Dobbins rec U1.5 + Sam Darnold pass TD 1+ | 48.2% | 58.3% | +107 | +132 | 1.00 |
| Sam Darnold pass TD 1+ + SEA to win | 48.0% | 48.0% | +108 | +133 | 1.14 |

### Mid-tier (more pay)
3 legs, mixing posted-line legs with a touchdown or game leg.

| Legs | Hit probability | Raw sim | Fair odds | Play at or better | Uplift |
|---|---|---|---|---|---|
| George Holani rush_att O4.5 + J.K. Dobbins rec U1.5 + Sam Darnold rush_att U2.5 | 23.8% | 41.1% | +321 | +371 | 1.02 |
| J.K. Dobbins rec U1.5 + Sam Darnold rush_att U2.5 + Rashid Shaheed rec O1.5 | 23.8% | 40.0% | +321 | +371 | 1.01 |
| J.K. Dobbins rec U1.5 + Jaylen Waddle rec U4.5 + Bo Nix pass_cmp U21.5 | 23.6% | 40.8% | +325 | +375 | 1.13 |

### Aggressive (longer shot, model likes)
3 to 4 legs with at least one touchdown leg, ranked by hit probability inside a 2.5-8% band (ranking by uplift alone picked incoherent shootout scenarios).

| Legs | Hit probability | Raw sim | Fair odds | Play at or better | Uplift |
|---|---|---|---|---|---|
| Courtland Sutton rec U3.5 + Jaylen Waddle anytime TD + Bo Nix pass TD 2+ | 8.0% | 9.0% | +1150 | +1300 | 1.79 |
| J.K. Dobbins rec U1.5 + Emanuel Wilson anytime TD + Sam Darnold pass TD 2+ + SEA -2.5 | 8.0% | 9.7% | +1150 | +1300 | 1.53 |
| George Holani rush_yds O13.5 + Bo Nix pass_att U34.5 + Jaylen Waddle rec_yds U45.5 + Sam Darnold pass TD 2+ | 8.0% | 13.9% | +1150 | +1300 | 0.97 |

## Line movement since open (DraftKings via ESPN)

| Player | Market | Open | Now |
|---|---|---|---|
| Bo Nix | pass_yds | 212.5 | 198.5 |
| Tory Horton | rec_yds | 7.5 | 1.5 |
| Jaylen Waddle | rec_yds | 51.5 | 45.5 |
| Emanuel Wilson | rush_yds | 62.5 | 67.5 |
| Lil'Jordan Humphrey | rec_yds | 7.5 | 3.5 |
| Courtland Sutton | rec_yds | 35.5 | 31.5 |
| Jaxon Smith-Njigba | rec_yds | 88.5 | 92.5 |
| AJ Barner | rec_yds | 22.5 | 26.5 |

Book prices (and any anytime/first TD prices) were not available. Send a screenshot of the DraftKings board for this game and I will re-price every pick against the real number.
