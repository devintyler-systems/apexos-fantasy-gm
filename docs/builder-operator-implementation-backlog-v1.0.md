# Builder/Operator Implementation Backlog

**Artifact:** `builder_operator_implementation_backlog`
**Version:** 1.0
**Status:** READY FOR BUILDER
**Owner:** Devin Tyler (Architect)
**Depends On:** All 8 prior specification artifacts (complete)
**Created:** 2026-08-10

---

## 1. Decision Statement

This is the last architecture artifact. It translates 8 completed specification documents into an ordered, dependency-mapped list of concrete build tickets. No new design decisions are made here — every ticket traces back to a specific contract section already approved in the repo. Builder executes against this list; Reviewer validates against the acceptance tests already defined in each source contract.

---

## 2. Repository State (as of this backlog)

```text
apexos-fantasy-gm/
├── AGENTS.md
├── README.md
├── contracts/
│   ├── league_rules/
│   │   ├── spamml-2026-v0.3.yaml           <- CURRENT, use this version
│   │   └── CHANGELOG.md
│   ├── draft/
│   │   └── draft-round-order-map-contract-v1.0.md
│   ├── projections/
│   │   ├── projection-artifact-contract-v1.0.md
│   │   └── projection-artifact-contract-v1.1-addendum.md
│   ├── scoring/
│   │   └── scoring-engine-contract-v1.0.md
│   ├── optimizer/
│   │   └── prv-calculator-contract-v1.0.md
│   └── recommendation/
│       ├── draft-recommendation-engine-contract-v1.0.md
│       ├── draft-recommendation-engine-contract-v1.1-addendum.md
│       └── draft-recommendation-engine-contract-v1.2-addendum.md
├── docs/
│   ├── data_source_connector_register.md            <- v1.2, current
│   ├── decision_ledger.md                            <- single source of truth for version history
│   ├── assumptions_register.md
│   ├── mvp-acceptance-gates-v1.0.md                  <- final go/no-go checklist
│   ├── runbooks/
│   │   └── live-draft-degraded-mode-runbook-v1.0.md
│   └── reference/                                     <- hypothesis/reference only, not contracts
├── data/
│   ├── raw/
│   │   ├── 2026_projections/    (Sharp Football PPG, VegasInsider win totals)
│   │   └── 2025_actuals/        (TeamRankings, PlayerRankings -- calibration only)
│   └── processed/            <- Builder creates: xTD lookup tables, frozen projection artifacts
└── tests/
    └── acceptance/
        └── test_draft_round_order_map.py    <- scaffold exists, needs implementation wiring
```

---

## 3. Ordered Backlog (dependency-sequenced)

### Phase 0: Foundation

| Ticket | Description | Depends On | Done When | Unlocks |
|---|---|---|---|---|
| B-01 | Set up Python project structure (`pyproject.toml`, virtualenv, `nfl_data_py` + `pandas`/`polars` + `pytest` deps) | Data Source Register v1.2 | `pip install -e .` succeeds; `pytest` runs (even with 0 tests passing yet) | Everything below |
| B-02 | Implement canonical data model (SQLite schema): `dim_player`, `dim_team`, `dim_game`, `player_alias_map` | League Rules Contract v0.3, TouchdownOS reference doc | Schema created; test inserts for all 5 SPAMML position types succeed | B-03, B-04 |
| B-03 | Implement League Rules Contract loader (reads `spamml-2026-v0.3.yaml` into a typed config object) | B-01 | Loader returns correct scoring map, roster slots, `draft_clock_config` | Scoring Engine, PRV, Recommendation Engine |

### Phase 1: Draft Mechanics (no data dependency — pure logic, buildable immediately)

| Ticket | Description | Depends On | Done When | Unlocks |
|---|---|---|---|---|
| B-04 | Implement `engine/draft/round_order_map.py` per Draft Round Order Map Contract Section 4 (algorithm) and Section 5 (acceptance tests T01-T10) | B-01 | All tests in `test_draft_round_order_map.py` pass, including T01 ground truth | B-10 (availability pressure) |
| B-05 | Implement Draft State Manager: `draft_state` table, pick entry, undo-last-entry, session persistence | B-02, League Rules Contract | Live-Draft Runbook §3, §7, §8 procedures demonstrable in a scripted test | B-11 (UI) |

### Phase 2: Projection Pipeline (data-dependent, can run parallel to Phase 1)

| Ticket | Description | Depends On | Done When | Unlocks |
|---|---|---|---|---|
| B-06 | Implement nflverse ingestion via `nfl_data_py` (2016-2025 seasons minimum) | B-01, Data Source Register 2.1 | Raw play-by-play pulled and cached locally as Parquet | B-07 |
| B-07 | Build xTD lookup table per Projection Artifact Contract Section 5 (field-position buckets, sample-size tracking) | B-06 | `xtd_lookup_table_v1.parquet` exists with `sample_size` column populated; low-confidence buckets flagged | B-08 |
| B-08 | Implement offensive player projection (Section 6a: QB/RB/WR/TE), kicker projection (6b), and D_O projection (6c), including the v1.1 addendum's PPG-primary/win-total-divergence rule | B-07, `data/raw/2026_projections/*` | PA01-PA10 all pass | B-09 |
| B-09 | Implement frozen artifact writer with immutability enforcement | B-08 | PA04 passes; attempting to modify a frozen artifact raises an error | B-12 |

### Phase 3: Scoring and Value Engines

| Ticket | Description | Depends On | Done When | Unlocks |
|---|---|---|---|---|
| B-10 | Implement Scoring Engine (pure conversion function, Sections 3a-3c) | B-03, B-09 | SE01-SE07 all pass, including the zero-hardcoded-constants static check | B-11 |
| B-11 | Implement PRV Calculator (static + dynamic replacement value, REC merged pool, scarcity_ratio) | B-10, B-05 | PRV01-PRV07 all pass, including the full 128-pick simulated draft test | B-12 |
| B-12 | Implement Draft Recommendation Engine (roster-fit filter, availability pressure via B-04, positional run detection, reason codes, snooze capability) | B-11, B-04 | DR01-DR13 all pass, including the snooze isolation tests (DR10, DR13) | B-13 |

### Phase 4: Interface and Operational Readiness

| Ticket | Description | Depends On | Done When | Unlocks |
|---|---|---|---|---|
| B-13 | Build Streamlit Draft UI: pick entry panel, roster display, recommendation panel with snooze buttons, stale-data banner | B-05, B-12 | Full simulated 128-pick draft completes end-to-end through the UI | B-14 |
| B-14 | Implement identity conflict halt-and-disambiguate flow (Runbook §4) | B-05 | Deliberately ambiguous player name triggers manual resolution UI, zero auto-merge | MVP Gate E2 |
| B-15 | Wire pre-computation trigger (Runbook §6) so recommendations are cached before Devin's turn, not calculated reactively | B-12, B-13 | Zero calculation lag observed at simulated pick time | MVP Gate E4 |

### Phase 5: Validation

| Ticket | Description | Depends On | Done When | Unlocks |
|---|---|---|---|---|
| B-16 | Run full MVP Acceptance Gates test suite (all 28 gates, Categories A-G) | B-01 through B-15 | Every gate shows PASS in the gates document | Live draft authorization |
| B-17 | Backtest xTD model and kicker model against 2025 TeamRankings/PlayerRankings calibration data | B-08 | Model beats a naive position-average baseline per TouchdownOS Gate 2 doctrine | Confidence calibration for "trust the model" (DR_R03a) |

---

## 4. Critical Path

```text
B-01 -> B-02 -> B-03 -> B-06 -> B-07 -> B-08 -> B-09 -> B-10 -> B-11 -> B-12 -> B-13 -> B-16
                  \-> B-04 (parallel, no data dependency) -----------------/
                  \-> B-05 (parallel, needs B-02/B-03 only) -------------/
```

B-04 (Draft Round Order Map) and B-05 (Draft State Manager) can be built and fully tested BEFORE any projection data work completes, since they have zero dependency on nflverse ingestion. Recommend Builder starts there for early momentum and a working demo of the draft-mechanics layer independent of the modeling layer.

---

## 5. Open Items That Do NOT Block This Backlog

| ID | Item | Why It Doesn't Block |
|---|---|---|
| U01 | 2026 draft position | Engine reads this from `draft_state` at runtime; no code depends on knowing it in advance |
| U02 | Draft date/time | Only affects WHEN the projection artifact gets frozen, not how the freeze mechanism works |
| U04-U09 | Trading, missed FG, waivers, playoffs, keeper, prize ties | All Phase 2/non-blocking per League Rules Contract v0.3 |
| B-17 timing | Backtest can run any time before draft day, not a hard sequential gate on B-01–B-16 | Runs in parallel once B-08 completes |

---

## 6. Reviewer Responsibilities

For each ticket marked "Done," Reviewer independently verifies (does not just accept Builder's self-report):
- The cited acceptance tests actually exist and pass when run fresh, not cached
- No hardcoded values appear where a contract specifies "read from config at runtime" (especially B-10/Scoring Engine)
- Frozen artifacts are genuinely immutable (attempt a manual overwrite and confirm it fails)
- The full 128-pick simulated draft (B-11, B-12, B-13) produces reproducible output on a second identical run

---

## 7. Decision Ledger Entry

This is the terminal architecture artifact. All future work in this repository, until a structural failure or major scope change occurs, should be implementation commits against these tickets — not new Architect-level design documents.
