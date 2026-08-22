# B-06 Controlled Historical Run v1.0

## Purpose and authority

`tools/run_b06_controlled.ps1` is a bounded, local evidence harness for one B-06
nflverse play-by-play season. It does not replace the adapter: only
`engine.ingestion.nflverse_pbp.ingest_nflverse_pbp_season()` may retrieve and write B-06
provider evidence. The harness performs preflight checks, runs the exact synthetic acceptance
suite, permits at most one adapter invocation, and packages review metadata without copying raw
Parquet bytes.

The review recipient is **Perplexity Evidence & Release Reviewer**. A live success remains
`FRESH_SUCCESS_PENDING_REVIEW`; it is not self-approved.

## Safety boundaries

- Use PowerShell 7 and Python 3.12.x from a clean checkout of the exact commit under review.
- Pass one integer season in the B-06 contract window, 2016 through 2025. The controlled 2023
  exercise passes only `-Season 2023`; the harness never loops over seasons.
- `DataRoot` and `RunRoot` must be explicit absolute local paths. Neither may equal, contain, or
  be contained by the other. Keep both outside the repository when practical.
- Never put credentials, authenticated URLs, proxy overrides, or provider bytes in command
  arguments or `RunRoot`.
- Live mode is prohibited if `season=<requested>/current.json` or the requested season's
  `revisions` directory already exists. Existing `failed-attempt-*.json` files are read, hashed,
  and checked for changes; they are not modified.
- The harness has no retry, source fallback, URL override, manual-download, or adapter-config
  path. A live invocation launches the adapter once.
- No GitHub Actions workflow is authorized to use `-ExecuteLive`.

Although `-WhatIf` is the safe operational choice, the mode must be explicit. Omitting both
mode switches, or passing both, is rejected.

## Establish the reviewed commit

From the repository root, capture the full commit before running anything:

```powershell
$expectedCommitSha = (git rev-parse HEAD).Trim()
if ($expectedCommitSha -notmatch '^[0-9a-f]{40}$') { throw 'HEAD is not a full Git SHA.' }
git status --short
python --version
```

The harness independently requires `ExpectedCommitSha` to equal `git rev-parse HEAD`. A mismatch
blocks before the focused tests or adapter invocation. For a post-merge controlled run, use the
reviewed full `main` SHA; for PR-only verification, use the reviewed PR-head SHA.

## Required preflight (`-WhatIf`)

```powershell
.\tools\run_b06_controlled.ps1 `
  -Season 2023 `
  -DataRoot 'C:\ApexOS\data\raw\nflverse\pbp' `
  -RunRoot 'C:\ApexOS\runs' `
  -ExpectedCommitSha $expectedCommitSha `
  -WhatIf
```

This runs exactly:

```text
python -B -m pytest tests/acceptance/test_nflverse_pbp_ingestion.py -p no:cacheprovider -o addopts=
```

It makes no adapter/provider request and writes no B-06 raw evidence. A passing package records
`operation_mode: "what_if"`, `adapter_invocation_attempted: false`,
`provider_request_made: false`, and
`status: "what_if_pass"`.

## One authorized live invocation

Only after the preflight package passes and the reviewer/operator has confirmed the intended
empty season state:

```powershell
.\tools\run_b06_controlled.ps1 `
  -Season 2023 `
  -DataRoot 'C:\ApexOS\data\raw\nflverse\pbp' `
  -RunRoot 'C:\ApexOS\runs' `
  -ExpectedCommitSha $expectedCommitSha `
  -ExecuteLive
```

The focused synthetic suite runs first. The harness then invokes
`ingest_nflverse_pbp_season(2023, <explicit DataRoot>)` once. Do not rerun after a partial or
failed result until an independent reviewer has inspected the package and the immutable failure
events. Never delete, edit, or replace the approved local failed-attempt event to make preflight
look clean.

## Outputs and interpretation

Each invocation creates a unique directory under `RunRoot` whose name includes a UTC timestamp,
`season=<season>`, and an abbreviated expected SHA. The durable files are:

- `console-transcript.txt`
- `review-package.json`

Temporary adapter runner/result files are removed during finalization. Raw `pbp.parquet` remains
only below `DataRoot`; no Parquet is copied anywhere below `RunRoot`, into a transcript or report,
Git, or fixtures. The derived-artifact scan covers `DataRoot`, the current run directory, a
repository-local `data` directory when present, and the enclosing `data` lake when `DataRoot`
uses the documented `data/raw/nflverse/pbp` layout. Preexisting matches are recorded separately;
`derived_artifact_paths` contains only paths that appeared during this invocation.

The package deliberately separates runner activity from provider-request evidence:

| Field | Semantics and evidence rule |
| --- | --- |
| `adapter_invocation_attempted` | Harness-owned fact. It becomes `true` only immediately before the child Python adapter runner is launched. It does not claim that imports completed, the adapter function started, or a provider was contacted. |
| `provider_request_made` | Evidence-derived claim. It is `true` only when this invocation creates a new adapter event containing `source_asset_url` (retrieval event) or `attempted_url` (failed-attempt event). Runner launch, process exit, and `adapter-result.json` alone are not evidence of provider contact. |
| `provider_request_evidence_source` | `retrieval_event`, `failed_attempt_event`, or `none`, according to the qualifying new event. |
| `provider_request_evidence_paths` | Local paths of the qualifying new immutable adapter events. Preexisting events never satisfy the claim. |

Consequently, a local runner failure can produce
`adapter_invocation_attempted: true` with `provider_request_made: false`, source `none`, and no
evidence paths. In this state, `false` means that the package has no qualifying evidence that a
provider request occurred; it is not an independent attestation that no network activity was
possible. Preserve the transcript and package, treat the outcome as `FAILED_OR_STALE`, and do not
retry until reviewed.

The final console line has one of these values:

| Line | Meaning | Operator action |
| --- | --- | --- |
| `B06_CONTROLLED_RUN_STATUS=WHAT_IF_PASS` | Synthetic preflight passed; no provider request occurred. | Review package, then separately authorize live mode if appropriate. |
| `B06_CONTROLLED_RUN_STATUS=FRESH_SUCCESS_PENDING_REVIEW` | The one adapter call returned fresh success and pointer/manifest/payload identities agree. | Stop. Route package and local evidence paths to the reviewer. |
| `B06_CONTROLLED_RUN_STATUS=FAILED_OR_STALE` | Adapter failed, returned cached/stale evidence, or did not produce a trustworthy result. | Stop. Preserve all state and route for review; do not retry. |
| `B06_CONTROLLED_RUN_STATUS=BLOCKED` | A preflight, commit, runtime, path, test, scope, or packaging guard failed. | Correct only the external precondition; do not bypass the guard. |

The machine-readable package records command parameters (no secrets), UTC start/end times,
repository SHA and working-tree status, Python version, focused-test exit code, the runner/request
field split and evidence paths, prior and new
events with content hashes, claims, result fields, pointer/manifest/payload SHA comparisons,
revision identity/timestamps, the 2016 presence check, derived-artifact scan, and limitations.
Null evidence fields are expected only when the status makes that evidence unavailable.

For a fresh 2023 root, reviewers should confirm:

- all three values in `success_evidence.sha_identity` are `true`;
- `scope_scan.season_2016_exists` is `false`;
- `scope_scan.derived_artifact_paths` is empty;
- `scope_scan.raw_parquet_copied_to_run_root` is `false`;
- the result is fresh and not `cached_valid_after_failure`; and
- preexisting failed-attempt hashes remain unchanged.

Do not commit generated run directories or local provider evidence.
