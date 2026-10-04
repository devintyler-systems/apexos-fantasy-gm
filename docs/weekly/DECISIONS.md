# Weekly engine decision log and gate bypass log

## Gate Bypass Log
The root `AGENTS.md` build gate (League Rules Contract, Product Charter, Connector Register, Canonical Data Model,
Draft Recommendation Contract, MVP Acceptance Gates) governs the draft product. The weekly props/DFS engine is a
separate, self-contained package. Per the operator's instruction ("project gates are bypassed, log each skipped gate"):

| Gate | Status for `engine/weekly` | Mitigation |
|---|---|---|
| League Rules Contract | Bypassed (no league scoring in scope; DK Classic scoring in `contracts/weekly/dk_salaries.v1.yaml`) | Weekly contracts written first |
| Draft Recommendation Contract | Not applicable (no draft recommendations produced) | Package never imports `engine.draft*` |
| MVP Acceptance Gates | Bypassed | `tests/weekly` invariant tests + backtest promotion rule |
| Product Charter / Connector Register / Canonical Data Model | Bypassed | nflverse is the only connector, read-only, hashed in every manifest |

AGENTS.md non-negotiables still hold: no secrets, no private league exports, no in-place overwrite of projection
artifacts, as-of + input hashes + version on every run, no future information, platform integrations read-only.

## Decisions
1. Two environment tracks (model-only, market-anchored) are always produced and labeled. Market-anchored won every backtest (team RMSE 8.97 vs 9.33).
2. Calibration is fitted to actuals, never to the market.
3. Joins use ids where available; names only via `norm_name` + team with rejects logged.
4. ffopportunity add-ons and star-preserving share normalization were backtested and NOT adopted (see RUNBOOK section 5).
5. Pipeline modules remain flat scripts for this first landing (byte-for-byte numeric parity with the validated Week 4 build, max diff 0.0). Refactor to relative imports is a later, separately tested change.
6. 2026-10-04: availability fix. Players whose nflverse roster status is RES (IR/PUP/NFI), CUT, RET or EXE are projected out (p_active 0) even when the injury report lists them (`params._apply_roster_out`). Found while auditing the Week 4 freeze: IR players such as Alec Pierce, De'Von Achane and A.J. Brown were projected 100% active. Operator confirmation: British Brooks was placed on IR the morning of the games while the report still listed him, and Odell Beckham Jr. was released. A same-team re-signing (ACT/DEV/INA row for the same player and team) keeps the player live. Baseline comparison: the rule only fires when the roster snapshot for the target week is a full roster; in 2023-25 only week 18 is, so the weeks 4-12 backtest baseline is unchanged by construction. Regression test: `tests/weekly/test_integration.py::test_reserve_released_players_are_never_projected_active`.
7. DK status can disagree with the NFL report and with rosters. Resolution order: roster status (RES/CUT/RET/EXE) > NFL injury report > DK status. Conflicts are flagged in run notes.
8. nflverse does not publish game-day inactives. The Sunday refresh uses the latest injuries, depth charts and rosters; confirmed inactives from another source are applied only as manual overrides recorded in the run notes.
9. 2026-10-04: QB fill-in order. When the depth-chart QB1 is Out, fill-ins are now ordered by depth-chart rank, then attempts (`params.qb_list`). Before, attempts alone were used and Week 4 CHI projected Case Keenum (34 attempts in Week 3) although the 2026-10-03 depth chart moved Tyson Bagent to QB2 behind the injured Caleb Williams, and an independent public projection sheet (DailyFantasyFantasy cheat sheet) listed Bagent. This repeats the anti-pattern "inferring a starter from attempts when a depth chart exists". Backtests are unchanged (older seasons have no depth-chart snapshot and fall back to attempts). Regression test: `test_starting_qb_follows_the_depth_chart_when_qb1_is_out` (fails without the fix, passes with it). WAS (Mariota) and TB (Daniels) were already correct.
10. External cross-check: the DFF cheat sheet (injury flags, public projections, lines) is used only as a sanity check, never as a model input. 2026-10-04 check: all 33 players DFF marks OUT were already out in the model; model vs DFF projection correlation 0.96 (RB 0.98, WR 0.86, QB 0.75). Its ownership column is empty.
