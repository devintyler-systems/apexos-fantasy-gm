# Week 6 post mortem (2026-10-15 Thursday to 2026-10-19 Monday)

Scope: all 14 games, final (SEA@DEN Thursday, 12 Sunday games, WAS@SF Monday). Per game, the latest frozen run made before kickoff: `2026_w06_*_20261015T2038*` (SEA@DEN), `2026_w06_*_20261017T2239*` (the Sunday-morning freeze; every 1 PM and 4 PM game was graded against it, not against the refreshes), `2026_w06_*_20261019T2255*` (WAS@SF). Reproduce the engine tables with `python engine/weekly/postmortem.py 2026 6`. Pick grading (sections 3.2 to 3.6) used the sims behind the published reports, graded with nflverse box scores plus the ESPN box score for WAS@SF (nflverse had not posted Monday night when this was written).
Caveats: one week, 14 games. Anything under about 100 observations is a direction, not a result. **Monday night is missing from `postmortem.py` section "availability"** (nflverse snap counts lag), so that table shows 18 WAS@SF players as projected-active with no snap; ignore those rows and rerun the script once nflverse posts the game. No book prices exist for any prop, so nothing here is ROI.

## 1. Headline

The engine is calibrated where it is supposed to be (PLAY singles, passing-TD ladder, DK-line-sized game errors) and has no edge where the books are strongest. Two new findings and one confirmed defect:

1. **Games: no edge, as before.** Market-anchored team-points RMSE 7.26 vs 7.30 for the DraftKings line it is anchored to; model-only 7.78. Winners: market-anchored 9 of 14, DK 8 of 14, model-only 6 of 14. Actual average total 43.6 against a 45.5 line (-1.9).
2. **NEW: our LEAN receiving props lost badly.** 105 labeled LEAN receiving lines hit **35%** against 56% expected (both sides: overs and unders alike). LEAN rush and passing lines hit 62% (63 lines). PLAY singles overall hit 58.5% against 59.7% expected (94 lines). This is the strongest signal of the week: where the model disagrees with a receiving line, the line is right.
3. **NEW: rushing yards are over-projected for the second week running** (+5.5 yards per screened rusher, +10.1 in the player table; W5 was +4.6). The 30 to 50 yard tier was projected 36.9 and ran 25.8.
4. **Confirmed defect: a vacated role goes to "other", not to the depth chart.** Jacory Croskey-Merritt (lead back, 12 carries a game) was Out. The engine gave the Washington backs 15 carries against a historical 24 and Rachaad White only 7.9 carries. White actually had 7 carries (27 yards), 4 catches, 30 yards and a touchdown, so the receiving unders (the leg that failed) were the real miss; the rushing unders we pulled would have hit. The mechanism is in `params.py` (`oth_c = max(R - Rushing_Att.sum(), 0)`): the missing player's usage is not in the active sum, so it lands in the "other" bucket and is split by a prior instead of going to peers.
5. **Process:** five of our published recommendations were pulled or downgraded after red-team review before kickoff (section 3.7), and every one that was pulled was right to be pulled.

## 2. What held up

| Check | Result |
|---|---|
| PLAY singles (n=94) | hit 58.5% vs 59.7% expected after the 50/50 shrink; rush and passing PLAYs 65.2% (n=46) |
| Rushing / passing-count lines, all labels (n=109) | rush_att 69% (26), rush_yds 66% (38), pass_att 62% (16), pass_cmp 56% (16), pass_yds 54% (13) |
| QB passing-TD ladder (n=25) | 1+ : sum of probabilities 19.0 vs 21 actual; 2+ : 10.4 vs 11. Calibrated |
| Anytime TD, top 10 | 7 of 10 scored (predicted 64%): Cook, McCaffrey (2), Walker (2), Taylor, J. Williams, Swift (2), Kittle |
| Level | team pass TD 1.44 vs 1.42; rush TD 0.94 vs 0.73; rec yds bias +2.9 per player; pass TD bias none |
| Skill vs a player's own average | rec yds MAE 19.8 vs 20.9 (n=161), rush yds MAE 20.2 vs 22.9 (n=39), pass cmp MAE 4.2 vs 4.7 |
| Freeze and red team | all six runs verified; red-team pulled five bad picks before kickoff (Hutchinson/Marks HOU rec, Daniels cmp O, the Purdy 93% parlay leg, White rush unders, the Purdy under props) |

## 3. What failed and what we learned

### 3.1 Games
| | Team RMSE | Margin MAE | Total MAE | Winners |
|---|---|---|---|---|
| DraftKings line | 7.30 | 6.64 | 10.43 | 8/14 |
| Market-anchored | 7.26 | 6.46 | 10.38 | 9/14 |
| Model-only | 7.78 | 7.44 | 11.29 | 6/14 |

Largest misses were results: HOU@JAX (HOU 34-31, total 65 against 42.5), BUF@LV (63 against 53.5), LAC@KC (KC by 16 as a 7.5-point favorite, total 28 against 41.5), DAL@GB (GB by 10, total 36 against 53.5), ARI@LA (LA won by 2 as a 12.5-point favorite; total 34 against 51.5), WAS@SF (SF 23-17, total 40 against 51.5). Three of the five games with a 51.5+ total finished 11 to 17.5 under (DAL@GB, ARI@LA, WAS@SF) while two others went over (HOU@JAX by 22.5, BUF@LV by 9.5). The model-only track has now lost to the line two weeks running (by 0.3 and 0.5 RMSE); keep it as a diagnostic, not as a pick source.

### 3.2 Single lines (475 screened lines, 262 labeled)
| Group | n | Hit | Expected |
|---|---|---|---|
| ALL screened lines | 475 | 50.1% | 55.8% (61.6% raw) |
| PLAY | 94 | 58.5% | 59.7% |
| LEAN | 168 | 45.2% | 56.3% |
| PLAY receiving (rec, rec_yds) | 48 | 52.1% | 60.0% |
| PLAY rush and passing | 46 | 65.2% | 59.4% |
| LEAN receiving | 105 | **35.2%** | 56.4% |
| LEAN rush and passing | 63 | 61.9% | 56.0% |

By raw model probability: the strongest bin (0.80 and above, n=27) hit 48.1%. Model confidence above 0.60 had no relationship with hit rate. The screen, not the number, is the only thing that works: the gate (log of 3+ games, side cleared in half of recent games) works for rushing and passing counts and fails for receiving.

Bias on all screened lines (model mean minus actual): pass attempts -4.7, pass yards -10.5, completions -2.2, receptions -0.1, receiving yards +0.7, rush attempts +0.4, **rush yards +5.5**. Quarterbacks threw more than projected (team pass attempts 37.0 vs 33.2) and runners ran for less (team rush yards 98.5 vs 118.3).

The published top-30 prop lists: Sunday 1 PM games 48.3% (n=29, expected 61.3%), Sunday 4 PM through Monday 48.3% (n=29, expected 60.7%). They were 9 receiving legs per list, which is why they missed.

### 3.3 Receiving props (the new finding)
LEAN receiving hit 35% on 105 lines, with OVER 41.5% / UNDER 39.5% on receptions and 40.0% / 41.2% on receiving yards, so it is not a direction bias. Low-line unders were worst (UNDER with a line of 2 or less: 27%, n=15; UNDER 30 to 60 yards: 11%, n=9): the model's low-projection players out-performed, which matches the long-standing receiving under-projection of low-share players (bias +22% in the backtest). Treat every receiving LEAN as suppressed until a multi-season check on lines exists (we have none: the backtest has no book lines). Action: stop publishing LEAN receiving lines (section 4, item 2).

### 3.4 Touchdowns
- Anytime TD board (163 players, active): predicted 40.0 TDs, actual 32; log loss 0.4471 vs 0.4953 for a flat base rate. Bins: 0.10 to 0.20 predicted 14.6%, actual 6.1% (n=66); 0.40 to 0.50 predicted 44.3%, actual 14.3% (n=14); 0.20 to 0.40 about right; 0.60 and above predicted 65%, actual 78% (n=9).
- Top 30 anytime: hit 37% (predicted 50%). Top 10 hit 70% (predicted 64%).
- Several of the board's RB favorites failed: Kyren Williams, Bijan Robinson, Nacua, Adams, Henry, Josh Allen (all 0). The 0.10 to 0.20 over-prediction sits in the floor's territory (anytime floor 0.06 adopted in #30); the review gate is Week 9.
- QB passing-TD ladder was calibrated (section 2). Purdy 1+ at 93% (raw) and 2+ at 74% were not the problem, but the 93% leg propped up every first-draft parlay.

### 3.5 Parlays
| Slate | Tickets | Hit | Expected |
|---|---|---|---|
| Sunday-morning published | 24 | 3 | 7.3 |
| 4 PM and later refresh | 24 | 6 | 7.4 |

All three AM winners were McCaffrey/other anytime TD + a QB 1+ passing-TD leg; the only 3-leg winners were the two Allgeier-under tickets in the refresh. The legs that sank the most tickets: Rachaad White rec U2.5 (21 tickets), Purdy pass TD 2+ (13), Dalton Kincaid rec U4.5 (10), Brissett rush yds O7.5 (6), Jordan Love rush att U2.5 (4). Same-game and same-script legs (running-back rush-attempt unders in a game that turned pass-heavy) failed together. The Thursday screen went 10/10 on PLAYs and 0/9 on parlays for the same reason.

### 3.6 Volume and availability
- Team pass attempts 33.2 projected, 37.0 actual (RMSE 8.7, sd 8.1); rush attempts 26.6 vs 25.5; pass yards 242 vs 238; rush yards 118 vs 98.5. Attempts were again unpredictable (correlation 0.22 to 0.0): script, not inputs.
- Players with real usage the projection never had: **A.J. Brown (NE, 10 targets)**, Marvin Harrison Jr. (HOU, 4), Travis Hunter (JAX, 4), Will Mallory (IND, 6), Ja'Kobi Lane (BAL, 5), Omar Cooper (NYJ, 7), KeAndre Lambert-Smith (LAC, 9), Audric Estime (CLE, 9 carries), J.J. McCarthy (NYG, 21 attempts and 2 carries; a backup who threw). Both A.J. Brown and Harrison were flagged known gaps before kickoff and kept out of parlays; neither gap was closed.
- Projected active with usage but no snap (excluding Monday night): Sarratt BAL, Shepard NYJ, Ertz PHI, Gainwell TB, Knight ARI.
- Availability of Evans (Questionable, 50% in the model): played, 3 catches, 94 yards. Diggs (67%): played, 6 catches, 44 yards and a TD. Croskey-Merritt: Out as modeled.

### 3.7 Monday night (WAS@SF) in detail
Final SF 23, WAS 17 (market SF 30.0, WAS 22.5). The picks:
- Hit: McCaffrey anytime TD (2 rushing TDs), Kittle anytime TD (1), McCaffrey rush yds O62.5 (64), Okonkwo rec O2.5 (7), Purdy pass att U30.5 (29), Daniels rush att U7.5 (4), White rush yds U45.5 (27, pulled before kickoff).
- Missed: White rec U2.5 (4 catches) and rec yds U14.5 (30), Purdy pass yds U252.5 (264), Daniels pass yds U211.5 (300). Also hit: Daniels pass att O30.5 (40).
- Daniels threw for 300 and 2 TDs with 40 attempts while the model had 193 yards and 1.4 TDs; SF threw for 264 with 2 passing TDs against a 2.4 projection. The pass volume for both teams was under-projected, the same direction as the week as a whole.

### 3.8 Fantasy league (SPAMML) calls
- Quarterback: Caleb Williams (CHI) had 1 passing TD (6 points); Aaron Rodgers (PIT) had 2 (12 points). The recommendation to start Williams with Rodgers as the fallback cost 6 points relative to the fallback.
- Kicker: Nick Folk (ATL, my K pick from the team-implied-points rule) scored 1 point (0 FG, 1 XP); the fallbacks scored Carlson 10, Zvada 7, Fitzgerald 7, Loop 4. Across the 26 kickers this week, **kicker points had a -0.20 correlation with team implied points** (high-implied-points teams scored touchdowns, not field goals). One week proves nothing against the backtest relationship (+), but the rule produced the worst outcome of the available choices.
- Lineup moves otherwise followed the written decision rule (DECISIONS #27); nothing in this section changes the rule. The Fantrax export for scoring the user's actual lineup was not available, so the league-points results above are for the options named in the advice only.

### 3.9 Process defects found
1. The postmortem tooling needs nflverse Monday-night data and breaks (availability, volume) without it. Add an ESPN box-score fallback so the script can run Tuesday morning.
2. `espn_inactives.py` only sees five names per team; final inactives never posted a cleaner list than the injury feed for the 4 PM and Monday games before kickoff.
3. PFR advanced pages remain Cloudflare-blocked; the nflverse mirror covers everything used.
4. Pick grading and parlay grading were run as one-off scripts. They should live in the repo (`pick_grade.py`).

## 4. Actions for Week 7

Ordered by expected value. Items 1 to 3 need a multi-season backtest and a DECISIONS entry before they go live (promotion rule in `contracts/weekly/grading.v0.1.yaml`).

1. **Redistribute a vacated role to peers (engine).** When a player with real usage is Out (manual out, IR, inactive), remove his share from `R`/`T` in `build_roster` so the active depth chart absorbs it, instead of letting it flow into "other". Affects every game with an injured lead back or WR1. Backtest on the 27 slates (weeks 4-12, 2023-25) with known inactives. Also fix the stale-team rule's effect on traded starters (Harrison) and add a Questionable-status hold for returning stars (A.J. Brown) so shares do not collapse to 0.69.
2. **Publishing rule: stop publishing receiving LEANs; keep receiving PLAYs flagged "thin".** The W6 result (35% on 105) plus W5's finding (books beat the model on every count and yardage market) is enough for a non-model gate change. Rush and passing-count lines keep their labels.
3. **Rushing yards over-projection (+5.5 per screened rusher, two weeks in a row).** Check the 27-slate backtest for rush yards bias by projection tier; if the 30 to 50 yard tier is over-projected there too, fit a rush yards multiplier (same mechanism as TD v2).
4. **Parlay construction.** No more than one leg per game script cluster (a rush-attempt under counts as the same script as a game-total under). Shrink all TD legs 50/50 and show raw; cap the pool at the cleanest 12 legs.
5. **Kicker rule.** Re-run `kicker_bt.py` with W4 to W6 included; if the team-implied-points relationship is flat on the 2026 sample, drop it from the lineup advice and rank kickers by the kicker's own 2026 average.
6. **Tooling:** commit `pick_grade.py` and a `postmortem.py --espn-fallback`; log the ESPN inactives file in each frozen run.
7. **Week 9 gate:** anytime-TD 0.06 floor review stays scheduled. W6 added 163 observations with the 0.10 to 0.20 bin over-predicted by 2.4x; if W7 and W8 repeat it the floor is not the cause and the TD v2 position multipliers should be re-fit.

Nothing in this document is a model change. Items 1 to 3 start as candidate branches with backtests, as for TD floor v3 (#29 to #30).
