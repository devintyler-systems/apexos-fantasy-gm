# Week 12 forward test, Wednesday early prices: NOT PLAYS

**These are not plays.** The 5-point TD rule is retired (DECISIONS #84, #86). Each row is logged to `docs/weekly/forward_test_ledger.csv` so closing-line movement and results can be measured forward (#85: about +1 point of price movement toward the engine per bet over the control is the bar).

- **Snapshot:** live Odds API `player_anytime_td`, 8 books, pulled 2026-11-25 17:07Z (book timestamps 16:54-17:06Z); 16 credits, 2,597 remaining.
- **Engine:** market track, 2026 week 12, current defaults on branch `claude/odds-backfill-2023-25` (includes R-31 and the #86 board), manual-out applied (`tools/intake/w11_manual_out.py`, 197 rows; the rebuild after the rerun added none). Not a frozen run; `runs/weekly` untouched.
- **Rule:** anytime TD, raw engine-book gap 5-10 points, p_active >= 0.9, blend w 0.2. Book probability = mean of per-book de-vigged prices (`config/weekly/td_book_devig.json`). Best price across the 8 books.
- **Injury filter:** players with any entry on the week-12 injury report are excluded (3 of 22). On Wednesday only 10 teams had published a report (BUF, CHI, DAL, DEN, DET, GB, KC, LA, PHI, PIT); for the other teams the filter cannot exclude anyone yet, marked *report pending* below.
- **Injury PDF overlay:** not available in this container (operator PDFs are not here); nflverse injuries only.

| # | Game | Player | Team | Best price | Book | Snapshot UTC | Engine p | Book p (de-vig) | Gap | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CAR@TB | Bucky Irving | TB | -120 | FanDuel | 2026-11-25 17:06:48 | 0.572 | 0.474 | +9.8 | report pending |
| 2 | SEA@SF | AJ Barner | SEA | +320 | DraftKings | 2026-11-25 17:06:42 | 0.294 | 0.213 | +8.1 | report pending |
| 3 | DEN@PIT | Bo Nix | DEN | +550 | DraftKings | 2026-11-25 17:06:42 | 0.215 | 0.135 | +8.0 |  |
| 4 | GB@LA | Matthew Golden | GB | +185 | BetRivers | 2026-11-25 17:05:57 | 0.392 | 0.314 | +7.8 |  |
| 5 | WAS@ARI | Trey McBride | ARI | +175 | Fanatics | 2026-11-25 17:06:19 | 0.410 | 0.332 | +7.8 | report pending |
| 6 | KC@BUF | Xavier Worthy | KC | +500 | DraftKings | 2026-11-25 17:06:40 | 0.222 | 0.149 | +7.3 |  |
| 7 | DEN@PIT | Germie Bernard | PIT | +600 | BetMGM | 2026-11-25 17:04:15 | 0.210 | 0.139 | +7.2 |  |
| 8 | TEN@JAX | Jakobi Meyers | JAX | +170 | FanDuel | 2026-11-25 17:06:51 | 0.394 | 0.329 | +6.5 | report pending |
| 9 | NO@CIN | Mitchell Tinsley | CIN | +1500 | Fanatics | 2026-11-25 16:54:42 | 0.125 | 0.061 | +6.4 | report pending p>85/<15 flag |
| 10 | BAL@HOU | Jacoby Brissett | BAL | +1200 | DraftKings | 2026-11-25 17:05:51 | 0.138 | 0.075 | +6.3 | report pending p>85/<15 flag |
| 11 | GB@LA | Ronnie Rivers | LA | +2200 | FanDuel | 2026-11-25 17:06:45 | 0.104 | 0.044 | +6.0 |  p>85/<15 flag |
| 12 | PHI@DAL | Zach Ertz | PHI | +1600 | DraftKings | 2026-11-25 17:06:44 | 0.114 | 0.054 | +6.0 |  p>85/<15 flag |
| 13 | LV@CLE | Quinshon Judkins | CLE | +115 | FanDuel | 2026-11-25 17:06:47 | 0.463 | 0.405 | +5.8 | report pending |
| 14 | WAS@ARI | Stefon Diggs | WAS | +220 | Fanatics | 2026-11-25 17:06:19 | 0.359 | 0.303 | +5.7 | report pending |
| 15 | TEN@JAX | Brian Thomas Jr | JAX | +380 | Fanatics | 2026-11-25 17:06:19 | 0.240 | 0.183 | +5.7 | report pending |
| 16 | BAL@HOU | Woody Marks | HOU | +190 | Fanatics | 2026-11-25 17:06:21 | 0.407 | 0.350 | +5.6 | report pending |
| 17 | NO@CIN | Chase Brown | CIN | -125 | FanDuel | 2026-11-25 17:06:48 | 0.546 | 0.491 | +5.5 | report pending |
| 18 | NYG@IND | Isaiah Likely | NYG | +205 | DraftKings | 2026-11-25 17:06:40 | 0.351 | 0.298 | +5.4 | report pending |
| 19 | CAR@TB | AJ Dillon | CAR | +5000 | DraftKings | 2026-11-25 17:06:56 | 0.073 | 0.019 | +5.4 | report pending p>85/<15 flag |

Excluded (on the injury report): Colby Parkinson LA, Dak Prescott DAL, Davis Allen LA

Close price, close book probability and result are filled after each game (the close pull at kickoff minus 10 minutes is scheduled by the parent session).
