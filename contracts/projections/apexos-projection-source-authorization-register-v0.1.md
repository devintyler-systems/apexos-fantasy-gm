# ApexOS Projection Source Authorization Register v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-PROJECTION-SOURCE-AUTHORIZATION-REGISTER` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — contract-only review required before source retrieval or implementation |
| Change type | Structural |
| Canonical repository | `devintyler-systems/apexos-fantasy-gm` |
| Dependencies | `contracts/projections/apexos-projection-feature-and-score-lineage-contract-v0.1.md`; `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`; `docs/data_source_connector_register.md`; `contracts/league_rules/spamml-2026-v0.3.yaml`; `docs/decision_ledger.md` |
| Applies to | Future independent ApexOS football-event projection evidence; Redraft is the first implementation target |
| Implementation authorization | None. This register authorizes only bounded source-evaluation status. It does not authorize ingestion, feature use, model training, model calibration, projection generation, scoring changes, recommendation changes, or external writes. |

## Decision Statement

**Design decision:** Future ApexOS Projection Mode must use independently
sourced, time-valid football evidence governed by source-specific
authorization records. The initial authorized evidence boundary is direct
nflverse GitHub release-asset access for approved historical football-event
evidence, subject to the existing nflverse ingestion contract and all
source-, feature-, time-, identity-, scoring-, and acceptance gates.

**Design decision:** Provider-generated fantasy projections, fantasy-point
totals, ranks, ADP, consensus, recommendations, provider status,
opponent/schedule context, percentages, and UI signals are prohibited as
direct or indirect inputs to ApexOS Projection Mode. They may appear only
in explicitly labeled `provider_snapshot` mode or as display-only external
comparison context after independent ApexOS output is frozen.

**Confirmed evidence:** `nfl_data_py` is prohibited. nflverse direct GitHub
release assets are the approved access direction defined by the existing
nflverse ingestion contract. This register does not convert that approved
access direction into an approved feature set, event model, or projection
implementation.

## Scope and Explicit Non-Goals

### Scope

- Record the initial source authorization boundary for nflverse direct
  GitHub release assets.
- Define source authorization status, required provenance, temporal,
  identity, permissions, fallback, and degraded-mode fields.
- Explicitly prohibit provider-generated fantasy projection outputs from
  ApexOS Projection Mode.
- Record deferred sources as unapproved pending source-specific review.
- Define the gate between authorized raw evidence and future feature or
  football-event projection use.

### Explicit Non-Goals

- No source retrieval, source ingestion, source parsing, data storage, data
  transformation, fixture creation, or release-asset download is authorized.
- No player feature, team feature, event target, player estimate, model
  weight, event rate, formula, training target, calibration target, or
  model architecture is approved.
- No projection artifact, football-event projection, SPAMML scoring output,
  replacement value, availability model, roster-fit score, wait cost,
  scarcity, rank, or recommendation is created or changed.
- No source-rights claim is invented. Rights and terms must remain bound to
  the existing approved source-register and ingestion-contract references,
  with unresolved items explicitly gated.
- No provider projection, rank, ADP, consensus, recommendation, status,
  opponent/schedule context, percentage, or UI semantics are approved as
  ApexOS Projection Mode evidence.
- No current-provider synchronization, platform availability, or external
  write capability is created or implied.

## Authority Precedence

Source authorization does not override other ApexOS control boundaries.

```yaml
authority_precedence:
  - "Approved league rules engine and scoring contract"
  - "Approved projection feature and score lineage contract"
  - "Approved source-specific authorization record"
  - "Immutable raw-evidence snapshot and canonical identity mapping"
  - "Approved feature-promotion record and time-integrity evidence"
  - "Approved football-event model and deterministic SPAMML scoring trace"
  - "Decision adapter and recommendation contract"
  - "Display-only provider comparison context"
```

An authorized source may supply only the fields, entity scope, temporal
range, and bounded purpose explicitly recorded in its source record. Source
authorization never authorizes provider contamination, hidden fallback,
future-information use, or an ApexOS projection claim without a valid
versioned projection artifact.

## Source Authorization Statuses

```yaml
source_authorization_statuses:
  approved_bounded:
    meaning: "Eligible only for the explicit bounded purpose, fields, entity scope, and time-valid workflow recorded in the source record."
    implementation_effect: "Does not authorize ingestion, feature promotion, event-model use, or production output by itself."

  registered_reference_only:
    meaning: "Recorded for context or future evaluation; not approved as an ApexOS Projection Mode feature or model input."
    implementation_effect: "Display, research, or review only as separately permitted; no model, scoring, or recommendation use."

  prohibited:
    meaning: "May not supply any direct or indirect ApexOS Projection Mode input, target, calibration signal, or decision input."
    implementation_effect: "Reject any attempted ApexOS-mode use with PROVIDER_CONTAMINATION_DETECTED or SOURCE_AUTHORIZATION_FAILED."

  unknown_pending_review:
    meaning: "No authorization decision has been made because required source fields, rights, time availability, semantics, or evidence are incomplete."
    implementation_effect: "No ingestion or projection use. Preserve the unknown state and require explicit review."
```

## Authorized Source Record: nflverse Direct GitHub Release Assets

```yaml
source_authorization:
  source_id: "nflverse_direct_github_release_assets"
  status: "approved_bounded"
  source_provider_or_url: "nflverse/nflverse-data GitHub release assets"
  canonical_contract_reference: "contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md"
  source_register_reference: "docs/data_source_connector_register.md"

  bounded_purpose:
    - "Historical football-event evidence for future, separately approved ApexOS feature evaluation and football-event projection development."
    - "Reproducible immutable raw-evidence snapshot capture under the approved ingestion contract."
    - "Historical baseline and time-integrity evaluation where separately contracted."

  explicitly_not_authorized:
    - "Automatic creation of an ApexOS projection artifact."
    - "Use as a player feature, event target, model weight, training label, calibration target, or recommendation input before feature and model gates pass."
    - "Use of post-decision information."
    - "Provider-projection substitution, blending, calibration, or fallback."
    - "Current live platform availability or draft-state authority."
    - "External writes."

  access_method:
    approved: "Direct GitHub release-asset access"
    prohibited:
      - "nfl_data_py"
    implementation_note: "Any future retrieval implementation must conform to the referenced ingestion contract and must be separately authorized."

  entity_scope:
    eligible_evidence_entities:
      - "player"
      - "team"
      - "game"
      - "play"
    canonical_identity_requirement: "Map through approved canonical identity controls; unresolved or ambiguous identities must remain unresolved and must not be destructively merged."

  field_scope:
    approved_at_this_register_stage:
      - "Only fields expressly permitted by the referenced nflverse ingestion contract and a subsequent approved feature-promotion record."
    prohibited_at_this_register_stage:
      - "Any provider-generated fantasy-point total, rank, ADP, consensus, recommendation, status, opponent/schedule context, percentage, or UI signal."
      - "Any field unavailable on or before the declared decision as-of timestamp."
      - "Any field whose semantics, availability, source lineage, or transformation is unresolved."

  provenance_requirements:
    source_provider_or_url: "Required"
    source_id: "Required"
    retrieval_timestamp: "Required"
    effective_timestamp: "Required when available; otherwise explicitly null with limitation"
    availability_cutoff_timestamp: "Required before feature use"
    immutable_snapshot_id: "Required"
    parser_version: "Required"
    raw_asset_name_or_identifier: "Required"
    source_contract_version: "Required"
    rights_or_terms_reference: "Required"
    canonical_identity_mapping_status: "Required"

  temporal_integrity:
    rule: "A future ApexOS feature may use only evidence available on or before its declared availability cutoff and recommendation as-of timestamp."
    required_checks:
      - "Retrieval time retained."
      - "Effective time retained when available."
      - "Availability cutoff retained."
      - "Future-information test passed before feature promotion."
      - "Snapshot identity retained for replay."
    failure_behavior: "Reject affected ApexOS Projection Mode artifact with TIME_INTEGRITY_FAILED."

  terms_rights:
    status: "Bound to the referenced source register and ingestion contract; no new terms or rights claim is made by this register."
    gate: "A source-specific terms/rights reference must be retained in each immutable evidence snapshot before projection-feature use."

  authentication:
    status: "No new authentication claim is made by this register."
    gate: "Any future authenticated access requires explicit source-register review, secret-boundary definition, and separate approval."

  rate_limits:
    status: "No new rate-limit claim is made by this register."
    gate: "Any retrieval implementation must implement the approved ingestion contract's documented handling or stop pending explicit source review."

  freshness:
    status: "Historical evidence boundary only; no live-currentness claim."
    required_display_for_stale_or_historical_use: "Historical raw-evidence snapshot; not current platform state."
    gate: "Any current-season or live-decision use requires separately approved freshness policy, retrieval evidence, and degraded behavior."

  permissions:
    read_permission: "Bounded read-only retrieval only when separately implemented under the referenced ingestion contract."
    write_permission: "Prohibited unless separately approved."
    external_action_permission: "Prohibited."

  fallback_and_degraded_behavior:
    approved_fallback: "No provider-projection fallback."
    failure_rule: "ApexOS Projection Mode must reject rather than substitute provider points, provider ranks, provider ADP, or other provider-generated outputs."
    visible_reason_codes:
      - "SOURCE_AUTHORIZATION_FAILED"
      - "SOURCE_SNAPSHOT_MISSING"
      - "SOURCE_FRESHNESS_UNKNOWN"
      - "CANONICAL_IDENTITY_UNRESOLVED"
      - "TIME_INTEGRITY_FAILED"
    safe_behavior:
      - "Retain last valid immutable evidence artifact only when its provenance and staleness are visible."
      - "Do not claim current provider state, current availability, or live synchronization."
      - "Require explicit mode selection for Provider Snapshot Mode; never silently downgrade."
```

### nflverse Authorization Limits

- **Design decision:** `approved_bounded` means eligible for future
  evidence evaluation only. It is not an approval of all nflverse fields,
  all data products, all time periods, or all implementation methods.
- **Confirmed evidence:** Direct GitHub release-asset access is the approved
  nflverse direction. `nfl_data_py` remains prohibited.
- **Unknown:** Exact feature-level field selection, event-target definitions,
  source-rights interpretation for each future use, current-season asset
  availability, retrieval cadence, and freshness thresholds remain separate
  review gates.
- **Design decision:** A missing asset, unavailable period, unresolved
  schema, ambiguous identity, or time-invalid record must fail visibly and
  cannot trigger provider-projection substitution.

## Prohibited Source Record: Provider Projection Outputs

```yaml
source_authorization:
  source_id: "provider_generated_fantasy_projection_outputs"
  status: "prohibited"
  applies_when: "projection_authority == apexos"

  prohibited_direct_inputs:
    - "Fantrax FPTs / FPts"
    - "Fantrax FP/G"
    - "Fantrax Rk / RkOv"
    - "Fantrax ADP"
    - "Fantrax Std / FA status"
    - "Fantrax Opp"
    - "Fantrax %D"
    - "Fantrax Ros"
    - "Fantrax +/-"
    - "Any provider-generated player rank, fantasy point total, recommendation, or consensus output"
    - "Any provider UI icon, display label, or unexplained provider interface signal"

  prohibited_indirect_uses:
    - "Training target or label for ApexOS player fantasy-point projections"
    - "Calibration target for ApexOS football event rates or scoring outputs"
    - "Feature, weight, threshold, tie-breaker, replacement anchor, scarcity input, roster-fit input, wait-cost input, availability input, rank input, or recommendation input"
    - "Silent fallback when ApexOS artifact generation, validation, identity mapping, scoring reconciliation, source authorization, or time-integrity validation fails"

  permitted_uses:
    - "Explicit provider_snapshot mode with degraded status and mandatory provider-authority disclosure"
    - "Clearly labeled side-by-side external benchmark after the ApexOS model output is frozen"
    - "Display-only comparison context in apexos_projection mode"

  enforcement:
    - "The projection artifact schema must not accept provider-derived projection or rank fields as required ApexOS model inputs."
    - "The scoring engine must consume ApexOS football event outputs, never provider fantasy-point totals."
    - "The decision adapter must consume apexos_projected_score only in apexos_projection mode."
    - "Any detected provider-derived input in apexos_projection mode invalidates the artifact and emits PROVIDER_CONTAMINATION_DETECTED."
    - "Tests must prove changed provider FPTs, rank, or ADP cannot alter an apexos_projection-mode score, rank, replacement value, wait cost, scarcity, roster fit, availability outcome, or recommendation."
```

## Deferred Reference Sources

```yaml
deferred_reference_sources:
  sharp_football_analysis:
    status: "registered_reference_only"
    permitted_purpose: "2026 PPG context only, pending source-specific authorization."
    prohibited_purpose: "ApexOS Projection Mode feature, target, calibration, scoring, or recommendation input."
    required_next_gate: "Source authorization record with fields, rights, temporal availability, semantics, fallback, and acceptance evidence."

  vegasinsider:
    status: "registered_reference_only"
    permitted_purpose: "2026 win-total context only, pending source-specific authorization."
    prohibited_purpose: "ApexOS Projection Mode feature, target, calibration, scoring, or recommendation input."
    required_next_gate: "Source authorization record with fields, rights, temporal availability, semantics, fallback, and acceptance evidence."

  all_unlisted_sources:
    status: "unknown_pending_review"
    rule: "No source not explicitly authorized by a versioned source record may enter ApexOS Projection Mode."
```

## Source-to-Projection Boundary

```text
authorized raw evidence
→ immutable raw-evidence snapshot
→ normalized fact / canonical identity
→ separately approved feature-promotion record
→ separately approved ApexOS football-event model
→ deterministic ApexOS SPAMML scoring engine
→ immutable ApexOS projection artifact
→ decision adapter
→ recommendation
```

**Design decision:** Source authorization is necessary but insufficient for
an ApexOS projection. A source record cannot bypass canonical identity,
temporal integrity, feature promotion, event-model approval, scoring
reconciliation, uncertainty, known limitations, or decision-adapter
validation.

**Design decision:** Provider Snapshot Mode is a parallel, explicitly
labeled operational mode. It must not supply the raw-evidence, normalized
fact, feature, event-model, scoring, or recommendation inputs of
`apexos_projection` mode.

## Source Authorization Gate

A source may progress from `unknown_pending_review` or
`registered_reference_only` to `approved_bounded` only when a versioned
source record contains all required fields below and an Architect approves
the bounded use.

```yaml
source_authorization_gate:
  required_fields:
    - "source_provider_or_url"
    - "stable source_id"
    - "bounded purpose"
    - "entity scope"
    - "approved fields"
    - "prohibited fields or uses"
    - "terms or rights reference"
    - "authentication method and secret boundary"
    - "documented rate limits and handling policy"
    - "freshness cadence and stale-after policy"
    - "approved fallback and visible degraded behavior"
    - "retrieval timestamp and effective timestamp behavior"
    - "immutable snapshot ID and retention policy"
    - "parser version"
    - "canonical identity mapping method and ambiguity policy"
    - "read and write permissions"
    - "time-availability assessment"
    - "known limitations"
    - "independent acceptance evidence"

  mandatory_rejections:
    - "Provider-generated fantasy projection, rank, ADP, consensus, or recommendation proposed as an ApexOS Projection Mode input."
    - "Unresolved rights, field semantics, canonical identity, or temporal availability."
    - "No immutable snapshot or provenance chain."
    - "No visible degraded behavior or fallback policy."
    - "Any external write authority not separately approved."
    - "Any source use that would add post-decision information."
```

## Rejection and Degraded Behavior

**Design decision:** Failure to authorize, retrieve, validate, map, or
time-bound source evidence must be visible and must not produce a false
ApexOS Projection Mode claim.

```yaml
source_failure_behavior:
  rejection_reason_codes:
    - "SOURCE_AUTHORIZATION_FAILED"
    - "SOURCE_TERMS_OR_RIGHTS_UNRESOLVED"
    - "SOURCE_SNAPSHOT_MISSING"
    - "SOURCE_FRESHNESS_UNKNOWN"
    - "SOURCE_SCHEMA_UNRESOLVED"
    - "CANONICAL_IDENTITY_UNRESOLVED"
    - "TIME_INTEGRITY_FAILED"
    - "PROVIDER_CONTAMINATION_DETECTED"

  prohibited_recovery:
    - "Silent substitution of provider fantasy points, rank, ADP, consensus, or recommendation."
    - "Silent use of an unapproved source or field."
    - "Claiming live source freshness or platform availability without evidence."
    - "External write or automated fantasy action."

  safe_recovery:
    - "Retain an immutable last-valid evidence snapshot only with visible as-of time, source identity, freshness status, limitations, and reason code."
    - "Reject ApexOS Projection Mode when the required chain is incomplete."
    - "Allow only an explicit operator-selected Provider Snapshot Mode transition, with degraded banner, provider-authority disclosure, reason code, and new recommendation payload."
    - "Preserve failed source records and validation evidence for review."
```

## Assumptions Register

| ID | Assumption | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-SOURCE-001 | Direct nflverse GitHub release assets remain the approved access direction under the existing ingestion contract. | Future raw-evidence ingestion | P0 if implementation uses `nfl_data_py` or an unapproved access path. | ApexOS Architect / Builder | Before any retrieval implementation. |
| A-SOURCE-002 | No nflverse field is approved as a projection feature until it passes feature promotion. | Feature lineage and event projection | P0 if raw source access is mistaken for feature approval. | ApexOS Architect | Before feature implementation. |
| A-SOURCE-003 | Current-season availability, schema, cadence, and freshness policy are not established by this register. | Live or current-season decision workflow | P1 if historical evidence is displayed as current state. | ApexOS Architect | Before current-season use. |
| A-SOURCE-004 | Source rights and terms remain source-specific and must be retained through source-register references and immutable snapshots. | Evidence lineage | P0 if rights are inferred or lost. | ApexOS Architect | Before each source use. |
| A-SOURCE-005 | Sharp Football Analysis and VegasInsider remain reference-only, pending source-specific authorization. | External-context handling | P1 if reference context becomes a hidden model input. | ApexOS Architect | Before any Projection Mode use. |
| A-SOURCE-006 | Provider-generated projection outputs remain prohibited in ApexOS Projection Mode. | Projection, scoring, decision adapter, recommendation | P0 if provider output contaminates independent projections. | ApexOS Architect / Builder | Immediate and ongoing. |
| A-SOURCE-007 | D/O remains a separately scoped team-event capability requiring separate event and source review. | Team-event projection | P1 if D/O is forced into player-event assumptions. | ApexOS Architect | Before D/O implementation. |

## Acceptance Criteria

This register is acceptable only when all criteria are true:

- Exactly one source is recorded as `approved_bounded`:
  `nflverse_direct_github_release_assets`.
- nflverse authorization is explicitly limited to direct GitHub release-asset
  access, historical football-event evidence, immutable snapshots, and
  separately gated future feature or model work.
- `nfl_data_py` is explicitly prohibited.
- No provider-generated fantasy projection, fantasy-point total, rank, ADP,
  consensus, recommendation, status, opponent/schedule context, percentage,
  or UI signal is authorized as a direct or indirect ApexOS Projection Mode
  input.
- Provider data is permitted only in explicit `provider_snapshot` mode or
  post-freeze display-only comparison context.
- Sharp Football Analysis and VegasInsider remain
  `registered_reference_only`, with no ApexOS Projection Mode input
  authority.
- The register requires provider/URL, purpose, fields, rights, auth, rate
  limits, freshness, fallback, retrieval/effective times, snapshot ID,
  parser version, canonical identity mapping, read/write permissions,
  temporal availability, known limitations, and independent acceptance
  evidence before new source authorization.
- Failed authorization, retrieval, freshness, schema, identity, or temporal
  integrity is visibly rejected and cannot trigger a provider fallback.
- The document adds no player values, feature weights, event rates, model
  formulas, source-rights claims, ingestion code, artifact, test,
  configuration, or production behavior.
- The PR is documentation-only, one-file, open, non-draft, and unmerged.

## Builder Handoff Boundary

**Design decision:** This register does not authorize source implementation.
No Builder may retrieve, ingest, parse, transform, store, or use nflverse
data for an ApexOS Projection Mode feature, event target, model, scoring
output, or recommendation until a separate implementation handoff is
issued against the existing ingestion contract and all listed gates.

A future source-ingestion handoff must include:

- Approved source-record version and bounded field list.
- Clean canonical worktree outside the quarantined checkout.
- Exact release-asset selection and immutable snapshot manifest.
- Terms and rights reference retained with the snapshot.
- Retrieval, effective, and availability timestamps.
- Parser version, schema validation, malformed-record behavior, and
  retention policy.
- Canonical identity mapping behavior and unresolved-identity quarantine.
- Time-integrity controls preventing post-decision information.
- Read-only permissions and explicit prohibition of external writes.
- Fixture-backed acceptance tests, degraded behavior, and replay evidence.
- Explicit proof that provider fantasy projections, ranks, ADP, consensus,
  status, and UI signals cannot enter ApexOS Projection Mode.

## Change Log

- `v0.1` — Structural source-governance contract introduced. Records
  bounded nflverse direct GitHub release-asset authorization for historical
  football-event evidence; prohibits provider-generated fantasy outputs
  from ApexOS Projection Mode; preserves deferred references as
  non-authoritative; and blocks implementation pending separate ingestion,
  feature, event-model, scoring, and acceptance gates.
