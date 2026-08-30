# ApexOS Normalized Fact and Canonical Identity Promotion Contract v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-NORMALIZED-FACT-AND-CANONICAL-IDENTITY-PROMOTION-CONTRACT` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — contract-only review required before normalization or canonical-identity implementation |
| Change type | Structural |
| Dependencies | Projection Feature and Score Lineage Contract v0.1; Projection Source Authorization Register v0.1; nflverse Authorization Reconciliation v0.1; Football-Event Target and Feature Promotion Contract v0.1; nflverse Play-by-Play Ingestion Contract v0.2; nflverse Raw-Evidence Capture Runbook v0.1; SPAMML 2026 league-rules contract; Data Source Connector Register; Decision Ledger |
| Applies to | Future independent ApexOS Projection Mode normalization and canonical-identity promotion |
| Implementation authorization | None. This contract authorizes no source retrieval, parser change, normalized-fact implementation, canonical mapping, identity resolution, feature, target, model, evaluation, scoring, artifact, recommendation, test, configuration change, or external write. |

## Decision Statement

**Design decision:** Raw evidence is immutable source bytes plus provenance. A
normalized fact is a versioned interpretation of bounded raw evidence.
Canonical identity is a durable non-destructive entity reference that preserves
source identity and source-system context. Neither is a projection, fantasy
score, feature, target, ranking, value, availability state, optimizer result,
board output, or recommendation.

**Design decision:** A raw record may become only a candidate normalized fact
after field-semantic mapping, source authorization, source-record lineage,
immutable snapshot ID, parser version, source contract version, retrieval,
effective where available, as-of, availability-cutoff timestamps, and
time-integrity evidence are retained. Candidate status is not operational use.

**Design decision:** Identity uncertainty fails closed. Unresolved aliases,
ambiguous matches, collisions, cross-source conflicts, invalid temporal
relationships, and incomplete provenance are quarantined with evidence. They
are never resolved through name guessing, score similarity, provider signals,
or destructive merge.

## Scope and Explicit Non-Goals

### Scope

- Define promotion boundaries for candidate normalized facts and candidate
  canonical-identity mappings as separate versioned, evidence-bound layers.
- Define lineage, field-semantic, grain, identity, temporal, transformation,
  duplicate, null, conflict, revision, acceptance, and degraded-mode gates.
- Preserve provider-contamination prohibition in `apexos_projection` mode.
- Preserve K and D/O as separate capability gaps.

### Explicit Non-Goals

- No normalized record, mapping, alias, team, game, fact, or data is created
  or approved.
- No source evidence is retrieved, captured, parsed, inspected, downloaded,
  transformed, or stored.
- No source-field semantics, matching algorithm, threshold, conflict rule,
  feature, target, model, metric, formula, score, projection, value,
  availability, optimizer output, board, or recommendation is defined.
- No source authorization, rights, freshness claim, rate limit, or field
  semantics is broadened or claimed.
- No production code, test, fixture, workflow, configuration, dependency,
  migration, artifact, or runtime behavior is authorized.

## Authority and Layer Boundary

```text
approved source authorization
→ immutable raw evidence
→ normalized fact / canonical identity
→ candidate feature record
→ football-event target
→ football-event projection
→ deterministic SPAMML scoring
→ immutable projection artifact
→ decision adapter
→ recommendation
```

Existing raw-evidence capability reaches immutable selected release-asset
evidence, provenance/integrity/time validation, and identity-safety
inspection/quarantine only. It does not create normalized facts, canonical
mappings, features, targets, forecasts, scores, artifacts, or recommendations.

```yaml
layer_separation:
  raw_evidence: "Immutable source bytes and source provenance."
  normalized_fact: "Versioned interpretation of bounded raw evidence with declared semantics and lineage."
  canonical_identity: "Durable non-destructive reference preserving source identity and evidence."
  candidate_feature: "Separately gated proposed model input."
  football_event_target: "Observed historical football outcome at declared grain and cutoff."
  football_event_projection: "Future football-event forecast; not a fantasy score."
  fantasy_scoring: "Deterministic league-rules conversion after separately approved event projection."
  projection_artifact: "Immutable ApexOS lineage artifact."
  provider_snapshot: "Separate, explicitly labeled provider-authority mode."
  recommendation: "Decision-layer output; not a fact, identity, target, or projection."
```

## Source-to-Normalized-Fact Promotion Boundary

A raw record is eligible only as a candidate normalized fact when it retains:

- Separately documented, versioned field-semantic mapping evidence.
- Approved bounded source authorization, source ID, provider or URL, and
  source record or locator reference.
- Immutable raw snapshot ID, parser version, source contract version, and raw
  source-field inventory.
- Retrieval time, effective time where available, as-of time, and availability
  cutoff, plus observation and availability times where distinct.
- Declared fact grain, unit/type, deterministic transformation provenance, and
  duplicate/null/conflict behavior.
- Canonical identity reference and mapping status, or an explicit
  `not_applicable` determination.
- Time-integrity reconstruction result, limitations, promotion decision,
  owner, timestamp, and independent acceptance evidence.

Source authorization never approves a source field semantic, normalized value,
mapping, feature, target, forecast, score, or decision input by itself.

## Candidate Normalized-Fact Record Contract

```yaml
candidate_normalized_fact_record:
  fact_id: "<stable-versioned-fact-id>"
  fact_definition_version: "<semantic-version>"
  status: "candidate_only_not_approved_for_use"
  fact_name: "<human-readable-fact-name>"
  fact_domain: "<bounded-domain>"
  entity_scope: "<player|team|game|play|source_record|other-explicit-scope>"
  row_grain: "<one-row-per-declared-grain>"
  normalized_value:
    value: "<bounded-value-or-explicit-null>"
    declared_unit: "<declared-unit>"
    declared_type: "<numeric|categorical|boolean|timestamp|other>"
  raw_evidence_lineage:
    raw_source_field_inventory: ["<approved-raw-field-reference>"]
    immutable_raw_snapshot_ids: ["<immutable-raw-evidence-snapshot-id>"]
    source_record_or_locator_references: ["<source-record-or-locator-reference>"]
    source_provider_or_url: "<provider-or-url>"
    source_authorization_record: "<approved-source-authorization-reference>"
    source_id: "<stable-source-id>"
    retrieval_timestamp: "<RFC3339 UTC timestamp>"
    effective_timestamp: "<RFC3339 UTC timestamp-or-null>"
    as_of_timestamp: "<RFC3339 UTC timestamp>"
    availability_cutoff_timestamp: "<RFC3339 UTC timestamp>"
    parser_version: "<semantic-version>"
    source_contract_version: "<semantic-version>"
    source_semantic_mapping_reference: "<separately-approved-versioned-reference>"
  canonical_identity:
    canonical_identity_reference: "<stable-canonical-id-or-not_applicable>"
    identity_mapping_status: "<resolved|unresolved|ambiguous|not_applicable>"
    source_identity_reference: "<source-system-identity-or-null>"
    source_system_context: "<bounded-source-context>"
    temporal_team_context: "<versioned-context-or-not_applicable>"
  transformation_provenance:
    normalization_version: "<semantic-version>"
    deterministic_transformation_description: "<bounded-versioned-description>"
    input_field_inventory: ["<raw-or-normalized-input-reference>"]
    duplicate_behavior: "<explicit-separately-versioned-policy>"
    conflict_behavior: "<preserve-conflict|quarantine|other-explicit-policy>"
    null_behavior: "<preserve-null|quarantine|other-explicit-policy>"
    correction_behavior: "new immutable evidence and fact revision; never overwrite prior lineage"
  temporal_integrity:
    raw_observation_timestamp: "<RFC3339 UTC timestamp-or-null>"
    raw_availability_timestamp: "<RFC3339 UTC timestamp-or-null>"
    normalized_fact_effective_timestamp: "<RFC3339 UTC timestamp-or-null>"
    time_integrity_result: "<pass|fail|not_run>"
    retrospective_reconstruction_rule: "Use only evidence available on or before the declared cutoff."
  uncertainty_and_limitations:
    data_freshness_status: "<historical_snapshot|other-approved-status>"
    known_limitations: ["<known-limitation>"]
  fact_promotion:
    decision: "<not_approved|approved|rejected>"
    owner: "<architect-owner>"
    timestamp: "<RFC3339 UTC timestamp-or-null>"
    independent_acceptance_evidence_references: ["<evidence-reference>"]
```

This schema does not create a field interpretation, value, transformation, or
fact instance. Candidate facts cannot enter feature, target, model, scoring,
artifact, replacement-value, availability, optimizer, board, or recommendation
paths.

## Canonical Identity Boundary and Candidate Mapping Record

Player, team, and game entities require stable canonical identifiers when
applicable. Source identity and source-system context are retained; source
aliases are supported without destructive merge.

```yaml
candidate_canonical_identity_mapping_record:
  mapping_id: "<stable-versioned-mapping-id>"
  mapping_definition_version: "<semantic-version>"
  status: "candidate_only_not_approved_for_use"
  entity:
    entity_type: "<player|team|game|other-explicit-type>"
    canonical_identity_id: "<stable-canonical-id-or-unresolved>"
    canonical_identity_status: "<resolved|unresolved|ambiguous|not_applicable>"
    source_identity_id: "<source-system-identity-or-null>"
    source_alias: "<source-preserved-alias-or-null>"
    source_system_context: "<source-system-or-url>"
    temporal_team_context: "<versioned-team-context-or-not_applicable>"
  evidence:
    immutable_raw_snapshot_ids: ["<immutable-raw-evidence-snapshot-id>"]
    source_record_or_locator_references: ["<source-record-or-locator-reference>"]
    source_authorization_record: "<approved-source-authorization-reference>"
    source_id: "<stable-source-id>"
    parser_version: "<semantic-version>"
    retrieval_timestamp: "<RFC3339 UTC timestamp>"
    effective_timestamp: "<RFC3339 UTC timestamp-or-null>"
    as_of_timestamp: "<RFC3339 UTC timestamp>"
    availability_cutoff_timestamp: "<RFC3339 UTC timestamp>"
  mapping_assessment:
    mapping_confidence_status: "<supported|unresolved|ambiguous|conflicted>"
    supporting_evidence_references: ["<evidence-reference>"]
    alias_behavior: "preserve source alias; do not destructively merge"
    ambiguity_behavior: "quarantine; do not guess"
    collision_behavior: "preserve collision and quarantine"
    temporal_relationship_result: "<pass|fail|not_run>"
    known_limitations: ["<known-limitation>"]
  promotion:
    decision: "<not_approved|approved|rejected>"
    owner: "<architect-owner>"
    timestamp: "<RFC3339 UTC timestamp-or-null>"
    independent_acceptance_evidence_references: ["<evidence-reference>"]
```

Name guessing, score similarity, provider rank or ADP, provider fantasy output,
provider consensus, provider recommendation, analyst output, and provider UI
context are prohibited as identity evidence, alias-resolution evidence, or
mapping transformations.

## Entity Grain and Temporal Integrity Rules

- Every fact definition declares exactly one row grain. Play, player-play,
  player-game, player-week, player-season, team-game, team-season, game, and
  source-record grains are distinct.
- Aggregation, disaggregation, joins, and grain conversion cannot be silent.
  A new grain requires a separately versioned definition and time-availability
  assessment.
- Raw observation, raw availability, normalized-fact effective, retrieval,
  as-of, and decision-time availability-cutoff timestamps are separately
  representable where they differ.
- Retrospective facts must be reconstructable only from evidence available on
  or before the relevant cutoff. Unknown availability, invalid time ordering,
  or failed reconstruction is rejected and quarantined.
- Later corrections create new immutable evidence and versioned fact revisions;
  they never rewrite prior snapshots, facts, mappings, or lineage.
- K remains a separate kicker-event capability gap and D/O a separate
  team-event capability gap. This contract implies neither K nor D/O mapping,
  target, or projection support.

## Deterministic Normalization and Conflict Boundary

Every future transformation must be versioned, deterministic, source-field
bounded, and traceable. This contract approves no source field semantics,
calculation, value, rate, feature, target derivation, or player record.

- Duplicate, null, correction, and conflict behavior must be explicit and
  separately versioned before implementation.
- Source disagreement remains preserved; no authoritative value may be chosen
  without a separately approved source-specific resolution policy.
- No value or identity may be imputed, defaulted, dropped, overwritten, or
  merged without an explicit separately versioned policy.

## Provider-Contamination Prohibition

```yaml
provider_contamination_prohibition:
  applies_when: "projection_authority == apexos"
  prohibited_as_fact_semantics_or_identity_evidence:
    - "Fantrax FPTs / FPts"
    - "Fantrax FP/G"
    - "Fantrax Rk / RkOv"
    - "Fantrax ADP"
    - "Fantrax Std / FA status"
    - "Fantrax Opp"
    - "Fantrax %D"
    - "Fantrax Ros"
    - "Fantrax +/-"
    - "Any provider consensus, ranking, fantasy forecast, recommendation, analyst output, or UI signal"
  prohibited_direct_or_indirect_uses:
    - "Fact value, field semantic, mapping evidence, alias-resolution evidence, transformation, calibration data, scoring input, or fallback."
    - "Feature, target, model, replacement-value, availability, optimizer, board, ranking, or recommendation input."
    - "Silent fallback when source, lineage, identity, semantic, time-integrity, or validation checks fail."
  permitted_provider_boundary:
    - "Explicitly labeled provider_snapshot mode with degraded provider authority."
    - "Display-only external comparison after independent ApexOS output is frozen."
    - "No provider field may enter ApexOS Projection Mode mathematics."
```

## Fact and Identity Promotion Gate

```yaml
normalized_fact_and_identity_promotion_gate:
  required_conditions:
    - "Predeclared field-semantic evidence and versioned mapping reference."
    - "Approved bounded source authorization, immutable snapshot, locator, parser, and source-contract lineage."
    - "Declared entity scope, row grain, normalized unit, and type."
    - "Canonical identity evidence or explicit not-applicable determination."
    - "Observation, availability, effective, retrieval, as-of, and cutoff temporal proof where applicable."
    - "Versioned deterministic transformation with bounded input-field inventory."
    - "Explicit duplicate, null, conflict, correction, limitation, and degraded-mode behavior."
    - "Independent acceptance evidence with falsifiable failure condition."
    - "Explicit Architect decision separate from any model output."
  mandatory_rejections:
    - "Source authorization, immutable lineage, field-semantic reference, parser version, or source-contract version missing."
    - "Fact grain, unit, type, transformation, null policy, duplicate policy, or conflict behavior undeclared."
    - "Identity guessed, destructively merged, unresolved, ambiguous, collided, or temporally invalid."
    - "Evidence unavailable by cutoff or time-integrity reconstruction failed."
    - "Provider field, output, rank, ADP, context, consensus, analyst output, or UI signal proposed as fact or identity authority."
    - "Independent evidence or explicit Architect decision missing."
```

No metric, model feature, weight, formula, scoring rule, source-field
interpretation, performance threshold, or implementation detail is selected by
this contract.

## Independent Acceptance Evidence

No test is added by this contract. A future independent, reproducible
acceptance record must prove schema completeness; source-to-fact and
source-to-mapping traceability; ambiguity, collision, alias, and temporal
quarantine; grain integrity; cutoff reconstruction; provider-contamination
negative validation; non-destructive revisions; and visible degraded behavior.

## Rejection and Degraded Behavior

```yaml
normalized_fact_and_identity_rejection_reason_codes:
  - "SOURCE_AUTHORIZATION_FAILED"
  - "RAW_SNAPSHOT_MISSING"
  - "SOURCE_FIELD_SEMANTICS_UNAPPROVED"
  - "FACT_DEFINITION_INCOMPLETE"
  - "FACT_LINEAGE_MISSING"
  - "FACT_GRAIN_UNDECLARED"
  - "FACT_TRANSFORMATION_UNVERSIONED"
  - "FACT_TIME_INTEGRITY_FAILED"
  - "FACT_AVAILABILITY_UNKNOWN"
  - "CANONICAL_IDENTITY_UNRESOLVED"
  - "CANONICAL_IDENTITY_AMBIGUOUS"
  - "IDENTITY_COLLISION_DETECTED"
  - "IDENTITY_TEMPORAL_CONTEXT_INVALID"
  - "SOURCE_CONFLICT_UNRESOLVED"
  - "NULL_POLICY_UNDECLARED"
  - "DUPLICATE_POLICY_UNDECLARED"
  - "INDEPENDENT_ACCEPTANCE_EVIDENCE_MISSING"
  - "PROVIDER_CONTAMINATION_DETECTED"
```

Safe degraded behavior retains immutable raw evidence, candidate facts,
candidate mapping evidence, conflicts, quarantines, validation results,
freshness status, limitations, and reason codes separately. It visibly marks
the candidate-only or degraded state, creates no false current-status claim,
does not overwrite evidence, and produces no valid feature, target, model,
score, artifact, value, availability, optimizer, board, or recommendation.
It must not silently fall back to provider data or Provider Snapshot Mode.

## Assumptions Register

| ID | Default / assumption | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-NORM-001 | No source field semantic is approved merely by raw-evidence capture. | Future normalization | P0 if raw bytes are treated as approved facts. | ApexOS Architect | Before field-semantic implementation. |
| A-NORM-002 | Canonical identity resolution is not implemented by this contract. | Future identity service | P0 if candidate mappings become hidden production identity. | ApexOS Architect / Builder | Before identity implementation. |
| A-NORM-003 | Raw aliases remain source-preserved until independently evidenced. | Alias and mapping workflow | P0 if aliases are silently or destructively merged. | ApexOS Architect | Before mapping promotion. |
| A-NORM-004 | Alternate grains require a separate versioned definition and time assessment. | Fact and feature lineage | P1 if aggregation causes leakage or duplicate counting. | ApexOS Architect | Before alternate-grain use. |
| A-NORM-005 | Provider outputs cannot resolve missing identity or fact semantics. | Normalization and identity boundary | P0 if provider context contaminates ApexOS Projection Mode. | ApexOS Architect / Builder | Immediate and ongoing. |
| A-NORM-006 | K and D/O remain unsupported target and identity capability gaps. | Kicker and team-event design | P1 if unsupported entities are implied as implemented. | ApexOS Architect | Before K or D/O work. |

## Acceptance Criteria

This contract is acceptable only when all criteria are true:

- Exactly one documentation-only contract exists at the declared path.
- Candidate facts and mappings are separate, versioned, evidence-bound layers
  with complete source, field, transformation, grain, identity, time, and
  revision lineage.
- Alias ambiguity, temporal identity conflict, provenance gaps, and source
  disagreement quarantine rather than guessed reconciliation.
- Promotion requires immutable provenance, field-semantic authority, source
  authorization, declared grain, time integrity, deterministic transformation,
  null/conflict policy, independent evidence, and explicit Architect decision.
- Provider data, outputs, ranks, signals, and fallbacks are prohibited from
  ApexOS Projection Mode normalization and identity logic.
- Degradation is visible, reason-coded, non-destructive, and provider-free.
- K and D/O capability implementation is excluded.
- No implementation, source retrieval, test/configuration change, projection,
  scoring, decision behavior, or production behavior is authorized.
- The PR remains one-file, documentation-only, open, non-draft, and unmerged.

## Builder Handoff Boundary

This contract authorizes no implementation. A Builder may not retrieve source
data; change a parser; implement facts, mappings, or identity resolution;
create features or targets; run a model or evaluation; change scoring; create
an artifact; alter board, optimizer, or recommendation behavior; modify tests
or configuration; or make an external write from this contract alone.

A separately approved implementation handoff must specify the approved fact or
mapping definition, bounded source authorization and field-semantic reference,
immutable snapshots and locators, entity grain, source identity and temporal
context, deterministic transformation, null/duplicate/conflict policy,
time-integrity proof, acceptance evidence, degraded behavior, revision
retention, and provider-contamination negative evidence.

## Change Log

- `v0.1` — Structural contract introduced. Establishes the normalized-fact and
  canonical-identity promotion gate following bounded raw-evidence ingestion
  and before candidate feature or football-event target implementation.
