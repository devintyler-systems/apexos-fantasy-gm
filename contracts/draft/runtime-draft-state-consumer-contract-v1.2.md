# Runtime Draft-State Consumer Contract — v1.2 (Architect-approved narrow correction)

Artifact: `runtime_draft_state_consumer_contract`
Version: 1.2
Status: CANONICAL upon merge — Architect-approved narrow correction; supersedes v1.1 for §4.3 only
Ticket: remediation for Issue #23 pause (C-01), pre-implementation contract-boundary conflict
Owner: Architect (Devin)

## Change Log
- v1.0 (2026-08-19): Initial contract. Corrected a Reviewer-channel verdict's fabricated
  interface claims against source excerpts.
- v1.1 (2026-08-19): Closed the two remaining `[unknown]` gaps by reading the complete
  `engine/contracts/draft_seat_assignment.py` source rather than excerpts. Corrected §4.1/§4.2
  field mappings, resolved §7 unresolved items, added one new risk (hard-coded single-league
  manager identity), and cleared Builder to begin implementation.
- v1.2 (2026-08-20): Builder (via Codex) halted Issue #23 implementation on a real
  contract-boundary conflict (C-01): v1.1 §4.3 mapped every `ContractValidationError` to
  `UNKNOWN`/`DSA_VALIDATION_FAILED_<criterion>`, but Issue #23's ordered work already assumed
  DSA-08 specifically degrades to `DEGRADED`/`DSA08_CLOCK_MISMATCH`. Both could not be true as
  written. Architect ruling: adds a single narrow exception for `.criterion == "DSA-08"` only.
  No other DSA criterion's handling changes.

---

## 1. Decision statement (unchanged from v1.1)

This consumer answers, at any moment during a live SPAMML 2026 draft: **"What can the draft-day
UI and recommendation adapter safely assume right now about which seat is on the clock, what
pick number that is, and whether this information is current enough to act on?"**

## 2. Scope and non-goals (unchanged from v1.1)

Read-only join across B-05, the DSA validator/classifier, the round-order-map authority, and
League Rules v0.4/v0.5. No pick-order derivation, no writes, no B-06, no automation.

## 3. Access patterns (unchanged from v1.1)

1. Resolve current manager seat.
2. Resolve next N picks for a manager's seat.
3. Determine live vs. degraded UI eligibility.
4. Resolve whose pick a given pick_number belongs to (delegated).
5. Detect and surface staleness.

## 4. Contracts

### 4.1 Input contract (unchanged from v1.1)

```python
class ContractValidationError(ValueError):
    """Structured, not just a message string."""
    criterion: str        # e.g. "DSA-08"
    artifact_path: str
    field_path: str       # e.g. "draft_state.draft_clock_status"
    actual: Any
    expected: str
    detail: str | None    # for DSA-08, carries the cross-referenced league artifact/field/value

@dataclass(frozen=True)
class DraftSeatAssignmentValidation:      # returned only on full pass; exactly 3 fields
    manager_team_name: str
    manager_draft_seat: int
    activity_classification: str          # already-derived DSA-07 classification string

@dataclass(frozen=True)
class DraftActivityClassification:        # richer object, 6 fields
    artifact_path: str
    raw_selection_state: Any
    derived_classification: str
    live_claim_allowed: bool
    missing_valid_selection_transition: bool
    missing_confirmed_real_time_pick_feed: bool
```

Entry points, freshness handling, and the "validator already calls the classifier internally"
finding are unchanged from v1.1 §4.1.

### 4.2 Output contract (unchanged from v1.1)

```yaml
draft_state_snapshot:
  as_of_timestamp: string
  input_snapshot_id: string
  dsa_validator_version: string
  round_order_map_version: string
  league_rules_version: string
  current_pick_number: integer | null
  on_the_clock_seat: integer | null
  on_the_clock_manager: string | null   # sourced from manager_team_name when validation passes
  live_status: enum[LIVE, DEGRADED, UNKNOWN]
  reason_codes: list[string]
  data_freshness:
    b05_session_age_seconds: number | null
    seat_assignment_artifact_age_seconds: number | null
  known_limitations: list[string]
  degraded_banner_required: boolean
```

### 4.3 Failure/degraded-mode contract (REVISED — v1.2, C-01 resolution)

- **`ContractValidationError` caught, `exc.criterion == "DSA-08"`:** map to
  `live_status: DEGRADED`, reason code `DSA08_CLOCK_MISMATCH`, `degraded_banner_required: true`.
  Do not populate seat/manager fields from the rejected artifact. This is the ONLY criterion with
  distinct handling. `[design decision — Architect ruling, C-01]`
- **`ContractValidationError` caught, any other `.criterion`:** use its structured `.criterion`
  field directly as part of the reason code (`f"DSA_VALIDATION_FAILED_{exc.criterion}"`),
  `live_status: UNKNOWN`, `degraded_banner_required: true`. Do not populate seat/manager fields.
  Unchanged from v1.1. `[confirmed evidence — exception is structured, not string-only]`
- All other §4.3 behavior from v1.1 (DSA-07 no-evidence, B-05 degraded, round-order-map
  unavailable, staleness) is unchanged.

**Rationale for the DSA-08 exception:** DSA-08 is a cross-contract clock-consistency check
(`draft_state.draft_clock_status` vs. League Rules `draft_clock_config.timer_enabled`). A failure
here means the two source artifacts disagree on a knowable fact, not that an artifact is
malformed or incomplete — a materially different, more specific condition than a generic
DSA-01..07 validation failure, and one Issue #23's ordered work already assumed would be visible
to the UI as a distinguishable degraded state rather than folded into a generic "unknown"
bucket.

## 5–6. (unchanged from v1.1)

Evidence snapshot requirements and round-order-map delegation boundary stand as written in v1.1.

## 7. Risks, assumptions, unresolved decisions

- All v1.1 §7 items stand (hard-coded `EXPECTED_MANAGER_NAME`/`EXPECTED_MANAGER_SEAT`; polling
  cadence/caching/concurrency open assumptions).
- **C-01 (this version):** RESOLVED — narrow DSA-08 exception above.
- **New note (v1.2):** `league_rules_version` in §4.2's output shape is currently populated by
  `round_order_map.py:_league_rules_version()`, which as of this contract version still derives
  the value from the league-rules YAML **filename**, not a parsed field. A separate,
  Architect-approved additive artifact (`contracts/league_rules/spamml-2026-v0.5.yaml`) has
  introduced a parseable `contract_version` field for this purpose (C-02), but the corresponding
  code change to `_league_rules_version()` is a **separate Builder issue/PR** and is NOT included
  in this contract revision. Until that code change merges, `league_rules_version` in the output
  snapshot remains filename-derived; do not assume `contract_version` is being read yet.

## 8. Builder handoff (unchanged scope from v1.1 — still CLEARED)

**Status: CLEARED to begin implementation**, contingent on this contract (v1.2) being merged to
`main` in addition to v1.1 — implement against v1.2's §4.3, not v1.1's.

**Ordered work:** unchanged from v1.1 §8, with step 5 updated to: "Implement all §4.3
degraded-mode paths using `ContractValidationError.criterion`, including the DSA-08 exception
(`DEGRADED`/`DSA08_CLOCK_MISMATCH`) introduced in this version."

Done-when, required tests, and dependency boundaries are unchanged from v1.1 §8.

---

**Version 5.3 – change made:** Published Runtime Draft-State Consumer Contract v1.2, resolving
C-01 with a narrow DSA-08 failure-mode exception; all other DSA criteria unchanged from v1.1.

**Highest-leverage next artifact:** Merge this contract, `spamml-2026-v0.5.yaml`, and Decision
Ledger v3.1 via the remediation PR, then open/merge the separate `round_order_map.py`
parsing-fix Builder issue before lifting Issue #23's pause.
