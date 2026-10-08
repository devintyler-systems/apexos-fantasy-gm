# Week 5 2026: books vs model (22:10-22:15Z snapshot)

- Odds file: NFL_Week5_Odds.xlsx, 17 books, Odds-API format, timestamps US Pacific converted +7h to UTC, snapshot 22:10:45Z to 22:15:21Z, hashed in the base manifests.
- Base runs: market-anchored `2026_w05_market_20261008T222514Z`, model-only `2026_w05_model_20261008T222515Z`. Quarterback scenario run `2026_w05_market_20261008T222707Z` is NOT a base run.
- No-vig: two-way exact per book, averaged over books at the SAME line. First TD is one-sided, so the no-vig figure is a flat 10% haircut, labeled Estimated (first-TD books typically carry more than 10%, so the Estimated market number is biased high).
- Label rule (postmortem P0 #2): AGREE appears only where model and no-vig market are within 3 points. Nothing is labeled edge or confident. Gap = model minus market, in probability points, shown so you can judge it yourself.
- **Model-side level bias on counts.** On pass attempts, completions, rush attempts and receptions the model sits 4 to 15 points below the books on P(over). The books' lines match 2026 Weeks 1-4 actuals (QB attempts: line 32.54 vs actual 32.62; completions 20.86 vs 20.92), so this is the model, not a book mispricing. Read those gaps as bias, not opportunity. Logged for a backtest, no change made.
- Books list NO prop of any kind for CHI Caleb Williams or BAL Lamar Jackson, and post Bagent pass props and Huntley first TD. The base run keeps both at the fixed 98% (NFL report governs, no game status). Treat every CHI and BAL number as conditional on that.


---
## TB@DAL

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -8.5 | 48.5 | 80.3% |
| market track (sim) | -10.0 | 48.5 | 75.2% |
| model track (sim) | -6.0 | 51.5 | 65.0% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Javonte Williams (DAL) | 19.5% / 17.6% | 19.6% | -0.0 | +400 Bally Bet | 9 | AGREE |
| CeeDee Lamb (DAL) | 10.5% / 9.4% | 13.8% | -3.4 | +575 Bally Bet | 9 |  |
| Bucky Irving (TB) | 9.8% / 11.9% | 7.2% | +2.6 | +1200 DraftKings | 9 | AGREE |
| George Pickens (DAL) | 7.2% / 6.5% | 11.2% | -4.0 | +775 BetMGM | 9 |  |
| Ryan Flournoy (DAL) | 6.4% / 5.9% | 5.3% | +1.1 | +1600 DraftKings | 9 | AGREE |
| Jake Ferguson (DAL) | 5.7% / 5.1% | 7.5% | -1.8 | +1200 BetMGM | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Dak Prescott (DAL) | pass_att | 34.5 | 28.2% / 31.6% | 47.9% | -19.7 | +100 BetMGM | 8 |  |
| Dak Prescott (DAL) | pass_cmp | 23.5 | 38.2% / 41.0% | 51.5% | -13.4 | -114 DraftKings | 10 |  |
| CeeDee Lamb (DAL) | rec | 6.5 | 43.6% / 45.2% | 49.4% | -5.8 | +100 betPARX | 12 |  |
| George Pickens (DAL) | rec | 4.5 | 51.1% / 51.5% | 53.3% | -2.3 | -115 betPARX | 12 | AGREE |
| Jake Ferguson (DAL) | rec | 3.5 | 41.1% / 42.9% | 45.6% | -4.6 | +115 Bovada | 12 |  |
| Ryan Flournoy (DAL) | rec | 3.5 | 38.5% / 39.5% | 42.8% | -4.4 | +130 Bovada | 12 |  |
| Javonte Williams (DAL) | rec | 2.5 | 51.0% / 51.8% | 53.0% | -1.9 | -122 betPARX | 12 | AGREE |
| Javonte Williams (DAL) | rush_att | 16.5 | 29.8% / 27.5% | 49.2% | -19.5 | -105 theScore Bet | 9 |  |
| Tyler Goodson (DAL) | rush_att | 4.5 | 32.9% / 31.8% | 44.8% | -11.9 | +105 Fliff | 1 |  |
| Dak Prescott (DAL) | rush_att | 3.5 | 22.0% / 21.1% | 44.0% | -22.0 | +115 Hard Rock Bet (FL) | 4 |  |
| Jalon Daniels (TB) | pass_att | 28.5 | 87.9% / 85.5% | 51.6% | +36.3 | -115 BetMGM | 10 |  |
| Jalon Daniels (TB) | pass_cmp | 17.5 | 88.9% / 87.2% | 52.7% | +36.3 | -121 betPARX | 6 |  |
| Cade Otton (TB) | rec | 3.5 | 68.6% / 67.4% | 48.6% | +20.0 | +102 FanDuel | 12 |  |
| Chris Godwin (TB) | rec | 3.5 | 43.6% / 42.7% | 55.5% | -11.9 | -134 BetRivers | 12 |  |
| Emeka Egbuka (TB) | rec | 3.5 | 58.1% / 57.2% | 43.7% | +14.4 | +130 BetMGM | 11 |  |
| Bucky Irving (TB) | rec | 2.5 | 51.7% / 51.0% | 41.1% | +10.6 | +140 betPARX | 12 |  |
| Bucky Irving (TB) | rush_att | 13.5 | 43.2% / 45.9% | 49.5% | -6.3 | -108 DraftKings | 6 |  |
| Jalon Daniels (TB) | rush_att | 7.5 | 1.4% / 1.6% | 47.9% | -46.4 | +104 betPARX | 8 |  |
| Kenny Gainwell (TB) | rush_att | 3.5 | 48.8% / 50.0% | 45.8% | +3.0 | +100 Fliff | 1 |  |

---
## PHI@JAX

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -7.5 | 41.5 | 75.8% |
| market track (sim) | -7.0 | 41.5 | 71.6% |
| model track (sim) | -6.0 | 43.8 | 66.6% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Bhayshul Tuten (JAX) | 13.9% / 13.1% | 16.4% | -2.5 | +500 theScore Bet | 9 | AGREE |
| Parker Washington (JAX) | 8.0% / 7.5% | 12.0% | -4.0 | +650 DraftKings | 9 |  |
| Chris Rodriguez Jr. (JAX) | 7.2% / 6.7% | 5.6% | +1.6 | +1500 DraftKings | 9 | AGREE |
| Jakobi Meyers (JAX) | 6.4% / 6.2% | 6.9% | -0.6 | +1300 theScore Bet | 9 | AGREE |
| Brenton Strange (JAX) | 5.4% / 5.2% | 6.9% | -1.5 | +1400 Bally Bet | 9 | AGREE |
| Dontayvion Wicks (PHI) | 4.6% / 5.1% | 4.3% | +0.3 | +2200 DraftKings | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Trevor Lawrence (JAX) | pass_att | 29.5 | 29.8% / 32.3% | 51.6% | -21.8 | -118 DraftKings | 6 |  |
| Trevor Lawrence (JAX) | pass_cmp | 19.5 | 34.6% / 36.2% | 50.1% | -15.5 | -108 betPARX | 11 |  |
| Parker Washington (JAX) | rec | 4.5 | 40.6% / 41.1% | 52.5% | -11.9 | -123 BetOnline.ag | 12 |  |
| Brenton Strange (JAX) | rec | 3.5 | 52.2% / 52.0% | 46.5% | +5.7 | +112 FanDuel | 12 |  |
| Jakobi Meyers (JAX) | rec | 3.5 | 47.0% / 47.9% | 52.2% | -5.1 | -119 DraftKings | 12 |  |
| Brian Thomas Jr (JAX) | rec | 2.5 | 54.5% / 54.9% | 38.3% | +16.2 | +151 DraftKings | 9 |  |
| Bhayshul Tuten (JAX) | rush_att | 14.5 | 49.1% / 48.0% | 53.4% | -4.3 | -125 BetMGM | 5 |  |
| Chris Rodriguez Jr. (JAX) | rush_att | 6.5 | 58.6% / 57.3% | 52.4% | +6.2 | -125 Hard Rock Bet | 6 |  |
| Trevor Lawrence (JAX) | rush_att | 3.5 | 40.9% / 40.3% | 49.0% | -8.1 | -105 theScore Bet | 7 |  |
| Jalen Hurts (PHI) | pass_att | 31.5 | 33.1% / 31.1% | 48.2% | -15.2 | -101 BetOnline.ag | 8 |  |
| Jalen Hurts (PHI) | pass_cmp | 18.5 | 51.5% / 49.7% | 50.6% | +1.0 | -106 DraftKings | 11 | AGREE |
| Dontayvion Wicks (PHI) | rec | 3.5 | 29.2% / 29.2% | 55.0% | -25.7 | -140 theScore Bet | 2 |  |
| Makai Lemon (PHI) | rec | 3.5 | 24.4% / 24.5% | 53.6% | -29.2 | -130 theScore Bet | 2 |  |
| Will Shipley (PHI) | rec | 2.5 | 6.5% / 6.8% | 48.2% | -41.7 | +100 BetMGM | 9 |  |
| Will Shipley (PHI) | rush_att | 11.5 | 0.3% / 0.4% | 49.2% | -48.9 | -110 betPARX | 2 |  |
| Jalen Hurts (PHI) | rush_att | 6.5 | 37.0% / 37.7% | 46.9% | -9.9 | +107 BetOnline.ag | 8 |  |

---
## CHI@GB

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +1.5 | 45.5 | 47.0% |
| market track (sim) | +3.0 | 45.3 | 42.9% |
| model track (sim) | +3.0 | 46.9 | 41.2% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| D'Andre Swift (CHI) | 16.7% / 16.6% | 16.4% | +0.3 | +475 DraftKings | 7 | AGREE |
| Kyle Monangai (CHI) | 13.3% / 13.2% | 10.6% | +2.7 | +800 DraftKings | 5 | AGREE |
| MarShawn Lloyd (GB) | 8.9% / 8.9% | 12.0% | -3.1 | +825 BetMGM | 9 |  |
| Christian Watson (GB) | 8.4% / 8.4% | 7.5% | +0.9 | +1300 theScore Bet | 9 | AGREE |
| Matthew Golden (GB) | 7.2% / 7.0% | 6.4% | +0.8 | +1400 theScore Bet | 9 | AGREE |
| Tucker Kraft (GB) | 6.5% / 6.4% | 6.0% | +0.5 | +1500 theScore Bet | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Luther Burden III (CHI) | rec | 4.5 | 40.2% / 39.6% | 52.2% | -12.0 | -115 theScore Bet | 12 |  |
| Colston Loveland (CHI) | rec | 3.5 | 43.6% / 43.3% | 57.6% | -14.0 | -154 BetOnline.ag | 12 |  |
| Kalif Raymond (CHI) | rec | 3.5 | 44.9% / 44.1% | 42.7% | +2.2 | +130 theScore Bet | 12 | AGREE |
| Rome Odunze (CHI) | rec | 3.5 | 50.8% / 50.5% | 41.3% | +9.5 | +130 Hard Rock Bet (FL) | 11 |  |
| D'Andre Swift (CHI) | rush_att | 14.5 | 66.5% / 66.6% | 49.1% | +17.5 | -115 Fliff | 1 |  |
| Kyle Monangai (CHI) | rush_att | 11.5 | 53.9% / 54.7% | 53.1% | +0.9 | -130 theScore Bet | 1 | AGREE |
| Jordan Love (GB) | pass_att | 33.5 | 46.2% / 46.6% | 50.4% | -4.2 | -112 DraftKings | 8 |  |
| Jordan Love (GB) | pass_cmp | 20.5 | 39.6% / 39.9% | 51.8% | -12.2 | -118 BetMGM | 8 |  |
| Christian Watson (GB) | rec | 4.5 | 49.8% / 49.8% | 44.2% | +5.6 | +115 DraftKings | 12 |  |
| Matthew Golden (GB) | rec | 4.5 | 41.3% / 41.9% | 49.2% | -8.0 | +100 betPARX | 12 |  |
| Tucker Kraft (GB) | rec | 4.5 | 45.8% / 46.2% | 47.4% | -1.6 | +105 DraftKings | 12 | AGREE |
| MarShawn Lloyd (GB) | rec | 2.5 | 28.2% / 28.6% | 40.9% | -12.7 | +135 theScore Bet | 11 |  |

---
## CIN@MIA

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +6.5 | 42.5 | 27.1% |
| market track (sim) | +7.0 | 42.6 | 31.7% |
| model track (sim) | +3.0 | 44.6 | 42.9% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Chase Brown (CIN) | 16.9% / 14.8% | 18.4% | -1.5 | +390 DraftKings | 7 | AGREE |
| Ja'Marr Chase (CIN) | 9.6% / 8.8% | 14.8% | -5.1 | +510 Bally Bet | 3 |  |
| Ollie Gordon II (MIA) | 8.5% / 10.2% | 11.2% | -2.8 | +800 DraftKings | 7 | AGREE |
| Tee Higgins (CIN) | 7.6% / 6.9% | 15.0% | -7.4 | +500 Bally Bet | 3 |  |
| Malik Washington (MIA) | 6.5% / 7.6% | 5.3% | +1.2 | +1700 DraftKings | 7 | AGREE |
| Mike Gesicki (CIN) | 5.9% / 5.2% | 6.9% | -1.0 | +1300 Bally Bet | 7 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Joe Burrow (CIN) | pass_att | 33.5 | 53.7% / 58.6% | 47.9% | +5.8 | +100 theScore Bet | 6 |  |
| Joe Burrow (CIN) | pass_cmp | 23.5 | 66.6% / 69.4% | 50.3% | +16.3 | -105 BetMGM | 11 |  |
| Chase Brown (CIN) | rush_att | 16.5 | 37.2% / 33.7% | 51.4% | -14.2 | -120 DraftKings | 8 |  |
| Malik Willis (MIA) | pass_att | 28.5 | 44.6% / 41.1% | 48.8% | -4.2 | -105 theScore Bet | 7 |  |
| Malik Willis (MIA) | pass_cmp | 16.5 | 48.9% / 46.2% | 50.6% | -1.7 | -115 BetOnline.ag | 11 | AGREE |
| Malik Washington (MIA) | rec | 4.5 | 39.4% / 38.6% | 51.4% | -12.0 | -105 BetMGM | 12 |  |
| Greg Dulcich (MIA) | rec | 2.5 | 45.1% / 44.6% | 56.1% | -11.0 | -135 BetMGM | 12 |  |
| Ollie Gordon II (MIA) | rush_att | 11.5 | 52.7% / 55.5% | 46.6% | +6.1 | +105 BetOnline.ag | 6 |  |
| Malik Willis (MIA) | rush_att | 5.5 | 48.9% / 50.8% | 48.1% | +0.9 | -105 betPARX | 2 | AGREE |

---
## LV@NE

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.5 | 45.0 | 63.2% |
| market track (sim) | -4.0 | 45.6 | 60.6% |
| model track (sim) | -4.0 | 43.7 | 64.3% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Ashton Jeanty (LV) | 12.8% / 11.9% | 15.0% | -2.2 | +550 DraftKings | 9 | AGREE |
| Rhamondre Stevenson (NE) | 9.4% / 10.0% | 16.4% | -7.0 | +475 betPARX | 8 |  |
| TreVeyon Henderson (NE) | 8.8% / 9.4% | 16.4% | -7.5 | +480 betPARX | 8 |  |
| Romeo Doubs (NE) | 8.5% / 8.7% | 9.0% | -0.5 | +1100 theScore Bet | 9 | AGREE |
| Brock Bowers (LV) | 7.9% / 7.2% | 9.5% | -1.6 | +1100 theScore Bet | 9 | AGREE |
| Mack Hollins (NE) | 7.3% / 7.7% | 6.9% | +0.4 | +1200 betPARX | 3 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Kirk Cousins (LV) | pass_att | 33.5 | 31.6% / 33.0% | 51.0% | -19.4 | -112 BetOnline.ag | 10 |  |
| Kirk Cousins (LV) | pass_cmp | 21.5 | 38.4% / 39.5% | 52.1% | -13.7 | -118 BetMGM | 11 |  |
| Brock Bowers (LV) | rec | 6.5 | 41.8% / 42.8% | 48.5% | -6.8 | +105 Bovada | 12 |  |
| Ashton Jeanty (LV) | rec | 3.5 | 48.9% / 49.5% | 51.9% | -3.0 | -106 betPARX | 12 |  |
| Michael Mayer (LV) | rec | 3.5 | 52.6% / 52.8% | 51.0% | +1.6 | -109 betPARX | 12 | AGREE |
| Tre Tucker (LV) | rec | 3.5 | 37.9% / 38.2% | 45.9% | -8.0 | +115 Bovada | 12 |  |
| Ashton Jeanty (LV) | rush_att | 16.5 | 51.1% / 50.1% | 51.8% | -0.8 | -104 betPARX | 8 | AGREE |
| Drake Maye (NE) | pass_att | 29.5 | 35.8% / 34.8% | 50.9% | -15.2 | -113 betPARX | 10 |  |
| Drake Maye (NE) | pass_cmp | 19.5 | 27.4% / 26.6% | 50.1% | -22.6 | -103 betPARX | 11 |  |
| Hunter Henry (NE) | rec | 3.5 | 33.0% / 32.3% | 52.2% | -19.2 | -118 BetMGM | 12 |  |
| Romeo Doubs (NE) | rec | 3.5 | 48.6% / 47.7% | 56.5% | -7.9 | -147 BetOnline.ag | 12 |  |
| DeMario Douglas (NE) | rec | 2.5 | 39.5% / 39.3% | 49.9% | -10.4 | -107 betPARX | 8 |  |
| Drake Maye (NE) | rush_att | 5.5 | 27.3% / 27.6% | 56.3% | -29.1 | -150 betPARX | 2 |  |

---
## MIN@NO

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +2.5 | 41.5 | 44.3% |
| market track (sim) | +3.0 | 41.6 | 43.5% |
| model track (sim) | +1.0 | 43.3 | 47.6% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Aaron Jones (MIN) | 15.5% / 14.8% | 18.0% | -2.5 | +425 theScore Bet | 8 | AGREE |
| Alvin Kamara (NO) | 9.4% / 10.3% | 12.0% | -2.6 | +700 betPARX | 8 | AGREE |
| Chris Olave (NO) | 8.1% / 8.7% | 8.2% | -0.1 | +1300 theScore Bet | 8 | AGREE |
| Juwan Johnson (NO) | 8.0% / 8.5% | 5.6% | +2.4 | +1500 betPARX | 8 | AGREE |
| Justin Jefferson (MIN) | 7.8% / 7.5% | 9.5% | -1.7 | +850 DraftKings | 7 | AGREE |
| T.J. Hockenson (MIN) | 7.4% / 7.2% | 6.0% | +1.4 | +1500 theScore Bet | 8 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Kyler Murray (MIN) | pass_att | 31.5 | 16.9% / 17.7% | 51.0% | -34.2 | -112 betPARX | 9 |  |
| Kyler Murray (MIN) | pass_cmp | 20.5 | 23.6% / 23.9% | 51.8% | -28.2 | -116 BetOnline.ag | 11 |  |
| Aaron Jones (MIN) | rec | 3.5 | 29.3% / 28.7% | 40.5% | -11.1 | +135 Hard Rock Bet (FL) | 6 |  |
| Aaron Jones (MIN) | rush_att | 17.5 | 65.7% / 64.4% | 48.5% | +17.2 | -105 Hard Rock Bet | 6 |  |
| Tyler Shough (NO) | pass_att | 35.5 | 46.7% / 44.3% | 52.2% | -5.5 | -120 BetOnline.ag | 5 |  |
| Tyler Shough (NO) | pass_cmp | 22.5 | 39.3% / 38.7% | 53.0% | -13.8 | -114 BetOnline.ag | 7 |  |
| Chris Olave (NO) | rec | 6.5 | 44.8% / 44.1% | 47.3% | -2.5 | +105 Bovada | 12 | AGREE |
| Juwan Johnson (NO) | rec | 4.5 | 56.6% / 56.0% | 45.4% | +11.2 | +120 betPARX | 12 |  |
| Devaughn Vele (NO) | rec | 3.5 | 44.2% / 44.4% | 53.5% | -9.3 | -125 BetMGM | 12 |  |

---
## CLE@NYJ

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -2.5 | 39.5 | 54.8% |
| market track (sim) | -3.0 | 39.4 | 57.5% |
| model track (sim) | -1.0 | 41.5 | 53.1% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Quinshon Judkins (CLE) | 11.8% / 12.7% | 13.3% | -1.6 | +700 DraftKings | 9 | AGREE |
| Braelon Allen (NYJ) | 11.6% / 11.2% | 15.7% | -4.0 | +500 betPARX | 9 |  |
| Garrett Wilson (NYJ) | 8.3% / 7.7% | 11.2% | -3.0 | +750 DraftKings | 9 | AGREE |
| KC Concepcion (CLE) | 6.4% / 6.7% | 6.0% | +0.4 | +1500 theScore Bet | 9 | AGREE |
| Harold Fannin Jr. (CLE) | 5.7% / 6.2% | 8.2% | -2.5 | +1150 BetMGM | 9 | AGREE |
| Kenyon Sadiq (NYJ) | 5.3% / 4.9% | 7.2% | -1.9 | +1300 theScore Bet | 7 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Deshaun Watson (CLE) | pass_att | 31.5 | 31.0% / 30.5% | 48.0% | -17.0 | +100 theScore Bet | 6 |  |
| Deshaun Watson (CLE) | pass_cmp | 19.5 | 53.1% / 52.7% | 51.5% | +1.6 | -115 BetRivers | 10 | AGREE |
| Harold Fannin Jr. (CLE) | rec | 4.5 | 46.1% / 45.8% | 42.3% | +3.8 | +125 DraftKings | 11 |  |
| KC Concepcion (CLE) | rec | 4.5 | 46.3% / 45.8% | 44.5% | +1.8 | +125 betPARX | 12 | AGREE |
| Denzel Boston (CLE) | rec | 3.5 | 37.9% / 37.7% | 44.2% | -6.3 | +125 theScore Bet | 12 |  |
| Quinshon Judkins (CLE) | rec | 2.5 | 41.8% / 42.2% | 54.6% | -12.8 | -140 Hard Rock Bet (FL) | 4 |  |
| Quinshon Judkins (CLE) | rush_att | 15.5 | 38.4% / 39.2% | 52.5% | -14.1 | -122 betPARX | 5 |  |
| Deshaun Watson (CLE) | rush_att | 5.5 | 34.8% / 34.8% | 54.1% | -19.3 | -130 betPARX | 6 |  |
| Geno Smith (NYJ) | pass_att | 31.5 | 29.6% / 30.6% | 47.4% | -17.8 | +101 DraftKings | 6 |  |
| Geno Smith (NYJ) | pass_cmp | 20.5 | 38.3% / 39.1% | 47.8% | -9.5 | +104 betPARX | 10 |  |
| Garrett Wilson (NYJ) | rec | 6.5 | 29.6% / 29.6% | 43.3% | -13.7 | +125 BetOnline.ag | 12 |  |
| Braelon Allen (NYJ) | rush_att | 17.5 | 24.1% / 23.5% | 49.7% | -25.5 | +100 BetOnline.ag | 7 |  |

---
## IND@PIT

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -2.5 | 44.5 | 56.8% |
| market track (sim) | -3.0 | 44.6 | 57.2% |
| model track (sim) | -0.0 | 47.6 | 50.8% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Jonathan Taylor (IND) | 17.1% / 18.9% | 20.5% | -3.4 | +360 theScore Bet | 8 |  |
| Jaylen Warren (PIT) | 13.1% / 12.0% | 16.8% | -3.7 | +475 betPARX | 8 |  |
| DK Metcalf (PIT) | 7.0% / 6.6% | 10.0% | -3.0 | +1100 theScore Bet | 8 | AGREE |
| Rico Dowdle (PIT) | 6.6% / 6.2% | 8.6% | -2.0 | +950 betPARX | 3 | AGREE |
| Pat Freiermuth (PIT) | 5.7% / 5.4% | 5.3% | +0.4 | +1800 theScore Bet | 8 | AGREE |
| Tyler Warren (IND) | 4.9% / 5.5% | 6.9% | -2.0 | +1500 theScore Bet | 8 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Daniel Jones (IND) | pass_att | 31.5 | 35.4% / 32.5% | 50.3% | -14.9 | -110 BetOnline.ag | 4 |  |
| Daniel Jones (IND) | pass_cmp | 19.5 | 52.3% / 49.1% | 52.3% | +0.1 | -120 DraftKings | 9 | AGREE |
| Tyler Warren (IND) | rec | 5.5 | 43.2% / 41.8% | 43.3% | -0.1 | +123 betPARX | 12 | AGREE |
| Josh Downs (IND) | rec | 4.5 | 44.1% / 42.3% | 56.8% | -12.8 | -148 FanDuel | 8 |  |
| Keenan Allen (IND) | rec | 3.5 | 57.7% / 56.8% | 42.8% | +14.9 | +125 DraftKings | 11 |  |
| Jonathan Taylor (IND) | rec | 2.5 | 56.7% / 55.6% | 50.9% | +5.8 | -110 FanDuel | 11 |  |
| Jonathan Taylor (IND) | rush_att | 19.5 | 43.0% / 44.8% | 49.8% | -6.8 | -110 betPARX | 7 |  |
| Aaron Rodgers (PIT) | pass_att | 34.5 | 46.0% / 48.7% | 51.3% | -5.2 | -113 betPARX | 10 |  |
| Aaron Rodgers (PIT) | pass_cmp | 21.5 | 39.2% / 41.5% | 48.7% | -9.5 | -105 Hard Rock Bet (FL) | 8 |  |
| DK Metcalf (PIT) | rec | 4.5 | 44.6% / 45.4% | 43.9% | +0.7 | +120 Fliff | 11 | AGREE |
| Pat Freiermuth (PIT) | rec | 3.5 | 35.4% / 36.0% | 44.1% | -8.7 | +120 BetMGM | 12 |  |
| Roman Wilson (PIT) | rec | 3.5 | 23.5% / 24.6% | 45.2% | -21.7 | +120 theScore Bet | 12 |  |
| Darnell Washington (PIT) | rec | 2.5 | 26.4% / 27.6% | 41.8% | -15.4 | +132 betPARX | 11 |  |
| Germie Bernard (PIT) | rec | 2.5 | 10.2% / 10.2% | 38.6% | -28.4 | +147 DraftKings | 8 |  |
| Michael Pittman Jr. (PIT) | rec | 2.5 | 53.2% / 53.7% | 49.0% | +4.2 | -110 theScore Bet | 1 |  |

---
## HOU@TEN

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +7.5 | 38.0 | 23.5% |
| market track (sim) | +7.0 | 37.5 | 28.9% |
| model track (sim) | +3.0 | 40.5 | 40.7% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| David Montgomery (HOU) | 15.0% / 13.0% | 15.0% | -0.0 | +550 DraftKings | 9 | AGREE |
| Woody Marks (HOU) | 10.9% / 9.5% | 10.0% | +0.9 | +900 DraftKings | 9 | AGREE |
| Tony Pollard (TEN) | 10.6% / 13.4% | 9.0% | +1.6 | +1100 theScore Bet | 9 | AGREE |
| Nico Collins (HOU) | 8.2% / 7.1% | 13.8% | -5.7 | +600 DraftKings | 9 |  |
| Dalton Schultz (HOU) | 5.3% / 4.6% | 9.0% | -3.7 | +1100 theScore Bet | 9 |  |
| Tyjae Spears (TEN) | 5.0% / 6.2% | 3.9% | +1.1 | +2250 Hard Rock Bet (FL) | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| C.J. Stroud (HOU) | pass_att | 31.5 | 61.0% / 65.6% | 49.6% | +11.4 | -110 DraftKings | 8 |  |
| C.J. Stroud (HOU) | pass_cmp | 21.5 | 51.0% / 54.6% | 50.3% | +0.7 | -108 BetOnline.ag | 7 | AGREE |
| Nico Collins (HOU) | rec | 5.5 | 46.0% / 47.2% | 51.2% | -5.2 | -105 BetOnline.ag | 12 |  |
| Dalton Schultz (HOU) | rec | 4.5 | 41.9% / 43.5% | 43.6% | -1.7 | +120 FanDuel | 11 | AGREE |
| Kayshon Boutte (HOU) | rec | 2.5 | 43.7% / 44.3% | 44.0% | -0.3 | +124 FanDuel | 11 | AGREE |
| David Montgomery (HOU) | rush_att | 14.5 | 27.3% / 25.6% | 49.1% | -21.8 | -105 DraftKings | 4 |  |
| Woody Marks (HOU) | rush_att | 8.5 | 44.7% / 41.6% | 52.4% | -7.7 | -125 Fliff | 4 |  |
| C.J. Stroud (HOU) | rush_att | 2.5 | 43.5% / 42.7% | 58.3% | -14.8 | -175 Fliff | 1 |  |
| Cam Ward (TEN) | pass_att | 31.5 | 46.8% / 42.8% | 50.8% | -4.0 | -115 BetMGM | 8 |  |
| Cam Ward (TEN) | pass_cmp | 19.5 | 55.9% / 53.3% | 49.9% | +6.0 | -110 BetOnline.ag | 7 |  |
| Carnell Tate (TEN) | rec | 4.5 | 55.5% / 54.9% | 45.7% | +9.8 | +115 theScore Bet | 7 |  |
| Wan'Dale Robinson (TEN) | rec | 3.5 | 58.5% / 57.6% | 55.3% | +3.2 | -135 Hard Rock Bet | 10 |  |
| Gunnar Helm (TEN) | rec | 2.5 | 50.0% / 49.9% | 47.2% | +2.8 | +115 theScore Bet | 10 | AGREE |
| Tony Pollard (TEN) | rush_att | 14.5 | 44.8% / 48.1% | 47.7% | -2.9 | +102 DraftKings | 4 | AGREE |
| Cam Ward (TEN) | rush_att | 3.5 | 46.5% / 46.9% | 45.5% | +1.0 | +100 Fliff | 1 | AGREE |

---
## NYG@WAS

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -4.0 | 41.5 | 63.7% |
| market track (sim) | -4.0 | 41.2 | 60.4% |
| model track (sim) | -0.0 | 45.4 | 51.5% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Stefon Diggs (WAS) | 9.5% / 8.7% | 10.6% | -1.1 | +1000 DraftKings | 7 | AGREE |
| Isaiah Likely (NYG) | 9.4% / 10.7% | 6.4% | +2.9 | +1300 DraftKings | 7 | AGREE |
| Terry McLaurin (WAS) | 7.6% / 7.1% | 10.0% | -2.4 | +850 DraftKings | 7 | AGREE |
| Cam Skattebo (NYG) | 7.5% / 8.9% | 12.9% | -5.4 | +650 DraftKings | 7 |  |
| Jacory Croskey-Merritt (WAS) | 6.2% / 5.3% | 12.9% | -6.6 | +650 DraftKings | 7 |  |
| Malik Nabers (NYG) | 6.2% / 7.0% | 7.5% | -1.3 | +1200 DraftKings | 7 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Jameis Winston (NYG) | pass_att | 31.5 | 21.3% / 19.2% | 47.9% | -26.6 | +100 theScore Bet | 9 |  |
| Jameis Winston (NYG) | pass_cmp | 18.5 | 43.8% / 41.1% | 50.3% | -6.5 | -113 DraftKings | 10 |  |
| Malik Nabers (NYG) | rec | 5.5 | 18.4% / 18.4% | 43.6% | -25.2 | +122 BetOnline.ag | 10 |  |
| Isaiah Likely (NYG) | rec | 4.5 | 56.0% / 54.0% | 47.9% | +8.1 | +106 FanDuel | 11 |  |
| Cam Skattebo (NYG) | rec | 2.5 | 36.6% / 35.9% | 41.3% | -4.7 | +135 Hard Rock Bet | 7 |  |
| Malachi Fields (NYG) | rec | 2.5 | 46.6% / 45.5% | 42.0% | +4.6 | +128 betPARX | 11 |  |
| Cam Skattebo (NYG) | rush_att | 15.5 | 29.7% / 31.2% | 51.1% | -21.4 | -114 BetOnline.ag | 5 |  |
| Jayden Daniels (WAS) | pass_att | 29.5 | 55.5% / 58.6% | 50.9% | +4.7 | -115 BetOnline.ag | 10 |  |
| Jayden Daniels (WAS) | pass_cmp | 17.5 | 57.7% / 59.8% | 52.7% | +5.0 | -121 betPARX | 6 |  |
| Jacory Croskey-Merritt (WAS) | rush_att | 13.5 | 14.6% / 13.3% | 50.2% | -35.6 | -110 BetOnline.ag | 7 |  |
| Jayden Daniels (WAS) | rush_att | 6.5 | 18.8% / 18.2% | 47.7% | -28.9 | +100 betPARX | 8 |  |

---
## DEN@LAC

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +3.5 | 42.0 | 38.0% |
| market track (sim) | +4.0 | 41.5 | 39.6% |
| model track (sim) | -0.0 | 41.2 | 48.0% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| J.K. Dobbins (DEN) | 12.4% / 11.1% | 12.0% | +0.4 | +650 DraftKings | 9 | AGREE |
| Omarion Hampton (LAC) | 9.8% / 11.1% | 11.2% | -1.4 | +850 DraftKings | 9 | AGREE |
| RJ Harvey (DEN) | 8.5% / 7.9% | 9.0% | -0.5 | +1100 theScore Bet | 9 | AGREE |
| Courtland Sutton (DEN) | 6.3% / 5.9% | 8.6% | -2.3 | +1200 BetMGM | 9 | AGREE |
| Jaylen Waddle (DEN) | 5.2% / 4.8% | 9.0% | -3.8 | +1100 theScore Bet | 9 |  |
| Keaton Mitchell (LAC) | 4.8% / 5.3% | 6.4% | -1.6 | +1500 theScore Bet | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Bo Nix (DEN) | pass_att | 33.5 | 36.0% / 37.7% | 50.1% | -14.1 | -110 DraftKings | 10 |  |
| Bo Nix (DEN) | pass_cmp | 21.5 | 33.9% / 34.8% | 49.0% | -15.2 | -105 theScore Bet | 11 |  |
| Jaylen Waddle (DEN) | rec | 4.5 | 27.1% / 27.8% | 48.7% | -21.6 | +105 theScore Bet | 12 |  |
| RJ Harvey (DEN) | rec | 4.5 | 31.5% / 31.3% | 42.1% | -10.7 | +125 theScore Bet | 7 |  |
| Courtland Sutton (DEN) | rec | 3.5 | 34.0% / 34.6% | 45.4% | -11.4 | +115 BetOnline.ag | 12 |  |
| Evan Engram (DEN) | rec | 2.5 | 43.3% / 43.8% | 41.2% | +2.0 | +135 BetOnline.ag | 12 | AGREE |
| J.K. Dobbins (DEN) | rush_att | 13.5 | 46.3% / 44.5% | 51.1% | -4.8 | -110 BetOnline.ag | 8 |  |
| Bo Nix (DEN) | rush_att | 4.5 | 29.8% / 28.9% | 46.6% | -16.7 | +105 theScore Bet | 5 |  |
| Justin Herbert (LAC) | pass_att | 30.5 | 45.4% / 42.7% | 48.2% | -2.8 | +100 theScore Bet | 9 | AGREE |
| Justin Herbert (LAC) | pass_cmp | 18.5 | 42.6% / 41.6% | 49.6% | -7.0 | -110 DraftKings | 11 |  |
| Omarion Hampton (LAC) | rush_att | 10.5 | 84.2% / 85.4% | 50.6% | +33.6 | -105 BetOnline.ag | 8 |  |
| Keaton Mitchell (LAC) | rush_att | 7.5 | 29.3% / 30.2% | 51.5% | -22.2 | -110 BetOnline.ag | 7 |  |
| Justin Herbert (LAC) | rush_att | 5.5 | 24.4% / 25.3% | 45.0% | -20.6 | +110 Fliff | 2 |  |

---
## DET@ARI

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +5.5 | 54.5 | 31.6% |
| market track (sim) | +6.0 | 54.4 | 35.5% |
| model track (sim) | +3.0 | 53.3 | 43.9% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Jahmyr Gibbs (DET) | 21.5% / 19.8% | 23.4% | -1.9 | +300 theScore Bet | 9 | AGREE |
| Amon-Ra St. Brown (DET) | 10.9% / 10.5% | 13.3% | -2.4 | +700 BetMGM | 9 | AGREE |
| Jeremiyah Love (ARI) | 9.5% / 10.3% | 12.9% | -3.4 | +900 BetMGM | 9 |  |
| Sam LaPorta (DET) | 9.0% / 8.3% | 6.9% | +2.1 | +1400 theScore Bet | 9 | AGREE |
| Trey McBride (ARI) | 8.4% / 9.1% | 8.2% | +0.3 | +1100 theScore Bet | 9 | AGREE |
| Michael Wilson (ARI) | 6.8% / 7.5% | 6.4% | +0.4 | +1400 DraftKings | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett (ARI) | pass_att | 37.5 | 28.9% / 25.5% | 50.7% | -21.8 | +100 betPARX | 9 |  |
| Jacoby Brissett (ARI) | pass_cmp | 25.5 | 36.2% / 34.2% | 48.6% | -12.4 | -105 Hard Rock Bet | 7 |  |
| Trey McBride (ARI) | rec | 7.5 | 58.4% / 57.0% | 54.8% | +3.5 | -125 theScore Bet | 12 |  |
| Michael Wilson (ARI) | rec | 5.5 | 44.1% / 43.5% | 56.6% | -12.5 | -140 DraftKings | 10 |  |
| Jeremiyah Love (ARI) | rec | 2.5 | 42.6% / 42.3% | 46.5% | -3.8 | +116 betPARX | 11 |  |
| Kendrick Bourne (ARI) | rec | 2.5 | 49.5% / 49.2% | 44.7% | +4.8 | +120 betPARX | 12 |  |
| Marvin Harrison Jr. (ARI) | rec | 2.5 | 50.8% / 51.0% | 55.2% | -4.4 | -140 Hard Rock Bet | 12 |  |
| Jeremiyah Love (ARI) | rush_att | 11.5 | 68.0% / 70.6% | 51.7% | +16.3 | -120 Hard Rock Bet (FL) | 6 |  |
| Tyler Allgeier (ARI) | rush_att | 6.5 | 55.1% / 57.4% | 52.3% | +2.8 | -117 DraftKings | 6 | AGREE |
| Jared Goff (DET) | pass_att | 34.5 | 37.1% / 39.6% | 49.4% | -12.4 | -105 DraftKings | 8 |  |
| Jared Goff (DET) | pass_cmp | 25.5 | 19.8% / 20.7% | 47.7% | -27.9 | +100 BetOnline.ag | 7 |  |
| Amon-Ra St. Brown (DET) | rec | 7.5 | 29.7% / 30.8% | 45.4% | -15.8 | +115 betPARX | 11 |  |
| Jahmyr Gibbs (DET) | rec | 4.5 | 37.5% / 37.3% | 52.2% | -14.7 | -115 theScore Bet | 12 |  |
| Sam LaPorta (DET) | rec | 4.5 | 60.0% / 60.6% | 56.4% | +3.7 | -143 betPARX | 12 |  |
| Jameson Williams (DET) | rec | 3.5 | 44.0% / 44.6% | 53.0% | -9.0 | -113 betPARX | 12 |  |
| Isaac TeSlaa (DET) | rec | 2.5 | 22.0% / 21.7% | 40.6% | -18.5 | +139 BetOnline.ag | 12 |  |
| Jahmyr Gibbs (DET) | rush_att | 19.5 | 49.6% / 46.5% | 50.2% | -0.6 | -110 DraftKings | 7 | AGREE |

---
## SF@SEA

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.0 | 46.0 | 60.3% |
| market track (sim) | -3.0 | 45.5 | 58.7% |
| model track (sim) | -2.0 | 48.1 | 54.8% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Jaxon Smith-Njigba (SEA) | 13.3% / 12.9% | 13.8% | -0.6 | +600 DraftKings | 9 | AGREE |
| Christian McCaffrey (SF) | 12.7% / 13.3% | 15.7% | -3.0 | +500 DraftKings | 9 | AGREE |
| Emanuel Wilson (SEA) | 11.1% / 10.6% | 15.0% | -3.9 | +525 betPARX | 9 |  |
| AJ Barner (SEA) | 6.7% / 6.6% | 5.6% | +1.1 | +1800 theScore Bet | 9 | AGREE |
| George Kittle (SF) | 6.6% / 6.9% | 7.5% | -0.9 | +1400 theScore Bet | 9 | AGREE |
| Mike Evans (SF) | 6.5% / 6.8% | 6.9% | -0.4 | +1300 theScore Bet | 9 | AGREE |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Sam Darnold (SEA) | pass_att | 30.5 | 37.0% / 39.2% | 50.9% | -13.9 | -107 betPARX | 10 |  |
| Sam Darnold (SEA) | pass_cmp | 19.5 | 46.6% / 48.1% | 53.3% | -6.8 | -129 betPARX | 9 |  |
| Jaxon Smith-Njigba (SEA) | rec | 6.5 | 52.7% / 53.8% | 52.4% | +0.3 | -121 DraftKings | 11 | AGREE |
| AJ Barner (SEA) | rec | 2.5 | 59.2% / 59.6% | 49.1% | +10.0 | +102 DraftKings | 12 |  |
| Cooper Kupp (SEA) | rec | 2.5 | 44.3% / 44.3% | 45.3% | -1.0 | +116 FanDuel | 12 | AGREE |
| Emanuel Wilson (SEA) | rush_att | 16.5 | 48.1% / 46.7% | 51.0% | -2.9 | -117 DraftKings | 5 | AGREE |
| Brock Purdy (SF) | pass_att | 32.5 | 20.5% / 19.9% | 49.2% | -28.7 | -105 Hard Rock Bet | 10 |  |
| Brock Purdy (SF) | pass_cmp | 20.5 | 37.2% / 36.3% | 51.4% | -14.2 | -116 DraftKings | 6 |  |
| Christian McCaffrey (SF) | rec | 4.5 | 46.8% / 46.0% | 53.0% | -6.1 | -125 FanDuel | 12 |  |
| George Kittle (SF) | rec | 4.5 | 43.6% / 42.6% | 50.4% | -6.8 | -106 FanDuel | 12 |  |
| Deebo Samuel (SF) | rec | 3.5 | 39.8% / 39.9% | 50.3% | -10.6 | -105 DraftKings | 11 |  |
| Mike Evans (SF) | rec | 3.5 | 55.9% / 56.1% | 58.5% | -2.5 | -155 theScore Bet | 10 | AGREE |
| Christian McCaffrey (SF) | rush_att | 14.5 | 32.9% / 33.6% | 50.9% | -18.1 | -115 DraftKings | 9 |  |

---
## BAL@ATL

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.5 | 43.5 | 60.9% |
| market track (sim) | -3.0 | 43.4 | 58.9% |
| model track (sim) | -0.0 | 48.3 | 49.3% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Bijan Robinson (ATL) | 21.4% / 19.5% | 23.1% | -1.6 | +300 DraftKings | 9 | AGREE |
| Derrick Henry (BAL) | 14.5% / 16.4% | 18.0% | -3.5 | +450 BetMGM | 9 |  |
| Brian Robinson Jr. (ATL) | 8.7% / 7.9% | 7.5% | +1.2 | +1200 Hard Rock Bet (FL) | 9 | AGREE |
| Zay Flowers (BAL) | 7.5% / 8.6% | 7.5% | +0.0 | +1300 theScore Bet | 9 | AGREE |
| Mark Andrews (BAL) | 5.4% / 5.9% | 6.0% | -0.6 | +1750 BetMGM | 9 | AGREE |
| Drake London (ATL) | 5.3% / 5.0% | 12.0% | -6.7 | +800 DraftKings | 9 |  |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. (ATL) | pass_att | 29.5 | 15.4% / 17.6% | 49.6% | -34.2 | -105 theScore Bet | 10 |  |
| Michael Penix Jr. (ATL) | pass_cmp | 18.5 | 27.3% / 29.7% | 47.8% | -20.5 | +102 DraftKings | 10 |  |
| Drake London (ATL) | rec | 5.5 | 31.7% / 32.8% | 54.9% | -23.2 | -130 BetOnline.ag | 11 |  |
| Bijan Robinson (ATL) | rec | 3.5 | 45.8% / 46.9% | 52.8% | -7.0 | -120 BetMGM | 12 |  |
| Kyle Pitts (ATL) | rec | 2.5 | 50.3% / 51.2% | 45.2% | +5.1 | +118 betPARX | 12 |  |
| Bijan Robinson (ATL) | rush_att | 18.5 | 41.2% / 39.5% | 51.4% | -10.2 | -117 DraftKings | 5 |  |
| Brian Robinson Jr. (ATL) | rush_att | 8.5 | 46.5% / 45.8% | 52.2% | -5.7 | -120 Hard Rock Bet | 4 |  |
| Zay Flowers (BAL) | rec | 5.5 | 50.3% / 49.3% | 47.4% | +2.9 | +108 betPARX | 12 | AGREE |
| Mark Andrews (BAL) | rec | 3.5 | 59.1% / 57.9% | 52.9% | +6.2 | -115 BetMGM | 12 |  |
| Derrick Henry (BAL) | rush_att | 20.5 | 40.5% / 42.1% | 49.4% | -8.9 | -108 DraftKings | 5 |  |

---
## BUF@LA

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.5 | 54.5 | 60.7% |
| market track (sim) | -3.0 | 54.3 | 58.4% |
| model track (sim) | -0.0 | 51.7 | 51.6% |

**First TD scorer** (model probability vs Estimated no-vig vs best price)

| Player | Model (mkt / model-only track) | Book est. no-vig | Gap | Best price | Books | |
|---|---|---|---|---|---|---|
| Kyren Williams (LA) | 15.4% / 14.5% | 15.0% | +0.4 | +500 DraftKings | 9 | AGREE |
| James Cook (BUF) | 14.2% / 14.9% | 12.0% | +2.2 | +650 DraftKings | 9 | AGREE |
| Davante Adams (LA) | 8.5% / 8.2% | 10.6% | -2.1 | +875 BetMGM | 9 | AGREE |
| Puka Nacua (LA) | 8.2% / 7.7% | 12.0% | -3.8 | +850 BetMGM | 9 |  |
| Blake Corum (LA) | 5.6% / 5.4% | 4.9% | +0.7 | +2000 theScore Bet | 9 | AGREE |
| Josh Allen (BUF) | 5.5% / 5.8% | 12.9% | -7.4 | +700 DraftKings | 9 |  |

**Count props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Books | |
|---|---|---|---|---|---|---|---|---|
| Josh Allen (BUF) | pass_att | 32.5 | 23.5% / 22.3% | 48.7% | -25.2 | +100 BetMGM | 7 |  |
| Josh Allen (BUF) | pass_cmp | 20.5 | 23.9% / 23.5% | 52.3% | -28.5 | -114 betPARX | 9 |  |
| Dalton Kincaid (BUF) | rec | 4.5 | 21.2% / 21.3% | 42.3% | -21.1 | +126 BetOnline.ag | 12 |  |
| Khalil Shakir (BUF) | rec | 4.5 | 29.8% / 29.8% | 43.3% | -13.5 | +116 FanDuel | 1 |  |
| Keon Coleman (BUF) | rec | 2.5 | 44.3% / 43.1% | 59.0% | -14.8 | -172 FanDuel | 1 |  |
| Ty Johnson (BUF) | rec | 2.5 | 24.4% / 24.2% | 37.1% | -12.8 | +152 FanDuel | 1 |  |
| James Cook (BUF) | rush_att | 17.5 | 34.2% / 36.1% | 47.3% | -13.1 | +100 DraftKings | 6 |  |
| Josh Allen (BUF) | rush_att | 7.5 | 21.1% / 21.7% | 51.5% | -30.4 | -114 DraftKings | 7 |  |
| Matthew Stafford (LA) | pass_att | 37.5 | 28.7% / 30.4% | 49.6% | -21.0 | -104 betPARX | 8 |  |
| Matthew Stafford (LA) | pass_cmp | 23.5 | 34.1% / 36.0% | 48.6% | -14.5 | -105 Hard Rock Bet | 7 |  |
| Puka Nacua (LA) | rec | 7.5 | 34.7% / 35.3% | 45.0% | -10.3 | +120 betPARX | 11 |  |
| Davante Adams (LA) | rec | 4.5 | 54.4% / 55.2% | 47.0% | +7.4 | +110 betPARX | 12 |  |
| Kyren Williams (LA) | rec | 2.5 | 55.0% / 56.2% | 56.3% | -1.3 | -140 BetMGM | 12 | AGREE |
| Tyler Higbee (LA) | rec | 2.5 | 43.6% / 44.6% | 54.2% | -10.6 | -138 FanDuel | 1 |  |
| Kyren Williams (LA) | rush_att | 15.5 | 35.4% / 34.3% | 47.0% | -11.7 | +100 Hard Rock Bet | 5 |  |