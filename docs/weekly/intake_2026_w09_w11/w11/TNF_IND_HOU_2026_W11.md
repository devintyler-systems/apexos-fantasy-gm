# TNF Week 11: Colts @ Texans, 2026-11-19 8:15 PM ET (2026-11-20 01:15Z), NRG Stadium

**Frozen runs** (15:39Z, 9.5 h before kickoff), both `verify` intact:
- `runs/weekly/2026_w11_market_20261119T153948Z`
- `runs/weekly/2026_w11_model_20261119T153952Z`

**Engine:** main + DECISIONS #66 (`APEX_DEPARTED` on) + the #61 manual-out (`manual_overrides.csv`, 166 rows).

**Inputs:**
- nflverse fetch 2026-11-19 15:30Z.
- Final TNF injury report with designations.
- Depth chart 2026-11-19T07:12:47Z.

**Pre-freeze checks:**
- data-auditor: pass on projections. Its one blocker, a pinned pricing clock, was fixed before the freeze.
- model-qa: pass.

## Availability (final report)
| | Out | Questionable |
|---|---|---|
| IND | LT Bernhard Raimann, RT Jalen Travis, TE Will Mallory, CB Charvarius Ward, DT Jerry Tillery | RT Charlie Heck (DNP all week), WR Anthony Gould (p_active 0.755) |
| HOU | RB Woody Marks (concussion), WR Marvin Harrison Jr., TE Brevin Jordan | G Wyatt Teller |

- **Roof:** retractable. Open for about 15% of games here, and the state is confirmed only near kickoff (operator PDF D038). Forecast 67°F, wind 3 mph, so no weather effect either way.
- **Referee:** Shawn Smith (D046; crews can be substituted).

## Game projection
| | Market-anchored (primary) | Model-only (injury-agnostic for points) | Line (nflverse, current) |
|---|---|---|---|
| HOU win | 84% | 68% | ML −750 / IND +525 |
| Margin (HOU) | 12.7 (median 13) | 6.4 | −12.5 |
| Total | 43.7 (P25–P75 34–53) | 48.4 | 43.5 |
| IND / HOU points | 15.5 (10–20) / 28.2 (20–35) | 21.0 / 27.4 | |

The model-only track's team points do not react to injuries (#33/#49): two IND tackles Out move IND's yardage and sacks but not its points there. Use the market-anchored track. The model-only gap to the line is a known weakness of that track (weeks 4–10), not an edge.

## Team expectations (market track)
| | Plays | Pass att | Rush att | Pass rate | Sacks taken | Pass yds | Rush yds | Off TDs | OL injury index |
|---|---|---|---|---|---|---|---|---|---|
| IND | 63.5 | 33.3 | 26.4 | .58 | **3.75** | 195 | 113 | 1.18 | **1.80** |
| HOU | 61.2 | 33.3 | 26.0 | .57 | 1.87 | 285 | 113 | 3.05 | 0.34 |

Mechanism: IND has no starting tackles, has lost its WR depth (Pierce on IR; Downs and Allen gone), and faces HOU's pass rush. That's why IND projects for the most sacks on the slate and why the market has HOU by 12.5.

## Players (market track; opportunity → production)
Full table: `w11/tnf_ind_hou_players_market.csv`.

| Player | Snaps/role | Targets (share) | Carries (share) | Yds | Anytime TD | Engine pts (P25–P75) |
|---|---|---|---|---|---|---|
| C.J. Stroud HOU | QB1 | – | 3.0 | 259 pass / 16 rush | 14% | 20.0 (14.1–25.1) |
| Nico Collins HOU | WR1 | 8.5 (19%) | – | 78 | 45% | 16.4 (10.1–21.4) |
| Dalton Schultz HOU | TE1 | 6.0 (14%) | – | 46 | 34% | 11.0 (6.1–14.8) |
| Xavier Hutchinson HOU | WR | 5.6 (13%) | – | 45 | 34% | 10.2 (5.4–14.0) |
| Tank Dell HOU | WR (Full) | 4.6 (10%) | – | 45 | 22% | 8.3 (4.2–12.3) |
| David Montgomery HOU | RB1 with Marks Out | 1.4 | 13.4 (32%) | 53 rush / 9 rec | 42% | 9.7 (5.7–13.6) |
| Emari Demercado HOU | RB2 | 1.1 | 6.6 (15%) | 30 rush | 18% | 5.4 |
| Jonathan Taylor IND | RB1 | 6.5 (15%) | 14.2 (53%) | 60 rush / 33 rec | 36% | 16.2 (11.4–20.3) |
| Tyler Warren IND | TE1 | **11.7 (27%)** | – | 64 | 20% | 15.1 (10.3–19.0) |
| Daniel Jones IND | QB1 | – | 2.2 | 198 pass / 8 rush | 8% | 9.0 (5.4–12.2) |
| Laquon Treadwell IND | WR | 3.9 (9%) | – | 26 | 10% | 5.4 |

Warren's 11.7 targets sits well above his last-three-game average (about 7) and comes from targets left by Pierce and Mallory. That's an upper-range projection; treat it as one.

## Markets
- **No actionable price.** The only odds in hand are the operator snapshot from 2026-11-18 19:27Z. They are 20.2 h old at pricing, which fails the 2-hour stale rule. They also predate the Marks and Harrison Jr. Out designations.
- Every IND@HOU row is flagged `stale=True` (reference only).
- **Reference only:** on those stale prices, the best anytime-TD gap is Hutchinson. The blended probability is 29.8% against the book's 26.3%, a +3.5-point edge, below the 5-point minimum (AGENT_INSTRUCTIONS §5). **No play** even before staleness.
- Non-TD props are information only (DECISIONS #64).
- **Model vs market:** the engine's market track sits on the line (HOU −12.65 / 43.7 vs −12.5 / 43.5). No side or total edge exists.
- **Recommendation: no play.** Re-price only if a current snapshot (within 2 h of kickoff) arrives.

## Scenarios
- **Heck (Q) sits:** IND's third-string tackle starts. The engine already carries IND at OL index 1.80; downside is more sacks and fewer IND points, with no recommendation change.
- **Roof open:** no material effect at 67°F and 3 mph.

## Fantasy (engine scoring: PPR, −2 INT/FL, no bonuses; no league-specific scoring verified)
- **Start:** Taylor, Collins, Warren (volume-driven ceiling), Stroud.
- **Downgrade:** Jones (198 yds, 3.75 sacks).
- **Upgrade:** Montgomery (13.4 carries with Marks Out), but his TD equity is shared with Demercado.
