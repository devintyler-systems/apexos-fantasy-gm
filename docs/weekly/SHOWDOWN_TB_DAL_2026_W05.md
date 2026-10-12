# Showdown ceiling entry: TB @ DAL, Week 5 2026 (NFL Showdown $300K Flea Flicker)

Exploratory and unvalidated. `engine/weekly/dfs_showdown.py` is new, has no backtest, and the dfs-classic skill says Showdown is not implemented in the validated pipeline. Evaluation plan: grade this lineup and its simulated distribution against the actual box score on Tuesday. Reliability, not hit probability.

## The entry (salary 49,900 of an assumed 50,000 cap)
| Slot | Player | DK id | Salary |
|---|---|---|---|
| CPT | CeeDee Lamb (DAL WR) | 44395165 | 17,700 |
| FLEX | Dak Prescott (DAL QB) | 44395115 | 10,400 |
| FLEX | Jalon Daniels (TB QB) | 44395118 | 8,600 |
| FLEX | Chase McLaughlin (TB K) | 44395128 | 5,000 |
| FLEX | Cade Otton (TB TE) | 44395130 | 4,400 |
| FLEX | Ryan Flournoy (DAL WR) | 44395132 | 3,800 |

## What the simulation says (odd-numbered holdout sims; the lineup was chosen on the even-numbered ones)
| View | Mean | P99 | Mean of top 1% | P(150+) | P(175+) |
|---|---|---|---|---|---|
| Raw sim (market-anchored track) | 89.8 | 156.9 | 168.3 | 1.9% | 0.2% |
| Book-anchored yards | 89.7 | 158.7 | 170.5 | 2.0% | 0.3% |

First place under both views, ranked by the worse of the two top-1% means. The next several lineups sit within 1 to 3 points, which is inside the sampling error of a 10,000-sim holdout, so this is the best of a cluster, not a clear winner. Daniels-free alternate with the same ceiling within noise: Prescott CPT, Otton, McLaughlin, Flournoy, Lamb, Pickens (50,000).

## Method
Rules: 1 CPT at 1.5x points and the CPT salary, 5 FLEX, both teams, cap 50,000 (DK Showdown standard; the contest text does not state it). 1,026,974 legal lineups from a 25-player pool (model mean 1 point or more, DK OUT/IR excluded). Ranked first by a mean-plus-2.3-sd proxy, then exactly on the search half. Book-anchored variant scales each player's simulated yardage and receptions so the active-draw median matches the books' main line where at least 3 feeds agree (clamped 0.5x to 2.0x); touchdowns are NOT anchored.

## Caveats
- Ceiling here is low in absolute terms: 2% chance of 150, a quarter of a percent of 175. Do not read "highest ceiling" as likely to win a $50,000 first prize.
- No ownership data, so leverage and uniqueness against a 71,000-entry field are not modeled. Lamb CPT with Prescott is likely popular.
- TB passing is overprojected by the raw sim (books: Daniels 182.5 pass yds, 28.5 attempts; model 250 and about 33). Daniels earns his slot partly through rushing upside (books 44.5 rush yds vs model 14.7), anchored here with a 2.0x cap.
- Kicker points are approximate (engine has no field-goal distance; 3.9 per made FG used).
- Availability: Lamb is Full participation with a thigh designation (about 5% inactive in the model); McLaughlin groin, Full (0.5%). Mayfield Out in both the NFL report and DK. Conflict: Jonathan Mingo (DAL WR) is Questionable (DNP, illness) on the NFL report and blank on DK; not in this lineup. DK lists Demercado and Camden Brown OUT where nflverse has no row. No Thursday report or inactives were available in nflverse at 22:56Z.
- Inputs: DraftKings salary file DKSalaries_5.csv (sha256 prefix 24dd83db5d986d1f, not committed); frozen base runs `2026_w05_market_20261008T230223Z` and `2026_w05_model_20261008T230224Z` define the environment (same spread 9.5 and total 48.5).
