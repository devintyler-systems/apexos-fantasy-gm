# Thursday night deep dive: TB @ DAL, Week 5 2026 (kickoff 2026-10-08 20:15 ET)

- **MAIN** = mean of the simulated outcome among games the player plays, MARKET-ANCHORED track (nflverse spread/total as the team-points prior), run `2026_w05_market_20261008T230223Z`. Model-only main (ratings + weather, no lines), run `2026_w05_model_20261008T230224Z`, sits beside it.
- **FLOOR / CEILING** = 10th / 90th percentile of the same 20,000 correlated simulations: a game that goes worse or better than expected for that player. Both are conditional on the player being active; availability is shown separately. A floor of 0 on touchdowns means at least 10% of simulated games end with none.
- **Book columns** come from NFL_Week5_Odds.xlsx (snapshot 22:10 to 22:15Z) and the Add-On workbook (22:37 to 22:42Z), US Pacific converted +7h to UTC; lines may have moved. Best price = the best Over (or Under) among 12 books at the main line (the line with the most feeds, ties to the price closest to even). Gap = model P(over) minus book no-vig P(over), in points, and it is diagnostic, not an edge. Probabilities above 85% or below 15% are shown as n/a (cap).
- **The model runs low on counts and yardage versus the books** (receptions, attempts, completions, yards), so Over gaps are biased negative. TB passing is overprojected (see the cautions).
- Anytime and first-TD no-vig numbers are a flat 10% haircut on a one-sided market, labeled Estimated, and one-signed by construction. No pick here is labeled edge or confident.

## Game

| Track | Winner (win prob) | TB pts: mean / P10-P90 | DAL pts: mean / P10-P90 | Total: mean / P10-P90 |
|---|---|---|---|---|
| Market-anchored | DAL 75% | 19.5 / 9-31 | 29.0 / 16-44 | 48.5 / 30-67 |
| Model-only | DAL 65% | 23.0 / 10-37 | 28.5 / 14-43 | 51.5 / 33-71 |

Books: DAL -8.5 (range -9.5 to -8.5), total 48.5 (range 48.5 to 49.5).

## Availability and data conflicts

- Baker Mayfield (TB QB1) is Out on the NFL report (thumb) and Out on DK. Jalon Daniels starts.
- DK lists Emari Demercado (DAL RB) and Camden Brown (DAL WR) OUT while nflverse has no row for either; the model had Demercado active, so he is excluded here. Jonathan Mingo (DAL WR) is Questionable on the NFL report (DNP, illness) with DK blank: the model has him at 50%.
- CeeDee Lamb: Full participation, thigh designation (model 95% active); DK blank. nflverse has no Thursday report and no inactives list yet.

## Summary tables (MAIN projection; floor-ceiling in brackets)

**Quarterbacks**

| Player | Att | Cmp | Pass yds | Pass TD | INT | Rush att | Rush yds | Anytime TD | First TD | DK pts |
|---|---|---|---|---|---|---|---|---|---|---|
| Dak Prescott (DAL) | 31.8 | 22.3 | 229 [138-333] | 1.91 [0-4] | 0.50 | 2.3 | 9 [0-23] | 11.7% | 2.4% | 18.3 [9-29] |
| Jalon Daniels (TB) | 34.1 | 22.9 | 251 [155-360] | 1.12 [0-2] | 0.82 | 2.5 | 15 [0-35] | 8.9% | 1.7% | 16.2 [8-27] |

**Running backs**

| Player | Rush att | Rush yds | Rush TD | Tgt | Rec | Rec yds | Rec TD | Scrimmage yds | Total TD | Anytime TD | First TD | DK pts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Javonte Williams (DAL) | 14.5 | 53 [22-92] | 0.79 | 3.7 | 2.8 | 17 [1-35] | 0.23 | 70 [34-112] | 1.02 | 66.1% | 19.5% | 16.0 [7-26] |
| Bucky Irving (TB) | 13.0 | 62 [29-103] | 0.37 | 3.6 | 2.8 | 22 [2-47] | 0.16 | 85 [44-132] | 0.53 | 42.0% | 9.8% | 14.7 [7-24] |
| Kenny Gainwell (TB) | 3.7 | 16 [1-36] | 0.10 | 3.1 | 2.4 | 18 [0-40] | 0.13 | 34 [9-64] | 0.23 | 20.5% | 4.2% | 7.1 [2-13] |
| Tyler Goodson (DAL) | 3.8 | 14 [1-33] | 0.13 | 0.7 | 0.6 | 4 [0-13] | 0.03 | 18 [3-39] | 0.16 | 15.2% | 3.1% | 3.3 [0-8] |

**Receivers (WR/TE)** (rushing shown where the model projects any)

| Player | Tgt | Rec | Rec yds | Rec TD | Rush att / yds | Anytime TD | First TD | DK pts |
|---|---|---|---|---|---|---|---|---|
| CeeDee Lamb (DAL WR) | 9.1 | 6.3 [3-10] | 78 [28-137] | 0.54 | 0.4 / 1 | 43.2% | 10.5% | 18.2 [8-31] |
| George Pickens (DAL WR) | 7.2 | 4.8 [2-8] | 59 [16-111] | 0.38 |  | 32.1% | 7.2% | 13.4 [5-24] |
| Emeka Egbuka (TB WR) | 6.9 | 4.1 [2-7] | 54 [13-103] | 0.22 |  | 20.6% | 4.2% | 11.3 [4-21] |
| Cade Otton (TB TE) | 7.0 | 4.8 [2-8] | 50 [15-92] | 0.21 |  | 18.8% | 3.7% | 11.2 [4-20] |
| Ryan Flournoy (DAL WR) | 4.8 | 3.2 [1-6] | 32 [5-65] | 0.34 |  | 29.0% | 6.4% | 8.4 [2-16] |
| Chris Godwin Jr. (TB WR) | 5.2 | 3.4 [1-6] | 38 [7-76] | 0.12 | 0.3 / 2 | 12.1% | 2.4% | 8.2 [2-15] |
| Jake Ferguson (DAL TE) | 4.4 | 3.3 [1-6] | 28 [4-56] | 0.30 |  | 26.2% | 5.7% | 7.9 [2-15] |
| Ted Hurst III (TB WR) | 4.1 | 2.6 [1-5] | 35 [1-75] | 0.14 |  | 12.8% | 2.5% | 7.0 [1-14] |
| Tez Johnson (TB WR) | 2.3 | 1.4 [0-3] | 19 [0-48] | 0.09 | 0.3 / 1 | 9.8% | 1.9% | 4.1 [0-9] |
| KaVontae Turpin (DAL WR) | 1.5 | 1.0 [0-2] | 12 [0-35] | 0.09 | 0.3 / 1 | 11.0% | 2.2% | 3.0 [0-8] |
| Brevyn Spann-Ford (DAL TE) | 1.1 | 0.8 [0-2] | 8 [0-23] | 0.04 |  | 4.4% | 0.8% | 1.8 [0-5] |

## Quarterbacks: full lines

#### Dak Prescott (DAL QB), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Pass attempts | 26.0 | **31.8** | 38.0 | 32.3 | 34.5 | O +100 BetMGM / U -114 BetOnline.ag | 28% vs 48% | -20 | 7 |
| Completions | 17.0 | **22.3** | 28.0 | 22.6 | 23.5 | O -114 DraftKings / U +100 BetOnline.ag | 38% vs 52% | -13 | 9 |
| Passing yards | 138 | **229** | 333 | 231 | 270.5 | O -112 DraftKings / U -112 DraftKings | 26% vs 50% | -24 | 2 |
| Passing TD | 0.00 | **1.91** | 4.00 | 1.89 |  |  |  |  |  |
| Interceptions | 0.00 | **0.50** | 1.00 | 0.50 |  |  |  |  |  |
| Rush attempts | 0.0 | **2.3** | 5.0 | 2.3 | 3.5 | O +115 Hard Rock Bet / U -146 DraftKings | 22% vs 44% | -22 | 3 |
| Rush yards | 0 | **9** | 23 | 9 | 9.5 | O -111 DraftKings / U -110 BetMGM | 33% vs 50% | -17 | 5 |
| Rush TD | 0.00 | **0.12** | 1.00 | 0.12 |  |  |  |  |  |
| DraftKings points | 8.7 | **18.3** | 29.3 | 18.3 | | | | | |
| Anytime TD (rush/rec) | model 11.7% (x availability 11.7%) | | | | | best +525 BetMGM | vig-in 16.0%; Estimated no-vig 15.0% | -3.3 | 6 |
| First TD scorer | model 2.4% (x availability 2.4%) | | | | | best +2800 Bally Bet | vig-in 3.4%; Estimated no-vig 3.5% | -1.1 | 6 |

#### Jalon Daniels (TB QB), availability 100%
> Caution: role mismatch with books (books: 182.5 pass yds / 28.5 att / 44.5 rush yds; model 250 / 33 / 15).
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Pass attempts | 28.0 | **34.1** | 40.0 | 33.6 | 28.5 | O -115 BetMGM / U -104 DraftKings | n/a (cap) |  | 9 |
| Completions | 17.0 | **22.9** | 29.0 | 22.5 | 17.5 | O -121 betPARX / U +102 DraftKings | n/a (cap) |  | 6 |
| Passing yards | 155 | **251** | 360 | 247 | 182.5 | O -111 DraftKings / U -110 BetOnline.ag | 79% vs 50% | +29 | 4 |
| Passing TD | 0.00 | **1.12** | 2.00 | 1.41 |  |  |  |  |  |
| Interceptions | 0.00 | **0.82** | 2.00 | 0.81 |  |  |  |  |  |
| Rush attempts | 0.0 | **2.5** | 5.0 | 2.6 | 7.5 | O +104 betPARX / U -120 Hard Rock Bet | n/a (cap) |  | 7 |
| Rush yards | 0 | **15** | 35 | 15 | 44.5 | O -112 DraftKings / U -112 DraftKings | n/a (cap) |  | 3 |
| Rush TD | 0.00 | **0.09** | 0.00 | 0.12 |  |  |  |  |  |
| DraftKings points | 7.5 | **16.2** | 26.6 | 17.4 | | | | | |
| Anytime TD (rush/rec) | model 8.9% (x availability 8.9%) | | | | | best +300 DraftKings | vig-in 25.0%; Estimated no-vig 24.3% | -15.4 | 6 |
| First TD scorer | model 1.7% (x availability 1.7%) | | | | | best +2000 theScore Bet | vig-in 4.8%; Estimated no-vig 4.6% | -2.9 | 6 |

## Running backs: rushing, receiving and overall

#### Javonte Williams (DAL RB), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Rush attempts | 9.0 | **14.5** | 20.0 | 14.2 | 16.5 | O -105 theScore Bet / U -115 BetOnline.ag | 30% vs 49% | -19 | 8 |
| Rush yards | 22 | **53** | 92 | 52 | 66.5 | O -111 BetMGM / U -109 DraftKings | 27% vs 50% | -23 | 4 |
| Rush TD | 0.00 | **0.79** | 2.00 | 0.77 |  |  |  |  |  |
| Targets | 1.0 | **3.7** | 7.0 | 3.7 |  |  |  |  |  |
| Receptions | 1.0 | **2.8** | 5.0 | 2.8 | 2.5 | O -122 betPARX / U +110 theScore Bet | 51% vs 53% | -2 | 11 |
| Receiving yards | 1 | **17** | 35 | 17 | 14.5 | O -107 DraftKings / U -112 BetRivers | 47% vs 50% | -3 | 4 |
| Receiving TD | 0.00 | **0.23** | 1.00 | 0.23 |  |  |  |  |  |
| **Overall: scrimmage yards** | 34 | **70** | 112 | 69 | | | | | |
| **Overall: total TD** | 0 | **1.02** | 2 | 0.99 | | | | | |
| DraftKings points | 6.8 | **16.0** | 26.3 | 15.8 | | | | | |
| Anytime TD (rush/rec) | model 66.1% (x availability 66.1%) | | | | | best -185 BetMGM | vig-in 64.9%; Estimated no-vig 61.8% | +4.3 | 6 |
| First TD scorer | model 19.5% (x availability 19.5%) | | | | | best +400 Bally Bet | vig-in 20.0%; Estimated no-vig 19.8% | -0.2 | 6 |

#### Bucky Irving (TB RB), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Rush attempts | 8.0 | **13.0** | 18.0 | 13.3 | 13.5 | O -108 DraftKings / U -115 Hard Rock Bet | 43% vs 49% | -6 | 5 |
| Rush yards | 29 | **62** | 103 | 64 | 52.5 | O -113 FanDuel / U -110 BetMGM | 57% vs 50% | +7 | 4 |
| Rush TD | 0.00 | **0.37** | 1.00 | 0.48 |  |  |  |  |  |
| Targets | 1.0 | **3.6** | 6.0 | 3.6 |  |  |  |  |  |
| Receptions | 1.0 | **2.8** | 5.0 | 2.8 | 2.5 | O +140 betPARX / U -158 FanDuel | 52% vs 41% | +11 | 11 |
| Receiving yards | 2 | **22** | 47 | 22 | 13.5 | O -107 DraftKings / U -113 FanDuel | 62% vs 49% | +12 | 4 |
| Receiving TD | 0.00 | **0.16** | 1.00 | 0.21 |  |  |  |  |  |
| **Overall: scrimmage yards** | 44 | **85** | 132 | 86 | | | | | |
| **Overall: total TD** | 0 | **0.53** | 1 | 0.68 | | | | | |
| DraftKings points | 6.7 | **14.7** | 24.1 | 15.8 | | | | | |
| Anytime TD (rush/rec) | model 42.0% (x availability 42.0%) | | | | | best +200 BetMGM | vig-in 33.3%; Estimated no-vig 31.3% | +10.7 | 6 |
| First TD scorer | model 9.8% (x availability 9.8%) | | | | | best +1200 DraftKings | vig-in 7.7%; Estimated no-vig 7.7% | +2.1 | 6 |

#### Kenny Gainwell (TB RB), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Rush attempts | 1.0 | **3.7** | 7.0 | 3.8 | 3.5 | O +100 Fliff / U -145 Fliff | 49% vs 46% | +3 | 1 |
| Rush yards | 1 | **16** | 36 | 17 | 12.5 | O -109 DraftKings / U -113 FanDuel | 48% vs 49% | -2 | 5 |
| Rush TD | 0.00 | **0.10** | 0.00 | 0.13 |  |  |  |  |  |
| Targets | 1.0 | **3.1** | 6.0 | 3.1 |  |  |  |  |  |
| Receptions | 0.0 | **2.4** | 5.0 | 2.4 | 1.5 | O -164 BetOnline.ag / U +141 DraftKings | 66% vs 60% | +6 | 11 |
| Receiving yards | 0 | **18** | 40 | 18 | 11.5 | O -110 BetMGM / U -107 DraftKings | 58% vs 50% | +8 | 3 |
| Receiving TD | 0.00 | **0.13** | 1.00 | 0.17 |  |  |  |  |  |
| **Overall: scrimmage yards** | 9 | **34** | 64 | 34 | | | | | |
| **Overall: total TD** | 0 | **0.23** | 1 | 0.29 | | | | | |
| DraftKings points | 2.0 | **7.1** | 13.3 | 7.5 | | | | | |
| Anytime TD (rush/rec) | model 20.5% (x availability 20.5%) | | | | | best +475 DraftKings | vig-in 17.4%; Estimated no-vig 16.2% | +4.3 | 6 |
| First TD scorer | model 4.2% (x availability 4.2%) | | | | | best +3500 DraftKings | vig-in 2.8%; Estimated no-vig 3.2% | +1.0 | 6 |

#### Tyler Goodson (DAL RB), availability 95%
> Availability 95%: the NFL report has this player listed; every number below is conditional on playing.
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Rush attempts | 1.0 | **3.8** | 7.0 | 3.7 | 4.5 | O +105 Fliff / U -150 Fliff | 33% vs 45% | -12 | 1 |
| Rush yards | 1 | **14** | 33 | 14 | 14.5 | O -108 DraftKings / U -110 BetRivers | 36% vs 50% | -14 | 5 |
| Rush TD | 0.00 | **0.13** | 1.00 | 0.13 |  |  |  |  |  |
| Targets | 0.0 | **0.7** | 2.0 | 0.8 |  |  |  |  |  |
| Receptions | 0.0 | **0.6** | 2.0 | 0.6 |  |  |  |  |  |
| Receiving yards | 0 | **4** | 13 | 4 |  |  |  |  |  |
| Receiving TD | 0.00 | **0.03** | 0.00 | 0.03 |  |  |  |  |  |
| **Overall: scrimmage yards** | 3 | **18** | 39 | 18 | | | | | |
| **Overall: total TD** | 0 | **0.16** | 1 | 0.16 | | | | | |
| DraftKings points | 0.3 | **3.3** | 7.9 | 3.3 | | | | | |
| Anytime TD (rush/rec) | model 15.2% (x availability 14.4%) | | | | | best +650 DraftKings | vig-in 13.3%; Estimated no-vig 12.0% | +3.2 | 6 |
| First TD scorer | model 3.1% (x availability 3.0%) | | | | | best +4500 DraftKings | vig-in 2.2%; Estimated no-vig 2.2% | +0.9 | 6 |

## Wide receivers and tight ends: receiving (and rushing where projected)

#### CeeDee Lamb (DAL WR), availability 95%
> Availability 95%: the NFL report has this player listed; every number below is conditional on playing.
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 5.0 | **9.1** | 13.0 | 9.2 |  |  |  |  |  |
| Receptions | 3.0 | **6.3** | 10.0 | 6.4 | 6.5 | O +100 betPARX / U -108 BetOnline.ag | 44% vs 49% | -6 | 11 |
| Receiving yards | 28 | **78** | 137 | 79 | 84.5 | O -114 DraftKings / U -110 DraftKings | 37% vs 50% | -13 | 4 |
| Receiving TD | 0.00 | **0.54** | 1.00 | 0.53 |  |  |  |  |  |
| Rush attempts | 0.0 | **0.4** | 1.0 | 0.3 |  |  |  |  |  |
| Rush yards | 0 | **1** | 4 | 1 |  |  |  |  |  |
| Rush TD | 0.00 | **0.01** | 0.00 | 0.01 |  |  |  |  |  |
| DraftKings points | 7.6 | **18.2** | 31.1 | 18.4 | | | | | |
| Anytime TD (rush/rec) | model 43.2% (x availability 41.0%) | | | | | best -111 BetMGM | vig-in 52.6%; Estimated no-vig 48.8% | -5.6 | 6 |
| First TD scorer | model 10.5% (x availability 9.9%) | | | | | best +575 Bally Bet | vig-in 14.8%; Estimated no-vig 13.8% | -3.4 | 6 |

#### George Pickens (DAL WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 4.0 | **7.2** | 11.0 | 7.3 |  |  |  |  |  |
| Receptions | 2.0 | **4.8** | 8.0 | 4.8 | 4.5 | O -115 betPARX / U +110 theScore Bet | 51% vs 53% | -2 | 11 |
| Receiving yards | 16 | **59** | 111 | 60 | 63.5 | O -113 FanDuel / U -113 FanDuel | 39% vs 50% | -11 | 2 |
| Receiving TD | 0.00 | **0.38** | 1.00 | 0.37 |  |  |  |  |  |
| DraftKings points | 4.6 | **13.4** | 24.4 | 13.4 | | | | | |
| Anytime TD (rush/rec) | model 32.1% (x availability 32.1%) | | | | | best +125 BetMGM | vig-in 44.4%; Estimated no-vig 42.9% | -10.7 | 6 |
| First TD scorer | model 7.2% (x availability 7.2%) | | | | | best +775 BetMGM | vig-in 11.4%; Estimated no-vig 11.2% | -4.0 | 6 |

#### Emeka Egbuka (TB WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 3.0 | **6.9** | 11.0 | 6.8 |  |  |  |  |  |
| Receptions | 2.0 | **4.1** | 7.0 | 4.1 | 3.5 | O +130 BetMGM / U -135 theScore Bet | 58% vs 44% | +14 | 10 |
| Receiving yards | 13 | **54** | 103 | 54 | 35.5 | O -109 DraftKings / U -113 FanDuel | 65% vs 50% | +15 | 2 |
| Receiving TD | 0.00 | **0.22** | 1.00 | 0.28 |  |  |  |  |  |
| DraftKings points | 3.6 | **11.3** | 21.1 | 11.6 | | | | | |
| Anytime TD (rush/rec) | model 20.6% (x availability 20.6%) | | | | | best +290 BetMGM | vig-in 25.6%; Estimated no-vig 25.0% | -4.4 | 6 |
| First TD scorer | model 4.2% (x availability 4.2%) | | | | | best +1900 DraftKings | vig-in 5.0%; Estimated no-vig 4.8% | -0.6 | 6 |

#### Cade Otton (TB TE), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 3.0 | **7.0** | 11.0 | 6.9 |  |  |  |  |  |
| Receptions | 2.0 | **4.8** | 8.0 | 4.7 | 3.5 | O +102 FanDuel / U -114 BetOnline.ag | 69% vs 49% | +20 | 11 |
| Receiving yards | 15 | **50** | 92 | 49 | 29.5 | O -113 FanDuel / U -105 BetMGM | 71% vs 51% | +21 | 4 |
| Receiving TD | 0.00 | **0.21** | 1.00 | 0.25 |  |  |  |  |  |
| DraftKings points | 4.0 | **11.2** | 20.1 | 11.4 | | | | | |
| Anytime TD (rush/rec) | model 18.8% (x availability 18.8%) | | | | | best +500 DraftKings | vig-in 16.7%; Estimated no-vig 15.9% | +2.9 | 6 |
| First TD scorer | model 3.7% (x availability 3.7%) | | | | | best +3000 DraftKings | vig-in 3.2%; Estimated no-vig 3.3% | +0.5 | 6 |

#### Ryan Flournoy (DAL WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 2.0 | **4.8** | 8.0 | 4.8 |  |  |  |  |  |
| Receptions | 1.0 | **3.2** | 6.0 | 3.2 | 3.5 | O +130 Bovada / U -148 FanDuel | 38% vs 43% | -4 | 11 |
| Receiving yards | 5 | **32** | 65 | 32 | 30.5 | O -110 DraftKings / U -114 DraftKings | 43% vs 50% | -6 | 2 |
| Receiving TD | 0.00 | **0.34** | 1.00 | 0.34 |  |  |  |  |  |
| DraftKings points | 1.8 | **8.4** | 15.8 | 8.5 | | | | | |
| Anytime TD (rush/rec) | model 29.0% (x availability 29.0%) | | | | | best +310 FanDuel | vig-in 24.4%; Estimated no-vig 22.5% | +6.5 | 6 |
| First TD scorer | model 6.4% (x availability 6.4%) | | | | | best +1600 DraftKings | vig-in 5.9%; Estimated no-vig 5.5% | +1.0 | 6 |

#### Chris Godwin Jr. (TB WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 2.0 | **5.2** | 9.0 | 5.1 |  |  |  |  |  |
| Receptions | 1.0 | **3.4** | 6.0 | 3.4 | 3.5 | O -134 betPARX / U +115 BetOnline.ag | 44% vs 55% | -12 | 11 |
| Receiving yards | 7 | **38** | 76 | 37 | 34.5 | O -110 DraftKings / U -110 Bovada | 47% vs 50% | -3 | 3 |
| Receiving TD | 0.00 | **0.12** | 1.00 | 0.15 |  |  |  |  |  |
| Rush attempts | 0.0 | **0.3** | 1.0 | 0.3 |  |  |  |  |  |
| Rush yards | 0 | **2** | 5 | 2 |  |  |  |  |  |
| Rush TD | 0.00 | **0.01** | 0.00 | 0.01 |  |  |  |  |  |
| DraftKings points | 2.1 | **8.2** | 15.0 | 8.3 | | | | | |
| Anytime TD (rush/rec) | model 12.1% (x availability 12.1%) | | | | | best +450 BetMGM | vig-in 18.2%; Estimated no-vig 19.6% | -7.5 | 6 |
| First TD scorer | model 2.4% (x availability 2.4%) | | | | | best +2800 Bally Bet | vig-in 3.4%; Estimated no-vig 3.9% | -1.5 | 6 |

#### Jake Ferguson (DAL TE), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 2.0 | **4.4** | 8.0 | 4.5 |  |  |  |  |  |
| Receptions | 1.0 | **3.3** | 6.0 | 3.3 | 3.5 | O +115 Bovada / U -130 betPARX | 41% vs 46% | -4 | 11 |
| Receiving yards | 4 | **28** | 56 | 28 | 25.5 | O -111 DraftKings / U -113 DraftKings | 46% vs 50% | -4 | 2 |
| Receiving TD | 0.00 | **0.30** | 1.00 | 0.29 |  |  |  |  |  |
| DraftKings points | 1.8 | **7.9** | 14.9 | 7.9 | | | | | |
| Anytime TD (rush/rec) | model 26.2% (x availability 26.2%) | | | | | best +225 BetMGM | vig-in 30.8%; Estimated no-vig 28.6% | -2.4 | 6 |
| First TD scorer | model 5.7% (x availability 5.7%) | | | | | best +1200 BetMGM | vig-in 7.7%; Estimated no-vig 7.5% | -1.8 | 6 |

#### Ted Hurst III (TB WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 1.0 | **4.1** | 7.0 | 4.0 |  |  |  |  |  |
| Receptions | 1.0 | **2.6** | 5.0 | 2.5 | 1.5 | O +115 theScore Bet / U -118 betPARX | 70% vs 47% | +23 | 11 |
| Receiving yards | 1 | **35** | 75 | 35 | 16.5 | O -113 FanDuel / U -113 FanDuel | 69% vs 50% | +19 | 4 |
| Receiving TD | 0.00 | **0.14** | 1.00 | 0.17 |  |  |  |  |  |
| DraftKings points | 1.3 | **7.0** | 13.8 | 7.1 | | | | | |
| Anytime TD (rush/rec) | model 12.8% (x availability 12.8%) | | | | | best +550 DraftKings | vig-in 15.4%; Estimated no-vig 14.8% | -2.0 | 6 |
| First TD scorer | model 2.5% (x availability 2.5%) | | | | | best +4000 DraftKings | vig-in 2.4%; Estimated no-vig 2.5% | -0.1 | 6 |

#### Tez Johnson (TB WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 0.0 | **2.3** | 5.0 | 2.3 |  |  |  |  |  |
| Receptions | 0.0 | **1.4** | 3.0 | 1.4 | 1.5 | O +145 betPARX / U -156 BetOnline.ag | 41% vs 41% | +0 | 11 |
| Receiving yards | 0 | **19** | 48 | 19 | 12.5 | O -111 DraftKings / U +105 BetMGM | 51% vs 51% | -0 | 4 |
| Receiving TD | 0.00 | **0.09** | 0.00 | 0.12 |  |  |  |  |  |
| Rush attempts | 0.0 | **0.3** | 1.0 | 0.3 |  |  |  |  |  |
| Rush yards | 0 | **1** | 5 | 2 |  |  |  |  |  |
| Rush TD | 0.00 | **0.01** | 0.00 | 0.01 |  |  |  |  |  |
| DraftKings points | 0.0 | **4.1** | 9.4 | 4.2 | | | | | |
| Anytime TD (rush/rec) | model 9.8% (x availability 9.8%) | | | | | best +700 DraftKings | vig-in 12.5%; Estimated no-vig 11.2% | -1.4 | 6 |
| First TD scorer | model 1.9% (x availability 1.9%) | | | | | best +5000 theScore Bet | vig-in 2.0%; Estimated no-vig 2.2% | -0.3 | 6 |

#### KaVontae Turpin (DAL WR), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 0.0 | **1.5** | 3.0 | 1.5 |  |  |  |  |  |
| Receptions | 0.0 | **1.0** | 2.0 | 1.0 | 0.5 | O -108 FanDuel / U -117 DraftKings | 58% vs 49% | +9 | 5 |
| Receiving yards | 0 | **12** | 35 | 12 | 0.5 | O -103 DraftKings / U -122 DraftKings | 58% vs 48% | +10 | 2 |
| Receiving TD | 0.00 | **0.09** | 0.00 | 0.09 |  |  |  |  |  |
| Rush attempts | 0.0 | **0.3** | 1.0 | 0.3 |  |  |  |  |  |
| Rush yards | 0 | **1** | 4 | 1 |  |  |  |  |  |
| Rush TD | 0.00 | **0.03** | 0.00 | 0.03 |  |  |  |  |  |
| DraftKings points | 0.0 | **3.0** | 7.8 | 3.0 | | | | | |
| Anytime TD (rush/rec) | model 11.0% (x availability 11.0%) | | | | | best +950 BetMGM | vig-in 9.5%; Estimated no-vig 9.2% | +1.8 | 6 |
| First TD scorer | model 2.2% (x availability 2.2%) | | | | | best +5000 theScore Bet | vig-in 2.0%; Estimated no-vig 2.3% | -0.1 | 6 |

#### Brevyn Spann-Ford (DAL TE), availability 100%
| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |
|---|---|---|---|---|---|---|---|---|---|
| Targets | 0.0 | **1.1** | 3.0 | 1.2 |  |  |  |  |  |
| Receptions | 0.0 | **0.8** | 2.0 | 0.8 | 0.5 | O -130 DraftKings / U +102 DraftKings | 52% vs 53% | -1 | 3 |
| Receiving yards | 0 | **8** | 23 | 8 | 4.5 | O -111 BetMGM / U -106 FanDuel | 42% vs 50% | -8 | 3 |
| Receiving TD | 0.00 | **0.04** | 0.00 | 0.05 |  |  |  |  |  |
| DraftKings points | 0.0 | **1.8** | 5.3 | 1.9 | | | | | |
| Anytime TD (rush/rec) | model 4.4% (x availability 4.4%) | | | | | best +850 DraftKings | vig-in 10.5%; Estimated no-vig 9.6% | -5.2 | 6 |
| First TD scorer | model 0.8% (x availability 0.8%) | | | | | best +4000 Bally Bet | vig-in 2.4%; Estimated no-vig 2.5% | -1.7 | 5 |

## Top 15 Anytime TD (rush or receiving TD; ranked by model probability x availability)

| # | Player | Model (if active / x avail.) | Targets / carries | Why (usage, red zone) | Best price | Book vig-in | Book est. no-vig | Gap (diag.) |
|---|---|---|---|---|---|---|---|---|
| 1 | Javonte Williams (DAL RB) | 66.1% / 66.1% | 3.7 / 14.5 | tgt_sh 10.5%; team att 34.2; opp DvP 1.00; RZ tgt 3; car_sh 56.3%; team rush 25.0; opp d_ypc 0.88; inside-10 car 13 | -185 BetMGM | 64.9% | 61.8% | +4.3 |
| 2 | Bucky Irving (TB RB) | 42.0% / 42.0% | 3.6 / 13.0 | tgt_sh 10.6%; team att 34.1; opp DvP 0.93; RZ tgt 4; car_sh 52.9%; team rush 24.0; opp d_ypc 1.08; inside-10 car 1 | +200 BetMGM | 33.3% | 31.3% | +10.7 |
| 3 | CeeDee Lamb (DAL WR) | 43.2% / 41.0% | 9.1 / 0.4 | tgt_sh 26.1%; team att 34.2; opp DvP 1.04; RZ tgt 6 | -111 BetMGM | 52.6% | 48.8% | -5.6 |
| 4 | George Pickens (DAL WR) | 32.1% / 32.1% | 7.2 / 0.0 | tgt_sh 20.2%; team att 34.2; opp DvP 1.04; RZ tgt 3 | +125 BetMGM | 44.4% | 42.9% | -10.7 |
| 5 | Ryan Flournoy (DAL WR) | 29.0% / 29.0% | 4.8 / 0.0 | tgt_sh 13.4%; team att 34.2; opp DvP 1.04; RZ tgt 5 | +310 FanDuel | 24.4% | 22.5% | +6.5 |
| 6 | Jake Ferguson (DAL TE) | 26.2% / 26.2% | 4.4 / 0.0 | tgt_sh 12.6%; team att 34.2; opp DvP 1.04; RZ tgt 4 | +225 BetMGM | 30.8% | 28.6% | -2.4 |
| 7 | Emeka Egbuka (TB WR) | 20.6% / 20.6% | 6.9 / 0.2 | tgt_sh 20.2%; team att 34.1; opp DvP 0.90; RZ tgt 3 | +290 BetMGM | 25.6% | 25.0% | -4.4 |
| 8 | Kenny Gainwell (TB RB) | 20.5% / 20.5% | 3.1 / 3.7 | tgt_sh 9.1%; team att 34.1; opp DvP 0.93; RZ tgt 3; car_sh 14.9%; team rush 24.0; opp d_ypc 1.08; inside-10 car 0 | +475 DraftKings | 17.4% | 16.2% | +4.3 |
| 9 | Cade Otton (TB TE) | 18.8% / 18.8% | 7.0 / 0.0 | tgt_sh 18.5%; team att 34.1; opp DvP 1.11; RZ tgt 2 | +500 DraftKings | 16.7% | 15.9% | +2.9 |
| 10 | Tyler Goodson (DAL RB) | 15.2% / 14.4% | 0.7 / 3.8 | car_sh 14.6%; team rush 25.0; opp d_ypc 0.88; inside-10 car 0 | +650 DraftKings | 13.3% | 12.0% | +3.2 |
| 11 | Ted Hurst III (TB WR) | 12.8% / 12.8% | 4.1 / 0.0 | tgt_sh 12.1%; team att 34.1; opp DvP 0.90; RZ tgt 2 | +550 DraftKings | 15.4% | 14.8% | -2.0 |
| 12 | Chris Godwin Jr. (TB WR) | 12.1% / 12.1% | 5.2 / 0.3 | tgt_sh 15.2%; team att 34.1; opp DvP 0.90; RZ tgt 0 | +450 BetMGM | 18.2% | 19.6% | -7.5 |
| 13 | Dak Prescott (DAL QB) | 11.7% / 11.7% | 0.0 / 2.3 | team att 34.2; ypa 7.09; opp d_ypa 0.98; pass rate 58.9% | +525 BetMGM | 16.0% | 15.0% | -3.3 |
| 14 | KaVontae Turpin (DAL WR) | 11.0% / 11.0% | 1.5 / 0.3 | tgt_sh 4.1%; team att 34.2; opp DvP 1.04; RZ tgt 1 | +950 BetMGM | 9.5% | 9.2% | +1.8 |
| 15 | Tez Johnson (TB WR) | 9.8% / 9.8% | 2.3 / 0.3 | tgt_sh 6.8%; team att 34.1; opp DvP 0.90; RZ tgt 2 | +700 DraftKings | 12.5% | 11.2% | -1.4 |

## Top 5 First TD scorer

| # | Player | Model (if active / x avail.) | Best price | Book vig-in | Book est. no-vig | Gap (diag.) |
|---|---|---|---|---|---|---|
| 1 | Javonte Williams (DAL RB) | 19.5% / 19.5% | +400 Bally Bet | 20.0% | 19.8% | -0.2 |
| 2 | CeeDee Lamb (DAL WR) | 10.5% / 9.9% | +575 Bally Bet | 14.8% | 13.8% | -3.4 |
| 3 | Bucky Irving (TB RB) | 9.8% / 9.8% | +1200 DraftKings | 7.7% | 7.7% | +2.1 |
| 4 | George Pickens (DAL WR) | 7.2% / 7.2% | +775 BetMGM | 11.4% | 11.2% | -4.0 |
| 5 | Ryan Flournoy (DAL WR) | 6.4% / 6.4% | +1600 DraftKings | 5.9% | 5.5% | +1.0 |

## Top bets

**Read this first.** The Week 4 postmortem is the evidence on this model against the books: flagged edges of 5+ points had the model at 57% implied, the market at 45%, and actual results at 44% (n=240), and the model's anytime-TD log loss was worse than the market's (0.4422 vs 0.4373). So nothing below is labeled edge or confident. These are **model-liked shots**: places where our simulation sits well above the books' own pricing, ranked by something that does not depend on the books' vig. Bet them small, as lottery tickets, if at all. The model also runs low on counts and yardage, so I have not recommended any count or yardage prop; TB receiving overs look attractive only because the sim overprojects TB passing (books: Daniels 28.5 attempts, model 34).

**How the ranking works.** The books' anytime-TD implied probabilities sum to 5.12 across the listed players against the model's 4.05 expected scorers, so a flat 10% haircut cannot be right. Instead I compare each player's *share* of the listed field: model share divided by book share (ratio above 1.0 means we like him more than the books do relative to everyone else). Every ratio is the raw model/book probability ratio divided by 0.79 (4.05/5.12): raw ratios are Irving 1.21, Flournoy 1.16, Gainwell 1.14, Goodson 1.14, Turpin 1.07, Otton 1.06, Williams 0.96. The ratio uses the median book's implied probability; Break-even uses the best price. Emari Demercado is left out of the field because DK lists him OUT (ESPN does not list him as Out; his role is tiny). EV is the return per $1 if the model's probability is right; it is not a forecast.

| Shot | Best price | Model | Break-even | Model share / book share | EV if model right | Tier | Why the model likes it | Main risk |
|---|---|---|---|---|---|---|---|---|
| Bucky Irving (TB RB) Anytime TD | +200 BetMGM | 42.0% | 33.3% | 1.53 | +26% | A | 13.0 projected carries (53% share) and 3.6 targets; 4 targets inside the 20 so far this season (season-to-date count, not a projection); model-only track has him higher (50.9%) | TB is an 8.5 to 9.5-point underdog (books -8.5 to -9.5); only 1 inside-10 carry so far this season |
| Ryan Flournoy (DAL WR) Anytime TD | +310 FanDuel | 29.0% | 24.4% | 1.47 | +19% | A | 4.8 projected targets, DAL projected 29 points; 5 targets inside the 20 so far this season (season-to-date count, not a projection) | WR3 volume is small; one catch from a miss |
| Kenny Gainwell (TB RB) Anytime TD | +475 DraftKings | 20.5% | 17.4% | 1.44 | +18% | B | 3.7 projected carries plus 3.1 targets; 3 targets inside the 20 so far this season | Thin role; depends on TB scoring plays |
| Cade Otton (TB TE) Anytime TD | +500 DraftKings | 18.8% | 16.7% | 1.35 | +13% | B | 7.0 targets, 18.8% anytime | TB passing is overprojected by the sim, so discount |
| Tyler Goodson (DAL RB) Anytime TD | +650 DraftKings | 15.2% | 13.3% | 1.44 | +14% | B | 3.8 projected carries as the DAL change-of-pace back | 95% active (ankle, Full participation); the stake is lost or voided depending on the book if he does not play; 0 inside-10 carries so far this season |
| KaVontae Turpin (DAL WR) Anytime TD | +950 BetMGM | 11.0% | 9.5% | 1.35 | +15% | C | Gadget and returner role, 1.5 targets | Thin and noisy; returner TDs are not in this number |
| *Javonte Williams (DAL RB) Anytime TD* | -185 BetMGM | 66.1% | 64.9% | 1.22 | +2% | fair | model and book agree on the probability; 14.5 projected carries (56% share); 13 inside-10 carries so far this season (season-to-date) | a fair price, not a shot |

Tier A = the projected usage behind the number is concrete (a large carry share, or targets plus season-to-date work inside the 20). Tier B = real but thin or leaning on the TB passing game. Tier C = mostly noise. Williams is the one place model and book agree (66% vs 65% break-even): a fair price, no more.

**First TD longshots the model likes more than the books** (first-TD books carry far more vig than 10%, so the ratio is the honest comparison):

| Shot | Best price | Model | Break-even | Model share / book share | EV if model right |
|---|---|---|---|---|---|
| Bucky Irving First TD | +1200 DraftKings | 9.8% | 7.7% | 1.56 | +28% |
| Ryan Flournoy First TD | +1600 DraftKings | 6.4% | 5.9% | 1.44 | +9% |
| Kenny Gainwell First TD | +3500 DraftKings | 4.2% | 2.8% | 1.59 | +50% |
| Tyler Goodson First TD | +4500 DraftKings | 3.1% | 2.2% | 1.73 | +43% |
| Cade Otton First TD | +3000 DraftKings | 3.7% | 3.2% | 1.39 | +16% |

Irving +1200 has the most behind it of these (9.8% for a back with a 53% projected carry share). Gainwell +3500 and Goodson +4500 are pure lottery tickets: their EV figures rest on 3 to 4% probabilities, so the ratios are unstable (the order changes if you use best-price instead of median-price implied probabilities).

**Where the books are higher than us** (do not use these in parlays; none of this is a bet because you cannot bet an anytime TD under): George Pickens +125 (model 32.1% vs 44.4% break-even), Jalon Daniels +300 (8.9% vs 25.0%), Chris Godwin +450 (12.1% vs 18.2%), Sean Tucker +380 (6.7% vs 20.8%), CeeDee Lamb -111 (43.2% vs 52.6%). The model is below the books on quarterback, wide receiver and tight end touchdowns (Daniels and Tucker are role mismatches, plus Pickens, Godwin and Lamb), and the shots above are mostly what is left over after that normalization: only Irving, Gainwell and Goodson are above the books on raw probability among the backs, and the model's running-back total is below the books for both teams. Dropping Daniels and Tucker from the field lowers every ratio by about 0.08, and also dropping Pickens and Godwin takes Irving to about 1.38 and Otton to about 1.21. The shot list is therefore a relative-value claim, and if the model's passing-game touchdown share is simply too low, several of these are wrong together.

## Parlays

No book prices these same-game parlays in the files, so the payouts below are **the legs' best prices multiplied**, which is more generous than a book will actually pay: books cut same-game parlays, commonly 15% to 30%. I show EV with no cut and with a 20% cut. Joint probabilities come from the simulated joint distribution, not from multiplying legs; the legs here are nearly independent (joint divided by multiplied legs is 0.92 to 1.13), so correlation does not help or hurt much, and the books' cut is pure cost. The multiplied prices combine different books (BetMGM for Irving and Turpin, FanDuel for Flournoy, DraftKings for Gainwell), so no single book offers these parlays and a same-book price will be lower. The 20% cut is applied to the profit. The three- and four-leg joint probabilities rest on few simulated hits (about 490 and 63 of 20,000), so treat their EV as rough, especially the four-leg row.

| Legs | Joint prob (sim) | Multiplied-legs payout | Model fair price | EV if model right, no cut | EV with 20% payout cut | Break-even payout cut |
|---|---|---|---|---|---|---|
| Bucky Irving + Ryan Flournoy | 12.4% | +1,130 | +704 | +53% | +25% | 38% |
| Ryan Flournoy + Kenny Gainwell | 6.2% | +2,258 | +1,526 | +45% | +17% | 32% |
| Bucky Irving + Kenny Gainwell | 7.9% | +1,625 | +1,162 | +37% | +11% | 29% |
| Bucky Irving + Ryan Flournoy + Kenny Gainwell | 2.4% | +6,972 | +3,990 | +73% | +39% | 43% |
| Bucky Irving + Ryan Flournoy + KaVontae Turpin | 1.3% | +12,815 | +7,335 | +74% | +39% | 43% |
| Bucky Irving + Ryan Flournoy + Kenny Gainwell + KaVontae Turpin | 0.3% | +74,161 | +32,158 | +130% | +84% | 57% |

If you take one, the two-leg Irving plus Flournoy is the one with the most behind it: highest joint probability among the shot combinations (12.4%; the Williams plus Lamb pairing is higher but it is not a shot), and it survives a cut of up to 38% before the EV turns negative. The three- and four-leg versions are lottery tickets: they pay more, they hit one time in 40 and one in 300, and every leg needs to be right. I would not build anything bigger than four legs.

**Parlays I would not build:** any leg with Daniels, Godwin or Tucker (books higher than us); Lamb or Williams anytime TD as a leg in a longer parlay (priced at -111 and -185, they add risk and almost no payout); and any parlay that pairs Williams with Lamb (the sim has them at 0.94 times the multiplied-legs probability because they compete for the same touchdowns).

**Correlation plays the books do not price in these files** (model fair prices from the joint simulation; no book number to compare):

| Game | Same-game parlay (all named players active) | Joint probability (sim) | Naive product of legs | Joint fair price | Correlation uplift |
|---|---|---|---|---|---|
| TB@DAL | Javonte Williams anytime TD + CeeDee Lamb anytime TD | 26.7% | 28.5% | +274 | 0.94x |
| TB@DAL | Dak Prescott 2+ pass TD + CeeDee Lamb anytime TD | 34.1% | 25.8% | +193 | 1.32x |
| TB@DAL | DAL wins + Javonte Williams anytime TD | 53.1% | 48.6% | -113 | 1.09x |


Two-plus passing-TD parlays cannot be compared to the books because the files have no passing-TD market.

## Before kickoff and other things worth knowing

- **Official inactives (ESPN game summary, stamped 22:48 to 22:49Z).** Skill players out: Mayfield (TB QB) and Camden Brown (DAL WR). Lamb, Prescott and McLaughlin are not listed as Out (ESPN's game summary has only an injuries list, so "playing" is inferred from absence; Mingo, Questionable on the NFL report, is also not listed). Defense and line out: DAL LB Overshown, CB Durant, LB Houston and OT Cornelius; TB S Winfield, CB Morrison, LB Dennis and G Schrauth. I reran the game with those as manual overrides (sensitivity only; the frozen base run stands): team scores identical, every player's DK points moved by 0.23 or less, anytime-TD probabilities by 0.6 points or less. Both teams lost starters in the secondary, which fits the books putting Prescott at 270.5 passing yards against our 229; I would not move our number on that alone.
- **DK vs ESPN conflict.** DK lists Emari Demercado (DAL RB) OUT; he is not on ESPN's inactive list. He is a $400 depth back and not in any pick here.
- **Where we disagree with the books by the most.** Prescott passing yards (model 229, book 270.5; ceiling P90 333); Daniels passing (model 251, book 182.5) and rushing (model 15, book 44.5); Irving receiving (model 22 yards, book 13.5). When the sim and the books split this far, bet neither side with confidence: one of us has the game script wrong.
- **Game script range.** Total points P10 to P90 is 30 to 67 and DAL's points 16 to 44. A floor outcome for everyone on one team is the same game: if DAL scores 16 or fewer, Lamb, Pickens, Williams and Prescott all hit their floors together.
- **Daniels.** Treat every TB passing and TB receiving number as lower-reliability. Books see him as the smaller passer and bigger runner than our model does.
- **Showdown.** The ceiling lineup built for the $300K contest is in `SHOWDOWN_TB_DAL_2026_W05.md`.
- **Everything here is model output on a snapshot.** Book lines were stamped 22:10 to 22:42Z, so they are about an hour old as of 23:35Z and have likely moved. Confidence in the model's numbers is a reliability index, not a hit probability, and no single-prop probability above 85% is shown.

## Non-TD props: best bets and parlays (added 23:39Z)

**Screen:** model vs book at the main line, centered on the model's known low bias on counts and yardage (diagnostic only, never a calibration), checked against each player's 2026 Weeks 1 to 4 games versus the line, with role flags. Ten props pass. Eight are TB pass-catcher overs that all depend on TB's passing volume, where the sim (34 attempts) and the books (28.5) disagree most, so they are one correlated bet, not eight.

**The only prop that qualifies for a label under the project rule (rush yards, 50/50 blend with the market):**
- **Javonte Williams UNDER 66.5 rush yards, -109 DraftKings.** Model P(under) 73%, book no-vig 50%, blend 61.5%. Weeks 1 to 4: over 66.5 in 1 of 4 games, average 57.8. Model main 53 [22-92]. Even centered on the model's rushing-yards bias the gap is about 17 points. Risk: DAL is a roughly 9-point favorite and could run late; his P90 is 92 yards. A rushing or receiving TD does not hurt this bet (his anytime TD is 66% and comes from short carries).

**Supported by game logs, not by the label rule** (receptions, receiving yards and attempts are markets where the model has not beaten the books):
- Williams UNDER 16.5 rush attempts, -105 theScore (average 15.5, over in 2 of 4). Overlaps the yards bet (correlation 1.13).
- Ted Hurst III OVER 16.5 receiving yards, -113 FanDuel (over in 4 of 4 games, average 32; model 35 [1-75]).
- Cade Otton OVER 29.5 receiving yards, -113 FanDuel (3 of 4, average 39; model 50 [15-92]).
- Bucky Irving OVER 52.5 rush yards, -113 FanDuel (2 of 4, average 60; marginal).

**Parlays.** The model's leg probabilities (about 70%) sit far above the books' 50%, so the raw EV (+80% and more) is not credible. Using the 50/50 blend per leg (Williams under 61.5%, Hurst over 59%, Otton over 61%) and a 20% payout cut:
| Parlay | Blended joint | Multiplied-legs payout | Fair price | EV with 20% cut |
|---|---|---|---|---|
| Williams U66.5 rush yds + Hurst O16.5 rec yds | 36.5% | +261 | +174 | +13% |
| Williams U66.5 + Hurst O16.5 + Otton O29.5 rec yds | 22.3% | +581 | +348 | +40% |

Take either only if the book pays at least the fair price. Excluded: every Daniels prop (role mismatch), every Prescott prop (two feeds on yards, the model is well below the books), and every Lamb, Pickens, Ferguson and Flournoy receiving prop (the model is below the books by more than its usual bias and no game-log support).
