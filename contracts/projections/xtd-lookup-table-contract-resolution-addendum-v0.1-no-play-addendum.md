# B-07 xTD Lookup Table Contract Resolution Addendum v0.1 — Logical `no_play` Addendum

**Artifact:** B-07 xTD Logical `no_play` Addendum
**Version:** 0.1
**Owner:** Architect
**Status:** Proposed — pending contract-promotion PR and independent Evidence & Release Reviewer verdict
**Depends On:** B-07 xTD Lookup Table Contract Resolution Addendum v0.1; B-06 v0.2 Logical `no_play` Addendum v0.1
**Change type:** Structural contract clarification

## 1. Decision statement

B-07 consumes `logical_no_play` produced by the approved B-06 v0.2 normalization boundary. It
does not require a physical provider column named `no_play` in the immutable raw Parquet file.

The normalization is controlled by
`contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2-no-play-addendum-v0.1.md` and
version `b06-no-play-normalization-v0.1`. B-06 v0.2 remains the controlling upstream interface;
this addendum does not adopt B-06 v0.3.

## 2. Source-schema clarification

Section 6 of the B-07 v0.1 contract is clarified as follows:

- the physical raw-source requirement contains the original fields except physical `no_play`;
- physical `play_type`, `pass_attempt`, and `rush_attempt` are required normalization inputs; and
- a successfully validated B-06 logical `no_play` capability is required in addition to the
  physical source schema.

The physical provider fields required for B-07 are therefore:

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
two_point_conv_result
touchdown
td_player_id
```

Absence of any physical field above, failure to apply normalization version
`b06-no-play-normalization-v0.1`, or any unknown logical result invalidates the B-06 revision for
B-07 production use.

## 3. Eligibility semantics

Every B-07 predicate written as `no_play != true` means `logical_no_play != true`. All eligibility
semantics and quality-counter behavior otherwise remain unchanged. Unknown logical values never
reach B-07 because B-06 promotion fails closed.

The separate exclusions for penalties, sacks, spikes, two-point attempts, conflicting flags,
invalid field position, and missing receiver identity remain binding and must not be inferred
from `logical_no_play`.

## 4. Unchanged contract decisions

This addendum changes none of the following:

- regular-season-only policy;
- production seasons 2023, 2024, and 2025;
- weights 0.17, 0.33, and 0.50;
- field-position buckets or ordering;
- rush-attempt or pass-target definitions;
- receiver identity requirement;
- touchdown numerator;
- 100.0 weighted-sample confidence threshold or PA02 propagation;
- immutable output/provenance behavior; or
- rolling-origin Brier-score promotion gate.

B-07 remains blocked until valid controlled B-06 revisions for 2023, 2024, and 2025 satisfy every
live/controlled-data requirement. This addendum creates no B-07 artifact and makes no readiness
claim.

## 5. Acceptance criteria

1. B-07 accepts a physical raw schema without `no_play` only when the approved B-06 logical
   normalization is proven and reports zero unknown rows.
2. Logical true is treated exactly as the former `no_play = true` predicate.
3. Unknown normalization evidence blocks B-06 promotion and B-07 generation.
4. The independent penalty, sack, spike, two-point, receiver, conflict, and yardline rules remain
   unchanged.
5. No other B-07 normative rule changes.

## 6. Change log

- **v0.1:** Replaces the physical `no_play` source-column requirement with the approved B-06
  logical normalization capability while preserving all B-07 filtering and promotion gates.
