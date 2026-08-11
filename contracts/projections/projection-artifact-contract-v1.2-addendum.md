# Projection Artifact Contract — v1.2 Addendum

**Supersedes:** Section 5 source line, and the `source_citations` field in Sections 6a/6b/6c,
in `projection-artifact-contract-v1.0.md`
**Resolves:** Structural conflict between the v1.0 contract's `nfl_data_py` source citation
format and Data Source Register v1.4 (`nfl_data_py` PROHIBITED, direct nflverse-data GitHub
release-asset access APPROVED)
**Status:** APPROVED
**Created:** 2026-08-11

---

## 1. Decision Statement

Projection Artifact Contract v1.0 assumed nflverse play-by-play data would be sourced via the
`nfl_data_py` Python wrapper package and cited projections as `nflverse:nfl_data_py:v{package_version}`.
Data Source Register v1.4 prohibits `nfl_data_py` and approves direct nflverse-data GitHub
release-asset access instead, per the `nflverse-play-by-play-ingestion-contract-v0.2.md` (B-06).
This addendum updates the source line and citation format to match, without altering any
modeling logic, weight, or acceptance test threshold. `design decision`

---

## 2. Rationale

`nfl_data_py` is an archived, read-only upstream package. Citing a "package version" for a
package that will receive no further releases is not a meaningful freshness or provenance
signal. B-06 instead produces a per-file manifest carrying the release ID, asset ID, and a
locally computed SHA-256 of the downloaded bytes (`revision_sha256`) — a stronger, self-
verifying provenance chain than a package version string ever was. `confirmed evidence`

---

## 3. Implementation Rule

```text
Section 5 source line changes from:
  "Source: nflverse play-by-play data via nfl_data_py (2016-2025 window minimum)"
to:
  "Source: nflverse play-by-play data via direct nflverse-data GitHub release assets
   (2016-2025 window minimum), per nflverse-play-by-play-ingestion-contract-v0.2.md.
   nfl_data_py is prohibited (Data Source Register v1.4)."

Section 6a/6b/6c source_citations field changes from:
  nflverse:nfl_data_py:v{package_version}
to:
  nflverse:pbp:{release_id}:{revision_sha256}

Section 10 Builder Handoff item 1 changes from:
  "Implement nflverse ingestion (`nfl_data_py` pull for 2023-2025 seasons minimum)"
to:
  "Implement nflverse ingestion via direct nflverse-data GitHub release assets
   (B-06, no `nfl_data_py`) for 2016-2025 seasons minimum"
  -- this also corrects a pre-existing internal inconsistency in v1.0, where Section 10
  stated a 2023-2025 window against Section 5's 2016-2025 window. 2016-2025 is authoritative,
  matching Data Source Register 2.1 and the B-06 v0.2 ingestion contract. `confirmed evidence`
```

No other section of v1.0 is altered. All acceptance tests PA01-PA10 remain in force unchanged;
PA01 (Source Citation Completeness) now validates against the updated citation format above.

---

## 4. Acceptance Test Update

### PA01 — Source Citation Completeness (BLOCK, restated)
```
Every projection row must have a non-empty source_citations list referencing only sources
marked APPROVED in Data Source and Connector Register v1.4. nflverse citations must use the
format nflverse:pbp:{release_id}:{revision_sha256}. Any citation string containing
"nfl_data_py" fails this test.
```

---

## 5. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| P07 | `{revision_sha256}` in the citation string assumes B-06 has already validated and promoted the revision before B-07/B-08 consume it | `design decision` | LOW -- B-06's manifest/current.json design (v0.2 ingestion contract) makes an unvalidated revision unreachable by construction |

---

## 6. Decision Ledger Entry

This addendum resolves the structural conflict between the v1.0 contract and Data Source
Register v1.4 without altering any modeling logic. See `docs/decision_ledger.md` Version 2.9
for the full verification trail (live nflverse-data release inspection) that preceded this
approval.
