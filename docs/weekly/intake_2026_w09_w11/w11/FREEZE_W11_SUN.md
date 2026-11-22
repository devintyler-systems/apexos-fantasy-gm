# W11 Sunday/Monday freeze (2026-11-22, 16:47Z)

**Frozen runs** (`verify`: intact)
- `runs/weekly/2026_w11_market_20261122T164702Z` (primary).
- `runs/weekly/2026_w11_model_20261122T164706Z`.

**Availability**
- **nflverse W11 designations** for every team. The Friday PDF overlay (`APEX_STATUS_OVERLAY`) agrees with all 129 rows, so applying it changed nothing.
- **ESPN game-summary Outs**, two pulls (16:36Z and 16:44Z). The skill-position changes:
  - Beck (ARI QB) Out, so Josh Johnson gets p 1.0.
  - Spears (TEN RB) on IR.
  - Singleton (TEN RB) Out.
  - Sarratt (BAL WR) Out, a coach's decision.
- **Roster rules, run twice** (DEV with no depth-chart slot; moved or released). The second pass caught four players who appeared in this run but not in Friday's:
  - M. Brown (PHI)
  - Horn (CAR)
  - R. Miller (MIA)
  - E.J. Jenkins (PHI)

  Lesson: run `w11_manual_out.py` on the *current* run's `proj_all.pkl`, then rerun. Make it a step in the RUNBOOK.
- **Manual-out file:** `var/ro/manual_out_w11_sun.csv`, 242 rows (frozen as `manual_overrides.csv`).
- **R48 players** (Brooks, Pittman, R. Wilson, Shipley, Croskey-Merritt) were still RES in the 16:36Z roster, so they're held Out.
- **Mayfield (TB)** is Questionable after a limited practice and gets p 0.35 (Daniels 0.65). He isn't on ESPN's TB Outs, which only lists 4 of its cap of 5, so he's probably active. Per #55 the feed never marks a player Active, so the split stands. R-17 hold.

**Odds**
- No Sunday prop capture arrived.
- Friday's odds were 2.7 h old and over the 2 h limit, so I deleted them before the freeze.
- No priced output: **no plays.**

**QA**
- data-auditor: PASS after the second roster pass.
- model-qa: PASS.
  - The market track is within 0.23 points of the line.
  - TB moved from 20.0 to 22.5 because the line moved (5.5 / 45.5 to 3.5 / 48.5), not because of the model.

**Holds:** R-14 PHI rushing, R-15 McBride, R-17 TB passing, R-18 KC backfield.

**Slate:** `slate_w11_sun_final.csv`.
