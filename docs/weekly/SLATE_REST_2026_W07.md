# Week 7 2026: full slate predictions

**How to read this.** Two simulation tracks, always labeled: MARKET-ANCHORED (nflverse spread/total as the team-points prior) and MODEL-ONLY (ratings and weather, no lines). Player numbers are the market-anchored track unless stated. Props use DraftKings lines via ESPN: lines only, **no prices and no touchdown prices**. Singles are screened at an assumed -110 after shrinking the model 50/50 toward 50%; touchdown and parlay prices are FAIR odds from the joint simulation, 'play at' adds a 12% cushion. The W4 and W5 postmortems found no edge over the books on yardage and count props and calibrated anytime-TD probabilities, so read everything as a ranked lean. TD v2 multipliers and the anytime-TD floor (0.06, DECISIONS #29-30) are live.

**Inputs used (UTC).** ESPN game-summary Outs (5 names per team cap, not the official inactives): 2026-10-25T17:30:13Z. Sleeper status overlay (newer Out replaces the NFL row): 2026-10-25T17:30:05+00:00. nflverse depth charts: 2026-10-25T12:30:46Z; nflverse injuries: no timestamp in the feed. Lines: ESPN/DraftKings fetched 2026-10-25T17:30Z (no prices; the per-line `last_updated_utc` stamps run ahead of the fetch time and their zone is unverified, so no recency claim is made from them). Official inactives: **not used** (the ESPN feed carries injuries, not the NFL inactive list). Code: git eea7635.

**Started or finished, excluded from picks:** CIN@BAL, CLE@TEN, IND@MIN, MIA@NYJ, NE@CHI, NYG@HOU, PIT@NO, SF@ATL, TB@CAR.

## 1. Predicted scores

| Game | Kickoff ET | Market (spread / total) | Market-anchored score | Win prob | Total | Model-only score | Model-only win | Fair spread |
|---|---|---|---|---|---|---|---|---|
| DEN@ARI | 2026-10-25 16:05 | ARI +4.5 / 43.5 | DEN 24.0, ARI 19.5 | DEN 63% / ARI 37% | 43.5 | DEN 23.4, ARI 21.1 | DEN 57% | ARI +4.0 |
| GB@DET | 2026-10-25 16:25 | DET -3.5 / 55.5 | GB 25.8, DET 29.5 | GB 40% / DET 60% | 55.3 | GB 23.0, DET 27.8 | GB 37% | DET -4.0 |
| LA@LV | 2026-10-25 16:25 | LV +3.5 / 48.5 | LA 25.9, LV 22.4 | LA 61% / LV 39% | 48.3 | LA 24.8, LV 23.3 | LA 55% | LV +4.0 |
| KC@SEA | 2026-10-25 20:20 | SEA -3.0 / 42.5 | KC 19.7, SEA 22.7 | KC 41% / SEA 59% | 42.4 | KC 21.5, SEA 24.1 | KC 43% | SEA -3.0 |
| DAL@PHI | 2026-10-26 20:15 | PHI +4.5 / 43.5 | DAL 23.9, PHI 19.4 | DAL 63% / PHI 37% | 43.3 | DAL 23.1, PHI 23.8 | DAL 48% | PHI +4.0 |

Already played: NE@CHI final NE 24, CHI 30 (market CHI -3.0, total 50.5; projected 23.7-26.7).

Already played: PIT@NO final PIT 16, NO 10 (market NO +3.0, total 43.5; projected 23.1-20.2).

## 2. Team offense (through Week 6, per game)

| team | g | pts | plays | pass_rate | pass_yds | rush_yds | td_per_g | pass_epa | rush_epa | rz_td_pct | turnovers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BUF | 6 | 32.8 | 60 | 49% | 251 | 149 | 3.8 | +0.33 | +0.03 | 67% | 1.5 |
| DET | 5 | 32.8 | 66 | 60% | 297 | 114 | 4.0 | +0.28 | +0.01 | 81% | 0.2 |
| SF | 6 | 29.5 | 57 | 50% | 243 | 128 | 3.7 | +0.36 | +0.01 | 86% | 0.8 |
| CAR | 5 | 29.2 | 68 | 61% | 310 | 109 | 3.2 | +0.20 | -0.05 | 70% | 0.6 |
| KC | 5 | 28.0 | 62 | 52% | 262 | 160 | 3.2 | +0.18 | +0.12 | 56% | 0.6 |
| LV | 6 | 27.0 | 64 | 58% | 272 | 79 | 2.8 | +0.17 | -0.22 | 52% | 1.3 |
| BAL | 6 | 26.0 | 61 | 48% | 233 | 152 | 3.0 | +0.21 | -0.01 | 71% | 0.7 |
| JAX | 6 | 25.7 | 60 | 52% | 247 | 113 | 3.0 | +0.26 | +0.01 | 63% | 0.7 |
| CIN | 5 | 25.6 | 62 | 62% | 272 | 83 | 2.6 | +0.15 | -0.07 | 53% | 1.0 |
| NO | 6 | 25.3 | 67 | 60% | 240 | 97 | 3.0 | -0.02 | -0.11 | 76% | 2.0 |
| DAL | 6 | 25.2 | 62 | 67% | 273 | 76 | 3.0 | +0.12 | -0.02 | 74% | 1.2 |
| CHI | 6 | 25.0 | 73 | 49% | 246 | 161 | 3.0 | +0.09 | -0.05 | 50% | 2.2 |
| SEA | 6 | 24.7 | 63 | 55% | 245 | 107 | 2.7 | +0.04 | -0.24 | 63% | 2.3 |
| IND | 6 | 24.0 | 67 | 57% | 215 | 112 | 2.2 | -0.14 | +0.06 | 63% | 1.8 |
| HOU | 6 | 24.0 | 63 | 61% | 286 | 85 | 2.5 | +0.15 | -0.16 | 54% | 0.5 |
| ATL | 6 | 23.7 | 60 | 48% | 211 | 150 | 2.5 | -0.15 | +0.05 | 75% | 1.8 |
| PIT | 6 | 22.8 | 64 | 64% | 248 | 99 | 2.2 | -0.14 | +0.05 | 50% | 1.3 |
| NE | 6 | 22.7 | 64 | 50% | 252 | 131 | 2.5 | +0.18 | -0.16 | 50% | 2.2 |
| NYG | 6 | 22.7 | 66 | 56% | 242 | 105 | 2.2 | +0.06 | -0.16 | 58% | 1.8 |
| LA | 6 | 22.5 | 68 | 63% | 301 | 113 | 2.8 | +0.08 | -0.04 | 62% | 1.5 |
| WAS | 6 | 22.0 | 64 | 55% | 214 | 125 | 2.3 | +0.06 | -0.14 | 50% | 0.3 |
| MIN | 5 | 21.8 | 61 | 48% | 188 | 116 | 1.6 | -0.03 | -0.18 | 54% | 0.8 |
| GB | 6 | 21.2 | 61 | 64% | 281 | 60 | 2.3 | +0.12 | -0.27 | 52% | 1.2 |
| ARI | 6 | 21.0 | 67 | 60% | 222 | 96 | 2.0 | +0.02 | -0.08 | 55% | 1.2 |
| TB | 6 | 19.8 | 63 | 55% | 186 | 128 | 1.7 | -0.18 | -0.04 | 50% | 1.8 |
| DEN | 6 | 19.0 | 57 | 56% | 175 | 84 | 1.8 | -0.10 | -0.05 | 65% | 0.8 |
| NYJ | 6 | 18.7 | 59 | 53% | 223 | 94 | 1.8 | +0.06 | -0.15 | 36% | 0.7 |
| CLE | 6 | 17.7 | 59 | 53% | 196 | 94 | 1.7 | +0.01 | -0.26 | 50% | 1.2 |
| PHI | 6 | 17.7 | 58 | 60% | 191 | 82 | 2.2 | -0.10 | -0.20 | 62% | 0.8 |
| LAC | 6 | 15.0 | 62 | 52% | 190 | 119 | 1.5 | -0.24 | -0.20 | 53% | 2.5 |
| MIA | 5 | 14.0 | 55 | 50% | 170 | 127 | 1.4 | -0.12 | -0.11 | 50% | 1.6 |
| TEN | 6 | 14.0 | 53 | 57% | 166 | 83 | 1.2 | -0.18 | -0.10 | 47% | 1.3 |

## 3. Team defense (through Week 6, per game allowed; rank 1 = allows the most)

| team | g | pts_allowed | pass_yds | rush_yds | td_allowed_pg | pass_epa_allowed | rush_epa_allowed | rz_td_pct_allowed | sacks | takeaways |
|---|---|---|---|---|---|---|---|---|---|---|
| ARI | 6 | 29.7 | 247 | 121 | 3.7 | +0.25 | -0.13 | 73% | 2.3 | 1.2 |
| NO | 6 | 29.7 | 256 | 138 | 3.5 | +0.10 | +0.02 | 61% | 2.5 | 1.5 |
| DET | 5 | 29.6 | 321 | 107 | 4.0 | +0.24 | -0.04 | 76% | 4.0 | 1.0 |
| WAS | 6 | 28.7 | 268 | 100 | 3.3 | +0.14 | -0.07 | 82% | 1.8 | 1.3 |
| BUF | 6 | 28.5 | 299 | 101 | 3.5 | +0.23 | -0.06 | 69% | 1.8 | 1.0 |
| IND | 6 | 27.3 | 240 | 122 | 2.7 | +0.08 | +0.05 | 61% | 1.7 | 0.5 |
| LV | 6 | 27.0 | 254 | 134 | 3.3 | +0.13 | -0.11 | 74% | 2.5 | 1.7 |
| DAL | 6 | 26.5 | 239 | 150 | 3.0 | +0.34 | -0.06 | 68% | 1.3 | 0.5 |
| MIA | 5 | 26.4 | 226 | 111 | 3.0 | +0.30 | -0.12 | 64% | 0.8 | 0.8 |
| ATL | 6 | 25.5 | 269 | 83 | 2.7 | +0.03 | -0.12 | 64% | 2.5 | 1.0 |
| LAC | 6 | 25.2 | 216 | 124 | 2.7 | -0.00 | -0.07 | 50% | 1.8 | 1.7 |
| CAR | 5 | 24.6 | 237 | 132 | 2.8 | +0.01 | -0.05 | 77% | 2.2 | 1.6 |
| HOU | 6 | 23.8 | 264 | 83 | 2.5 | +0.06 | -0.12 | 59% | 3.0 | 1.0 |
| NYG | 6 | 23.3 | 199 | 136 | 3.0 | +0.07 | -0.06 | 76% | 1.3 | 1.5 |
| LA | 6 | 23.0 | 174 | 127 | 2.0 | +0.02 | -0.11 | 52% | 1.3 | 1.0 |
| TB | 6 | 23.0 | 238 | 76 | 1.8 | -0.05 | -0.16 | 53% | 1.8 | 1.3 |
| PHI | 6 | 22.8 | 254 | 119 | 2.7 | +0.12 | +0.01 | 59% | 1.3 | 0.5 |
| BAL | 6 | 22.0 | 226 | 100 | 2.0 | -0.02 | -0.06 | 55% | 2.5 | 1.0 |
| CIN | 5 | 21.8 | 245 | 123 | 2.0 | -0.02 | -0.04 | 39% | 3.4 | 1.8 |
| TEN | 6 | 21.5 | 235 | 122 | 2.0 | +0.14 | -0.08 | 55% | 2.7 | 0.8 |
| PIT | 6 | 21.3 | 222 | 103 | 1.7 | -0.04 | -0.09 | 50% | 2.7 | 1.5 |
| GB | 6 | 20.8 | 209 | 114 | 2.7 | -0.08 | -0.02 | 68% | 2.5 | 1.8 |
| DEN | 6 | 20.8 | 230 | 140 | 2.2 | -0.05 | -0.01 | 53% | 3.0 | 1.8 |
| CLE | 6 | 20.3 | 227 | 112 | 2.0 | -0.01 | -0.07 | 47% | 3.2 | 1.2 |
| SEA | 6 | 20.3 | 157 | 96 | 2.0 | -0.10 | -0.19 | 85% | 2.7 | 1.5 |
| NYJ | 6 | 20.3 | 202 | 123 | 2.2 | +0.04 | -0.17 | 52% | 2.8 | 1.3 |
| CHI | 6 | 19.8 | 228 | 90 | 2.3 | -0.02 | -0.05 | 71% | 2.8 | 1.2 |
| NE | 6 | 18.8 | 228 | 92 | 2.0 | +0.01 | -0.05 | 50% | 2.3 | 1.2 |
| SF | 6 | 18.3 | 226 | 90 | 1.7 | +0.01 | -0.16 | 50% | 2.5 | 1.3 |
| JAX | 6 | 17.3 | 283 | 72 | 1.8 | +0.04 | -0.17 | 40% | 1.8 | 1.5 |
| KC | 5 | 16.6 | 224 | 89 | 1.4 | -0.08 | -0.14 | 38% | 1.6 | 2.0 |
| MIN | 5 | 12.8 | 195 | 87 | 1.0 | -0.21 | -0.22 | 25% | 3.4 | 2.0 |

## 4. Defense versus position (touchdowns allowed per game to the position, with the Week 7 opponent list)

Rank 1 = most TDs allowed. League TD points = 6 x TDs. Six games of data: descriptive, noisy.

**QB** most TDs allowed: DET 3.2 TD, 27.4 PPR; ARI 2.8 TD, 21.6 PPR; WAS 2.7 TD, 22.2 PPR; BUF 2.5 TD, 21.8 PPR; LV 2.5 TD, 20.5 PPR; NYG 2.5 TD, 20.1 PPR; MIA 2.4 TD, 18.8 PPR; DAL 2.0 TD, 21.3 PPR. Fewest: TEN 1.2; PIT 1.0; BAL 1.0; KC 0.8; MIN 0.6.

**RB** most TDs allowed: NO 2.0 TD, 30.1 PPR; GB 1.7 TD, 26.8 PPR; BUF 1.5 TD, 27.3 PPR; MIA 1.4 TD, 26.1 PPR; CAR 1.2 TD, 25.7 PPR; LAC 1.2 TD, 23.5 PPR; DAL 1.2 TD, 23.2 PPR; ATL 1.2 TD, 22.6 PPR. Fewest: JAX 0.5; MIN 0.4; LA 0.3; TB 0.3; CLE 0.2.

**WR** most TDs allowed: BUF 1.8 TD, 42.3 PPR; ARI 1.7 TD, 34.9 PPR; CLE 1.2 TD, 33.5 PPR; DAL 1.2 TD, 36.2 PPR; PHI 1.2 TD, 38.3 PPR; NYG 1.2 TD, 31.4 PPR; LV 1.2 TD, 32.6 PPR; LA 1.2 TD, 26.9 PPR. Fewest: JAX 0.5; PIT 0.5; CAR 0.4; MIA 0.4; KC 0.0.

**TE** most TDs allowed: DET 1.8 TD, 31.9 PPR; WAS 1.3 TD, 21.5 PPR; LV 1.0 TD, 17.7 PPR; ARI 1.0 TD, 19.1 PPR; KC 0.8 TD, 20.0 PPR; MIA 0.8 TD, 19.8 PPR; CAR 0.8 TD, 16.0 PPR; JAX 0.7 TD, 11.8 PPR. Fewest: LA 0.2; NE 0.2; CIN 0.0; MIN 0.0; SF 0.0.

**Week 7 matchup edges** (team vs the opponent's rank in TDs allowed to that position; top 6 per position):

- **QB**: GB vs DET (rank 1, 3.2 TD/g); DEN vs ARI (rank 2, 2.8 TD/g); HOU vs NYG (rank 4, 2.5 TD/g); LA vs LV (rank 4, 2.5 TD/g); NYJ vs MIA (rank 7, 2.4 TD/g); PHI vs DAL (rank 8, 2.0 TD/g)
- **RB**: PIT vs NO (rank 1, 2.0 TD/g); DET vs GB (rank 2, 1.7 TD/g); NYJ vs MIA (rank 4, 1.4 TD/g); TB vs CAR (rank 5, 1.2 TD/g); PHI vs DAL (rank 6, 1.2 TD/g); SF vs ATL (rank 6, 1.2 TD/g)
- **WR**: DEN vs ARI (rank 2, 1.7 TD/g); HOU vs NYG (rank 3, 1.2 TD/g); PHI vs DAL (rank 3, 1.2 TD/g); LA vs LV (rank 3, 1.2 TD/g); LV vs LA (rank 3, 1.2 TD/g); DAL vs PHI (rank 3, 1.2 TD/g)
- **TE**: GB vs DET (rank 1, 1.8 TD/g); DEN vs ARI (rank 3, 1.0 TD/g); LA vs LV (rank 3, 1.0 TD/g); NYJ vs MIA (rank 5, 0.8 TD/g); SEA vs KC (rank 5, 0.8 TD/g); TB vs CAR (rank 5, 0.8 TD/g)

## 4b. Advanced team stats (Pro Football Reference advanced tabs, via the nflverse copy; per game through Week 6)

pro-football-reference.com serves a bot challenge (HTTP 403) to scripted requests, so the same PFR advanced data is read from the nflverse mirror. Defense coverage columns are what each defense allowed on targets against it; pass rush columns are what it generated. Sorted by passer rating allowed (highest = weakest coverage).

| team | g | tgt_pg | cmp_pct_allowed | yds_per_tgt | rating_allowed | td_allowed_pg | adot_allowed | yac_pg | pressures_pg | sacks_pg | blitzes_pg | missed_tackle_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DAL | 6 | 29.2 | 71% | 8.1 | 98.0 | 1.8 | 8.7 | 109.3 | 8.0 | 1.3 | 11.2 | 9% |
| MIA | 5 | 32.0 | 69% | 7.7 | 96.3 | 2.6 | 7.0 | 113.0 | 6.2 | 0.8 | 9.0 | 7% |
| BUF | 6 | 40.7 | 64% | 7.6 | 94.0 | 2.5 | 8.1 | 129.2 | 10.8 | 1.8 | 12.0 | 10% |
| DET | 5 | 47.0 | 61% | 8.0 | 93.1 | 2.8 | 9.0 | 126.2 | 12.6 | 4.0 | 22.0 | 3% |
| LV | 6 | 30.8 | 66% | 8.3 | 92.0 | 2.2 | 9.4 | 126.8 | 12.2 | 2.5 | 10.3 | 9% |
| ARI | 6 | 31.3 | 60% | 8.2 | 91.6 | 2.7 | 9.0 | 107.5 | 6.7 | 2.2 | 9.0 | 6% |
| NO | 6 | 34.0 | 65% | 8.0 | 90.7 | 2.0 | 8.0 | 113.2 | 7.3 | 2.5 | 12.2 | 10% |
| WAS | 6 | 37.3 | 64% | 7.7 | 89.0 | 2.5 | 7.8 | 116.2 | 10.0 | 1.8 | 25.3 | 8% |
| ATL | 6 | 41.0 | 65% | 7.0 | 88.8 | 2.2 | 8.2 | 125.8 | 11.7 | 2.5 | 9.3 | 7% |
| CHI | 6 | 26.8 | 64% | 8.8 | 88.6 | 1.5 | 8.7 | 98.3 | 9.3 | 2.8 | 14.8 | 9% |
| LAC | 6 | 27.7 | 69% | 7.8 | 88.6 | 1.2 | 7.6 | 99.8 | 7.7 | 1.8 | 9.7 | 8% |
| IND | 6 | 32.8 | 58% | 8.1 | 87.8 | 1.8 | 9.0 | 124.5 | 6.3 | 1.7 | 5.0 | 10% |
| TEN | 6 | 30.2 | 70% | 7.8 | 87.7 | 1.0 | 8.0 | 97.5 | 8.3 | 2.7 | 4.5 | 5% |
| TB | 6 | 37.8 | 63% | 6.9 | 87.6 | 1.8 | 6.6 | 148.7 | 7.7 | 1.8 | 18.8 | 11% |
| SF | 6 | 35.5 | 66% | 6.7 | 87.5 | 1.3 | 7.3 | 122.7 | 11.0 | 2.5 | 10.8 | 8% |
| NE | 6 | 32.7 | 65% | 7.6 | 87.3 | 1.3 | 7.2 | 119.2 | 8.5 | 2.3 | 17.5 | 7% |
| HOU | 6 | 37.3 | 62% | 7.1 | 87.1 | 1.7 | 8.5 | 107.0 | 10.2 | 3.0 | 6.3 | 7% |
| PHI | 6 | 35.8 | 61% | 7.4 | 85.2 | 1.3 | 8.2 | 118.8 | 8.3 | 1.3 | 13.0 | 10% |
| BAL | 6 | 33.2 | 63% | 7.4 | 84.6 | 1.0 | 6.7 | 106.0 | 8.5 | 2.5 | 15.3 | 8% |
| NYJ | 6 | 34.5 | 57% | 6.4 | 83.6 | 1.5 | 7.5 | 96.8 | 9.2 | 2.8 | 17.7 | 6% |
| JAX | 6 | 37.5 | 62% | 8.1 | 83.2 | 1.2 | 8.4 | 120.8 | 9.5 | 1.7 | 14.7 | 9% |
| KC | 5 | 35.8 | 63% | 6.3 | 82.6 | 0.8 | 7.5 | 106.8 | 9.8 | 1.4 | 21.0 | 6% |
| CIN | 5 | 36.6 | 57% | 7.6 | 82.4 | 1.0 | 9.1 | 139.0 | 11.4 | 3.4 | 6.8 | 11% |
| NYG | 6 | 31.3 | 63% | 6.4 | 81.7 | 2.0 | 7.9 | 94.0 | 6.3 | 1.3 | 18.3 | 10% |
| CLE | 6 | 36.3 | 57% | 7.0 | 81.2 | 2.0 | 9.5 | 109.8 | 8.8 | 3.2 | 9.5 | 10% |
| CAR | 5 | 40.8 | 56% | 6.9 | 80.4 | 1.4 | 8.6 | 93.6 | 11.4 | 2.0 | 17.6 | 7% |
| GB | 6 | 35.7 | 64% | 6.2 | 75.5 | 1.2 | 6.8 | 121.3 | 10.2 | 2.5 | 18.0 | 8% |
| DEN | 6 | 34.0 | 58% | 6.8 | 74.9 | 1.0 | 8.5 | 100.3 | 10.3 | 3.0 | 21.2 | 12% |
| SEA | 6 | 31.0 | 61% | 5.2 | 73.4 | 1.2 | 6.5 | 86.0 | 11.3 | 2.7 | 12.7 | 7% |
| PIT | 6 | 40.8 | 50% | 6.4 | 72.4 | 1.2 | 8.6 | 117.3 | 7.3 | 2.7 | 8.8 | 12% |
| MIN | 5 | 29.4 | 57% | 6.6 | 72.1 | 0.6 | 8.6 | 103.0 | 14.0 | 3.4 | 43.8 | 7% |
| LA | 6 | 29.5 | 59% | 5.9 | 70.5 | 1.3 | 7.1 | 108.0 | 7.2 | 1.3 | 21.5 | 9% |

**Offense: protection, accuracy, drops and run-game contact** (sorted by pressure rate allowed, highest first)

| team | pressured_pg | sacked_pg | pressure_rate | bad_throw_rate | drops_pg | rec_drops_pg | ybc_per_att | yac_per_att | broken_tackles_pg |
|---|---|---|---|---|---|---|---|---|---|
| CAR | 14.0 | 2.4 | 33% | 15% | 1.2 | 1.2 | 2.5 | 1.7 | 2.6 |
| SEA | 11.3 | 2.7 | 32% | 12% | 1.7 | 1.7 | 2.3 | 1.6 | 1.2 |
| MIA | 9.0 | 2.8 | 31% | 18% | 1.6 | 1.6 | 3.4 | 1.4 | 1.4 |
| LAC | 9.8 | 3.5 | 29% | 17% | 2.3 | 2.3 | 2.4 | 1.8 | 3.7 |
| CLE | 9.5 | 4.0 | 29% | 16% | 1.0 | 1.0 | 2.0 | 1.7 | 1.5 |
| WAS | 10.2 | 2.3 | 28% | 15% | 1.7 | 1.7 | 3.2 | 1.3 | 0.8 |
| PHI | 10.0 | 2.7 | 28% | 20% | 1.8 | 1.8 | 2.0 | 1.7 | 1.3 |
| NE | 9.0 | 1.8 | 27% | 12% | 1.8 | 1.8 | 2.7 | 1.5 | 0.3 |
| TB | 9.3 | 3.7 | 26% | 19% | 1.0 | 1.0 | 2.7 | 2.1 | 3.3 |
| TEN | 8.0 | 1.7 | 26% | 16% | 2.5 | 2.5 | 2.5 | 1.3 | 0.7 |
| DAL | 10.3 | 1.2 | 24% | 15% | 1.8 | 1.8 | 2.4 | 1.4 | 0.7 |
| LV | 9.3 | 1.3 | 24% | 15% | 2.0 | 2.0 | 1.4 | 1.6 | 1.3 |
| NYJ | 8.0 | 3.2 | 24% | 12% | 1.3 | 1.3 | 2.0 | 1.6 | 2.0 |
| GB | 9.7 | 2.2 | 24% | 18% | 3.3 | 3.3 | 1.7 | 1.2 | 1.2 |
| BAL | 7.0 | 2.2 | 23% | 15% | 1.2 | 1.2 | 2.8 | 2.2 | 1.5 |
| DEN | 7.5 | 1.3 | 23% | 15% | 1.2 | 1.2 | 2.0 | 1.4 | 0.3 |
| CIN | 9.0 | 1.8 | 23% | 13% | 0.8 | 0.8 | 2.4 | 1.3 | 1.2 |
| IND | 8.8 | 2.5 | 23% | 16% | 1.3 | 1.3 | 2.3 | 1.7 | 1.3 |
| CHI | 8.3 | 2.5 | 22% | 14% | 1.3 | 1.3 | 2.7 | 1.7 | 1.3 |
| NO | 9.2 | 2.2 | 22% | 17% | 1.3 | 1.3 | 2.3 | 1.5 | 1.7 |
| MIN | 6.8 | 3.0 | 22% | 14% | 1.8 | 1.8 | 2.5 | 1.3 | 0.8 |
| PIT | 9.0 | 3.2 | 21% | 16% | 1.5 | 1.7 | 2.3 | 2.3 | 2.0 |
| JAX | 6.8 | 1.7 | 21% | 10% | 1.3 | 1.5 | 1.8 | 2.3 | 2.2 |
| ARI | 8.7 | 2.0 | 21% | 13% | 1.3 | 1.3 | 2.1 | 1.6 | 2.0 |
| BUF | 6.3 | 2.0 | 21% | 14% | 1.0 | 1.0 | 3.3 | 1.8 | 1.7 |
| KC | 6.8 | 1.2 | 21% | 15% | 1.2 | 1.2 | 2.9 | 2.6 | 2.6 |
| NYG | 7.8 | 3.0 | 20% | 21% | 1.3 | 1.3 | 2.1 | 1.6 | 0.8 |
| DET | 7.8 | 2.2 | 19% | 15% | 1.6 | 1.6 | 3.1 | 1.3 | 1.4 |
| HOU | 7.5 | 2.3 | 19% | 13% | 0.8 | 0.8 | 2.2 | 1.3 | 1.2 |
| ATL | 5.7 | 2.7 | 19% | 16% | 1.5 | 1.5 | 2.5 | 2.6 | 1.3 |
| SF | 5.2 | 0.8 | 18% | 14% | 0.5 | 0.5 | 2.9 | 1.7 | 0.8 |
| LA | 7.3 | 1.7 | 17% | 15% | 2.3 | 2.3 | 2.8 | 1.8 | 1.5 |

**Pass-rush mismatches this week** (offense that gets pressured often vs a defense that generates pressure): TB vs CAR (pressure rate 26%, opp 11.4 pressures/g); SEA vs KC (pressure rate 32%, opp 9.8 pressures/g); GB vs DET (pressure rate 24%, opp 12.6 pressures/g); IND vs MIN (pressure rate 23%, opp 14.0 pressures/g); MIA vs NYJ (pressure rate 31%, opp 9.2 pressures/g)

**Softest pass coverage faced** (passer rating allowed): PHI vs DAL (98); NYJ vs MIA (96); GB vs DET (93); LA vs LV (92); DEN vs ARI (92)

## 5. Player projections (market-anchored; active-conditional means; p = chance he plays)

`League pts` = 6 x expected TDs x availability (this league). `DK` = DraftKings points. `PPR` = standard PPR from the same projection (no QB passing).

**Quarterbacks**

| player | team | opp | p_active | pass_cmp_mean | pass_yds_mean | pass_td_mean | rush_yds_mean | rush_td_mean | any_td_pct | league_ev | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jordan Love | GB | DET | 98% | 22.9 | 289.6 | 1.98 | 5.1 | 0.07 | 7% | 12.1 | 18.4 |
| Matthew Stafford | LA | LV | 100% | 23.7 | 257.1 | 1.84 | 3.4 | 0.09 | 9% | 11.6 | 16.5 |
| Jared Goff | DET | GB | 100% | 22.2 | 231.3 | 1.80 | 4.6 | 0.12 | 11% | 11.5 | 16.2 |
| Bo Nix | DEN | ARI | 100% | 18.6 | 212.3 | 1.53 | 11.4 | 0.23 | 21% | 10.5 | 15.7 |
| Kirk Cousins | LV | LA | 100% | 20.3 | 225.7 | 1.53 | 5.1 | 0.04 | 4% | 9.4 | 13.9 |
| Dak Prescott | DAL | PHI | 100% | 23.9 | 258.8 | 1.37 | 8.2 | 0.15 | 14% | 9.1 | 15.7 |
| Sam Darnold | SEA | KC | 100% | 19.3 | 216.2 | 1.42 | 6.6 | 0.07 | 7% | 8.9 | 13.2 |
| Tanner McKee | PHI | DAL | 100% | 20.7 | 215.2 | 1.33 | 8.8 | 0.06 | 6% | 8.3 | 13.7 |
| Jacoby Brissett | ARI | DEN | 100% | 21.7 | 210.0 | 1.12 | 19.6 | 0.16 | 15% | 7.7 | 13.4 |
| Patrick Mahomes | KC | SEA | 98% | 19.5 | 188.0 | 1.08 | 14.5 | 0.10 | 10% | 7.0 | 11.8 |

**Running backs**

| player | team | opp | p_active | rush_att_mean | rush_yds_mean | rush_td_mean | rec_mean | rec_yds_mean | rec_td_mean | any_td_pct | league_ev | ppr | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | 100% | 20.0 | 91.9 | 1.17 | 4.2 | 30.6 | 0.22 | 77% | 8.3 | 24.7 | 24.5 |
| Kyren Williams | LA | LV | 100% | 13.4 | 72.0 | 0.65 | 5.4 | 43.5 | 0.35 | 65% | 6.0 | 22.9 | 22.7 |
| Javonte Williams | DAL | PHI | 100% | 13.7 | 54.2 | 0.78 | 2.7 | 17.4 | 0.10 | 60% | 5.3 | 15.2 | 15.0 |
| Kenneth Walker III | KC | SEA | 100% | 18.6 | 96.8 | 0.54 | 3.4 | 23.8 | 0.18 | 53% | 4.3 | 19.8 | 19.6 |
| Ashton Jeanty | LV | LA | 100% | 16.2 | 59.7 | 0.37 | 3.7 | 28.8 | 0.23 | 46% | 3.6 | 16.1 | 15.9 |
| J.K. Dobbins | DEN | ARI | 100% | 13.5 | 54.9 | 0.51 | 1.1 | 9.1 | 0.04 | 43% | 3.3 | 10.8 | 10.7 |
| Emanuel Wilson | SEA | KC | 100% | 15.4 | 59.8 | 0.46 | 1.2 | 8.7 | 0.06 | 41% | 3.1 | 11.2 | 11.0 |
| Dameon Pierce | PHI | DAL | 100% | 12.6 | 50.2 | 0.31 | 3.2 | 24.0 | 0.13 | 36% | 2.6 | 13.3 | 13.1 |
| MarShawn Lloyd | GB | DET | 100% | 8.6 | 30.2 | 0.30 | 1.9 | 14.2 | 0.14 | 36% | 2.6 | 8.9 | 8.8 |
| Blake Corum | LA | LV | 100% | 7.5 | 39.7 | 0.26 | 1.8 | 14.6 | 0.15 | 34% | 2.4 | 9.6 | 9.6 |
| RJ Harvey | DEN | ARI | 100% | 5.4 | 23.4 | 0.16 | 3.3 | 27.3 | 0.21 | 31% | 2.2 | 10.6 | 10.5 |
| Tyler Allgeier | ARI | DEN | 100% | 14.8 | 59.8 | 0.30 | 1.6 | 10.9 | 0.06 | 30% | 2.1 | 10.8 | 10.7 |
| Pierre Strong | GB | DET | 100% | 5.6 | 21.2 | 0.16 | 3.7 | 28.4 | 0.14 | 27% | 1.8 | 10.4 | 10.4 |
| George Holani | SEA | KC | 100% | 7.4 | 28.9 | 0.20 | 1.7 | 12.1 | 0.07 | 24% | 1.7 | 7.5 | 7.4 |
| Sione Vaki | DET | GB | 100% | 4.6 | 18.3 | 0.19 | 0.6 | 4.6 | 0.02 | 19% | 1.3 | 4.2 | 4.2 |
| Saquon Barkley | PHI | DAL | 71% | 6.8 | 35.0 | 0.18 | 2.0 | 14.9 | 0.07 | 23% | 1.1 | 8.5 | 5.9 |
| Bam Knight | ARI | DEN | 100% | 6.1 | 31.9 | 0.13 | 0.7 | 4.7 | 0.02 | 14% | 0.9 | 5.2 | 5.2 |
| Emari Demercado | DAL | PHI | 100% | 3.9 | 17.0 | 0.14 | 0.5 | 3.6 | 0.01 | 14% | 0.9 | 3.4 | 3.4 |

**Wide receivers**

| player | team | opp | p_active | tgt_mean | rec_mean | rec_yds_mean | rec_td_mean | any_td_pct | league_ev | ppr | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Amon-Ra St. Brown | DET | GB | 100% | 10.4 | 6.5 | 67.6 | 0.64 | 49% | 3.8 | 17.1 | 17.0 |
| Jaxon Smith-Njigba | SEA | KC | 100% | 11.1 | 6.9 | 95.3 | 0.57 | 45% | 3.5 | 20.0 | 20.0 |
| Matthew Golden | GB | DET | 96% | 8.5 | 4.9 | 75.3 | 0.60 | 46% | 3.4 | 16.1 | 15.4 |
| Christian Watson | GB | DET | 96% | 8.6 | 5.1 | 89.9 | 0.51 | 40% | 2.9 | 17.1 | 16.4 |
| CeeDee Lamb | DAL | PHI | 100% | 10.8 | 6.7 | 83.3 | 0.42 | 35% | 2.6 | 17.7 | 17.6 |
| Courtland Sutton | DEN | ARI | 100% | 5.3 | 2.9 | 39.3 | 0.34 | 29% | 2.1 | 8.9 | 8.9 |
| Jaylen Waddle | DEN | ARI | 95% | 6.7 | 3.9 | 51.9 | 0.32 | 28% | 1.9 | 11.2 | 10.6 |
| George Pickens | DAL | PHI | 95% | 8.8 | 5.4 | 71.7 | 0.31 | 27% | 1.7 | 14.4 | 13.6 |
| Puka Nacua | LA | LV | 50% | 10.8 | 7.1 | 92.1 | 0.54 | 45% | 1.7 | 20.0 | 9.9 |
| Michael Wilson | ARI | DEN | 100% | 8.3 | 4.6 | 48.0 | 0.28 | 25% | 1.7 | 11.1 | 11.0 |
| Tre Tucker | LV | LA | 100% | 5.7 | 3.2 | 45.9 | 0.27 | 24% | 1.7 | 9.6 | 9.6 |
| Darius Cooper | PHI | DAL | 100% | 2.7 | 1.5 | 21.7 | 0.26 | 23% | 1.6 | 5.3 | 5.3 |
| Xavier Worthy | KC | SEA | 100% | 6.7 | 4.1 | 43.9 | 0.25 | 23% | 1.5 | 10.0 | 10.0 |
| Jameson Williams | DET | GB | 100% | 5.5 | 3.4 | 48.4 | 0.25 | 22% | 1.5 | 9.7 | 9.7 |
| Ryan Flournoy | DAL | PHI | 100% | 5.7 | 3.5 | 38.9 | 0.24 | 21% | 1.4 | 8.8 | 8.8 |
| Makai Lemon | PHI | DAL | 100% | 6.8 | 4.0 | 43.3 | 0.21 | 19% | 1.3 | 9.7 | 9.6 |
| Rashid Shaheed | SEA | KC | 95% | 5.0 | 2.9 | 32.6 | 0.18 | 17% | 1.1 | 7.4 | 7.0 |
| Cooper Kupp | SEA | KC | 100% | 4.4 | 2.6 | 30.0 | 0.18 | 16% | 1.1 | 6.7 | 6.6 |
| Kendrick Bourne | ARI | DEN | 100% | 4.8 | 2.9 | 32.1 | 0.17 | 16% | 1.0 | 7.1 | 7.1 |
| Konata Mumpfield | LA | LV | 100% | 3.4 | 1.9 | 27.7 | 0.17 | 15% | 1.0 | 5.7 | 5.7 |
| Isaac TeSlaa | DET | GB | 100% | 2.6 | 1.6 | 21.1 | 0.16 | 15% | 1.0 | 4.7 | 4.6 |
| Cody White | LV | LA | 100% | 2.2 | 1.2 | 16.1 | 0.16 | 15% | 1.0 | 3.8 | 3.8 |
| Troy Franklin | DEN | ARI | 100% | 2.7 | 1.6 | 21.4 | 0.15 | 15% | 0.9 | 4.8 | 4.8 |
| Jalen Nailor | LV | LA | 100% | 3.4 | 1.8 | 23.8 | 0.12 | 12% | 0.7 | 5.0 | 4.9 |

**Tight ends**

| player | team | opp | p_active | tgt_mean | rec_mean | rec_yds_mean | rec_td_mean | any_td_pct | league_ev | ppr | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Sam LaPorta | DET | GB | 100% | 8.0 | 5.6 | 57.4 | 0.47 | 38% | 2.8 | 14.2 | 14.2 |
| Tucker Kraft | GB | DET | 100% | 7.5 | 4.9 | 57.1 | 0.44 | 37% | 2.8 | 13.5 | 13.4 |
| Brock Bowers | LV | LA | 95% | 9.6 | 6.0 | 66.3 | 0.44 | 37% | 2.5 | 15.2 | 14.4 |
| Trey McBride | ARI | DEN | 100% | 11.8 | 7.6 | 66.2 | 0.38 | 32% | 2.3 | 16.6 | 16.5 |
| Colby Parkinson | LA | LV | 95% | 5.9 | 4.0 | 41.8 | 0.40 | 33% | 2.3 | 10.6 | 10.0 |
| Tyler Higbee | LA | LV | 100% | 6.9 | 4.7 | 52.5 | 0.34 | 29% | 2.0 | 12.0 | 11.9 |
| Dallas Goedert | PHI | DAL | 95% | 8.2 | 5.3 | 55.1 | 0.34 | 29% | 2.0 | 12.9 | 12.2 |
| AJ Barner | SEA | KC | 100% | 4.8 | 3.1 | 29.4 | 0.27 | 25% | 1.7 | 7.8 | 7.8 |
| Travis Kelce | KC | SEA | 96% | 8.1 | 5.4 | 55.7 | 0.28 | 24% | 1.6 | 12.7 | 12.1 |
| Zach Ertz | PHI | DAL | 100% | 5.8 | 3.7 | 37.8 | 0.23 | 21% | 1.4 | 8.8 | 8.8 |
| Michael Mayer | LV | LA | 100% | 5.6 | 3.5 | 35.1 | 0.22 | 20% | 1.3 | 8.3 | 8.3 |
| Evan Engram | DEN | ARI | 100% | 4.1 | 2.6 | 29.1 | 0.20 | 19% | 1.2 | 6.7 | 6.7 |
| Jake Ferguson | DAL | PHI | 100% | 5.4 | 3.7 | 33.1 | 0.19 | 18% | 1.2 | 8.1 | 8.1 |
| Noah Gray | KC | SEA | 100% | 4.1 | 2.6 | 24.2 | 0.15 | 14% | 0.9 | 6.0 | 6.0 |

**Kickers (this league: FG 3, XP 1; ranked by team implied points, the only validated signal; differences are within noise)**: DET 8.3; HOU 7.8; SF 7.8; LA 7.8; GB 7.8; CIN 7.6; DEN 7.5; DAL 7.5; MIN 7.5; CAR 7.5

## 6. Touchdown boards (anytime counts rushing and receiving TDs; fair odds; 'play at' = fair + 12% cushion)

**Top 30 anytime TD** (ranked by probability times chance he plays; 'prob' is conditional on playing)

| player | team | opp | pos | prob | adj | fair | playat | p_active | note |
|---|---|---|---|---|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | RB | 77.5% | 77.5% | -344 | -224 | 100% |  |
| Kyren Williams | LA | LV | RB | 64.8% | 64.8% | -184 | -138 | 100% |  |
| Javonte Williams | DAL | PHI | RB | 60.0% | 60.0% | -150 | -115 | 100% | opp QB: fill-in QB (Tanner McKee) red-team downgrade |
| Kenneth Walker III | KC | SEA | RB | 52.8% | 52.8% | -112 | +112 | 100% |  |
| Amon-Ra St. Brown | DET | GB | WR | 48.5% | 48.5% | +106 | +131 | 100% |  |
| Ashton Jeanty | LV | LA | RB | 46.0% | 46.0% | +117 | +143 | 100% |  |
| Jaxon Smith-Njigba | SEA | KC | WR | 44.8% | 44.8% | +123 | +150 | 100% |  |
| Matthew Golden | GB | DET | WR | 45.9% | 44.0% | +118 | +144 | 96% |  |
| J.K. Dobbins | DEN | ARI | RB | 43.4% | 43.4% | +131 | +158 | 100% |  |
| Emanuel Wilson | SEA | KC | RB | 41.0% | 41.0% | +144 | +173 | 100% |  |
| Christian Watson | GB | DET | WR | 40.5% | 38.8% | +147 | +177 | 96% |  |
| Sam LaPorta | DET | GB | TE | 38.2% | 38.2% | +162 | +193 | 100% |  |
| Tucker Kraft | GB | DET | TE | 37.5% | 37.5% | +167 | +199 | 100% |  |
| Dameon Pierce | PHI | DAL | RB | 36.3% | 36.3% | +175 | +208 | 100% | fill-in QB (Tanner McKee) |
| CeeDee Lamb | DAL | PHI | WR | 35.4% | 35.4% | +183 | +217 | 100% | opp QB: fill-in QB (Tanner McKee) |
| Brock Bowers | LV | LA | TE | 36.5% | 34.6% | +174 | +207 | 95% |  |
| Blake Corum | LA | LV | RB | 34.1% | 34.1% | +193 | +228 | 100% |  |
| Trey McBride | ARI | DEN | TE | 32.2% | 32.2% | +210 | +247 | 100% |  |
| Colby Parkinson | LA | LV | TE | 33.4% | 31.7% | +199 | +235 | 95% |  |
| RJ Harvey | DEN | ARI | RB | 31.2% | 31.2% | +221 | +259 | 100% |  |
| Tyler Allgeier | ARI | DEN | RB | 30.2% | 30.2% | +231 | +270 | 100% |  |
| Courtland Sutton | DEN | ARI | WR | 29.4% | 29.4% | +240 | +281 | 100% |  |
| Tyler Higbee | LA | LV | TE | 28.8% | 28.8% | +247 | +288 | 100% |  |
| Dallas Goedert | PHI | DAL | TE | 29.4% | 27.9% | +240 | +281 | 95% | fill-in QB (Tanner McKee) |
| Jaylen Waddle | DEN | ARI | WR | 28.4% | 27.0% | +252 | +294 | 95% |  |
| AJ Barner | SEA | KC | TE | 25.4% | 25.4% | +294 | +341 | 100% |  |
| George Pickens | DAL | PHI | WR | 26.7% | 25.4% | +274 | +319 | 95% | opp QB: fill-in QB (Tanner McKee) |
| Michael Wilson | ARI | DEN | WR | 24.5% | 24.5% | +308 | +356 | 100% |  |
| George Holani | SEA | KC | RB | 24.5% | 24.5% | +309 | +358 | 100% |  |
| Tre Tucker | LV | LA | WR | 24.3% | 24.3% | +311 | +360 | 100% |  |

**2+ TD (top 10)**

| player | team | opp | prob | fair |
|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | 41.4% | +141 |
| Kyren Williams | LA | LV | 26.4% | +279 |
| Javonte Williams | DAL | PHI | 21.9% | +357 |
| Kenneth Walker III | KC | SEA | 16.0% | +526 |
| Amon-Ra St. Brown | DET | GB | 13.0% | +670 |
| Ashton Jeanty | LV | LA | 11.7% | +755 |
| Matthew Golden | GB | DET | 11.6% | +761 |
| Jaxon Smith-Njigba | SEA | KC | 11.2% | +792 |
| Puka Nacua | LA | LV | 11.1% | +802 |
| J.K. Dobbins | DEN | ARI | 10.0% | +896 |

**First TD (top 10)**

| player | team | opp | prob | fair |
|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | 21.8% | +360 |
| Kyren Williams | LA | LV | 18.5% | +440 |
| Javonte Williams | DAL | PHI | 17.8% | +463 |
| Kenneth Walker III | KC | SEA | 16.3% | +514 |
| Jaxon Smith-Njigba | SEA | KC | 12.9% | +672 |
| J.K. Dobbins | DEN | ARI | 12.1% | +730 |
| Emanuel Wilson | SEA | KC | 11.7% | +755 |
| Ashton Jeanty | LV | LA | 10.9% | +815 |
| Puka Nacua | LA | LV | 10.8% | +823 |
| Amon-Ra St. Brown | DET | GB | 9.9% | +911 |

**Sneaky longshots** (8% to 25% anytime, active 90%+): Michael Wilson (ARI) 25% fair +308, take at +356+; George Holani (SEA) 24% fair +309, take at +358+; Tre Tucker (LV) 24% fair +311, take at +360+; Travis Kelce (KC) 24% fair +309, take at +358+; Darius Cooper (PHI) 23% fair +334, take at +386+; Xavier Worthy (KC) 23% fair +342, take at +395+; Jameson Williams (DET) 22% fair +354, take at +408+; Ryan Flournoy (DAL) 21% fair +369, take at +425+; Zach Ertz (PHI) 21% fair +381, take at +439+; Bo Nix (DEN) 21% fair +386, take at +445+; Michael Mayer (LV) 20% fair +399, take at +459+; Makai Lemon (PHI) 19% fair +417, take at +479+; Sione Vaki (DET) 19% fair +423, take at +486+; Evan Engram (DEN) 19% fair +436, take at +500+; Jake Ferguson (DAL) 18% fair +465, take at +533+; Cooper Kupp (SEA) 16% fair +514, take at +588+; Rashid Shaheed (SEA) 17% fair +483, take at +553+; Kendrick Bourne (ARI) 16% fair +542, take at +619+; Konata Mumpfield (LA) 15% fair +553, take at +632+; Isaac TeSlaa (DET) 15% fair +561, take at +640+

## 7. Single-line screen (DraftKings lines via ESPN, assumed -110)

188 lines screened: **8 PLAY** (4 receiving, tagged thin: W6 receiving lines hit 35 to 52 percent, Thursday 7 of 11), 21 LEAN (the 21 best shown). Pulled by rule: receiving LEANs, pass-volume UNDERs, UNDERs on a teammate of a player now Out or Questionable ('role change'). PLAY = shrunk probability about 55.4%+ (about 61% raw), active 95%+, side cleared in at least half of the player's games. 'Agree' = the model-only track picks the same side.

| label | game | player | market | side | line | model_p | shrunk | fair | log | agree | flag | caution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAY (thin) | DEN@ARI | Tyler Allgeier | rec | UNDER | 2.5 | 77% | 63% | -173 | 5/6 | yes |  |  |
| PLAY | GB@DET | Jordan Love | rush_yds | UNDER | 6.5 | 75% | 62% | -166 | 4/5 | yes |  |  |
| PLAY | LA@LV | Kyren Williams | rush_att | UNDER | 15.5 | 71% | 61% | -154 | 4/6 | yes |  |  |
| PLAY (thin) | KC@SEA | Noah Gray | rec | OVER | 1.5 | 70% | 60% | -151 | 3/5 | yes |  |  |
| PLAY (thin) | DEN@ARI | Courtland Sutton | rec | UNDER | 3.5 | 65% | 58% | -136 | 6/6 | yes |  |  |
| PLAY (thin) | DEN@ARI | Trey McBride | rec | OVER | 6.5 | 63% | 57% | -131 | 6/6 | yes |  |  |
| PLAY | DEN@ARI | Bo Nix | rush_yds | UNDER | 10.5 | 63% | 56% | -130 | 6/6 | yes |  |  |
| PLAY | KC@SEA | Kenneth Walker III | rush_yds | OVER | 80.5 | 63% | 56% | -129 | 4/5 | yes |  |  |
| LEAN | DAL@PHI | Saquon Barkley | rush_yds | UNDER | 70.5 | 92% | 71% | -245 | 2/4 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | DEN@ARI | Jacoby Brissett | rush_yds | OVER | 6.5 | 78% | 64% | -178 | 4/6 | yes | red-team downgrade |  |
| LEAN | DAL@PHI | Javonte Williams | rush_att | UNDER | 16.5 | 77% | 64% | -175 | 4/6 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | KC@SEA | Emmett Johnson | rush_yds | OVER | 8.5 | 72% | 61% | -155 | 3/4 | yes | red-team downgrade |  |
| LEAN | DAL@PHI | Dak Prescott | rush_yds | UNDER | 9.5 | 71% | 60% | -152 | 2/5 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | DAL@PHI | Javonte Williams | rush_yds | UNDER | 64.5 | 70% | 60% | -151 | 5/6 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | DAL@PHI | Tanner McKee | pass_cmp | OVER | 19.5 | 69% | 59% | -146 | 1/1 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | GB@DET | Sione Vaki | rush_yds | OVER | 8.5 | 68% | 59% | -144 | 2/4 | yes | red-team downgrade |  |
| LEAN | LA@LV | Blake Corum | rush_att | UNDER | 8.5 | 66% | 58% | -137 | 3/6 | yes | red-team downgrade |  |
| LEAN | DAL@PHI | Tanner McKee | pass_yds | OVER | 193.5 | 66% | 58% | -137 | 1/1 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | LA@LV | Ashton Jeanty | rush_att | OVER | 14.5 | 63% | 56% | -130 | 4/6 | yes | red-team downgrade |  |
| LEAN | DEN@ARI | RJ Harvey | rush_yds | OVER | 14.5 | 63% | 56% | -129 | 3/5 | yes | red-team downgrade |  |
| LEAN | DAL@PHI | Dak Prescott | pass_cmp | OVER | 23.5 | 60% | 55% | -123 | 5/6 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | GB@DET | Jahmyr Gibbs | rush_yds | UNDER | 95.5 | 59% | 55% | -120 | 2/5 | yes |  |  |
| LEAN | LA@LV | Matthew Stafford | pass_cmp | OVER | 23.5 | 58% | 54% | -118 | 4/6 | yes |  |  |
| LEAN | GB@DET | Jared Goff | rush_yds | OVER | 0.5 | 58% | 54% | -118 | 4/4 | yes |  |  |
| LEAN | GB@DET | Jordan Love | rush_att | UNDER | 1.5 | 57% | 54% | -116 | 3/5 | yes |  |  |
| LEAN | KC@SEA | Emanuel Wilson | rush_att | OVER | 14.5 | 57% | 54% | -116 | 3/6 | yes |  |  |
| LEAN | DAL@PHI | Dak Prescott | pass_att | OVER | 37.5 | 56% | 53% | -113 | 4/6 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | DAL@PHI | Tanner McKee | pass_att | UNDER | 34.5 | 54% | 52% | -109 | 0/1 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | DAL@PHI | Tanner McKee | rush_yds | UNDER | 5.5 | 52% | 51% | -105 | 1/1 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |

## 8. Parlays across the slate (fair odds; legs from different games are independent, same-game legs use the joint simulation)

Pool: PLAY/LEAN single-line legs (shrunk), anytime-TD legs (12-60%), QB 1+ and 2+ passing TD legs. Hit probability is after the single-leg shrink. A real same-game parlay usually pays less than the product of its legs, so only take it at or better than 'play at'. Singles are in section 7; the best single touchdown plays are in section 6.

### 2-leg

**Highest chance to hit**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love pass TD 1+ | 43.3% | 66.5% | +131 | +159 |
| DEN@ARI: Tyler Allgeier rec U2.5 + LA@LV: Matthew Stafford pass TD 1+ | 43.3% | 66.4% | +131 | +159 |
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jared Goff pass TD 1+ | 42.9% | 65.5% | +133 | +161 |
| GB@DET: Jordan Love rush_yds U6.5 + LA@LV: Matthew Stafford pass TD 1+ | 41.8% | 63.5% | +139 | +168 |

**Touchdown-led (at least one TD leg, longer shot)**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 37.7% | 47.6% | +165 | +197 |
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love pass TD 2+ | 35.0% | 46.4% | +186 | +220 |
| KC@SEA: Kenneth Walker III anytime TD + GB@DET: Jordan Love pass TD 1+ | 34.9% | 45.3% | +186 | +221 |
| KC@SEA: Kenneth Walker III anytime TD + LA@LV: Matthew Stafford pass TD 1+ | 34.9% | 45.2% | +186 | +221 |

### 3-leg

**Highest chance to hit**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love rush_yds U6.5 + LA@LV: Matthew Stafford pass TD 1+ | 26.4% | 48.7% | +278 | +324 |
| DEN@ARI: Tyler Allgeier rec U2.5 + LA@LV: Kyren Williams rush_att U15.5 + GB@DET: Jordan Love pass TD 1+ | 26.2% | 47.4% | +281 | +327 |
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love rush_yds U6.5 + GB@DET: Jared Goff pass TD 1+ | 26.2% | 48.0% | +281 | +327 |
| DEN@ARI: Tyler Allgeier rec U2.5 + KC@SEA: Noah Gray rec O1.5 + GB@DET: Jordan Love pass TD 1+ | 26.0% | 46.7% | +284 | +330 |

**Touchdown-led (at least one TD leg, longer shot)**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 23.9% | 36.4% | +319 | +369 |
| GB@DET: Jordan Love rush_yds U6.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 23.3% | 35.2% | +329 | +381 |
| LA@LV: Kyren Williams rush_att U15.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 22.9% | 33.9% | +338 | +390 |
| KC@SEA: Noah Gray rec O1.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 22.7% | 33.4% | +341 | +394 |

### 4-leg

**Highest chance to hit**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love rush_yds U6.5 + KC@SEA: Noah Gray rec O1.5 + LA@LV: Matthew Stafford pass TD 1+ | 15.9% | 34.2% | +529 | +604 |
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love rush_yds U6.5 + LA@LV: Kyren Williams rush_att U15.5 + GB@DET: Jared Goff pass TD 1+ | 15.9% | 34.2% | +529 | +605 |
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love rush_yds U6.5 + LA@LV: Kyren Williams rush_att U15.5 + LA@LV: Matthew Stafford pass TD 1+ | 15.8% | 34.2% | +533 | +609 |
| DEN@ARI: Tyler Allgeier rec U2.5 + LA@LV: Kyren Williams rush_att U15.5 + KC@SEA: Noah Gray rec O1.5 + GB@DET: Jordan Love pass TD 1+ | 15.8% | 33.3% | +534 | +610 |

**Touchdown-led (at least one TD leg, longer shot)**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| DEN@ARI: Tyler Allgeier rec U2.5 + GB@DET: Jordan Love rush_yds U6.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 14.7% | 27.0% | +578 | +659 |
| DEN@ARI: Tyler Allgeier rec U2.5 + LA@LV: Kyren Williams rush_att U15.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 14.5% | 26.0% | +591 | +674 |
| DEN@ARI: Tyler Allgeier rec U2.5 + KC@SEA: Noah Gray rec O1.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 14.4% | 25.6% | +597 | +680 |
| GB@DET: Jordan Love rush_yds U6.5 + LA@LV: Kyren Williams rush_att U15.5 + GB@DET: Amon-Ra St. Brown anytime TD + GB@DET: Jared Goff pass TD 1+ | 14.1% | 25.1% | +608 | +693 |

### Quarterback passing-TD ladder (calibrated market: the model beat the books here in W4; fair odds)

Raw simulation probability, with the 50/50-shrunk figure used in parlays in brackets. Treat anything above 85% raw as 'very likely', not a number to price. Backup QBs are not listed.

| QB | 1+ raw (shrunk) | 2+ raw (shrunk) |
|---|---|---|
| Jordan Love | 87% (68%) | 61% (55%) |
| Matthew Stafford | 87% (68%) | 56% (53%) |
| Jared Goff | 85% (68%) | 55% (53%) |
| Kirk Cousins | 82% (66%) | 48% (49%) |
| Bo Nix | 80% (65%) | 46% (48%) |
| Sam Darnold | 78% (64%) | 43% (47%) |
| Dak Prescott | 76% (63%) | 40% (45%) |
| Jacoby Brissett | 69% (60%) | 30% (40%) |
| Patrick Mahomes | 66% (58%) | 30% (40%) |

## 9. This league (SPAMML) view

League points use expected TDs, so the player tables above (`League pts` column) are the lineup and waiver inputs; `apex-weekly waiver --run <run_dir> --roster ... --available ...` turns them into add/drop moves under the written rule (DECISIONS #27). Kickers: rank by team implied points only. DST is worth about 1 point a game for everyone in this league.

## 10. Last week's scorecard (Week 6, graded in POSTMORTEM_2026_W06.md)

| Group | Result | Expected |
|---|---|---|
| PLAY singles | 58.5% (n=94) | 59.7% |
| LEAN rush and passing counts | 61.9% (n=63) | 56.0% |
| LEAN receiving | **35.2% (n=105)** | 56.4% |
| Anytime TD board, 204 active non-QB players | 38 scored | 40.6 predicted |
| QB passing-TD ladder | 1+: 21 vs 19.0, 2+: 11 vs 10.4 | calibrated |
| Parlays | 9 of 48 | 14.7 |

Thursday Week 7 (NE@CHI, graded in `TNF_NE_CHI_2026_W07_SCORECARD.md`): published singles 11 of 22 (50%, +0.43 units at best of six books), pass-volume unders 1 of 6, CHI RB lines withheld by the old gate 4 of 4.

What it says: where the model disagrees with a receiving line, the line was right, so receiving LEANs are no longer published (this report has none) and receiving PLAYs are flagged thin. Rush and passing-count lines and the QB passing-TD ladder held up. Parlays failed together on shared scripts: each ticket here holds at most one QB passing-TD leg, and every touchdown leg is shown raw next to the shrunk number.

## 10b. Lines with no projection, and players withheld

1 players have posted lines but no projection row (not on the 2026 stats universe, injured/exempt, or name mismatch). Nothing is published for them:

| player | team | game | market |
|---|---|---|---|
| Josh Jacobs | GB | GB@DET | reception_yds, receptions, rush_attempts, rush_yds |

**Withheld on purpose** (no line, touchdown or parlay leg):

| player | team | reason |
|---|---|---|
| Josh Jacobs | GB | RB1 on the depth chart and ACT on the roster with no 2026 games and no projection row (book lines posted; role unknown) |
| MarShawn Lloyd | GB | GB backfield shares are unpriced while Jacobs is missing |
| Kaleb Johnson | GB | GB backfield shares are unpriced while Jacobs is missing |
| Pierre Strong | GB | GB backfield shares are unpriced while Jacobs is missing |
| Chris Brooks | GB | GB backfield shares are unpriced while Jacobs is missing |

## 11. Known gaps and audit results (read before betting)

Each window is audited before it is frozen by a data audit, a model sanity check and a red-team pass (QB1 against the depth chart, bye-team rows, Out players and their volume, team codes, unmatched names); the audit verdicts are written into the run notes of the frozen manifest. Remaining, by how much they change a pick:

1. **Fill-in quarterbacks (depth-chart QB1 who is not the 2026 completions leader):** BAL (QB1 uncertain, start probability 0%), NYG (J.J. McCarthy), PHI (Tanner McKee), TB (QB1 uncertain, start probability 65%). The backup is modeled at 92% of starter efficiency with the team's YPA and the model-only track does not discount him, so pass-game singles for these teams carry a caution flag and the QBs are left out of touchdown boards and parlay legs.
2. **Carries leak to 'other'.** The vacated-role candidate (DECISIONS #35) did not move the 27-slate backtest, so the engine is unchanged: team RBs get about 70% of team carries in the projection against about 80% in practice, so rushing props are not inflated for backs on teams with a lead back Out. Since the Thursday result (DECISIONS #43) these lines are no longer withheld; compare them with any book number you have.
3. **DAL@PHI** (Monday 8:15 PM ET) runs on this window's inputs, which stop on Sunday morning: treat its availability as provisional and use the Monday rerun. The raw `w4_*` files in the frozen run still contain the played NE@CHI rows (flagged PLAYED); this report excludes them.
3b. **Known biases to price in.** QB over/under props and QB fantasy points run about 5 to 7 percent low (the sim gives the starter 93 percent of team yards, attempts and completions; starters took 97 to 98 percent in 2023-26; a backtest candidate, not changed this week). Team rush yards run 4 to 5 percent high and ATL, NYG, BAL and PHI backs are under-allocated carries (6 or more carries go to an unlisted bucket), so read rushing props for those teams as uncertain. Team touchdowns run about 6 percent light against 2026 weeks 1 to 6. The model-only track disagrees with the market by 4.5 or more points of margin in CIN@BAL, DAL@PHI and NYG@HOU: a diagnostic, not a pick source.
3c. **Log hit rates drop zero-usage games** (a game with no target or carry is missing from the 'log' column), which flatters OVERs on low-volume players; red-team corrected Hooper, Dillon and Dulcich by hand. **No model-versus-market gap flags:** there are no prices, so no no-vig anchor exists to measure a gap against.
4. **Availability prior.** Healthy players with no designation carry p_active of about 0.95 (fitted prior), so A.J. Brown's anytime TD is 5% below his conditional number. Inactives (about 90 minutes before each kickoff) replace the prior with certainty.
5. Anytime-TD board: the 0.10 to 0.20 bin was over-predicted 2.4x in Week 6 in the sim board (frozen-run board: predicted 15.0% vs 9.1% actual, n=55) and the top ten hit 70% against 64% predicted; the W9 postmortem checks the floor. Probabilities are conditional on playing, so discount by the p_active column.
6. Minor: about two dozen practice-squad or inactive players carry small volumes at 100% active (e.g. players listed IR/PUP who appear in the unmatched-names report).
7. Nothing here is priced: no book prices and no touchdown prices. A PLAY is a lean at an assumed -110, not an edge. Send a screenshot of any board and I will re-price against the real numbers.

Method: `apex-weekly run` both tracks, `espn_inactives.py`, `espn_props.py`, `slate_full.py sim/render`, `team_tables.py` (box score, play-by-play and PFR advanced), `league_spm.py`.