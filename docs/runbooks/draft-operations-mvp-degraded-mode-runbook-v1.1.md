# Draft Operations MVP Degraded-Mode Runbook

**Artifact:** Draft Operations MVP Degraded-Mode Runbook  
**Version:** 1.1  
**Owner:** ApexOS Principal Product and Systems Architect  
**Status:** Approved architecture — pending repository promotion  
**Dependencies:** SPAMML 2026 League Rules v0.7; SPAMML 2026 Draft Seat Assignment v1.2; SPAMML 2026 Round Order Map v1.0; validated B-05 session state; Draft State Manager Contract v0.2-correction  
**Change type:** Structural  
**Implementation target:** Redraft Draft Operations MVP  
**External-data posture:** No external player evidence required or authorized  
**Decision-system posture:** No recommendations, rankings, projections, scoring, PRV, availability, roster fit, optimizer, or automated player actions  

## 1. Decision statement

ApexOS Draft Operations MVP is a manual-entry-first live-draft control system.

During a live draft, ApexOS must:

1. Record observed draft events safely.
2. Preserve the authority and provenance of each visible state claim.
3. Display planned schedule information without treating it as live evidence.
4. Allow additive correction, void, restoration, and identity correction.
5. Preserve unresolved player identity as a visible manual claim.
6. Enter visible degraded mode when a required input is missing, invalid, stale, conflicting, ambiguous, or unauthorized.
7. Withhold claims that cannot be proven safely.
8. Remain useful without player recommendations or external player data.

ApexOS Draft Operations MVP must not select players, rank players, calculate player value, infer availability, refresh projections, perform scoring, calculate PRV or replacement value, calculate roster fit, invoke an optimizer, retrieve player data, or make any external draft-platform write.

## 2. Scope and non-goals

### In scope

- Manual pick entry.
- Manual draft-event validation.
- Planned schedule visibility.
- Live draft-state visibility.
- Manual-live, validated B-05, and planned-schedule authority handling.
- Additive correction, void, restore, and identity-correction workflows.
- Canonical identity safety without provider lookup.
- Visible degraded mode.
- Roster and draft-state visibility.
- Auditability, provenance, correction lineage, and post-draft reconciliation.

### Explicit non-goals

- Player recommendations.
- Best-available-player logic.
- Player rankings, ADP, analyst projections, or crowd consensus.
- Football projections or projected fantasy points.
- Scoring, PRV, replacement value, or value-over-replacement calculations.
- Availability models, availability pools, injuries, roster status, or player-status claims.
- Roster-fit scoring.
- Draft optimization.
- Provider retrieval, API clients, player-source lookup, caching, or player-data persistence.
- Canonical identity mapping validation or automatic canonical identity creation.
- Endpoints that expose player recommendation or source-derived player evidence.
- Automated pick, waiver, lineup, trade, or account behavior.
- Any external write.

## 3. Authority hierarchy

ApexOS must determine draft state through this authority order:

```text
1. MANUAL_LIVE_EVENT
2. VALIDATED_B05_SESSION_STATE
3. PLANNED_SCHEDULE_STATE
4. NO_VALID_STATE
```

### 3.1 Manual live event

A `MANUAL_LIVE_EVENT` is an operator-entered observed pick, correction, void, restoration, or identity-correction event.

A valid manual live event has the highest authority because it records an observed real-world draft occurrence. It may establish that an operator entered a claim about a pick, team, player text, correction, or state transition.

It does not independently establish an externally verified player identity, player status, roster status, current team, injury, availability, or recommendation.

### 3.2 Validated B-05 session state

A `VALIDATED_B05_SESSION_STATE` may provide live draft-state evidence only when it satisfies its own validation, provenance, temporal, and degraded-state requirements.

Validated B-05 state must not override a valid later manual live event.

A stale, invalid, missing, unparseable, incomplete, or degraded B-05 state must trigger degraded mode. It must not be silently replaced with planned schedule state.

### 3.3 Planned schedule state

A `PLANNED_SCHEDULE_STATE` is limited to planned schedule and planned seat information.

For SPAMML 2026, the governing planned authorities are:

- League Rules: `contracts/league_rules/spamml-2026-v0.7.yaml`
- Planned schedule and seat assignment: `contracts/draft/spamml-2026-draft-seat-assignment-v1.2.yaml`
- Finalized round order map: `contracts/draft/spamml-2026-round-order-map-v1.0.yaml`

Planned schedule state may display:

- League name.
- League format.
- Planned draft date and time.
- Local timezone and UTC start time.
- Planned manager seat.
- Planned pick sequence.
- Schedule validation state.
- Authority reference.
- Known planned-schedule limitations.

Planned schedule state must not claim:

- The draft is live.
- A pick clock is active.
- A current overall pick exists.
- A player has been selected.
- A roster is current.
- A team is currently on the clock.
- A provider-confirmed draft event has occurred.

### 3.4 No valid state

`NO_VALID_STATE` applies when ApexOS lacks a valid manual live event, validated B-05 session state, or valid planned schedule artifact for the requested claim.

When `NO_VALID_STATE` applies, ApexOS must enter visible degraded mode, show the reason, preserve safe manual entry where possible, and withhold unsupported claims.

## 4. Pre-draft operating procedure

Before draft start, the operator must:

1. Confirm the league context is SPAMML 2026.
2. Confirm the manager/operator context is Professor FleX.
3. Confirm the planned manager seat is 4.
4. Confirm the planned overall picks are:
   - 4
   - 29
   - 45
   - 52
   - 68
   - 93
   - 109
   - 116
5. Confirm the planned draft start:
   - Local: `2026-08-30 16:00 America/Los_Angeles`
   - UTC: `2026-08-30T23:00:00Z`
6. Confirm ApexOS displays the planned schedule as `PLANNED_SCHEDULE_STATE`.
7. Confirm manual pick entry is available.
8. Confirm additive correction, void, restore, and identity-correction workflows are available.
9. Confirm ApexOS displays the active state authority, validation state, as-of timestamp, and known limitations.
10. Confirm no player recommendation or player-source retrieval process is active.

The system must:

1. Validate the League Rules artifact selected by the applicable version-discovery process.
2. Validate the planned seat-assignment artifact.
3. Validate planned schedule timing, timezone, manager seat, and team/seat constraints.
4. Validate the finalized round order map.
5. Display schedule information as planned only.
6. Enter degraded mode if planned schedule validation fails.
7. Never infer a live draft from the scheduled start time, clock value, date, timezone, or planned pick sequence alone.

## 5. Manual pick-entry procedure

### 5.1 Operator procedure

For each observed live pick:

1. Select the observed overall pick, or the observed round and draft slot.
2. Enter the observed drafting team or seat.
3. Enter the player text exactly as observed.
4. Confirm the manual event before acceptance.
5. Review whether the event was accepted, rejected, pending correction, or marked identity-unresolved.
6. Review the resulting draft-state authority and validation/degraded-mode status.

### 5.2 System procedure

For each manual pick-entry attempt, ApexOS must:

1. Validate the pick against the finalized round order map when that map is valid.
2. Validate team/seat consistency when a valid planned seat assignment can support the validation.
3. Preserve the entry attempt whether accepted or rejected, subject to the event-record policy.
4. Record the operator, entry time, event sequence, source authority, and validation result.
5. Store manual player text as an observed manual claim.
6. Rebuild draft state only from accepted ordered events.
7. Show whether a resulting state is manual-live, validated B-05, planned-only, degraded, or unavailable.
8. Show any reason code and known limitation.
9. Never trigger external player lookup.
10. Never create a player recommendation.
11. Never infer a canonical player identity from manual text alone.

## 6. Player identity safety

### 6.1 Identity rule

Manual player text is a draft-event claim. It is not a verified canonical identity unless a pre-existing valid ApexOS canonical identity is explicitly available through an independently approved identity workflow.

A player claim may have one of these states:

```text
RESOLVED_FROM_EXISTING_CANONICAL_IDENTITY
MANUAL_CLAIM_PENDING_REVIEW
AMBIGUOUS_IDENTITY_QUARANTINED
IDENTITY_UNAVAILABLE
```

### 6.2 Unresolved identity procedure

When manual player text is unresolved or ambiguous, ApexOS must:

1. Preserve the manual text exactly as entered.
2. Preserve the manual pick event if it is structurally valid.
3. Leave `canonical_player_id` absent.
4. Attach `CANONICAL_IDENTITY_UNRESOLVED`, `AMBIGUOUS_IDENTITY_QUARANTINED`, or `IDENTITY_UNAVAILABLE` as applicable.
5. Show the identity uncertainty visibly.
6. Exclude the unresolved identity from any source-dependent or future decision workflow.
7. Permit a later additive identity-correction event.
8. Preserve the original manual event and original manual player text.

### 6.3 Prohibited identity behavior

ApexOS Draft Operations MVP must not:

- Retrieve an external player source.
- Query a provider.
- Fuzzy-match player names.
- Match a player based on team, position, age, college, jersey number, draft information, ranking, ADP, or narrative context.
- Automatically create a canonical player identity.
- Automatically merge identities.
- Destructively replace an existing identity record.
- Claim a player’s current team, roster, injury, availability, position, or status.

## 7. Additive correction procedure

### 7.1 Correction principle

Every correction is additive. ApexOS must preserve the original manual event, its original evidence, and its original state effect.

A correction changes the current reconstructed state through a new attributable event. It must never silently mutate or erase historical entry evidence.

### 7.2 Operator procedure

When a manual event is wrong, incomplete, duplicated, out of order, or identity-ambiguous:

1. Select the target original event.
2. Choose the correction type.
3. Enter a correction reason.
4. Enter corrected information where applicable.
5. Confirm the correction.
6. Review the resulting rebuilt state.
7. Confirm that the original event remains visible in the audit history.

Allowed correction types:

```text
WRONG_PLAYER_ENTRY
WRONG_TEAM_OR_SEAT
WRONG_PICK_NUMBER
DUPLICATE_ENTRY
EVENT_ORDER_CORRECTION
VOID_MANUAL_ENTRY
RESTORE_PREVIOUSLY_VOIDED_ENTRY
IDENTITY_CORRECTION
```

### 7.3 System procedure

For every correction, ApexOS must:

1. Create a new correction event.
2. Reference the target event ID.
3. Record correction type, correction reason, correction owner, and correction timestamp.
4. Preserve the target original event unchanged.
5. Record state before correction and state after correction.
6. Rebuild draft and roster state from valid ordered events.
7. Mark affected state as corrected, voided, restored, or pending review.
8. Retain correction lineage for post-draft reconciliation.
9. Enter degraded mode if deterministic state rebuild fails.
10. Never hide a correction or rewrite history silently.

## 8. Degraded-mode procedure

### 8.1 General rule

Degraded mode is mandatory whenever ApexOS cannot make a required claim safely.

Degraded mode must:

- Be visible.
- Identify the affected capability.
- Identify one or more reason codes.
- Identify the active state authority.
- Show the last valid state time where available.
- State known limitations.
- Preserve safe manual operation where structurally possible.
- Withhold invalid, stale, uncertain, or unauthorized claims.
- Never substitute unavailable data with narrative, rankings, ADP, analyst projections, or recommendation language.

### 8.2 Trigger and response matrix

| Trigger | Required state | Required operator action | Required system behavior |
|---|---|---|---|
| Planned schedule is missing, invalid, or unparseable | `DEGRADED` | Verify actual draft context manually and use observed manual entry where safe | Show `PLANNED_SCHEDULE_UNAVAILABLE` or `PLANNED_SCHEDULE_INVALID`; do not claim live state |
| Seat assignment is invalid, duplicated, missing a manager marker, mismatched, or timezone-invalid | `DEGRADED` | Do not rely on planned seat/pick calculations; preserve manually observed events | Show applicable schedule reason; do not derive current manager seat from invalid data |
| Finalized round map is unavailable or invalid | `DEGRADED` | Enter manual event as pending/manual claim only where policy permits | Show `ROUND_MAP_UNAVAILABLE` or `ROUND_MAP_INVALID`; withhold structural pick validity and next-pick assertions |
| A valid manual event is accepted | `MANUAL_LIVE_EVENT` | Continue observed manual entry | Rebuild from accepted ordered manual events; manual event outranks B-05 and planned schedule |
| B-05 state is missing, stale, invalid, unparseable, incomplete, or degraded | `DEGRADED` or `MANUAL_LIVE_EVENT` | Continue manual entry; do not rely on B-05 for unsupported claims | Show B-05 reason code; do not silently fall back to planned schedule as live state |
| Duplicate overall pick or conflicting manual events | `DEGRADED` | Create an additive correction, void, or restore event | Show `DRAFT_EVENT_CONFLICT` or `DUPLICATE_OVERALL_PICK`; preserve all conflicting evidence |
| Player identity is unresolved or ambiguous | `DEGRADED_IDENTITY` | Preserve exact manual text and correct later if evidence becomes available | Do not lookup, infer, merge, or claim verified identity |
| Correction or state rebuild fails | `DEGRADED` | Stop relying on reconstructed current state; preserve event evidence | Show `STATE_REBUILD_FAILED`; display last valid state only with timestamp and limitation |
| Player source is unavailable, unauthorized, or insufficiently evidenced | `SOURCE_UNAVAILABLE` | Continue manual draft-event recording only | Show source reason; do not attempt retrieval or substitute another source |
| Scheduled draft time has passed but no live evidence exists | `SCHEDULE_ONLY` or `NO_VALID_STATE` | Confirm draft activity through observed manual event | Do not claim the draft is live or a pick clock is active |

### 8.3 Required reason codes

```text
PLANNED_SCHEDULE_UNAVAILABLE
PLANNED_SCHEDULE_INVALID
DRAFT_SEAT_ASSIGNMENT_INVALID
DRAFT_SEAT_AMBIGUOUS
ROUND_MAP_UNAVAILABLE
ROUND_MAP_INVALID
SCHEDULE_ONLY_NO_LIVE_CONFIRMATION
B05_SESSION_STATE_MISSING
B05_SESSION_STATE_INVALID
B05_SESSION_STATE_STALE
B05_SESSION_STATE_DEGRADED
NO_VALID_LIVE_STATE
MANUAL_LIVE_EVENT_ACCEPTED
DRAFT_EVENT_CONFLICT
DUPLICATE_OVERALL_PICK
STATE_REBUILD_FAILED
CANONICAL_IDENTITY_UNRESOLVED
AMBIGUOUS_IDENTITY_QUARANTINED
IDENTITY_UNAVAILABLE
IDENTITY_CORRECTION_PENDING
SOURCE_NOT_APPROVED
SOURCE_RIGHTS_INSUFFICIENT_EVIDENCE
SOURCE_UNAVAILABLE
SOURCE_PROVENANCE_INCOMPLETE
```

### 8.4 Required visible state

Every visible Draft Operations state must expose:

```text
degraded_mode_active
degraded_reason_codes
active_state_authority
as_of_timestamp
input_snapshot_id_or_null
event_log_version_or_null
last_valid_state_timestamp_or_null
known_limitations
safe_operator_action
withheld_claims
```

The system must never display any of the following unless independently proven through the applicable state authority:

```text
Draft is live.
Current pick is known.
A team is on the clock.
A player identity is confirmed.
A roster is current.
A player is available.
A player is recommended.
A source is current.
```

## 9. Draft and roster-state visibility

### 9.1 Required schedule view

The schedule view must display:

- League name and season.
- Draft format.
- Planned start local time.
- Planned start UTC time.
- Timezone.
- Planned manager seat.
- Planned pick sequence.
- Schedule authority artifact reference.
- Schedule validation state.
- Known limitations.
- `PLANNED_SCHEDULE_STATE` authority label.

### 9.2 Required live-state view

The live-state view must display:

- Draft session ID.
- Active state authority.
- As-of timestamp.
- Input snapshot ID where available.
- Event-log version where available.
- Completed-pick count.
- Expected draft bound where valid.
- Current overall pick, round, and slot only when proven.
- Degraded mode state.
- Reason codes.
- Known limitations.
- Last valid state timestamp where available.
- Correction count.
- Unresolved identity count.

### 9.3 Required roster-state view

The roster-state view must display only what accepted ordered events and valid authority can support:

- Drafting team or seat claim.
- Accepted draft events.
- Corrected, voided, restored, and pending-review event markers.
- Roster-slot occupancy claim where structurally supported.
- Unresolved identity count.
- State rebuild time.
- Active state authority.
- Validation and degraded state.
- Known limitations.

Roster state must not claim an externally verified player, current roster, position, status, team, injury, availability, or player-source fact unless a separate future authorization explicitly permits that role.

## 10. Audit and post-draft reconciliation

### 10.1 Required event audit fields

Every manual event must retain:

```text
event_id
event_type
league_id
draft_session_id
overall_pick
round_number
draft_slot
drafting_team_claim
player_display_input
canonical_player_id_or_null
identity_resolution_status
identity_reason_code
source_authority
entered_by
entered_at_utc
as_of_timestamp
input_snapshot_id_or_null
event_sequence
prior_state_hash
resulting_state_hash
```

Every correction must additionally retain:

```text
correction_event_id
target_event_id
correction_type
correction_reason
correction_owner
correction_at_utc
original_event_preserved
prior_state_hash
resulting_state_hash
rebuild_result
```

### 10.2 Post-draft reconciliation

After the operator confirms draft completion:

1. Freeze the ordered draft-event log.
2. Record final event-log version.
3. Record final state hash.
4. Record completed-pick count and expected pick bound where the final round map is valid.
5. Record unresolved player identity claims.
6. Record rejected, voided, restored, corrected, and pending-review events.
7. Record degraded-mode periods and reason codes.
8. Record whether B-05 state was present, valid, and consistent with manual events.
9. Produce a reconciliation summary for the operator.
10. Do not infer missing events, missing player identities, current roster facts, player availability, or draft outcomes.

## 11. Legacy v1.0 relationship

`docs/runbooks/live-draft-degraded-mode-runbook-v1.0.md` remains preserved without modification.

For Draft Operations MVP only, v1.0 is non-governing because it contains procedures associated with a future Projection-Backed MVP, including recommendation, projection, scoring, PRV, availability, roster-fit, optimizer, and related decision-system behavior.

Those procedures are deferred. They may be reconsidered only after separately approved source-specific authorization, projection-artifact, scoring, decision-adapter, optimizer, implementation, acceptance-test, release-review, and operator-confirmation gates are satisfied.

This v1.1 runbook is the governing live-draft operating procedure for Draft Operations MVP.

## 12. Risks, assumptions, and limitations

### Risks

- Planned schedule may be valid but cannot prove the draft is live.
- Manual player text may be structurally usable for event recording while player identity remains unresolved.
- B-05 state may be missing, stale, invalid, or degraded during a live draft.
- Corrections can affect downstream roster/draft-state claims.
- A valid manual event may conflict with planned schedule or B-05 state.
- No authorized operational player-evidence source exists.
- No recommendation system is available or permitted in this MVP.
- The runtime League Rules default-path v0.6/v0.7 discrepancy remains an unresolved implementation provenance issue.

### Assumptions

- SPAMML 2026 remains a 16-team, eight-round, no-bench, manual-entry redraft league.
- The planned seat is 4.
- Manual live entry remains the safe primary operational path.
- Existing B-05 and Draft State Manager components may be used only to the extent that their validation and authority conditions are satisfied.
- No external player source, player projection, ranking, ADP, or analyst projection is required for Draft Operations MVP.

### Known limitations

- ApexOS may record manual player text without resolving canonical identity.
- ApexOS may show planned draft information without claiming live draft status.
- ApexOS may show manual-event-derived draft state without externally verifying players.
- ApexOS does not provide player-choice guidance in this MVP.
- ApexOS must visibly degrade rather than invent current-state, player, roster, or decision claims.

## 13. Acceptance criteria

1. The runbook explicitly governs Draft Operations MVP only.
2. The runbook explicitly preserves `live-draft-degraded-mode-runbook-v1.0.md` unchanged.
3. The runbook explicitly designates v1.0 as non-governing for Draft Operations MVP.
4. The runbook contains a manual-entry-first live-draft procedure.
5. The runbook states manual live event > validated B-05 session state > planned schedule state.
6. The runbook prohibits live-status claims from planned schedule data alone.
7. The runbook defines additive correction, void, restore, and state rebuild behavior.
8. The runbook preserves unresolved identity as a visible manual claim.
9. The runbook prohibits provider lookup, fuzzy matching, automatic identity creation, and destructive identity merge.
10. The runbook defines visible degraded mode with reason codes, safe operator action, known limitations, and withheld claims.
11. The runbook defines audit and post-draft reconciliation requirements.
12. The runbook contains no operative instruction to generate, display, calculate, consume, or rely on recommendations, rankings, ADP, analyst projections, projections, scoring, PRV, replacement value, availability, roster fit, optimizer outputs, provider retrieval, player-source lookup, player-data persistence, automated actions, or external writes.
13. Every reference to deferred decision-system capabilities appears only in an explicit prohibition, non-goal, risk, limitation, or legacy-v1.0 deferral statement.
14. The runbook makes no false current-player, current-roster, current-status, player-availability, or live-draft claim.
