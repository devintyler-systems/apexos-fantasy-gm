# B-07 Candidate Registration Record v0.1

**Artifact:** B-07 Candidate Registration Record
**Version:** 0.1
**Owner:** Architect
**Status:** Registered — not implemented, fitted, evaluated, or production-authorized
**Dependencies:** B-07 Candidate-Phase Evaluation Plan v0.1; B-07 v0.1 contract; baseline-only merge `19bfcdd7ebd4903cbf6b54363be3b4a0f313f58b`
**Change type:** Structural

## 1. Decision statement

The first B-07 candidate is L2-regularized binary logistic regression, separately fit for `rush` and `pass_target`. The registration freezes the estimator, parameters, development-only preprocessing, feature schema, holdout controls, and promotion criteria before any candidate evaluation.

This record does not authorize candidate code, fitting, 2025 evaluation, candidate artifact creation, production xTD output, current pointer, endpoint, recommendation, UI, API, or external write.

## 2. Registered candidate

```yaml
candidate_id: "b07-v0.1-l2-logit-separate-opportunity-types-1"
status: "registered_not_implemented"

binding_baseline:
  repository_sha: "19bfcdd7ebd4903cbf6b54363be3b4a0f313f58b"
  contract_path: "contracts/projections/b07_v0_1_contract.yaml"
  contract_sha256: "7cd8e294ca1b6fefadb1d35472e9a421c4829dd6f37dc6690abf2513b9da0abc"
  baseline_version: "b07-v0.1-contextual-baseline-1"
  baseline_validation_artifact_sha256: "33e7463e2b06db536a75d90c3afe99c30be56536018225f8d8eb4d01af0546a5"

source_boundary:
  development_seasons: [2023, 2024]
  final_out_of_time_holdout: 2025
  holdout_fitting_access: false
  accepted_payload_sha256:
    "2023": "bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776"
    "2024": "3fd2896bc0b911b615142d2f1fabae54a4bbba5ab7b73b28187b118ef8af6a3b"
    "2025": "c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29"

models:
  rush:
    estimator: "L2-regularized binary logistic regression"
    target: "raw_b06_rush_touchdown"
  pass_target:
    estimator: "L2-regularized binary logistic regression"
    target: "raw_b06_pass_touchdown"
  pooling_between_opportunity_types: "prohibited"

implementation:
  library: "scikit-learn"
  required_version: "1.6.1"
  estimator: "sklearn.linear_model.LogisticRegression"
  solver: "lbfgs"
  penalty: "l2"
  C: 1.0
  fit_intercept: true
  class_weight: null
  max_iter: 1000
  tolerance: 0.00000001
  random_state: 20260825
  post_fit_calibration: "prohibited"

features:
  numeric:
    - yardline_100
    - ydstogo
    - quarter
    - game_seconds_remaining
    - score_differential
  categorical:
    down:
      encoding: "one_hot"
      fixed_domain: [1, 2, 3, 4]
  binary:
    goal_to_go:
      source: "raw_b06_goal_to_go"
      encoding: "false_0_true_1"
  numeric_transformation: "development_fit_z_score"
  imputation: "prohibited"
  interactions: "prohibited"
  polynomial_features: "prohibited"
  feature_selection: "prohibited"
  dimensionality_reduction: "prohibited"
  target_encoding: "prohibited"

prohibited_predictors:
  - player_id
  - team_id
  - player_history
  - team_history
  - realized_touchdown_as_feature
  - yards_gained
  - epa
  - wpa
  - success
  - fantasy_points
  - post_play_scores
  - future_data
  - season_end_aggregates
  - shotgun
  - no_huddle

fail_closed_reason_codes:
  - B07_CANDIDATE_FEATURE_MISSING
  - B07_CANDIDATE_FEATURE_OUT_OF_DOMAIN
  - B07_CANDIDATE_ZERO_VARIANCE_NUMERIC_FEATURE
  - B07_CANDIDATE_FEATURE_SCHEMA_MISMATCH
  - B07_CANDIDATE_PROHIBITED_FEATURE_PRESENT
  - B07_CANDIDATE_SEVERE_CALIBRATION_FAILURE

evaluation:
  primary_populations: [rush, pass_target, combined]
  candidate_brier_requirement: "strictly_lower_than_frozen_baseline_for_every_primary_population"
  reliability_bins: 10
  severe_calibration_ece_threshold: 0.015
  bootstrap:
    method: "paired_bootstrap"
    cluster_unit: "game_id"
    resamples: 2000
    confidence_interval: 0.95

production_boundary:
  candidate_artifact_kind: "immutable_local_candidate_validation_package"
  production_promotion_authorized: false
  current_pointer_created: false
  endpoint_authorized: false
  recommendation_behavior_authorized: false
```

## 3. User and system flow

1. Codex confirms local compatibility of the registered dependency without changing dependencies.
2. Architect issues a separate bounded implementation handoff.
3. Codex implements the exact registration without substitutions.
4. All 2023–2024 preprocessing and fitting complete before 2025 label access.
5. A locked candidate is evaluated once on 2025.
6. Architect and Evidence & Release Reviewer audit immutable evidence.
7. Candidate evidence may be accepted or rejected; production remains separately gated.

## 4. Acceptance criteria

- `rush` and `pass_target` have separate fitted estimators.
- Standardization statistics use eligible 2023–2024 events only.
- `down` uses fixed domain `[1, 2, 3, 4]` and cannot infer categories from 2025.
- Missing, invalid, prohibited, or zero-variance features fail closed with a registered reason code.
- Any configuration difference invalidates this candidate ID and requires a new registration.
- A candidate cannot pass if 2025 enters fitting, preprocessing fitting, domain inference, feature selection, calibration, tuning, or candidate selection.
- Promotion is blocked if ECE exceeds 0.015 in rush, pass target, or combined output.
- A candidate-phase PASS remains non-production.

## 5. Risks and assumptions

- `C=1.0` is fixed and may not be tuned against 2025.
- No post-fit calibration is permitted; calibration quality is evaluated through reliability and ECE diagnostics.
- The candidate may not outperform the baseline; that is a valid failure result.
- Material cohorts remain diagnostic-only until a distinct-game support threshold is frozen.
- `scikit-learn==1.6.1` must be confirmed against the local dependency environment before implementation. A compatibility conflict is a stop condition, not permission to substitute a version.

## 6. Builder handoff gate

A separate implementation handoff is required before code work. It must name one owner, allowed source/test/config paths, exact dependency action, test commands, acceptance tests, immutable evidence requirements, stop conditions, and reviewer focus.
