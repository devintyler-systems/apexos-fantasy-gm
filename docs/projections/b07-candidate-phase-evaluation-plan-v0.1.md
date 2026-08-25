# B-07 Candidate-Phase Evaluation Plan v0.1

**Artifact:** B-07 Candidate-Phase Evaluation Plan
**Version:** 0.1
**Owner:** Architect
**Status:** Approved design — implementation blocked pending separate Architect-to-Codex handoff
**Dependencies:** B-07 v0.1 contract; baseline-only merge `19bfcdd7ebd4903cbf6b54363be3b4a0f313f58b`; retained baseline validation artifact `33e7463e2b06db536a75d90c3afe99c30be56536018225f8d8eb4d01af0546a5`
**Change type:** Structural

## 1. Decision statement

B-07 may evaluate one immutable, pre-registered candidate estimator after a separate implementation authorization. Candidate fitting, preprocessing fitting, feature selection, calibration definition, and tuning use 2023–2024 development data only. The final 2025 season is evaluation-only.

Candidate evidence is research validation only. It cannot create a production xTD artifact, current pointer, endpoint, recommendation, decision adapter, UI, API, or external write.

## 2. Scope and non-goals

### In scope

- Candidate registration requirements.
- Time-integrity controls.
- Candidate-vs-baseline evaluation requirements.
- Severe calibration promotion block.
- Immutable validation evidence and reviewer requirements.

### Explicit non-goals

- Selecting a candidate after observing 2025 outcomes.
- Candidate implementation, fitting, evaluation, or artifact generation.
- Production xTD promotion or recommendation behavior.
- B-06 mutation, new provider retrieval, or 2026 data work.
- Defining a distinct-game threshold for material-cohort calibration claims.

## 3. Frozen evidence boundary

```yaml
source_boundary:
  accepted_payload_sha256:
    "2023": "bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776"
    "2024": "3fd2896bc0b911b615142d2f1fabae54a4bbba5ab7b73b28187b118ef8af6a3b"
    "2025": "c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29"
  development_seasons: [2023, 2024]
  final_out_of_time_holdout: 2025
  holdout_fitting_access: false
  holdout_access_mode: "evaluation_only"
  raw_goal_to_go_required: true
  inferred_goal_to_go_prohibited: true
```

2025 must fail closed if requested for fitting, standardization fitting, imputation fitting, category/domain inference, feature selection, hyperparameter tuning, calibration-rail definition, candidate selection, or lookup/support-threshold construction.

## 4. Candidate controls

```yaml
candidate_registration:
  required_before_2025_label_access:
    - candidate_id
    - repository_commit_sha
    - estimator_family_and_version
    - dependency_lock_digest
    - exact_hyperparameters
    - deterministic_seed_policy
    - exact_feature_schema
    - exact_transformations
    - missingness_policy
    - calibration_policy
    - training_snapshot_id
    - candidate_artifact_schema
    - fail_closed_reason_codes
  immutable_after_registration: true
  change_behavior: >
    Any change to estimator, dependency, parameter, seed, feature,
    transformation, source identity, calibration policy, or evaluation
    protocol creates a new candidate_id and requires new Architect approval.
```

Candidate raw features may use only `yardline_100`, `down`, `ydstogo`, raw B-06 `goal_to_go`, `quarter`, `game_seconds_remaining`, and `score_differential`.

Candidate predictors must not include player/team IDs, player/team history, realized touchdown as a feature, yards gained, EPA, WPA, success, fantasy points, post-play scores, future data, season-end aggregates, shotgun, or no-huddle.

## 5. Evaluation and promotion gates

```yaml
evaluation_protocol:
  opportunity_types: [rush, pass_target]
  separate_candidate_outputs_required: true
  primary_populations: [rush, pass_target, combined]
  baseline_comparison:
    baseline_version: "b07-v0.1-contextual-baseline-1"
    requirement: "Candidate Brier must be strictly lower than frozen baseline Brier in every primary population."
  reliability:
    method: "equal_frequency_quantiles"
    requested_bins: 10
    report_per_population: true
  severe_calibration:
    ece_threshold: 0.015
    block_condition: "ECE > 0.015 in any primary population"
    failure_reason_code: "B07_CANDIDATE_SEVERE_CALIBRATION_FAILURE"
  uncertainty:
    method: "paired_bootstrap"
    cluster_unit: "game_id"
    resamples: 2000
    confidence_interval: 0.95
    required_outputs:
      - candidate_brier_confidence_interval
      - baseline_brier_confidence_interval
      - candidate_minus_baseline_brier_delta_confidence_interval
      - observed_minus_expected_touchdowns_confidence_interval
  cohorts:
    required:
      - opportunity_type
      - yardline_band
      - goal_to_go
      - down_when_support_eligible
    status: "diagnostic_only_distinct_game_threshold_undeclared"
    calibration_pass_claim_allowed: false
```

Candidate-phase evidence passes only when source, manifest, digest, identity, feature-contract, timing, and artifact checks pass; Brier improves strictly in all primary populations; ECE is at most 0.015 in all primary populations; required diagnostics are retained; and Architect plus Evidence & Release Reviewer issue PASS.

A candidate-phase PASS means `candidate_phase_evidence_accepted_only`. It does not authorize production promotion.

## 6. Required evidence package

Every candidate evaluation package must include candidate ID, code SHA, dependency-lock digest, deterministic seed policy, contract SHA, input snapshot ID, accepted source identities, `as_of_timestamp`, data freshness, feature schema, transformation record, separate rush/pass-target outputs, Brier, ECE, reliability, bootstrap, cohort, exclusion, uncertainty, and limitation evidence, immutable package digests, read-only inspection command, explicit no-current-pointer result, and false production/recommendation authorization flags.

## 7. Risks and unresolved decisions

- The initial candidate may not outperform the baseline; failure is an accepted, non-consumable result.
- A numeric material-cohort distinct-game threshold remains unresolved; cohorts remain diagnostic-only.
- A later structural decision is required before adding post-fit calibration.
- A future candidate implementation may not change B-06 or use 2026 data.

## 8. Builder handoff gate

No implementation begins until the Candidate Registration Record is merged and a separate Architect-to-Codex implementation handoff names one execution owner, exact allowed paths, commands, acceptance criteria, retained evidence, stop conditions, and reviewer focus.
