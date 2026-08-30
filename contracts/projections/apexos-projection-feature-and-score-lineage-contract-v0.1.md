# ApexOS Projection Feature and Score Lineage Contract v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-PROJECTION-FEATURE-AND-SCORE-LINEAGE-CONTRACT` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — contract-only review required before implementation |
| Change type | Structural |
| Dependencies | `contracts/league_rules/spamml-2026-v0.3.yaml`; projection, scoring, optimizer, and recommendation contract families; `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`; `docs/data_source_connector_register.md`; `docs/decision_ledger.md`; PR #57 as read-only evidence only |
| Applies to | Redraft first implementation target; future supported modes must preserve the same authority and lineage boundary |
| Implementation authorization | None. This artifact is a documentation contract and does not authorize production implementation. |

## Decision Statement

**Design decision:** Independent ApexOS projections require the complete
`raw evidence → normalized fact / canonical identity → ApexOS football-event
projection → deterministic ApexOS SPAMML scoring engine → immutable ApexOS
projection artifact → decision adapter → recommendation` lineage.

Provider Snapshot Mode and ApexOS Projection Mode are mutually exclusive.
A provider point estimate may support only explicitly labeled
`provider_snapshot` mode. An ApexOS recommendation in `apexos_projection`
mode must consume an independently generated `apexos_projected_score` with
complete artifact, source, feature, identity, timestamp, uncertainty, and
scoring lineage.

**Confirmed evidence:** The current Fantrax marginal-value draft board is a
provider-snapshot decision board. Its displayed provider FPts must not be
described as an ApexOS projection, ApexOS projected points, ApexOS player
forecast, or independent ApexOS ranking.

## Scope and Explicit Non-Goals

### Scope

- Define mutually exclusive projection authority modes.
- Define the decision-adapter score-field cutover from
  `provider_projected_score` to `apexos_projected_score`.
- Define minimum immutable projection-artifact lineage.
- Prohibit direct and indirect provider contamination in
  `apexos_projection` mode.
- Preserve the separate boundaries among football-event projection,
  deterministic fantasy scoring, replacement value, availability model,
  roster-fit score, and recommendation.
- Define required future gates for source authorization and feature
  promotion.
- Define visible rejection and degraded-mode behavior when ApexOS
  projection lineage is incomplete or invalid.

### Explicit Non-Goals

- This contract does not create an independent ApexOS event model.
- This contract does not approve any player feature, player-specific score,
  player estimate, model weight, event rate, projection formula, source
  claim, source right, provider blend, source connector, or training label.
- This contract does not alter or relabel the frozen draft-day offline
  provider-snapshot board.
- This contract does not authorize production code, source adapters,
  scoring-engine changes, optimizer changes, data ingestion, artifact
  generation, test implementation, provider synchronization, or board
  regeneration.
- This contract does not force D/O team-event projections into the player
  artifact schema.
- This contract does not grant any external write authority.

## Projection Authority Modes

```yaml
projection_authority_modes:
  provider_snapshot:
    display_name: "Fantrax Provider Snapshot — ApexOS Decision Layer"
    projection_authority: "provider"
    point_estimate_field: "provider_projected_score"
    permitted_inputs:
      - "immutable user-provided provider snapshot"
      - "canonical identity mapping"
      - "league configuration"
      - "manual local availability state"
    permitted_outputs:
      - "provider-labeled projected-score display"
      - "ApexOS replacement value"
      - "ApexOS availability-aware recommendation"
      - "ApexOS roster-fit score"
      - "ApexOS wait-cost, scarcity, and suppression components"
    mandatory_disclosures:
      - "Provider projection, not an ApexOS projection."
      - "Degraded local snapshot; no current-provider synchronization claim."
      - "Manual availability is local-only and not platform-validated live state."
    prohibited_claims:
      - "ApexOS projection"
      - "ApexOS projected points"
      - "ApexOS player forecast"
      - "Independent ApexOS ranking"
    data_freshness_status: "degraded"

  apexos_projection:
    display_name: "ApexOS Projection-Backed Board"
    projection_authority: "apexos"
    point_estimate_field: "apexos_projected_score"
    mandatory_prerequisites:
      - "versioned ApexOS projection artifact"
      - "immutable raw-evidence snapshot references"
      - "canonical identity mapping"
      - "effective, retrieval, and as-of timestamps"
      - "versioned feature definitions and transformations"
      - "ApexOS football-event projection output"
      - "deterministic SPAMML scoring-engine conversion"
      - "uncertainty and known-limitations payload"
      - "time-integrity and baseline-comparison evidence"
    provider_data_rule:
      - "Provider projections may appear only as explicitly labeled comparison data."
      - "Provider projected points, ranks, and ADP must not supply the ApexOS point estimate."
      - "Provider values must not enter ApexOS recommendation math in apexos_projection mode."
    required_disclosures:
      - "ApexOS projection artifact ID and version."
      - "Projection as-of timestamp and input snapshot IDs."
      - "Scoring-engine version and league-rules version."
      - "Uncertainty, reason codes, data freshness, and known limitations."
```

## Decision Adapter Input and Cutover

```yaml
decision_adapter_projection_input:
  provider_snapshot_mode:
    required_projection_field: "provider_projected_score"
    required_projection_authority: "provider"
    required_data_freshness_status: "degraded"
    required_banner: "Fantrax Provider Snapshot — ApexOS Decision Layer"

  apexos_projection_mode:
    required_projection_field: "apexos_projected_score"
    required_projection_authority: "apexos"
    required_artifact_type: "apexos_projection_artifact"
    required_scoring_authority: "ApexOS SPAMML scoring engine"
    optional_provider_comparison_field: "provider_projected_score"
    provider_comparison_rule: "display-only; excluded from all decision calculations"

mode_selection_rule:
  - "The decision adapter must select exactly one authority mode for every recommendation."
  - "The selected mode and projection artifact ID must appear in the recommendation payload."
  - "The adapter must reject apexos_projection mode when required artifact lineage, scoring trace, timestamps, uncertainty, or known limitations are missing."
  - "The adapter must not silently fall back from apexos_projection mode to provider_snapshot mode."
  - "A fallback requires an explicit mode change, visible degraded banner, reason code, and a new recommendation payload."
```

## Required Lineage Schema

```json
{
  "projection_artifact_id": "apexos-spamml-2026-<immutable-run-id>",
  "projection_authority": "apexos",
  "projection_version": "<semantic-version>",
  "as_of_timestamp": "<RFC3339 UTC timestamp>",
  "input_snapshot_ids": [
    "<immutable-raw-evidence-snapshot-id>"
  ],
  "canonical_identity": {
    "entity_type": "player_or_team",
    "canonical_identity_id": "<stable-canonical-id>",
    "source_identity_mappings": [
      {
        "source_id": "<source-record-id>",
        "source_provider_or_url": "<provider-or-url>",
        "mapping_status": "resolved"
      }
    ]
  },
  "evidence_lineage": [
    {
      "source_provider_or_url": "<provider-or-url>",
      "source_id": "<source-record-id>",
      "retrieval_timestamp": "<RFC3339 UTC timestamp>",
      "effective_timestamp": "<RFC3339 UTC timestamp-or-null>",
      "snapshot_id": "<immutable-snapshot-id>",
      "parser_version": "<semantic-version>",
      "rights_or_terms_reference": "<approved-source-register-reference>"
    }
  ],
  "feature_lineage": [
    {
      "feature_id": "<versioned-feature-id>",
      "feature_definition_version": "<semantic-version>",
      "transformation_version": "<semantic-version>",
      "availability_cutoff_timestamp": "<RFC3339 UTC timestamp>",
      "missing_data_behavior": "<explicit-policy>",
      "future_information_check": "pass"
    }
  ],
  "football_event_projection": {
    "passing_touchdowns": null,
    "passing_two_point_conversions": null,
    "rushing_touchdowns": null,
    "rushing_two_point_conversions": null,
    "receiving_touchdowns": null,
    "receiving_two_point_conversions": null,
    "field_goals_made": null,
    "extra_points_made": null,
    "defensive_touchdowns": null,
    "special_teams_touchdowns": null,
    "safeties": null
  },
  "fantasy_scoring": {
    "scoring_authority": "ApexOS SPAMML scoring engine",
    "league_rules_version": "spamml-2026-v0.3",
    "scoring_engine_version": "<semantic-version>",
    "apexos_projected_score": null,
    "reconciliation_status": "pass"
  },
  "uncertainty": {
    "distribution_type": "<required-distribution-type>",
    "low": null,
    "median": null,
    "high": null,
    "confidence": null
  },
  "model_lineage": {
    "projection_model_version": "<semantic-version>",
    "parameter_set_version": "<immutable-parameter-set-id>",
    "run_id": "<immutable-run-id>"
  },
  "reason_codes": [],
  "known_limitations": [],
  "manual_override": {
    "model_output": null,
    "override_applied": false,
    "override_owner": null,
    "override_reason": null,
    "final_output": null
  }
}
```

## Provider-Contamination Prohibition

```yaml
no_provider_contamination_rule:
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

  prohibited_indirect_uses:
    - "Training target or label for ApexOS player fantasy-point projections"
    - "Calibration target for ApexOS event rates or scoring outputs"
    - "Feature, weight, threshold, tie-breaker, replacement anchor, scarcity input, roster-fit input, wait-cost input, availability input, or recommendation input"
    - "Silent fallback when ApexOS artifact generation, validation, identity mapping, or scoring reconciliation fails"

  permitted_uses:
    - "Clearly labeled side-by-side external benchmark after the ApexOS model output is frozen"
    - "Display-only comparison context in apexos_projection mode"
    - "Explicit provider_snapshot mode, with degraded status and mandatory provider-authority disclosure"

  enforcement:
    - "The projection artifact schema must not accept provider-derived projection or rank fields as required ApexOS model inputs."
    - "The scoring engine must consume ApexOS football event outputs, never provider fantasy-point totals."
    - "The decision adapter must consume apexos_projected_score only in apexos_projection mode."
    - "Tests must prove a changed provider FPTs/rank/ADP value cannot change an apexos_projection-mode score, rank, replacement value, wait cost, scarcity, roster fit, or recommendation."
    - "Any detected provider-derived input in apexos_projection mode invalidates the artifact and emits PROVIDER_CONTAMINATION_DETECTED."
```

## Screenshot Concept Disposition

### PROMOTE — architecture and decision concepts only

These are not approval for player weights, player scores, formulas, sources,
or production feature implementations:

```yaml
promote:
  - canonical identity
  - raw source position versus normalized league pool
  - separate recommendation output
  - replacement anchor and marginal replacement value
  - scarcity component
  - roster-fit score
  - specialist suppression
  - local/manual availability model
  - offline artifact boundary
  - visible degraded mode and provenance
```

### HOLD — no implementation authority yet

```yaml
hold:
  - provider FP/G
  - bye week
  - opponent/schedule context
  - provider status/FA
  - "%D"
  - Ros
  - "+/-"
  - provider UI icons
  - all screenshot-implied formulas, weights, player inputs, or ranking semantics
```

### REJECT — as ApexOS projection authority

```yaml
reject_as_apexos_projection_authority:
  - Fantrax FPTs / current board provider FPts
  - Fantrax rank / current board provider rank
  - Fantrax ADP
  - provider status, opponent, percentages, UI signals
  - any provider-generated point estimate, rank, recommendation, or consensus output
  - provider_points as an input to ApexOS Projection Mode
```

Provider data may appear only:

1. In explicitly labeled `provider_snapshot` mode; or
2. As post-freeze, display-only external comparison context after ApexOS
   output is generated independently.

Provider data may not be used as:

- Direct or indirect ApexOS event-model input.
- Target or training label.
- Calibration target.
- Score weight.
- Replacement value input.
- Scarcity, roster-fit, wait-cost, availability, rank, or recommendation
  input.
- Silent fallback when an ApexOS projection artifact fails.

## Entity and Event Modeling Boundary

**Design decision:** Projection artifact entity scope must match the football
event producer rather than force all positions into a player-only shape.

- QB, RB, and REC require player-event projection artifacts. Their event
  payloads must be limited to approved, versioned football-event definitions
  and must preserve canonical identity and time-valid evidence lineage.
- K requires kicker-event projection artifacts. Its event payloads must
  represent approved kicker events and must remain separate from player
  event assumptions that do not apply to kickers.
- D/O requires a separate team-event projection artifact. D/O must not be
  forced into the player schema. Team canonical identity, team-event
  evidence lineage, uncertainty, scoring reconciliation, and limitations
  must remain first-class fields.
- The general lineage structure may be shared where entity-safe, but
  implementation must preserve the `player_or_team` identity boundary and
  must not invent a completed D/O event formulation.
- **Assumption:** The detailed D/O formulation remains a distinct capability
  gap pending separately approved event definitions, source authorization,
  baseline evidence, and acceptance tests.

## Required Source Authorization Template

**Design decision:** A source becomes eligible for future independent
ApexOS projection work only after a source-specific authorization record is
approved and versioned in the source register. No generic source approval is
created by this contract.

```yaml
source_authorization_template:
  source_provider_or_url: "<provider-or-canonical-url>"
  source_id: "<stable-source-record-id>"
  purpose: "<bounded-projection-evidence-purpose>"
  approved_entity_scope:
    - "<player-or-team>"
  approved_fields:
    - "<field-name>"
  prohibited_fields_or_uses:
    - "<field-name-or-use>"
  terms_or_rights_reference: "<terms-license-or-register-reference>"
  authentication:
    method: "<none-or-approved-auth-method>"
    secret_handling: "<approved-secret-boundary>"
  rate_limits:
    documented_limit: "<limit-or-unknown>"
    handling_policy: "<backoff-cache-or-manual-policy>"
  freshness:
    expected_update_cadence: "<cadence-or-unknown>"
    stale_after: "<duration-or-explicit-policy>"
  fallback:
    approved_fallback: "<none-or-approved-source/artifact>"
    degraded_behavior: "<visible-banner-reason-code-and-safe-action>"
  temporal_lineage:
    retrieval_timestamp: "<RFC3339 UTC timestamp>"
    effective_timestamp: "<RFC3339 UTC timestamp-or-null>"
    availability_cutoff_timestamp: "<RFC3339 UTC timestamp>"
  immutable_snapshot:
    snapshot_id: "<immutable-snapshot-id>"
    retention_policy: "<approved-retention-policy>"
    parser_version: "<semantic-version>"
  canonical_identity_mapping:
    entity_type: "<player_or_team>"
    mapping_method: "<approved-mapping-method>"
    ambiguity_policy: "unresolved; do not destructively merge"
  permissions:
    read_permission: "<approved-read-only-or-other-explicit-boundary>"
    write_permission: "prohibited unless separately approved"
  approval:
    status: "<proposed-approved-prohibited>"
    approver: "<owner>"
    approval_timestamp: "<RFC3339 UTC timestamp-or-null>"
    known_limitations:
      - "<limitation>"
```

Required source authorization checks:

- The record must state provider or URL, bounded purpose, approved fields,
  terms or rights reference, authentication, rate limits, freshness,
  fallback, retrieval time, effective time, snapshot ID, parser version,
  canonical identity mapping, read/write permissions, and degraded behavior.
- A source whose rights, temporal availability, field semantics, or
  canonical identity reliability are unresolved cannot supply an ApexOS
  projection feature.
- Provider-generated projections, provider rankings, provider ADP, provider
  recommendations, provider consensus output, and provider UI semantics
  remain prohibited ApexOS Projection Mode inputs even if the provider is
  otherwise authorized for a different bounded purpose.
- External writes remain prohibited by default.

## Feature Promotion Gate

**Design decision:** A concept, field, or feature may not enter an ApexOS
football-event projection until it passes every gate below. Passing one gate
does not authorize production use until the complete feature record is
reviewed and approved.

```yaml
feature_promotion_gate:
  feature_id: "<versioned-feature-id>"
  definition:
    required: true
    requirement: "Plain-language and machine-readable definition with explicit unit, grain, and entity scope."
  causal_role:
    required: true
    requirement: "State the hypothesized causal or predictive role without converting correlation into asserted causality."
  entity_scope:
    required: true
    requirement: "Player, team, game, season, or other explicitly bounded entity scope."
  source:
    required: true
    requirement: "Approved source authorization reference and approved source fields."
  temporal_availability:
    required: true
    requirement: "Evidence the feature is available on or before the decision as-of timestamp."
  transformation:
    required: true
    requirement: "Versioned deterministic transformation and aggregation definition."
  missing_data_behavior:
    required: true
    requirement: "Explicit reject, impute, suppress, carry-forward, or degraded-mode policy."
  version:
    required: true
    requirement: "Feature-definition version and transformation version."
  uncertainty:
    required: true
    requirement: "Bounded uncertainty treatment and limitations."
  future_information_test:
    required: true
    requirement: "Pass a time-integrity test against the availability cutoff timestamp."
  baseline:
    required: true
    requirement: "Predeclared simple baseline and comparison method."
  acceptance_test:
    required: true
    requirement: "Independent reproducible acceptance test with failure condition."
  independent_evidence:
    required: true
    requirement: "Evidence independent of provider fantasy projections, ranks, ADP, consensus, or recommendation output."
```

Feature promotion requirements:

- No feature may be approved from a screenshot implication, provider UI
  label, unverified narrative, or player-specific intuition alone.
- The feature record must distinguish raw evidence, normalized facts,
  football-event projection inputs, fantasy-scoring outputs, and
  recommendation-layer fields.
- The feature must not use post-decision information, directly or through
  transformed or joined fields.
- The baseline comparison must be appropriate to the declared entity scope,
  projection horizon, and event target.
- Failed source authorization, identity resolution, temporal availability,
  transformation validation, baseline evidence, or acceptance testing
  blocks feature promotion.
- **Assumption:** No player features or numeric feature weights are approved
  by this v0.1 contract.

## Rejection and Degraded Behavior

**Design decision:** The decision adapter must reject invalid
`apexos_projection` inputs visibly and must never silently downgrade to
`provider_snapshot` mode.

The decision adapter must reject ApexOS Projection Mode and emit a visible
reason code when any required projection artifact field, lineage record, or
validation proof is absent, invalid, stale under its declared policy,
unresolved, or inconsistent.

Required rejection conditions include:

- Missing or invalid projection artifact ID, projection version, run ID, or
  immutable input snapshot ID.
- Missing, unresolved, or ambiguous canonical identity mapping.
- Missing retrieval, effective, as-of, or feature-availability timestamps.
- Failed future-information or time-integrity check.
- Missing versioned feature definition or transformation lineage.
- Missing ApexOS football-event projection payload.
- Missing deterministic SPAMML scoring trace, scoring-engine version,
  league-rules version, or scoring reconciliation pass.
- Missing uncertainty payload or known limitations.
- Detected provider-derived projection, rank, ADP, consensus,
  recommendation, status, opponent, percentage, or UI field in an
  ApexOS-mode model, scoring, or decision calculation.
- Missing baseline-comparison evidence where required by the active
  projection-model approval gate.

Minimum reason codes:

```yaml
apexos_projection_rejection_reason_codes:
  - "PROJECTION_ARTIFACT_LINEAGE_MISSING"
  - "CANONICAL_IDENTITY_UNRESOLVED"
  - "TIME_INTEGRITY_FAILED"
  - "FEATURE_LINEAGE_MISSING"
  - "EVENT_PROJECTION_MISSING"
  - "SCORING_RECONCILIATION_FAILED"
  - "UNCERTAINTY_MISSING"
  - "KNOWN_LIMITATIONS_MISSING"
  - "PROVIDER_CONTAMINATION_DETECTED"
  - "BASELINE_EVIDENCE_MISSING"
```

Safe behavior on rejection:

- Do not generate or display an ApexOS Projection Mode score, rank,
  replacement value, wait cost, scarcity component, roster-fit score, or
  recommendation as valid.
- Display the selected mode, visible rejection reason code, artifact
  identifier when present, timestamp status, and known safe next action.
- Retain the invalid artifact and validation evidence for review; do not
  overwrite it in place.
- A transition to `provider_snapshot` requires an explicit operator-selected
  mode change, the mandatory provider-snapshot degraded banner, reason code,
  and a newly generated recommendation payload.
- Manual availability remains local-only unless separately validated by an
  approved platform-state authority.
- No external write, draft action, waiver action, lineup action, trade
  action, or account change is permitted.

## Acceptance Criteria

This documentation contract is acceptable only when all criteria are true:

- Exactly one declared authority mode exists for every recommendation:
  `provider_snapshot` or `apexos_projection`.
- `apexos_projected_score` is defined as deriving only from a versioned
  ApexOS football-event projection and the deterministic ApexOS SPAMML
  scoring engine.
- `provider_projected_score` is the required projection field only in
  `provider_snapshot` mode.
- Provider projected points, ranks, ADP, status, opponent, percentages,
  consensus, recommendations, and UI signals are prohibited from
  ApexOS-mode model, score, replacement-value, availability, wait-cost,
  scarcity, roster-fit, ranking, and recommendation mathematics.
- The lineage schema requires complete artifact ID, authority, version,
  input snapshot, canonical identity, evidence, feature, time,
  event-projection, scoring, uncertainty, model, reason-code, limitation,
  and override fields.
- D/O remains explicitly capable of a separate team-event projection
  artifact and is not forced into a player-only schema.
- The contract adds no player-specific projection values, player weights,
  event rates, provider claims, source-rights claims, formulas, or
  production implementation.
- Future implementation tests must prove that changing provider
  FPTs/rank/ADP values cannot change an `apexos_projection`-mode score,
  rank, replacement value, wait cost, scarcity, roster fit, or
  recommendation.
- Future implementation tests must prove that missing lineage, scoring
  reconciliation, canonical identity, time integrity, uncertainty, or
  known limitations rejects ApexOS Projection Mode visibly.
- This PR remains one-file, documentation-only, open, non-draft, and
  unmerged with no production behavior change.

## Assumptions Register

| ID | Assumption | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-PROJ-001 | No player features or numeric player weights are approved. | Future event projection service | P0 if assumptions become hidden production defaults. | ApexOS Architect | Before feature implementation. |
| A-PROJ-002 | No independent ApexOS football-event model is implemented. | Projection artifact generation | P0 if provider snapshots are relabeled as ApexOS projections. | ApexOS Architect / Builder | Before ApexOS Projection Mode implementation. |
| A-PROJ-003 | D/O formulation remains a distinct team-event capability gap. | Team-event projection artifact and scoring path | P1 if D/O is forced into a player-only model. | ApexOS Architect | Before D/O projection implementation. |
| A-PROJ-004 | Source rights, field semantics, and temporal availability require source-specific authorization. | Ingestion and feature lineage | P0 if unapproved or time-invalid evidence enters projections. | ApexOS Architect | Before each source is used. |
| A-PROJ-005 | PR #57 is evidence only and is not a production projection artifact. | Evidence register and review process | P0 if screenshot evidence becomes model authority. | ApexOS Architect | Immediate and ongoing. |
| A-PROJ-006 | Current board remains a frozen offline provider-snapshot artifact through the immediate draft window. | Draft board operations | P0 if draft-day artifact behavior or labels change without a full validation gate. | ApexOS Architect / Operator | Until separately released. |

## Builder Handoff Boundary

**Design decision:** No production implementation is authorized by this
contract until it is reviewed and approved, and until source,
canonical-identity, feature-promotion, event-model, scoring, baseline,
time-integrity, and independent acceptance gates are separately passed.

Builder may not, based on this contract alone:

- Create or modify a production projection model.
- Ingest, approve, or blend a data source.
- Add a provider projection, rank, ADP, status, opponent, percentage,
  consensus, or UI field to an ApexOS Projection Mode input.
- Change the SPAMML scoring engine, league rules engine, optimizer,
  decision adapter, board, recommendation schema, or draft artifact.
- Generate an ApexOS projection artifact.
- Represent a provider snapshot as an independent ApexOS projection.
- Add or modify runtime tests as evidence of implementation completion.

Any future Builder handoff must name:

- The approved contract version and exact implementation boundary.
- A clean canonical worktree outside the quarantined checkout.
- Source authorization records and immutable raw-evidence snapshot IDs.
- Canonical identity mapping behavior and ambiguity handling.
- Approved feature definitions, temporal availability proofs, transformations,
  missing-data policies, and future-information tests.
- Football-event projection target definitions and deterministic scoring
  reconciliation.
- Projection artifact schema, run identity, uncertainty, known limitations,
  reason codes, and manual override separation.
- Baseline-comparison method and independent acceptance-test fixtures.
- Explicit provider-contamination tests proving provider changes cannot alter
  ApexOS Projection Mode output.
- Visible degraded-mode behavior, rollback path, and reviewer evidence.

## Change Log

- `v0.1` — Structural contract introduced. Establishes mutually exclusive
  projection authority modes; defines independent ApexOS event-to-score
  lineage; prohibits provider contamination; preserves D/O as a team-event
  capability; and blocks production implementation pending separate review
  and gate completion.
