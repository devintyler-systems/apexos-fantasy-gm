# Week 7 2026: full slate predictions

**How to read this.** Two simulation tracks, always labeled: MARKET-ANCHORED (nflverse spread/total as the team-points prior) and MODEL-ONLY (ratings and weather, no lines). Player numbers are the market-anchored track unless stated. Props use DraftKings lines via ESPN: lines only, **no prices and no touchdown prices**. Singles are screened at an assumed -110 after shrinking the model 50/50 toward 50%; touchdown and parlay prices are FAIR odds from the joint simulation, 'play at' adds a 12% cushion. The W4 and W5 postmortems found no edge over the books on yardage and count props and calibrated anytime-TD probabilities, so read everything as a ranked lean. TD v2 multipliers and the anytime-TD floor (0.06, DECISIONS #29-30) are live.

**Inputs used (UTC).** ESPN game-summary Outs (5 names per team cap, not the official inactives): 2026-10-25T15:31:34Z. Sleeper status overlay (newer Out replaces the NFL row): 2026-10-25T15:31:30+00:00. nflverse depth charts: 2026-10-25T12:30:46Z; nflverse injuries: no timestamp in the feed. Lines: ESPN/DraftKings fetched 2026-10-25T15:31Z (no prices; the per-line `last_updated_utc` stamps run ahead of the fetch time and their zone is unverified, so no recency claim is made from them). Official inactives: **not used** (the ESPN feed carries injuries, not the NFL inactive list). Code: git 0a4e3b3.

**Started or finished, excluded from picks:** NE@CHI, PIT@NO.

## 1. Predicted scores

| Game | Kickoff ET | Market (spread / total) | Market-anchored score | Win prob | Total | Model-only score | Model-only win | Fair spread |
|---|---|---|---|---|---|---|---|---|
| SF@ATL | 2026-10-25 13:00 | ATL +2.5 / 49.5 | SF 26.0, ATL 23.3 | SF 58% / ATL 42% | 49.2 | SF 25.8, ATL 22.4 | SF 59% | ATL +3.0 |
| CIN@BAL | 2026-10-25 13:00 | BAL +3.0 / 46.5 | CIN 24.7, BAL 21.8 | CIN 58% / BAL 42% | 46.5 | CIN 23.6, BAL 26.4 | CIN 42% | BAL +3.0 |
| TB@CAR | 2026-10-25 13:00 | CAR -3.0 / 44.5 | TB 20.6, CAR 23.8 | TB 41% / CAR 59% | 44.4 | TB 20.8, CAR 25.6 | TB 36% | CAR -3.0 |
| NYG@HOU | 2026-10-25 13:00 | HOU -10.5 / 42.5 | NYG 15.9, HOU 26.4 | NYG 21% / HOU 79% | 42.4 | NYG 19.8, HOU 25.1 | NYG 35% | HOU -11.0 |
| IND@MIN | 2026-10-25 13:00 | MIN -6.5 / 41.5 | IND 17.4, MIN 24.0 | IND 30% / MIN 70% | 41.4 | IND 20.6, MIN 24.4 | IND 38% | MIN -7.0 |
| MIA@NYJ | 2026-10-25 13:00 | NYJ -3.5 / 39.5 | MIA 17.9, NYJ 21.6 | MIA 39% / NYJ 61% | 39.5 | MIA 18.7, NYJ 22.3 | MIA 40% | NYJ -3.0 |
| CLE@TEN | 2026-10-25 13:00 | TEN +2.5 / 36.5 | CLE 19.4, TEN 17.0 | CLE 58% / TEN 42% | 36.4 | CLE 18.9, TEN 17.6 | CLE 54% | TEN +3.0 |
| DEN@ARI | 2026-10-25 16:05 | ARI +4.5 / 42.5 | DEN 23.4, ARI 19.1 | DEN 63% / ARI 37% | 42.5 | DEN 23.3, ARI 21.2 | DEN 57% | ARI +4.0 |
| GB@DET | 2026-10-25 16:25 | DET -3.5 / 55.5 | GB 26.1, DET 29.4 | GB 41% / DET 59% | 55.4 | GB 22.7, DET 27.8 | GB 36% | DET -3.0 |
| LA@LV | 2026-10-25 16:25 | LV +3.5 / 48.5 | LA 26.0, LV 22.4 | LA 60% / LV 40% | 48.4 | LA 24.9, LV 23.3 | LA 55% | LV +4.0 |
| KC@SEA | 2026-10-25 20:20 | SEA -3.0 / 42.5 | KC 19.6, SEA 22.7 | KC 41% / SEA 59% | 42.4 | KC 21.6, SEA 24.0 | KC 43% | SEA -3.0 |
| DAL@PHI | 2026-10-26 20:15 | PHI +4.5 / 43.5 | DAL 24.0, PHI 19.4 | DAL 63% / PHI 37% | 43.5 | DAL 23.2, PHI 23.9 | DAL 48% | PHI +4.0 |

Already played: NE@CHI final NE 24, CHI 30 (market CHI -3.0, total 50.5; projected 23.7-26.7).

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
| Jordan Love | GB | DET | 98% | 22.9 | 288.9 | 2.00 | 5.3 | 0.08 | 7% | 12.2 | 18.5 |
| Brock Purdy | SF | ATL | 100% | 20.3 | 217.3 | 1.82 | 17.8 | 0.20 | 19% | 12.2 | 18.0 |
| Matthew Stafford | LA | LV | 100% | 23.7 | 257.2 | 1.86 | 3.4 | 0.09 | 9% | 11.7 | 16.6 |
| Jared Goff | DET | GB | 100% | 22.3 | 231.9 | 1.79 | 4.7 | 0.12 | 11% | 11.4 | 16.2 |
| C.J. Stroud | HOU | NYG | 100% | 20.6 | 238.5 | 1.62 | 21.4 | 0.23 | 21% | 11.1 | 18.3 |
| Joe Burrow | CIN | BAL | 100% | 23.4 | 245.0 | 1.65 | 8.1 | 0.11 | 11% | 10.6 | 16.3 |
| Bo Nix | DEN | ARI | 100% | 18.6 | 212.1 | 1.49 | 11.4 | 0.22 | 20% | 10.3 | 15.5 |
| Bryce Young | CAR | TB | 98% | 21.5 | 252.3 | 1.59 | 8.4 | 0.15 | 14% | 10.2 | 16.2 |
| Kirk Cousins | LV | LA | 100% | 20.4 | 226.9 | 1.55 | 5.1 | 0.04 | 4% | 9.5 | 14.0 |
| Dak Prescott | DAL | PHI | 100% | 23.9 | 259.2 | 1.37 | 8.0 | 0.15 | 14% | 9.1 | 15.8 |
| Kyler Murray | MIN | IND | 100% | 16.7 | 191.4 | 1.32 | 14.2 | 0.19 | 17% | 9.1 | 14.3 |
| Sam Darnold | SEA | KC | 100% | 19.3 | 216.8 | 1.42 | 6.5 | 0.07 | 7% | 8.9 | 13.2 |
| Michael Penix Jr. | ATL | SF | 100% | 17.6 | 197.4 | 1.35 | 6.5 | 0.08 | 8% | 8.6 | 12.6 |
| Geno Smith | NYJ | MIA | 100% | 21.2 | 232.4 | 1.32 | 8.8 | 0.10 | 9% | 8.5 | 14.9 |

**Running backs**

| player | team | opp | p_active | rush_att_mean | rush_yds_mean | rush_td_mean | rec_mean | rec_yds_mean | rec_td_mean | any_td_pct | league_ev | ppr | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | 100% | 20.0 | 91.6 | 1.18 | 4.2 | 30.8 | 0.22 | 78% | 8.4 | 24.8 | 24.5 |
| Christian McCaffrey | SF | ATL | 100% | 14.5 | 66.7 | 0.58 | 6.5 | 54.4 | 0.43 | 66% | 6.1 | 24.7 | 24.5 |
| Kyren Williams | LA | LV | 100% | 13.4 | 72.1 | 0.65 | 5.4 | 43.4 | 0.35 | 65% | 6.0 | 22.9 | 22.7 |
| Bijan Robinson | ATL | SF | 100% | 20.6 | 101.3 | 0.78 | 4.0 | 30.2 | 0.19 | 64% | 5.8 | 22.9 | 22.7 |
| Javonte Williams | DAL | PHI | 100% | 13.7 | 54.1 | 0.79 | 2.7 | 17.4 | 0.10 | 61% | 5.3 | 15.2 | 15.1 |
| Woody Marks | HOU | NYG | 100% | 18.6 | 80.6 | 0.75 | 1.5 | 11.0 | 0.10 | 59% | 5.1 | 15.8 | 15.6 |
| Chase Brown | CIN | BAL | 100% | 15.3 | 58.3 | 0.53 | 4.0 | 26.3 | 0.19 | 53% | 4.3 | 16.8 | 16.6 |
| Kenneth Walker III | KC | SEA | 100% | 18.6 | 96.8 | 0.53 | 3.4 | 24.1 | 0.18 | 52% | 4.3 | 19.8 | 19.6 |
| Derrick Henry | BAL | CIN | 100% | 18.2 | 94.2 | 0.65 | 1.0 | 7.9 | 0.04 | 51% | 4.1 | 15.4 | 15.2 |
| Ashton Jeanty | LV | LA | 100% | 16.2 | 59.5 | 0.36 | 3.7 | 28.8 | 0.23 | 45% | 3.6 | 16.1 | 15.9 |
| Bucky Irving | TB | CAR | 95% | 14.9 | 78.7 | 0.47 | 3.2 | 22.3 | 0.14 | 47% | 3.5 | 17.0 | 15.9 |
| Chuba Hubbard | CAR | TB | 95% | 15.6 | 67.2 | 0.45 | 1.9 | 14.5 | 0.12 | 44% | 3.2 | 13.5 | 12.6 |
| Aaron Jones | MIN | IND | 100% | 16.2 | 72.7 | 0.40 | 2.3 | 17.1 | 0.13 | 42% | 3.2 | 14.4 | 14.2 |
| J.K. Dobbins | DEN | ARI | 100% | 13.5 | 55.2 | 0.49 | 1.1 | 9.2 | 0.04 | 42% | 3.2 | 10.7 | 10.6 |
| Emanuel Wilson | SEA | KC | 100% | 15.5 | 59.9 | 0.46 | 1.2 | 8.6 | 0.06 | 41% | 3.1 | 11.2 | 11.0 |
| Jonathan Taylor | IND | MIN | 95% | 17.8 | 77.1 | 0.47 | 2.8 | 20.5 | 0.06 | 42% | 3.0 | 15.7 | 14.7 |
| Dameon Pierce | PHI | DAL | 100% | 12.6 | 50.6 | 0.30 | 3.2 | 23.9 | 0.14 | 36% | 2.7 | 13.3 | 13.2 |
| MarShawn Lloyd | GB | DET | 100% | 8.7 | 30.1 | 0.30 | 1.9 | 14.4 | 0.13 | 36% | 2.6 | 8.9 | 8.8 |

**Wide receivers**

| player | team | opp | p_active | tgt_mean | rec_mean | rec_yds_mean | rec_td_mean | any_td_pct | league_ev | ppr | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Amon-Ra St. Brown | DET | GB | 100% | 10.4 | 6.5 | 67.5 | 0.63 | 48% | 3.8 | 17.0 | 16.9 |
| Matthew Golden | GB | DET | 96% | 8.5 | 4.9 | 74.8 | 0.61 | 47% | 3.5 | 16.1 | 15.4 |
| Jaxon Smith-Njigba | SEA | KC | 100% | 11.2 | 7.0 | 95.4 | 0.57 | 45% | 3.4 | 20.1 | 20.0 |
| Ja'Marr Chase | CIN | BAL | 100% | 9.0 | 6.1 | 66.7 | 0.50 | 40% | 3.0 | 15.8 | 15.7 |
| Christian Watson | GB | DET | 96% | 8.7 | 5.1 | 89.6 | 0.52 | 41% | 3.0 | 17.2 | 16.4 |
| Tetairoa McMillan | CAR | TB | 100% | 9.0 | 5.3 | 76.4 | 0.43 | 35% | 2.6 | 15.6 | 15.5 |
| CeeDee Lamb | DAL | PHI | 100% | 10.8 | 6.7 | 83.7 | 0.41 | 35% | 2.5 | 17.7 | 17.6 |
| Nico Collins | HOU | NYG | 96% | 7.7 | 4.8 | 65.3 | 0.37 | 35% | 2.4 | 14.1 | 13.5 |
| Drake London | ATL | SF | 100% | 8.6 | 5.2 | 75.5 | 0.36 | 31% | 2.2 | 15.1 | 15.0 |
| Justin Jefferson | MIN | IND | 95% | 7.0 | 4.3 | 58.3 | 0.36 | 31% | 2.0 | 12.4 | 11.7 |
| Zay Flowers | BAL | CIN | 100% | 7.6 | 5.2 | 75.9 | 0.32 | 29% | 2.0 | 14.9 | 14.9 |
| Courtland Sutton | DEN | ARI | 100% | 5.3 | 3.0 | 39.8 | 0.33 | 29% | 2.0 | 8.9 | 8.9 |
| Jalen Coker | CAR | TB | 100% | 7.0 | 4.4 | 57.3 | 0.32 | 28% | 1.9 | 12.1 | 12.1 |
| Tee Higgins | CIN | BAL | 100% | 7.4 | 4.8 | 67.0 | 0.32 | 28% | 1.9 | 13.4 | 13.4 |
| Jaylen Waddle | DEN | ARI | 95% | 6.8 | 4.0 | 52.3 | 0.32 | 28% | 1.8 | 11.2 | 10.6 |
| Garrett Wilson | NYJ | MIA | 100% | 7.0 | 5.0 | 58.6 | 0.31 | 27% | 1.8 | 12.7 | 12.6 |
| Puka Nacua | LA | LV | 50% | 10.8 | 7.1 | 91.5 | 0.56 | 45% | 1.8 | 20.0 | 9.9 |
| George Pickens | DAL | PHI | 95% | 8.8 | 5.4 | 72.0 | 0.31 | 27% | 1.8 | 14.5 | 13.7 |
| Tre Tucker | LV | LA | 100% | 5.7 | 3.3 | 45.7 | 0.27 | 24% | 1.7 | 9.6 | 9.6 |
| Malik Nabers | NYG | HOU | 100% | 8.4 | 5.0 | 65.6 | 0.27 | 24% | 1.6 | 13.2 | 13.2 |
| Michael Wilson | ARI | DEN | 100% | 8.3 | 4.7 | 48.9 | 0.26 | 23% | 1.6 | 11.1 | 11.1 |
| Wan'Dale Robinson | TEN | CLE | 100% | 7.3 | 4.3 | 42.7 | 0.26 | 23% | 1.6 | 10.2 | 10.2 |
| Darius Cooper | PHI | DAL | 100% | 2.7 | 1.6 | 21.9 | 0.25 | 23% | 1.5 | 5.3 | 5.3 |
| KC Concepcion | CLE | TEN | 95% | 6.2 | 4.0 | 43.2 | 0.24 | 24% | 1.5 | 10.1 | 9.5 |

**Tight ends**

| player | team | opp | p_active | tgt_mean | rec_mean | rec_yds_mean | rec_td_mean | any_td_pct | league_ev | ppr | dk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| George Kittle | SF | ATL | 100% | 9.3 | 6.6 | 76.9 | 0.76 | 54% | 4.6 | 18.8 | 18.8 |
| Sam LaPorta | DET | GB | 100% | 8.1 | 5.7 | 57.5 | 0.46 | 37% | 2.8 | 14.2 | 14.1 |
| Tucker Kraft | GB | DET | 100% | 7.4 | 4.9 | 56.8 | 0.44 | 37% | 2.8 | 13.4 | 13.4 |
| Brock Bowers | LV | LA | 95% | 9.6 | 6.0 | 67.0 | 0.45 | 37% | 2.5 | 15.4 | 14.5 |
| Colby Parkinson | LA | LV | 95% | 5.9 | 4.1 | 42.2 | 0.40 | 34% | 2.3 | 10.7 | 10.1 |
| Trey McBride | ARI | DEN | 100% | 11.8 | 7.6 | 66.0 | 0.37 | 32% | 2.2 | 16.5 | 16.4 |
| Dallas Goedert | PHI | DAL | 95% | 8.2 | 5.3 | 55.2 | 0.35 | 30% | 2.0 | 12.9 | 12.2 |
| Tyler Higbee | LA | LV | 100% | 7.0 | 4.7 | 52.7 | 0.33 | 29% | 2.0 | 12.0 | 12.0 |
| Kyle Pitts | ATL | SF | 100% | 5.1 | 3.4 | 32.7 | 0.32 | 27% | 1.9 | 8.5 | 8.5 |
| Isaiah Likely | NYG | HOU | 100% | 9.0 | 5.8 | 62.4 | 0.30 | 26% | 1.8 | 13.8 | 13.8 |
| AJ Barner | SEA | KC | 100% | 4.8 | 3.1 | 29.4 | 0.27 | 25% | 1.7 | 7.8 | 7.8 |
| T.J. Hockenson | MIN | IND | 95% | 5.0 | 3.4 | 33.8 | 0.30 | 26% | 1.7 | 8.6 | 8.1 |
| Dalton Schultz | HOU | NYG | 95% | 5.8 | 4.0 | 37.8 | 0.30 | 26% | 1.7 | 9.6 | 9.1 |
| Travis Kelce | KC | SEA | 96% | 8.0 | 5.4 | 55.4 | 0.28 | 25% | 1.6 | 12.6 | 12.0 |

**Kickers (this league: FG 3, XP 1; ranked by team implied points, the only validated signal; differences are within noise)**: DET 8.3; HOU 7.9; GB 7.8; LA 7.8; SF 7.8; CIN 7.6; DAL 7.5; MIN 7.5; CAR 7.5; DEN 7.5

## 6. Touchdown boards (anytime counts rushing and receiving TDs; fair odds; 'play at' = fair + 12% cushion)

**Top 30 anytime TD** (ranked by probability times chance he plays; 'prob' is conditional on playing)

| player | team | opp | pos | prob | adj | fair | playat | p_active | note |
|---|---|---|---|---|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | RB | 77.9% | 77.9% | -352 | -228 | 100% |  |
| Christian McCaffrey | SF | ATL | RB | 65.7% | 65.7% | -192 | -142 | 100% |  |
| Kyren Williams | LA | LV | RB | 65.5% | 65.5% | -190 | -141 | 100% |  |
| Bijan Robinson | ATL | SF | RB | 63.7% | 63.7% | -175 | -132 | 100% |  |
| Javonte Williams | DAL | PHI | RB | 60.7% | 60.7% | -154 | -118 | 100% | opp QB: fill-in QB (Tanner McKee) |
| Woody Marks | HOU | NYG | RB | 58.9% | 58.9% | -143 | -111 | 100% | opp QB: fill-in QB (J.J. McCarthy) |
| George Kittle | SF | ATL | TE | 54.3% | 54.3% | -119 | +106 | 100% |  |
| Chase Brown | CIN | BAL | RB | 52.6% | 52.6% | -111 | +113 | 100% | opp QB: fill-in QB (QB1 Out) |
| Kenneth Walker III | KC | SEA | RB | 52.3% | 52.3% | -110 | +114 | 100% |  |
| Derrick Henry | BAL | CIN | RB | 50.9% | 50.9% | -104 | +120 | 100% | fill-in QB (QB1 Out) |
| Amon-Ra St. Brown | DET | GB | WR | 47.6% | 47.6% | +110 | +135 | 100% |  |
| Ashton Jeanty | LV | LA | RB | 45.5% | 45.5% | +120 | +146 | 100% |  |
| Matthew Golden | GB | DET | WR | 46.7% | 44.7% | +114 | +140 | 96% |  |
| Jaxon Smith-Njigba | SEA | KC | WR | 44.7% | 44.7% | +124 | +151 | 100% |  |
| Bucky Irving | TB | CAR | RB | 46.9% | 44.6% | +113 | +139 | 95% | QB1 designation (start probability 65%) |
| Chuba Hubbard | CAR | TB | RB | 44.0% | 41.8% | +127 | +155 | 95% | opp QB: QB1 designation (start probability 65%) |
| Aaron Jones | MIN | IND | RB | 41.8% | 41.8% | +139 | +168 | 100% |  |
| J.K. Dobbins | DEN | ARI | RB | 41.7% | 41.7% | +140 | +169 | 100% |  |
| Emanuel Wilson | SEA | KC | RB | 41.4% | 41.4% | +141 | +170 | 100% |  |
| Ja'Marr Chase | CIN | BAL | WR | 39.9% | 39.9% | +151 | +181 | 100% | opp QB: fill-in QB (QB1 Out) |
| Jonathan Taylor | IND | MIN | RB | 41.9% | 39.8% | +139 | +167 | 95% |  |
| Christian Watson | GB | DET | WR | 41.0% | 39.3% | +144 | +173 | 96% |  |
| Sam LaPorta | DET | GB | TE | 37.5% | 37.5% | +167 | +199 | 100% |  |
| Tucker Kraft | GB | DET | TE | 37.2% | 37.2% | +168 | +201 | 100% |  |
| Dameon Pierce | PHI | DAL | RB | 36.3% | 36.3% | +175 | +209 | 100% | fill-in QB (Tanner McKee) |
| Ollie Gordon II | MIA | NYJ | RB | 36.0% | 36.0% | +178 | +211 | 100% |  |
| Tetairoa McMillan | CAR | TB | WR | 35.5% | 35.5% | +182 | +216 | 100% | opp QB: QB1 designation (start probability 65%) |
| Braelon Allen | NYJ | MIA | RB | 35.5% | 35.5% | +182 | +216 | 100% |  |
| CeeDee Lamb | DAL | PHI | WR | 34.8% | 34.8% | +187 | +222 | 100% | opp QB: fill-in QB (Tanner McKee) |
| Brock Bowers | LV | LA | TE | 36.5% | 34.6% | +174 | +207 | 95% |  |

**2+ TD (top 10)**

| player | team | opp | prob | fair |
|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | 41.5% | +141 |
| Christian McCaffrey | SF | ATL | 27.0% | +271 |
| Kyren Williams | LA | LV | 26.0% | +285 |
| Bijan Robinson | ATL | SF | 25.2% | +297 |
| Javonte Williams | DAL | PHI | 22.0% | +355 |
| Woody Marks | HOU | NYG | 20.8% | +381 |
| George Kittle | SF | ATL | 17.4% | +476 |
| Chase Brown | CIN | BAL | 15.9% | +527 |
| Kenneth Walker III | KC | SEA | 15.5% | +544 |
| Derrick Henry | BAL | CIN | 14.9% | +569 |

**First TD (top 10)**

| player | team | opp | prob | fair |
|---|---|---|---|---|
| Jahmyr Gibbs | DET | GB | 21.7% | +361 |
| Woody Marks | HOU | NYG | 20.0% | +400 |
| Kyren Williams | LA | LV | 18.5% | +441 |
| Javonte Williams | DAL | PHI | 17.8% | +461 |
| Christian McCaffrey | SF | ATL | 17.5% | +472 |
| Bijan Robinson | ATL | SF | 16.7% | +500 |
| Kenneth Walker III | KC | SEA | 15.9% | +529 |
| Chase Brown | CIN | BAL | 14.1% | +607 |
| Aaron Jones | MIN | IND | 14.0% | +614 |
| Jonathan Taylor | IND | MIN | 13.7% | +632 |

**Sneaky longshots** (8% to 25% anytime, active 90%+): Samaje Perine (CIN) 25% fair +306, take at +354+; Tre Tucker (LV) 24% fair +309, take at +358+; George Holani (SEA) 24% fair +313, take at +363+; Malik Nabers (NYG) 24% fair +318, take at +368+; Travis Kelce (KC) 25% fair +308, take at +357+; Michael Wilson (ARI) 23% fair +327, take at +378+; Wan'Dale Robinson (TEN) 23% fair +333, take at +385+; Malik Washington (MIA) 23% fair +342, take at +395+; Darius Cooper (PHI) 23% fair +343, take at +396+; KC Concepcion (CLE) 24% fair +321, take at +371+; Mike Gesicki (CIN) 23% fair +344, take at +398+; Jameson Williams (DET) 22% fair +346, take at +400+; Xavier Worthy (KC) 22% fair +350, take at +404+; Darren Waller (CAR) 23% fair +333, take at +385+; Cade Otton (TB) 22% fair +360, take at +415+; Ryan Flournoy (DAL) 22% fair +363, take at +419+; Brandin Cooks (SF) 21% fair +370, take at +427+; Jahan Dotson (ATL) 21% fair +370, take at +427+; Kaelon Black (SF) 21% fair +370, take at +427+; Harold Fannin Jr. (CLE) 21% fair +374, take at +431+

## 7. Single-line screen (DraftKings lines via ESPN, assumed -110)

451 lines screened: **27 PLAY** (17 receiving, tagged thin: W6 receiving lines hit 35 to 52 percent, Thursday 7 of 11), 61 LEAN (the 25 best shown). Pulled by rule: receiving LEANs, pass-volume UNDERs, UNDERs on a teammate of a player now Out or Questionable ('role change'). PLAY = shrunk probability about 55.4%+ (about 61% raw), active 95%+, side cleared in at least half of the player's games. 'Agree' = the model-only track picks the same side.

| label | game | player | market | side | line | model_p | shrunk | fair | log | agree | flag | caution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAY | CIN@BAL | Chase Brown | rush_att | OVER | 11.5 | 83% | 66% | -197 | 4/5 | yes |  | opp QB: BAL fill-in QB (QB1 Out) |
| PLAY | IND@MIN | Kyler Murray | rush_yds | UNDER | 25.5 | 83% | 66% | -197 | 3/4 | yes |  |  |
| PLAY (thin) | DEN@ARI | Jalen Brooks | rec_yds | UNDER | 16.5 | 79% | 65% | -183 | 2/3 | yes |  |  |
| PLAY | MIA@NYJ | Braelon Allen | rush_yds | UNDER | 74.5 | 78% | 64% | -180 | 4/6 | yes |  |  |
| PLAY (thin) | DEN@ARI | Tyler Allgeier | rec | UNDER | 2.5 | 77% | 63% | -174 | 5/6 | yes |  |  |
| PLAY | TB@CAR | Bryce Young | rush_yds | UNDER | 11.5 | 77% | 63% | -174 | 4/4 | yes |  | opp QB: TB QB1 designation (start probability 65%) |
| PLAY (thin) | NYG@HOU | Xavier Hutchinson | rec | OVER | 1.5 | 76% | 63% | -170 | 6/6 | yes |  | opp QB: NYG fill-in QB (J.J. McCarthy) |
| PLAY | GB@DET | Jordan Love | rush_yds | UNDER | 6.5 | 75% | 63% | -167 | 4/5 | yes |  |  |
| PLAY (thin) | NYG@HOU | Kayshon Boutte | rec_yds | OVER | 10.5 | 73% | 61% | -160 | 6/6 | yes |  | opp QB: NYG fill-in QB (J.J. McCarthy) |
| PLAY (thin) | LA@LV | Kyren Williams | rec | OVER | 3.5 | 72% | 61% | -158 | 3/6 | yes |  |  |
| PLAY (thin) | GB@DET | Amon-Ra St. Brown | rec_yds | UNDER | 84.5 | 72% | 61% | -157 | 4/5 | yes |  |  |
| PLAY (thin) | CIN@BAL | Ja'Marr Chase | rec | UNDER | 7.5 | 72% | 61% | -156 | 4/5 | yes |  | opp QB: BAL fill-in QB (QB1 Out) |
| PLAY | LA@LV | Kyren Williams | rush_att | UNDER | 15.5 | 71% | 61% | -153 | 4/6 | yes |  |  |
| PLAY (thin) | LA@LV | Davis Allen | rec | OVER | 0.5 | 70% | 60% | -150 | 4/5 | yes |  |  |
| PLAY (thin) | KC@SEA | Noah Gray | rec | OVER | 1.5 | 70% | 60% | -150 | 3/5 | yes |  |  |
| PLAY (thin) | TB@CAR | Chuba Hubbard | rec | UNDER | 2.5 | 70% | 60% | -150 | 3/5 | yes |  | opp QB: TB QB1 designation (start probability 65%) |
| PLAY (thin) | NYG@HOU | Marvin Harrison Jr. | rec | UNDER | 2.5 | 67% | 58% | -141 | 3/5 | yes |  | opp QB: NYG fill-in QB (J.J. McCarthy) |
| PLAY (thin) | DEN@ARI | Courtland Sutton | rec | UNDER | 3.5 | 66% | 58% | -137 | 6/6 | yes |  |  |
| PLAY (thin) | GB@DET | Jameson Williams | rec_yds | UNDER | 54.5 | 65% | 57% | -135 | 4/5 | yes |  |  |
| PLAY (thin) | LA@LV | Tyler Higbee | rec | OVER | 3.5 | 65% | 57% | -134 | 4/5 | yes |  |  |
| PLAY | KC@SEA | Kenneth Walker III | rush_yds | OVER | 80.5 | 64% | 57% | -133 | 4/5 | yes |  |  |
| PLAY (thin) | DEN@ARI | Trey McBride | rec | OVER | 6.5 | 63% | 57% | -130 | 6/6 | yes |  |  |
| PLAY | DEN@ARI | Bo Nix | rush_yds | UNDER | 10.5 | 63% | 57% | -130 | 6/6 | yes |  |  |
| PLAY | CLE@TEN | Cam Ward | rush_yds | UNDER | 10.5 | 63% | 56% | -129 | 4/6 | yes |  |  |
| PLAY (thin) | IND@MIN | Jauan Jennings | rec | UNDER | 1.5 | 61% | 56% | -125 | 4/4 | yes |  |  |
| PLAY | CLE@TEN | Cam Ward | pass_att | OVER | 30.5 | 61% | 55% | -124 | 4/6 | yes |  |  |
| PLAY (thin) | CIN@BAL | Samaje Perine | rec | UNDER | 1.5 | 61% | 55% | -124 | 3/5 | yes |  | opp QB: BAL fill-in QB (QB1 Out) |
| LEAN | DAL@PHI | Saquon Barkley | rush_yds | UNDER | 70.5 | 92% | 71% | -245 | 2/4 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | CLE@TEN | Deshaun Watson | rush_yds | UNDER | 29.5 | 84% | 67% | -205 | 3/6 | yes | model vs own record |  |
| LEAN | MIA@NYJ | Braelon Allen | rush_att | UNDER | 17.5 | 78% | 64% | -177 | 5/6 | yes | same bet as sibling line |  |
| LEAN | CIN@BAL | Tyler Huntley | rush_att | UNDER | 5.5 | 77% | 63% | -174 | 2/3 | yes |  | fill-in QB (QB1 Out) |
| LEAN | DEN@ARI | Jacoby Brissett | rush_yds | OVER | 6.5 | 77% | 63% | -174 | 4/6 | yes | red-team downgrade |  |
| LEAN | DAL@PHI | Javonte Williams | rush_att | UNDER | 16.5 | 77% | 63% | -173 | 4/6 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | CLE@TEN | Quinshon Judkins | rush_att | UNDER | 14.5 | 75% | 63% | -167 | 3/5 | yes | red-team downgrade |  |
| LEAN | CIN@BAL | Tyler Huntley | pass_yds | OVER | 197.5 | 73% | 61% | -158 | 1/3 | yes |  | fill-in QB (QB1 Out) |
| LEAN | SF@ATL | Michael Penix Jr. | pass_att | UNDER | 31.5 | 72% | 61% | -158 | 2/4 | yes | same bet as sibling line |  |
| LEAN | KC@SEA | Emmett Johnson | rush_yds | OVER | 8.5 | 72% | 61% | -155 | 3/4 | yes | red-team downgrade |  |
| LEAN | SF@ATL | Brock Purdy | rush_att | UNDER | 4.5 | 71% | 61% | -153 | 2/6 | yes | same bet as sibling line |  |
| LEAN | DAL@PHI | Dak Prescott | rush_yds | UNDER | 9.5 | 71% | 61% | -153 | 2/5 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | NYG@HOU | C.J. Stroud | rush_yds | OVER | 9.5 | 70% | 60% | -150 | 4/6 | yes | red-team downgrade | opp QB: NYG fill-in QB (J.J. McCarthy) |
| LEAN | DAL@PHI | Javonte Williams | rush_yds | UNDER | 64.5 | 70% | 60% | -149 | 5/6 | yes | same bet as sibling line | opp QB: PHI fill-in QB (Tanner McKee) |
| LEAN | TB@CAR | Chuba Hubbard | rush_att | UNDER | 17.5 | 69% | 59% | -146 | 2/5 | yes |  | opp QB: TB QB1 designation (start probability 65%) |
| LEAN | DAL@PHI | Tanner McKee | pass_cmp | OVER | 19.5 | 69% | 59% | -146 | 1/1 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | CLE@TEN | Tony Pollard | rush_att | UNDER | 17.5 | 69% | 59% | -146 | 5/6 | yes | red-team downgrade |  |
| LEAN | CIN@BAL | Chase Brown | rush_yds | OVER | 41.5 | 68% | 59% | -143 | 3/5 | yes | same bet as sibling line | opp QB: BAL fill-in QB (QB1 Out) |
| LEAN | GB@DET | Sione Vaki | rush_yds | OVER | 8.5 | 68% | 59% | -142 | 2/4 | yes | red-team downgrade |  |
| LEAN | NYG@HOU | Woody Marks | rush_att | OVER | 16.5 | 67% | 59% | -142 | 0/6 | yes |  | opp QB: NYG fill-in QB (J.J. McCarthy) |
| LEAN | NYG@HOU | Woody Marks | rush_yds | OVER | 63.5 | 66% | 58% | -139 | 0/6 | yes |  | opp QB: NYG fill-in QB (J.J. McCarthy) |
| LEAN | CLE@TEN | Quinshon Judkins | rush_yds | UNDER | 45.5 | 66% | 58% | -139 | 3/5 | yes | red-team downgrade |  |
| LEAN | DAL@PHI | Tanner McKee | pass_yds | OVER | 193.5 | 66% | 58% | -137 | 1/1 | yes | same bet as sibling line | fill-in QB (Tanner McKee) |
| LEAN | LA@LV | Blake Corum | rush_att | UNDER | 8.5 | 65% | 58% | -136 | 3/6 | yes | red-team downgrade |  |
| LEAN | SF@ATL | Brock Purdy | rush_yds | UNDER | 19.5 | 65% | 58% | -136 | 1/6 | yes | same bet as sibling line |  |

## 8. Parlays across the slate (fair odds; legs from different games are independent, same-game legs use the joint simulation)

Pool: PLAY/LEAN single-line legs (shrunk), anytime-TD legs (12-60%), QB 1+ and 2+ passing TD legs. Hit probability is after the single-leg shrink. A real same-game parlay usually pays less than the product of its legs, so only take it at or better than 'play at'. Singles are in section 7; the best single touchdown plays are in section 6.

### 2-leg

**Highest chance to hit**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| CIN@BAL: Chase Brown rush_att O11.5 + LA@LV: Matthew Stafford pass TD 1+ | 45.4% | 71.8% | +120 | +147 |
| CIN@BAL: Chase Brown rush_att O11.5 + GB@DET: Jordan Love pass TD 1+ | 45.4% | 71.8% | +120 | +147 |
| IND@MIN: Kyler Murray rush_yds U25.5 + LA@LV: Matthew Stafford pass TD 1+ | 45.4% | 71.8% | +120 | +147 |
| IND@MIN: Kyler Murray rush_yds U25.5 + GB@DET: Jordan Love pass TD 1+ | 45.4% | 71.7% | +120 | +147 |

**Touchdown-led (at least one TD leg, longer shot)**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 40.8% | 53.9% | +145 | +175 |
| CIN@BAL: Chase Brown rush_att O11.5 + GB@DET: Jordan Love pass TD 2+ | 36.8% | 50.4% | +172 | +204 |
| IND@MIN: Kyler Murray rush_yds U25.5 + GB@DET: Jordan Love pass TD 2+ | 36.8% | 50.4% | +172 | +204 |
| DEN@ARI: Jalen Brooks rec_yds U16.5 + GB@DET: Jordan Love pass TD 2+ | 35.8% | 48.3% | +179 | +212 |

### 3-leg

**Highest chance to hit**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + LA@LV: Matthew Stafford pass TD 1+ | 30.1% | 59.3% | +232 | +272 |
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + GB@DET: Jordan Love pass TD 1+ | 30.1% | 59.3% | +232 | +272 |
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + SF@ATL: Brock Purdy pass TD 1+ | 29.9% | 58.9% | +234 | +274 |
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + GB@DET: Jared Goff pass TD 1+ | 29.9% | 58.6% | +235 | +275 |

**Touchdown-led (at least one TD leg, longer shot)**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| CIN@BAL: Chase Brown rush_att O11.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 27.1% | 44.5% | +270 | +314 |
| IND@MIN: Kyler Murray rush_yds U25.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 27.1% | 44.5% | +270 | +314 |
| DEN@ARI: Jalen Brooks rec_yds U16.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 26.4% | 42.7% | +279 | +325 |
| MIA@NYJ: Braelon Allen rush_yds U74.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 26.2% | 42.3% | +282 | +327 |

### 4-leg

**Highest chance to hit**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + DEN@ARI: Jalen Brooks rec_yds U16.5 + LA@LV: Matthew Stafford pass TD 1+ | 19.4% | 47.0% | +414 | +476 |
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + DEN@ARI: Jalen Brooks rec_yds U16.5 + GB@DET: Jordan Love pass TD 1+ | 19.4% | 47.0% | +414 | +476 |
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + DEN@ARI: Jalen Brooks rec_yds U16.5 + SF@ATL: Brock Purdy pass TD 1+ | 19.4% | 46.6% | +417 | +479 |
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + MIA@NYJ: Braelon Allen rush_yds U74.5 + LA@LV: Matthew Stafford pass TD 1+ | 19.3% | 46.5% | +417 | +479 |

**Touchdown-led (at least one TD leg, longer shot)**

| Legs | Hit probability | Raw sim | Fair odds | Play at or better |
|---|---|---|---|---|
| CIN@BAL: Chase Brown rush_att O11.5 + IND@MIN: Kyler Murray rush_yds U25.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 17.9% | 36.8% | +457 | +524 |
| CIN@BAL: Chase Brown rush_att O11.5 + DEN@ARI: Jalen Brooks rec_yds U16.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 17.5% | 35.3% | +472 | +541 |
| IND@MIN: Kyler Murray rush_yds U25.5 + DEN@ARI: Jalen Brooks rec_yds U16.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 17.5% | 35.3% | +472 | +541 |
| CIN@BAL: Chase Brown rush_att O11.5 + MIA@NYJ: Braelon Allen rush_yds U74.5 + SF@ATL: George Kittle anytime TD + SF@ATL: Brock Purdy pass TD 1+ | 17.4% | 34.9% | +475 | +544 |

### Quarterback passing-TD ladder (calibrated market: the model beat the books here in W4; fair odds)

Raw simulation probability, with the 50/50-shrunk figure used in parlays in brackets. Treat anything above 85% raw as 'very likely', not a number to price. Backup QBs are not listed.

| QB | 1+ raw (shrunk) | 2+ raw (shrunk) |
|---|---|---|
| Matthew Stafford | 87% (68%) | 57% (54%) |
| Jordan Love | 87% (68%) | 61% (55%) |
| Brock Purdy | 86% (68%) | 56% (53%) |
| Jared Goff | 86% (68%) | 56% (53%) |
| C.J. Stroud | 83% (67%) | 51% (50%) |
| Joe Burrow | 83% (66%) | 51% (50%) |
| Kirk Cousins | 81% (65%) | 47% (49%) |
| Bryce Young | 80% (65%) | 47% (49%) |
| Bo Nix | 80% (65%) | 45% (48%) |
| Sam Darnold | 78% (64%) | 42% (46%) |
| Dak Prescott | 77% (63%) | 40% (45%) |
| Michael Penix Jr. | 76% (63%) | 40% (45%) |
| Geno Smith | 76% (63%) | 39% (45%) |
| Kyler Murray | 75% (63%) | 39% (44%) |
| Deshaun Watson | 68% (59%) | 30% (40%) |
| Jacoby Brissett | 67% (58%) | 28% (39%) |
| Patrick Mahomes | 67% (58%) | 29% (40%) |
| Cam Ward | 66% (58%) | 28% (39%) |
| Malik Willis | 60% (55%) | 22% (36%) |
| Daniel Jones | 45% (48%) | 11% (31%) |

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

4 players have posted lines but no projection row (not on the 2026 stats universe, injured/exempt, or name mismatch). Nothing is published for them:

| player | team | game | market |
|---|---|---|---|
| Christian Kirk | SF | SF@ATL | reception_yds, receptions |
| Josh Jacobs | GB | GB@DET | reception_yds, receptions, rush_attempts, rush_yds |
| Khalil Herbert | ATL | SF@ATL | rush_yds |
| Tank Dell | HOU | NYG@HOU | reception_yds, receptions |

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