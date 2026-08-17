# B-06 PR #17 Release-Review Evidence v1

**Scope:** documentation and independently reproducible review evidence for the proposed B-06
v0.3 contract only. This is not implementation authorization, an ingestion run, or a source-data
artifact.

## Binding and review state

| Field | Recorded value |
|---|---|
| Repository / PR | `devintyler-systems/apexos-fantasy-gm` / #17 |
| Base SHA | `29c3b9451c52b90a521dd4e8deb1378ebdbc0b22` |
| Pre-remediation reviewed head | `1f5b04a8bfd3d48a007c0d8b3a90932c9a98b9ab` |
| Branch at evidence capture | `architect/b06-v0.3-release-gate` |
| Operator identity | `Codex /root` automated review-evidence operator (not a final Evidence & Release Reviewer verdict) |
| Reviewer identity / verdict | Not issued in this record; `BLOCKED_PENDING_EVIDENCE_AND_RELEASE_REVIEW` remains in force. |
| Session identifier | `PR17-B06-EVIDENCE-20260817T034229Z` |
| Contract inspected | `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.3.md` |

This evidence is deliberately bound to the exact **pre-remediation** head above. The commit that
adds this document, its transcript files, and the review utility changes PR #17's head. An
Evidence & Release Reviewer must re-review the resulting PR against its new exact head; this
record neither supplies nor substitutes for that verdict. The PR must not be merged, marked
ready, or used to authorize B-06 implementation until that reviewer issues PASS for the exact
current head and the PR subsequently merges.

## Independent release-asset observation

The operator made a read-only GitHub API request, independently of the contract text, to
`https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp`. The metadata retrieval
window was `2026-08-17T03:43:04.0627475Z` through `2026-08-17T03:43:04.4769610Z`; the command
used PowerShell 7.6.5.0 and GitHub's release API. The selected release was `pbp`, release ID
`58152862`, API `updated_at` `2026-08-13T12:39:29Z`.

### Provenance reconciliation: historical versus controlling 2025 asset

Decision Ledger v2.9 records a prior 2025 observation for asset ID `354718810`, size
`20,343,981`, and digest `sha256:3730c4db2ab99d2dfc4017de975b7610c46c35301b9280b65c03de1b1c74265a`.
The independent API retrieval in this evidence session instead returned asset ID `512957613`,
size `20,337,029`, and digest
`sha256:c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29` for the same 2025
asset name. The current release endpoint reports its `updated_at` as `2026-08-13T12:39:29Z` and
the exact controlling retrieval window for this evidence is
`2026-08-17T03:43:04.0627475Z`–`2026-08-17T03:43:04.4769610Z`.

This record does not claim a mechanism for the difference (for example, replacement or
re-upload), because the current response alone cannot prove one. The ledger remains a historical
observation. For this evidence run, only the time-bounded current API response and the matching
memory-only schema retrieval are controlling; the old asset ID and digest must not be used to
identify or validate the current asset.

The exact command was:

```powershell
Write-Output "retrieval_started_utc=$(Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ss.fffffffZ')"; $release = Invoke-RestMethod -Headers @{ 'User-Agent' = 'ApexOS-B06-review-only' } -Uri 'https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp'; $release | Select-Object id,tag_name,published_at,updated_at | ConvertTo-Json -Compress; $release.assets | Where-Object { $_.name -in @('play_by_play_2025.parquet','play_by_play_2016.parquet') } | Select-Object id,name,state,size,digest,browser_download_url,updated_at | Sort-Object name | ConvertTo-Json -Compress; Write-Output "retrieval_finished_utc=$(Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ss.fffffffZ')"
```

Its unedited output was:

```text
retrieval_started_utc=2026-08-17T03:43:04.0627475Z
{"id":58152862,"tag_name":"pbp","published_at":"2022-01-28T02:12:09Z","updated_at":"2026-08-13T12:39:29Z"}
[{"id":250647177,"name":"play_by_play_2016.parquet","state":"uploaded","size":19344382,"digest":null,"browser_download_url":"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2016.parquet","updated_at":"2025-04-30T06:34:29Z"},{"id":512957613,"name":"play_by_play_2025.parquet","state":"uploaded","size":20337029,"digest":"sha256:c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29","browser_download_url":"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.parquet","updated_at":"2026-08-13T12:26:09Z"}]
retrieval_finished_utc=2026-08-17T03:43:04.4769610Z
```

### Provider-digest rule reproduced

| Asset | Release / asset ID | Source URL | Provider digest | UTC inspection window | Locally computed SHA-256 |
|---|---|---|---|---|---|
| `play_by_play_2025.parquet` | `pbp` / `512957613` | `https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.parquet` | `sha256:c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29` | `2026-08-17T03:43:15.6325687Z`–`2026-08-17T03:43:16.5929319Z` | `c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29` |
| `play_by_play_2016.parquet` | `pbp` / `250647177` | `https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2016.parquet` | `null` | `2026-08-17T03:43:30.5704556Z`–`2026-08-17T03:43:31.6622099Z` | `95eba04e2145e3c1c8ca502f2a3a76cfb0a5990680c3fb480f02a74a45f54a3b` |

Both downloads were held only in process memory by the review utility. No provider Parquet bytes
were persisted locally. The first source digest equals the independently computed local SHA-256;
the second source digest is absent while a local SHA-256 remains available. This demonstrates the
nullable provider-digest rule, not an ingestion or manifest write.

## Parquet schema transcript (AC-04)

The named 2025 release asset was inspected with Python and `pyarrow` `22.0.0`. The exact command
was:

```powershell
python tools/review/b06_release_schema_evidence.py --asset-url https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.parquet --output docs/evidence/b06-pr17-release-schema-transcript-2025-v1.txt
```

The unedited, durable utility output is
[`b06-pr17-release-schema-transcript-2025-v1.txt`](b06-pr17-release-schema-transcript-2025-v1.txt).
It names every required v0.3 validation column and reports Arrow logical type, Arrow nullability,
Parquet logical type, and Parquet physical type. In particular, the observed binary fields are
all Arrow `double` / Parquet `DOUBLE` (with no Parquet logical annotation): `touchdown`,
`rush_attempt`, and `pass_attempt`.

The same tool generated the durable no-provider-digest asset transcript:
[`b06-pr17-release-schema-transcript-2016-v1.txt`](b06-pr17-release-schema-transcript-2016-v1.txt).
Those files are generated from source metadata only; they contain no source rows or raw payload.

## Review-only utility and reproduction

`tools/review/b06_release_schema_evidence.py` is intentionally outside `engine/`, is not in the
project package discovery path, and contains no promotion, storage, validation-of-rows, or
ingestion behavior. It accepts exactly one read-only input:

```powershell
# Remote source: memory-only download; prints a deterministic transcript.
python tools/review/b06_release_schema_evidence.py --asset-url <release-browser-download-url>

# Local source: reads an operator-supplied Parquet file; prints a deterministic transcript.
python tools/review/b06_release_schema_evidence.py --parquet <local-parquet-path>
```

Optional `--output` is limited by the utility to the named gitignored `.review-evidence/` scratch
directory or `docs/evidence/` for a committed transcript. It exits `2` if one or more of the
seven required columns is absent. A URL input is read into memory only; it does not create a
Parquet file. The transcript includes SHA-256 for both local-file and memory-only URL inputs.

The narrow utility-only failure-path check was:

```powershell
pytest tests/review/test_b06_release_schema_evidence.py -q
```

```text
.                                                                        [100%]
```

It proves only that the review utility returns nonzero when its synthetic temporary metadata
fixture omits `pass_attempt`; it is not B-06 adapter acceptance-test execution.

## `nfl_data_py` active-use scan

Allowed historical/reference paths are limited to contract, ledger, architecture, addendum,
review-evidence, audit, and migration records that state the package's former status or its
prohibition. In this snapshot those paths include:

- `docs/decision_ledger.md`, `docs/architect-continuation-prompt.md`, and
  `docs/data_source_connector_register.md`;
- `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md` and v0.3;
- `contracts/projections/projection-artifact-contract-v1.0.md` and
  `projection-artifact-contract-v1.2-addendum.md`; and
- this evidence document and its review transcript files.

Prohibited active-use path classes are importable/executable source (`engine/**`, `src/**`,
`tests/**`, and executable `tools/**` or `scripts/**`), dependency and lock manifests
(`pyproject.toml`, `requirements*.txt`, `Pipfile*`, `poetry.lock`, `uv.lock`), CI/workflows
(`.github/**`), install commands, and active Builder instructions or kickoff material that
authorizes use. Historical references are not evidence of active use.

The executable/dependency/workflow scan command and captured output were:

```powershell
rg -n -i -S "(^|[^A-Za-z0-9_])(from|import)[[:space:]]+nfl_data_py|nfl_data_py[[:space:]]*(==|>=|<=|~=)|pip[[:space:]]+install[^\r\n]*nfl_data_py" engine tests tools .github pyproject.toml 2>$null; if ($LASTEXITCODE -eq 1) { Write-Output "NO_ACTIVE_USE_MATCHES"; exit 0 } else { exit $LASTEXITCODE }
```

```text
NO_ACTIVE_USE_MATCHES
```

The active Builder-instruction scan command and captured output were:

```powershell
rg -n -i -S "nfl_data_py" docs/builder-operator-implementation-backlog-v1.0.md docs/builder-kickoff-prompt.md 2>$null; if ($LASTEXITCODE -eq 1) { Write-Output "NO_ACTIVE_BUILDER_INSTRUCTION_REFERENCES"; exit 0 } else { exit $LASTEXITCODE }
```

```text
docs/builder-operator-implementation-backlog-v1.0.md:9:**Amended:** 2026-08-11 -- B-01 and B-06 updated to remove `nfl_data_py` and point to
docs/builder-operator-implementation-backlog-v1.0.md:74:| B-01 | Set up Python project structure (`pyproject.toml`, virtualenv, `httpx>=0.27,<0.29` + `pyarrow>=19,<25` (B-06 ingestion) + `pandas`/`polars` + `pytest` deps). `nfl_data_py` MUST be absent from all dependency groups, lockfile, and source tree per Data Source Register v1.4 | Data Source Register v1.4 | `pip install -e .` succeeds; `pytest` runs (even with 0 tests passing yet); dependency scan confirms no `nfl_data_py` reference | Everything below |
docs/builder-operator-implementation-backlog-v1.0.md:89:| B-06 | Implement nflverse play-by-play ingestion via direct GitHub release assets (release tag `pbp`, `httpx`+`pyarrow`, NO `nfl_data_py`), 2016-2025 seasons minimum, per `nflverse-play-by-play-ingestion-contract-v0.2.md`. Immutable, content-addressed revisions; regular-season completeness validation; postseason rows retained but not sampled | B-01, Data Source Register 2.1 (v1.4) | Raw play-by-play pulled and cached locally as immutable Parquet revisions under `data/raw/nflverse/pbp/season={season}/revisions/sha256={sha256}/`, each with a companion manifest | B-07 |
docs/builder-operator-implementation-backlog-v1.0.md:149:- B-06 specifically: repository scan confirms zero `nfl_data_py` references in dependencies, lockfile, or imports (per Data Source Register v1.4)
docs/builder-operator-implementation-backlog-v1.0.md:157:**2026-08-11 amendment:** B-01 and B-06 updated to remove `nfl_data_py` and reference direct
```

Each Builder-instruction match is prohibitory or historical; none authorizes the package. This
scan is evidence of the current text only. The AC-15 positive/negative repository fixture remains
required before implementation PASS.

## Filesystem and concurrency support boundary

No supported filesystem, create-if-absent primitive, or recovery behavior has been independently
selected or demonstrated. The source schema evidence cannot establish those local filesystem
properties. Accordingly, no immutable-promotion guarantee is claimed here.

| Architecture item | State | Later evidence required |
|---|---|---|
| Supported filesystem boundary | `BLOCKED` | Identify supported local filesystem(s), platform/version, and test environment. |
| Create-if-absent primitive | `BLOCKED` | Name the exact primitive and demonstrate exclusive creation under contention on each supported filesystem. |
| Durable claim state machine | `DEFERRED_UNTIL_IMPLEMENTATION` | Implementation test proving durable terminal claim records and fail-closed behavior. |
| Lock/abandoned-claim recovery | `BLOCKED` | A reviewed recovery policy plus crash/abandonment tests; none is evidenced by this review. |
| Same-hash and different-byte contention | `DEFERRED_UNTIL_IMPLEMENTATION` | Concurrent promotion fixtures, event-count checks, path/hash checks, and deterministic pointer-order tests. |

## Acceptance matrix

`PASS` means independently reproduced in this evidence session only. Contract-only requirements
that cannot execute without a B-06 implementation are explicitly deferred; a final reviewer
verdict is not asserted.

| Criterion | Required claim | Evidence / fixture | Expected outcome | Observed outcome | Status | Evidence location |
|---|---|---|---|---|---|---|
| AC-01 | Required subset rejects each missing required column and preserves extra raw columns. | Utility-only synthetic missing-`pass_attempt` test; no adapter fixture. | Seven omission fixtures reject; extra bytes survive. | Utility exits nonzero for one missing column; adapter behavior and retained-byte comparison are not executable. Later: seven minimal omission fixtures plus retained-byte comparison. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §9; `tests/review/test_b06_release_schema_evidence.py`. |
| AC-02 | Required/nullable column rules are enforced. | No row-validation implementation or null fixtures. | Required nulls reject; permitted nulls follow contract. | Not executable. Later: one null fixture per required column. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §4.2, §9. |
| AC-03 | Prohibited types/domains reject with classified failure. | No validation implementation or invalid-value fixtures. | Every prohibited type/domain rejects. | Not executable. Later: invalid season/type/game/yardline/binary fixtures. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §4.2–§4.3, §9. |
| AC-04 | Named release asset transcript identifies seven columns and binary representations. | Independently retrieved 2025 asset `512957613`; PyArrow 22.0.0 transcript. | All seven named; binary Arrow and Parquet types recorded. | All seven present; three binary fields are Arrow `double`, Parquet `DOUBLE`. | `PASS` | `b06-pr17-release-schema-transcript-2025-v1.txt`. |
| AC-05 | Provider digest persists and local SHA-256 is mandatory/matches bytes. | 2025 asset metadata and memory-only local SHA-256. | Provider digest present; local SHA-256 agrees. | Provider `sha256:c6ec…df29` equals local `c6ec…df29`. | `PASS` | Release observation above; 2025 transcript. |
| AC-06 | Null provider digest is retained while local SHA-256 remains authoritative. | 2016 asset `250647177` metadata and memory-only local SHA-256. | Provider digest null; local SHA-256 available. | Provider digest `null`; local SHA-256 `95eba0…54a3b`. | `PASS` | Release observation above; 2016 transcript. |
| AC-07 | Discovery failure leaves evidence/pointer unchanged and returns allowed outcome only. | No adapter or failure simulation. | No mutation; allowed fallback only with valid prior revision. | Not executable. Later: zero/multiple/non-2xx/redirect/metadata simulations. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §3.1, §5.2, §9. |
| AC-08 | Invalid Parquet prevents promotion and preserves pointer. | No adapter or corrupt fixture. | Failed attempt only; no promotion/pointer change. | Not executable. Later: corrupt/unreadable Parquet fixture. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §8–§9. |
| AC-09 | Incorrect REG game count rejects. | No adapter or game-count fixture. | Candidate not current. | Not executable. Later: valid-schema incorrect-count fixture. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §4.4, §9. |
| AC-10 | Same-hash contention makes one evidence revision and separate events. | No supported filesystem/primitive or implementation. | One payload/manifest; deterministic outcomes/pointer. | Support boundary unresolved; no contention test. | `BLOCKED` | Filesystem boundary above; Contract §6. |
| AC-11 | Different-byte contention creates distinct revisions and ordered pointer. | No supported filesystem/primitive or implementation. | No overwrite; pointer follows ordering key. | Support boundary unresolved; no contention test. | `BLOCKED` | Filesystem boundary above; Contract §6. |
| AC-12 | Retained evidence cannot be overwritten/replaced. | No selected filesystem primitive or promotion implementation. | Paths/hashes immutable; replace attempt prohibited. | No durable filesystem guarantee evidenced. | `BLOCKED` | Filesystem boundary above; Contract §6.1. |
| AC-13 | Pointer changes only for winning successful publication. | No pointer implementation or ordered-candidate fixture. | Other cases byte-identical. | Not executable; depends on unresolved claim boundary. | `BLOCKED` | Filesystem boundary above; Contract §6.4. |
| AC-14 | Failed refresh with valid prior revision is visibly stale only. | No adapter or forced-failure fixture. | Exactly `cached_valid_after_failure`; no fresh wording. | Not executable. Later: forced refresh failure with valid prior revision. | `DEFERRED_UNTIL_IMPLEMENTATION` | Contract §5.2, §8–§9. |
| AC-15 | Active use is rejected while permitted historical/prohibition references remain allowed. | Captured executable/dependency/workflow and Builder-text scans; no positive/negative fixtures. | Active use fails; permitted references pass. | Current scan has no active-use match; Builder matches are prohibitions. Fixture proof still absent. | `DEFERRED_UNTIL_IMPLEMENTATION` | Active-use scan above; Contract §7, §9. |
| AC-16 | Independent reviewer reruns evidence and records identity/session/time/current head/result. | This operator record binds the pre-remediation head only; no final independent reviewer verdict. | Reviewer evidence for exact current head; self-assertion insufficient. | Final reviewer rerun and verdict absent; remediation changes head. | `BLOCKED` | Binding section; this document. |

## Remaining release block

This record closes only the named-release schema transcript and nullable-digest evidence gap for
the pre-remediation reviewed head. It does not close the independent-review, implementation-test,
or filesystem/concurrency boundaries. B-06 remains blocked and no Builder branch, ingestion
adapter, ingestion job, raw data, canonical data, database rows, or production artifact is
authorized by this evidence.
