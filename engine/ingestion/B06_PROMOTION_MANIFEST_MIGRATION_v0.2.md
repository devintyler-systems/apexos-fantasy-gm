# B-06 Promotion Manifest Migration v0.2

## Scope

This implementation-only migration binds newly promoted 2023–2025 nflverse PBP revisions to
the controlling B-06 v0.2 interface plus `b06-no-play-normalization-v0.1`. It does not change
provider Parquet bytes or the `current.json` pointer schema.

## Additive revision-manifest evidence

New manifests retain the existing v0.2 provenance fields and add the handoff evidence needed to
audit provider lineage, reported/computed digest equality, full raw schema, regular-season game
counts, and logical no-play normalization counts. `parser_version` now identifies
`b06-v0.2-evidence-1+b06-no-play-normalization-v0.1`; B-06 v0.3 remains non-controlling.

The new raw-schema snapshot records provider column names, Arrow types, and nullability so a
2024 or 2025 schema delta is visible rather than implicitly treated as equivalent to 2023.

## Compatibility and immutability

Existing immutable revision manifests are never edited or repaired. A controlled rerun must use
an empty season state, as enforced by `tools/run_b06_controlled.ps1`. A prior revision whose raw
SHA-256 path contains an older manifest remains historical evidence and is not silently upgraded.

Missing normalization fields, unexpected `play_type` values, or opportunity-shaped null
`play_type` rows block promotion. A missing provider digest also blocks the 2023–2025 handoff
window. Synthetic acceptance tests cover every new field and fail-closed branch.
