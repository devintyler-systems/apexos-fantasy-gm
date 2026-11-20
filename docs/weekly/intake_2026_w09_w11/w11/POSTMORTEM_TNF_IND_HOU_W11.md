# Post mortem: TNF Week 11, Colts @ Texans (2026-11-19). Final HOU 26, IND 3

**Graded runs** (frozen 2026-11-19 15:39Z, before kickoff):
- `runs/weekly/2026_w11_market_20261119T153948Z` (primary).
- `..._model_20261119T153952Z`.

**Actuals:** nflverse, fetched 2026-11-20 23:45Z; ESPN agrees (event 401873066). Tables: `python engine/weekly/postmortem.py 2026 11`.

**Scope:** one game. Nothing here is evidence of model quality; it's a source of hypotheses for the backtest.

## 1. Game level
| | Market-anchored | Model-only | Line | Actual |
|---|---|---|---|---|
| HOU – IND | 28.2 – 15.5 | 27.4 – 21.0 | 28.5 – 16 (−12.5 / 44.5) | **26 – 3** |
| Margin (HOU) | 12.7 | 6.4 | 12.5 | **23** |
| Total | 43.7 | 48.4 | 44.5 | **29** |
| Margin / total error | −10.4 / +14.7 | −16.6 / +19.4 | −10.5 / +15.5 | |

- **Winner:** right on both tracks.
- **Market track:** matched the line, as designed. Team RMSE 8.98 (line 9.36).
- **Model-only track:** worse (12.75). Its team points ignore injuries (#33/#49), so it gave IND, with both tackles Out, 21 points.
- **Sequence:** IND scored first (a FG), then nothing; HOU led 17–3 at half and 26–3 after three quarters.
- **First-score props:** the engine had HOU first to score at 60% and a FG first at 49%, so the first was a miss and the second a hit. First TD went to Collins, the engine's #1 (13%).

## 2. Team volume and efficiency
| | Pass att | Comp | Pass yds | Sacks | Carries | Rush yds | INT |
|---|---|---|---|---|---|---|---|
| HOU projected | 33.3 | 19.4 | 285 | 1.9 | 26.0 | 113 | 0.3 |
| HOU actual | 27 | 21 | 194 | 1 | **37** | **167** | 1 |
| IND projected | 33.3 | 19.9 | 195 | **3.75** | 26.4 | 113 | 0.9 |
| IND actual | 29 | 12 | 144 | 2 | 17 | 38 | 1 |

Volume followed the game script, not the pregame projection:
- HOU ran 37 times with a 14-point lead at half.
- IND threw only 29 times and ran just 17 times.

Two more misses:
- Jones went 12/29 for 5.0 yards per attempt; the projection was 6.2.
- The engine over-projected sacks on Jones: 3.75 against 2 actual.

## 3. Players (frozen market track vs actual)
| Player | Projected | Actual | Note |
|---|---|---|---|
| **David Montgomery** | 13.4 car / 53 yds | **26 car / 107 yds** | 70% of HOU carries. Marks' lead-back carries (15.8 a game) were spread across all rushers, not to the RB2 → R-18 |
| Tyler Warren | 11.7 tgt / 64 yds | 5 tgt / 22 yds | Vacated targets went to Gould (3), Dulin (4), Watkins (3), Burks (3) → R-15 |
| C.J. Stroud | 259 yds | 194 yds, 3 TD, 1 INT | Lead-protecting script |
| Daniel Jones | 198 yds | 144 yds (12/29), 1 INT | Efficiency collapse behind backup tackles |
| Jonathan Taylor | 14.2 car / 60 + 33 rec | 11 car / 21 + 6 rec | Game script |
| Nico Collins | 78 yds, ATD 45% | 58 yds, TD (first TD) | ✓ TD |
| Kayshon Boutte | 37 yds, ATD 23% | 40 yds, TD | ✓ |
| **Marlin Klein** (TE) | 0.3 tgt | 4 tgt / 24 yds / TD | TE3 with B. Jordan Out → R-19 |
| **Quez Watkins** | not projected | 3 tgt / 26 yds | ACT, unmodelled (#62) → R-19 |
| Anthony Gould | 1.2 tgt (Q, p 0.75) | 3 tgt / 48 yds, 60% snaps | Under-projected |
| Seth McGowan | 4.7 car / 22 | 3 car / 7 | Engine right; the operator review moved off the under |
| Cade Stover (HOU TE) | p_active 1.0, 0.8 tgt | no snap | Availability miss (minor) |

**Shared vs engine-only misses.** The game result was shared with the market: both the line and the engine missed by 10–15 points on margin and total. The engine-specific misses are in how volume is split between players:
- Montgomery's carries;
- Warren's targets;
- Klein and Watkins' targets.

## 4. The published card (DeepDish reads, frozen engine, book % from Thu 2:32 PM ET)
| Read | Result |
|---|---|
| Warren O37.5 rec | ✗ 22 |
| Taylor O21.5 rec | ✗ 6 |
| Schultz O29.5 rec | ✗ 11 |
| Montgomery U56.5 rush | ✗ 107 |
| Treadwell U27.5 rec | ✓ 0 |
| Demercado O20.5 rush | ✓ 33 |
| Jones O179.5 pass | ✗ 144 |
| Dulin O13.5 rec | ✓ 30 |

**3–5.** Three of the misses (Warren, Taylor receiving, Jones passing) were the high-volume IND reads the blowout script killed. Montgomery's rush under was the R-18 miss.

**Removed after operator review:**
- McGowan U26.5: would have **won** (7 yds).
- Jones U7.5 rush: would have **won** (3).
- Montgomery U8.5 rec: would have **lost** (17).

Manual overrides of the engine went 1–2. One game; recorded, not acted on.

**Touchdown bets:** none qualified, so no bet was placed. Hutchinson, the only price-conditional candidate, did not score. The non-touchdown "information only" rule (#64) held up here: 3–5 would have cost money as plays.

## 5. Areas to review
| ID | Finding | Proposed work |
|---|---|---|
| **R-18** | Vacated **carries** from an Out lead back spread proportionally across every rusher (and 'other'), so the RB2 is under-projected (Montgomery 32% share projected, 70% actual). #69 only moves targets. | `APEX_RB_VAC_CAR`: an Out RB's carry weight goes to active RBs (weighted). Two-seed backtest; check the team-weeks with an Out lead back separately. |
| **R-15** (more evidence) | Vacated targets over-concentrate on the top remaining receiver (Warren 11.7 projected vs 5; McBride W11 Sunday). | Cap or shrink each player's share of vacated volume; backtest. |
| **R-19** | Active depth players without a current role (Watkins), and backups whose role jumps when the player above them is Out (Klein TE3 with B. Jordan Out), are missing or near zero. | Extend #62: a replacement prior keyed to depth-chart rank behind an Out player. |
| **R-20** | Game-script elasticity: HOU 37 carries (proj 26), IND 29 attempts (proj 33). The sim's rush share responds weakly to the lead. | Backtest the margin slope (`VOL.pr_margin_slope`, currently 0.0022) against 2023–25 by-quarter script. #40 says pregame volume is mostly unforecastable; this tests the in-sim response, not the pregame mean. |
| #33/#49 | Model-only team points ignore injuries (IND 21 with both tackles Out). | Already queued; this game is a clear example. |
| — | Sack projection with backup tackles: 3.75 projected vs 2. | Monitor; one game. |

**No model change ships from one game.** R-18 and R-15 have a direct mechanism and are the next two backtests.
