# ApexOS nflverse Play-by-Play Field Semantics Evidence Contract v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-NFLVERSE-PLAY-BY-PLAY-FIELD-SEMANTICS-EVIDENCE-CONTRACT` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — contract-only review required before individual field semantic approval |
| Change type | Structural |
| Dependencies | Normalized Fact and Canonical Identity Promotion Contract v0.1; Football-Event Target and Feature Promotion Contract v0.1; Projection Feature and Score Lineage Contract v0.1; Projection Source Authorization Register v0.1; nflverse Authorization Reconciliation v0.1; nflverse Play-by-Play Ingestion Contract v0.2; nflverse Raw-Evidence Capture Runbook v0.1; Data Source Connector Register; Decision Ledger |
| Applies to | Future source-field semantic evidence for independently governed ApexOS Projection Mode work |
| Implementation authorization | None. This contract authorizes no source retrieval, documentation collection, evidence retention, parser change, raw-evidence processing, semantic mapping, normalized-fact creation, canonical identity work, feature, target, model, evaluation, scoring, artifact, board, optimizer, recommendation, test, configuration, dependency, external write, or merge. |

## Decision Statement

**Design decision:** Version-pinned upstream nflverse play-by-play documentation
is the only semantic authority for future raw-field meaning. Immutable locally
retained evidence is required for auditability, but is an audit artifact only
and never substitutes for upstream semantic authority.

Neither upstream documentation presence nor local retention alone approves an
individual field semantic, normalized fact, canonical identity, feature,
target, forecast, fantasy score, artifact, rank, value, availability state,
optimizer output, board output, recommendation, or implementation.

**Decision ID:** `D-NORM-SEMANTICS-001`.

## Scope and Explicit Non-Goals

### Scope

- Establish source-evidence authority and retention requirements before a
  future individual raw-field semantic decision.
- Define evidence-registration and future field-semantic authorization record
  schemas using placeholders only.
- Define version applicability, revision, evidence sufficiency, rejection,
  degradation, provider-contamination, and no-inference boundaries.
- Preserve K and D/O as separate capability gaps.

### Explicit Non-Goals

- No upstream documentation is retrieved, browsed, downloaded, inspected,
  quoted, captured, or retained.
- No actual raw field is named, enumerated, selected, or defined.
- No semantic statement is made about a field, event, attribution, ownership,
  null, correction, timing, identity, player, team, game, play, or source.
- No evidence snapshot, retention artifact, source mapping, normalized fact,
  canonical identity, feature, target, model, evaluation, score, projection,
  artifact, board, optimizer, or recommendation is created.
- No code, test, fixture, configuration, workflow, dependency, migration, or
  data artifact is added or changed.
- No source authorization is broadened and no provider input or provider-
  derived semantic claim is permitted.

## Authority and Layer Boundary

```text
approved source authorization
→ immutable raw evidence
→ source-field semantic evidence
→ candidate normalized fact / candidate canonical identity
→ candidate feature
→ football-event target
→ event projection
→ deterministic SPAMML scoring
→ immutable projection artifact
→ decision adapter
→ recommendation
```

```yaml
source_authority_roles:
  upstream_version_pinned_documentation:
    role: "Required semantic authority for an individual source field."
    required_identity: "Upstream documentation URL plus immutable commit, tag, or equivalent version pin."
  immutable_local_evidence_snapshot:
    role: "Required retained audit record for bounded documentation evidence."
    required_identity: "Immutable snapshot ID and SHA-256."
    limitation: "Never substitutes for upstream semantic authority."
  approved_source_authorization_register:
    role: "Separately required permission and boundary authority."
    limitation: "Does not confer field semantics."
  raw_release_asset:
    role: "Immutable source-data evidence."
    limitation: "May establish observed structural presence only; cannot independently establish field meaning."
  normalized_fact_contract:
    role: "Downstream consumer gate."
    limitation: "Cannot promote a raw field without separately approved semantic-mapping reference."
```

## Evidence Registration Record Contract

This schema registers a future semantic question. It contains no actual URL,
commit, tag, field, documentation excerpt, snapshot, or semantic claim.

```yaml
field_semantic_evidence_registration:
  evidence_registration_id: "<stable-versioned-evidence-registration-id>"
  contract_version: "v0.1"
  status: "candidate_only_not_approved_for_use"
  source_family: "<source-family>"
  upstream_documentation_url: "<upstream-documentation-url>"
  upstream_immutable_version_pin:
    pin_type: "<commit|tag|equivalent>"
    pin_value: "<immutable-version-pin>"
  documentation_title_or_locator: "<documentation-title-or-locator>"
  documentation_retrieval_timestamp: "<RFC3339 UTC timestamp>"
  documentation_effective_or_published_timestamp: "<RFC3339 UTC timestamp-or-null>"
  terms_or_rights_reference: "<approved-reference>"
  documentation_availability_status: "<available|unavailable|unknown>"
  immutable_local_evidence:
    snapshot_id: "<immutable-local-evidence-snapshot-id>"
    sha256: "<sha256-digest>"
    retention_locator: "<approved-retention-locator>"
  source_release_asset_applicability:
    release_asset_family: "<bounded-family>"
    version_applicability: "<specific-version-or-range>"
    parser_version: "<semantic-version>"
    source_contract_version: "<semantic-version>"
  intended_field_name: "<exact-raw-field-name>"
  intended_semantic_question: "<bounded-question>"
  evidence_statuses:
    value_meaning: "<documented|undocumented|conflicted|unknown>"
    null_behavior: "<documented|undocumented|conflicted|unknown>"
    attribution_behavior: "<documented|not_applicable|undocumented|conflicted|unknown>"
    correction_behavior: "<documented|undocumented|conflicted|unknown>"
    availability_behavior: "<documented|undocumented|conflicted|unknown>"
    conflict_status: "<none|unresolved|resolved-by-separate-decision>"
    time_integrity_status: "<pass|fail|not_run>"
  review:
    reviewer: "<reviewer>"
    architect_decision: "<not_approved|approved|rejected>"
    decision_timestamp: "<RFC3339 UTC timestamp-or-null>"
  limitations: ["<known-limitation>"]
  immutable_evidence_references: ["<evidence-reference>"]
```

## Future Individual Field-Semantic Authorization Record

An individual field semantic may be considered only through a future,
separately versioned decision record. This schema does not authorize or state
any semantic mapping.

```yaml
field_semantic_authorization_record:
  semantic_mapping_id: "<stable-versioned-semantic-mapping-id>"
  mapping_definition_version: "<semantic-version>"
  status: "candidate_only_not_approved_for_use"
  exact_raw_field_name: "<exact-raw-field-name>"
  source_family: "<source-family>"
  upstream_documentation_evidence_registration_id: "<evidence-registration-id>"
  upstream_immutable_version_pin: "<immutable-version-pin>"
  local_evidence_snapshot_id: "<immutable-local-evidence-snapshot-id>"
  local_evidence_sha256: "<sha256-digest>"
  release_asset_version_applicability: "<specific-release-asset-and-version-boundary>"
  declared_semantic_statement: "<bounded-semantic-statement>"
  declared_value_type_and_unit: "<declared-type-and-unit>"
  evidence_references:
    null_semantics: "<evidence-reference>"
    attribution_semantics: "<evidence-reference-or-not_applicable>"
    correction_behavior: "<evidence-reference>"
    observation_semantics: "<evidence-reference>"
    availability_semantics: "<evidence-reference>"
  source_record_grain: "<declared-grain>"
  known_limitations: ["<known-limitation>"]
  conflict_handling: "<preserve-conflict|quarantine|separately-approved-policy>"
  temporal_applicability: "<specific-time-boundary>"
  independent_acceptance_evidence: ["<evidence-reference>"]
  architect_decision: "<not_approved|approved|rejected>"
  effective_timestamp: "<RFC3339 UTC timestamp-or-null>"
  supersession_or_revision_reference: "<prior-or-successor-mapping-reference-or-null>"
```

## Version Applicability and Revision Boundary

Every future semantic claim is bounded to one exact raw field, one specific
upstream documentation version, one retained local evidence snapshot, one
release-asset applicability range, and one separately versioned mapping
decision. A semantic claim cannot transfer across upstream versions, seasons,
release-asset variants, parser versions, or source contracts without a recorded
applicability assessment.

A new upstream version or correction creates a new immutable evidence snapshot
and separately versioned mapping revision. It never rewrites prior evidence or
mappings.

## Evidence Sufficiency Gate

```yaml
individual_field_semantic_evidence_sufficiency_gate:
  required_conditions:
    - "Version-pinned upstream documentation identified by URL and immutable pin."
    - "Accessible upstream evidence and retained immutable local audit evidence."
    - "Documented value meaning and declared value type/unit."
    - "Documented null and missingness behavior."
    - "Documented attribution and ownership behavior where relevant."
    - "Documented correction and revision behavior."
    - "Declared source-record grain."
    - "Documented temporal availability and effective-time treatment."
    - "Confirmed release-asset and source-version applicability."
    - "Explicit conflict handling and known limitations."
    - "Independent acceptance evidence with falsifiable failure condition."
    - "Explicit Architect approval."
    - "No provider contamination."
  failure_rule: "Insufficient evidence creates no semantic mapping and no downstream consumer authorization."
```

Absent, stale, inaccessible, contradictory, unpinned, undocumented,
truncated, version-inapplicable, or otherwise insufficient evidence fails
closed. It cannot create a semantic mapping, normalized fact, canonical
mapping, feature, target, model, score, artifact, value, availability output,
optimizer result, board output, or recommendation.

## Structural Evidence Is Not Semantic Evidence

Raw parquet column names, type inspection, isolated records, inferred football
knowledge, screenshots, and downstream expected outputs can establish only a
candidate question or observed structure. They cannot establish field meaning,
attribution, ownership, null rules, correction behavior, or availability
behavior.

No individual field semantic is approved, no field list is selected, and no
event, player, team, game, play, or identity field is named as authoritative.
No event-target derivation is authorized. K and D/O remain separate capability
gaps; this contract implies no kicker or D/O field semantics, mapping, target,
or projection support.

## Provider-Contamination Prohibition

```yaml
provider_contamination_prohibition:
  applies_when: "projection_authority == apexos"
  prohibited_semantic_authority_or_supplement:
    - "Fantrax FPTs / FPts"
    - "Fantrax FP/G"
    - "Fantrax Rk / RkOv"
    - "Fantrax ADP"
    - "Fantrax Std / FA status"
    - "Fantrax Opp"
    - "Fantrax percentage fields"
    - "Fantrax Ros"
    - "Fantrax +/-"
    - "Any provider consensus, rank, fantasy forecast, analyst output, recommendation, status, opponent context, or UI signal"
  prohibited_uses:
    - "Raw-field meaning, null behavior, attribution, ownership, identity, timing, correction, transformation, or fallback behavior."
    - "Feature, target, model, scoring, artifact, availability, optimizer, board, rank, or recommendation input."
    - "Substitute for failed or missing semantic evidence."
  permitted_boundary:
    - "Explicitly labeled provider_snapshot mode with degraded provider authority."
    - "Display-only external comparison after independent ApexOS output is frozen."
    - "No provider field may enter ApexOS Projection Mode mathematics."
```

## Future Source-Evidence Workflow Boundary

```text
register semantic question
→ identify upstream version-pinned documentation
→ retain immutable local evidence snapshot
→ assess source/release applicability and temporal availability
→ independently validate evidence sufficiency
→ obtain separately versioned Architect semantic-mapping decision
→ only then permit a candidate normalized-fact definition
```

This contract authorizes none of those operational steps.

## Rejection and Degraded Behavior

```yaml
field_semantic_rejection_reason_codes:
  - "UPSTREAM_DOCUMENTATION_UNPINNED"
  - "UPSTREAM_DOCUMENTATION_UNAVAILABLE"
  - "UPSTREAM_DOCUMENTATION_VERSION_UNVERIFIED"
  - "LOCAL_EVIDENCE_SNAPSHOT_MISSING"
  - "LOCAL_EVIDENCE_DIGEST_MISSING"
  - "DOCUMENTATION_APPLICABILITY_UNCONFIRMED"
  - "RAW_FIELD_NAME_UNBOUND"
  - "FIELD_VALUE_SEMANTICS_UNDOCUMENTED"
  - "FIELD_NULL_SEMANTICS_UNDOCUMENTED"
  - "FIELD_ATTRIBUTION_SEMANTICS_UNDOCUMENTED"
  - "FIELD_CORRECTION_BEHAVIOR_UNDOCUMENTED"
  - "FIELD_AVAILABILITY_SEMANTICS_UNDOCUMENTED"
  - "FIELD_GRAIN_UNDECLARED"
  - "SEMANTIC_EVIDENCE_CONFLICT_UNRESOLVED"
  - "SEMANTIC_TIME_INTEGRITY_FAILED"
  - "INDEPENDENT_SEMANTIC_ACCEPTANCE_EVIDENCE_MISSING"
  - "ARCHITECT_SEMANTIC_DECISION_MISSING"
  - "PROVIDER_CONTAMINATION_DETECTED"
```

Degraded mode visibly reports evidence status, missing or failed authority
components, source-version applicability, data freshness, limitations,
retained evidence references, and reason codes. It preserves raw evidence and
unresolved semantic evidence separately, creates no false claim that a field
is semantically approved, never infers meaning, and does not substitute
Provider Snapshot Mode or provider output.

## Assumptions Register

| ID | Assumption / default | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-SEM-001 | No documentation source has yet been pinned or retained under this contract. | Future evidence collection | P0 if placeholders are treated as proof. | ApexOS Architect | Before evidence collection. |
| A-SEM-002 | No raw-field semantic is approved. | Future normalization | P0 if structural evidence becomes semantic authority. | ApexOS Architect | Before semantic mapping. |
| A-SEM-003 | Raw release assets are structural evidence only. | Raw-evidence boundary | P0 if inferred field meaning enters normalization. | ApexOS Architect / Builder | Immediate and ongoing. |
| A-SEM-004 | Upstream documentation revisions require new review and immutable evidence. | Semantic revision process | P1 if mappings are silently rewritten. | ApexOS Architect | Before applying any revision. |
| A-SEM-005 | Local retention is audit-only and cannot replace upstream authority. | Evidence retention | P0 if audit copies become source authority. | ApexOS Architect | Before approval. |
| A-SEM-006 | Provider data cannot fill semantic gaps. | ApexOS Projection Mode boundary | P0 if provider contamination enters semantics or identity. | ApexOS Architect / Builder | Immediate and ongoing. |
| A-SEM-007 | K and D/O remain unsupported capability gaps. | Entity and target design | P1 if this contract implies unsupported scope. | ApexOS Architect | Before K or D/O work. |
| A-SEM-008 | Source-availability semantics remain unverified until bounded field evaluation. | Temporal integrity | P0 if availability is inferred. | ApexOS Architect | Before field approval. |

## Acceptance Criteria

This contract is acceptable only when all criteria are true:

- Exactly one documentation-only file is added at the declared path.
- Upstream version-pinned documentation is semantic authority and immutable
  local retention is audit evidence only.
- Evidence-registration and future mapping-decision schemas contain no actual
  field, documentation, URL, version, snapshot, or semantic claim.
- Raw structure cannot become semantic, attribution, null, correction, or
  availability authority.
- Semantic applicability is pinned to upstream version, retained evidence,
  release-asset range, and separately versioned mapping decision.
- Fail-closed reason codes and visible degraded behavior are complete and no
  provider fallback exists.
- Provider influence is prohibited for raw-field semantics, identity,
  attribution, timing, transformation, and fallback behavior.
- K and D/O remain unsupported capability gaps.
- No retrieval, retention, parser, normalized-fact, identity, feature, target,
  model, scoring, artifact, board, optimizer, recommendation, test,
  configuration, dependency, or runtime change is authorized.
- The PR remains one-file, documentation-only, open, non-draft, and unmerged.

## Builder Handoff Boundary

This contract authorizes no source retrieval, documentation collection,
evidence retention, parser change, raw evidence processing, semantic mapping,
normalized-fact creation, canonical identity work, feature creation, target
extraction, model, evaluation, scoring, artifact, board, optimizer,
recommendation, test, configuration, dependency, external write, or merge.

A separately approved future handoff for evidence collection or mapping work
must identify an exact authorized upstream URL and immutable version pin,
rights or terms reference, retention destination, allowed paths, evidence
commands, acceptance criteria, stop conditions, and reviewer focus.

## Change Log

- `v0.1` — Structural contract introduced. Establishes the evidence-authority
  and retention gate after raw evidence and before source-field semantic
  mapping, normalized facts, or football-event target derivation.
