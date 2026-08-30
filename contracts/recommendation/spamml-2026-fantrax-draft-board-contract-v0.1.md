# SPAMML 2026 Fantrax Draft Board Contract v0.1

The board is an offline, deterministic decision artifact. It accepts only a
user-provided local Fantrax 2026 projection CSV, a local 2025 calibration CSV,
and the attested `engine.draft.spamml_configuration` result. It never contacts
a provider, observes live state, derives a generic snake order, or drafts.

`Fantrax FPts` is a provider-computed SPAMML scoring projection; raw scoring
event components were not supplied and are not claimed. ADP is display-only
market context and has zero numeric role in scoring, rank, replacement value,
wait cost, scarcity, fit, or recommendation value.

The adapter-supplied sequence is `[4, 29, 45, 52, 68, 93, 109, 116]`. Pool
demands and replacement anchors are QB16, RB32, REC48, K16, and D_O16. WT
normalizes to REC and DST to D_O while retaining original source values.

For each roster-valid available candidate, the board derives provider score and
rank, pool rank, `replacement_anchor_score` at the canonical pool anchor, and
`generic_replacement_value = max(0, provider_projected_score -
replacement_anchor_score)`. It separately serializes the weighted score inputs
`remaining_slot_scarcity_pressure`, `valid_roster_fit_score`, and
`early_position_suppression_penalty`. The exact reconciliation is
`recommended_pick_value = next_pick_wait_cost + generic_replacement_value +
remaining_slot_scarcity_pressure + valid_roster_fit_score -
early_position_suppression_penalty`. K is suppressed before round 6
unless its documented wait-cost exception passes; D/O is suppressed before the
final round absent its modeled marginal-advantage exception.

Every output is degraded, planned-schedule-only, and manual-live-state-only.
Snapshot provenance records only input filenames, byte sizes, SHA-256 digests,
UUID, `as_of_timestamp`, UTC build timestamp, input snapshot ID,
`projection_version` (`fantrax-provider-fpts-local-snapshot-v0.1`),
`league_id` (`spamml-2026`), `manager_seat` (`4`), configuration version,
optimizer version, uncertainty, and known limitations—never absolute external
paths. `projection_version` identifies this deterministic local-board build; it
does not claim an embedded provider methodology version. The 2025 file is
calibration metadata only and cannot alter 2026 decision math.

The static HTML embeds the generated snapshot and exposes degraded provenance.
Manual drafted/unavailable choices are explicitly local, in-memory browser
state only, are discarded on reload, and are never live-platform validation.
After every recomputation, each rendered availability control and its accessible
`Local/manual` status label must exactly reflect that row's in-memory
availability state. Manually drafted or excluded rows receive conditional
unavailable styling; available rows do not present a stale manual marker.

The static HTML embeds normalized decision inputs, canonical pool demands and
anchors, planned sequence, options, and parity fixtures. Its in-memory adapter
recomputes availability, fallbacks, replacement deltas, components, suppression,
reason codes, alternatives, and recommendation rather than re-ranking stale
precomputed values.

Acceptance mapping: FB-01 header validation; FB-02 historical isolation;
FB-03 raw preservation; FB-04..06 normalization/identity; FB-07..13 planned
schedule and anchors; FB-14..20 eligibility, ADP isolation, marginal sorting,
and suppression; FB-21..27 output/provenance/degraded behavior; FB-28 import
guard; FB-29 deterministic generic, causality, time-integrity, reversibility,
live-failure, and independent acceptance coverage.
