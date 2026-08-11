# Draft State Manager Contract — v0.2-correction (APPROVED — CANONICAL)

# Artifact: draft_state_manager_contract
# Version: 0.2-correction
# Status: APPROVED — canonical B-05 contract, Architect (Devin) sign-off given
# Ticket: B-05 — Draft State Manager
# Change Log:
#   v0.1 — Initial proposal draft. Flagged 4 open questions instead of guessing.
#   v0.2-correction — Resolves U-B05-01 through U-B05-04 per Architect decision. Adds
#          draft_pick_overrides table (including new_entry_id, Builder addition, Architect-
#          confirmed), correction_of_entry_id column, undo audit columns, and acceptance
#          criteria T11-T13. Softens B-06 "unlocks" claim to an assumption. Mirrors B-04's
#          v1.0 -> v1.2-correction lifecycle: a correction creates a new version, nothing in
#          v0.1 is edited in place.

---

## 0. Status

This is the approved, canonical B-05 contract as of Architect sign-off. Implementation may
proceed against this version. Any future change must be a v0.3 clarification/correction,
never an in-place edit.

---

## 1. Scope

Implement a Draft State Manager service that records a live, manually-entered SPAMML
draft pick-by-pick, validates each entry against the frozen B-04 round-order map, and
persists state to SQLite so the draft can be safely paused and resumed.

**Depends on (frozen, already merged):**
- `engine/draft/round_order_map.py` — B-04 pick-order lookup (PR #2, merged)
- `data/processed/draft_round_order_map_spamml_2026.csv` / `draft_position_pick_map_spamml_2026.json`
- `engine/canonical/schema.py` + `engine/canonical/repository.py` — B-02 canonical tables (PR #6, merged)
- `contracts/league_rules/spamml-2026-v0.3.yaml` — league_id, positions, roster config

**Assumption (unconfirmed, not built against):** B-05's output may feed a future B-06
optimizer-input ticket. No B-06 contract exists. Nobody should design against this until a
real B-06 contract exists and explicitly claims B-05 as a dependency.

---

## 2. Non-goals

- No platform API, sync, scraping, or websocket code.
- No autonomous pick, waiver, lineup, or trade logic.
- No auto-merge of ambiguous player identity.
- No re-derivation of the B-04 pick order.

---

## 3. Data model (SQLite, additive to B-02's canonical tables)

```sql
-- One row per manual pick entry attempt, including rejected/invalid attempts.
CREATE TABLE IF NOT EXISTS draft_pick_entries (
    entry_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_session_id     TEXT NOT NULL,
    pick_number          INTEGER NOT NULL,
    raw_player_name      TEXT NOT NULL,
    normalized_player_id TEXT,
    drafting_team_id     TEXT,
    entry_source         TEXT NOT NULL DEFAULT 'manual_entry',
    validation_status    TEXT NOT NULL CHECK (validation_status IN
                          ('accepted','rejected_sequence_mismatch','rejected_identity_ambiguous',
                           'rejected_identity_unresolved','pending_disambiguation')),
    validation_reason_codes TEXT,
    b04_map_version       TEXT NOT NULL,
    correction_of_entry_id INTEGER REFERENCES draft_pick_entries(entry_id),
    entered_at             TEXT NOT NULL,
    accepted_at            TEXT,
    undone_at              TEXT,
    undone_by              TEXT,
    undone_reason          TEXT,
    created_at             TEXT NOT NULL,
    CHECK (
        (undone_at IS NULL AND undone_by IS NULL AND undone_reason IS NULL)
        OR
        (undone_at IS NOT NULL AND undone_by IS NOT NULL AND undone_reason IS NOT NULL)
    )
);

-- Exactly one row per draft session; tracks resume/degraded state.
CREATE TABLE IF NOT EXISTS draft_session_state (
    draft_session_id      TEXT PRIMARY KEY,
    league_id               TEXT NOT NULL,
    current_pick_number     INTEGER NOT NULL,
    last_accepted_entry_id  INTEGER REFERENCES draft_pick_entries(entry_id),
    degraded_mode            INTEGER NOT NULL DEFAULT 0,
    resume_confirmed_at      TEXT,
    started_at               TEXT NOT NULL,
    updated_at               TEXT NOT NULL
);

-- Override path with mandatory audit trail. Resolves U-B05-01.
-- The original rejected_sequence_mismatch row in draft_pick_entries is never mutated.
-- new_entry_id: Builder addition, Architect-confirmed, for bidirectional queryability.
CREATE TABLE IF NOT EXISTS draft_pick_overrides (
    override_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    original_entry_id  INTEGER NOT NULL REFERENCES draft_pick_entries(entry_id),
    new_entry_id        INTEGER NOT NULL REFERENCES draft_pick_entries(entry_id),
    override_reason     TEXT NOT NULL,
    overridden_by       TEXT NOT NULL,
    overridden_at        TEXT NOT NULL
);
```

Separate SQLite file for draft-session state (resolves U-B05-02): draft-session tables live
in `data/draft_state/<session_id>.db`, physically apart from B-02's canonical reference DB.

---

## 4. Behavioral rules

1. **Sequence validation:** reject on mismatch, no state change, no auto-retry.
2. **Override path (resolves U-B05-01):** a human may override a `rejected_sequence_mismatch`
   entry. Requires a non-empty `override_reason` and a real `overridden_by` identity (never
   "system" or blank). Writes a new `accepted` row in `draft_pick_entries` plus a linking row
   in `draft_pick_overrides`. `trading_during_draft` (league rules U04, still unknown) is not
   a blocker — generic override support ships now; if in-draft trading is later confirmed, it
   becomes a specific `override_reason` code, not new schema.
3. **Identity resolution:** zero matches halts as unresolved, multiple matches halts as
   ambiguous, exactly one match proceeds. Never auto-picks.
4. **Disambiguation correction (resolves U-B05-03):** resolving a previously rejected
   ambiguous/unresolved row writes a new row with `correction_of_entry_id` pointing at the
   original. The original row is retained forever, unedited.
5. **Acceptance & persistence:** every accepted pick (including override-derived and
   correction-derived rows) is persisted in the same transaction as the `draft_session_state`
   update. No in-memory-only accepted state.
6. **Resume:** explicit human confirmation required; last accepted pick displayed for
   verification before new entries are accepted.
7. **Undo audit trail (resolves U-B05-04):** undo may only affect
   `draft_session_state.last_accepted_entry_id`. Sets `undone_at`, `undone_by`, and
   `undone_reason` together — CHECK constraint rejects partial fills. Undone rows are never
   deleted; `last_accepted_entry_id` moves back to the prior accepted entry (excluding
   overridden/undone rows).
8. **Degraded mode:** honest stale-state banner, never a false live-status claim.

---

## 5. Acceptance criteria (T01–T13)

| # | Criterion | Test evidence |
|---|---|---|
| T01 | Accepted entry's pick_number matches B-04 map's expected position-for-pick | Insert valid sequential entries for a full round; assert no rejections |
| T02 | Out-of-sequence entry is rejected, not silently accepted | Submit pick 5 when current_pick_number is 3; assert `rejected_sequence_mismatch` |
| T03 | Unresolved player name halts, does not guess | Submit unknown name; assert `rejected_identity_unresolved`, no `dim_player` row auto-created |
| T04 | Ambiguous player name halts with multiple candidates surfaced | Submit name matching 2+ `player_alias_map` rows; assert `rejected_identity_ambiguous`, both candidates returned |
| T05 | Every accepted pick is persisted before the next entry is accepted | Kill process after accept; reload; assert last accepted pick present |
| T06 | Resume requires explicit confirmation, never silent | Restart with existing session; assert new entries rejected until `resume_confirmed_at` is set |
| T07 | Undo affects only the immediately preceding accepted pick | Accept picks 1-3; undo; assert pick 3 undone, picks 1-2 untouched, pick 4 not implicitly resurrected |
| T08 | Degraded mode never claims live status | Simulate missing B-04 artifact; assert `degraded_mode = 1` and banner-equivalent field set |
| T09 | No hardcoded scoring/roster/provider/position values | Service reads league_id, positions, roster config only from league rules contract |
| T10 | Raw entry, normalized identity, timestamps, provenance, validation outcome stored as distinct fields | Schema/row-level assertion on `draft_pick_entries` columns |
| T11 | Override creates a new row; original rejected row is never mutated | Reject a sequence-mismatch entry; submit override with reason+identity; assert original row's `validation_status` still `rejected_sequence_mismatch` and unchanged, new row exists with `validation_status='accepted'`, `draft_pick_overrides` row links both |
| T12 | Undo requires all three audit fields together or fails | Attempt to set only `undone_at` via direct write; assert CHECK constraint violation; then set all three together; assert success |
| T13 | Correction row links via `correction_of_entry_id`; original row unchanged | Resolve an ambiguous entry; assert new row has `correction_of_entry_id = original entry_id`; assert original row's `validation_status` still `rejected_identity_ambiguous`, no fields mutated |

---

## 6. Resolved questions (formerly open in v0.1)

| ID | Resolution |
|---|---|
| U-B05-01 | Override path required, with mandatory audit trail (`draft_pick_overrides`). `trading_during_draft` (league rules U04) remains a separate, non-blocking dependency — generic override support ships now. |
| U-B05-02 | Separate SQLite file for draft-session state, approved. Canonical B-02 data stays untouched by draft-session resets. |
| U-B05-03 | Disambiguation correction is a new row via `correction_of_entry_id`, never an edit. Mirrors B-04's file-level versioning at the row level. |
| U-B05-04 | Undo requires `undone_at` + `undone_by` + `undone_reason` populated together, enforced by a CHECK constraint — partial fill fails. |

---

## 7. Still open / downgraded

- B-06 "unlocks" claim: downgraded to an explicit unconfirmed assumption (§1). Nobody should design against it.
- `draft_pick_overrides.new_entry_id`: Builder addition, Architect-confirmed and approved in final schema.

---

## 8. Reviewer focus

1. Confirm override path never mutates the original rejected row (T11).
2. Confirm undo CHECK constraint actually rejects partial audit-field fills (T12).
3. Confirm disambiguation corrections are additive-only (T13).
4. Confirm sequence validation reads from `round_order_map.py` only — no re-implementation.
5. Confirm identity resolution never auto-picks a candidate under ambiguity.
6. Confirm persistence happens per-accepted-pick, not batched or in-memory-only.
7. Confirm resume path cannot silently continue without explicit human confirmation.
8. Confirm degraded-mode banner/flag is honest and never implies live platform sync.

---

## 9. Disclaimer

This document has not been checked against `docs/decision_ledger.md`, the implementation
backlog, `contracts/optimizer/`, `contracts/scoring/`, or `contracts/recommendation/` — those
files could not be read through the available tooling at draft time. Any contradiction between
this contract and those real documents resolves in favor of the real documents; a follow-up
reconciliation pass is recommended once connector read access is restored.
