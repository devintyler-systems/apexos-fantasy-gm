# nflverse Play-by-Play Ingestion Contract

**Artifact:** `nflverse_play_by_play_ingestion_contract`
**Version:** 0.3
**Owner:** Architect / Evidence & Release Reviewer
**Status:** `PROPOSED_PENDING_EVIDENCE_AND_RELEASE_REVIEW`
**Depends On:** Data Source and Connector Register v1.4 (Section 2.1); v0.2 source-access baseline; independent release-asset Parquet schema transcript
**Supersession:** Supersedes v0.2 only after independent Evidence & Release Reviewer PASS and merge to `main`
**Builder status:** B-06 implementation is BLOCKED; do not create `builder/b-06-nflverse-ingestion`
**Created:** 2026-08-11
**Change class:** Structural contract correction

---

## 1. Decision statement

B-06 shall retrieve nflverse play-by-play data directly from the `nflverse/nflverse-data` GitHub release tagged `pbp`, select an exact uploaded season asset, retain the published Parquet bytes as immutable content-addressed evidence, and expose only a validated season pointer through `current.json`. This contract preserves v0.2's direct release-asset model; it corrects three release-blocking boundaries: named validation columns, collision-safe immutable promotion, and a scoped active-use prohibition on `nfl_data_py`. `design decision`

This is a contract and acceptance-test specification only. It does not approve a Builder branch, implementation, dependency installation, download, ingestion run, raw-data write, canonical-data write, or external-platform write. `design decision`

---

## 2. Scope, non-goals, and inheritance

### 2.1 Scope

In scope: release discovery; exact asset selection; bounded download to a same-filesystem temporary path; local SHA-256 computation; Parquet validation; regular-season game-count validation; immutable revision evidence; retrieval and failed-attempt events; concurrency-safe promotion; current-pointer publication; degraded-mode result semantics; and active-use scanning for `nfl_data_py`.

### 2.2 Explicit non-goals

Not in scope: xTD derivation, SQLite/canonical identity writes, scoring, projection computation, roster/draft-state writes, platform automation, postseason filtering, or B-07's sample-window decision. B-06 retains provider payloads and records counts; B-07 alone selects regular-only or regular-plus-postseason analytical windows. `design decision`

### 2.3 v0.2 requirements retained

Until this contract receives independent Reviewer PASS and merges, v0.2 remains the committed source-access baseline. After PASS and merge, v0.3 inherits every non-conflicting v0.2 requirement, including:

- direct `nflverse-data` release-asset discovery using the `pbp` release tag, exact asset-name matching, uploaded-state check, returned `browser_download_url`, approved-host redirect restriction, and failure on zero or multiple exact matches;
- revision evidence paths, colocated manifests, season-level `current.json`, retrieval events, failed attempts, manifest provenance fields, raw payload retention, and regular-season count policy;
- nullable provider-reported digest and mandatory local SHA-256 revision identity;
- visible degraded mode with no false current-status claim; and
- B-07 ownership of sample-window and season-type selection.

Where v0.3 conflicts with v0.2, v0.3 controls only after that PASS and merge. `design decision`

---

## 3. Source and evidence contract

### 3.1 Discovery and asset selection

1. Request `GET https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp`.
2. Select exactly one asset for requested `season` where `name == "play_by_play_{season}.parquet"` and `state == "uploaded"`.
3. Download only that asset's returned `browser_download_url`; do not construct an asset URL.
4. Reject non-2xx responses, zero or multiple exact matches, a non-Parquet name or extension, missing release metadata, or a redirect outside approved GitHub hosts.
5. Record release tag and ID, asset ID, name, reported size, provider digest when supplied, requested season, retrieval timestamp, effective source observation timestamp when available, parser version, and canonical source ID in the revision manifest or retrieval event as applicable.

The provider-reported digest is nullable. The locally computed SHA-256 of the exact downloaded bytes is mandatory, authoritative for local revision identity, and must be 64 lowercase hexadecimal characters. `confirmed evidence` / `design decision`

### 3.2 Retained evidence layout

```text
data/raw/nflverse/pbp/
  season={season}/
    revisions/
      sha256={revision_sha256}/
        pbp.parquet
        manifest.json
    events/
      retrieval-{event_id}.json
      failed-attempt-{attempt_id}.json
    current.json
  claims/
    revision/season={season}/sha256={revision_sha256}/
    pointer/season={season}/
```

`pbp.parquet` and `manifest.json` are retained evidence. After a successful promotion they are immutable and are never modified, renamed over, deleted by a refresh path, or replaced. `current.json` is a non-evidence season index and is the only path in this contract that may be atomically replaced. `design decision`

---

## 4. Required validation subset

### 4.1 Preservation rule

The following seven provider columns are the **minimum required validation subset**. Their presence and values are validated, but they are not a projection schema and do not limit retained data. The promoted `pbp.parquet` must preserve every raw provider column and row as published; no additional provider column may be discarded, renamed, coerced, derived, or filtered by B-06. `design decision`

```text
season, season_type, game_id, yardline_100, touchdown, rush_attempt, pass_attempt
```

### 4.2 Column rules

| Column | Required | Nullability | Logical type family | Semantic and domain rule |
|---|---:|---|---|---|
| `season` | yes | no | integral numeric | Every row has the requested season; reject null, non-integral, or any value not equal to the requested season. |
| `season_type` | yes | no | UTF-8 string / dictionary-encoded string | Every value is a non-empty recognized season type. `REG` must be represented and is used for regular-season counting; `POST` is retained when present. Reject null, blank, or unrecognized values. |
| `game_id` | yes | no | UTF-8 string / dictionary-encoded string | Every value is non-empty after no transformation; distinct values among `season_type == "REG"` are the regular-season game count. Reject null or blank values. |
| `yardline_100` | yes | yes | finite numeric | Null is allowed for plays without a meaningful line-to-goal value. Every non-null value is finite and within inclusive range 0 through 100. Reject strings, NaN, infinity, and values outside range. |
| `touchdown` | yes | yes | binary representation; see 4.3 | Non-null values mean whether the play records a touchdown and must encode exactly 0 or 1. |
| `rush_attempt` | yes | yes | binary representation; see 4.3 | Non-null values mean whether the play is a rushing attempt and must encode exactly 0 or 1. |
| `pass_attempt` | yes | yes | binary representation; see 4.3 | Non-null values mean whether the play is a passing attempt and must encode exactly 0 or 1. |

### 4.3 Binary-field type rule

This contract does **not** assume final Arrow physical types for `touchdown`, `rush_attempt`, or `pass_attempt`. Before v0.3 can receive PASS, the independent Evidence & Release Reviewer must obtain and attach a release-asset Parquet schema transcript identifying their observed Arrow logical and physical representations. `confirmed evidence requirement`

Pending that transcript, each binary field may be boolean, integer numeric, or floating numeric only. For each field, every non-null value must equal exactly `0` or `1`; boolean false/true are accepted as the semantic equivalents. Reject UTF-8/string encodings, dictionary/string encodings, decimal values other than exactly 0 or 1, NaN, infinity, and all other values. The transcript may narrow this provisional allowance only through a subsequent reviewed contract revision. `design decision`

### 4.4 Completeness rule

A requested season is valid only when all seven required columns are present, the Parquet file is readable, exactly one observed `season` equals the requested season, row count is nonzero, at least one regular-season game exists, and the regular-season distinct-`game_id` count equals the versioned policy:

| Season | Expected `REG` distinct game count |
|---|---:|
| 2016–2020 | 256 |
| 2021 | 272 |
| 2022 | 271 |
| 2023–2025 | 272 |

No B-06 operation selects an analytical sample or drops postseason rows. The manifest must record `game_counts_by_season_type`, `regular_season_expected_game_count`, and `regular_season_game_count_valid`. `design decision`

---

## 5. Manifest, events, and result contract

### 5.1 Required revision manifest fields

```json
{
  "canonical_source_id": "nflverse/nflverse-data:release:pbp",
  "source_url": "https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp",
  "source_release_tag": "pbp",
  "source_release_id": "integer",
  "source_asset_id": "integer",
  "source_asset_name": "play_by_play_{season}.parquet",
  "source_asset_size_bytes_reported": "integer",
  "source_asset_digest_reported": "sha256:<hex> | null",
  "requested_season": "integer",
  "game_counts_by_season_type": {"REG": "integer", "POST": "integer | omitted when absent"},
  "regular_season_expected_game_count": "integer",
  "regular_season_game_count_valid": "boolean",
  "revision_sha256": "required 64-character lowercase hex",
  "retrieved_at_utc": "RFC3339 UTC timestamp",
  "effective_time": "RFC3339 UTC timestamp | null",
  "parser_version": "string",
  "promotion_claim_id": "opaque immutable identifier",
  "retrieval_event_id": "opaque immutable identifier"
}
```

A retrieval event records the attempted source metadata, local SHA-256 when bytes were obtained, outcome, freshness state, claimed and actual revision identity, and the prior current-pointer identity. A failed attempt records UTC timestamp, attempted release/asset URL, failure class, safe error detail, and prior-valid SHA-256 when present. Events and failed attempts are append-only records. `design decision`

### 5.2 Exactly four decision-adapter outcomes

The decision adapter may return exactly these outcomes:

| Outcome | Meaning | Freshness / pointer rule |
|---|---|---|
| `success_new_revision` | A newly observed SHA-256 passed all validation and was promoted as a new immutable revision. | Fresh success; eligible for ordered pointer publication. |
| `success_existing_revision` | A fresh retrieval completed and its SHA-256 already had a valid immutable revision. | Fresh same-hash success; append retrieval event; eligible for ordered pointer publication; never label as stale. |
| `cached_valid_after_failure` | Refresh/discovery/download/validation/promotion failed, but an independently valid prior current revision exists. | Stale fallback; retain existing pointer; response must expose stale status, failure class, and prior revision SHA-256. |
| `failed` | Refresh failed and no independently valid prior current revision exists. | No fresh or cached-valid claim; do not create or change `current.json`. |

No other success, cache, partial, or implicit outcome is permitted. `design decision`

---

## 6. Immutable promotion and concurrency

### 6.1 General invariants

- Never invoke `os.replace` on a retained revision directory, `pbp.parquet`, or `manifest.json`.
- Atomic replacement is permitted **only** for `season={season}/current.json`.
- A candidate becomes a revision only after complete byte hashing and all validations pass.
- Revision and pointer claims are separate because evidence promotion and current-pointer publication have different collision domains.
- A failed claimant may never change retained evidence or the current pointer.

### 6.2 Revision-level promotion claim

For `(requested_season, revision_sha256)`, a claimant must acquire an exclusive revision claim before promotion using an atomic create-if-absent primitive in `claims/revision/season={season}/sha256={sha256}/`. The immutable claim record includes `promotion_claim_id`, claimant UUID, requested season, SHA-256, temporary-file identity, start timestamp, and source-asset identity.

The claim holder validates the temporary bytes, creates the final revision directory only if absent, writes `pbp.parquet` and `manifest.json` using create-new semantics, fsyncs files and directory metadata, and verifies the persisted bytes hash to the claimed SHA-256. It then writes an append-only retrieval event and marks the claim completed. No operation may overwrite an already-created evidence path.

If a valid final revision already exists, a claimant must verify its manifest/path/hash consistency, emit a separate retrieval event, and return `success_existing_revision`. If the existing revision is invalid or inconsistent, the operation fails closed; it must not repair, overwrite, or repoint around retained evidence. `design decision`

### 6.3 Deterministic contention behavior

| Case | Required behavior |
|---|---|
| Same-hash concurrent claimants | One claimant owns the exclusive revision claim. Others wait for terminal claim state or re-read the final revision. If valid evidence exists, each non-owner records its own retrieval event and returns `success_existing_revision`; no duplicate payload or manifest is written. |
| Different-byte concurrent claimants | SHA-256 values define independent revision claim domains. Both may promote independently after validation. Neither may overwrite the other revision. |
| Failed claimant | Persist a failed-attempt event. Release only ephemeral claim/lock state. Do not mutate retained evidence or `current.json`. A later claimant may attempt a new claim; its event history remains distinct. |
| Existing evidence collision | Validate immutable evidence identity. Match returns `success_existing_revision`; mismatch or unreadability returns `failed` or `cached_valid_after_failure` according to Section 5.2, without overwrite. |

### 6.4 Separate season-level pointer-publication claim

After, and only after, a successful revision outcome, a claimant must acquire a separate exclusive pointer-publication claim in `claims/pointer/season={season}/`. The pointer claim includes candidate SHA-256, candidate retrieval observation timestamp, revision claim ID, and a deterministic ordering key:

```text
(source_observed_at_utc, retrieval_completed_at_utc, revision_sha256)
```

The claimant reads the existing `current.json`. It publishes the candidate only when no valid pointer exists or the candidate ordering key is strictly greater than the existing pointer's recorded ordering key. Publication writes a complete temporary `current.json` on the same filesystem, fsyncs it, then atomically replaces only `current.json`. If the candidate key is lower or equal, it leaves the pointer unchanged and records that non-publication in the retrieval event. This prevents a delayed older retrieval from moving the pointer backward while making different-byte concurrency deterministic.

`current.json` contains only the selected revision manifest path, revision SHA-256, and pointer ordering key. A refresh failure, invalid candidate, failed claim, or stale fallback must never modify it. `design decision`

---

## 7. Scoped `nfl_data_py` prohibition

`nfl_data_py` is prohibited in active B-06 use. The required active-use scan covers:

- executable/importable source imports;
- dependency manifests and extras;
- lockfiles;
- executable scripts and CI/workflow definitions;
- install commands; and
- active Builder instructions, backlog lines, or kickoff instructions that authorize, direct, or imply its use.

The prohibition does **not** ban historical, audit, migration, prohibition, fixture, addendum, contract, ledger, or review-evidence references that accurately record its former status or explicitly state that it is prohibited. Such references are allowed and must not fail the active-use scan. `design decision`

---

## 8. Degraded mode

On any discovery, download, digest, Parquet, schema, completeness, promotion, or pointer-publication failure, the adapter must persist a failed-attempt event. If an independently valid previously pointed revision exists, return `cached_valid_after_failure` with a visible stale banner/state, prior revision SHA-256, failure class, retrieval timestamp, and no claim that refresh succeeded. Otherwise return `failed` with no current-status claim. `design decision`

---

## 9. Release-blocking acceptance matrix

All rows are release-blocking for B-06 implementation authorization. Fixtures may be synthetic except the independent schema transcript row, which must be obtained from a release asset independently of the Architect drafting session.

| ID | Criterion | Required evidence / test | Pass condition |
|---|---|---|---|
| AC-01 | Required subset | Parquet fixture missing each required column in turn | Each missing-column fixture is rejected; additional raw columns survive retained-byte comparison. |
| AC-02 | Nullability | Null fixtures for each column | `season`, `season_type`, and `game_id` nulls reject; `yardline_100` and binary nulls follow Section 4.2/4.3. |
| AC-03 | Type/domain | Invalid season, season type, game ID, yardline, and binary fixtures | All prohibited type/domain values reject with classified failure. |
| AC-04 | Binary schema evidence | Independent `pbp` release-asset Parquet schema transcript | Transcript names the seven columns and the observed Arrow logical/physical representation of all three binary fields; Reviewer attaches it before PASS. |
| AC-05 | Provider digest present | Fixture or recorded asset metadata with digest | Provider digest persists in manifest; local SHA-256 is required and matches downloaded bytes. |
| AC-06 | Provider digest absent | Fixture or recorded asset metadata without digest | Manifest stores null provider digest; local SHA-256 remains required and authoritative. |
| AC-07 | Discovery failure | Zero/multiple asset, non-2xx, bad redirect, or missing metadata simulation | No evidence/pointer mutation; returns `cached_valid_after_failure` only with independently valid prior revision, otherwise `failed`. |
| AC-08 | Invalid Parquet | Corrupt/unreadable Parquet fixture | No promotion; failed-attempt event; pointer unchanged. |
| AC-09 | Game-count policy | Valid schema fixture with incorrect REG distinct game count | Rejects according to the versioned policy; retains no candidate as current. |
| AC-10 | Same-hash concurrency | Two concurrent same-byte promotions | Exactly one immutable payload/manifest; distinct retrieval events; one new and one or more existing-revision outcomes; deterministic pointer. |
| AC-11 | Different-byte concurrency | Two valid, distinct-byte candidates for one season | Distinct immutable revisions; no overwrite; pointer follows Section 6.4 ordering key. |
| AC-12 | Retained-evidence invariance | Attempt overwrite/replace after promotion | Revision directory, `pbp.parquet`, and `manifest.json` byte hashes and paths are unchanged; any `os.replace` attempt for them is prohibited/fails test. |
| AC-13 | Pointer invariance | Failure, stale fallback, and lower/equal ordered pointer candidate cases | `current.json` changes only through a winning successful pointer-publication claim; otherwise remains byte-identical. |
| AC-14 | Stale labeling | Forced refresh failure with valid prior revision | Exactly `cached_valid_after_failure`; visible stale state and prior SHA-256; never fresh/success wording. |
| AC-15 | Active-use scan | Positive and negative repository fixtures | Active imports/dependencies/locks/scripts/workflows/install commands/active Builder instructions fail; permitted historical/audit/prohibition references pass. |
| AC-16 | Independent-validator isolation | Reviewer reruns release/schema and acceptance evidence outside Architect/Builder assertion | PASS evidence identifies independent reviewer session, source retrieval time, artifact/commit SHA, and reproduced result; self-assertion alone fails. |

---

## 10. Risks, assumptions, and handoff

| ID | Item | Label | Required disposition |
|---|---|---|---|
| B06-R01 | Exact Arrow physical types for the three binary fields are not yet independently transcribed. | `unknown` | Reviewer obtains release-asset schema transcript before PASS. |
| B06-R02 | Local filesystem primitive behavior varies by platform and network filesystem. | `assumption` | Builder must select and test a create-if-absent primitive that satisfies Sections 6.1–6.4 on the supported local filesystem before implementation PASS. |
| B06-R03 | B-07 sampling can be incorrectly inferred from B-06 retained rows. | `design decision` | B-07 must declare explicit sample-window/season-type selection and cite `game_counts_by_season_type`. |

**Ordered handoff:** (1) Evidence & Release Reviewer independently obtains the Parquet schema transcript and reviews this exact text; (2) Reviewer issues PASS or BLOCK on this PR; (3) only on PASS and merge may Architect assess a separate B-06 implementation kickoff; (4) Builder then implements exactly against the merged contract and acceptance matrix.

**Done definition:** Independent Reviewer PASS on this exact text, merged to `main`; no Builder work is included in this artifact.

**Change log:** v0.3 proposes named required validation columns, schema-evidence gate, exactly four result outcomes, immutable claim/pointer semantics, scoped active-use prohibition, and release-blocking negative-path matrix while retaining v0.2's direct source model.
