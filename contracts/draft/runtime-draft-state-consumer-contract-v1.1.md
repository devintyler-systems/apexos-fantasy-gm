# Runtime Draft-State Consumer Contract — v1.1 (DRAFT — pending Architect/Reviewer sign-off)

Artifact: `runtime_draft_state_consumer_contract`
Version: 1.1
Status: DRAFT — proposed, not yet canonical; supersedes v1.0
Ticket: (new — depends on B-05, DSA-01–08, Round-Order-Map v1.2, League Rules v0.4)
Owner: Architect (Devin)

## Change Log
- v1.0 (2026-08-19): Initial contract. Corrected a Reviewer-channel verdict's fabricated
  interface claims against source excerpts.
- v1.1 (2026-08-19): Closed the two remaining `[unknown]` gaps by reading the complete
  `engine/contracts/draft_seat_assignment.py` source (666 lines, from the PR #20 commit patch)
  rather than excerpts. Corrects §4.1/§4.2 field mappings, resolves §7 unresolved items, adds
  one new risk (hard-coded single-league manager identity), and clears Builder to begin
  implementation.

---

## 1. Decision statement (unchanged from v1.0)

This consumer answers, at any moment during a live SPAMML 2026 draft: **"What can the draft-day
UI and recommendation adapter safely assume right now about which seat is on the clock, what
pick number that is, and whether this information is current enough to act on?"**

## 2. Scope and non-goals (unchanged from v1.0)

Read-only join across B-05, the DSA validator/classifier, the round-order-map authority, and
League Rules v0.4. No pick-order derivation, no writes, no B-06, no automation.

## 3. Access patterns (unchanged from v1.0)

1. Resolve current manager seat.
2. Resolve next N picks for a manager's seat.
3. Determine live vs. degraded UI eligibility.
4. Resolve whose pick a given pick_number belongs to (delegated).
5. Detect and surface staleness.

## 4. Contracts (revised)

### 4.1 Input contract — corrected field-level bindings

`[confirmed evidence, full source read]`

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

**Key architectural finding (new in v1.1):** `validate_draft_seat_assignment(...)` **already
calls `classify_draft_activity` internally** and folds its `derived_classification` string into
`DraftSeatAssignmentValidation.activity_classification`. The consumer gets a basic live/degraded
signal for free from a single validator call. It only needs a **second, separate call** to
`classify_draft_activity(seat_contract, seat_path)` when it needs the richer boolean evidence
flags (`live_claim_allowed`, `missing_valid_selection_transition`,
`missing_confirmed_real_time_pick_feed`) for the degraded-banner UI copy — the validator's return
object does not expose these.

| Source | Confirmed entry point | Freshness handling |
|---|---|---|
| B-05 session state | `engine/draft_state/repository.py` against `draft_session_state`/`draft_pick_entries` | Read at call time |
| DSA validator | `validate_draft_seat_assignment(seat_artifact_path, league_rules_path) -> DraftSeatAssignmentValidation`; raises `ContractValidationError` on any DSA-01–08 failure | Re-run every snapshot; catch `ContractValidationError` specifically, not bare `Exception` |
| DSA activity classifier (optional 2nd call) | `classify_draft_activity(seat_contract: Mapping, seat_path) -> DraftActivityClassification` | Call only when boolean evidence flags are needed for banner copy |
| Round-order-map | `engine/draft/round_order_map.py: build_full_map()` | Deterministic; re-derive if resolved league-rules version changes |
| League Rules v0.4 | `contracts/league_rules/spamml-2026-v0.4.yaml`, `draft.draft_clock_config.*` | Loaded fresh per snapshot |

### 4.2 Output contract (unchanged shape from v1.0; provenance now fully bound)

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

No field remains unbound to a confirmed source. §4.2's shape is now final, not provisional.

### 4.3 Failure/degraded-mode contract (revised)

- **`ContractValidationError` caught:** use its structured `.criterion` field directly as part of
  the reason code (e.g. `f"DSA_VALIDATION_FAILED_{exc.criterion}"`), `live_status: UNKNOWN`,
  `degraded_banner_required: true`. Do not populate seat/manager fields from the rejected
  artifact. `[confirmed evidence — exception is structured, not string-only]`
- All other §4.3 behavior from v1.0 (DSA-07 no-evidence, B-05 degraded, DSA-08 mismatch,
  round-order-map unavailable, staleness) is unchanged and now fully evidence-bound.

## 5–6. (unchanged from v1.0)

Evidence snapshot requirements and round-order-map delegation boundary stand as written in v1.0.

## 7. Risks, assumptions, unresolved decisions (revised)

- ~~`[unknown]` Full field lists for `DraftSeatAssignmentValidation`~~ — **RESOLVED**: exactly 3
  fields, confirmed via complete source read.
- ~~`[unknown]` Exact failure signaling from `validate_draft_seat_assignment`~~ — **RESOLVED**:
  raises `ContractValidationError` (structured subclass of `ValueError`) on any DSA-01–08
  failure; never returns a false/partial result object.
- **New risk `[confirmed evidence]`:** `EXPECTED_MANAGER_NAME = "Professor FleX"` and
  `EXPECTED_MANAGER_SEAT = 4` are hard-coded module-level constants inside
  `draft_seat_assignment.py`, not read from any config or league-rules field. DSA-03 will hard-fail
  for any future league/season where the manager isn't literally "Professor FleX" at seat 4. This
  validator is currently single-season/single-league bound despite ApexOS's stated
  multi-league/format-agnostic vocabulary. **Owner: Architect. Decision needed before this
  validator is reused for any second league or the 2027 season:** either parameterize these
  constants from League Rules/seat-assignment identity fields, or explicitly scope this validator
  as a SPAMML-2026-only artifact and design a general-purpose successor separately.
- Polling cadence, caching, and concurrency remain open assumptions per v1.0 (unchanged) —
  **Owner: Devin/Architect, before Builder implementation.**

## 8. Builder handoff (revised — unblocked)

**Status: CLEARED to begin implementation.** Both blocking `[unknown]` items are resolved.

**Ordered work (revised):**
1. ~~Enumerate full dataclass fields~~ — done, see §4.1.
2. ~~Read validator's failure path~~ — done: catches must target `ContractValidationError`
   specifically, using its structured `.criterion` attribute.
3. Implement `engine/draft/live_state_consumer.py` producing the §4.2 snapshot shape, calling
   `validate_draft_seat_assignment` first, and only calling `classify_draft_activity` a second
   time when boolean evidence flags are needed for banner copy.
4. Wire the five §3 access patterns.
5. Implement all §4.3 degraded-mode paths using `ContractValidationError.criterion` in reason
   codes.
6. Before treating this validator as reusable for a second league, resolve the new §7 hard-coded
   identity risk with Architect.

Done-when, required tests, and dependency boundaries are unchanged from v1.0 §8.

---

**Version 4.3 – change made:** Closed both remaining `[unknown]` gaps in the Runtime Draft-State
Consumer Contract via complete source verification, corrected the output-field provenance,
surfaced a new hard-coded single-league-identity risk, and cleared Builder to begin
`engine/draft/live_state_consumer.py` implementation.

**Highest-leverage next artifact:** Commit this v1.1 revision to the canonical GitHub repository
under `contracts/draft/`, then open the Builder implementation ticket/issue for
`engine/draft/live_state_consumer.py` referencing this contract.
