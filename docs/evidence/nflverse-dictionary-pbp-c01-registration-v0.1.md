# ApexOS nflverse Dictionary PBP C-01 Evidence Registration v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-NFLVERSE-DICTIONARY-PBP-C01-EVIDENCE-REGISTRATION` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | EVIDENCE RETAINED — no individual field semantic approved |
| Change type | Structural evidence registration |
| Governing decisions | `D-NORM-SEMANTICS-001`; `D-NORM-SEMANTICS-002` |
| Collection authorization | `APEXOS-NFLVERSE-DICTIONARY-PBP-EVIDENCE-RETENTION-021` |
| Collection boundary | Candidate dictionary evidence only; no downstream implementation authorization. |

## Provenance and Retained Evidence

| Field | Value |
|---|---|
| Upstream repository | `nflverse/nflreadr` |
| Canonical repository URL | `https://github.com/nflverse/nflreadr` |
| Source path | `data-raw/dictionary_pbp.csv` |
| Canonical blob URL | `https://github.com/nflverse/nflreadr/blob/d072c08492067b578f27e562b6cc9c9e3b8589c3/data-raw/dictionary_pbp.csv` |
| Raw retrieval URL | `https://raw.githubusercontent.com/nflverse/nflreadr/d072c08492067b578f27e562b6cc9c9e3b8589c3/data-raw/dictionary_pbp.csv` |
| Immutable pin | `d072c08492067b578f27e562b6cc9c9e3b8589c3` |
| Pin type | Git commit SHA |
| Artifact type | Static official dictionary source |
| Source origin status | Confirmed official nflverse repository origin |
| Retrieval mechanism | Binary-safe HTTPS GET, with HTTPS-only protocol, TLS 1.2, no redirects, and no credentials |
| First retrieval timestamp | `2026-08-30T11:59:46.5243170Z` |
| Observed response content type | `text/plain; charset=utf-8` |
| Snapshot ID | `nflverse-dictionary-pbp-c01-d072c084-137f3c1a-v0.1` |
| Snapshot byte count | `39127` |
| Snapshot SHA-256 | `137f3c1ae4794e2a1a4bc55ac543d807d36c6c3c24c8088e0489dd7a5c156f33` |
| Retained snapshot | `docs/evidence/nflverse-dictionary-pbp-c01-snapshot-v0.1.csv` |
| Retained checksum | `docs/evidence/nflverse-dictionary-pbp-c01-snapshot-v0.1.sha256` |
| Retrieval-integrity record | `docs/evidence/nflverse-dictionary-pbp-c01-retrieval-integrity-v0.1.txt` |
| Repeat retrieval | Same pinned raw URL; byte count and SHA-256 matched independently |
| Source-provider / terms reference | `unknown` — separate review required |

The first raw HTTPS response is retained byte-for-byte in the snapshot. The
first response, staged Git blob materialization, and independent second response
each measured 39127 bytes and had SHA-256
`137f3c1ae4794e2a1a4bc55ac543d807d36c6c3c24c8088e0489dd7a5c156f33`.

Windows environment note: system Git reported `core.autocrlf=true`. Hashing
used the binary downloaded response and a byte-preserved materialization of the
Git blob, never a CRLF-transformed working-tree checkout.

## Bounded Relationship and Applicability

C-01 is a static official dictionary source. The upstream pinned build source
was observed to read it to create package data. This records provenance only;
it does not quote, summarize, name, classify, or interpret source rows or
definitions.

`DOCUMENTATION_APPLICABILITY_UNCONFIRMED` is the release-asset applicability
status. No direct upstream statement has been retained or approved establishing
that this artifact applies to `play_by_play_{season}.parquet`. It therefore
cannot authorize an individual field semantic or any downstream use.

## Strict Non-Claims

- No raw field is named, selected, enumerated, interpreted, or approved.
- No event, scoring, null, attribution, ownership, correction, availability,
  timing, player, team, game, play, or identity rule is stated or approved.
- No semantic mapping, normalized fact, canonical identity, feature, target,
  model, evaluation, score, projection, artifact, value, availability state,
  optimizer result, board output, or recommendation is created or authorized.
- No production authorization follows from retention of this candidate evidence.

## Provider-Contamination Prohibition

No provider or fantasy-platform point, rank, ADP, status, opponent context,
percentage, consensus, analyst output, recommendation, UI signal, or
provider-derived identity or semantic evidence may supplement collection,
provenance, integrity, applicability, semantics, or fallback behavior.

## Fail-Closed and Degraded Behavior

The following visible reason codes preserve no claimed semantic authority and
permit no provider-data or Provider Snapshot Mode fallback:

```text
UPSTREAM_DOCUMENTATION_UNAVAILABLE
UPSTREAM_DOCUMENTATION_UNPINNED
UPSTREAM_DOCUMENTATION_VERSION_UNVERIFIED
UPSTREAM_ORIGIN_UNCONFIRMED
LOCAL_EVIDENCE_SNAPSHOT_MISSING
LOCAL_EVIDENCE_DIGEST_MISSING
LOCAL_EVIDENCE_DIGEST_MISMATCH
RETRIEVAL_REPEAT_DIGEST_MISMATCH
DOCUMENTATION_APPLICABILITY_UNCONFIRMED
TERMS_OR_RIGHTS_REFERENCE_MISSING
PROVIDER_CONTAMINATION_DETECTED
```

Degraded behavior retains evidence references, integrity results, limitations,
and reason codes separately; it makes the failed or unknown condition visible,
creates no false semantic approval, and does not fall back to provider data.

## Assumptions and Limitations

| ID | Assumption / default | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-C01-001 | Dictionary/release-family applicability remains `DOCUMENTATION_APPLICABILITY_UNCONFIRMED`. | Future semantic mapping | P0 if retention is mistaken for applicability approval. | ApexOS Architect | Before any mapping decision. |
| A-C01-002 | Local retention does not grant semantic authority; all source rows remain uninterpreted. | Evidence governance | P0 if source content becomes an implicit mapping. | ApexOS Architect | Immediate and ongoing. |
| A-C01-003 | Upstream content can change after the immutable pin. | Future evidence collection | P1 if a later version is mistaken for this evidence. | ApexOS Architect | Before any revision review. |
| A-C01-004 | Terms may require separate review. | Source governance | P1 if provenance is mistaken for terms approval. | ApexOS Architect | Before operational use. |
| A-C01-005 | Windows checkout line-ending behavior can differ from committed blob bytes. | Evidence integrity | P0 if working-tree conversion is used as blob proof. | ApexOS Architect / Builder | Before any verification run. |
| A-C01-006 | No implementation follows from this retention. | Projection program | P0 if evidence retention is mistaken for build authorization. | ApexOS Architect | Immediate and ongoing. |

## Acceptance Criteria

- Exactly four evidence-only paths are added.
- The immutable upstream pin, byte-preserved raw CSV, checksum, and independent
  repeat-retrieval evidence are retained.
- First response, committed Git blob, and second response have matching byte
  counts and SHA-256 values.
- `DOCUMENTATION_APPLICABILITY_UNCONFIRMED` remains explicit and fail-closed.
- No field-level semantic claim, provider contamination, or production behavior
  is introduced.
- The PR is open, non-draft, evidence-only, and unmerged.

## Builder Handoff Boundary

This evidence-only branch, commit, and PR authorize no parser, CSV ingestion,
raw-data processing, field-semantic mapping, normalized fact, canonical
identity, feature, target, model, evaluation, scoring, artifact, board,
optimizer, recommendation, test, configuration, dependency, or external write.

Any future work requires a separately approved implementation handoff.

## Change Log

- `v0.1` — Retains C-01 at its declared immutable upstream pin as candidate
  dictionary evidence, with binary retrieval and repeat-retrieval integrity
  records. No source applicability or field semantic is approved.
