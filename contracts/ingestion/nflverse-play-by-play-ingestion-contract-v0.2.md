# nflverse Play-by-Play Ingestion Contract

**Artifact:** `nflverse_play_by_play_ingestion_contract`
**Version:** 0.2
**Owner:** Builder / Operator
**Status:** APPROVED
**Depends On:** Data Source and Connector Register v1.4 (Section 2.1)
**Unlocks:** B-07 (xTD lookup table)
**Created:** 2026-08-11
**Approved:** 2026-08-11 (Architect), following independent verification against the live
nflverse-data `pbp` release (release ID 58152862) and the repository documentation audit
recorded in Decision Ledger v2.9

---

## 1. Decision Statement

B-06 ingests nflverse play-by-play data directly from nflverse-data GitHub release assets
(release tag `pbp`), using `httpx` for bounded synchronous HTTP retrieval and `pyarrow` for
Parquet metadata/column reads. `nfl_data_py` is explicitly prohibited in this module and
across this repository (Data Source Register v1.4). No adapter code, branch, ingestion run,
or raw-data write is authorized by this contract alone -- it defines the requirement;
implementation is a separate, subsequently-gated Builder ticket (B-06).

---

## 2. Scope and Non-Goals

**In scope:** release discovery, asset selection, download-to-temp-file, SHA-256 computation,
regular-season completeness validation, immutable content-addressed revision storage,
degraded-mode behavior on failure.

**Not in scope:** xTD derivation (B-07), any SQLite/canonical-identity write, any scoring or
projection computation, any postseason/regular-season sampling decision (B-07 owns the
explicit sample-window choice; B-06 only records `game_counts_by_season_type`).

---

## 3. Resolutions (U-B06-01 through U-B06-05)

| ID | Resolution |
|---|---|
| U-B06-01 Dependencies | `httpx>=0.27,<0.29` (sync bounded HTTP retrieval), `pyarrow>=19,<25` (Parquet metadata/column reads). No `pandas` dependency required by B-06. `nfl_data_py` must be absent from the B-06 extra and source tree. Pin ranges in `pyproject.toml`; lock resolved versions in CI. |
| U-B06-02 Discovery | `GET https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp`; select exactly one asset whose `name == "play_by_play_{season}.parquet"` and `state == "uploaded"`. Download the returned `browser_download_url`, never a constructed URL. Record release tag, release ID, asset ID, asset name, asset size, and provider digest if present. Fail closed on zero/multiple exact matches, unexpected extension, missing asset, redirect outside approved GitHub hosts, or non-2xx response. |
| U-B06-03 Completeness | "Complete" = exactly one observed `season` value equal to the requested season; all seven required columns present; readable Parquet; nonzero row/game counts; expected regular-season game count via `season_type == "REG"` and distinct `game_id`. B-06 retains the full raw artifact including postseason rows where published; it does not filter or derive a B-07 sample. Regular-season expected counts are versioned config: 2016-2020: 256; 2021: 272; 2022: 271 (Bills-Bengals cancelled); 2023-2025: 272. |
| U-B06-04 Immutable revisions | Evidence paths: `data/raw/nflverse/pbp/season={season}/revisions/sha256={sha256}/pbp.parquet` with a colocated `manifest.json`. Non-evidence index: `data/raw/nflverse/pbp/season={season}/current.json`, written atomically, containing only the selected manifest path/hash. A provider byte change creates a new revision directory; no retained file is overwritten. A same-hash retrieval writes only a separate retrieval event under `events/`, never duplicate evidence bytes. |
| U-B06-05 Postseason | B-06 stores the provider payload as published and validates regular-season completeness only. It records `game_counts_by_season_type` in the manifest. B-07 must explicitly select its sample window and season types before xTD construction. |

---

## 4. Required Manifest Fields

```json
{
  "source_release_tag": "pbp",
  "source_release_id": 58152862,
  "source_asset_id": "int",
  "source_asset_name": "play_by_play_{season}.parquet",
  "source_asset_size_bytes_reported": "int",
  "source_asset_digest_reported": "sha256:... | null",
  "game_counts_by_season_type": {"REG": "int", "POST": "int"},
  "regular_season_expected_game_count": "int",
  "regular_season_game_count_valid": "bool",
  "revision_sha256": "required-64-character-hex",
  "retrieval_event_id": "uuid-or-content-addressed-id"
}
```

`source_asset_digest_reported` is nullable because older GitHub release assets may lack a
provider digest -- confirmed against the live `pbp` release, where 2019+ season assets carry a
`digest` field and pre-2019 assets do not. ApexOS's own `revision_sha256`, computed from the
downloaded bytes, is always required and authoritative for local reproducibility.

---

## 5. Boundary Rules for Implementation (future B-06 ticket, not authorized by this contract)

- `httpx` writes only to a temporary file in the destination filesystem.
- `pyarrow.parquet.ParquetFile` validates metadata and reads only the columns needed for validation.
- SHA-256 is computed against the exact downloaded temporary-file bytes.
- Promotion uses atomic `os.replace` into a previously non-existent revision directory.
- A failure produces `failed_attempt.json`; it never changes the current revision or reports
  fresh/complete evidence.
- The adapter returns a typed result: `success`, `cached_valid`, or `failed`, plus
  stale/freshness metadata.
- No SQLite, canonical identity, scoring, xTD, projection, roster, draft-state, or
  external-platform write is permitted.

---

## 6. Operations and Degraded Mode

Return `cached_valid` only if an independently valid prior revision exists. Persist
`failed_attempt.json` with UTC time, attempted release/asset URL, failure class, safe error
detail, and prior-valid SHA-256. Otherwise return `failed`. No caller may label cached
evidence as a successful current refresh.

---

## 7. Verification Evidence (Architect, 2026-08-11)

Independently confirmed against the live `nflverse/nflverse-data` `pbp` release (release ID
58152862) before approval: `play_by_play_{season}.parquet` assets present and `state: "uploaded"`
for 2016 through 2025 inclusive; no `play_by_play_2026.*` asset exists; the 2025 asset (asset ID
354718810, size 20,343,981 bytes) carries digest
`sha256:3730c4db2ab99d2dfc4017de975b7610c46c35301b9280b65c03de1b1c74265a`, matching this
contract's manifest example exactly; pre-2019 season assets (e.g., 2016, asset ID 250647177)
report no `digest` field, confirming the nullable-digest design in Section 4. `confirmed evidence`

---

## 8. Decision Ledger Entry

This contract's five resolutions (U-B06-01 through U-B06-05) are approved as design. B-06
implementation remains gated on Builder opening a dedicated branch against this contract; no
branch exists as of this version. See `docs/decision_ledger.md` Version 2.9.
