# W11 Sunday/Monday preliminary slate (Friday data, not frozen)

**Run**
- Market-anchored and model-only tracks, run on 2026-11-21 against Friday data.
- `APEX_MANUAL_OUT`: `var/ro/manual_out_w11_fri.csv` (166 rows).
- `APEX_STATUS_OVERLAY`: `var/ro/status_overlay_w11_fri.csv`. These are 129 Friday designations parsed from the operator's injury PDF (D052); nflverse hasn't loaded Sunday designations yet.
- Game projections: `slate_w11_sun_prelim.csv`.

**QA** (data-auditor and model-qa)
- **Projections pass.**
  - The market track matches the line to within 0.3 points on every game.
  - Target shares sum to 1.00 on every team except JAX (0.96).
  - The QB splits reconcile: TB Mayfield 0.35 / Daniels 0.65; ARI Beck 0.35 / Johnson 0.65.
- **Pricing fails.** Every odds row is 2.69 h old, past the 2 h limit. Engine-vs-book gaps below are information only until there's a Sunday capture.

**Known issues**
- **Coverage report.** `injury_report_coverage.csv` counts nflverse rows only, so it shows `out_rows=0` for every team even though the overlay applied. Walker, Ferguson and Addison are all at `p_active` 0. Reporting gap; fix queued.
- **R48 players held Out.** These players are on IR but designated to return, and practicing in their window: Brooks (CAR), Pittman, R. Wilson (PIT), Shipley (PHI), Croskey-Merritt (WAS). They're held Out until they're activated. Sunday's run re-fetches the roster, so a Saturday activation flips them live.

**Holds** (flagged; no reads published on these)
- R-14: PHI rushing (carry allocation 0.69).
- R-15: McBride's target share.
- R-17: TB passing (Mayfield Q).
- R-18: KC backfield with Walker Out (E. Johnson gets 51.6% of carries).

**Touchdown candidates** (blended w=0.5, at least 5 points; stale prices, conditional on a fresh price)

| Player | Model | Book (no-vig) | Edge |
|---|---|---|---|
| Xavier Worthy | 32.8% | 19.6% | +6.6 |
| D'Andre Swift | 65.1% | 54.0% | +5.6 |
| J.K. Dobbins | 37.3% | 26.5% | +5.4 |
| Patrick Mahomes | 26.2% | 15.5% | +5.3 |
