# nflverse Raw-Evidence Capture Runbook v0.1

## Purpose and strict boundary

This runbook covers capture of exactly one explicitly selected historical
nflverse direct GitHub release asset into immutable local raw evidence. The
capture boundary records and validates evidence only. It does not browse
releases, select an asset, sweep seasons, resolve canonical identities, or
produce features, projections, scores, ranks, or recommendations.

## Required governing contracts

- `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`
- `contracts/projections/apexos-projection-feature-and-score-lineage-contract-v0.1.md`
- `contracts/projections/apexos-projection-source-authorization-register-v0.1.md`
- `contracts/projections/apexos-nflverse-authorization-reconciliation-v0.1.md`

The bounded source ID is `nflverse_direct_github_release_assets`; the release
tag is `pbp`; and the only accepted asset name is
`play_by_play_{season}.parquet` for one requested season from 2016 through
2025 inclusive. `nfl_data_py` is prohibited.

## Allowed invocation inputs

The CLI requires explicit `--season`, `--asset-url`, `--as-of-timestamp`, and
`--output-root` values. It also requires `--expected-sha256`, except when both
`--fixture-mode` and `--allow-unsigned-for-local-fixture` are explicitly set.
Optional bounded inputs are expected byte count, parser version, and source
contract version. The CLI never discovers or infers an asset.

Example production-shaped invocation:

```text
python tools/capture_nflverse_raw_evidence.py --season 2024 --asset-url <explicit-approved-github-release-asset-url> --as-of-timestamp <RFC3339-UTC> --output-root <local-evidence-root> --expected-sha256 <64-lowercase-hex>
```

The CLI prints one JSON result and performs no display or decision rendering.

## Immutable snapshot layout

```text
<output-root>/
  raw/<snapshot_id>/play_by_play_<season>.parquet
  manifests/<snapshot_id>.json
  quarantine/<snapshot_id>.jsonl
```

The snapshot ID is deterministic from source ID, release tag, asset name, raw
SHA-256, parser version, and source-contract version. Temporary files are
fully written and synchronized before create-only publication. The manifest
is the final completion marker. Existing evidence is verified for idempotency
and is never overwritten; inconsistent evidence returns `SNAPSHOT_CONFLICT`.

### Cross-platform immutable publication

Final snapshot publication uses a bounded, cross-platform create-only
publication lock and does not depend on hard-link behavior. Raw bytes and
quarantine output publish before the manifest; the manifest publishes last and
is the only completion marker. Concurrent identical captures converge to one
complete immutable snapshot. A non-winning caller validates that complete set
and returns idempotent success without rewriting its raw bytes.

Incomplete, unreadable, or inconsistent final evidence fails closed with
`SNAPSHOT_CONFLICT`; no final evidence is overwritten. On any failure, only
temporary files created by the current caller may be cleaned. A caller never
deletes unverified final evidence that could belong to another publisher.
Publication lock acquisition uses a deterministic bounded retry of 20 attempts
with a 10-millisecond delay. Retries never alter asset identity, bytes, hash,
timestamps, lineage, or source selection.

Native Windows reproduction evidence is still required before production
operational-capture authorization if this environment-specific incident has not
been exercised on a native Windows operational-capture environment.

#### Stale Lock Recovery and Diagnostics

Each publication lock contains create-only `owner.json` metadata: lock protocol
version, snapshot ID, unique attempt ID, RFC3339 UTC acquisition time, process
ID, host identifier, raw SHA-256, asset name, and source ID. PID and hostname
are diagnostic only; neither proves liveness or permits lock deletion.

A lock is eligible for recovery only after 300 seconds under the injected UTC
clock, with valid matching owner metadata and no final raw, quarantine, or
manifest evidence. Reclamation requires atomic ownership transfer and
owner-byte revalidation. An expired lock with complete equivalent
manifest-bearing evidence returns idempotent success without replacing final
evidence; partial or conflicting evidence returns `SNAPSHOT_CONFLICT`.

`SNAPSHOT_LOCK_UNAVAILABLE` means a publication lock exists but cannot be safely acquired or reclaimed because it is active, recent, unreadable,
malformed, future-dated, foreign, changed during verification, or otherwise
owner-ambiguous. The safe operator action is to preserve the lock directory,
owner metadata, reason code, and any final evidence; do not manually delete or
overwrite them; investigate and retry only after the documented stale-lock
protocol can evaluate the state. Recovery never changes the selected asset,
retries a source, invokes a provider fallback, permits a live-current claim,
or permits an external write.

## Manifest and provenance contents

Every successful manifest contains snapshot and source IDs, source URL,
release tag, asset name and URL, season, retrieval/effective/as-of timestamps,
computed and expected integrity values, parser and source-contract versions,
the source-register rights/terms reference, schema validation, parsed row
count, identity-quarantine summary, reason codes, limitations, and degraded
state.

Fixed declarations are:

```json
{
  "freshness_status": "historical_snapshot",
  "projection_authority": "none_raw_evidence_only",
  "provider_projection_fields_used": false,
  "rights_or_terms_reference": "docs/data_source_connector_register.md"
}
```

## Validation and time-integrity rules

Raw bytes are captured and hashed before parsing. Supplied SHA-256 and byte
count must match. The asset must be readable Parquet containing `season`,
`week`, `game_id`, `posteam`, `defteam`, and `play_type`. This is a minimal
evidence-validation subset, not a feature schema or event model.

As-of and effective timestamps must be RFC3339 UTC. An effective timestamp
later than the as-of timestamp returns `TIME_INTEGRITY_FAILED`. Missing source
effective time remains visible as `SOURCE_FRESHNESS_UNKNOWN`; it never becomes
a current, live, synchronized, or platform-validated claim.

## Identity quarantine behavior

Capture performs identity-safety inspection only. Null or blank values in
present required source identity fields are written as
`IdentityQuarantineRecord` entries with `CANONICAL_IDENTITY_UNRESOLVED`.
Nothing is guessed, destructively merged, added to a canonical table, or
written to a database.

## Degraded mode and reason codes

Every failure returns a structured result with `degraded_mode: true`, at least
one explicit reason code, and a known limitation. The supported vocabulary is:

```text
UNSUPPORTED_SEASON
INVALID_ASSET_IDENTITY
HTTP_RETRIEVAL_FAILED
SOURCE_SNAPSHOT_MISSING
HASH_MISMATCH
BYTE_COUNT_MISMATCH
MALFORMED_PARQUET
REQUIRED_SCHEMA_FIELD_MISSING
INVALID_TIMESTAMP
TIME_INTEGRITY_FAILED
SNAPSHOT_CONFLICT
FILESYSTEM_WRITE_FAILED
CANONICAL_IDENTITY_UNRESOLVED
SOURCE_FRESHNESS_UNKNOWN
PROVIDER_CONTAMINATION_DETECTED
FIXTURE_MODE_NOT_PRODUCTION
SNAPSHOT_LOCK_UNAVAILABLE
```

There is no provider projection or provider fallback. Failed evidence never
produces a false success or freshness claim.

## Fixture-mode warning

Fixture mode exists only for local deterministic validation. Unsigned capture
is rejected unless both fixture flags are present. Fixture mode visibly emits
`FIXTURE_MODE_NOT_PRODUCTION`; its output must not be represented as production
source evidence.

## Explicit non-goals

- No provider projection or provider fallback.
- No ApexOS event projection.
- No fantasy scoring.
- No decision adapter or recommendation behavior.
- No external write.
- No feature engineering, model training, calibration, rank, replacement
  value, availability, scarcity, roster-fit, wait-cost, or board behavior.

## Verification commands

```text
python -m pytest tests/acceptance/test_u08_nflverse_candidate_evidence_authorization_v0_1.py -q
python -m pytest tests/acceptance/test_nflverse_raw_evidence_ingestion.py -q
python -m pytest tests/acceptance -q
python -m compileall engine/ingestion tools/capture_nflverse_raw_evidence.py
git diff --check
```

All ingestion acceptance tests use only local fixture bytes and injected
fixture transport. They do not retrieve a live release asset.

## Rollback and retention boundary

Rollback means stopping callers from using the new capture entry point and
reverting the code change. A validated published raw snapshot is immutable
evidence and is not overwritten or deleted by rollback. Incomplete temporary
files may be removed safely; manifest-bearing snapshots require separate
retention authorization before any removal. No external system is mutated.
