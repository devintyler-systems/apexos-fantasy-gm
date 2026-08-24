# B-07 xTD Lookup Table Contract Resolution Addendum

**Artifact:** B-07 xTD Lookup Table Contract Resolution Addendum
**Version:** 0.1
**Owner:** Architect
**Status:** Proposed — ready for contract-promotion PR; no B-07 implementation authorized until merged
**Change type:** Structural
**Dependencies:** Projection Artifact Contract v1.0 §5 and §8 PA02; Projection Artifact Contract v1.2 Addendum §§3–4; B-06 ingestion contract v0.2; B-06 live/controlled-data gate
**Implementation owner:** Codex
**Reviewer:** Evidence & Release Reviewer

## 1. Decision statement

1. B-07 produces a versioned, immutable, regular-season-only lookup table of touchdown probabilities by `field_position_bucket` and `play_type`.
2. The only allowed lookup `play_type` values are `rush_attempt` and `pass_target`.
3. The initial production season window is exactly 2023, 2024, and 2025.
4. The production window uses count-weighted seasonal decay: 2023 = 0.17, 2024 = 0.33, and 2025 = 0.50.
5. The controlling upstream ingestion interface is `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`.
6. B-06 v0.3 is not controlling until it receives an explicit Evidence & Release Reviewer PASS verdict and the Decision Ledger records that approval.
7. B-07 production generation must fail closed when a required source revision, source schema, manifest, or quality requirement is unavailable or invalid.
8. B-07 must not use synthetic fixtures, MockTransport data, incomplete seasons, unpromoted B-06 revisions, or an unapproved B-06 v0.3 pointer interface as production input.
9. Historical 2016–2022 PBP data is excluded from the production lookup. It may only be used in the evaluation workflow defined by this contract.

## 2. Scope and non-goals

### In scope

- Deterministic xTD lookup aggregation from immutable B-06 PBP revisions.
- Field-position bucket rules, play eligibility, touchdown attribution, confidence rules, output schema, provenance, and publication behavior.
- A controlled-data prerequisite for real artifact generation.
- An evaluation gate for using xTD as a projection feature.

### Explicit non-goals

- This artifact does not calculate individual-player projections, player xTD totals, replacement value, availability, roster-fit score, draft recommendations, or betting probabilities.
- This artifact does not infer a target from `pass_attempt` without `receiver_player_id`.
- This artifact does not use postseason, preseason, Pro Bowl, or other non-regular-season plays.
- This artifact does not define a B-07 `current.json` pointer.
- This artifact does not allow a previously generated artifact or manifest to be overwritten.
- This artifact does not authorize use of xTD as a production projection feature before the evaluation gate passes.

## 3. System flow

1. Resolve immutable B-06 revisions for 2023, 2024, and 2025 through the B-06 v0.2 pointer and manifest chain.
2. Verify pointer-to-manifest hash continuity, required manifest fields, regular-season validity, immutable source data, and required source columns.
3. Filter rows to eligible regular-season `rush_attempt` or `pass_target` opportunities.
4. Assign each eligible row to one and only one defined field-position bucket.
5. Calculate raw and weighted touchdown and opportunity counts by bucket and play type.
6. Calculate `xtd_rate`, `weighted_sample_size`, and low-confidence status.
7. Write exactly one immutable Parquet lookup table and one immutable provenance manifest per calculated lookup revision.
8. Apply degraded mode when validation fails: do not create a new artifact, do not claim current xTD status, and do not apply new xTD-derived projection adjustments.
9. Permit xTD use in a projection artifact only after the evaluation and promotion gate passes.

## 4. Controlling B-06 interface

B-07 consumes B-06 v0.2 pointer semantics only:

```text
data/raw/nflverse/pbp/season={season}/current.json
  -> manifest_path
  -> revision_sha256

{manifest_path}
  -> data/raw/nflverse/pbp/season={season}/revisions/sha256={revision_sha256}/manifest.json
```

The resolved B-06 manifest must match the pointer `revision_sha256` and contain all fields below:

```text
canonical_source_id
source_url
source_release_tag
source_release_id
source_asset_id
source_asset_name
source_asset_size_bytes_reported
source_asset_digest_reported
requested_season
game_counts_by_season_type
regular_season_expected_game_count
regular_season_game_count_valid
revision_sha256
retrieved_at_utc
effective_time
parser_version
promotion_claim_id
retrieval_event_id
```

A required B-06 season is invalid and blocks B-07 production generation if any condition below is true:

- The season pointer is missing.
- The pointer does not contain `manifest_path`.
- The pointer does not contain `revision_sha256`.
- The resolved manifest is missing.
- The pointer `revision_sha256` differs from the manifest `revision_sha256`.
- The manifest `requested_season` differs from the required season.
- `regular_season_game_count_valid` is not exactly `true`.
- The immutable Parquet revision is missing.
- A required B-06 manifest field is absent.
- A required B-07 source column is absent.
- The source revision is synthetic, fixture-based, MockTransport-derived, partial, or lacks non-synthetic provider provenance.

A B-06 v0.3 pointer may contain additional fields, including `pointer_ordering_key`. B-07 v0.1 must not require, interpret, or depend on those additional fields.

## 5. Field-position buckets

`yardline_100` means the offensive distance, in yards, to the opponent’s goal line at the beginning of an eligible opportunity.

A valid `yardline_100` is an integral numeric value from 0 through 100 inclusive.

Every valid value must be assigned to exactly one bucket using this exact stable ordering:

| bucket_order | field_position_bucket | display_label | Inclusive rule |
|---:|---|---|---|
| 0 | `goal_line_0` | `0` | `yardline_100 = 0` |
| 1 | `one_yard_line` | `1` | `yardline_100 = 1` |
| 2 | `two_to_three` | `2-3` | `2 <= yardline_100 <= 3` |
| 3 | `four_to_five` | `4-5` | `4 <= yardline_100 <= 5` |
| 4 | `six_to_ten` | `6-10` | `6 <= yardline_100 <= 10` |
| 5 | `eleven_to_twenty` | `11-20` | `11 <= yardline_100 <= 20` |
| 6 | `twenty_one_plus` | `21+` | `21 <= yardline_100 <= 100` |

A null, non-integral, negative, or greater-than-100 `yardline_100` is ineligible.

Ineligible field-position values must not be imputed, rounded, coerced, merged with a valid bucket, or assigned to an “unknown” output bucket.

A valid `yardline_100 = 0` belongs only to `goal_line_0`. It must not be discarded or merged with `one_yard_line`.

## 6. Required source columns

B-07 requires all source columns below in each selected B-06 revision:

```text
season
season_type
play_type
yardline_100
rush_attempt
pass_attempt
receiver_player_id
sack
qb_spike
penalty
no_play
two_point_conv_result
touchdown
td_player_id
```

Generation must fail closed if any required source column is absent.

No substitute column, renamed provider field, inferred semantic, or similarly named field may be used unless a later approved contract revision explicitly changes this section.

A source flag is true only when its value is explicitly boolean true or numeric `1`. A null source flag is not true.

## 7. Eligible opportunity contract

### 7.1 Eligible rush attempt

A row is an eligible `rush_attempt` when and only when every condition below is true:

```text
season_type = "REG"
play_type = "run"
rush_attempt = true
pass_attempt != true
no_play != true
penalty != true
two_point_conv_result IS NULL
yardline_100 is valid
```

### 7.2 Eligible pass target

A row is an eligible `pass_target` when and only when every condition below is true:

```text
season_type = "REG"
play_type = "pass"
pass_attempt = true
receiver_player_id IS NOT NULL
rush_attempt != true
sack != true
qb_spike != true
no_play != true
penalty != true
two_point_conv_result IS NULL
yardline_100 is valid
```

`receiver_player_id IS NOT NULL` is the binding pass-target criterion.

A `pass_attempt = true` row with null `receiver_player_id` is not a target. It must be excluded and increment `excluded_no_receiver_target`.

The following treatment is mandatory:

| Condition | Treatment |
|---|---|
| `sack = true` | Exclude from `pass_target` |
| `qb_spike = true` | Exclude from `pass_target` |
| Throwaway / no receiver identity | Exclude from `pass_target`; increment `excluded_no_receiver_target` |
| `penalty = true` | Exclude from both play types; increment `excluded_penalty` |
| `no_play = true` | Exclude from both play types; increment `excluded_no_play` |
| `two_point_conv_result IS NOT NULL` | Exclude from both play types; increment `excluded_two_point` |
| `rush_attempt = true` and `pass_attempt = true` | Exclude from both play types; increment `conflicting_opportunity_flags` |
| Required true predicate is null | Exclude; do not infer a value |
| Invalid `yardline_100` | Exclude; increment applicable yardline quality counter |

For every eligible row:

```text
is_touchdown = (touchdown = true)
```

Every eligible row where `is_touchdown = true` increments the relevant touchdown numerator by exactly one.

`td_player_id` is retained as source provenance only. It must not redefine an eligible event’s touchdown numerator and does not make an otherwise ineligible event eligible.

## 8. Production season policy and decay

The production B-07 v1 lookup uses exactly this window:

```yaml
included_seasons:
  - season: 2023
    weight: 0.17
  - season: 2024
    weight: 0.33
  - season: 2025
    weight: 0.50
included_season_types:
  - REG
excluded_season_types:
  - POST
  - PRE
excluded_production_seasons:
  - 2016
  - 2017
  - 2018
  - 2019
  - 2020
  - 2021
  - 2022
```

No fallback season substitution is permitted.

If any required production season is missing, invalid, incomplete, synthetic, unpromoted, or unavailable through the controlling B-06 v0.2 interface, B-07 production generation must fail.

B-07 v0.1 must not substitute an older season, a partial current season, playoff data, preseason data, or synthetic data for any required season.

For each included season `s`, bucket `b`, and play type `t`:

```text
TD[s,b,t] = count of eligible rows where is_touchdown = true
PLAYS[s,b,t] = count of eligible rows
```

Apply seasonal weights to counts before calculating the rate:

\[
weighted\_touchdown\_count[b,t] =
\sum_s weight[s] \times TD[s,b,t]
\]

\[
weighted\_sample\_size[b,t] =
\sum_s weight[s] \times PLAYS[s,b,t]
\]

\[
xtd\_rate[b,t] =
\begin{cases}
weighted\_touchdown\_count[b,t] / weighted\_sample\_size[b,t],
& \text{if } weighted\_sample\_size[b,t] > 0 \\
null, & \text{if } weighted\_sample\_size[b,t] = 0
\end{cases}
\]

B-07 must not calculate separate season rates and average those rates.

`raw_touchdown_count` is the unweighted sum of touchdown events across 2023, 2024, and 2025.

`raw_sample_size` is the unweighted sum of eligible opportunities across 2023, 2024, and 2025.

2016–2022 data must not contribute to production `weighted_touchdown_count`, `weighted_sample_size`, `raw_touchdown_count`, `raw_sample_size`, or `xtd_rate`.

## 9. Low-confidence contract

The binding low-confidence threshold is:

```text
weighted_sample_size < 100.0
```

Every output row must include:

```text
is_low_confidence: bool
low_confidence_reason_codes: list<string>
```

The deterministic rule is:

```text
is_low_confidence =
  (weighted_sample_size < 100.0)
  OR
  (xtd_rate IS NULL)
```

The only allowed low-confidence reason codes are:

```text
WEIGHTED_SAMPLE_LT_100
ZERO_ELIGIBLE_WEIGHTED_PLAYS
```

For a zero-denominator bucket and play type, the required output values are:

```text
xtd_rate = null
weighted_touchdown_count = 0.0
weighted_sample_size = 0.0
raw_touchdown_count = 0
raw_sample_size = 0
is_low_confidence = true
low_confidence_reason_codes = [
  "WEIGHTED_SAMPLE_LT_100",
  "ZERO_ELIGIBLE_WEIGHTED_PLAYS"
]
```

A row with nonzero `weighted_sample_size` below 100.0 must include only:

```text
["WEIGHTED_SAMPLE_LT_100"]
```

When a downstream projection artifact uses a B-07 row with `is_low_confidence = true`, it must:

```text
set projected_role_confidence = "low"
include reason code "XTD_LOOKUP_LOW_CONFIDENCE"
retain the B-07 lookup revision and manifest identity in source_citations
```

A decision adapter must never increase `projected_role_confidence` because of B-07.

When no valid non-low-confidence B-07 row exists, downstream behavior is no xTD adjustment. It must not borrow, smooth, infer, or impute a rate from another bucket or play type.

## 10. Output artifact contract

The immutable output Parquet path is:

```text
data/processed/projections/xtd_lookup_table/
  contract_version=v0.1/
  as_of_date={YYYY-MM-DD}/
  revision_sha256={sha256}/
  xtd_lookup_table_v1.parquet
```

The immutable provenance manifest path is:

```text
data/processed/projections/xtd_lookup_table/
  contract_version=v0.1/
  as_of_date={YYYY-MM-DD}/
  revision_sha256={sha256}/
  xtd_lookup_table_v1.manifest.json
```

The Arrow and Parquet schema is exactly:

```text
field_position_bucket: string, non-null
display_label: string, non-null
bucket_order: int8, non-null
play_type: string, non-null
xtd_rate: float64, nullable
weighted_touchdown_count: float64, non-null
weighted_sample_size: float64, non-null
raw_touchdown_count: int64, non-null
raw_sample_size: int64, non-null
is_low_confidence: bool, non-null
low_confidence_reason_codes: list<string>, non-null
season_window: string, non-null
season_types: list<string>, non-null
as_of_timestamp: timestamp[us, tz=UTC], non-null
contract_version: string, non-null
lookup_revision_sha256: string, non-null
```

The only valid `play_type` values are:

```text
rush_attempt
pass_target
```

The artifact must contain exactly 14 rows:

```text
7 field-position buckets x 2 play types = 14 rows
```

Every bucket and play-type combination must be represented, including combinations with zero eligible plays.

The exact output sort order is:

```text
bucket_order ascending
then play_type ascending:
  rush_attempt
  pass_target
```

`season_window` must equal this canonical JSON string:

```json
[{"season":2023,"weight":0.17},{"season":2024,"weight":0.33},{"season":2025,"weight":0.50}]
```

`season_types` must equal:

```json
["REG"]
```

Publication is append-only. If the calculated immutable artifact or manifest path already exists, generation must fail. B-07 must not overwrite a prior Parquet file or manifest.

B-07 v0.1 does not define a `current.json` pointer for lookup publication.

## 11. Provenance manifest contract

The provenance manifest must have this structure:

```json
{
  "artifact_name": "xtd_lookup_table_v1",
  "contract_version": "v0.1",
  "lookup_revision_sha256": "<sha256>",
  "created_at_utc": "<RFC3339 UTC timestamp>",
  "as_of_timestamp": "<RFC3339 UTC timestamp>",
  "season_window": [
    {"season": 2023, "weight": 0.17},
    {"season": 2024, "weight": 0.33},
    {"season": 2025, "weight": 0.50}
  ],
  "season_types": ["REG"],
  "source_contract": {
    "path": "contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md",
    "version": "v0.2"
  },
  "consumed_b06_revisions": [
    {
      "season": 2023,
      "pointer_path": "<path>",
      "pointer_sha256": "<sha256>",
      "manifest_path": "<path>",
      "revision_sha256": "<sha256>",
      "canonical_source_id": "<value>",
      "source_url": "<value>",
      "source_release_tag": "<value>",
      "source_release_id": "<value>",
      "source_asset_id": "<value>",
      "source_asset_name": "<value>",
      "source_asset_digest_reported": "<value-or-null>",
      "retrieved_at_utc": "<RFC3339 UTC timestamp>",
      "effective_time": "<RFC3339 UTC timestamp>",
      "parser_version": "<value>",
      "promotion_claim_id": "<value>",
      "retrieval_event_id": "<value>"
    }
  ],
  "eligibility_spec_version": "v0.1",
  "quality_counters": {
    "null_yardline_100": 0,
    "out_of_range_yardline_100": 0,
    "conflicting_opportunity_flags": 0,
    "excluded_no_play": 0,
    "excluded_penalty": 0,
    "excluded_sack": 0,
    "excluded_spike": 0,
    "excluded_no_receiver_target": 0,
    "excluded_two_point": 0
  }
}
```

The `consumed_b06_revisions` array must contain exactly three entries, one for each required production season:

```text
2023
2024
2025
```

Every consumed revision must retain all specified B-06 source and retrieval lineage.

Missing B-06 provenance invalidates the B-07 artifact for production use.

## 12. B-06 live/controlled-data gate

Before B-07 creates a real artifact, every condition below must pass:

1. Immutable B-06 Parquet revisions for 2023, 2024, and 2025 exist beneath `data/raw/nflverse/pbp`.
2. Each required season resolves through a B-06 v0.2-compatible pointer and immutable manifest chain.
3. Each selected manifest has `regular_season_game_count_valid = true`.
4. Each selected manifest has non-synthetic provider, source, release, asset, retrieval, parser, and promotion lineage.
5. Each selected Parquet revision contains every required source column from Section 6.
6. Generation evidence proves only `season_type = "REG"` rows entered the production aggregation.
7. The B-07 provenance manifest retains all three consumed B-06 revision identities.
8. No selected B-06 revision derives from MockTransport, test fixtures, synthetic data, an incomplete season, or a partial provider response.

Failure of any condition blocks production artifact generation.

On a live/controlled-data gate failure, degraded mode requires:

```text
No claim that B-07 xTD data is current.
No new xTD-derived adjustment in any projection artifact.
A visible stale or unavailable reason.
A separately approved prior immutable artifact may remain inspectable,
but it must not be represented as current.
```

## 13. Evaluation and promotion gate

The naive baseline is the pooled training-window touchdown rate by `play_type` only:

\[
baseline\_rate[t] =
\frac{\sum_b TD[b,t]}{\sum_b PLAYS[b,t]}
\]

Evaluation uses rolling-origin, regular-season-only holdouts:

| Holdout season | Training seasons |
|---:|---|
| 2020 | 2017, 2018, 2019 |
| 2021 | 2018, 2019, 2020 |
| 2022 | 2019, 2020, 2021 |
| 2023 | 2020, 2021, 2022 |
| 2024 | 2021, 2022, 2023 |
| 2025 | 2022, 2023, 2024 |

For every rolling training window:

```text
oldest season weight = 0.17
middle season weight = 0.33
newest season weight = 0.50
```

For each eligible event in a holdout season:

```text
observed outcome y = 1 when touchdown = true, otherwise 0
lookup prediction p = applicable field-position-bucket and play-type xtd_rate
baseline prediction p = applicable play-type-only baseline_rate
```

The primary metric is event-level Brier score:

\[
Brier =
\frac{1}{n}
\sum_{i=1}^{n}(p_i-y_i)^2
\]

The lookup may become a production projection feature only if every condition below is met:

1. Pooled Brier score improves by at least 1.0% relative to the naive baseline.
2. The 1.0% relative Brier-score improvement requirement passes separately for `rush_attempt` and `pass_target`.
3. A 10,000-resample season-block bootstrap across the six holdout seasons produces a 95% confidence interval for:

\[
Brier_{lookup} - Brier_{baseline}
\]

whose upper bound is below 0 for the pooled sample and separately for both play types.
4. The tested projection feature path uses no B-07 row where `is_low_confidence = true`.

If any promotion condition fails, the xTD lookup remains a research artifact only. It must not adjust a production projection artifact.

## 14. Acceptance criteria

1. The seven field-position buckets have exact labels, inclusive edges, sort order, zero treatment, and null treatment.
2. Every valid integer `yardline_100` from 0 through 100 maps to one and only one bucket.
3. A pass attempt with null `receiver_player_id` is not a pass target.
4. Penalties, no-plays, sacks, spikes, throwaways, two-point attempts, conflicting flags, null predicates, and invalid field positions are treated deterministically.
5. Production aggregation includes only regular-season 2023, 2024, and 2025 data.
6. Production aggregation applies count-weighted 0.17, 0.33, and 0.50 seasonal decay.
7. The artifact contains exactly 14 rows in the required order.
8. Every row has `is_low_confidence` and `low_confidence_reason_codes`.
9. Any downstream use of a low-confidence lookup propagates `projected_role_confidence = "low"` and reason code `XTD_LOOKUP_LOW_CONFIDENCE`.
10. The output manifest retains all three B-06 revisions and all required B-06 provenance fields.
11. Publication is immutable and non-overwriting.
12. A real artifact cannot be generated before every B-06 live/controlled-data gate condition passes.
13. The lookup cannot influence a production projection artifact before every evaluation promotion condition passes.
14. B-06 v0.2 remains the controlling upstream interface until a separate approved B-06 v0.3 adoption decision exists.

## 15. Assumptions Register

| ID | Statement | Status | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|---|
| AR-B07-01 | Production xTD uses regular-season data only | Design decision | B-07 aggregation and projection feature | Low | Architect | Resolved in v0.1 |
| AR-B07-02 | 2023–2025 are the three complete seasons used by the initial artifact | Design decision | B-07 season selector | Medium | Architect | Resolved in v0.1 |
| AR-B07-03 | Required nflverse columns exist in all selected revisions | Assumption | B-06/B-07 adapter | High | Codex validates | Before real artifact |
| AR-B07-04 | B-06 v0.2 is controlling | Design decision | B-07 revision resolver | Medium | Architect | Resolved in v0.1 |
| AR-B07-05 | B-06 v0.3 lacks a recorded independent release approval | Unknown | Future B-06 interface adoption | Medium | Evidence & Release Reviewer | Before v0.3 adoption |
| AR-B07-06 | 100 weighted opportunities is an appropriate initial confidence floor | Design decision | Confidence propagation | Medium | Architect | Reassess after evaluation |
| AR-B07-07 | The specified Brier-score evaluation is sufficient for feature promotion | Design decision | Projection artifact | Medium | Architect and Reviewer | Before feature integration |

## 16. Change log

- **v0.1:** Establishes regular-season-only xTD lookup generation; exact bucket, eligibility, and touchdown rules; 2023–2025 count-weighted decay; confidence propagation; immutable artifact and provenance requirements; B-06 v0.2 authority; live-data gating; and xTD feature-promotion evaluation.

## 17. Decision Ledger impact

On merge, append a structural `Version 3.6` entry to `docs/decision_ledger.md` stating:

- B-07 contract-resolution blockers are bound by this addendum.
- B-07 uses regular-season-only data from 2023, 2024, and 2025.
- B-07 uses count-weighted seasonal decay of 0.17, 0.33, and 0.50.
- B-06 v0.2 is controlling until B-06 v0.3 receives independent release approval and a Decision Ledger record.
- Production artifact generation remains blocked on the B-06 live/controlled-data gate.
- Production projection use remains blocked on the Brier-score promotion gate.

**Version 0.1 – change made:** Bound B-07 to regular-season-only, 2023–2025 count-weighted xTD lookup generation with deterministic eligibility, confidence, provenance, B-06 authority, and feature-promotion gates.

**Highest-leverage next artifact:** B-07 contract-promotion PR and independent Evidence & Release Reviewer verdict.
