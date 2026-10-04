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
6. 2026-10-04: availability fix. Players with nflverse roster status RES (IR/PUP/NFI) who are not on the injury report now get p_active 0 (`params._reserve_rows`). Found while auditing the Week 4 freeze: IR players such as Alec Pierce, De'Von Achane and A.J. Brown were projected 100% active. A player who is on the injury report keeps the report's status, since he may have been activated. Baseline comparison: the rule only fires when the roster snapshot for the target week is a full roster; in 2023-25 only week 18 is, so the weeks 4-12 backtest baseline is unchanged by construction. Regression test: `tests/weekly/test_integration.py::test_reserve_list_players_are_never_projected_active` (fails without the fix, passes with it).
7. Known gap: DK status can show OUT/IR for players the NFL report does not list (Week 4: Odell Beckham Jr, British Brooks). The NFL report governs; conflicts are flagged in run notes.
