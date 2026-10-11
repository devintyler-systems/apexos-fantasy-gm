# Week 5 2026 Sunday slate (APEX weekly engine), frozen 2026-10-11T06:58Z

- MARKET-ANCHORED run `2026_w05_market_20261011T065831Z`, as_of_utc 2026-10-11T06:58:31Z, git 62785380
- MODEL-ONLY run `2026_w05_model_20261011T065831Z`, as_of_utc 2026-10-11T06:58:31Z, git 62785380
- Inputs: nflverse fetched 2026-10-11T06:41Z; depth chart snapshot 2026-10-11T06:01:52Z; injuries = the week 5 NFL report with game statuses for all 30 playing teams (no timestamp in the feed). Stats stop at week 4: the Thursday TB@DAL result (TB 24, DAL 16) does not enter the model. Kickoffs in US Eastern.
- USED: nflverse schedule spread/total (market-anchored track only). NOT USED: odds, DK salaries, manual overrides. There are no market numbers in this file and no pick is labeled edge or confident (postmortem P0 #2). Official inactives are NOT applied yet; they post about 90 minutes before each window.
- Confidence columns are a reliability index, not a hit probability. No single-prop probability here exceeds 85%. Player projections are conditional on the player playing; availability is shown separately.
- The played Thursday game (TB@DAL) is excluded. Monday BUF@LA (8:15 PM ET, 10-12) is included at the end.


## Read before using any number

1. **Availability changed a lot since Thursday and the report is now complete.** BAL Lamar Jackson is Out (Tyler Huntley starts). CHI Caleb Williams is Questionable and modeled at 35% active (Tyson Bagent 65%), and CHI Monangai is Out. PHI Barkley, DeVonta Smith and Marquise Brown are Out. WAS Mariota and Diggs are Out, McLaurin Questionable (0.67). LAC Johnston and Thompson are Out, McConkey Questionable (0.50). NYJ Hall and Mitchell are Out. CIN Chase and Higgins are Questionable (0.75). LV Jeanty is Questionable (0.50). Questionable values are the fitted practice-status probabilities, not news.
2. **Official inactives are not in.** They post about 90 minutes before each window (about 12:00Z for PHI@JAX, 15:30Z for the 1 PM games). The nflverse feed never carries them. Rerun the affected games after they post.
3. **The engine does not carry quarterback quality to receivers.** Huntley (BAL) projects at about 222 passing yards, above Jackson's frozen 217, and Bagent (CHI) at 221 above Williams' 208. Every BAL and CHI pass-catcher is not discounted for the backup. Treat those two games as the least reliable.
4. **PHI running back output is unreliable.** About 11 of PHI's 25.6 team carries are not assigned to any named player (Barkley and Bigsby are out; Pierce and Steele have no 2026 stats). Shipley is probably under-projected, and Hurts's rushing TD share is probably inflated (anytime TD 0.27 in the market track).
5. **Backup running backs carry big redistributions that history does not support yet.** NYJ Braelon Allen 18.7 carries (his share 69.5% vs 33% season to date) and anytime TD 0.50; CHI Swift 20.7 carries (61% share vs 43%). Treat as upper-range.
6. **The target-share cap is disabled.** No player is above 34% (Smith-Njigba 33.9%, Bowers 33.7%, Wilson 32.2%), but nothing enforces it.
7. **Thursday result for the record:** TB 24, DAL 16 against a sim that had DAL winning (75% market-anchored, 65% model-only). That game is graded Tuesday and it does not enter this run.
8. **No market numbers exist in this file.** The Thursday odds workbooks are two days old and were not used; send new ones for the Sunday slate and I will price against them.


---
## PHI @ JAX  (2026-10-11 09:30 ET)  [neutral site, London]

| Track | Winner (win prob) | PHI pts mean / median | JAX pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | JAX 73% | PHI 16.5 / 16 | JAX 25.0 / 24 | 41.5 / 41 | -8.0 |
| model | JAX 67% | PHI 18.9 / 17 | JAX 25.0 / 24 | 43.9 / 44 | -6.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Jalen Hurts (PHI) | QB | 98% | 18.7 | 218 [166-262] (217) | 1.09 |  |  |  | 27.3% / 32.1% | 85 |
| Will Shipley (PHI) | RB | 100% |  |  |  | 34 [16-45] (34) | 1.3 [0-2] | 10 [0-16] (10) | 20.1% / 23.7% | 52 |
| Dontayvion Wicks (PHI) | WR | 96% |  |  |  | 0 [0-0] (0) | 4.3 [3-6] | 61 [30-83] (61) | 27.1% / 31.7% | 63 |
| Makai Lemon (PHI) | WR | 100% |  |  |  | 2 [0-1] (2) | 3.9 [2-5] | 46 [22-64] (46) | 15.5% / 19.0% | 56 |
| Darius Cooper (PHI) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.6 [0-2] | 20 [0-31] (20) | 18.2% / 21.3% | 31 |
| Dallas Goedert (PHI) | TE | 95% |  |  |  | 0 [0-0] (0) | 4.5 [3-6] | 49 [25-66] (48) | 21.3% / 24.1% | 41 |
| Trevor Lawrence (JAX) | QB | 100% | 17.9 | 203 [151-243] (205) | 1.48 |  |  |  | 9.7% / 9.8% | 86 |
| Bhayshul Tuten (JAX) | RB | 100% |  |  |  | 67 [43-84] (65) | 1.2 [0-2] | 9 [0-14] (9) | 48.8% / 48.7% | 82 |
| Chris Rodriguez Jr. (JAX) | RB | 100% |  |  |  | 33 [16-43] (32) | 0.1 [0-0] | 1 [0-0] (1) | 29.0% / 28.3% | 52 |
| Parker Washington (JAX) | WR | 100% |  |  |  | 1 [0-0] (1) | 4.1 [3-5] | 56 [28-76] (56) | 31.9% / 32.0% | 74 |
| Jakobi Meyers (JAX) | WR | 95% |  |  |  | 1 [0-0] (1) | 3.6 [2-5] | 42 [19-58] (43) | 26.0% / 26.4% | 53 |
| Brian Thomas Jr. (JAX) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.9 [2-4] | 37 [15-52] (38) | 19.6% / 19.5% | 52 |
| Brenton Strange (JAX) | TE | 100% |  |  |  | 0 [0-0] (0) | 3.8 [2-5] | 39 [18-53] (39) | 22.8% / 23.1% | 62 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Bhayshul Tuten (JAX) | 48.8% | 0.56 | 0.08 | 1.6 (6%) | 14.7 (47%) | tgt_sh 5.8%; team att 29.1; opp DvP 0.93; RZ tgt 1; car_sh 46.8%; team rush 30.8; opp d_ypc 0.98; inside-10 car 3 |
| 2 | Parker Washington (JAX) | 31.9% | 0.01 | 0.37 | 6.7 (22%) |  | tgt_sh 22.0%; team att 29.1; opp DvP 1.06; RZ tgt 4 |
| 3 | Chris Rodriguez Jr. (JAX) | 29.0% | 0.33 | 0.01 | 0.1 (0%) | 7.4 (24%) | car_sh 23.7%; team rush 30.8; opp d_ypc 0.98; inside-10 car 3 |
| 4 | Jalen Hurts (PHI) | 27.3% | 0.31 | 0.00 |  |  | team att 31.6; ypa 7.40; opp d_ypa 1.10; pass rate 57.5% |
| 5 | Dontayvion Wicks (PHI) | 27.1% | 0.00 | 0.31 | 7.0 (13%) |  | tgt_sh 13.5%; team att 31.6; opp DvP 1.05; RZ tgt 4 |
| 6 | Jakobi Meyers (JAX) | 26.0% | 0.01 | 0.29 | 5.5 (18%) |  | tgt_sh 18.0%; team att 29.1; opp DvP 1.06; RZ tgt 3 |

**First TD scorer ranking (model probability)**: Bhayshul Tuten (JAX) 14.2%; Parker Washington (JAX) 8.2%; Chris Rodriguez Jr. (JAX) 7.5%; Jalen Hurts (PHI) 6.8%; Dontayvion Wicks (PHI) 6.5%

MODEL-ONLY track anytime top 3 for comparison: Bhayshul Tuten 48.7%; Jalen Hurts 32.1%; Parker Washington 32.0%


---
## CHI @ GB  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | CHI pts mean / median | GB pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | CHI 54% | CHI 24.1 / 24 | GB 22.5 / 22 | 46.5 / 46 | +1.0 |
| model | CHI 58% | CHI 24.9 / 24 | GB 22.0 / 21 | 46.9 / 47 | +3.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Tyson Bagent (CHI) | QB | 65% | 20.2 | 221 [165-266] (219) | 1.14 |  |  |  | 23.5% / 24.7% | 41 |
| D'Andre Swift (CHI) | RB | 95% |  |  |  | 101 [73-124] (101) | 2.2 [1-3] | 16 [5-23] (16) | 66.1% / 68.0% | 77 |
| Roschon Johnson (CHI) | RB | 100% |  |  |  | 6 [0-8] (6) | 0.3 [0-0] | 2 [0-0] (2) | 8.4% / 8.8% | 24 |
| Luther Burden III (CHI) | WR | 100% |  |  |  | 3 [0-2] (3) | 4.1 [3-5] | 49 [24-67] (48) | 24.5% / 25.0% | 70 |
| Rome Odunze (CHI) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.8 [2-5] | 52 [25-72] (51) | 17.8% / 18.9% | 62 |
| Kalif Raymond (CHI) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.4 [2-5] | 37 [17-52] (37) | 17.4% / 18.4% | 65 |
| Colston Loveland (CHI) | TE | 100% |  |  |  | 0 [0-0] (0) | 3.4 [2-5] | 33 [15-46] (33) | 20.2% / 20.8% | 58 |
| Jordan Love (GB) | QB | 100% | 19.2 | 238 [179-286] (240) | 1.72 |  |  |  | 4.4% / 4.4% | 86 |
| MarShawn Lloyd (GB) | RB | 100% |  |  |  | 46 [27-59] (46) | 1.9 [1-3] | 14 [3-20] (14) | 41.4% / 40.5% | 74 |
| Kaleb Johnson (GB) | RB | 100% |  |  |  | 28 [13-37] (27) | 0.4 [0-1] | 3 [0-2] (3) | 18.0% / 17.7% | 51 |
| Christian Watson (GB) | WR | 100% |  |  |  | 0 [0-0] (0) | 4.8 [3-6] | 76 [40-102] (75) | 38.1% / 37.3% | 75 |
| Matthew Golden (GB) | WR | 100% |  |  |  | 1 [0-0] (1) | 4.3 [3-6] | 58 [30-79] (59) | 33.6% / 32.8% | 74 |
| Skyy Moore (GB) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.6 [1-2] | 18 [1-27] (18) | 17.7% / 17.1% | 37 |
| Tucker Kraft (GB) | TE | 100% |  |  |  | 1 [0-0] (1) | 4.6 [3-6] | 52 [27-70] (52) | 30.8% / 30.3% | 73 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | D'Andre Swift (CHI) | 66.1% | 0.93 | 0.09 | 2.9 (9%) | 20.7 (42%) | tgt_sh 9.0%; team att 30.0; opp DvP 0.93; RZ tgt 1; car_sh 42.2%; team rush 33.8; opp d_ypc 1.00; inside-10 car 13 |
| 2 | MarShawn Lloyd (GB) | 41.4% | 0.35 | 0.17 | 2.8 (6%) | 11.2 (46%) | tgt_sh 6.3%; team att 35.1; opp DvP 1.12; RZ tgt 3; car_sh 46.4%; team rush 19.7; opp d_ypc 1.09; inside-10 car 5 |
| 3 | Christian Watson (GB) | 38.1% | 0.00 | 0.47 | 8.4 (20%) |  | tgt_sh 20.2%; team att 35.1; opp DvP 1.00; RZ tgt 7 |
| 4 | Matthew Golden (GB) | 33.6% | 0.00 | 0.40 | 7.8 (19%) |  | tgt_sh 18.8%; team att 35.1; opp DvP 1.00; RZ tgt 5 |
| 5 | Tucker Kraft (GB) | 30.8% | 0.02 | 0.34 | 7.4 (18%) |  | tgt_sh 18.3%; team att 35.1; opp DvP 0.92; RZ tgt 4 |
| 6 | Luther Burden III (CHI) | 24.5% | 0.02 | 0.26 | 6.2 (19%) | 0.6 (1%) | tgt_sh 19.1%; team att 30.0; opp DvP 0.93; RZ tgt 6 |

**First TD scorer ranking (model probability)**: D'Andre Swift (CHI) 19.7%; MarShawn Lloyd (GB) 10.0%; Christian Watson (GB) 9.0%; Matthew Golden (GB) 7.6%; Tucker Kraft (GB) 6.9%

MODEL-ONLY track anytime top 3 for comparison: D'Andre Swift 68.0%; MarShawn Lloyd 40.5%; Christian Watson 37.3%


---
## CIN @ MIA  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | CIN pts mean / median | MIA pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | CIN 70% | CIN 25.3 / 24 | MIA 18.2 / 17 | 43.6 / 43 | +7.0 |
| model | CIN 57% | CIN 23.7 / 23 | MIA 21.1 / 20 | 44.8 / 44 | +3.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Joe Burrow (CIN) | QB | 100% | 25.6 | 275 [211-326] (278) | 1.71 |  |  |  | 8.4% / 7.4% | 88 |
| Chase Brown (CIN) | RB | 100% |  |  |  | 59 [38-75] (58) | 5.2 [3-7] | 36 [18-48] (36) | 57.3% / 53.2% | 81 |
| Samaje Perine (CIN) | RB | 100% |  |  |  | 20 [8-27] (19) | 1.7 [1-3] | 13 [1-20] (13) | 22.4% / 20.6% | 51 |
| Ja'Marr Chase (CIN) | WR | 75% |  |  |  | 0 [0-0] (0) | 6.6 [4-8] | 74 [43-97] (75) | 37.2% / 35.7% | 59 |
| Tee Higgins (CIN) | WR | 75% |  |  |  | 0 [0-0] (0) | 5.6 [4-7] | 82 [45-110] (84) | 31.1% / 29.4% | 58 |
| Mitchell Tinsley (CIN) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.9 [1-3] | 25 [5-37] (25) | 19.3% / 18.3% | 29 |
| Mike Gesicki (CIN) | TE | 100% |  |  |  | 0 [0-0] (0) | 3.6 [2-5] | 39 [17-54] (39) | 25.2% / 23.0% | 55 |
| Malik Willis (MIA) | QB | 100% | 16.6 | 212 [159-255] (210) | 0.93 |  |  |  | 15.6% / 19.0% | 86 |
| Ollie Gordon II (MIA) | RB | 100% |  |  |  | 61 [38-79] (63) | 1.2 [0-2] | 10 [0-15] (10) | 37.3% / 43.4% | 66 |
| Jaylen Wright (MIA) | RB | 65% |  |  |  | 24 [10-33] (25) | 0.4 [0-1] | 4 [0-4] (4) | 19.7% / 24.0% | 24 |
| Malik Washington (MIA) | WR | 100% |  |  |  | 6 [0-8] (6) | 5.0 [3-7] | 63 [34-84] (62) | 30.6% / 36.2% | 76 |
| Chris Bell (MIA) | WR | 95% |  |  |  | 0 [0-0] (0) | 2.8 [1-4] | 44 [17-63] (43) | 12.9% / 15.3% | 47 |
| Kevin Coleman Jr. (MIA) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.2 [1-3] | 31 [9-46] (31) | 13.9% / 17.0% | 41 |
| Greg Dulcich (MIA) | TE | 100% |  |  |  | 0 [0-0] (0) | 3.1 [2-4] | 38 [16-54] (38) | 19.9% / 23.9% | 49 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Chase Brown (CIN) | 57.3% | 0.57 | 0.25 | 6.1 (13%) | 15.4 (64%) | tgt_sh 13.1%; team att 36.6; opp DvP 0.97; RZ tgt 1; car_sh 64.1%; team rush 23.0; opp d_ypc 0.93; inside-10 car 3 |
| 2 | Ollie Gordon II (MIA) | 37.3% | 0.41 | 0.05 | 1.7 (4%) | 13.3 (24%) | tgt_sh 3.5%; team att 30.1; opp DvP 1.13; RZ tgt 0; car_sh 24.2%; team rush 25.7; opp d_ypc 1.04; inside-10 car 1 |
| 3 | Ja'Marr Chase (CIN) | 37.2% | 0.00 | 0.46 | 9.0 (23%) |  | tgt_sh 22.5%; team att 36.6; opp DvP 0.96; RZ tgt 4 |
| 4 | Tee Higgins (CIN) | 31.1% | 0.00 | 0.37 | 8.0 (20%) |  | tgt_sh 20.0%; team att 36.6; opp DvP 0.96; RZ tgt 2 |
| 5 | Malik Washington (MIA) | 30.6% | 0.08 | 0.27 | 8.7 (20%) | 1.4 (3%) | tgt_sh 19.8%; team att 30.1; opp DvP 0.88; RZ tgt 1 |
| 6 | Mike Gesicki (CIN) | 25.2% | 0.00 | 0.29 | 4.7 (9%) |  | tgt_sh 9.5%; team att 36.6; opp DvP 1.13; RZ tgt 3 |

**First TD scorer ranking (model probability)**: Chase Brown (CIN) 17.5%; Ja'Marr Chase (CIN) 9.7%; Ollie Gordon II (MIA) 9.6%; Tee Higgins (CIN) 7.9%; Malik Washington (MIA) 7.4%

MODEL-ONLY track anytime top 3 for comparison: Chase Brown 53.2%; Ollie Gordon II 43.4%; Malik Washington 36.2%


---
## LV @ NE  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | LV pts mean / median | NE pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | NE 60% | LV 21.0 / 20 | NE 24.5 / 24 | 45.5 / 45 | -4.0 |
| model | NE 64% | LV 19.4 / 19 | NE 24.2 / 24 | 43.6 / 43 | -4.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Kirk Cousins (LV) | QB | 100% | 20.2 | 233 [177-279] (234) | 1.39 |  |  |  | 5.9% / 5.6% | 87 |
| Ashton Jeanty (LV) | RB | 50% |  |  |  | 61 [39-76] (60) | 3.9 [2-5] | 31 [15-43] (31) | 50.3% / 45.8% | 41 |
| Mike Washington Jr. (LV) | RB | 100% |  |  |  | 51 [22-72] (50) | 0.5 [0-1] | 4 [0-5] (4) | 21.5% / 18.9% | 51 |
| Tre Tucker (LV) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.9 [2-5] | 57 [27-78] (57) | 21.9% / 19.2% | 70 |
| Cody White (LV) | WR | 95% |  |  |  | 0 [0-0] (0) | 1.4 [0-2] | 19 [0-29] (19) | 17.3% / 14.9% | 29 |
| Malik Benson (LV) | WR | 100% |  |  |  | 1 [0-0] (1) | 0.7 [0-1] | 10 [0-15] (10) | 4.5% / 4.1% | 21 |
| Brock Bowers (LV) | TE | 95% |  |  |  | 0 [0-0] (0) | 7.5 [5-9] | 85 [53-110] (86) | 38.9% / 35.7% | 68 |
| Drake Maye (NE) | QB | 98% | 17.0 | 200 [147-243] (199) | 1.66 |  |  |  | 19.3% / 18.8% | 84 |
| TreVeyon Henderson (NE) | RB | 100% |  |  |  | 63 [39-81] (63) | 1.3 [0-2] | 10 [0-15] (10) | 40.8% / 39.8% | 69 |
| Rhamondre Stevenson (NE) | RB | 65% |  |  |  | 38 [21-51] (39) | 2.9 [2-4] | 25 [10-35] (25) | 39.4% / 40.1% | 49 |
| Romeo Doubs (NE) | WR | 100% |  |  |  | 0 [0-0] (0) | 4.5 [3-6] | 66 [34-89] (66) | 42.0% / 40.2% | 66 |
| DeMario Douglas (NE) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.9 [2-4] | 38 [15-54] (37) | 26.9% / 26.6% | 56 |
| Kyle Williams (NE) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.1 [0-2] | 14 [0-23] (15) | 8.2% / 8.1% | 24 |
| Hunter Henry (NE) | TE | 100% |  |  |  | 0 [0-0] (0) | 3.6 [2-5] | 41 [19-57] (40) | 25.2% / 25.3% | 56 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Ashton Jeanty (LV) | 50.3% | 0.34 | 0.32 | 5.5 (15%) | 16.8 (61%) | tgt_sh 14.6%; team att 33.5; opp DvP 1.00; RZ tgt 6; car_sh 60.7%; team rush 26.9; opp d_ypc 1.03; inside-10 car 7 |
| 2 | Romeo Doubs (NE) | 42.0% | 0.00 | 0.53 | 7.9 (17%) |  | tgt_sh 16.8%; team att 29.9; opp DvP 1.04; RZ tgt 4 |
| 3 | TreVeyon Henderson (NE) | 40.8% | 0.43 | 0.08 | 1.9 (4%) | 13.5 (39%) | tgt_sh 4.2%; team att 29.9; opp DvP 0.98; RZ tgt 0; car_sh 39.1%; team rush 29.2; opp d_ypc 1.13; inside-10 car 1 |
| 4 | Rhamondre Stevenson (NE) | 39.4% | 0.30 | 0.18 | 4.1 (10%) | 8.4 (28%) | tgt_sh 10.1%; team att 29.9; opp DvP 0.98; RZ tgt 0; car_sh 27.9%; team rush 29.2; opp d_ypc 1.13; inside-10 car 2 |
| 5 | Brock Bowers (LV) | 38.9% | 0.00 | 0.48 | 11.3 (25%) |  | tgt_sh 25.0%; team att 33.5; opp DvP 1.11; RZ tgt 4 |
| 6 | DeMario Douglas (NE) | 26.9% | 0.00 | 0.31 | 5.1 (11%) |  | tgt_sh 10.6%; team att 29.9; opp DvP 1.04; RZ tgt 2 |

**First TD scorer ranking (model probability)**: Ashton Jeanty (LV) 13.5%; Romeo Doubs (NE) 10.6%; TreVeyon Henderson (NE) 10.5%; Rhamondre Stevenson (NE) 9.9%; Brock Bowers (LV) 9.5%

MODEL-ONLY track anytime top 3 for comparison: Ashton Jeanty 45.8%; Romeo Doubs 40.2%; Rhamondre Stevenson 40.1%


---
## MIN @ NO  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | MIN pts mean / median | NO pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | MIN 56% | MIN 21.9 / 20 | NO 19.5 / 20 | 41.3 / 40 | +3.0 |
| model | MIN 53% | MIN 22.2 / 22 | NO 21.0 / 20 | 43.2 / 43 | +1.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Kyler Murray (MIN) | QB | 100% | 17.7 | 184 [138-221] (185) | 1.10 |  |  |  | 16.0% / 16.5% | 78 |
| Aaron Jones (MIN) | RB | 100% |  |  |  | 90 [64-111] (90) | 3.1 [2-4] | 23 [9-32] (23) | 51.2% / 51.6% | 84 |
| Demond Claiborne (MIN) | RB | 100% |  |  |  | 9 [0-13] (9) | 0.4 [0-1] | 3 [0-3] (3) | 6.2% / 6.2% | 25 |
| Justin Jefferson (MIN) | WR | 67% |  |  |  | 0 [0-0] (0) | 5.0 [3-7] | 63 [34-86] (64) | 28.0% / 29.5% | 42 |
| Jordan Addison (MIN) | WR | 67% |  |  |  | 1 [0-0] (1) | 3.4 [2-5] | 46 [21-65] (46) | 19.6% / 20.9% | 44 |
| Jauan Jennings (MIN) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.1 [1-3] | 25 [6-36] (25) | 9.3% / 9.9% | 30 |
| T.J. Hockenson (MIN) | TE | 100% |  |  |  | 0 [0-0] (0) | 5.1 [3-7] | 48 [25-65] (48) | 31.1% / 31.5% | 75 |
| Tyler Shough (NO) | QB | 98% | 21.4 | 247 [189-293] (246) | 1.30 |  |  |  | 14.7% / 16.7% | 86 |
| Alvin Kamara (NO) | RB | 65% |  |  |  | 38 [21-50] (38) | 3.3 [2-4] | 24 [10-33] (24) | 33.1% / 36.8% | 47 |
| Kendre Miller (NO) | RB | 100% |  |  |  | 34 [16-46] (34) | 1.1 [0-2] | 8 [0-13] (8) | 26.3% / 28.8% | 54 |
| Chris Olave (NO) | WR | 95% |  |  |  | 0 [0-0] (0) | 6.6 [5-8] | 93 [55-121] (93) | 31.0% / 34.0% | 74 |
| Devaughn Vele (NO) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.4 [2-5] | 42 [18-58] (42) | 22.6% / 24.9% | 71 |
| Bryce Lance (NO) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.3 [0-2] | 17 [0-25] (16) | 7.3% / 7.9% | 35 |
| Juwan Johnson (NO) | TE | 100% |  |  |  | 0 [0-0] (0) | 5.2 [3-7] | 58 [31-77] (58) | 28.9% / 31.1% | 76 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Aaron Jones (MIN) | 51.2% | 0.51 | 0.19 | 4.4 (11%) | 19.4 (47%) | tgt_sh 11.3%; team att 29.0; opp DvP 0.89; RZ tgt 2; car_sh 46.6%; team rush 29.2; opp d_ypc 1.12; inside-10 car 1 |
| 2 | Alvin Kamara (NO) | 33.1% | 0.25 | 0.14 | 4.7 (11%) | 9.8 (26%) | tgt_sh 10.7%; team att 37.5; opp DvP 1.20; RZ tgt 1; car_sh 26.2%; team rush 22.8; opp d_ypc 1.00; inside-10 car 2 |
| 3 | T.J. Hockenson (MIN) | 31.1% | 0.00 | 0.37 | 7.3 (19%) |  | tgt_sh 19.3%; team att 29.0; opp DvP 0.85; RZ tgt 5 |
| 4 | Chris Olave (NO) | 31.0% | 0.00 | 0.37 | 11.3 (26%) |  | tgt_sh 25.9%; team att 37.5; opp DvP 0.96; RZ tgt 5 |
| 5 | Juwan Johnson (NO) | 28.9% | 0.00 | 0.34 | 8.1 (17%) |  | tgt_sh 16.8%; team att 37.5; opp DvP 1.13; RZ tgt 7 |
| 6 | Justin Jefferson (MIN) | 28.0% | 0.00 | 0.33 | 8.1 (24%) |  | tgt_sh 24.0%; team att 29.0; opp DvP 0.98; RZ tgt 3 |

**First TD scorer ranking (model probability)**: Aaron Jones (MIN) 16.4%; Alvin Kamara (NO) 9.2%; Chris Olave (NO) 8.5%; T.J. Hockenson (MIN) 8.4%; Juwan Johnson (NO) 7.9%

MODEL-ONLY track anytime top 3 for comparison: Aaron Jones 51.6%; Alvin Kamara 36.8%; Chris Olave 34.0%


---
## CLE @ NYJ  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | CLE pts mean / median | NYJ pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | NYJ 58% | CLE 18.3 / 17 | NYJ 21.0 / 20 | 39.4 / 39 | -3.0 |
| model | NYJ 53% | CLE 20.2 / 20 | NYJ 21.2 / 20 | 41.5 / 41 | -1.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Deshaun Watson (CLE) | QB | 100% | 19.9 | 206 [157-246] (205) | 1.06 |  |  |  | 11.4% / 13.2% | 87 |
| Quinshon Judkins (CLE) | RB | 100% |  |  |  | 54 [33-69] (54) | 2.4 [1-3] | 16 [5-24] (16) | 39.2% / 43.5% | 80 |
| Raheim Sanders (CLE) | RB | 100% |  |  |  | 12 [3-17] (12) | 2.0 [1-3] | 14 [4-21] (14) | 10.9% / 12.7% | 44 |
| KC Concepcion (CLE) | WR | 100% |  |  |  | 3 [0-3] (3) | 4.6 [3-6] | 49 [26-66] (48) | 23.6% / 26.8% | 75 |
| Denzel Boston (CLE) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.2 [2-4] | 47 [20-66] (47) | 18.4% / 20.8% | 66 |
| Jerry Jeudy (CLE) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.3 [1-3] | 27 [9-39] (27) | 9.4% / 10.6% | 39 |
| Harold Fannin Jr. (CLE) | TE | 100% |  |  |  | 0 [0-0] (0) | 4.6 [3-6] | 43 [22-58] (43) | 21.0% / 24.1% | 72 |
| Geno Smith (NYJ) | QB | 100% | 19.6 | 217 [165-260] (219) | 1.41 |  |  |  | 10.5% / 10.4% | 87 |
| Braelon Allen (NYJ) | RB | 100% |  |  |  | 79 [54-98] (78) | 1.6 [1-2] | 12 [0-19] (13) | 49.9% / 50.0% | 74 |
| Isaiah Davis (NYJ) | RB | 100% |  |  |  | 4 [0-5] (4) | 0.6 [0-1] | 5 [0-7] (5) | 4.3% / 4.6% | 23 |
| Garrett Wilson (NYJ) | WR | 100% |  |  |  | 0 [0-0] (0) | 6.5 [5-8] | 80 [48-105] (81) | 33.4% / 34.4% | 79 |
| Isaiah Williams (NYJ) | WR | 100% |  |  |  | 2 [0-0] (2) | 2.6 [1-4] | 31 [11-44] (31) | 17.7% / 17.8% | 47 |
| Sterling Shepard (NYJ) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.4 [0-2] | 18 [0-27] (18) | 11.7% / 12.2% | 17 |
| Kenyon Sadiq (NYJ) | TE | 100% |  |  |  | 2 [0-0] (2) | 4.1 [3-5] | 45 [22-62] (45) | 24.0% / 23.9% | 63 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Braelon Allen (NYJ) | 49.9% | 0.44 | 0.23 | 2.1 (5%) | 18.7 (31%) | tgt_sh 4.6%; team att 31.3; opp DvP 1.10; RZ tgt 3; car_sh 31.1%; team rush 26.9; opp d_ypc 1.05; inside-10 car 1 |
| 2 | Quinshon Judkins (CLE) | 39.2% | 0.34 | 0.15 | 3.1 (10%) | 14.5 (51%) | tgt_sh 9.9%; team att 31.5; opp DvP 0.91; RZ tgt 3; car_sh 51.3%; team rush 26.6; opp d_ypc 1.01; inside-10 car 4 |
| 3 | Garrett Wilson (NYJ) | 33.4% | 0.00 | 0.40 | 10.1 (24%) |  | tgt_sh 23.6%; team att 31.3; opp DvP 0.95; RZ tgt 1 |
| 4 | Kenyon Sadiq (NYJ) | 24.0% | 0.05 | 0.22 | 6.0 (14%) |  | tgt_sh 14.4%; team att 31.3; opp DvP 0.90; RZ tgt 0 |
| 5 | KC Concepcion (CLE) | 23.6% | 0.01 | 0.25 | 7.1 (21%) | 0.6 (2%) | tgt_sh 20.8%; team att 31.5; opp DvP 1.05; RZ tgt 3 |
| 6 | Harold Fannin Jr. (CLE) | 21.0% | 0.00 | 0.24 | 6.5 (19%) |  | tgt_sh 18.9%; team att 31.5; opp DvP 1.08; RZ tgt 3 |

**First TD scorer ranking (model probability)**: Braelon Allen (NYJ) 16.3%; Quinshon Judkins (CLE) 11.7%; Garrett Wilson (NYJ) 9.6%; Kenyon Sadiq (NYJ) 6.6%; KC Concepcion (CLE) 6.3%

MODEL-ONLY track anytime top 3 for comparison: Braelon Allen 50.0%; Quinshon Judkins 43.5%; Garrett Wilson 34.4%


---
## IND @ PIT  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | IND pts mean / median | PIT pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | PIT 58% | IND 20.5 / 20 | PIT 23.0 / 23 | 43.5 / 43 | -3.0 |
| model | PIT 50% | IND 23.9 / 23 | PIT 23.7 / 24 | 47.7 / 47 | -0.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Daniel Jones (IND) | QB | 100% | 19.9 | 195 [150-233] (193) | 0.87 |  |  |  | 9.3% / 11.3% | 87 |
| Jonathan Taylor (IND) | RB | 95% |  |  |  | 85 [60-104] (85) | 3.5 [2-5] | 25 [11-36] (25) | 55.4% / 64.9% | 80 |
| Seth McGowan (IND) | RB | 100% |  |  |  | 23 [9-31] (23) | 0.7 [0-1] | 5 [0-8] (5) | 18.3% / 23.1% | 43 |
| Josh Downs (IND) | WR | 100% |  |  |  | 0 [0-0] (0) | 4.9 [3-6] | 54 [29-73] (54) | 22.0% / 26.9% | 75 |
| Keenan Allen (IND) | WR | 75% |  |  |  | 0 [0-0] (0) | 4.2 [3-6] | 43 [22-58] (42) | 18.0% / 22.7% | 50 |
| Laquon Treadwell (IND) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.2 [0-2] | 14 [0-23] (14) | 7.8% / 9.7% | 31 |
| Tyler Warren (IND) | TE | 100% |  |  |  | 2 [0-0] (2) | 6.0 [4-8] | 55 [31-74] (55) | 22.5% / 27.5% | 77 |
| Aaron Rodgers (PIT) | QB | 100% | 20.6 | 254 [192-304] (257) | 1.68 |  |  |  | 3.0% / 3.1% | 87 |
| Jaylen Warren (PIT) | RB | 100% |  |  |  | 70 [45-90] (69) | 3.9 [2-5] | 35 [16-48] (35) | 49.6% / 50.5% | 81 |
| Rico Dowdle (PIT) | RB | 65% |  |  |  | 29 [14-38] (29) | 2.3 [1-3] | 20 [6-29] (20) | 26.7% / 27.5% | 33 |
| DK Metcalf (PIT) | WR | 100% |  |  |  | 0 [0-0] (0) | 5.3 [4-7] | 80 [44-108] (82) | 30.8% / 31.6% | 76 |
| Roman Wilson (PIT) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.9 [2-4] | 42 [16-60] (43) | 21.9% / 22.7% | 68 |
| Germie Bernard (PIT) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.2 [0-2] | 17 [0-26] (17) | 13.0% / 13.9% | 31 |
| Pat Freiermuth (PIT) | TE | 100% |  |  |  | 1 [0-0] (1) | 3.6 [2-5] | 42 [19-59] (43) | 25.9% / 27.3% | 62 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Jonathan Taylor (IND) | 55.4% | 0.67 | 0.11 | 4.5 (11%) | 18.9 (68%) | tgt_sh 10.6%; team att 32.0; opp DvP 1.05; RZ tgt 1; car_sh 68.2%; team rush 26.7; opp d_ypc 1.02; inside-10 car 8 |
| 2 | Jaylen Warren (PIT) | 49.6% | 0.34 | 0.32 | 5.5 (12%) | 13.0 (48%) | tgt_sh 11.9%; team att 36.8; opp DvP 1.04; RZ tgt 4; car_sh 47.8%; team rush 23.1; opp d_ypc 1.08; inside-10 car 0 |
| 3 | DK Metcalf (PIT) | 30.8% | 0.00 | 0.36 | 9.8 (22%) |  | tgt_sh 22.2%; team att 36.8; opp DvP 0.95; RZ tgt 1 |
| 4 | Rico Dowdle (PIT) | 26.7% | 0.18 | 0.12 | 3.4 (8%) | 6.9 (29%) | tgt_sh 8.2%; team att 36.8; opp DvP 1.04; RZ tgt 0; car_sh 29.2%; team rush 23.1; opp d_ypc 1.08; inside-10 car 0 |
| 5 | Pat Freiermuth (PIT) | 25.9% | 0.01 | 0.29 | 5.7 (13%) |  | tgt_sh 13.2%; team att 36.8; opp DvP 0.90; RZ tgt 3 |
| 6 | Tyler Warren (IND) | 22.5% | 0.01 | 0.24 | 8.8 (21%) |  | tgt_sh 20.5%; team att 32.0; opp DvP 1.02; RZ tgt 3 |

**First TD scorer ranking (model probability)**: Jonathan Taylor (IND) 17.1%; Jaylen Warren (PIT) 14.6%; DK Metcalf (PIT) 7.9%; Rico Dowdle (PIT) 6.8%; Pat Freiermuth (PIT) 6.5%

MODEL-ONLY track anytime top 3 for comparison: Jonathan Taylor 64.9%; Jaylen Warren 50.5%; DK Metcalf 31.6%


---
## HOU @ TEN  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | HOU pts mean / median | TEN pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | HOU 70% | HOU 22.2 / 21 | TEN 15.3 / 14 | 37.4 / 37 | +7.0 |
| model | HOU 60% | HOU 21.8 / 21 | TEN 18.4 / 17 | 40.2 / 40 | +3.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| C.J. Stroud (HOU) | QB | 100% | 21.7 | 255 [196-303] (257) | 1.25 |  |  |  | 7.8% / 7.3% | 87 |
| David Montgomery (HOU) | RB | 100% |  |  |  | 44 [25-56] (43) | 1.0 [0-2] | 8 [0-12] (8) | 45.7% / 44.7% | 79 |
| Woody Marks (HOU) | RB | 100% |  |  |  | 31 [16-41] (30) | 1.3 [0-2] | 9 [0-15] (10) | 35.6% / 35.2% | 66 |
| Nico Collins (HOU) | WR | 96% |  |  |  | 1 [0-0] (1) | 5.4 [4-7] | 74 [42-99] (76) | 27.8% / 28.0% | 58 |
| Xavier Hutchinson (HOU) | WR | 100% |  |  |  | 2 [0-0] (2) | 3.2 [2-4] | 40 [17-57] (40) | 17.0% / 16.4% | 71 |
| Kayshon Boutte (HOU) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.4 [1-3] | 32 [11-46] (33) | 15.0% / 14.2% | 48 |
| Dalton Schultz (HOU) | TE | 100% |  |  |  | 0 [0-0] (0) | 4.3 [3-6] | 42 [21-58] (42) | 19.2% / 19.0% | 74 |
| Cam Ward (TEN) | QB | 100% | 20.4 | 218 [167-260] (216) | 0.81 |  |  |  | 8.8% / 11.8% | 87 |
| Tony Pollard (TEN) | RB | 95% |  |  |  | 56 [36-72] (57) | 2.2 [1-3] | 15 [4-22] (15) | 36.7% / 45.5% | 77 |
| Tyjae Spears (TEN) | RB | 100% |  |  |  | 22 [9-29] (22) | 2.1 [1-3] | 15 [4-22] (15) | 14.3% / 17.9% | 52 |
| Carnell Tate (TEN) | WR | 67% |  |  |  | 0 [0-0] (0) | 4.6 [3-6] | 58 [31-79] (58) | 15.0% / 20.4% | 50 |
| Wan'Dale Robinson (TEN) | WR | 100% |  |  |  | 1 [0-0] (1) | 4.5 [3-6] | 49 [25-66] (48) | 19.1% / 23.9% | 71 |
| Elic Ayomanor (TEN) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.6 [1-4] | 37 [13-53] (37) | 16.3% / 20.2% | 43 |
| Gunnar Helm (TEN) | TE | 95% |  |  |  | 0 [0-0] (0) | 3.0 [2-4] | 28 [11-40] (28) | 11.8% / 15.3% | 46 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | David Montgomery (HOU) | 45.7% | 0.54 | 0.06 | 1.4 (4%) | 12.4 (48%) | tgt_sh 4.1%; team att 35.2; opp DvP 0.92; RZ tgt 1; car_sh 48.5%; team rush 24.4; opp d_ypc 0.93; inside-10 car 5 |
| 2 | Tony Pollard (TEN) | 36.7% | 0.39 | 0.05 | 2.8 (8%) | 14.2 (57%) | tgt_sh 7.6%; team att 33.4; opp DvP 0.99; RZ tgt 0; car_sh 56.6%; team rush 24.6; opp d_ypc 0.90; inside-10 car 13 |
| 3 | Woody Marks (HOU) | 35.6% | 0.34 | 0.09 | 1.7 (5%) | 8.3 (32%) | tgt_sh 5.2%; team att 35.2; opp DvP 0.92; RZ tgt 2; car_sh 32.3%; team rush 24.4; opp d_ypc 0.93; inside-10 car 3 |
| 4 | Nico Collins (HOU) | 27.8% | 0.01 | 0.31 | 8.4 (23%) |  | tgt_sh 23.2%; team att 35.2; opp DvP 1.14; RZ tgt 3 |
| 5 | Dalton Schultz (HOU) | 19.2% | 0.00 | 0.21 | 6.0 (18%) |  | tgt_sh 17.7%; team att 35.2; opp DvP 0.95; RZ tgt 2 |
| 6 | Wan'Dale Robinson (TEN) | 19.1% | 0.00 | 0.21 | 7.1 (19%) |  | tgt_sh 18.8%; team att 33.4; opp DvP 1.02; RZ tgt 4 |

**First TD scorer ranking (model probability)**: David Montgomery (HOU) 14.8%; Tony Pollard (TEN) 10.9%; Woody Marks (HOU) 10.7%; Nico Collins (HOU) 8.0%; Dalton Schultz (HOU) 5.2%

MODEL-ONLY track anytime top 3 for comparison: Tony Pollard 45.5%; David Montgomery 44.7%; Woody Marks 35.2%


---
## NYG @ WAS  (2026-10-11 13:00 ET)

| Track | Winner (win prob) | NYG pts mean / median | WAS pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | WAS 61% | NYG 18.9 / 19 | WAS 22.5 / 22 | 41.5 / 40 | -4.0 |
| model | WAS 52% | NYG 22.4 / 23 | WAS 23.1 / 23 | 45.5 / 44 | -0.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Jameis Winston (NYG) | QB | 100% | 18.0 | 206 [155-246] (203) | 1.23 |  |  |  | 1.6% / 2.3% | 81 |
| Cam Skattebo (NYG) | RB | 95% |  |  |  | 47 [28-60] (47) | 2.1 [1-3] | 18 [5-26] (17) | 26.9% / 33.8% | 75 |
| Najee Harris (NYG) | RB | 95% |  |  |  | 26 [12-35] (26) | 0.1 [0-0] | 1 [0-0] (1) | 10.2% / 12.9% | 46 |
| Malik Nabers (NYG) | WR | 95% |  |  |  | 0 [0-0] (0) | 3.8 [2-5] | 49 [23-68] (49) | 24.1% / 30.2% | 69 |
| Malachi Fields (NYG) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.5 [1-4] | 35 [13-51] (35) | 14.9% / 18.3% | 52 |
| Darnell Mooney (NYG) | WR | 100% |  |  |  | 1 [0-0] (1) | 2.1 [1-3] | 30 [9-44] (30) | 11.3% / 14.3% | 40 |
| Isaiah Likely (NYG) | TE | 95% |  |  |  | 0 [0-0] (0) | 4.9 [3-6] | 53 [28-71] (52) | 33.3% / 40.0% | 72 |
| Jayden Daniels (WAS) | QB | 98% | 18.5 | 183 [137-220] (186) | 1.72 |  |  |  | 9.0% / 9.4% | 64 |
| Jacory Croskey-Merritt (WAS) | RB | 95% |  |  |  | 40 [22-51] (39) | 1.0 [0-2] | 7 [0-10] (7) | 26.5% / 27.1% | 74 |
| Rachaad White (WAS) | RB | 100% |  |  |  | 27 [12-36] (26) | 1.9 [1-3] | 12 [3-18] (12) | 28.6% / 29.0% | 59 |
| Terry McLaurin (WAS) | WR | 67% |  |  |  | 0 [0-0] (0) | 4.1 [3-5] | 51 [26-70] (52) | 34.5% / 35.2% | 46 |
| Antonio Williams (WAS) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.3 [2-4] | 35 [15-50] (35) | 29.0% / 29.7% | 61 |
| Dyami Brown (WAS) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.0 [1-3] | 22 [5-32] (22) | 17.9% / 18.3% | 43 |
| Chig Okonkwo (WAS) | TE | 95% |  |  |  | 0 [0-0] (0) | 3.5 [2-5] | 31 [13-43] (31) | 20.8% / 21.1% | 39 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Terry McLaurin (WAS) | 34.5% | 0.00 | 0.41 | 7.2 (18%) |  | tgt_sh 17.6%; team att 32.6; opp DvP 1.09; RZ tgt 2 |
| 2 | Isaiah Likely (NYG) | 33.3% | 0.00 | 0.39 | 7.5 (23%) |  | tgt_sh 23.1%; team att 30.1; opp DvP 1.03; RZ tgt 6 |
| 3 | Antonio Williams (WAS) | 29.0% | 0.00 | 0.34 | 5.6 (12%) |  | tgt_sh 11.6%; team att 32.6; opp DvP 1.09; RZ tgt 2 |
| 4 | Rachaad White (WAS) | 28.6% | 0.13 | 0.20 | 2.7 (6%) | 5.8 (18%) | tgt_sh 6.1%; team att 32.6; opp DvP 0.91; RZ tgt 2; car_sh 18.2%; team rush 28.1; opp d_ypc 1.06; inside-10 car 2 |
| 5 | Cam Skattebo (NYG) | 26.9% | 0.21 | 0.09 | 3.0 (9%) | 12.3 (42%) | tgt_sh 9.3%; team att 30.1; opp DvP 0.99; RZ tgt 0; car_sh 41.6%; team rush 28.5; opp d_ypc 0.98; inside-10 car 5 |
| 6 | Jacory Croskey-Merritt (WAS) | 26.5% | 0.20 | 0.10 | 1.4 (3%) | 10.4 (34%) | tgt_sh 3.2%; team att 32.6; opp DvP 0.91; RZ tgt 1; car_sh 33.8%; team rush 28.1; opp d_ypc 1.06; inside-10 car 2 |

**First TD scorer ranking (model probability)**: Terry McLaurin (WAS) 9.6%; Isaiah Likely (NYG) 8.9%; Antonio Williams (WAS) 7.8%; Rachaad White (WAS) 7.7%; Cam Skattebo (NYG) 7.0%

MODEL-ONLY track anytime top 3 for comparison: Isaiah Likely 40.0%; Terry McLaurin 35.2%; Cam Skattebo 33.8%


---
## DEN @ LAC  (2026-10-11 16:05 ET)

| Track | Winner (win prob) | DEN pts mean / median | LAC pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | DEN 60% | DEN 22.5 / 22 | LAC 19.0 / 18 | 41.5 / 41 | +3.0 |
| model | DEN 53% | DEN 21.0 / 20 | LAC 20.2 / 20 | 41.2 / 40 | +1.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Bo Nix (DEN) | QB | 100% | 19.9 | 228 [172-274] (230) | 1.46 |  |  |  | 15.0% / 13.9% | 87 |
| J.K. Dobbins (DEN) | RB | 100% |  |  |  | 54 [33-68] (53) | 0.8 [0-1] | 6 [0-9] (6) | 43.9% / 41.6% | 76 |
| RJ Harvey (DEN) | RB | 100% |  |  |  | 26 [12-34] (25) | 4.0 [2-5] | 32 [15-45] (33) | 34.9% / 31.7% | 69 |
| Jaylen Waddle (DEN) | WR | 100% |  |  |  | 1 [0-0] (1) | 3.8 [2-5] | 52 [24-71] (52) | 23.0% / 21.6% | 73 |
| Courtland Sutton (DEN) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.2 [2-4] | 43 [18-61] (44) | 27.9% / 24.8% | 65 |
| Troy Franklin (DEN) | WR | 100% |  |  |  | 1 [0-0] (1) | 1.7 [1-3] | 23 [3-35] (24) | 11.9% / 11.2% | 26 |
| Evan Engram (DEN) | TE | 100% |  |  |  | 0 [0-0] (0) | 2.7 [1-4] | 29 [11-41] (29) | 15.0% / 14.0% | 49 |
| Justin Herbert (LAC) | QB | 100% | 18.2 | 198 [149-238] (195) | 1.10 |  |  |  | 13.6% / 14.9% | 87 |
| Omarion Hampton (LAC) | RB | 100% |  |  |  | 65 [43-82] (65) | 2.3 [1-3] | 17 [5-25] (17) | 39.6% / 42.2% | 82 |
| Keaton Mitchell (LAC) | RB | 100% |  |  |  | 29 [14-39] (30) | 2.2 [1-3] | 16 [4-24] (16) | 23.1% / 24.9% | 66 |
| Tre Harris (LAC) | WR | 100% |  |  |  | 0 [0-0] (0) | 4.2 [3-6] | 58 [28-79] (57) | 25.5% / 27.3% | 67 |
| Marquez Valdes-Scantling (LAC) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.1 [0-2] | 15 [0-22] (15) | 4.9% / 5.5% | 17 |
| Derius Davis (LAC) | WR | 100% |  |  |  | 0 [0-0] (0) | 0.5 [0-1] | 6 [0-8] (6) | 2.2% / 2.1% | 27 |
| Oronde Gadsden II (LAC) | TE | 100% |  |  |  | 1 [0-0] (1) | 3.9 [2-5] | 44 [20-61] (43) | 23.7% / 25.2% | 56 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | J.K. Dobbins (DEN) | 43.9% | 0.53 | 0.03 | 1.1 (3%) | 13.5 (44%) | car_sh 44.1%; team rush 25.1; opp d_ypc 0.94; inside-10 car 5 |
| 2 | Omarion Hampton (LAC) | 39.6% | 0.41 | 0.08 | 3.2 (6%) | 14.7 (50%) | tgt_sh 5.6%; team att 31.7; opp DvP 1.03; RZ tgt 0; car_sh 49.7%; team rush 28.1; opp d_ypc 1.08; inside-10 car 7 |
| 3 | RJ Harvey (DEN) | 34.9% | 0.18 | 0.24 | 5.5 (14%) | 6.1 (20%) | tgt_sh 13.7%; team att 34.2; opp DvP 1.09; RZ tgt 2; car_sh 20.1%; team rush 25.1; opp d_ypc 0.94; inside-10 car 0 |
| 4 | Courtland Sutton (DEN) | 27.9% | 0.00 | 0.32 | 5.7 (15%) |  | tgt_sh 15.2%; team att 34.2; opp DvP 0.96; RZ tgt 5 |
| 5 | Tre Harris (LAC) | 25.5% | 0.00 | 0.29 | 7.3 (13%) |  | tgt_sh 12.9%; team att 31.7; opp DvP 1.01; RZ tgt 3 |
| 6 | Oronde Gadsden II (LAC) | 23.7% | 0.00 | 0.26 | 6.3 (12%) |  | tgt_sh 11.7%; team att 31.7; opp DvP 0.91; RZ tgt 3 |

**First TD scorer ranking (model probability)**: J.K. Dobbins (DEN) 12.3%; Omarion Hampton (LAC) 10.5%; RJ Harvey (DEN) 9.2%; Courtland Sutton (DEN) 7.0%; Tre Harris (LAC) 6.3%

MODEL-ONLY track anytime top 3 for comparison: Omarion Hampton 42.2%; J.K. Dobbins 41.6%; RJ Harvey 31.7%


---
## DET @ ARI  (2026-10-11 16:25 ET)

| Track | Winner (win prob) | DET pts mean / median | ARI pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | DET 64% | DET 30.1 / 30 | ARI 24.6 / 24 | 54.7 / 54 | +6.0 |
| model | DET 56% | DET 27.6 / 27 | ARI 25.4 / 24 | 52.9 / 53 | +3.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Jared Goff (DET) | QB | 100% | 21.6 | 272 [205-326] (276) | 2.19 |  |  |  | 4.9% / 4.4% | 87 |
| Jahmyr Gibbs (DET) | RB | 100% |  |  |  | 86 [61-107] (85) | 4.0 [2-5] | 35 [17-48] (36) | 75.6% / 71.7% | 84 |
| Sione Vaki (DET) | RB | 100% |  |  |  | 14 [4-19] (13) | 0.7 [0-1] | 6 [0-10] (6) | 15.0% / 13.2% | 40 |
| Amon-Ra St. Brown (DET) | WR | 100% |  |  |  | 0 [0-0] (0) | 6.2 [4-8] | 78 [45-102] (79) | 51.9% / 47.6% | 78 |
| Jameson Williams (DET) | WR | 100% |  |  |  | 0 [0-0] (0) | 3.4 [2-5] | 57 [25-79] (57) | 25.1% / 22.8% | 72 |
| Isaac TeSlaa (DET) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.5 [1-2] | 26 [1-39] (26) | 16.7% / 15.0% | 43 |
| Sam LaPorta (DET) | TE | 100% |  |  |  | 0 [0-0] (0) | 5.3 [4-7] | 64 [35-86] (65) | 43.6% / 39.9% | 76 |
| Jacoby Brissett (ARI) | QB | 100% | 23.9 | 232 [178-276] (229) | 1.62 |  |  |  | 13.5% / 14.0% | 87 |
| Jeremiyah Love (ARI) | RB | 95% |  |  |  | 60 [39-77] (61) | 2.4 [1-3] | 16 [5-24] (16) | 46.1% / 48.0% | 77 |
| Tyler Allgeier (ARI) | RB | 100% |  |  |  | 32 [15-42] (32) | 1.4 [0-2] | 9 [0-14] (9) | 30.5% / 32.0% | 69 |
| Michael Wilson (ARI) | WR | 100% |  |  |  | 0 [0-0] (0) | 5.4 [4-7] | 58 [32-78] (58) | 35.8% / 37.1% | 77 |
| Marvin Harrison Jr. (ARI) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.8 [1-4] | 37 [14-52] (37) | 17.1% / 17.4% | 49 |
| Kendrick Bourne (ARI) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.7 [1-4] | 31 [11-44] (30) | 15.1% / 15.5% | 51 |
| Trey McBride (ARI) | TE | 100% |  |  |  | 0 [0-0] (0) | 8.4 [6-10] | 74 [47-95] (72) | 42.7% / 43.8% | 80 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Jahmyr Gibbs (DET) | 75.6% | 0.96 | 0.36 | 5.3 (16%) | 19.6 (78%) | tgt_sh 16.2%; team att 35.1; opp DvP 1.01; RZ tgt 6; car_sh 77.5%; team rush 24.5; opp d_ypc 1.00; inside-10 car 10 |
| 2 | Amon-Ra St. Brown (DET) | 51.9% | 0.00 | 0.70 | 9.8 (28%) |  | tgt_sh 28.4%; team att 35.1; opp DvP 1.14; RZ tgt 12 |
| 3 | Jeremiyah Love (ARI) | 46.1% | 0.45 | 0.15 | 3.1 (9%) | 13.5 (51%) | tgt_sh 8.8%; team att 37.2; opp DvP 0.90; RZ tgt 3; car_sh 50.9%; team rush 25.6; opp d_ypc 1.03; inside-10 car 4 |
| 4 | Sam LaPorta (DET) | 43.6% | 0.00 | 0.56 | 7.6 (20%) |  | tgt_sh 19.8%; team att 35.1; opp DvP 1.39; RZ tgt 9 |
| 5 | Trey McBride (ARI) | 42.7% | 0.00 | 0.55 | 11.6 (29%) |  | tgt_sh 29.2%; team att 37.2; opp DvP 1.13; RZ tgt 9 |
| 6 | Michael Wilson (ARI) | 35.8% | 0.00 | 0.44 | 8.5 (22%) |  | tgt_sh 22.0%; team att 37.2; opp DvP 1.07; RZ tgt 9 |

**First TD scorer ranking (model probability)**: Jahmyr Gibbs (DET) 21.3%; Amon-Ra St. Brown (DET) 11.2%; Jeremiyah Love (ARI) 9.4%; Sam LaPorta (DET) 8.9%; Trey McBride (ARI) 8.5%

MODEL-ONLY track anytime top 3 for comparison: Jahmyr Gibbs 71.7%; Jeremiyah Love 48.0%; Amon-Ra St. Brown 47.6%


---
## SF @ SEA  (2026-10-11 16:25 ET)

| Track | Winner (win prob) | SF pts mean / median | SEA pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | SEA 58% | SF 21.2 / 20 | SEA 24.2 / 24 | 45.4 / 44 | -3.0 |
| model | SEA 55% | SF 23.2 / 23 | SEA 25.1 / 24 | 48.3 / 48 | -2.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Brock Purdy (SF) | QB | 100% | 19.1 | 207 [155-248] (206) | 1.56 |  |  |  | 8.8% / 9.6% | 86 |
| Christian McCaffrey (SF) | RB | 95% |  |  |  | 61 [39-78] (61) | 4.8 [3-6] | 38 [20-51] (38) | 52.6% / 56.1% | 77 |
| Kaelon Black (SF) | RB | 95% |  |  |  | 33 [16-43] (33) | 0.4 [0-1] | 3 [0-2] (3) | 15.1% / 17.6% | 56 |
| Mike Evans (SF) | WR | 96% |  |  |  | 0 [0-0] (0) | 4.3 [3-6] | 54 [27-73] (53) | 32.3% / 35.0% | 70 |
| Deebo Samuel Sr. (SF) | WR | 100% |  |  |  | 4 [0-5] (4) | 3.5 [2-5] | 43 [19-60] (43) | 31.2% / 33.3% | 59 |
| Brandin Cooks (SF) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.0 [0-2] | 12 [0-19] (12) | 5.9% / 6.4% | 14 |
| George Kittle (SF) | TE | 100% |  |  |  | 0 [0-0] (0) | 4.7 [3-6] | 51 [26-69] (51) | 32.4% / 36.0% | 70 |
| Sam Darnold (SEA) | QB | 100% | 19.3 | 224 [168-269] (225) | 1.80 |  |  |  | 6.1% / 6.2% | 77 |
| Emanuel Wilson (SEA) | RB | 100% |  |  |  | 75 [49-95] (74) | 1.2 [0-2] | 9 [0-14] (9) | 47.7% / 49.0% | 82 |
| George Holani (SEA) | RB | 65% |  |  |  | 31 [15-41] (31) | 1.2 [0-2] | 9 [0-13] (9) | 26.7% / 27.5% | 39 |
| Jaxon Smith-Njigba (SEA) | WR | 95% |  |  |  | 0 [0-0] (0) | 7.1 [5-9] | 99 [61-129] (99) | 52.1% / 54.6% | 75 |
| Rashid Shaheed (SEA) | WR | 100% |  |  |  | 3 [0-2] (3) | 3.0 [2-4] | 34 [14-48] (34) | 19.8% / 20.4% | 54 |
| Cooper Kupp (SEA) | WR | 100% |  |  |  | 0 [0-0] (0) | 2.6 [1-4] | 32 [11-46] (32) | 18.0% / 18.7% | 46 |
| AJ Barner (SEA) | TE | 100% |  |  |  | 1 [0-0] (1) | 3.3 [2-5] | 33 [14-46] (33) | 31.8% / 32.7% | 55 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey (SF) | 52.6% | 0.37 | 0.34 | 6.6 (17%) | 13.2 (43%) | tgt_sh 17.1%; team att 30.8; opp DvP 1.05; RZ tgt 3; car_sh 43.4%; team rush 28.9; opp d_ypc 0.93; inside-10 car 9 |
| 2 | Jaxon Smith-Njigba (SEA) | 52.1% | 0.00 | 0.71 | 10.6 (31%) |  | tgt_sh 31.2%; team att 31.4; opp DvP 0.88; RZ tgt 10 |
| 3 | Emanuel Wilson (SEA) | 47.7% | 0.54 | 0.10 | 1.6 (4%) | 18.5 (39%) | tgt_sh 4.3%; team att 31.4; opp DvP 0.98; RZ tgt 1; car_sh 38.5%; team rush 29.1; opp d_ypc 0.94; inside-10 car 9 |
| 4 | George Kittle (SF) | 32.4% | 0.00 | 0.38 | 6.7 (19%) |  | tgt_sh 18.9%; team att 30.8; opp DvP 0.88; RZ tgt 5 |
| 5 | Mike Evans (SF) | 32.3% | 0.00 | 0.38 | 7.1 (20%) |  | tgt_sh 19.6%; team att 30.8; opp DvP 0.94; RZ tgt 4 |
| 6 | AJ Barner (SEA) | 31.8% | 0.03 | 0.35 | 4.8 (13%) |  | tgt_sh 13.4%; team att 31.4; opp DvP 0.92; RZ tgt 5 |

**First TD scorer ranking (model probability)**: Christian McCaffrey (SF) 13.5%; Jaxon Smith-Njigba (SEA) 13.4%; Emanuel Wilson (SEA) 12.3%; George Kittle (SF) 7.2%; Mike Evans (SF) 7.1%

MODEL-ONLY track anytime top 3 for comparison: Christian McCaffrey 56.1%; Jaxon Smith-Njigba 54.6%; Emanuel Wilson 49.0%


---
## BAL @ ATL  (2026-10-11 20:20 ET)

| Track | Winner (win prob) | BAL pts mean / median | ATL pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | ATL 59% | BAL 20.3 / 20 | ATL 23.2 / 23 | 43.5 / 43 | -3.0 |
| model | BAL 50% | BAL 24.1 / 24 | ATL 24.0 / 24 | 48.2 / 47 | -0.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Tyler Huntley (BAL) | QB | 100% | 19.3 | 222 [165-266] (218) | 1.16 |  |  |  | 11.4% / 14.4% | 49 |
| Derrick Henry (BAL) | RB | 100% |  |  |  | 79 [55-98] (80) | 1.3 [0-2] | 10 [0-15] (10) | 52.2% / 61.6% | 77 |
| Justice Hill (BAL) | RB | 100% |  |  |  | 12 [3-17] (12) | 1.6 [0-2] | 12 [0-18] (12) | 12.5% / 15.2% | 41 |
| Zay Flowers (BAL) | WR | 67% |  |  |  | 1 [0-0] (1) | 5.4 [4-7] | 84 [47-111] (82) | 31.9% / 37.3% | 45 |
| Rashod Bateman (BAL) | WR | 95% |  |  |  | 0 [0-0] (0) | 2.8 [1-4] | 36 [13-52] (36) | 18.2% / 22.2% | 46 |
| Chris Moore (BAL) | WR | 95% |  |  |  | 0 [0-0] (0) | 1.6 [1-2] | 21 [2-32] (21) | 10.6% / 13.1% | 25 |
| Mark Andrews (BAL) | TE | 95% |  |  |  | 0 [0-0] (0) | 4.8 [3-6] | 45 [23-61] (44) | 25.5% / 31.5% | 64 |
| Michael Penix Jr. (ATL) | QB | 100% | 16.2 | 183 [135-221] (186) | 1.03 |  |  |  | 6.4% / 6.6% | 63 |
| Bijan Robinson (ATL) | RB | 100% |  |  |  | 96 [68-119] (95) | 3.5 [2-5] | 28 [13-39] (28) | 66.0% / 68.0% | 84 |
| Brian Robinson (ATL) | RB | 100% |  |  |  | 38 [20-50] (37) | 0.5 [0-1] | 3 [0-4] (4) | 35.2% / 36.6% | 70 |
| Drake London (ATL) | WR | 100% |  |  |  | 1 [0-0] (1) | 4.6 [3-6] | 68 [36-91] (69) | 23.1% / 24.0% | 76 |
| Jahan Dotson (ATL) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.9 [1-3] | 25 [6-36] (25) | 10.2% / 10.7% | 44 |
| Olamide Zaccheaus (ATL) | WR | 100% |  |  |  | 0 [0-0] (0) | 1.5 [0-2] | 15 [0-23] (16) | 11.3% / 11.7% | 26 |
| Kyle Pitts (ATL) | TE | 100% |  |  |  | 0 [0-0] (0) | 2.7 [1-4] | 27 [10-39] (28) | 13.2% / 13.7% | 43 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Bijan Robinson (ATL) | 66.0% | 0.82 | 0.20 | 4.8 (19%) | 17.8 (52%) | tgt_sh 18.9%; team att 26.7; opp DvP 0.92; RZ tgt 1; car_sh 52.4%; team rush 33.1; opp d_ypc 0.96; inside-10 car 8 |
| 2 | Derrick Henry (BAL) | 52.2% | 0.66 | 0.06 | 1.8 (5%) | 19.6 (61%) | tgt_sh 4.8%; team att 29.2; opp DvP 0.95; RZ tgt 0; car_sh 61.0%; team rush 30.8; opp d_ypc 0.85; inside-10 car 17 |
| 3 | Brian Robinson (ATL) | 35.2% | 0.37 | 0.05 | 0.6 (2%) | 8.5 (25%) | car_sh 25.1%; team rush 33.1; opp d_ypc 0.96; inside-10 car 3 |
| 4 | Zay Flowers (BAL) | 31.9% | 0.01 | 0.37 | 8.2 (24%) |  | tgt_sh 24.4%; team att 29.2; opp DvP 1.07; RZ tgt 4 |
| 5 | Mark Andrews (BAL) | 25.5% | 0.00 | 0.29 | 7.0 (19%) |  | tgt_sh 18.9%; team att 29.2; opp DvP 0.92; RZ tgt 3 |
| 6 | Drake London (ATL) | 23.1% | 0.01 | 0.25 | 7.3 (27%) |  | tgt_sh 26.6%; team att 26.7; opp DvP 1.08; RZ tgt 0 |

**First TD scorer ranking (model probability)**: Bijan Robinson (ATL) 21.3%; Derrick Henry (BAL) 14.7%; Brian Robinson (ATL) 8.9%; Zay Flowers (BAL) 7.7%; Mark Andrews (BAL) 5.9%

MODEL-ONLY track anytime top 3 for comparison: Bijan Robinson 68.0%; Derrick Henry 61.6%; Zay Flowers 37.3%


---
## BUF @ LA  (2026-10-12 20:15 ET)

| Track | Winner (win prob) | BUF pts mean / median | LA pts mean / median | Total mean / median | Fair spread (home) |
|---|---|---|---|---|---|
| market | LA 59% | BUF 25.5 / 24 | LA 28.8 / 28 | 54.4 / 54 | -3.0 |
| model | LA 53% | BUF 25.5 / 24 | LA 26.4 / 27 | 51.9 / 51 | -1.0 |

**Player lines** (mean, P25-P75 from the MARKET-ANCHORED track; MODEL-ONLY mean beside it; Avail = p_active; conf = reliability index; anytime TD = model probability, no market price available)

| Player | Pos | Avail | Pass cmp | Pass yds | Pass TD | Rush yds | Rec | Rec yds | Anytime TD mkt-track / model-track | Conf (yds) |
|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen (BUF) | QB | 100% | 18.0 | 196 [146-236] (195) | 1.43 |  |  |  | 30.3% / 29.6% | 86 |
| James Cook (BUF) | RB | 100% |  |  |  | 85 [60-106] (86) | 1.9 [1-3] | 14 [3-21] (14) | 62.2% / 62.2% | 84 |
| Ty Johnson (BUF) | RB | 100% |  |  |  | 11 [2-15] (11) | 2.0 [1-3] | 17 [4-25] (16) | 20.8% / 21.1% | 32 |
| Khalil Shakir (BUF) | WR | 100% |  |  |  | 0 [0-0] (0) | 4.3 [3-6] | 48 [24-65] (48) | 33.1% / 33.1% | 71 |
| DJ Moore (BUF) | WR | 67% |  |  |  | 2 [0-0] (1) | 3.0 [2-4] | 39 [16-55] (39) | 25.0% / 25.5% | 41 |
| Keon Coleman (BUF) | WR | 95% |  |  |  | 0 [0-0] (0) | 2.9 [2-4] | 37 [14-52] (36) | 20.7% / 20.2% | 52 |
| Dalton Kincaid (BUF) | TE | 100% |  |  |  | 0 [0-0] (0) | 3.7 [2-5] | 43 [20-60] (43) | 20.2% / 20.1% | 63 |
| Matthew Stafford (LA) | QB | 100% | 21.9 | 272 [205-326] (274) | 2.07 |  |  |  | 8.9% / 8.3% | 87 |
| Kyren Williams (LA) | RB | 100% |  |  |  | 72 [48-91] (71) | 3.1 [2-4] | 25 [10-35] (25) | 65.3% / 61.1% | 82 |
| Blake Corum (LA) | RB | 100% |  |  |  | 37 [20-50] (37) | 0.8 [0-1] | 6 [0-10] (6) | 32.0% / 28.4% | 68 |
| Puka Nacua (LA) | WR | 100% |  |  |  | 1 [0-0] (1) | 6.9 [5-9] | 96 [56-125] (96) | 43.3% / 40.4% | 66 |
| Davante Adams (LA) | WR | 95% |  |  |  | 0 [0-0] (0) | 5.1 [3-7] | 80 [43-106] (81) | 44.9% / 41.1% | 72 |
| Konata Mumpfield (LA) | WR | 95% |  |  |  | 0 [0-0] (0) | 1.2 [0-2] | 17 [0-26] (17) | 13.8% / 12.5% | 35 |
| Tyler Higbee (LA) | TE | 81% |  |  |  | 0 [0-0] (0) | 2.5 [1-4] | 27 [9-39] (27) | 22.3% / 20.1% | 46 |

**Anytime TD ranking (MARKET-ANCHORED track; model probability only)** with the usage behind it

| # | Player | Model prob | Rush TD mean | Rec TD mean | Targets (share) | Carries (share) | Driver |
|---|---|---|---|---|---|---|---|
| 1 | Kyren Williams (LA) | 65.3% | 0.72 | 0.28 | 4.4 (10%) | 14.2 (48%) | tgt_sh 10.0%; team att 37.5; opp DvP 0.89; RZ tgt 2; car_sh 47.9%; team rush 26.0; opp d_ypc 0.98; inside-10 car 7 |
| 2 | James Cook (BUF) | 62.2% | 0.78 | 0.15 | 2.8 (7%) | 16.1 (57%) | tgt_sh 7.4%; team att 31.4; opp DvP 1.09; RZ tgt 2; car_sh 57.5%; team rush 27.1; opp d_ypc 0.97; inside-10 car 8 |
| 3 | Davante Adams (LA) | 44.9% | 0.00 | 0.58 | 9.0 (20%) |  | tgt_sh 19.9%; team att 37.5; opp DvP 0.97; RZ tgt 4 |
| 4 | Puka Nacua (LA) | 43.3% | 0.04 | 0.51 | 10.9 (24%) |  | tgt_sh 23.5%; team att 37.5; opp DvP 0.97; RZ tgt 1 |
| 5 | Khalil Shakir (BUF) | 33.1% | 0.00 | 0.40 | 7.2 (19%) |  | tgt_sh 19.0%; team att 31.4; opp DvP 1.09; RZ tgt 5 |
| 6 | Blake Corum (LA) | 32.0% | 0.28 | 0.10 | 1.1 (3%) | 7.9 (27%) | tgt_sh 2.6%; team att 37.5; opp DvP 0.89; RZ tgt 1; car_sh 26.6%; team rush 26.0; opp d_ypc 0.98; inside-10 car 0 |

**First TD scorer ranking (model probability)**: Kyren Williams (LA) 15.7%; James Cook (BUF) 14.4%; Davante Adams (LA) 8.9%; Puka Nacua (LA) 8.6%; Khalil Shakir (BUF) 6.1%

MODEL-ONLY track anytime top 3 for comparison: James Cook 62.2%; Kyren Williams 61.1%; Davante Adams 41.1%
