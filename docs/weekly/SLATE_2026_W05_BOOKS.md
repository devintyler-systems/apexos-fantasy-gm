# Week 5 2026: books vs model (22:10-22:15Z snapshot)

- Odds files: NFL_Week5_Odds.xlsx (first TD, receptions, pass attempts, completions, rush attempts) and NFL_Week5_Odds-AddOn.xlsx (anytime TD, passing, receiving and rushing yards). Odds-API format, timestamps US Pacific converted +7h to UTC; snapshots 22:10:45Z to 22:15:21Z and 22:37Z to 22:42Z. sha256 of both is recorded in the base manifests (`odds_xlsx`, `odds_xlsx_1`). Raw prices are not committed.
- Base runs: market-anchored `2026_w05_market_PENDING`, model-only `2026_w05_model_PENDING`. The scenario run `2026_w05_market_20261008T223635Z` (priced on the first workbook only) (CHI Williams and BAL Jackson forced Out) is NOT a base run even though its id sorts later.
- **12 book names on player props, 6 independent first-TD feeds and 8 to 11 independent feeds on the count markets** after collapsing books whose price sheets are identical (Hard Rock variants; several first-TD feeds). "Books" below means independent feeds. Thin rows (1 to 2 feeds) are shown but never tagged.
- No-vig: two-way exact per book, averaged over independent feeds at the SAME line. First TD is one-sided: the flat 10% haircut is shown as Estimated, and it is NOT reliable. Listed-field first-TD books actually carry 14% to 44% overround, so the Estimated no-vig column overstates the market. The ceiling column forces each feed's listed field to sum to 1, an upper bound that is still above the true no-vig (unlisted players also take probability). **No first-TD agreement is claimed.** Anytime TD is one-sided too, so its no-vig is also the flat 10% Estimated. Across 380 priced players model and books rank almost identically (correlation 0.94, model 2.8 points below the Estimated number on average), but with an Estimated level the safe claim is ranking agreement only.
- Label rule (postmortem P0 #2): AGREE appears only on count, yardage and anytime-TD rows, within 3 points, with at least 3 independent feeds, and not for a player the books do not list. Nothing is labeled edge or confident. Gap = model minus market in probability points, for you to read yourself. Model probabilities above 85% or below 15% are shown as "n/a (cap)": they are never printed beside a price.
- **Count props: the model sits below the books on P(over), by about 12 points on pass attempts, 8 on completions, 7 on RB rushing, 3 to 10 on receptions (WR/TE 2 to 4), and 19 on QB rushing (the projections carry no QB rush attempts at all, which is a defect).** Weeks 1-4 actuals do not settle it for pass attempts (over-rate 42%, between model 38% and books 50%, n=99); they match the books on completions and RB rushing. Read these gaps as a model level bias on volume, not as book mispricing and not as opportunity. Logged for a backtest, no change made.
- **Book-vs-report conflicts.** No book lists any prop of any kind for CHI Caleb Williams, BAL Lamar Jackson, PHI Saquon Barkley, PHI DeVonta Smith or NYJ Breece Hall, while the model keeps all five active (98%, 98%, 100%, 100%, 59%). The NFL report governs and has no game status for them, so the base run keeps them; their count props are suppressed below and anything on CHI, BAL, PHI and NYJ is conditional on them playing. Books post Bagent pass props and Huntley first TD.
- Your Gibbs quote checks out against the file: anytime TD DraftKings -450, FanDuel -450, BetRivers and BetOnline -500, Bovada -460, BetMGM -400 (best). Model 75.9% vs Estimated no-vig 72% to 75%. At -450 the break-even is 81.8%, so the bet itself is about -8% by the model: a fair number at a bad price.
- **Yardage.** Rush yards (the one market where a 50/50 blend slightly beat the market historically): model P(over) runs 6.5 points below the books while 2026 W1-4 actuals match the lines (35.2 line vs 34.9 actual), and the largest gaps sit on thin feeds, quarterbacks, and role mismatches (books price Philadelphia's Will Shipley at 35.5 yards because they apparently expect Barkley out). No rush-yard row is labeled.
- Tonight (TB@DAL): books price Jalon Daniels at 28.5 attempts / 17.5 completions; the model projects roughly 33 attempts and prices both overs above 85% (suppressed). Treat TB passing numbers as unreliable, the same team-volume overshoot as Week 4.


---
## TB@DAL

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -8.5 | 48.5 | 80.3% |
| market track (sim) | -10.0 | 48.5 | 75.2% |
| model track (sim) | -6.0 | 51.5 | 65.0% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Javonte Williams (DAL) | 66.1% / 65.0% | 68.7% | 61.8% | +4.3 | -185 BetMGM | 6 |  |
| CeeDee Lamb (DAL) | 43.2% / 42.6% | 54.2% | 48.8% | -5.6 | -111 BetMGM | 6 |  |
| Bucky Irving (TB) | 42.0% / 50.9% | 34.8% | 31.3% | +10.7 | +200 BetMGM | 6 |  |
| George Pickens (DAL) | 32.1% / 31.4% | 47.6% | 42.9% | -10.7 | +125 BetMGM | 6 |  |
| Ryan Flournoy (DAL) | 29.0% / 28.7% | 25.0% | 22.5% | +6.5 | +310 FanDuel | 6 |  |
| Jake Ferguson (DAL) | 26.2% / 25.3% | 31.8% | 28.6% | -2.4 | +225 BetMGM | 6 | AGREE |
| Emeka Egbuka (TB) | 20.6% / 25.4% | 27.8% | 25.0% | -4.4 | +290 BetMGM | 6 |  |
| Kenny Gainwell (TB) | 20.5% / 25.7% | 18.0% | 16.2% | +4.3 | +475 DraftKings | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Javonte Williams (DAL) | 19.5% / 17.6% | 22.0% | 19.8% | 18.2% | +400 Bally Bet | 6 |
| CeeDee Lamb (DAL) | 10.5% / 9.4% | 15.4% | 13.8% | 12.6% | +575 Bally Bet | 6 |
| Bucky Irving (TB) | 9.8% / 11.9% | 8.5% | 7.7% | 6.9% | +1200 DraftKings | 6 |
| George Pickens (DAL) | 7.2% / 6.5% | 12.5% | 11.2% | 10.2% | +775 BetMGM | 6 |
| Ryan Flournoy (DAL) | 6.4% / 5.9% | 6.1% | 5.5% | 5.0% | +1600 DraftKings | 6 |
| Jake Ferguson (DAL) | 5.7% / 5.1% | 8.3% | 7.5% | 6.8% | +1200 BetMGM | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Dak Prescott (DAL) | pass_att | 34.5 | 28.2% / 31.6% | 47.9% | -19.7 | +100 BetMGM | 7 |  |
| Dak Prescott (DAL) | pass_cmp | 23.5 | 38.2% / 41.0% | 51.6% | -13.4 | -114 DraftKings | 9 |  |
| Dak Prescott (DAL) | pass_yds | 270.5 | 26.1% / 27.3% | 50.0% | -23.9 | -112 DraftKings | 2 |  |
| CeeDee Lamb (DAL) | rec | 6.5 | 43.6% / 45.2% | 49.2% | -5.7 | +100 betPARX | 11 |  |
| George Pickens (DAL) | rec | 4.5 | 51.1% / 51.5% | 53.3% | -2.2 | -115 betPARX | 11 | AGREE |
| Jake Ferguson (DAL) | rec | 3.5 | 41.1% / 42.9% | 45.5% | -4.5 | +115 Bovada | 11 |  |
| Ryan Flournoy (DAL) | rec | 3.5 | 38.5% / 39.5% | 42.8% | -4.4 | +130 Bovada | 11 |  |
| Javonte Williams (DAL) | rec | 2.5 | 51.0% / 51.8% | 52.9% | -1.9 | -122 betPARX | 11 | AGREE |
| CeeDee Lamb (DAL) | rec_yds | 84.5 | 37.4% / 38.2% | 50.1% | -12.7 | -114 DraftKings | 4 |  |
| George Pickens (DAL) | rec_yds | 63.5 | 38.6% / 38.7% | 49.7% | -11.1 | -113 FanDuel | 2 |  |
| Ryan Flournoy (DAL) | rec_yds | 30.5 | 43.4% / 44.6% | 49.8% | -6.4 | -110 DraftKings | 2 |  |
| Jake Ferguson (DAL) | rec_yds | 25.5 | 46.0% / 46.9% | 49.9% | -3.9 | -111 DraftKings | 2 |  |
| Javonte Williams (DAL) | rush_att | 16.5 | 29.8% / 27.5% | 49.1% | -19.4 | -105 theScore Bet | 8 |  |
| Tyler Goodson (DAL) | rush_att | 4.5 | 32.9% / 31.8% | 44.8% | -11.9 | +105 Fliff | 1 |  |
| Dak Prescott (DAL) | rush_att | 3.5 | 22.0% / 21.1% | 44.1% | -22.1 | +115 Hard Rock Bet | 3 |  |
| Javonte Williams (DAL) | rush_yds | 66.5 | 26.8% / 25.8% | 50.2% | -23.5 | -111 BetMGM | 4 |  |
| Tyler Goodson (DAL) | rush_yds | 14.5 | 35.8% / 35.1% | 49.8% | -14.0 | -108 DraftKings | 5 |  |
| Dak Prescott (DAL) | rush_yds | 9.5 | 33.5% / 32.8% | 50.2% | -16.7 | -111 DraftKings | 5 |  |
| Jalon Daniels (TB) | pass_att | 28.5 | n/a (cap) | 51.5% |  | -115 BetMGM | 9 |  |
| Jalon Daniels (TB) | pass_cmp | 17.5 | n/a (cap) | 52.7% |  | -121 betPARX | 6 |  |
| Jalon Daniels (TB) | pass_yds | 182.5 | 79.3% / 77.6% | 50.2% | +29.2 | -111 DraftKings | 4 |  |
| Cade Otton (TB) | rec | 3.5 | 68.6% / 67.4% | 48.5% | +20.1 | +102 FanDuel | 11 |  |
| Chris Godwin (TB) | rec | 3.5 | 43.6% / 42.7% | 55.4% | -11.8 | -134 betPARX | 11 |  |
| Emeka Egbuka (TB) | rec | 3.5 | 58.1% / 57.2% | 43.6% | +14.5 | +130 BetMGM | 10 |  |
| Bucky Irving (TB) | rec | 2.5 | 51.7% / 51.0% | 41.1% | +10.6 | +140 betPARX | 11 |  |
| Emeka Egbuka (TB) | rec_yds | 35.5 | 64.5% / 64.1% | 49.7% | +14.9 | -109 DraftKings | 2 |  |
| Chris Godwin (TB) | rec_yds | 34.5 | 47.4% / 46.2% | 50.2% | -2.8 | -110 DraftKings | 3 | AGREE |
| Cade Otton (TB) | rec_yds | 29.5 | 71.3% / 69.8% | 50.6% | +20.7 | -113 FanDuel | 4 |  |
| Ted Hurst III (TB) | rec_yds | 16.5 | 68.7% / 68.2% | 50.1% | +18.6 | -113 FanDuel | 4 |  |
| Bucky Irving (TB) | rush_att | 13.5 | 43.2% / 45.9% | 49.4% | -6.2 | -108 DraftKings | 5 |  |
| Jalon Daniels (TB) | rush_att | 7.5 | n/a (cap) | 47.7% |  | +104 betPARX | 7 |  |
| Kenny Gainwell (TB) | rush_att | 3.5 | 48.8% / 50.0% | 45.8% | +3.0 | +100 Fliff | 1 |  |
| Bucky Irving (TB) | rush_yds | 52.5 | 57.3% / 59.2% | 50.5% | +6.8 | -113 FanDuel | 4 |  |
| Jalon Daniels (TB) | rush_yds | 44.5 | n/a (cap) | 50.2% |  | -112 DraftKings | 3 |  |
| Kenny Gainwell (TB) | rush_yds | 12.5 | 47.5% / 49.4% | 49.4% | -1.9 | -109 DraftKings | 5 | AGREE |
| Sean Tucker (TB) | rush_yds | 9.5 | 22.5% / 23.2% | 50.5% | -27.9 | -113 FanDuel | 4 |  |

---
## PHI@JAX

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -7.5 | 41.5 | 75.8% |
| market track (sim) | -7.0 | 41.5 | 71.6% |
| model track (sim) | -6.0 | 43.8 | 66.6% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Bhayshul Tuten (JAX) | 47.8% / 48.4% | 52.5% | 47.2% | +0.6 | -105 FanDuel | 6 | AGREE |
| Parker Washington (JAX) | 31.0% / 31.8% | 41.2% | 37.1% | -6.1 | +150 BetMGM | 6 |  |
| Chris Rodriguez Jr. (JAX) | 28.5% / 28.7% | 24.1% | 21.7% | +6.8 | +330 DraftKings | 6 |  |
| Jakobi Meyers (JAX) | 25.6% / 26.4% | 27.0% | 24.3% | +1.2 | +275 DraftKings | 6 | AGREE |
| Brenton Strange (JAX) | 22.3% / 22.7% | 25.6% | 23.1% | -0.8 | +310 BetRivers | 6 | AGREE |
| Dontayvion Wicks (PHI) | 19.5% / 23.1% | 23.8% | 21.4% | -2.0 | +350 DraftKings | 5 | AGREE |
| Brian Thomas Jr (JAX) | 19.3% / 19.7% | 22.0% | 19.8% | -0.5 | +370 DraftKings | 6 | AGREE |
| Dallas Goedert (PHI) | 15.2% / 17.1% | 23.3% | 20.9% | -5.8 | +330 DraftKings | 5 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Bhayshul Tuten (JAX) | 13.9% / 13.1% | 18.0% | 16.2% | 15.3% | +500 theScore Bet | 6 |
| Parker Washington (JAX) | 8.0% / 7.5% | 13.3% | 12.0% | 11.6% | +650 DraftKings | 6 |
| Chris Rodriguez Jr. (JAX) | 7.2% / 6.7% | 6.2% | 5.6% | 5.6% | +1500 DraftKings | 6 |
| Jakobi Meyers (JAX) | 6.4% / 6.2% | 7.7% | 6.9% | 6.6% | +1300 theScore Bet | 6 |
| Brenton Strange (JAX) | 5.4% / 5.2% | 7.7% | 6.9% | 6.6% | +1400 Bally Bet | 6 |
| Dontayvion Wicks (PHI) | 4.6% / 5.1% | 4.6% | 4.1% | 4.2% | +2200 DraftKings | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Trevor Lawrence (JAX) | pass_att | 29.5 | 29.8% / 32.3% | 51.7% | -21.9 | -118 DraftKings | 5 |  |
| Trevor Lawrence (JAX) | pass_cmp | 19.5 | 34.6% / 36.2% | 50.2% | -15.6 | -108 betPARX | 10 |  |
| Trevor Lawrence (JAX) | pass_yds | 225.5 | 32.5% / 33.0% | 50.0% | -17.5 | -114 FanDuel | 3 |  |
| Parker Washington (JAX) | rec | 4.5 | 40.6% / 41.1% | 52.5% | -11.9 | -123 BetOnline.ag | 11 |  |
| Brenton Strange (JAX) | rec | 3.5 | 52.2% / 52.0% | 46.6% | +5.6 | +112 FanDuel | 11 |  |
| Jakobi Meyers (JAX) | rec | 3.5 | 47.0% / 47.9% | 52.2% | -5.1 | -119 DraftKings | 11 |  |
| Brian Thomas Jr (JAX) | rec | 2.5 | 54.5% / 54.9% | 38.3% | +16.2 | +151 DraftKings | 9 |  |
| Parker Washington (JAX) | rec_yds | 60.5 | 37.9% / 38.2% | 50.0% | -12.1 | -114 FanDuel | 2 |  |
| Jakobi Meyers (JAX) | rec_yds | 42.5 | 41.4% / 42.3% | 49.9% | -8.4 | -110 DraftKings | 3 |  |
| Brenton Strange (JAX) | rec_yds | 34.5 | 48.7% / 49.5% | 49.9% | -1.2 | -111 DraftKings | 3 | AGREE |
| Brian Thomas Jr (JAX) | rec_yds | 23.5 | 61.5% / 62.4% | 50.9% | +10.6 | -116 DraftKings | 3 |  |
| Bhayshul Tuten (JAX) | rush_att | 14.5 | 49.1% / 48.0% | 53.3% | -4.1 | -125 BetMGM | 4 |  |
| Chris Rodriguez Jr. (JAX) | rush_att | 6.5 | 58.6% / 57.3% | 52.5% | +6.1 | -125 Hard Rock Bet | 5 |  |
| Trevor Lawrence (JAX) | rush_att | 3.5 | 40.9% / 40.3% | 49.0% | -8.1 | -105 theScore Bet | 6 |  |
| Bhayshul Tuten (JAX) | rush_yds | 67.5 | 41.2% / 41.3% | 49.8% | -8.6 | -110 DraftKings | 4 |  |
| Chris Rodriguez Jr. (JAX) | rush_yds | 26.5 | 51.9% / 51.1% | 50.3% | +1.6 | -114 FanDuel | 3 | AGREE |
| Trevor Lawrence (JAX) | rush_yds | 13.5 | 36.7% / 35.9% | 50.0% | -13.3 | -114 BetOnline.ag | 2 |  |
| Jalen Hurts (PHI) | pass_att | 31.5 | 33.1% / 31.1% | 48.3% | -15.2 | -101 BetOnline.ag | 7 |  |
| Jalen Hurts (PHI) | pass_cmp | 18.5 | 51.5% / 49.7% | 50.6% | +0.9 | -106 DraftKings | 10 | AGREE |
| Jalen Hurts (PHI) | pass_yds | 186.5 | 64.4% / 62.8% | 49.8% | +14.6 | -114 BetRivers | 2 |  |
| Dontayvion Wicks (PHI) | rec | 3.5 | 29.2% / 29.2% | 55.0% | -25.7 | -140 theScore Bet | 2 |  |
| Makai Lemon (PHI) | rec | 3.5 | 24.4% / 24.5% | 53.6% | -29.2 | -130 theScore Bet | 2 |  |
| Will Shipley (PHI) | rec | 2.5 | n/a (cap) | 48.2% |  | +100 BetMGM | 9 |  |
| Will Shipley (PHI) | rush_att | 11.5 | n/a (cap) | 49.2% |  | -110 betPARX | 2 |  |
| Jalen Hurts (PHI) | rush_att | 6.5 | 37.0% / 37.7% | 46.9% | -9.8 | +107 BetOnline.ag | 7 |  |
| Will Shipley (PHI) | rush_yds | 35.5 | n/a (cap) | 49.9% |  | -111 DraftKings | 3 |  |
| Jalen Hurts (PHI) | rush_yds | 26.5 | 34.4% / 34.8% | 50.1% | -15.7 | -113 DraftKings | 2 |  |

---
## CHI@GB

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +1.5 | 45.5 | 47.0% |
| market track (sim) | +3.0 | 45.3 | 42.9% |
| model track (sim) | +3.0 | 46.9 | 41.2% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| D'Andre Swift (CHI) | 58.2% / 58.8% | 58.3% | 52.5% | +5.7 | -135 DraftKings | 6 |  |
| Kyle Monangai (CHI) | 49.0% / 50.3% | 45.5% | 40.9% | +8.1 | +120 BetOnline.ag | 1 |  |
| MarShawn Lloyd (GB) | 36.9% / 38.2% | 46.5% | 41.9% | -5.0 | +125 BetMGM | 6 |  |
| Christian Watson (GB) | 35.4% / 36.4% | 36.7% | 33.0% | +2.4 | +185 BetRivers | 6 | AGREE |
| Matthew Golden (GB) | 31.2% / 31.9% | 32.3% | 29.0% | +2.2 | +220 FanDuel | 6 | AGREE |
| Tucker Kraft (GB) | 28.7% / 29.3% | 31.2% | 28.1% | +0.6 | +230 DraftKings | 6 | AGREE |
| Luther Burden III (CHI) | 24.3% / 25.6% | 30.8% | 27.7% | -3.3 | +230 DraftKings | 6 |  |
| Colston Loveland (CHI) | 20.0% / 20.8% | 30.3% | 27.3% | -7.3 | +250 BetRivers | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| D'Andre Swift (CHI) | 16.7% / 16.6% | 18.0% | 16.2% | 14.7% | +475 DraftKings | 4 |
| Kyle Monangai (CHI) | 13.3% / 13.2% | 11.4% | 10.3% | 10.1% | +800 DraftKings | 4 |
| MarShawn Lloyd (GB) | 8.9% / 8.9% | 11.4% | 10.3% | 10.6% | +825 BetMGM | 6 |
| Christian Watson (GB) | 8.4% / 8.4% | 7.7% | 6.9% | 6.8% | +1300 theScore Bet | 6 |
| Matthew Golden (GB) | 7.2% / 7.0% | 7.1% | 6.4% | 6.0% | +1400 theScore Bet | 6 |
| Tucker Kraft (GB) | 6.5% / 6.4% | 6.7% | 6.0% | 5.8% | +1500 theScore Bet | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Luther Burden III (CHI) | rec | 4.5 | 40.2% / 39.6% | 52.2% | -12.0 | -115 theScore Bet | 11 |  |
| Colston Loveland (CHI) | rec | 3.5 | 43.6% / 43.3% | 57.6% | -14.0 | -154 BetOnline.ag | 11 |  |
| Kalif Raymond (CHI) | rec | 3.5 | 44.9% / 44.1% | 42.7% | +2.2 | +130 theScore Bet | 11 | AGREE |
| Rome Odunze (CHI) | rec | 3.5 | 50.8% / 50.5% | 41.4% | +9.4 | +130 Hard Rock Bet | 10 |  |
| D'Andre Swift (CHI) | rec | 2.5 | 34.2% / 34.2% | 38.0% | -3.7 | +148 FanDuel | 2 |  |
| Luther Burden III (CHI) | rec_yds | 48.5 | 42.6% / 42.3% | 50.0% | -7.4 | -112 DraftKings | 4 |  |
| Rome Odunze (CHI) | rec_yds | 40.5 | 55.5% / 54.8% | 50.2% | +5.2 | -114 DraftKings | 3 |  |
| Colston Loveland (CHI) | rec_yds | 37.5 | 35.8% / 35.0% | 50.3% | -14.5 | -113 DraftKings | 5 |  |
| Kalif Raymond (CHI) | rec_yds | 28.5 | 55.4% / 54.9% | 50.3% | +5.1 | -114 FanDuel | 4 |  |
| D'Andre Swift (CHI) | rush_att | 14.5 | 66.5% / 66.6% | 49.1% | +17.5 | -115 Fliff | 1 |  |
| Kyle Monangai (CHI) | rush_att | 11.5 | 53.9% / 54.7% | 53.1% | +0.9 | -130 theScore Bet | 1 |  |
| Jordan Love (GB) | pass_att | 33.5 | 46.2% / 46.6% | 50.4% | -4.3 | -112 DraftKings | 7 |  |
| Jordan Love (GB) | pass_cmp | 20.5 | 39.6% / 39.9% | 51.9% | -12.4 | -118 BetMGM | 7 |  |
| Jordan Love (GB) | pass_yds | 235.5 | 47.9% / 48.4% | 50.0% | -2.1 | -111 DraftKings | 3 | AGREE |
| Christian Watson (GB) | rec | 4.5 | 49.8% / 49.8% | 44.2% | +5.6 | +115 DraftKings | 11 |  |
| Matthew Golden (GB) | rec | 4.5 | 41.3% / 41.9% | 49.2% | -7.9 | +100 betPARX | 11 |  |
| Tucker Kraft (GB) | rec | 4.5 | 45.8% / 46.2% | 47.3% | -1.5 | +105 DraftKings | 11 | AGREE |
| MarShawn Lloyd (GB) | rec | 2.5 | 28.2% / 28.6% | 40.9% | -12.7 | +135 theScore Bet | 10 |  |
| Christian Watson (GB) | rec_yds | 61.5 | 54.9% / 54.6% | 49.8% | +5.1 | -111 DraftKings | 3 |  |
| Matthew Golden (GB) | rec_yds | 56.5 | 44.5% / 45.4% | 50.1% | -5.6 | -114 DraftKings | 3 |  |
| Tucker Kraft (GB) | rec_yds | 49.5 | 45.1% / 45.1% | 50.1% | -5.0 | -113 DraftKings | 5 |  |
| Kaleb Johnson (GB) | rush_yds | 36.5 | 21.6% / 20.9% | 49.5% | -27.9 | -108 DraftKings | 5 |  |
| MarShawn Lloyd (GB) | rush_yds | 27.5 | 67.5% / 66.7% | 49.9% | +17.6 | -110 DraftKings | 5 |  |

---
## CIN@MIA

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +6.5 | 42.5 | 27.1% |
| market track (sim) | +7.0 | 42.6 | 31.7% |
| model track (sim) | +3.0 | 44.6 | 42.9% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Chase Brown (CIN) | 54.9% / 52.4% | 61.9% | 55.7% | -0.8 | -139 BetRivers | 6 | AGREE |
| Ja'Marr Chase (CIN) | 36.2% / 35.2% | 52.6% | 47.3% | -11.2 | +106 BetRivers | 3 |  |
| Ollie Gordon II (MIA) | 32.8% / 39.6% | 39.6% | 35.6% | -2.9 | +165 BetMGM | 6 | AGREE |
| Tee Higgins (CIN) | 30.2% / 28.7% | 51.9% | 46.7% | -16.6 | +107 BetRivers | 2 |  |
| Malik Washington (MIA) | 26.4% / 31.5% | 24.1% | 21.7% | +4.7 | +320 DraftKings | 6 |  |
| Mike Gesicki (CIN) | 23.7% / 22.3% | 28.2% | 25.4% | -1.6 | +310 BetRivers | 6 | AGREE |
| Samaje Perine (CIN) | 21.1% / 19.8% | 21.7% | 19.6% | +1.6 | +425 BetRivers | 6 | AGREE |
| Jaylen Wright (MIA) | 19.4% / 24.0% | 28.2% | 25.4% | -6.0 | +280 BetMGM | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Chase Brown (CIN) | 16.9% / 14.8% | 20.4% | 18.4% | 18.8% | +390 DraftKings | 4 |
| Ja'Marr Chase (CIN) | 9.6% / 8.8% | 16.4% | 14.8% | 10.2% | +510 Bally Bet | 1 |
| Ollie Gordon II (MIA) | 8.5% / 10.2% | 11.8% | 10.6% | 10.9% | +800 DraftKings | 4 |
| Tee Higgins (CIN) | 7.6% / 6.9% | 16.7% | 15.0% | 10.3% | +500 Bally Bet | 1 |
| Malik Washington (MIA) | 6.5% / 7.6% | 5.7% | 5.1% | 5.1% | +1700 DraftKings | 4 |
| Mike Gesicki (CIN) | 5.9% / 5.2% | 7.7% | 6.9% | 7.1% | +1300 Bally Bet | 4 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Joe Burrow (CIN) | pass_att | 33.5 | 53.7% / 58.6% | 47.9% | +5.8 | +100 theScore Bet | 6 |  |
| Joe Burrow (CIN) | pass_cmp | 23.5 | 66.6% / 69.4% | 50.4% | +16.2 | -105 BetMGM | 10 |  |
| Joe Burrow (CIN) | pass_yds | 242.5 | 58.2% / 60.3% | 50.2% | +8.0 | -114 FanDuel | 2 |  |
| Chase Brown (CIN) | rush_att | 16.5 | 37.2% / 33.7% | 51.5% | -14.3 | -120 DraftKings | 7 |  |
| Chase Brown (CIN) | rush_yds | 66.5 | 33.9% / 31.7% | 49.4% | -15.5 | -110 DraftKings | 3 |  |
| Samaje Perine (CIN) | rush_yds | 14.5 | 52.5% / 51.2% | 50.3% | +2.1 | -113 DraftKings | 5 | AGREE |
| Joe Burrow (CIN) | rush_yds | 8.5 | 30.1% / 28.8% | 50.1% | -20.1 | -114 DraftKings | 5 |  |
| Malik Willis (MIA) | pass_att | 28.5 | 44.6% / 41.1% | 48.8% | -4.1 | -105 theScore Bet | 6 |  |
| Malik Willis (MIA) | pass_cmp | 16.5 | 48.9% / 46.2% | 50.7% | -1.8 | -115 BetOnline.ag | 10 | AGREE |
| Malik Willis (MIA) | pass_yds | 191.5 | 59.4% / 56.5% | 49.9% | +9.5 | -111 DraftKings | 4 |  |
| Malik Washington (MIA) | rec | 4.5 | 39.4% / 38.6% | 51.3% | -12.0 | -105 BetMGM | 11 |  |
| Greg Dulcich (MIA) | rec | 2.5 | 45.1% / 44.6% | 56.1% | -11.0 | -135 BetMGM | 11 |  |
| Malik Washington (MIA) | rec_yds | 44.5 | 51.3% / 50.6% | 49.9% | +1.4 | -110 DraftKings | 3 | AGREE |
| Chris Bell (MIA) | rec_yds | 34.5 | 43.4% / 42.3% | 50.0% | -6.6 | -114 FanDuel | 1 |  |
| Greg Dulcich (MIA) | rec_yds | 24.5 | 51.8% / 51.3% | 50.9% | +0.8 | -116 DraftKings | 3 | AGREE |
| Kevin Coleman Jr. (MIA) | rec_yds | 18.5 | 51.4% / 51.1% | 50.0% | +1.4 | -114 FanDuel | 1 |  |
| Ollie Gordon II (MIA) | rush_att | 11.5 | 52.7% / 55.5% | 46.6% | +6.1 | +105 BetOnline.ag | 6 |  |
| Malik Willis (MIA) | rush_att | 5.5 | 48.9% / 50.8% | 48.1% | +0.9 | -105 betPARX | 2 |  |
| Ollie Gordon II (MIA) | rush_yds | 42.5 | 62.7% / 65.1% | 50.2% | +12.5 | -113 DraftKings | 4 |  |
| Malik Willis (MIA) | rush_yds | 33.5 | 37.3% / 38.3% | 49.5% | -12.2 | -108 DraftKings | 4 |  |
| Jaylen Wright (MIA) | rush_yds | 24.5 | 40.1% / 41.2% | 50.6% | -10.5 | -115 BetMGM | 4 |  |

---
## LV@NE

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.5 | 45.0 | 63.2% |
| market track (sim) | -4.0 | 45.6 | 60.6% |
| model track (sim) | -4.0 | 43.7 | 64.3% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Ashton Jeanty (LV) | 48.6% / 44.3% | 55.6% | 50.0% | -1.4 | -115 FanDuel | 6 | AGREE |
| Rhamondre Stevenson (NE) | 38.4% / 37.7% | 59.2% | 53.3% | -14.9 | -115 BetRivers | 5 |  |
| TreVeyon Henderson (NE) | 35.9% / 35.9% | 57.6% | 51.9% | -16.0 | -112 BetRivers | 5 |  |
| Romeo Doubs (NE) | 35.1% / 34.1% | 37.0% | 33.3% | +1.7 | +175 BetMGM | 6 | AGREE |
| Brock Bowers (LV) | 33.1% / 29.3% | 43.0% | 38.7% | -5.6 | +140 BetMGM | 6 |  |
| Mack Hollins (NE) | 30.5% / 30.9% | 30.1% | 27.1% | +3.4 | +245 BetRivers | 2 |  |
| DeMario Douglas (NE) | 21.8% / 21.3% | 24.1% | 21.7% | +0.1 | +525 BetRivers | 6 | AGREE |
| Hunter Henry (NE) | 20.8% / 20.1% | 34.5% | 31.0% | -10.2 | +260 BetRivers | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Ashton Jeanty (LV) | 12.8% / 11.9% | 16.0% | 14.4% | 12.4% | +550 DraftKings | 6 |
| Rhamondre Stevenson (NE) | 9.4% / 10.0% | 18.2% | 16.4% | 13.9% | +475 Bally Bet | 5 |
| TreVeyon Henderson (NE) | 8.8% / 9.4% | 18.2% | 16.4% | 13.9% | +480 Bally Bet | 5 |
| Romeo Doubs (NE) | 8.5% / 8.7% | 9.8% | 8.8% | 7.1% | +1100 theScore Bet | 6 |
| Brock Bowers (LV) | 7.9% / 7.2% | 9.5% | 8.6% | 7.0% | +1100 theScore Bet | 6 |
| Mack Hollins (NE) | 7.3% / 7.7% | 7.7% | 6.9% | 4.8% | +1200 Bally Bet | 1 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Kirk Cousins (LV) | pass_att | 33.5 | 31.6% / 33.0% | 51.0% | -19.4 | -112 BetOnline.ag | 9 |  |
| Kirk Cousins (LV) | pass_cmp | 21.5 | 38.4% / 39.5% | 52.1% | -13.7 | -118 BetMGM | 10 |  |
| Kirk Cousins (LV) | pass_yds | 232.5 | 38.5% / 39.3% | 50.0% | -11.6 | -111 DraftKings | 3 |  |
| Brock Bowers (LV) | rec | 6.5 | 41.8% / 42.8% | 48.5% | -6.7 | +105 theScore Bet | 11 |  |
| Ashton Jeanty (LV) | rec | 3.5 | 48.9% / 49.5% | 51.9% | -3.0 | -106 betPARX | 11 |  |
| Michael Mayer (LV) | rec | 3.5 | 52.6% / 52.8% | 51.0% | +1.6 | -109 betPARX | 11 | AGREE |
| Tre Tucker (LV) | rec | 3.5 | 37.9% / 38.2% | 45.9% | -8.0 | +115 Bovada | 11 |  |
| Brock Bowers (LV) | rec_yds | 69.5 | 40.0% / 41.4% | 49.9% | -9.9 | -111 DraftKings | 2 |  |
| Tre Tucker (LV) | rec_yds | 38.5 | 47.7% / 47.9% | 50.2% | -2.5 | -114 DraftKings | 2 |  |
| Michael Mayer (LV) | rec_yds | 29.5 | 56.3% / 56.2% | 50.5% | +5.9 | -116 BetOnline.ag | 2 |  |
| Ashton Jeanty (LV) | rec_yds | 24.5 | 48.9% / 49.6% | 50.0% | -1.1 | -114 FanDuel | 3 | AGREE |
| Cody White (LV) | rec_yds | 17.5 | 32.6% / 32.0% | 49.9% | -17.2 | -110 DraftKings | 3 |  |
| Ashton Jeanty (LV) | rush_att | 16.5 | 51.1% / 50.1% | 51.6% | -0.6 | -104 betPARX | 7 | AGREE |
| Ashton Jeanty (LV) | rush_yds | 59.5 | 47.8% / 47.1% | 49.9% | -2.1 | -110 DraftKings | 4 | AGREE |
| Mike Washington Jr. (LV) | rush_yds | 23.5 | 52.7% / 51.7% | 49.6% | +3.1 | -110 BetOnline.ag | 2 |  |
| Drake Maye (NE) | pass_att | 29.5 | 35.8% / 34.8% | 50.9% | -15.1 | -113 betPARX | 9 |  |
| Drake Maye (NE) | pass_cmp | 19.5 | 27.4% / 26.6% | 50.1% | -22.6 | -103 BetRivers | 10 |  |
| Drake Maye (NE) | pass_yds | 226.5 | 32.3% / 32.6% | 50.0% | -17.7 | -114 FanDuel | 2 |  |
| Hunter Henry (NE) | rec | 3.5 | 33.0% / 32.3% | 52.2% | -19.2 | -118 BetMGM | 11 |  |
| Romeo Doubs (NE) | rec | 3.5 | 48.6% / 47.7% | 56.6% | -7.9 | -147 BetOnline.ag | 11 |  |
| DeMario Douglas (NE) | rec | 2.5 | 39.5% / 39.3% | 49.9% | -10.4 | -107 betPARX | 8 |  |
| Romeo Doubs (NE) | rec_yds | 52.5 | 42.7% / 42.4% | 50.0% | -7.3 | -113 BetRivers | 3 |  |
| Hunter Henry (NE) | rec_yds | 37.5 | 34.2% / 34.2% | 49.9% | -15.7 | -110 DraftKings | 5 |  |
| DeMario Douglas (NE) | rec_yds | 24.5 | 48.7% / 49.4% | 49.5% | -0.8 | -108 DraftKings | 4 | AGREE |
| Drake Maye (NE) | rush_att | 5.5 | 27.3% / 27.6% | 56.3% | -29.1 | -150 betPARX | 2 |  |
| Drake Maye (NE) | rush_yds | 31.5 | 28.6% / 28.9% | 49.9% | -21.4 | -111 DraftKings | 4 |  |

---
## MIN@NO

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +2.5 | 41.5 | 44.3% |
| market track (sim) | +3.0 | 41.6 | 43.5% |
| model track (sim) | +1.0 | 43.3 | 47.6% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Aaron Jones (MIN) | 49.9% / 50.4% | 55.6% | 50.0% | -0.1 | -120 FanDuel | 6 | AGREE |
| Alvin Kamara (NO) | 34.0% / 38.3% | 43.3% | 39.0% | -5.0 | +165 BetMGM | 6 |  |
| Chris Olave (NO) | 30.2% / 33.4% | 34.5% | 31.0% | -0.9 | +195 FanDuel | 6 | AGREE |
| Juwan Johnson (NO) | 29.7% / 32.6% | 25.6% | 23.1% | +6.6 | +310 BetRivers | 6 |  |
| Justin Jefferson (MIN) | 29.0% / 29.2% | 37.9% | 34.1% | -5.1 | +165 DraftKings | 6 |  |
| T.J. Hockenson (MIN) | 28.0% / 28.3% | 25.0% | 22.5% | +5.5 | +310 BetMGM | 6 |  |
| Kendre Miller (NO) | 27.2% / 29.5% | 41.2% | 37.1% | -9.9 | +380 FanDuel | 6 |  |
| Devaughn Vele (NO) | 23.7% / 24.9% | 23.8% | 21.4% | +2.3 | +350 FanDuel | 6 | AGREE |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Aaron Jones (MIN) | 15.5% / 14.8% | 20.0% | 18.0% | 15.7% | +425 theScore Bet | 5 |
| Alvin Kamara (NO) | 9.4% / 10.3% | 13.3% | 12.0% | 10.6% | +700 Bally Bet | 5 |
| Chris Olave (NO) | 8.1% / 8.7% | 7.7% | 6.9% | 6.5% | +1300 theScore Bet | 5 |
| Juwan Johnson (NO) | 8.0% / 8.5% | 6.2% | 5.6% | 5.1% | +1500 Bally Bet | 5 |
| Justin Jefferson (MIN) | 7.8% / 7.5% | 10.7% | 9.6% | 8.3% | +850 DraftKings | 4 |
| T.J. Hockenson (MIN) | 7.4% / 7.2% | 6.7% | 6.0% | 5.2% | +1500 theScore Bet | 5 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Kyler Murray (MIN) | pass_att | 31.5 | 16.9% / 17.7% | 51.0% | -34.2 | -112 betPARX | 8 |  |
| Kyler Murray (MIN) | pass_cmp | 20.5 | 23.6% / 23.9% | 51.8% | -28.2 | -116 BetOnline.ag | 10 |  |
| Kyler Murray (MIN) | pass_yds | 212.5 | 33.5% / 33.2% | 50.0% | -16.5 | -114 FanDuel | 2 |  |
| Aaron Jones (MIN) | rec | 2.5 | 48.9% / 48.5% | 59.0% | -10.1 | -165 BetMGM | 6 |  |
| Aaron Jones (MIN) | rec_yds | 18.5 | 43.8% / 43.7% | 50.1% | -6.3 | -114 FanDuel | 3 |  |
| Aaron Jones (MIN) | rush_att | 17.5 | 65.7% / 64.4% | 48.6% | +17.1 | -105 Fliff | 5 |  |
| Aaron Jones (MIN) | rush_yds | 72.5 | 66.4% / 65.5% | 50.0% | +16.4 | -113 BetRivers | 4 |  |
| Kyler Murray (MIN) | rush_yds | 17.5 | 28.1% / 27.4% | 50.0% | -21.9 | -113 BetRivers | 5 |  |
| Tyler Shough (NO) | pass_att | 35.5 | 46.7% / 44.3% | 52.2% | -5.5 | -120 BetOnline.ag | 5 |  |
| Tyler Shough (NO) | pass_cmp | 22.5 | 39.3% / 38.7% | 52.8% | -13.6 | -114 BetOnline.ag | 6 |  |
| Tyler Shough (NO) | pass_yds | 236.5 | 49.5% / 48.4% | 50.1% | -0.6 | -113 DraftKings | 3 | AGREE |
| Chris Olave (NO) | rec | 6.5 | 44.8% / 44.1% | 47.4% | -2.6 | +105 theScore Bet | 11 | AGREE |
| Juwan Johnson (NO) | rec | 4.5 | 56.6% / 56.0% | 45.5% | +11.1 | +120 betPARX | 11 |  |
| Devaughn Vele (NO) | rec | 3.5 | 44.2% / 44.4% | 53.5% | -9.3 | -125 BetMGM | 11 |  |
| Chris Olave (NO) | rec_yds | 81.5 | 49.4% / 48.6% | 49.8% | -0.4 | -110 DraftKings | 4 | AGREE |
| Juwan Johnson (NO) | rec_yds | 43.5 | 59.7% / 58.6% | 50.0% | +9.8 | -113 DraftKings | 3 |  |
| Devaughn Vele (NO) | rec_yds | 37.5 | 48.4% / 47.9% | 49.9% | -1.5 | -110 DraftKings | 3 | AGREE |
| Alvin Kamara (NO) | rush_yds | 33.5 | 48.9% / 49.1% | 49.7% | -0.8 | -109 DraftKings | 2 |  |
| Kendre Miller (NO) | rush_yds | 18.5 | 71.0% / 72.3% | 50.0% | +21.0 | -114 FanDuel | 1 |  |
| Tyler Shough (NO) | rush_yds | 9.5 | 71.5% / 71.7% | 50.0% | +21.5 | -114 DraftKings | 5 |  |

---
## CLE@NYJ

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -2.5 | 39.5 | 54.8% |
| market track (sim) | -3.0 | 39.4 | 57.5% |
| model track (sim) | -1.0 | 41.5 | 53.1% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Quinshon Judkins (CLE) | 39.2% / 43.4% | 41.8% | 37.6% | +1.6 | +155 DraftKings | 6 | AGREE |
| Braelon Allen (NYJ) | 38.3% / 38.9% | 51.8% | 46.6% | -8.3 | +102 BetRivers | 6 |  |
| Breece Hall (NYJ) | 37.4% / 38.7% | 52.6% | 47.3% | -9.9 | -111 BetOnline.ag | 1 |  |
| Garrett Wilson (NYJ) | 28.9% / 29.3% | 42.6% | 38.3% | -9.4 | +150 BetMGM | 6 |  |
| KC Concepcion (CLE) | 23.6% / 26.5% | 25.0% | 22.5% | +1.1 | +320 DraftKings | 6 | AGREE |
| Harold Fannin Jr. (CLE) | 21.7% / 24.8% | 31.7% | 28.6% | -6.9 | +270 BetMGM | 6 |  |
| Kenyon Sadiq (NYJ) | 20.1% / 19.5% | 28.6% | 25.7% | -5.7 | +260 FanDuel | 6 |  |
| Adonai Mitchell (NYJ) | 18.7% / 19.8% | 30.3% | 27.3% | -8.5 | +230 BetOnline.ag | 2 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Quinshon Judkins (CLE) | 11.8% / 12.7% | 13.7% | 12.3% | 11.2% | +700 DraftKings | 6 |
| Braelon Allen (NYJ) | 11.6% / 11.2% | 17.6% | 15.9% | 14.5% | +500 Bally Bet | 6 |
| Garrett Wilson (NYJ) | 8.3% / 7.7% | 12.1% | 10.9% | 9.6% | +750 DraftKings | 6 |
| KC Concepcion (CLE) | 6.4% / 6.7% | 6.7% | 6.0% | 5.5% | +1500 theScore Bet | 6 |
| Harold Fannin Jr. (CLE) | 5.7% / 6.2% | 9.1% | 8.2% | 7.3% | +1150 BetMGM | 6 |
| Kenyon Sadiq (NYJ) | 5.3% / 4.9% | 7.7% | 6.9% | 6.3% | +1300 theScore Bet | 5 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Deshaun Watson (CLE) | pass_att | 31.5 | 31.0% / 30.5% | 48.0% | -17.0 | +100 theScore Bet | 6 |  |
| Deshaun Watson (CLE) | pass_cmp | 19.5 | 53.1% / 52.7% | 51.5% | +1.6 | -115 betPARX | 9 | AGREE |
| Deshaun Watson (CLE) | pass_yds | 203.5 | 48.0% / 47.5% | 49.9% | -1.9 | -112 BetOnline.ag | 3 | AGREE |
| Harold Fannin Jr. (CLE) | rec | 4.5 | 46.1% / 45.8% | 42.3% | +3.8 | +125 DraftKings | 10 |  |
| KC Concepcion (CLE) | rec | 4.5 | 46.3% / 45.8% | 44.6% | +1.7 | +125 betPARX | 11 | AGREE |
| Denzel Boston (CLE) | rec | 3.5 | 37.9% / 37.7% | 44.2% | -6.3 | +125 theScore Bet | 11 |  |
| Quinshon Judkins (CLE) | rec | 2.5 | 41.8% / 42.2% | 54.6% | -12.8 | -140 Hard Rock Bet | 3 |  |
| Denzel Boston (CLE) | rec_yds | 47.5 | 40.6% / 41.1% | 49.9% | -9.3 | -111 DraftKings | 4 |  |
| KC Concepcion (CLE) | rec_yds | 39.5 | 54.9% / 54.1% | 50.2% | +4.7 | -113 DraftKings | 3 |  |
| Harold Fannin Jr. (CLE) | rec_yds | 35.5 | 54.6% / 53.8% | 50.1% | +4.4 | -113 DraftKings | 4 |  |
| Quinshon Judkins (CLE) | rec_yds | 15.5 | 43.9% / 43.6% | 49.8% | -5.9 | -111 BetMGM | 3 |  |
| Quinshon Judkins (CLE) | rush_att | 15.5 | 38.4% / 39.2% | 52.5% | -14.1 | -122 betPARX | 5 |  |
| Deshaun Watson (CLE) | rush_att | 5.5 | 34.8% / 34.8% | 54.1% | -19.3 | -130 betPARX | 6 |  |
| Quinshon Judkins (CLE) | rush_yds | 58.5 | 35.8% / 36.2% | 50.0% | -14.2 | -112 DraftKings | 2 |  |
| Deshaun Watson (CLE) | rush_yds | 25.5 | 30.1% / 30.0% | 50.5% | -20.4 | -112 DraftKings | 2 |  |
| Geno Smith (NYJ) | pass_att | 31.5 | 29.6% / 30.6% | 47.4% | -17.8 | +101 DraftKings | 6 |  |
| Geno Smith (NYJ) | pass_cmp | 20.5 | 38.3% / 39.1% | 47.9% | -9.6 | +104 betPARX | 9 |  |
| Geno Smith (NYJ) | pass_yds | 206.5 | 50.5% / 50.8% | 50.0% | +0.5 | -114 FanDuel | 2 |  |
| Garrett Wilson (NYJ) | rec | 6.5 | 29.6% / 29.6% | 43.3% | -13.7 | +125 BetOnline.ag | 11 |  |
| Garrett Wilson (NYJ) | rec_yds | 69.5 | 39.3% / 39.1% | 49.9% | -10.6 | -110 DraftKings | 4 |  |
| Braelon Allen (NYJ) | rush_att | 17.5 | 24.1% / 23.5% | 49.6% | -25.5 | +100 BetOnline.ag | 6 |  |
| Braelon Allen (NYJ) | rush_yds | 71.5 | 27.4% / 27.1% | 50.0% | -22.7 | -114 FanDuel | 3 |  |
| Geno Smith (NYJ) | rush_yds | 10.5 | 44.6% / 44.3% | 50.0% | -5.4 | -110 DraftKings | 6 |  |
| Isaiah Davis (NYJ) | rush_yds | 10.5 | n/a (cap) | 50.0% |  | -107 BetRivers | 3 |  |

---
## IND@PIT

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -2.5 | 44.5 | 56.8% |
| market track (sim) | -3.0 | 44.6 | 57.2% |
| model track (sim) | -0.0 | 47.6 | 50.8% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Jonathan Taylor (IND) | 56.7% / 63.9% | 65.7% | 59.1% | -2.4 | -175 FanDuel | 6 | AGREE |
| Jaylen Warren (PIT) | 46.8% / 46.9% | 59.0% | 53.1% | -6.3 | -129 BetRivers | 6 |  |
| DK Metcalf (PIT) | 28.1% / 29.0% | 39.2% | 35.3% | -7.2 | +175 BetMGM | 6 |  |
| Rico Dowdle (PIT) | 26.6% / 27.3% | 38.7% | 34.8% | -8.2 | +180 BetRivers | 2 |  |
| Pat Freiermuth (PIT) | 23.8% / 24.4% | 25.7% | 23.1% | +0.7 | +360 BetMGM | 6 | AGREE |
| Tyler Warren (IND) | 21.0% / 25.2% | 32.1% | 28.8% | -7.8 | +235 DraftKings | 6 |  |
| Josh Downs (IND) | 20.9% / 24.6% | 31.2% | 28.1% | -7.2 | +230 DraftKings | 6 |  |
| Roman Wilson (PIT) | 20.0% / 20.4% | 28.0% | 25.2% | -5.2 | +270 FanDuel | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Jonathan Taylor (IND) | 17.1% / 18.9% | 22.7% | 20.5% | 19.1% | +360 theScore Bet | 5 |
| Jaylen Warren (PIT) | 13.1% / 12.0% | 19.0% | 17.1% | 16.2% | +475 Bally Bet | 5 |
| DK Metcalf (PIT) | 7.0% / 6.6% | 9.1% | 8.2% | 7.7% | +1100 theScore Bet | 5 |
| Rico Dowdle (PIT) | 6.6% / 6.2% | 9.5% | 8.6% | 6.7% | +950 Bally Bet | 1 |
| Pat Freiermuth (PIT) | 5.7% / 5.4% | 5.6% | 5.0% | 4.7% | +1800 theScore Bet | 5 |
| Tyler Warren (IND) | 4.9% / 5.5% | 6.7% | 6.0% | 5.7% | +1500 theScore Bet | 5 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Daniel Jones (IND) | pass_att | 31.5 | 35.4% / 32.5% | 50.4% | -15.0 | -110 BetOnline.ag | 3 |  |
| Daniel Jones (IND) | pass_cmp | 19.5 | 52.3% / 49.1% | 52.1% | +0.2 | -120 DraftKings | 8 | AGREE |
| Daniel Jones (IND) | pass_yds | 210.5 | 34.2% / 32.5% | 49.9% | -15.7 | -111 DraftKings | 2 |  |
| Tyler Warren (IND) | rec | 5.5 | 43.2% / 41.8% | 43.3% | -0.1 | +123 betPARX | 11 | AGREE |
| Josh Downs (IND) | rec | 4.5 | 44.1% / 42.3% | 56.9% | -12.8 | -148 FanDuel | 7 |  |
| Keenan Allen (IND) | rec | 3.5 | 57.7% / 56.8% | 42.8% | +14.9 | +125 DraftKings | 10 |  |
| Jonathan Taylor (IND) | rec | 2.5 | 56.7% / 55.6% | 50.9% | +5.8 | -110 FanDuel | 10 |  |
| Josh Downs (IND) | rec_yds | 57.5 | 31.1% / 30.3% | 50.2% | -19.2 | -113 DraftKings | 3 |  |
| Tyler Warren (IND) | rec_yds | 46.5 | 44.9% / 43.6% | 50.2% | -5.3 | -115 DraftKings | 3 |  |
| Keenan Allen (IND) | rec_yds | 27.5 | 64.1% / 62.6% | 50.2% | +13.9 | -112 DraftKings | 3 |  |
| Jonathan Taylor (IND) | rec_yds | 16.5 | 54.9% / 54.0% | 49.1% | +5.8 | -110 DraftKings | 3 |  |
| Jonathan Taylor (IND) | rush_att | 19.5 | 43.0% / 44.8% | 49.8% | -6.7 | -110 betPARX | 6 |  |
| Jonathan Taylor (IND) | rush_yds | 85.5 | 42.9% / 43.6% | 50.1% | -7.2 | -112 DraftKings | 3 |  |
| Daniel Jones (IND) | rush_yds | 10.5 | 29.4% / 28.6% | 48.9% | -19.6 | -104 DraftKings | 4 |  |
| Aaron Rodgers (PIT) | pass_att | 34.5 | 46.0% / 48.7% | 51.3% | -5.3 | -113 betPARX | 9 |  |
| Aaron Rodgers (PIT) | pass_cmp | 21.5 | 39.2% / 41.5% | 48.8% | -9.6 | -105 Hard Rock Bet | 7 |  |
| Aaron Rodgers (PIT) | pass_yds | 218.5 | 60.0% / 61.6% | 49.9% | +10.1 | -111 DraftKings | 2 |  |
| DK Metcalf (PIT) | rec | 4.5 | 44.6% / 45.4% | 44.0% | +0.6 | +120 Fliff | 10 | AGREE |
| Pat Freiermuth (PIT) | rec | 3.5 | 35.4% / 36.0% | 44.1% | -8.7 | +120 BetMGM | 11 |  |
| Roman Wilson (PIT) | rec | 3.5 | 23.5% / 24.6% | 45.1% | -21.6 | +120 theScore Bet | 11 |  |
| Darnell Washington (PIT) | rec | 2.5 | 26.4% / 27.6% | 41.8% | -15.4 | +132 betPARX | 10 |  |
| Germie Bernard (PIT) | rec | 2.5 | n/a (cap) | 38.6% |  | +147 DraftKings | 8 |  |
| Michael Pittman Jr. (PIT) | rec | 2.5 | 53.2% / 53.7% | 49.0% | +4.2 | -110 theScore Bet | 1 |  |
| DK Metcalf (PIT) | rec_yds | 52.5 | 55.8% / 56.4% | 50.2% | +5.6 | -114 DraftKings | 5 |  |
| Roman Wilson (PIT) | rec_yds | 41.5 | 33.1% / 34.0% | 50.0% | -16.9 | -114 FanDuel | 3 |  |
| Pat Freiermuth (PIT) | rec_yds | 27.5 | 52.6% / 52.9% | 50.2% | +2.3 | -114 DraftKings | 5 | AGREE |
| Darnell Washington (PIT) | rec_yds | 22.5 | 37.0% / 38.0% | 50.0% | -13.0 | -114 FanDuel | 4 |  |
| Germie Bernard (PIT) | rec_yds | 18.5 | 28.6% / 28.6% | 50.1% | -21.5 | -114 FanDuel | 4 |  |
| Jaylen Warren (PIT) | rush_yds | 63.5 | 43.1% / 41.5% | 50.4% | -7.3 | -114 DraftKings | 1 |  |

---
## HOU@TEN

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +7.5 | 38.0 | 23.5% |
| market track (sim) | +7.0 | 37.5 | 28.9% |
| model track (sim) | +3.0 | 40.5 | 40.7% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| David Montgomery (HOU) | 45.8% / 44.5% | 45.5% | 40.9% | +4.9 | +120 DraftKings | 6 |  |
| Tony Pollard (TEN) | 36.3% / 45.6% | 29.4% | 26.5% | +9.8 | +250 DraftKings | 6 |  |
| Woody Marks (HOU) | 36.2% / 35.1% | 33.3% | 30.0% | +6.2 | +230 FanDuel | 6 |  |
| Nico Collins (HOU) | 28.7% / 27.3% | 43.0% | 38.7% | -10.0 | +150 FanDuel | 6 |  |
| Dalton Schultz (HOU) | 19.6% / 18.6% | 28.2% | 25.4% | -5.7 | +270 FanDuel | 6 |  |
| Tyjae Spears (TEN) | 18.6% / 24.0% | 16.3% | 14.7% | +3.9 | +650 FanDuel | 6 |  |
| Wan'Dale Robinson (TEN) | 17.6% / 23.4% | 18.8% | 16.9% | +0.7 | +490 FanDuel | 6 | AGREE |
| Xavier Hutchinson (HOU) | 17.0% / 16.8% | 14.6% | 13.1% | +3.9 | +700 BetRivers | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| David Montgomery (HOU) | 15.0% / 13.0% | 15.7% | 14.1% | 13.2% | +550 DraftKings | 6 |
| Woody Marks (HOU) | 10.9% / 9.5% | 10.5% | 9.5% | 8.6% | +900 DraftKings | 6 |
| Tony Pollard (TEN) | 10.6% / 13.4% | 9.5% | 8.6% | 8.0% | +1100 theScore Bet | 6 |
| Nico Collins (HOU) | 8.2% / 7.1% | 14.8% | 13.4% | 12.2% | +600 DraftKings | 6 |
| Dalton Schultz (HOU) | 5.3% / 4.6% | 9.5% | 8.6% | 7.9% | +1100 theScore Bet | 6 |
| Tyjae Spears (TEN) | 5.0% / 6.2% | 4.3% | 3.9% | 3.7% | +2250 Hard Rock Bet | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| C.J. Stroud (HOU) | pass_att | 31.5 | 61.0% / 65.6% | 49.5% | +11.5 | -110 DraftKings | 7 |  |
| C.J. Stroud (HOU) | pass_cmp | 21.5 | 51.0% / 54.6% | 50.4% | +0.6 | -108 BetOnline.ag | 6 | AGREE |
| C.J. Stroud (HOU) | pass_yds | 239.5 | 54.5% / 56.2% | 50.0% | +4.5 | -114 FanDuel | 2 |  |
| Nico Collins (HOU) | rec | 5.5 | 46.0% / 47.2% | 51.3% | -5.3 | -105 BetOnline.ag | 11 |  |
| Dalton Schultz (HOU) | rec | 4.5 | 41.9% / 43.5% | 43.7% | -1.8 | +120 FanDuel | 10 | AGREE |
| Kayshon Boutte (HOU) | rec | 2.5 | 43.7% / 44.3% | 44.1% | -0.4 | +124 FanDuel | 10 | AGREE |
| Nico Collins (HOU) | rec_yds | 77.5 | 42.5% / 43.1% | 50.0% | -7.5 | -114 FanDuel | 2 |  |
| Dalton Schultz (HOU) | rec_yds | 37.5 | 49.8% / 50.9% | 49.9% | -0.1 | -109 DraftKings | 5 | AGREE |
| Kayshon Boutte (HOU) | rec_yds | 25.5 | 52.0% / 51.9% | 50.7% | +1.3 | -114 FanDuel | 4 | AGREE |
| Jaylin Noel (HOU) | rec_yds | 18.5 | 49.3% / 49.0% | 49.8% | -0.5 | -104 BetRivers | 3 | AGREE |
| David Montgomery (HOU) | rush_att | 14.5 | 27.3% / 25.6% | 49.1% | -21.8 | -105 DraftKings | 3 |  |
| Woody Marks (HOU) | rush_att | 8.5 | 44.7% / 41.6% | 52.5% | -7.9 | -125 Fliff | 3 |  |
| C.J. Stroud (HOU) | rush_att | 2.5 | 43.5% / 42.7% | 58.3% | -14.8 | -175 Fliff | 1 |  |
| David Montgomery (HOU) | rush_yds | 46.5 | 38.6% / 37.2% | 50.1% | -11.5 | -112 DraftKings | 3 |  |
| Woody Marks (HOU) | rush_yds | 30.5 | 41.9% / 40.7% | 49.6% | -7.7 | -109 DraftKings | 3 |  |
| C.J. Stroud (HOU) | rush_yds | 9.5 | 48.0% / 47.4% | 50.5% | -2.5 | -114 FanDuel | 3 | AGREE |
| Cam Ward (TEN) | pass_att | 31.5 | 46.8% / 42.8% | 50.8% | -4.0 | -115 BetMGM | 7 |  |
| Cam Ward (TEN) | pass_cmp | 19.5 | 55.9% / 53.3% | 49.9% | +6.0 | -110 BetOnline.ag | 6 |  |
| Cam Ward (TEN) | pass_yds | 192.5 | 62.2% / 60.3% | 50.1% | +12.1 | -113 DraftKings | 3 |  |
| Carnell Tate (TEN) | rec | 4.5 | 55.5% / 54.9% | 45.7% | +9.8 | +115 theScore Bet | 6 |  |
| Wan'Dale Robinson (TEN) | rec | 3.5 | 58.5% / 57.6% | 55.5% | +3.0 | -135 Hard Rock Bet | 9 |  |
| Gunnar Helm (TEN) | rec | 2.5 | 50.0% / 49.9% | 47.1% | +2.9 | +115 theScore Bet | 9 | AGREE |
| Carnell Tate (TEN) | rec_yds | 44.5 | 64.0% / 63.4% | 50.1% | +13.9 | -113 DraftKings | 2 |  |
| Wan'Dale Robinson (TEN) | rec_yds | 32.5 | 59.8% / 59.3% | 50.0% | +9.8 | -114 FanDuel | 2 |  |
| Elic Ayomanor (TEN) | rec_yds | 17.5 | 65.3% / 65.2% | 49.0% | +16.3 | -105 BetOnline.ag | 4 |  |
| Gunnar Helm (TEN) | rec_yds | 17.5 | 57.8% / 57.9% | 49.5% | +8.4 | -108 DraftKings | 4 |  |
| Tony Pollard (TEN) | rush_att | 14.5 | 44.8% / 48.1% | 47.6% | -2.8 | +102 DraftKings | 3 | AGREE |
| Cam Ward (TEN) | rush_att | 3.5 | 46.5% / 46.9% | 45.5% | +1.0 | +100 Fliff | 1 |  |
| Tony Pollard (TEN) | rush_yds | 49.5 | 53.6% / 54.8% | 50.4% | +3.2 | -114 DraftKings | 3 |  |
| Tyjae Spears (TEN) | rush_yds | 13.5 | 72.8% / 73.3% | 50.0% | +22.8 | -112 DraftKings | 2 |  |
| Cam Ward (TEN) | rush_yds | 10.5 | 49.8% / 50.1% | 50.8% | -1.0 | -114 FanDuel | 5 | AGREE |

---
## NYG@WAS

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -4.0 | 41.5 | 63.7% |
| market track (sim) | -4.0 | 41.2 | 60.4% |
| model track (sim) | -0.0 | 45.4 | 51.5% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Isaiah Likely (NYG) | 34.3% / 41.9% | 29.6% | 26.7% | +7.7 | +250 BetMGM | 6 |  |
| Stefon Diggs (WAS) | 34.0% / 35.4% | 37.4% | 33.6% | +0.4 | +185 DraftKings | 6 | AGREE |
| Terry McLaurin (WAS) | 28.2% / 29.6% | 36.7% | 33.0% | -4.8 | +185 DraftKings | 6 |  |
| Cam Skattebo (NYG) | 28.1% / 36.3% | 44.9% | 40.5% | -12.3 | +130 DraftKings | 6 |  |
| Malik Nabers (NYG) | 24.1% / 30.0% | 32.3% | 29.0% | -4.9 | +220 FanDuel | 6 |  |
| Jacory Croskey-Merritt (WAS) | 23.6% / 23.0% | 43.1% | 38.7% | -15.1 | +155 FanDuel | 6 |  |
| Rachaad White (WAS) | 23.3% / 24.5% | 32.8% | 29.5% | -6.3 | +215 DraftKings | 6 |  |
| Antonio Williams (WAS) | 22.8% / 23.6% | 23.3% | 20.9% | +1.9 | +330 DraftKings | 5 | AGREE |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Stefon Diggs (WAS) | 9.5% / 8.7% | 10.4% | 9.4% | 7.0% | +1000 DraftKings | 4 |
| Isaiah Likely (NYG) | 9.4% / 10.7% | 7.1% | 6.4% | 5.2% | +1300 DraftKings | 4 |
| Terry McLaurin (WAS) | 7.6% / 7.1% | 11.0% | 9.9% | 7.8% | +850 DraftKings | 4 |
| Cam Skattebo (NYG) | 7.5% / 8.9% | 14.0% | 12.6% | 10.4% | +650 DraftKings | 4 |
| Jacory Croskey-Merritt (WAS) | 6.2% / 5.3% | 14.0% | 12.6% | 10.0% | +650 DraftKings | 4 |
| Malik Nabers (NYG) | 6.2% / 7.0% | 8.0% | 7.2% | 6.0% | +1200 DraftKings | 4 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Jameis Winston (NYG) | pass_att | 31.5 | 21.3% / 19.2% | 47.9% | -26.6 | +100 theScore Bet | 8 |  |
| Jameis Winston (NYG) | pass_cmp | 18.5 | 43.8% / 41.1% | 50.3% | -6.5 | -113 DraftKings | 9 |  |
| Jameis Winston (NYG) | pass_yds | 199.5 | 44.1% / 42.5% | 49.9% | -5.7 | -111 DraftKings | 2 |  |
| Malik Nabers (NYG) | rec | 5.5 | 18.4% / 18.4% | 43.7% | -25.4 | +122 BetOnline.ag | 9 |  |
| Isaiah Likely (NYG) | rec | 4.5 | 56.0% / 54.0% | 47.9% | +8.1 | +106 FanDuel | 10 |  |
| Cam Skattebo (NYG) | rec | 2.5 | 36.6% / 35.9% | 41.5% | -4.9 | +135 Hard Rock Bet | 6 |  |
| Malachi Fields (NYG) | rec | 2.5 | 46.6% / 45.5% | 42.0% | +4.6 | +128 betPARX | 10 |  |
| Malik Nabers (NYG) | rec_yds | 54.5 | 34.4% / 33.7% | 50.2% | -15.8 | -114 FanDuel | 2 |  |
| Isaiah Likely (NYG) | rec_yds | 40.5 | 58.4% / 56.9% | 50.2% | +8.2 | -113 BetRivers | 3 |  |
| Malachi Fields (NYG) | rec_yds | 27.5 | 52.4% / 51.3% | 49.9% | +2.5 | -110 DraftKings | 4 | AGREE |
| Darnell Mooney (NYG) | rec_yds | 17.5 | 60.1% / 59.3% | 50.0% | +10.1 | -113 BetRivers | 3 |  |
| Cam Skattebo (NYG) | rush_att | 15.5 | 29.7% / 31.2% | 51.1% | -21.4 | -114 BetOnline.ag | 4 |  |
| Cam Skattebo (NYG) | rush_yds | 56.5 | 35.3% / 36.1% | 50.1% | -14.8 | -114 DraftKings | 3 |  |
| Najee Harris (NYG) | rush_yds | 28.5 | 33.3% / 33.8% | 49.8% | -16.6 | -112 BetOnline.ag | 2 |  |
| Jayden Daniels (WAS) | pass_att | 29.5 | 55.5% / 58.6% | 50.8% | +4.7 | -115 BetOnline.ag | 9 |  |
| Jayden Daniels (WAS) | pass_cmp | 17.5 | 57.7% / 59.8% | 52.7% | +5.0 | -121 betPARX | 6 |  |
| Jayden Daniels (WAS) | pass_yds | 198.5 | 35.4% / 36.3% | 49.5% | -14.2 | -105 BetOnline.ag | 5 |  |
| Jacory Croskey-Merritt (WAS) | rush_att | 13.5 | n/a (cap) | 50.2% |  | -110 BetOnline.ag | 6 |  |
| Jayden Daniels (WAS) | rush_att | 6.5 | 18.8% / 18.2% | 47.7% | -28.9 | +100 betPARX | 7 |  |
| Jacory Croskey-Merritt (WAS) | rush_yds | 55.5 | 18.8% / 18.0% | 50.3% | -31.5 | -111 BetOnline.ag | 4 |  |
| Jayden Daniels (WAS) | rush_yds | 30.5 | 35.9% / 35.4% | 50.0% | -14.1 | -114 FanDuel | 3 |  |

---
## DEN@LAC

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +3.5 | 42.0 | 38.0% |
| market track (sim) | +4.0 | 41.5 | 39.6% |
| model track (sim) | -0.0 | 41.2 | 48.0% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| J.K. Dobbins (DEN) | 44.1% / 40.2% | 42.6% | 38.3% | +5.8 | +145 FanDuel | 6 |  |
| Omarion Hampton (LAC) | 37.1% / 40.5% | 37.4% | 33.6% | +3.5 | +170 DraftKings | 6 |  |
| RJ Harvey (DEN) | 33.1% / 30.8% | 33.9% | 30.5% | +2.6 | +200 FanDuel | 6 | AGREE |
| Courtland Sutton (DEN) | 25.6% / 24.0% | 33.3% | 30.0% | -4.4 | +225 BetMGM | 6 |  |
| Jaylen Waddle (DEN) | 21.6% / 20.3% | 33.9% | 30.5% | -8.9 | +210 BetMGM | 6 |  |
| Keaton Mitchell (LAC) | 20.2% / 22.0% | 26.3% | 23.7% | -3.4 | +310 BetMGM | 6 |  |
| Tre Harris (LAC) | 18.9% / 21.0% | 23.3% | 20.9% | -2.1 | +360 FanDuel | 6 | AGREE |
| Ladd McConkey (LAC) | 18.4% / 20.2% | 30.3% | 27.3% | -8.9 | +240 BetMGM | 2 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| J.K. Dobbins (DEN) | 12.4% / 11.1% | 13.6% | 12.2% | 11.4% | +650 DraftKings | 6 |
| Omarion Hampton (LAC) | 9.8% / 11.1% | 11.3% | 10.1% | 9.2% | +850 DraftKings | 6 |
| RJ Harvey (DEN) | 8.5% / 7.9% | 10.0% | 9.0% | 8.0% | +1100 theScore Bet | 6 |
| Courtland Sutton (DEN) | 6.3% / 5.9% | 8.3% | 7.5% | 7.0% | +1200 theScore Bet | 6 |
| Jaylen Waddle (DEN) | 5.2% / 4.8% | 9.8% | 8.8% | 8.0% | +1100 theScore Bet | 6 |
| Keaton Mitchell (LAC) | 4.8% / 5.3% | 6.7% | 6.0% | 5.6% | +1500 theScore Bet | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Bo Nix (DEN) | pass_att | 33.5 | 36.0% / 37.7% | 50.1% | -14.1 | -110 DraftKings | 9 |  |
| Bo Nix (DEN) | pass_cmp | 21.5 | 33.9% / 34.8% | 49.0% | -15.2 | -105 theScore Bet | 10 |  |
| Bo Nix (DEN) | pass_yds | 220.5 | 45.8% / 47.2% | 49.9% | -4.1 | -111 DraftKings | 2 |  |
| Jaylen Waddle (DEN) | rec | 4.5 | 27.1% / 27.8% | 48.7% | -21.6 | +105 theScore Bet | 11 |  |
| Courtland Sutton (DEN) | rec | 3.5 | 34.0% / 34.6% | 45.3% | -11.3 | +115 BetOnline.ag | 11 |  |
| RJ Harvey (DEN) | rec | 3.5 | 48.1% / 49.3% | 58.8% | -10.6 | -161 BetOnline.ag | 5 |  |
| Evan Engram (DEN) | rec | 2.5 | 43.3% / 43.8% | 41.2% | +2.1 | +135 BetOnline.ag | 11 | AGREE |
| Jaylen Waddle (DEN) | rec_yds | 53.5 | 33.7% / 34.2% | 50.7% | -17.0 | -114 FanDuel | 4 |  |
| Courtland Sutton (DEN) | rec_yds | 36.5 | 43.9% / 44.7% | 50.1% | -6.2 | -113 DraftKings | 4 |  |
| RJ Harvey (DEN) | rec_yds | 27.5 | 44.1% / 45.0% | 49.9% | -5.7 | -111 BetOnline.ag | 4 |  |
| Troy Franklin (DEN) | rec_yds | 19.5 | 40.8% / 41.1% | 49.9% | -9.1 | -110 DraftKings | 4 |  |
| Evan Engram (DEN) | rec_yds | 16.5 | 59.2% / 59.0% | 50.9% | +8.3 | -116 DraftKings | 2 |  |
| J.K. Dobbins (DEN) | rush_att | 13.5 | 46.3% / 44.5% | 51.1% | -4.8 | -110 BetOnline.ag | 7 |  |
| Bo Nix (DEN) | rush_att | 4.5 | 29.8% / 28.9% | 46.5% | -16.6 | +105 theScore Bet | 4 |  |
| J.K. Dobbins (DEN) | rush_yds | 51.5 | 45.2% / 43.9% | 50.2% | -5.0 | -113 DraftKings | 4 |  |
| RJ Harvey (DEN) | rush_yds | 22.5 | 45.1% / 44.0% | 50.3% | -5.1 | -110 BetMGM | 4 |  |
| Bo Nix (DEN) | rush_yds | 14.5 | 28.9% / 28.2% | 49.2% | -20.3 | -107 DraftKings | 4 |  |
| Justin Herbert (LAC) | pass_att | 30.5 | 45.4% / 42.7% | 48.1% | -2.7 | +100 theScore Bet | 8 | AGREE |
| Justin Herbert (LAC) | pass_cmp | 18.5 | 42.6% / 41.6% | 49.5% | -7.0 | -110 DraftKings | 10 |  |
| Justin Herbert (LAC) | pass_yds | 199.5 | 51.7% / 50.4% | 50.0% | +1.8 | -113 DraftKings | 3 | AGREE |
| Omarion Hampton (LAC) | rush_att | 10.5 | 84.2% / n/a (cap) | 50.5% | +33.7 | -105 BetOnline.ag | 7 |  |
| Keaton Mitchell (LAC) | rush_att | 7.5 | 29.3% / 30.2% | 51.6% | -22.3 | -110 BetOnline.ag | 6 |  |
| Justin Herbert (LAC) | rush_att | 5.5 | 24.4% / 25.3% | 45.0% | -20.6 | +110 Fliff | 2 |  |
| Omarion Hampton (LAC) | rush_yds | 37.5 | 84.0% / 84.0% | 50.2% | +33.8 | -114 FanDuel | 3 |  |
| Keaton Mitchell (LAC) | rush_yds | 31.5 | 38.9% / 40.2% | 50.2% | -11.3 | -113 DraftKings | 3 |  |
| Justin Herbert (LAC) | rush_yds | 26.5 | 32.3% / 33.4% | 50.1% | -17.8 | -111 DraftKings | 3 |  |

---
## DET@ARI

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | +5.5 | 54.5 | 31.6% |
| market track (sim) | +6.0 | 54.4 | 35.5% |
| model track (sim) | +3.0 | 53.3 | 43.9% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Jahmyr Gibbs (DET) | 75.9% / 71.6% | 82.0% | 73.8% | +2.1 | -400 BetMGM | 6 | AGREE |
| Amon-Ra St. Brown (DET) | 50.6% / 48.5% | 59.0% | 53.1% | -2.5 | -135 BetMGM | 6 | AGREE |
| Jeremiyah Love (ARI) | 46.0% / 47.6% | 57.5% | 51.8% | -5.8 | -118 BetMGM | 6 |  |
| Sam LaPorta (DET) | 43.9% / 40.2% | 37.7% | 34.0% | +9.9 | +180 DraftKings | 6 |  |
| Trey McBride (ARI) | 42.2% / 43.5% | 47.1% | 42.4% | -0.1 | +115 DraftKings | 6 | AGREE |
| Michael Wilson (ARI) | 35.8% / 37.5% | 37.5% | 33.8% | +2.1 | +175 DraftKings | 6 | AGREE |
| Tyler Allgeier (ARI) | 29.7% / 31.6% | 33.1% | 29.8% | -0.1 | +220 FanDuel | 6 | AGREE |
| Jameson Williams (DET) | 25.1% / 22.8% | 35.7% | 32.1% | -7.1 | +185 BetMGM | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Jahmyr Gibbs (DET) | 21.5% / 19.8% | 25.6% | 23.1% | 21.4% | +300 theScore Bet | 6 |
| Amon-Ra St. Brown (DET) | 10.9% / 10.5% | 13.6% | 12.2% | 11.3% | +700 BetMGM | 6 |
| Jeremiyah Love (ARI) | 9.5% / 10.3% | 13.6% | 12.2% | 11.3% | +900 BetMGM | 6 |
| Sam LaPorta (DET) | 9.0% / 8.3% | 7.4% | 6.7% | 6.2% | +1400 theScore Bet | 6 |
| Trey McBride (ARI) | 8.4% / 9.1% | 9.1% | 8.2% | 7.5% | +1100 theScore Bet | 6 |
| Michael Wilson (ARI) | 6.8% / 7.5% | 6.9% | 6.2% | 5.8% | +1400 DraftKings | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett (ARI) | pass_att | 37.5 | 28.9% / 25.5% | 50.7% | -21.8 | +100 betPARX | 8 |  |
| Jacoby Brissett (ARI) | pass_cmp | 25.5 | 36.2% / 34.2% | 48.7% | -12.5 | -105 Hard Rock Bet | 6 |  |
| Jacoby Brissett (ARI) | pass_yds | 269.5 | 26.8% / 25.8% | 49.9% | -23.1 | -111 DraftKings | 2 |  |
| Trey McBride (ARI) | rec | 7.5 | 58.4% / 57.0% | 54.8% | +3.6 | -125 theScore Bet | 11 |  |
| Michael Wilson (ARI) | rec | 5.5 | 44.1% / 43.5% | 56.5% | -12.4 | -140 DraftKings | 9 |  |
| Jeremiyah Love (ARI) | rec | 2.5 | 42.6% / 42.3% | 46.4% | -3.8 | +116 betPARX | 10 |  |
| Kendrick Bourne (ARI) | rec | 2.5 | 49.5% / 49.2% | 44.8% | +4.8 | +120 betPARX | 11 |  |
| Marvin Harrison Jr. (ARI) | rec | 2.5 | 50.8% / 51.0% | 55.2% | -4.4 | -140 BetMGM | 11 |  |
| Trey McBride (ARI) | rec_yds | 80.5 | 36.4% / 34.9% | 50.0% | -13.7 | -114 FanDuel | 2 |  |
| Michael Wilson (ARI) | rec_yds | 73.5 | 27.3% / 27.4% | 50.0% | -22.7 | -112 DraftKings | 2 |  |
| Marvin Harrison Jr. (ARI) | rec_yds | 34.5 | 43.8% / 43.2% | 50.0% | -6.2 | -111 DraftKings | 5 |  |
| Kendrick Bourne (ARI) | rec_yds | 24.5 | 50.4% / 49.9% | 49.7% | +0.8 | -108 DraftKings | 4 | AGREE |
| Jeremiyah Love (ARI) | rush_att | 11.5 | 68.0% / 70.6% | 51.9% | +16.1 | -120 Hard Rock Bet | 5 |  |
| Tyler Allgeier (ARI) | rush_att | 6.5 | 55.1% / 57.4% | 52.1% | +3.0 | -117 DraftKings | 5 |  |
| Jeremiyah Love (ARI) | rush_yds | 45.5 | 65.6% / 67.1% | 50.0% | +15.6 | -114 FanDuel | 2 |  |
| Tyler Allgeier (ARI) | rush_yds | 25.5 | 49.8% / 52.2% | 50.1% | -0.4 | -111 BetMGM | 6 | AGREE |
| Jared Goff (DET) | pass_att | 34.5 | 37.1% / 39.6% | 49.3% | -12.3 | -105 DraftKings | 7 |  |
| Jared Goff (DET) | pass_cmp | 25.5 | 19.8% / 20.7% | 47.8% | -28.0 | +100 BetOnline.ag | 6 |  |
| Jared Goff (DET) | pass_yds | 279.5 | 43.6% / 44.2% | 50.0% | -6.4 | -112 DraftKings | 2 |  |
| Amon-Ra St. Brown (DET) | rec | 7.5 | 29.7% / 30.8% | 45.5% | -15.8 | +115 betPARX | 10 |  |
| Jahmyr Gibbs (DET) | rec | 4.5 | 37.5% / 37.3% | 52.2% | -14.7 | -115 theScore Bet | 11 |  |
| Sam LaPorta (DET) | rec | 4.5 | 60.0% / 60.6% | 56.4% | +3.7 | -143 BetOnline.ag | 11 |  |
| Jameson Williams (DET) | rec | 3.5 | 44.0% / 44.6% | 52.8% | -8.9 | -113 betPARX | 11 |  |
| Isaac TeSlaa (DET) | rec | 2.5 | 22.0% / 21.7% | 40.5% | -18.5 | +139 BetOnline.ag | 11 |  |
| Amon-Ra St. Brown (DET) | rec_yds | 80.5 | 42.4% / 43.0% | 49.8% | -7.4 | -110 DraftKings | 4 |  |
| Jameson Williams (DET) | rec_yds | 53.5 | 45.6% / 46.1% | 49.9% | -4.3 | -111 DraftKings | 3 |  |
| Sam LaPorta (DET) | rec_yds | 51.5 | 57.6% / 57.1% | 49.9% | +7.6 | -110 DraftKings | 5 |  |
| Jahmyr Gibbs (DET) | rec_yds | 37.5 | 40.1% / 39.6% | 49.9% | -9.9 | -112 DraftKings | 5 |  |
| Isaac TeSlaa (DET) | rec_yds | 25.5 | 40.5% / 40.1% | 50.1% | -9.6 | -112 DraftKings | 5 |  |
| Jahmyr Gibbs (DET) | rush_att | 19.5 | 49.6% / 46.5% | 50.0% | -0.5 | -110 DraftKings | 6 | AGREE |
| Jahmyr Gibbs (DET) | rush_yds | 93.5 | 39.1% / 37.0% | 50.0% | -10.9 | -111 DraftKings | 3 |  |

---
## SF@SEA

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.0 | 46.0 | 60.3% |
| market track (sim) | -3.0 | 45.5 | 58.7% |
| model track (sim) | -2.0 | 48.1 | 54.8% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Jaxon Smith-Njigba (SEA) | 51.6% / 53.4% | 52.9% | 47.6% | +4.0 | -105 DraftKings | 6 |  |
| Christian McCaffrey (SF) | 49.6% / 54.4% | 58.3% | 52.5% | -2.9 | -139 BetRivers | 6 | AGREE |
| Emanuel Wilson (SEA) | 44.8% / 45.6% | 54.8% | 49.3% | -4.5 | -115 FanDuel | 6 |  |
| AJ Barner (SEA) | 30.2% / 31.6% | 25.0% | 22.5% | +7.7 | +310 DraftKings | 6 |  |
| George Kittle (SF) | 30.0% / 33.1% | 35.4% | 31.9% | -1.8 | +185 DraftKings | 6 | AGREE |
| Mike Evans (SF) | 29.3% / 32.6% | 33.9% | 30.5% | -1.2 | +200 FanDuel | 6 | AGREE |
| Deebo Samuel (SF) | 28.2% / 30.6% | 31.0% | 27.9% | +0.3 | +230 FanDuel | 6 | AGREE |
| George Holani (SEA) | 26.5% / 27.6% | 27.2% | 24.5% | +2.0 | +310 FanDuel | 6 | AGREE |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Jaxon Smith-Njigba (SEA) | 13.3% / 12.9% | 14.3% | 12.9% | 11.9% | +600 DraftKings | 6 |
| Christian McCaffrey (SF) | 12.7% / 13.3% | 16.7% | 15.0% | 13.7% | +500 DraftKings | 6 |
| Emanuel Wilson (SEA) | 11.1% / 10.6% | 16.7% | 15.0% | 14.1% | +525 Bally Bet | 6 |
| AJ Barner (SEA) | 6.7% / 6.6% | 6.1% | 5.5% | 5.0% | +1800 theScore Bet | 6 |
| George Kittle (SF) | 6.6% / 6.9% | 7.7% | 7.0% | 6.5% | +1400 theScore Bet | 6 |
| Mike Evans (SF) | 6.5% / 6.8% | 7.7% | 6.9% | 6.4% | +1300 theScore Bet | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Sam Darnold (SEA) | pass_att | 30.5 | 37.0% / 39.2% | 50.8% | -13.9 | -107 betPARX | 9 |  |
| Sam Darnold (SEA) | pass_cmp | 19.5 | 46.6% / 48.1% | 53.4% | -6.8 | -129 betPARX | 8 |  |
| Sam Darnold (SEA) | pass_yds | 225.5 | 38.9% / 40.7% | 49.9% | -11.0 | -111 DraftKings | 2 |  |
| Jaxon Smith-Njigba (SEA) | rec | 6.5 | 52.7% / 53.8% | 52.4% | +0.2 | -121 DraftKings | 10 | AGREE |
| AJ Barner (SEA) | rec | 2.5 | 59.2% / 59.6% | 49.2% | +10.0 | +102 DraftKings | 11 |  |
| Cooper Kupp (SEA) | rec | 2.5 | 44.3% / 44.3% | 45.3% | -1.1 | +116 FanDuel | 11 | AGREE |
| Jaxon Smith-Njigba (SEA) | rec_yds | 92.5 | 43.4% / 44.7% | 50.2% | -6.7 | -113 DraftKings | 3 |  |
| Cooper Kupp (SEA) | rec_yds | 23.5 | 50.3% / 50.5% | 50.3% | +0.1 | -114 FanDuel | 2 |  |
| AJ Barner (SEA) | rec_yds | 22.5 | 55.0% / 55.5% | 50.4% | +4.6 | -114 BetOnline.ag | 4 |  |
| Rashid Shaheed (SEA) | rec_yds | 20.5 | 58.9% / 59.6% | 50.0% | +8.8 | -113 DraftKings | 5 |  |
| Emanuel Wilson (SEA) | rush_att | 16.5 | 48.1% / 46.7% | 51.0% | -2.9 | -117 DraftKings | 4 | AGREE |
| Emanuel Wilson (SEA) | rush_yds | 63.5 | 47.5% / 46.6% | 50.1% | -2.6 | -112 DraftKings | 3 | AGREE |
| George Holani (SEA) | rush_yds | 19.5 | 64.4% / 64.5% | 50.1% | +14.4 | -113 DraftKings | 4 |  |
| Brock Purdy (SF) | pass_att | 32.5 | 20.5% / 19.9% | 49.4% | -28.8 | -105 Hard Rock Bet | 9 |  |
| Brock Purdy (SF) | pass_cmp | 20.5 | 37.2% / 36.3% | 51.2% | -14.0 | -116 DraftKings | 5 |  |
| Brock Purdy (SF) | pass_yds | 226.5 | 31.1% / 31.2% | 50.1% | -19.0 | -112 DraftKings | 3 |  |
| Christian McCaffrey (SF) | rec | 4.5 | 46.8% / 46.0% | 53.0% | -6.1 | -125 FanDuel | 11 |  |
| George Kittle (SF) | rec | 4.5 | 43.6% / 42.6% | 50.4% | -6.8 | -106 FanDuel | 11 |  |
| Deebo Samuel (SF) | rec | 3.5 | 39.8% / 39.9% | 50.2% | -10.5 | -105 DraftKings | 10 |  |
| Mike Evans (SF) | rec | 3.5 | 55.9% / 56.1% | 58.4% | -2.4 | -155 theScore Bet | 9 | AGREE |
| George Kittle (SF) | rec_yds | 53.5 | 34.5% / 34.2% | 49.8% | -15.2 | -110 DraftKings | 2 |  |
| Mike Evans (SF) | rec_yds | 48.5 | 43.4% / 43.3% | 49.9% | -6.5 | -110 DraftKings | 3 |  |
| Christian McCaffrey (SF) | rec_yds | 36.5 | 39.9% / 39.5% | 49.7% | -9.8 | -111 DraftKings | 4 |  |
| Deebo Samuel (SF) | rec_yds | 34.5 | 47.5% / 48.2% | 49.4% | -1.9 | -108 DraftKings | 4 | AGREE |
| Christian McCaffrey (SF) | rush_att | 14.5 | 32.9% / 33.6% | 50.9% | -18.1 | -115 DraftKings | 8 |  |
| Christian McCaffrey (SF) | rush_yds | 51.5 | 54.5% / 55.0% | 50.0% | +4.5 | -114 FanDuel | 4 |  |
| Brock Purdy (SF) | rush_yds | 21.5 | 28.1% / 27.4% | 50.0% | -21.9 | -114 FanDuel | 3 |  |
| Kaelon Black (SF) | rush_yds | 15.5 | 75.4% / 75.3% | 50.2% | +25.3 | -112 DraftKings | 3 |  |
| Deebo Samuel (SF) | rush_yds | 8.5 | n/a (cap) | 50.2% |  | -114 DraftKings | 3 |  |

---
## BAL@ATL

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.5 | 43.5 | 60.9% |
| market track (sim) | -3.0 | 43.4 | 58.9% |
| model track (sim) | -0.0 | 48.3 | 49.3% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Bijan Robinson (ATL) | 66.1% / 67.9% | 70.8% | 63.7% | +2.3 | -230 FanDuel | 6 | AGREE |
| Derrick Henry (BAL) | 52.0% / 61.1% | 60.2% | 54.1% | -2.1 | -150 DraftKings | 6 | AGREE |
| Brian Robinson Jr. (ATL) | 35.0% / 36.2% | 30.3% | 27.3% | +7.7 | +240 FanDuel | 6 |  |
| Zay Flowers (BAL) | 31.0% / 38.5% | 33.3% | 30.0% | +1.0 | +205 DraftKings | 6 | AGREE |
| Mark Andrews (BAL) | 23.1% / 28.3% | 28.0% | 25.2% | -2.0 | +300 BetMGM | 6 | AGREE |
| Drake London (ATL) | 23.0% / 24.5% | 44.9% | 40.5% | -17.5 | +125 DraftKings | 6 |  |
| Rashod Bateman (BAL) | 15.5% / 20.2% | 18.5% | 16.7% | -1.1 | +525 BetMGM | 6 | AGREE |
| Kyle Pitts (ATL) | 13.4% / 13.7% | 21.3% | 19.1% | -5.8 | +380 BetRivers | 6 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Bijan Robinson (ATL) | 21.4% / 19.5% | 25.3% | 22.8% | 21.5% | +300 DraftKings | 6 |
| Derrick Henry (BAL) | 14.5% / 16.4% | 19.1% | 17.2% | 16.0% | +450 theScore Bet | 6 |
| Brian Robinson Jr. (ATL) | 8.7% / 7.9% | 8.3% | 7.5% | 6.9% | +1200 Hard Rock Bet | 6 |
| Zay Flowers (BAL) | 7.5% / 8.6% | 7.8% | 7.1% | 6.5% | +1300 theScore Bet | 6 |
| Mark Andrews (BAL) | 5.4% / 5.9% | 6.5% | 5.8% | 5.5% | +1750 BetMGM | 6 |
| Drake London (ATL) | 5.3% / 5.0% | 12.5% | 11.3% | 10.3% | +800 DraftKings | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. (ATL) | pass_att | 29.5 | 15.4% / 17.6% | 49.6% | -34.2 | -105 theScore Bet | 9 |  |
| Michael Penix Jr. (ATL) | pass_cmp | 18.5 | 27.3% / 29.7% | 47.7% | -20.5 | +102 DraftKings | 9 |  |
| Michael Penix Jr. (ATL) | pass_yds | 216.5 | 27.6% / 29.1% | 50.0% | -22.4 | -112 DraftKings | 2 |  |
| Drake London (ATL) | rec | 5.5 | 31.7% / 32.8% | 54.8% | -23.1 | -130 BetOnline.ag | 10 |  |
| Bijan Robinson (ATL) | rec | 3.5 | 45.8% / 46.9% | 52.8% | -7.0 | -120 BetMGM | 11 |  |
| Kyle Pitts (ATL) | rec | 2.5 | 50.3% / 51.2% | 45.2% | +5.1 | +118 betPARX | 11 |  |
| Drake London (ATL) | rec_yds | 81.5 | 32.5% / 32.7% | 50.1% | -17.6 | -112 DraftKings | 4 |  |
| Bijan Robinson (ATL) | rec_yds | 26.5 | 45.3% / 46.3% | 50.0% | -4.7 | -114 FanDuel | 2 |  |
| Kyle Pitts (ATL) | rec_yds | 24.5 | 47.0% / 47.9% | 49.9% | -2.9 | -110 DraftKings | 5 | AGREE |
| Jahan Dotson (ATL) | rec_yds | 19.5 | 48.9% / 48.7% | 50.0% | -1.2 | -110 DraftKings | 5 | AGREE |
| Bijan Robinson (ATL) | rush_att | 18.5 | 41.2% / 39.5% | 51.5% | -10.3 | -117 DraftKings | 4 |  |
| Brian Robinson Jr. (ATL) | rush_att | 9.5 | 35.4% / 34.7% | 44.7% | -9.3 | +112 betPARX | 4 |  |
| Bijan Robinson (ATL) | rush_yds | 89.5 | 51.0% / 49.9% | 50.1% | +0.8 | -114 DraftKings | 3 | AGREE |
| Brian Robinson Jr. (ATL) | rush_yds | 35.5 | 45.0% / 44.6% | 49.5% | -4.6 | -108 DraftKings | 4 |  |
| Zay Flowers (BAL) | rec | 5.5 | 50.3% / 49.3% | 47.4% | +3.0 | +108 betPARX | 11 | AGREE |
| Mark Andrews (BAL) | rec | 3.5 | 59.1% / 57.9% | 52.9% | +6.2 | -115 BetMGM | 11 |  |
| Zay Flowers (BAL) | rec_yds | 68.5 | 59.9% / 58.9% | 50.1% | +9.8 | -114 DraftKings | 5 |  |
| Mark Andrews (BAL) | rec_yds | 30.5 | 57.4% / 56.5% | 49.9% | +7.4 | -111 DraftKings | 3 |  |
| Rashod Bateman (BAL) | rec_yds | 17.5 | 63.4% / 62.3% | 50.3% | +13.1 | -112 DraftKings | 6 |  |
| Derrick Henry (BAL) | rush_att | 20.5 | 40.5% / 42.1% | 49.5% | -9.0 | -108 DraftKings | 4 |  |
| Derrick Henry (BAL) | rush_yds | 85.5 | 35.5% / 36.5% | 49.9% | -14.3 | -110 DraftKings | 4 |  |
| Justice Hill (BAL) | rush_yds | 11.5 | 36.7% / 37.5% | 50.7% | -14.0 | -114 FanDuel | 4 |  |

---
## BUF@LA

| Source | Home spread | Total | Home win prob |
|---|---|---|---|
| Books (17 books, modal line / avg no-vig ML) | -3.5 | 54.5 | 60.7% |
| market track (sim) | -3.0 | 54.3 | 58.4% |
| model track (sim) | -0.0 | 51.7 | 51.6% |

**Anytime TD** (model probability vs book; Estimated no-vig is a flat 10% haircut on a one-sided market, so read the level loosely and the ranking firmly)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig | Gap | Best price | Feeds | |
|---|---|---|---|---|---|---|---|
| Kyren Williams (LA) | 64.1% / 59.6% | 64.6% | 58.2% | +6.0 | -170 FanDuel | 6 |  |
| James Cook (BUF) | 61.5% / 61.0% | 54.0% | 48.6% | +12.9 | -115 DraftKings | 6 |  |
| Davante Adams (LA) | 43.2% / 40.1% | 51.8% | 46.6% | -3.5 | -104 BetRivers | 6 |  |
| Puka Nacua (LA) | 41.8% / 38.5% | 56.0% | 50.4% | -8.6 | -124 BetRivers | 6 |  |
| Blake Corum (LA) | 30.4% / 28.0% | 28.2% | 25.4% | +5.0 | +270 FanDuel | 6 |  |
| Josh Allen (BUF) | 30.2% / 29.9% | 54.4% | 49.0% | -18.8 | -110 DraftKings | 6 |  |
| Khalil Shakir (BUF) | 29.7% / 29.7% | 29.0% | 26.1% | +3.6 | +250 BetRivers | 5 |  |
| DJ Moore (BUF) | 24.1% / 23.9% | 34.8% | 31.3% | -7.2 | +195 BetRivers | 2 |  |

**First TD scorer** (model vs book; no agreement claimed)

| Player | Model (mkt / model-only track) | Book implied, vig in | Book Estimated no-vig (10% flat, unreliable) | Book ceiling (listed field = 1) | Best price | Feeds |
|---|---|---|---|---|---|---|
| Kyren Williams (LA) | 15.4% / 14.5% | 16.7% | 15.0% | 13.5% | +500 DraftKings | 6 |
| James Cook (BUF) | 14.2% / 14.9% | 13.6% | 12.2% | 11.2% | +650 DraftKings | 6 |
| Davante Adams (LA) | 8.5% / 8.2% | 11.4% | 10.3% | 9.0% | +875 BetMGM | 6 |
| Puka Nacua (LA) | 8.2% / 7.7% | 12.1% | 10.9% | 9.7% | +850 BetMGM | 6 |
| Blake Corum (LA) | 5.6% / 5.4% | 5.1% | 4.6% | 4.1% | +2000 theScore Bet | 6 |
| Josh Allen (BUF) | 5.5% / 5.8% | 13.4% | 12.1% | 10.4% | +700 DraftKings | 6 |

**Count and yardage props, Over side** (model P(over) vs no-vig P(over) at the books' main line; see level-bias note)

| Player | Market | Line | Model P(over) mkt / model-only | Book no-vig P(over) | Gap | Best Over | Feeds | |
|---|---|---|---|---|---|---|---|---|
| Josh Allen (BUF) | pass_att | 32.5 | 23.5% / 22.3% | 48.7% | -25.2 | +100 BetMGM | 6 |  |
| Josh Allen (BUF) | pass_cmp | 20.5 | 23.9% / 23.5% | 52.2% | -28.3 | -114 betPARX | 8 |  |
| Josh Allen (BUF) | pass_yds | 244.5 | 23.2% / 23.2% | 50.0% | -26.8 | -111 DraftKings | 5 |  |
| Dalton Kincaid (BUF) | rec | 4.5 | 21.2% / 21.3% | 42.3% | -21.1 | +126 BetOnline.ag | 11 |  |
| Khalil Shakir (BUF) | rec | 4.5 | 29.8% / 29.8% | 43.3% | -13.5 | +116 FanDuel | 1 |  |
| Keon Coleman (BUF) | rec | 2.5 | 44.3% / 43.1% | 59.0% | -14.8 | -172 FanDuel | 1 |  |
| Ty Johnson (BUF) | rec | 2.5 | 24.4% / 24.2% | 37.1% | -12.8 | +152 FanDuel | 1 |  |
| Dalton Kincaid (BUF) | rec_yds | 52.5 | 24.0% / 24.3% | 49.9% | -25.8 | -110 DraftKings | 3 |  |
| Khalil Shakir (BUF) | rec_yds | 43.5 | 38.1% / 38.3% | 50.0% | -11.9 | -114 FanDuel | 1 |  |
| Keon Coleman (BUF) | rec_yds | 37.5 | 32.6% / 31.8% | 50.0% | -17.4 | -114 FanDuel | 1 |  |
| Joshua Palmer (BUF) | rec_yds | 19.5 | 36.4% / 36.3% | 50.0% | -13.6 | -114 FanDuel | 1 |  |
| James Cook (BUF) | rush_att | 17.5 | 34.2% / 36.1% | 47.3% | -13.1 | +100 DraftKings | 5 |  |
| Josh Allen (BUF) | rush_att | 7.5 | 21.1% / 21.7% | 51.5% | -30.5 | -114 DraftKings | 6 |  |
| James Cook (BUF) | rush_yds | 75.5 | 56.0% / 56.9% | 49.8% | +6.2 | -112 BetOnline.ag | 4 |  |
| Josh Allen (BUF) | rush_yds | 36.5 | 17.4% / 17.5% | 50.0% | -32.6 | -113 DraftKings | 6 |  |
| Matthew Stafford (LA) | pass_att | 37.5 | 28.7% / 30.4% | 49.6% | -20.9 | -104 betPARX | 7 |  |
| Matthew Stafford (LA) | pass_cmp | 23.5 | 34.1% / 36.0% | 48.7% | -14.6 | -105 Hard Rock Bet | 6 |  |
| Matthew Stafford (LA) | pass_yds | 277.5 | 40.2% / 41.4% | 49.9% | -9.7 | -111 DraftKings | 4 |  |
| Puka Nacua (LA) | rec | 7.5 | 34.7% / 35.3% | 45.1% | -10.4 | +120 betPARX | 10 |  |
| Davante Adams (LA) | rec | 4.5 | 54.4% / 55.2% | 47.0% | +7.4 | +110 betPARX | 11 |  |
| Kyren Williams (LA) | rec | 2.5 | 55.0% / 56.2% | 56.2% | -1.2 | -140 BetMGM | 11 | AGREE |
| Tyler Higbee (LA) | rec | 2.5 | 43.6% / 44.6% | 54.2% | -10.6 | -138 FanDuel | 1 |  |
| Puka Nacua (LA) | rec_yds | 94.5 | 40.0% / 40.5% | 49.9% | -9.9 | -112 DraftKings | 4 |  |
| Davante Adams (LA) | rec_yds | 62.5 | 54.4% / 55.1% | 50.2% | +4.3 | -114 DraftKings | 4 |  |
| Tyler Higbee (LA) | rec_yds | 25.5 | 41.7% / 42.4% | 50.0% | -8.3 | -114 FanDuel | 1 |  |
| Kyren Williams (LA) | rec_yds | 20.5 | 48.1% / 48.7% | 50.3% | -2.2 | -114 DraftKings | 3 | AGREE |
| Colby Parkinson (LA) | rec_yds | 16.5 | 36.9% / 37.1% | 50.0% | -13.1 | -114 FanDuel | 1 |  |
| Kyren Williams (LA) | rush_att | 15.5 | 35.4% / 34.3% | 47.1% | -11.7 | +100 Hard Rock Bet | 4 |  |
| Kyren Williams (LA) | rush_yds | 68.5 | 48.0% / 47.3% | 50.1% | -2.1 | -114 FanDuel | 3 | AGREE |
| Blake Corum (LA) | rush_yds | 32.5 | 50.6% / 49.6% | 50.0% | +0.6 | -112 DraftKings | 3 | AGREE |