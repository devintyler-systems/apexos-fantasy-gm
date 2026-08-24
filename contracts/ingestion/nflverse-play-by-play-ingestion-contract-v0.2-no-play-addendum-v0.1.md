# nflverse Play-by-Play Ingestion Contract v0.2 — Logical `no_play` Addendum

**Artifact:** `nflverse_play_by_play_ingestion_contract_v0.2_no_play_addendum`
**Version:** 0.1
**Owner:** Architect
**Status:** Proposed — pending contract-promotion PR and independent Evidence & Release Reviewer verdict
**Depends On:** `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`; B-07 xTD Lookup Table Contract Resolution Addendum v0.1
**Change type:** Structural contract clarification

## 1. Decision statement

B-06 v0.2 remains the controlling source-access and immutable-evidence contract. This addendum
defines a logical normalized `no_play` value for B-07 because the verified official 2023
`nflverse-data` PBP Parquet asset has no physical column named `no_play`.

The raw provider Parquet bytes and columns remain unchanged. B-06 must never add, rename,
overwrite, or substitute a physical provider column. The logical value exists only at the B-06
decision-adapter/normalization boundary and is identified by normalization version
`b06-no-play-normalization-v0.1`.

## 2. Required raw source fields

The normalization requires physical provider columns `play_type`, `pass_attempt`, and
`rush_attempt`. Their absence is a schema failure. No description-text parsing, penalty-field
inference, `play_deleted`, `play_type_nfl`, or similarly named field may replace them.

A source opportunity flag is true only when it is explicitly boolean true or numeric `1`.
Null is not true.

## 3. Deterministic normalization

The recognized non-null `play_type` domain is exactly:

```text
extra_point
field_goal
kickoff
no_play
pass
punt
qb_kneel
qb_spike
run
```

For each raw row, calculate `logical_no_play` in this exact order:

```text
if physical column play_type is absent:
  logical_no_play = unknown
else if play_type = "no_play":
  logical_no_play = true
else if play_type IS NULL:
  if pass_attempt = true OR rush_attempt = true:
    logical_no_play = unknown
  else:
    logical_no_play = true
else if play_type IN (
  "extra_point", "field_goal", "kickoff", "pass", "punt",
  "qb_kneel", "qb_spike", "run"
):
  logical_no_play = false
else:
  logical_no_play = unknown
```

Null `play_type` with no true rush/pass opportunity flag maps to `true`, not `false`. This is a
conservative exclusion rule supported by the retained official 2023 asset: all 1,452 null
`play_type` rows had no rush/pass opportunity shape. A future null row with a true opportunity
flag is unknown and fails closed.

## 4. Unknown and promotion behavior

B-06 must calculate the normalization for every row before promoting a revision for B-07 use.
If any row produces `logical_no_play = unknown`, promotion fails with reason code
`logical_no_play_unknown`; no new immutable revision, manifest, or pointer may be published.

The B-06 parser must require the three physical fields in Section 2, validate the recognized
`play_type` domain, record normalization version `b06-no-play-normalization-v0.1` within the
existing `parser_version` manifest value, and retain evidence counts for normalized true, false,
and unknown values. This adds no manifest field and does not change the v0.2 pointer schema.

## 5. Separation from other exclusions

`logical_no_play` does not replace the independent B-07 exclusions for `penalty`, `sack`,
`qb_spike`, `two_point_conv_result`, conflicting opportunity flags, invalid field position, or
missing receiver identity. In particular:

- an accepted penalty on a retained pass/run row may normalize to false and remains excluded by
  B-07's separate `penalty = true` rule;
- a sack or spike may normalize to false and remains excluded by its dedicated predicate;
- a two-point row may normalize to either value and remains excluded by
  `two_point_conv_result IS NOT NULL`; and
- description text containing “No Play” is not authoritative because replay text can retain that
  phrase after the final ruling reverses the no-play decision.

## 6. Evidence basis and risks

The official 2023 asset at release ID `58152862`, asset ID `354728689`, and SHA-256
`bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776` contained 49,665 rows.
Observed evidence included:

- 4,555 rows with `play_type = "no_play"`;
- 1,452 rows with null `play_type`, with zero rush/pass opportunity-shaped rows;
- 2,496 descriptions containing “No Play”, including two replay-reversal rows whose final
  `play_type` was `pass` or `punt`;
- 3,229 penalty rows, including 764 whose `play_type` was not `no_play`; and
- `play_deleted = 0` for all 49,665 rows.

False-positive risk is bounded by treating administrative/null non-opportunity rows as no-play;
they cannot enter B-07's pass/run opportunity set. False-negative risk is fail-closed: a future
null `play_type` with a true rush/pass flag or any unexpected non-null domain value blocks
promotion rather than silently normalizing false.

## 7. Acceptance criteria

1. Raw `play_type = "no_play"` normalizes true.
2. Each recognized non-null non-`no_play` value normalizes false.
3. Null `play_type` without a true rush/pass opportunity flag normalizes true.
4. Null `play_type` with a true rush or pass flag normalizes unknown and blocks promotion.
5. An absent `play_type`, `pass_attempt`, or `rush_attempt` field blocks promotion.
6. An unexpected non-null `play_type` value normalizes unknown and blocks promotion.
7. Accepted penalties, sacks, spikes, and two-point attempts remain governed by their independent
   B-07 predicates.
8. Normalization does not mutate the input record or retained raw Parquet bytes.
9. No B-06 v0.3 behavior is adopted.

## 8. Degraded mode

On a missing normalization field or any unknown result, B-06 must report unavailable/failed
normalization evidence, retain any previously valid pointer unchanged, and make no current-data
claim. It must not parse `desc`, infer from penalty text, or relax the recognized domain.

## 9. Change log

- **v0.1:** Defines an evidence-supported logical `no_play` normalization while preserving raw
  provider bytes and B-06 v0.2 authority.
