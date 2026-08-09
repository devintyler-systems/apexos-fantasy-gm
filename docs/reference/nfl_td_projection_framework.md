# NFL Touchdown Projection Framework (Hypothesis Source)

> **Status: hypothesis-source. Not an approved algorithm.** Trait weights, xTD constants, and modeling weights below require independent source validation before any value is used in production. See `touchdownos_planning_and_execution_blueprint.md` for the doctrinally correct scoring-neutral architecture this framework should be reconciled against.

**Original title:** A Mathematical Framework for NFL Touchdown Projections
**Author:** Predictive AI Collaborator | **Date:** August 2026 | **Scope:** QB, RB, WR, TE

## 1. Positional Trait Grading Framework (0-100 Scale)

### QB Trait Matrix
| Trait | Weight | Rationale |
|---|---|---|
| Goal-Line Rushing Gravity | 95/100 | QB draws/sneaks/read-options inside the 5; highest driver of elite QB scoring variance |
| Red Zone Off-Script Creation | 85/100 | Extending plays when routes break down in compressed spaces |
| Tight-Window Ball Placement | 80/100 | Precision on back-shoulder fades/quick seams in compressed field |
| Pre-Snap Processing & Auditing | 75/100 | Identifying blitzes/coverages, checking into optimal plays |

### RB Trait Matrix
| Trait | Weight | Rationale |
|---|---|---|
| Contact Balance & Pad Level | 95/100 | Absorbing contact at/behind LOS, maintaining momentum — convert-to-score mechanics |
| Short-Area Burst & Acceleration | 90/100 | Hitting closing creases before second-level fill — dictates green-zone conversion |
| Pass-Catching Versatility | 80/100 | Option routes/screens/wheels in red zone; keeps player on field all 3 downs |
| Open-Field Breakaway Speed | 70/100 | Turning 15-yard creases into 50+ yard scores |

### WR Trait Matrix
| Trait | Weight | Rationale |
|---|---|---|
| Compressed Space Route Separation | 95/100 | Hard breaks within 5 yards vs. press-man |
| Contested Catch & Catch Radius | 90/100 | Winning jump balls/back-shoulder throws |
| YAC & Explosive Elusiveness | 85/100 | Turning screens/crosses into long scores |
| Press-Coverage Release Profile | 80/100 | Defeating LOS jams instantly — critical in RZ timing |

### TE Trait Matrix
| Trait | Weight | Rationale |
|---|---|---|
| Apex Size & Height Leverage | 95/100 | Boxing out DBs/LBs in middle of field |
| Seam-Splitting Linear Speed | 85/100 | Clearing LBs, attacking safety void |
| Inline Blocking Integrity | 75/100 | Staying on field in run-heavy goal-line sets |
| Under-Cut Concentration | 70/100 | Securing catches under heavy contact over the middle |

## 2. Modeling Weights: Individual Stats vs. Scheme Impact

| Dimension | Weight | Core Metrics |
|---|---|---|
| Volume & Opportunity | 45% | Red zone carries/target share, goal-to-go touches (inside 5), routes per team dropback |
| Offensive Scheme Quality | 25% | Projected team implied Vegas point totals, EPA/play, pace, RZ pass/run ratio |
| Individual Efficiency | 20% | High-value touch conversion rate, xTD over/underperformance, targets per route run (TPRR) |
| Talent & Trait Profile | 10% | Speed/burst/height-weight percentiles, age-curve regression multipliers |

## 3. 20-Year Historical Macro Trends (2006-2026)

- **Devaluation of the workhorse RB:** Mid-2000s elite RBs logged 300+ carries, 75%+ goal-line share (Tomlinson, Alexander). Modern committees split volume, lowering individual floors.
- **Rise of the mobile QB:** Rushing QB production cannibalizes traditional RB goal-line scores.
- **Compressed target consolidation:** Modern passing funnels RZ looks to 'Power Slots' and dominant X-receivers, minimizing fullbacks/blocking TEs.

### Relative Positional Scarcity & Scoring Value
| Rank | Position | Predictive Reliability | Core Driver |
|---|---|---|---|
| 1 | RB | High (Tier 1) | High volume density inside the 5 makes rushing TDs easiest to model via opportunity tracking |
| 2 | WR | Moderate (Tier 2) | Dependent on passing volume/depth-of-target; high week-to-week variance |
| 3 | QB | Moderate (Tier 2) | Rushing QBs highly predictable; pocket passers depend on scheme quality |
| 4 | TE | Low (Tier 3) | Highly volatile; relies on elite targets or specific RZ mismatch designs |

## 4. Step-by-Step Blueprint for a 2026 Projection Engine

1. **Baseline Team Environment Setup:** Incorporate Vegas team implied point totals and win/loss over-unders for all 32 franchises. Regress against historical OC tendencies and O-line rankings.
2. **Calculate Expected Touchdowns (xTD):** Isolate historical touches by field location. Example cited values: carry from 1-yard line = 0.55 xTD; target at back of end zone = 0.38 xTD. **These constants are unvalidated — must be recomputed from your own historical play-by-play source (see decision log).**
3. **Factor in Personnel/Coaching Adjustments:** Adjust for offseason roster moves, coaching changes. 3-year weighted decay: 50% 2025, 33% 2024, 17% 2023.
4. **Execute Monte Carlo Simulation:** Minimum 10,000 iterations accounting for injury risk, schedule difficulty, variance. Use distribution mean for final rankings.

---
*Converted from source PDF `nfl_td_projection_framework.pdf`, uploaded 2026-08-09. Original marked "Confidential - Proprietary Research" by source author — verify redistribution rights before any external use.*
