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
11. 2026-10-05: team volume dispersion and target-share cap backtested and NOT adopted. Baseline = current model (plays sd 4.0, pass-rate slope 0.0022, no extra noise, no cap); 27 slates (2023-25 weeks 4-12), model track, 5,000 sims. Variant `new` (plays sd 7.9, slope 0.0043, extra pass-rate sd 0.054, cap 0.15, plays 36-95) matched observed team attempt spread (sim sd 7.2 vs 4.8; outside P5-P95 10.4% vs 27.9%) and improved rush yards MAE (24.25 vs 24.31), pinball (29.99 vs 30.32) and coverage (cov50 0.431 vs 0.396), but failed the promotion rule: rec yds MAE 20.288 vs 20.252, rec MAE 1.532 vs 1.528, TD log loss 0.4482 vs 0.4450, pass yds MAE and pinball worse, team points RMSE flat (9.022 vs 9.020). A 33%/36% target-share cap did not help either (rec yds MAE 20.275/20.273 with `new`; 20.244 with the old volume but TD log loss worse 0.4460 and top-1 receiver bias worse, -6.3% vs -6.2% / -7.2% with `new`). Conclusion: the extra volume variance is a calibration-of-tails improvement on rushing and pass coverage but costs point accuracy; no config shipped, defaults in `sim.VOL` equal the baseline. The Week 4 misses were therefore not primarily a volume-variance problem. Harness: `engine/weekly/bt_vol.sh`, `compare_vol.py`.
