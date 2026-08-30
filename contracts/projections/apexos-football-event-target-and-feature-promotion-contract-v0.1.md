# ApexOS Football-Event Target and Feature Promotion Contract v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-FOOTBALL-EVENT-TARGET-AND-FEATURE-PROMOTION-CONTRACT` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — contract-only review required before feature evaluation or event-model implementation |
| Change type | Structural |
| Dependencies | Projection Feature and Score Lineage Contract v0.1; Projection Source Authorization Register v0.1; nflverse Authorization Reconciliation v0.1; nflverse Play-by-Play Ingestion Contract v0.2; nflverse Raw-Evidence Capture Runbook v0.1; SPAMML 2026 league-rules contract; Data Source Connector Register; Decision Ledger |
| Applies to | Future independent ApexOS Projection Mode; QB/RB/REC player-event target design; Redraft first implementation target |
| Implementation authorization | None. This contract does not authorize source retrieval, feature transformation, model development, football-event forecasting, scoring, artifact generation, decision-adapter changes, recommendations, or external writes. |

## Decision Statement

**Design decision:** An ApexOS projection begins with independently
sourced, time-valid football-event targets and independently promotable
feature records. A fantasy-point total is not a football-event target. A
provider fantasy-point total, rank, ADP, consensus, recommendation, or
provider UI signal is never an ApexOS target, feature, calibration target,
or decision input in `apexos_projection` mode.

**Design decision:** QB, RB, and REC future projections must begin with
player-event target families. Deterministic ApexOS SPAMML scoring may occur
only after a separately approved football-event projection artifact exists.
This contract defines no player forecast, target value, event rate, model
coefficient, feature weight, scoring formula, or projected score.

**Design decision:** A candidate feature is not promoted by plausibility,
screenshot appearance, source availability, or correlation alone. Promotion
requires a versioned definition, bounded causal or predictive role, source
authorization, time-availability proof, deterministic transformation,
missing-data policy, uncertainty treatment, baseline comparison, and
independent acceptance evidence.

## Scope and Explicit Non-Goals

### Scope

- Define a candidate feature-record schema for future historical football
  evidence evaluation.
- Define feature-promotion gates that preserve source lineage, canonical
  identity, temporal integrity, and independent evaluation.
- Define QB/RB/REC football-event target families at a semantic contract
  level.
- Define target grain, target availability, target cutoff, and target
  lineage requirements.
- Define rejection and degraded behavior when target or feature evidence is
  incomplete, ambiguous, contaminated, or time-invalid.
- Preserve the distinction between raw evidence, normalized facts,
  football-event targets, future event forecasts, deterministic fantasy
  scoring, replacement value, availability, and recommendation.

### Explicit Non-Goals

- No feature is approved for production use.
- No player-specific feature record, player-specific event target value,
  player estimate, event rate, model weight, threshold, formula, or
  projection is created.
- No provider projection, provider fantasy point total, provider rank, ADP,
  consensus, recommendation, status, opponent/schedule context, percentage,
  or UI signal is approved as a target, feature, calibration signal,
  training label, scoring input, or decision input.
- No target extraction, feature transformation, training dataset,
  calibration dataset, model implementation, backtest, or evaluation run is
  authorized.
- No scoring-engine change, projection artifact creation, decision-adapter
  cutover, replacement value, availability, optimizer, board, or
  recommendation behavior is authorized.
- No source authorization is broadened and no new source is approved.
- No D/O or K event model is defined by this contract. D/O remains a
  separate team-event capability; K remains a separate kicker-event
  capability.

## Authority and Layer Boundary

```text
approved source authorization
→ immutable raw-evidence snapshot
→ normalized fact / canonical identity
→ candidate feature record
→ separately approved promoted feature
→ football-event target definition
→ separately approved event-model implementation
→ ApexOS football-event projection
→ deterministic ApexOS SPAMML scoring engine
→ immutable ApexOS projection artifact
→ decision adapter
→ recommendation
```

The following terms are mutually distinct:

```yaml
layer_separation:
  raw_evidence: "Immutable source bytes and source metadata."
  normalized_fact: "Versioned interpreted fact with canonical identity and retained source lineage."
  candidate_feature: "A proposed time-valid model input not yet approved for production use."
  promoted_feature: "A candidate feature that passed all stated approval and evidence gates."
  football_event_target: "Observed historical football outcome at a declared entity grain and cutoff."
  football_event_projection: "Future forecast of a defined football event; not a fantasy score."
  fantasy_scoring: "Deterministic league-rules conversion of approved event projection outputs."
  projection_artifact: "Immutable ApexOS artifact carrying event, scoring, uncertainty, and lineage."
  provider_snapshot: "Explicitly labeled provider authority mode, separate from ApexOS Projection Mode."
  recommendation: "League-specific decision output; not a target or a projection."
```

## Candidate Feature Record Contract

```yaml
candidate_feature_record:
  feature_id: "<stable-versioned-feature-id>"
  feature_definition_version: "<semantic-version>"
  status: "candidate_only_not_approved_for_use"

  feature_name: "<human-readable-name>"
  entity_scope: "<player|team|game|play|player_game|team_game|player_season|team_season>"
  entity_grain: "<one-row-per-declared-entity-grain>"
  canonical_identity_requirements:
    canonical_identity_id: "<required-or-explicitly-not-applicable>"
    source_identity_mapping_status: "<resolved|unresolved|not_applicable>"
    ambiguity_behavior: "quarantine; do not guess or destructively merge"

  definition:
    unit: "<declared-unit>"
    time_window: "<explicit-lookback-or-point-in-time-window>"
    observation_cutoff_rule: "<must-be-at-or-before-as-of>"
    proposed_predictive_role: "<bounded-hypothesis-not-asserted-causality>"
    prohibited_interpretations:
      - "No provider fantasy-point, rank, ADP, consensus, recommendation, status, or UI semantics."
      - "No post-decision information."
      - "No use as an implicit projection, score, or recommendation."

  source_lineage:
    source_authorization_record: "<approved-source-register-reference>"
    input_snapshot_ids:
      - "<immutable-raw-evidence-snapshot-id>"
    source_provider_or_url: "<provider-or-url>"
    source_ids:
      - "<source-record-id>"
    retrieval_timestamp: "<RFC3339 UTC timestamp>"
    effective_timestamp: "<RFC3339 UTC timestamp-or-null>"
    parser_version: "<semantic-version>"
    rights_or_terms_reference: "<approved-source-register-reference>"

  temporal_integrity:
    as_of_timestamp: "<RFC3339 UTC timestamp>"
    availability_cutoff_timestamp: "<RFC3339 UTC timestamp>"
    future_information_check: "<pass|fail|not_run>"
    retrospective_use_rule: "Historical feature values must be reconstructable using only evidence available at the declared cutoff."

  transformation:
    transformation_version: "<semantic-version>"
    deterministic_transformation_description: "<bounded-versioned-description>"
    input_field_inventory:
      - "<approved-normalized-field-id>"
    output_type: "<numeric|categorical|boolean|distribution|other>"
    missing_data_behavior: "<reject|quarantine|explicit-imputation-policy|suppress>"
    conflict_behavior: "<preserve-conflict|quarantine|other-explicit-policy>"

  uncertainty_and_limitations:
    uncertainty_treatment: "<required-explicit-policy>"
    known_limitations:
      - "<known-limitation>"
    data_freshness_status: "<historical_snapshot|other-approved-status>"

  evaluation_gate:
    baseline_definition: "<predeclared-simple-baseline>"
    comparison_metric: "<predeclared-metric>"
    evaluation_window: "<time-valid-historical-window>"
    independent_acceptance_test: "<test-id-or-contract-reference>"
    promotion_decision: "<not_approved|approved|rejected>"
    promotion_owner: "<owner>"
    promotion_timestamp: "<RFC3339 UTC timestamp-or-null>"
```

A candidate feature record is valid only when its source, entity grain,
identity handling, cutoff rule, transformations, missing-data behavior,
limitations, and evaluation plan are explicit. A candidate record cannot be
consumed by an event model, scoring engine, optimizer, or recommendation
service.

## Feature Promotion Gate

```yaml
feature_promotion_gate:
  required_conditions:
    - "Stable feature ID and versioned definition."
    - "Declared entity scope, unit, and row grain."
    - "Bounded predictive role stated as a hypothesis, not asserted causality."
    - "Approved source authorization and immutable input snapshot IDs."
    - "Canonical identity mapping or explicit not-applicable entity boundary."
    - "Retrieval, effective when available, as-of, and availability-cutoff timestamps."
    - "Pass future-information check proving evidence existed no later than the cutoff."
    - "Versioned deterministic transformation with complete approved input-field inventory."
    - "Explicit missing-data and conflicting-data behavior."
    - "Explicit uncertainty treatment and known limitations."
    - "Predeclared simple baseline, comparison metric, and time-valid evaluation window."
    - "Independent acceptance test with a falsifiable failure condition."
    - "Architect promotion decision recorded separately from model output."

  mandatory_rejections:
    - "Provider fantasy-point total, provider projection, rank, ADP, consensus, recommendation, status, schedule-context semantic, percentage, or UI signal proposed as a feature or target."
    - "Missing immutable snapshot ID, provenance, source authorization, parser version, or terms reference."
    - "Ambiguous identity represented as resolved or silently merged."
    - "Evidence available after the feature availability cutoff."
    - "Transformation, unit, time window, or input-field inventory not versioned."
    - "Missing-data policy, limitations, baseline, or independent acceptance test absent."
    - "A candidate feature presented as approved without the complete promotion decision."
```

## QB/RB/REC Football-Event Target Contract

**Design decision:** QB, RB, and REC target contracts define historical
observed football events. They do not define fantasy scoring, point
projections, position rankings, target event rates, or player values.

```yaml
football_event_target_contract:
  target_record_common:
    target_id: "<stable-versioned-target-id>"
    target_definition_version: "<semantic-version>"
    target_status: "candidate_only_not_approved_for_event-model-use"
    position_pool: "<QB|RB|REC>"
    canonical_player_identity_id: "<stable-canonical-player-id>"
    target_grain: "player-season unless separately versioned"
    observation_window:
      start_timestamp: "<RFC3339 UTC timestamp>"
      end_timestamp: "<RFC3339 UTC timestamp>"
      availability_cutoff_timestamp: "<RFC3339 UTC timestamp>"
    evidence_lineage:
      input_snapshot_ids:
        - "<immutable-raw-evidence-snapshot-id>"
      source_authorization_record: "<approved-source-register-reference>"
      parser_version: "<semantic-version>"
      normalized_fact_version: "<semantic-version>"
    target_integrity:
      post_decision_information_check: "<pass|fail|not_run>"
      canonical_identity_mapping_status: "<resolved|unresolved>"
      missing_data_behavior: "<reject|quarantine|explicit-policy>"
      conflict_behavior: "<preserve-conflict|quarantine|explicit-policy>"
    uncertainty_and_limitations:
      known_limitations:
        - "<known-limitation>"
    prohibited_output:
      - "Fantasy-point target."
      - "Provider projection target."
      - "Provider rank or ADP target."
      - "Player value, replacement value, availability, or recommendation target."

  qb_player_event_targets:
    - "passing_touchdowns"
    - "passing_two_point_conversions"
    - "rushing_touchdowns"
    - "rushing_two_point_conversions"

  rb_player_event_targets:
    - "rushing_touchdowns"
    - "rushing_two_point_conversions"
    - "receiving_touchdowns"
    - "receiving_two_point_conversions"

  rec_player_event_targets:
    - "receiving_touchdowns"
    - "receiving_two_point_conversions"
    - "rushing_touchdowns"
    - "rushing_two_point_conversions"
```

Target-family inclusion is not event-model approval. Each future target
must separately define its observed-event derivation from approved
normalized facts, source field lineage, historical observation window,
identity handling, missing/conflict behavior, cutoff proof, and independent
acceptance test.

## Target Availability and Time-Integrity Rules

- Historical target observation time and target availability time must be
  retained separately where they differ.
- A target record used for retrospective evaluation must be assembled only
  from source evidence that existed on or before the declared availability
  cutoff for the corresponding historical decision point.
- Event outcomes may be used as historical targets only within a declared
  historical evaluation design. They may not be joined into a feature row as
  post-decision information.
- A target or feature with missing source lineage, unknown availability,
  failed timestamp ordering, or failed future-information test must be
  rejected from candidate promotion and future model use.
- A later source correction must create a new immutable snapshot and
  versioned normalized fact; it must not overwrite prior target lineage.

## Entity Grain and Canonical Identity Boundary

- QB, RB, and REC event targets are player-event records. A target record
  must retain a stable canonical player identity, source identity mapping,
  source-team context where available, season/window grain, and source
  snapshots.
- The target entity grain is `player-season` by default for this contract.
  Any player-game, player-week, rolling-window, team-season, or
  game-context target requires a separately versioned target definition and
  time-availability assessment.
- Unresolved player identity, ambiguous alias, team-history conflict, or
  source identity collision must be quarantined. It cannot be normalized
  through name guessing, provider rank, ADP, or player-score similarity.
- D/O remains a team-event capability gap. K remains a kicker-event
  capability gap. Neither may be coerced into QB/RB/REC player-event
  targets.

## Provider-Contamination Prohibition

```yaml
provider_contamination_prohibition:
  applies_when: "projection_authority == apexos"

  prohibited_as_feature_target_or_evaluation_authority:
    - "Fantrax FPTs / FPts"
    - "Fantrax FP/G"
    - "Fantrax Rk / RkOv"
    - "Fantrax ADP"
    - "Fantrax Std / FA status"
    - "Fantrax Opp"
    - "Fantrax %D"
    - "Fantrax Ros"
    - "Fantrax +/-"
    - "Any provider-generated player rank, fantasy point total, recommendation, consensus output, analyst projection, or UI signal"

  prohibited_indirect_use:
    - "Training label or calibration target for football-event targets or event projections."
    - "Feature, weight, threshold, tie-breaker, target construction input, replacement anchor, availability input, scarcity input, roster-fit input, wait-cost input, rank input, or recommendation input."
    - "Silent fallback when source capture, canonical identity, feature promotion, target integrity, model validation, or scoring reconciliation fails."

  permitted_provider_boundary:
    - "Explicitly labeled provider_snapshot mode with degraded provider authority."
    - "Display-only external benchmark after independent ApexOS model output is frozen."
    - "No provider field may enter ApexOS Projection Mode mathematics."
```

## Baseline and Independent Evaluation Gate

**Design decision:** Feature and target promotion requires a predeclared
baseline and independent evidence. A complex candidate cannot be accepted
merely because it is plausible or improves an in-sample narrative.

```yaml
evaluation_gate:
  pre_registration:
    target_definition_version: "<semantic-version>"
    candidate_feature_ids:
      - "<feature-id>"
    historical_window: "<time-valid-window>"
    split_policy: "<chronological-or-other-time-valid-policy>"
    baseline:
      definition: "<simple-deterministic-baseline>"
      version: "<semantic-version>"
    metric:
      name: "<metric-name>"
      direction: "<higher-is-better|lower-is-better>"
    leakage_controls:
      - "Feature availability cutoff enforced."
      - "No post-decision information."
      - "No provider projection, rank, ADP, consensus, or recommendation data."
    acceptance_test:
      test_id: "<independent-test-id>"
      failure_condition: "<falsifiable-failure-condition>"
    decision:
      status: "<not_run|pass|fail>"
      owner: "<owner>"
      evidence_artifact_ids:
        - "<immutable-evidence-id>"
```

No baseline, evaluation metric, historical split policy, or feature/model
performance threshold is set by this contract.

## Rejection and Degraded Behavior

Candidate feature or target evaluation must fail visibly and must not create
an ApexOS projection, fantasy score, rank, or recommendation when any of
the following occurs:

```yaml
feature_target_rejection_reason_codes:
  - "SOURCE_AUTHORIZATION_FAILED"
  - "SOURCE_SNAPSHOT_MISSING"
  - "CANONICAL_IDENTITY_UNRESOLVED"
  - "FEATURE_DEFINITION_INCOMPLETE"
  - "FEATURE_TRANSFORMATION_UNVERSIONED"
  - "FEATURE_AVAILABILITY_UNKNOWN"
  - "TARGET_DEFINITION_INCOMPLETE"
  - "TARGET_LINEAGE_MISSING"
  - "TARGET_TIME_INTEGRITY_FAILED"
  - "POST_DECISION_INFORMATION_DETECTED"
  - "MISSING_DATA_POLICY_UNDECLARED"
  - "BASELINE_EVIDENCE_MISSING"
  - "INDEPENDENT_ACCEPTANCE_EVIDENCE_MISSING"
  - "PROVIDER_CONTAMINATION_DETECTED"
```

Safe behavior:

- Retain raw evidence, normalized facts, candidate records, validation
  results, and rejection reason codes separately.
- Do not overwrite prior snapshots, target lineage, or candidate evidence.
- Quarantine unresolved identities and preserve source conflicts.
- Display candidate-only status, data freshness, limitations, and reason
  codes.
- Do not silently substitute a provider projection or Provider Snapshot
  Mode result.
- Require explicit operator mode selection to use any separate
  `provider_snapshot` output.

## Assumptions Register

| ID | Assumption | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-FEATURE-001 | No historical feature is approved for production use by this contract. | Future feature pipeline | P0 if candidate definitions become hidden model inputs. | ApexOS Architect | Before feature implementation. |
| A-FEATURE-002 | QB/RB/REC event families are semantic candidate targets only; observed-event derivations remain separately versioned and tested. | Future event-target extraction | P0 if target names become unvalidated extraction logic. | ApexOS Architect / Builder | Before target extraction. |
| A-FEATURE-003 | The default player-season grain may not be generalized to player-game, player-week, rolling-window, or team-context targets without a separate temporal design. | Historical evaluation | P1 if mixed grains introduce leakage or duplicate counting. | ApexOS Architect | Before alternate-grain modeling. |
| A-FEATURE-004 | No provider fantasy output may enter ApexOS Projection Mode feature, target, calibration, scoring, or recommendation math. | Projection program | P0 if the independent projection boundary is breached. | ApexOS Architect / Builder | Immediate and ongoing. |
| A-FEATURE-005 | D/O and K remain distinct target-formulation capability gaps. | Team-event and kicker-event projection design | P1 if unsupported entities are forced into player-event assumptions. | ApexOS Architect | Before D/O or K implementation. |
| A-FEATURE-006 | Source rights, field semantics, target availability, and historical asset coverage remain source-specific approval gates. | Source and target lineage | P0 if claims are inferred from raw-capture capability. | ApexOS Architect | Before source/feature promotion. |

## Acceptance Criteria

This contract is acceptable only when all criteria are true:

- Exactly one documentation-only contract file is added.
- The contract declares football-event targets as distinct from fantasy
  scoring, provider projections, rankings, replacement value, availability,
  and recommendations.
- The candidate feature-record contract requires source authorization,
  immutable snapshot lineage, canonical identity handling, as-of and
  availability timestamps, deterministic transformation version,
  missing/conflict behavior, uncertainty, baseline, and independent
  acceptance evidence.
- The feature-promotion gate explicitly rejects incomplete lineage,
  unresolved identity, future information, unversioned transformation,
  missing policy, absent baseline, absent independent acceptance evidence,
  and provider contamination.
- QB, RB, and REC semantic football-event target families are defined with
  no target values, event rates, player estimates, weights, formulas, or
  scoring outputs.
- QB/RB/REC default target grain is explicit and alternative grains require
  separate versioned definitions.
- D/O and K are explicitly out of scope and preserved as separate
  capability gaps.
- Provider fantasy-point totals, projections, ranks, ADP, consensus,
  recommendations, statuses, context, percentages, and UI signals are
  prohibited as direct and indirect ApexOS Projection Mode feature/target/
  evaluation authority.
- Rejection behavior is visible, reason-coded, non-destructive, and cannot
  silently fall back to Provider Snapshot Mode.
- No production code, tests, fixtures, sources, data capture, player data,
  projection artifact, scoring output, decision behavior, dependency, or
  external write is introduced.
- The PR is one-file, documentation-only, open, non-draft, and unmerged.

## Builder Handoff Boundary

This contract does not authorize implementation.

Before a Builder may implement any target extraction, candidate feature
transformation, feature-promotion evaluator, model, or historical
evaluation, a separate implementation handoff must identify:

- The approved target definition version and one declared entity grain.
- The exact source authorization record and immutable raw-evidence snapshot
  manifest(s).
- The explicit source field inventory, normalized-fact contract, and
  canonical identity mapping/ambiguity behavior.
- The target observation window and feature availability-cutoff proof.
- The deterministic transformation and missing/conflict behavior.
- The predeclared baseline, chronological evaluation split, metric, and
  independent acceptance test.
- Provider-contamination negative tests.
- Degraded mode, rejection reason codes, rollback, and evidence-retention
  behavior.

No Builder may create an ApexOS projected score, football-event forecast,
fantasy-scoring result, rank, replacement value, availability output, or
recommendation based on this contract alone.

## Change Log

- `v0.1` — Structural contract introduced. Defines the candidate
  feature-record and QB/RB/REC football-event target boundaries required
  before independent ApexOS feature promotion or event-model
  implementation. Preserves source lineage, canonical identity, time
  integrity, provider-contamination prohibition, baseline comparison, and
  fail-closed behavior.
