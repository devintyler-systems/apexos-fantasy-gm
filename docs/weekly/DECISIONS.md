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
