# Post mortem: all of Week 11 (13 games, 2026)

**Graded runs** (frozen before kickoff; `verify` intact; `grade.json` and `grade_players.csv` added next to each):
- Thursday, IND @ HOU: `2026_w11_market_20261119T153948Z` (primary) and `..._model_20261119T153952Z`.
- Sunday and Monday, the other 12 games: `2026_w11_market_20261122T164702Z` (primary) and `..._model_20261122T164706Z`.

**Actuals:** nflverse, fetched 2026-11-24. Pooled player tables use the Sunday run for the 12 games and the Thursday run for IND @ HOU, which is how `engine/weekly/postmortem.py` picks runs.

**Scope:** one week. Nothing here is evidence of model quality by itself; it is a source of hypotheses for the multi-season backtest. No model or calibration change ships from this document (CLAUDE.md rule 5).

## 1. Headline numbers

| Metric (market track, primary) | W11 | Context |
|---|---|---|
| Team points RMSE | **8.46** (line 8.29, model-only 8.85) | W5 8.5–8.6, W6 7.3 |
| Winner hit rate | 9 of 13 (69%) | same as the line; the 4 misses were all underdog wins |
| Rec-yds MAE | 19.5 | W5 21.4–22.1, W6 19.3 |
| Rec-yds P25–P75 coverage | 54% | target 50% |
| Rush-yds MAE (model vs naive average) | **24.4 vs 28.1** | better than naive; W11's best result |
| Pass-yds MAE (model vs naive) | 44.0 vs 46.6 | better than naive in 4 of the last 5 weeks |
| Anytime TD: projected vs actual scorers | **49.5 vs 50** | W5 53–54 vs 55, W6 43–46 vs 40–41 |
| Anytime TD log loss / Brier | **0.410 / 0.126** (`grade.json`, 242 players with a snap) | best of the graded weeks (W5 0.43–0.44, W6 0.43) |
| Team points inside P25–P75 / above P90 | 54% / 4% | calibrated |

Takeaway: the player-level engine had a good week. The team level matched the line by design, and the line missed this week for market-wide reasons. The gaps are in how volume is split between players, in availability rules, and in two pieces of operations.

## 2. Where the engine performed well

1. **Anytime TD probabilities.** Projected scorers 49.5 against 50 actual; every position within 3 scorers. The top bucket (engine 40%+) went 14 of 20 against 10.3 expected, so the engine was if anything under-confident at the top this week (n small).
2. **Rushing.** Yards MAE 24.4 against 28.1 naive, correlation 0.61 against 0.46, calibration slope 0.96. Player carries correlate 0.73 with actual.
3. **Team scoring distributions.** 54% of team scores landed inside P25–P75 and 4% above P90 (only DAL's 51).
4. **Target counts for the top receiver.** Projected 8.08 targets for each team's WR1, actual 8.04.
5. **Within-team ordering.** Projected target rank against actual receiving-yard rank: 0.56.
6. **Availability for healthy players.** Of 280 projected-active players, only 26 logged no snap, and those carried 0.6 projected targets per team.
7. **Availability catches before the freeze.** Beck (ARI) Out, and the second roster pass (four players projected for teams they had left) removed about 4 phantom targets from the frozen run.

## 3. Where it fell short (ranked by impact)

### 3.1 Carry allocation: "OTHER" bucket leakage and lead-back compression
- **Team carries:** actual 26.2 a team against 23.9 allocated to players (**2.3 a team, 9% unassigned**), plus 1.7 carries a team to players who were not in the projection file at all.
- **Lead backs:** projected 13.8 carries, actual 15.3; **6 of 23 lead backs were 6 or more carries above the projection (5 by 8 or more)**:

| Lead back | Projected | Actual |
|---|---|---|
| Chuba Hubbard (CAR) | 14.7 | 27 |
| Jonah Coleman (DEN) | 12.1 | 24 (3 TD) |
| Emmett Johnson (KC) | 12.6 | 23 (105 yds), with Walker Out |
| Breece Hall (NYJ) | 11.4 | 20 |
| Travis Etienne (NO) | 7.7 | 14 |
| Saquon Barkley (PHI) | 11.7 | 17 (75 yds) |
| Montgomery (HOU, TNF) | 13.4 | 26 |

- **RB2:** projected 5.9, actual 4.7. Backups are over-projected as the leaders are under-projected.
- **Consequence:** rush-yards and anytime-TD errors on the lead back. The pre-game unders I drafted on Coleman (24 carries) and Barkley (75 yards) before the entry was rebuilt for MIN @ SF only would have lost.
- **Status:** R-18 tested only the vacated-carries case and was rejected. This is broader: R-14 and R-18 evidence together point at the unassigned bucket.

### 3.2 Availability rules
- **R48 players held Out played.** Roman Wilson (PIT, 49 snaps, 6 targets), Croskey-Merritt (WAS, 28 snaps, 13 carries) and Will Shipley (PHI, 19 snaps) were RES on the Sunday roster and Questionable on the injury report. We zeroed all five R48 players; **3 of 5 played** (Brooks and Pittman did not). WAS's backfield was the casualty: Rachaad White projected 8.75 carries, got 0.
- **Questionable players.** Skill players projected between 5% and 90% to play (n=17, mean 0.63) played 88% of the time (postmortem tool's played flag).
- **Starting QBs.** Mayfield (TB) was projected 0.35 to play and played every snap. Over 2023–26, starting QBs who were Questionable with Limited practice played **49% of the time (n=35)**, against 16% for backups (n=50). The pooled fit (0.35) mixes the two.
- **Inactives timing.** The Sunday freeze (16:47Z) preceded the 4:05 and 4:25 and 8:20 PM ET inactives, so late-window Outs were absent from the frozen runs (they were applied in the DFS and Showdown reruns). Dobbins logged 1 snap with no injury event; that is the kind of player the T-90 list catches.

### 3.3 Receiving yards for high-volume players
- **Calibration slope 0.84** (actual = 1.7 + 0.84 × projected, n=190); TE 0.72, RB 0.67.
- **Where:** players projected for 8 or more targets averaged **75 projected yards against 60 actual**; 4–6 targets, 36 against 29. The WR1 target count was right (8.08 vs 8.04); the WR2 and WR3 target counts were over (5.97 vs 4.88; 4.74 vs 4.08). So the miss is mostly yards per target for the top two options.
- **Examples:** Chase 101 projected, 31 actual; Metcalf 62 projected, 2 actual (4 targets); Burden 62 / 10; Tyson 50 / 6. On the other side, depth players broke out: Antonio Williams 122 yds on 11 targets (projected 38), Jeanty 90, Bech 88, Parker Washington 103.
- **Versus naive:** W11 is the first of the five graded weeks in which the per-game average (MAE 19.73) edged the engine (19.86); the weeks before it favoured the engine by 0.3 to 1.5 yards. A blend of the two was best this week (19.52).

### 3.4 Game script and QB passing
- **Margin errors are market-wide.** The line missed margins by 7.8 on average (engine 7.9), totals by 10.8. Three shootouts did the damage: TEN @ DAL 81 points (line 55.5), BAL @ CAR 68 (44.5), LV @ DEN 62 (41.5). Three games went well under: IND @ HOU 29, MIA @ BUF 35, NO @ CHI 34.
- **No home-field signal.** Home teams beat the spread by 5.0 points in W11 but by -1.2 on the season (2026 weeks swing ±6; 2023–25 averaged +0.6). Noise; nothing to change.
- **QB passing yards** correlate -0.29 with the final margin: QBs on teams that lost by 10+ were over-projected by 23 yards, and QBs on teams that won by 10+ were under-projected by 30. Pass TDs were under-projected: 35.3 projected, 41 actual (+16%).
- **Elasticity check (R-20).** Observed rush share rises 0.0025 per point of margin; the engine uses 0.0022. The engine's response is about right.

### 3.5 In-game availability (RUNBOOK section 3)
Flagged player-games, which should not be read as projection error:

| Game | Event |
|---|---|
| IND @ HOU | Warren missed time; McGowan exited |
| MIA @ BUF | D.J. Moore and Chris Bell missed time; Hawes cut back |
| BAL @ CAR | Bateman missed time; Coker exited in Q4 |
| TB @ DET | Bucky Irving missed time (9 touches after) |
| JAX @ NYG | Tuten exited in Q4 (31 snaps, 10 carries) |
| NYJ @ LAC | Keaton Mitchell hurt in Q1, returned |
| LV @ DEN | Pat Bryant, Dareke Young missed time; Dobbins 1 snap |

Snap drops with no injury event logged (mostly blowout script): Swift 46%, Kamara 11%, Hockenson 51%, Metcalf 62%.

### 3.6 Other
- **Completions:** P25–P75 coverage 42% against 50% target; completions are under-dispersed.
- **Rush yards:** coverage 39% (under-dispersed), so rush intervals are too narrow.
- **Unproven QBs:** Josh Johnson (ARI) projected 220, actual 155; McCord 218 / 102; Milton 211 / 141.

## 4. Game by game

| Game | Final | Engine, home–away (market / model-only) | Line | Margin error vs engine | Notes |
|---|---|---|---|---|---|
| IND @ HOU (TNF) | HOU 26–3 | 28.2–15.5 / 27.4–21.0 | HOU −12.5, 44.5 | +10.3 | See `POSTMORTEM_TNF_IND_HOU_W11.md`; Montgomery 26 carries |
| MIA @ BUF | BUF 26–9 | 30.5–14.0 / 30.3–17.8 | BUF −16.5, 45.5 | +0.5 | Allen 304 yds (proj 227); McCord 102 (218); Shakir 101 |
| BAL @ CAR | CAR 35–33 | 23.4–21.0 / 25.1–21.9 | CAR −2.5, 44.5 | −0.4 | 68 points; Hubbard 27 carries, 2 TD; Henry TD; Legette no snap despite p 1.0 |
| NO @ CHI | CHI 21–13 | 29.5–18.0 / 27.9–19.9 | CHI −11.5, 47.5 | −3.5 | Swift TD on 46% snaps; Etienne 14 carries (7.7); Burden 10 yds |
| TEN @ DAL | DAL 51–30 | 30.9–23.5 / 29.9–21.6 | DAL −7.5, 55.5 | +13.6 | 81 points; Prescott 325 yds, 4 TD; J. Williams 2 TD |
| TB @ DET | DET 31–21 | 25.8–22.4 / 26.7–21.7 | DET −3.5, 48.5 | +6.6 | Mayfield played (p 0.35): 187 yds; Gibbs 2 TD |
| ARI @ KC | KC 34–7 | 28.0–12.5 / 27.5–17.0 | KC −15.5, 40.5 | +11.5 | Beck Out, J. Johnson 155 yds; Mahomes 324, 3 TD; E. Johnson 23/105; McBride 14 targets (proj 13.5), 54 yds; Kelce 2 TD; Worthy TD |
| JAX @ NYG | NYG 23–18 | 19.7–25.8 / 20.3–26.7 | JAX −6.0, 45.5 | +11.1 | Upset; Lawrence 301; Washington 103 yds; McCarthy 173 (236) |
| NYJ @ LAC | NYJ 27–24 | 22.7–19.8 / 22.1–19.4 | LAC −3.0, 43.5 | −5.9 | Road underdog won; Hall 20 carries; McConkey and Shepard 2 TD; Herbert 131 yds |
| LV @ DEN | DEN 38–24 | 25.5–15.0 / 26.6–19.9 | DEN −11.5, 41.5 | +3.5 | 62 points; Coleman 24 carries, 3 TD; Mendoza 267, 3 TD; Jeanty 90 rec; Dobbins 1 snap |
| PIT @ PHI | PHI 19–16 | 17.1–20.4 / 19.0–21.2 | PIT −3.5, 37.5 | +6.3 | Barkley 17/75 + TD; Metcalf 2 yds; Wilson (held Out) 6 targets |
| MIN @ SF | SF 35–10 | 25.1–21.4 / 23.4–20.1 | SF −4.5, 44.5 | +21.3 | Largest margin miss; Evans (Q) 109 yds + TD; Purdy 255, 3 TD; Kittle 2 TD |
| CIN @ WAS (MNF) | WAS 22–20 | 24.3–30.3 / 23.6–28.0 | CIN −6.0, 54.5 | +8.0 | Upset; Chase 31 yds (proj 101); A. Williams 122 on 11 targets; Croskey-Merritt 13 carries (held Out) |

## 5. Scorecard for what we put in front of the operator

| Item | Result |
|---|---|
| **Plays (touchdown markets, 5-pt blended edge)** | **None placed.** Every price was stale (Sat 8:27 PM ET). No bet, no loss. |
| Worthy anytime TD (KC), price-conditional at +305 or longer | **Scored** (TD). Would have cashed if taken at that price. |
| Dobbins anytime TD (DEN) | Did not score (1 snap). |
| Worthy + Dobbins cross-game parlay | Lost. |
| DeepDish top 15 anytime TD (late window) | 6 of 15 scored (Nabers, Hall, Coleman, Barkley, Kittle, McCaffrey), against 5.4 expected; Worthy also scored. |
| Top 15 overall by engine % | 12 of 15 scored against 8.2 expected. |
| DFS Classic lineups, late slate (A / B / C) | **151.0 / 121.6 / 152.7**. Coleman 37.9 and Jeanty 27.9 hit; Wilson 6.9, Hampton 10.3, Mason Taylor 4.5 and Tuten 8.3 did not. Contest finish unknown. |
| Showdown MIN @ SF (Lineup 1 / 2) | **82.5 / 74.2.** Mike Evans (Q, left out) led the game with 25.9 DK points. Builder is exploratory and ungraded. |
| 6-pick, MIN @ SF (all unders) | **2 of 6 (lost).** Won: Jefferson (86, line 87.5), McCaffrey rec (13 vs 33.5). Lost: Cousins (235 vs 232.5), Felton (42 vs 14.5), Hockenson (55 vs 47.5), Purdy (255 vs 241.5). With Kittle (34 vs 48.5, a win) instead of McCaffrey it was 3 of 6. |

The 6-pick lost mostly on SF's blowout: all six legs were the same game-script bet (a grind), and that is what correlation does when the script breaks. The "non-touchdown props are information only" rule (#64) stands.

## 6. Change register for Week 12

Nothing below ships without the noise-aware multi-season backtest where the item is a model change (`promotion_rule_noise_aware`), and a DECISIONS entry.

| ID | Item | Evidence this week | Next step |
|---|---|---|---|
| **R-22** | Carry allocation: close the OTHER bucket (renormalize player carries to team carries, with weight toward the lead back) | 2.3 carries a team unassigned; lead backs +1.5, RB2 -1.2; 6 of 23 leads +6 or more | Backtest `APEX_CARRY_RENORM` on rush_yds MAE, rush_att MAE, TD log loss; subsumes R-14 and the vacated-carry piece of R-18. **Top priority.** |
| **R-23** | Availability: starter flag for QBs (49% vs 16% at Questionable/LP), then the other positions | Mayfield p 0.35, played every snap; Q players overall 63% projected vs 88% played | Add `starter` (depth-chart #1 or last-week snap leader) to `fit_availability`; refit on the scheduled refit day; backtest. |
| **R-24** | R48 players with a practice designation: replace the hard Out with a probability | 3 of 5 played (Wilson, Croskey-Merritt, Shipley) | Roster history is too sparse to backtest. Owner decision: provisional p_active 0.5 for RES/R48 players who appear on the report as Questionable or better, logged weekly. |
| **R-25** | Receiving yards for high-volume receivers (slope 0.84; WR2/WR3 target counts over) | 8+ target players: 75 projected vs 60 actual | Backtest a shrink on yards per target for the top two options, and WR2/WR3 target counts. Do not touch WR1 target counts. |
| **R-26** | QB pass TD rate (35.3 projected vs 41 actual) and completion dispersion (42% coverage) | One week | Check on the 2023–25 backtest first; QB-only rule (#59) applies if confirmed. |
| R-15 | Close it. McBride's projected targets (13.5) matched the actual 14. The concentration concern does not hold for the top option; the yardage piece moves to R-25. | | Lift the McBride hold. |
| R-17 | Fold into R-23. | Mayfield played | |
| R-20 | Close. Observed 0.0025 vs engine 0.0022. | | No backtest. |
| Home-field / totals | Close. Noise (+5.0 this week, -1.2 on the season). | | |

## 7. Operations for Week 12

1. **Two freezes on game day.** Freeze the 1 PM window right after its T-90 inactives (about 16:35Z, as this week). Re-run with the late inactives at about 19:40Z (T-90 for the 4:05 PM ET games), tag the run as the late window, and freeze again. The late ESPN Outs (Thompson, Lambert-Smith, Woods, Cooper) were added only in the DFS rerun, not in a frozen run.
2. **Run `w11_manual_out.py` twice,** the second time on the current run's `proj_all.pkl`. It caught four players projected for teams they had left.
3. **Fresh prices or no plays.** The Sharp pages arrived stamped Sat 8:27 PM ET. Capture prop pages between 11:00 and 11:30 AM ET, refresh before printing, and check the "updated" stamp before sending.
4. **Official inactives.** ESPN's feed caps at 5 names a team. The operator reading NFL.com (or `nfl_inactives.py` after kickoff minus 90) fills the gap.
5. **Fixes shipped this week** (tests pass; both in PR #109): `dfs_collect.py` took its slate from a hard-coded W4 list, so any other week collected nothing; it now reads the games from the DraftKings file. `dfs_showdown.py` dropped both DSTs on MIN @ SF because of a 4-team name map; it now reads the name from the DraftKings file.
6. **Add the in-game availability tool to the Tuesday run.** Done in RUNBOOK section 3; this document used it for all 13 games.
