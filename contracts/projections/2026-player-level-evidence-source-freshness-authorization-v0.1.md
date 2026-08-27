# 2026 Player-Level Evidence Source & Freshness Authorization Contract v0.1

**Artifact:** `2026_player_level_evidence_source_freshness_authorization`
**Version:** `0.1`
**Owner:** ApexOS Architect
**Status:** APPROVED GOVERNANCE GATE — NO SOURCE OR LIVE EVIDENCE AUTHORIZED
**Scope:** Documentation and contract-validation only

## 1. Decision and non-authorization boundary

This contract defines the mandatory approval record for any future 2026
player-level evidence source. It does not approve a source, authorize a
provider retrieval, authorize live evidence, create a live projection artifact,
or authorize a recommendation input. A source-specific authorization approved
under this contract is required before a source can be used.

Every source remains read-only. No authorization under this contract may grant
write access for draft picks, rosters, lineups, waivers, trades, provider
accounts, or any external system. Provider/API/network retrieval remains out of
scope for this documentation PR and requires separately authorized
implementation after the source-specific record passes review.

## 2. Permitted roles and prohibited benchmark inputs

`ranking`, `ADP`, and `analyst_projection` roles are benchmark-only. They are
not permitted evidence inputs to an ApexOS-owned projection artifact, scoring,
PRV, availability, roster-fit, or recommendation behavior. A future
source-specific authorization must declare one approved evidence role and must
fail closed if its observed role differs.

## 3. Source-specific authorization record

Before use, each source must have a separately approved, immutable
source-specific authorization record that contains all of the following:

- a unique source authorization ID, source ID, intended decision scope, and
  allowed evidence role;
- confirmation that the source is read-only, its permitted-use/terms posture,
  and an explicit prohibition on external writes;
- `source_sha256` for the exact supplied bytes and a versioned
  `parser_version` used to interpret those bytes;
- non-empty `source_provider` and exactly one source locator: an absolute
  HTTP/HTTPS `source_url` or a non-empty `provider_record_id`;
- UTC `retrieved_at_utc`, UTC `effective_time_utc`, and a declared artifact
  `as_of_timestamp_utc` for non-futurity comparison;
- canonical player/team identity coverage, known limitations, and an explicit
  degraded-mode disposition.

Missing, hash-mismatched, malformed, unapproved, or post-as-of evidence must
fail closed. The provider/locator and parser declarations identify supplied
evidence; they do not authorize a network call.

## 4. U08 hard ingest prerequisite

U08 (keeper/dynasty status) is a hard ingest prerequisite for 2026
player-level evidence. Before any source-specific authorization can be used,
the current U08 resolution and its authority must be recorded for the target
league and as-of time. An unresolved, conflicting, or expired U08 decision
blocks ingest; a default or inferred setting is not a substitute for the
recorded prerequisite.

## 5. Time integrity, freshness, and degraded mode

This v0.1 contract validates temporal non-futurity only: both
`retrieved_at_utc` and `effective_time_utc` must be less than or equal to the
artifact `as_of_timestamp_utc`. It does not certify source freshness and does
not invent a numeric freshness threshold or source SLA.

The source-specific authorization record must define a separately approved,
source-specific freshness policy before non-fixture 2026 evidence or any live
artifact can be authorized. Until that policy is approved, no live evidence
authorization exists under this contract.

When evidence is stale or incomplete, a later authorized consumer must surface
`data_freshness_status` as `stale` or `incomplete`, retain
`known_limitations`, identify the affected decision scope, and avoid any
current, fresh, or complete claim. Stale or incomplete status is degraded mode,
not an authorization to silently substitute data or to produce a live artifact.
This documentation PR implements no display, ingest, or runtime behavior.

## 6. Required evidence package and release gate

A source-specific authorization review package must bind the authorization ID
to the source identity, exact SHA-256, parser version, provider/locator,
retrieval/effective/as-of times, approved role, U08 resolution, freshness
policy, canonical-identity limitations, and degraded-mode statement. The
review must confirm that the package contains no ranking/ADP/analyst input and
no unsupported current-state claim.

Only a separately approved source-specific record that satisfies this contract,
including U08 and the source-specific freshness policy, may be considered for a
separate implementation authorization. That subsequent authorization must
remain fixture-first unless it explicitly grants a different boundary.

## 7. Explicit exclusions

This contract does not change `data/raw`, `data/processed`, engine code, tools,
B-06, B-07, dependencies, CI, provider/API/network behavior, live projection
artifacts, scoring, PRV, availability, roster fit, or recommendations. It does
not authorize retrieval from any existing register entry and does not promote a
candidate connector.
