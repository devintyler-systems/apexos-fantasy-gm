param(
    [Parameter(Mandatory = $true)]
    [int]$Season,

    [Parameter(Mandatory = $true)]
    [string]$DataRoot,

    [Parameter(Mandatory = $true)]
    [string]$RunRoot,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedCommitSha,

    [switch]$WhatIf,
    [switch]$ExecuteLive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$HarnessVersion = "1.1.0"
$FocusedTestCommand = "python -B -m pytest tests/acceptance/test_nflverse_pbp_ingestion.py tests/acceptance/test_b06_no_play_logical_field.py -p no:cacheprovider -o addopts="
$ExitCode = 2
$FinalStatus = "blocked"
$AdapterInvocationAttempted = $false
$ProviderRequestMade = $false
$ProviderRequestEvidenceSource = "none"
$ProviderRequestEvidencePaths = @()
$AdapterInvocationCount = 0
$TranscriptStarted = $false
$RunDirectory = $null
$ReviewPackagePath = $null
$TranscriptPath = $null
$AdapterRunnerPath = $null
$AdapterResultPath = $null
$Package = $null
$StartedAtUtc = [DateTimeOffset]::UtcNow
$EndedAtUtc = $null
$InitialWorkingDirectory = (Get-Location).Path
$RepositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$NormalizedDataRoot = $null
$NormalizedRunRoot = $null
$PythonVersion = $null
$FocusedTestExitCode = $null
$HeadSha = $null
$WorkingTreeStatus = @()
$WorkingTreeDirty = $false
$PriorFailedAttempts = @()
$PriorFailureHashes = @{}
$PreexistingEventHashes = @{}
$PreexistingDerivedArtifactPaths = @()
$PreexistingCurrent = $false
$PreexistingRevisions = $false
$PostexistingCurrent = $false
$PostexistingRevisions = $false
$PriorFailuresUnchanged = $true
$Events = @()
$Claims = @()
$KnownLimitations = @(
    "The harness records local filesystem and adapter evidence; it does not independently attest provider-side state.",
    "Path containment is evaluated using normalized local paths and does not resolve nonexistent-path symbolic-link targets."
)

function Get-UtcTimestamp {
    return [DateTimeOffset]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}

function Normalize-LocalAbsolutePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ([string]::IsNullOrWhiteSpace($Path) -or -not [IO.Path]::IsPathFullyQualified($Path)) {
        throw "$Label must be an explicit absolute local path."
    }
    if ($Path.StartsWith("\\") -or $Path.StartsWith("//")) {
        throw "$Label must be local and cannot be a UNC path."
    }
    $fullPath = [IO.Path]::GetFullPath($Path)
    $pathRoot = [IO.Path]::GetPathRoot($fullPath)
    if ($fullPath.Length -gt $pathRoot.Length) {
        $fullPath = $fullPath.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    }
    return $fullPath
}

function Test-SameOrNestedPath {
    param(
        [Parameter(Mandatory = $true)][string]$Candidate,
        [Parameter(Mandatory = $true)][string]$Parent
    )

    $relative = [IO.Path]::GetRelativePath($Parent, $Candidate)
    if ($relative -eq ".") {
        return $true
    }
    if ([IO.Path]::IsPathRooted($relative)) {
        return $false
    }
    return -not ($relative -eq ".." -or $relative.StartsWith("..$([IO.Path]::DirectorySeparatorChar)"))
}

function Get-FileSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Read-JsonEvidence {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Kind
    )

    $raw = [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8)
    $content = $raw | ConvertFrom-Json
    return [ordered]@{
        kind = $Kind
        path = [IO.Path]::GetFullPath($Path)
        sha256 = Get-FileSha256 -Path $Path
        content = $content
    }
}

function Get-FailureEvidence {
    param([Parameter(Mandatory = $true)][string]$SeasonRoot)

    $eventsRoot = Join-Path $SeasonRoot "events"
    if (-not (Test-Path -LiteralPath $eventsRoot -PathType Container)) {
        return @()
    }
    return @(
        Get-ChildItem -LiteralPath $eventsRoot -File -Filter "failed-attempt-*.json" |
            Sort-Object FullName |
            ForEach-Object { Read-JsonEvidence -Path $_.FullName -Kind "failed_attempt" }
    )
}

function Get-AllEventEvidence {
    param([Parameter(Mandatory = $true)][string]$SeasonRoot)

    $eventsRoot = Join-Path $SeasonRoot "events"
    if (-not (Test-Path -LiteralPath $eventsRoot -PathType Container)) {
        return @()
    }
    return @(
        Get-ChildItem -LiteralPath $eventsRoot -File -Filter "*.json" |
            Sort-Object FullName |
            ForEach-Object {
                $kind = if ($_.Name.StartsWith("failed-attempt-")) { "failed_attempt" } else { "retrieval" }
                Read-JsonEvidence -Path $_.FullName -Kind $kind
            }
    )
}

function Get-ClaimEvidence {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][int]$RequestedSeason
    )

    $claimsRoot = Join-Path $Root "claims"
    if (-not (Test-Path -LiteralPath $claimsRoot -PathType Container)) {
        return @()
    }
    return @(
        Get-ChildItem -LiteralPath $claimsRoot -File -Recurse -Filter "*.json" |
            Where-Object { $_.FullName -match "[\\/]season=$RequestedSeason([\\/]|$)" } |
            Sort-Object FullName |
            ForEach-Object { Read-JsonEvidence -Path $_.FullName -Kind "claim" }
    )
}

function Test-ProviderRequestEvidenceEvent {
    param([Parameter(Mandatory = $true)]$Event)

    if ($Event.kind -eq "retrieval") {
        $urlProperty = $Event.content.PSObject.Properties["source_asset_url"]
        return $null -ne $urlProperty -and -not [string]::IsNullOrWhiteSpace([string]$urlProperty.Value)
    }
    if ($Event.kind -eq "failed_attempt") {
        $urlProperty = $Event.content.PSObject.Properties["attempted_url"]
        return $null -ne $urlProperty -and -not [string]::IsNullOrWhiteSpace([string]$urlProperty.Value)
    }
    return $false
}

function Get-DerivedArtifactPaths {
    param([Parameter(Mandatory = $true)][string[]]$Roots)

    $pattern = "(?i)(^|[\\/_.-])(xtd|projections?|scoring|recommendations?|streamlit|ui)([\\/_.-]|$)"
    $matches = @()
    foreach ($root in @($Roots | Sort-Object -Unique)) {
        if (Test-Path -LiteralPath $root -PathType Container) {
            $matches += @(
                Get-ChildItem -LiteralPath $root -File -Recurse |
                    Where-Object { $_.FullName -match $pattern } |
                    ForEach-Object { $_.FullName }
            )
        }
    }
    return @($matches | Sort-Object -Unique)
}

function Get-DerivedScanRoots {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$CurrentRunDirectory,
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )

    $scanRoots = @($Root, $CurrentRunDirectory)
    $dataRootLeaf = Split-Path -Leaf $Root
    $nflverseRoot = Split-Path -Parent $Root
    $rawRoot = Split-Path -Parent $nflverseRoot
    $dataLakeRoot = Split-Path -Parent $rawRoot
    if (
        $dataRootLeaf -ieq "pbp" -and
        (Split-Path -Leaf $nflverseRoot) -ieq "nflverse" -and
        (Split-Path -Leaf $rawRoot) -ieq "raw"
    ) {
        $scanRoots += $dataLakeRoot
    }
    $repositoryDataRoot = Join-Path $RepoRoot "data"
    if (Test-Path -LiteralPath $repositoryDataRoot -PathType Container) {
        $scanRoots += $repositoryDataRoot
    }
    return @($scanRoots | Sort-Object -Unique)
}

function Invoke-FocusedTests {
    Write-Host "FOCUSED_TEST_COMMAND=$FocusedTestCommand"
    & python -B -m pytest tests/acceptance/test_nflverse_pbp_ingestion.py tests/acceptance/test_b06_no_play_logical_field.py -p no:cacheprovider -o "addopts=" 2>&1 |
        ForEach-Object { Write-Host $_ }
    $focusedExitCode = $LASTEXITCODE
    return [int]$focusedExitCode
}

function Invoke-AdapterOnce {
    param(
        [Parameter(Mandatory = $true)][int]$RequestedSeason,
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$ResultPath
    )

    if ($script:AdapterInvocationCount -ne 0) {
        throw "The B-06 adapter may be invoked at most once per harness invocation."
    }
    $script:AdapterInvocationCount++

    $runnerSource = @'
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

season = int(sys.argv[1])
data_root = Path(sys.argv[2])
result_path = Path(sys.argv[3])
repository_root = Path(sys.argv[4]).resolve()
sys.path.insert(0, str(repository_root))

from engine.ingestion import nflverse_pbp

adapter_module_path = Path(nflverse_pbp.__file__).resolve()
adapter_module_sha256 = hashlib.sha256(adapter_module_path.read_bytes()).hexdigest()
ingest_nflverse_pbp_season = nflverse_pbp.ingest_nflverse_pbp_season
result = ingest_nflverse_pbp_season(season, data_root)
payload = asdict(result)
if payload["manifest_path"] is not None:
    payload["manifest_path"] = str(payload["manifest_path"])
payload["adapter_module_path"] = str(adapter_module_path)
payload["adapter_module_sha256"] = adapter_module_sha256
result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
'@
    [IO.File]::WriteAllText($script:AdapterRunnerPath, $runnerSource, [Text.UTF8Encoding]::new($false))
    $script:AdapterInvocationAttempted = $true
    & python -B $script:AdapterRunnerPath $RequestedSeason $Root $ResultPath $RepositoryRoot 2>&1 |
        ForEach-Object { Write-Host $_ }
    $adapterExitCode = $LASTEXITCODE
    return [int]$adapterExitCode
}

function New-BaseReviewPackage {
    param([Parameter(Mandatory = $true)][string]$OperationMode)

    return [ordered]@{
        artifact_type = "b06_controlled_run_review_package"
        harness_version = $HarnessVersion
        generated_at_utc = $null
        operation_mode = $OperationMode
        adapter_invocation_attempted = $false
        provider_request_made = $false
        provider_request_evidence_source = "none"
        provider_request_evidence_paths = @()
        requested_season = $Season
        command_parameters = [ordered]@{
            season = $Season
            data_root = $NormalizedDataRoot
            run_root = $NormalizedRunRoot
            expected_commit_sha = $ExpectedCommitSha
            what_if = [bool]$WhatIf
            execute_live = [bool]$ExecuteLive
        }
        started_at_utc = $StartedAtUtc.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        ended_at_utc = $null
        repository = [ordered]@{
            root = $RepositoryRoot
            head_sha = $null
            expected_sha = $ExpectedCommitSha
            is_expected_sha = $false
            working_tree_dirty = $false
            working_tree_porcelain_v1 = @()
            working_tree_status = @()
        }
        runtime = [ordered]@{
            python_version = $null
            working_directory = $InitialWorkingDirectory
            focused_test_command = $FocusedTestCommand
            focused_test_exit_code = $null
            adapter_module_path = $null
            adapter_module_sha256 = $null
            adapter_module_matches_repository = $false
        }
        data_root = [ordered]@{
            path = $NormalizedDataRoot
            season_root = Join-Path $NormalizedDataRoot "season=$Season"
            preexisting_current_json = $false
            preexisting_revisions_directory = $false
            postexisting_current_json = $false
            postexisting_revisions_directory = $false
            prior_failed_attempts = @()
            prior_failed_attempts_unchanged = $true
        }
        result = [ordered]@{
            status = $null
            season = $Season
            revision_sha256 = $null
            manifest_path = $null
            failure_class = $null
            failure_detail = $null
            freshness = $null
            stale_banner_required = $false
        }
        success_evidence = [ordered]@{
            current_json = $null
            manifest = $null
            payload = [ordered]@{
                path = $null
                size_bytes = $null
                sha256 = $null
            }
            sha_identity = [ordered]@{
                pointer_equals_manifest = $null
                manifest_equals_payload = $null
                pointer_equals_payload = $null
            }
            revision_directory = $null
        }
        promotion_gate = [ordered]@{
            contract_version = "b06_promotion_gate_v0.2"
            controlling_interface = "b06-no-play-normalization-v0.1"
            authentic_provider_lineage = $false
            reported_digest_equals_computed_digest = $false
            required_raw_schema_present = $false
            logical_no_play_normalization_applied = $false
            regular_season_game_count_valid = $false
            manifest_immutable_and_timestamped = $false
            current_json_pointer_update_atomic = $false
            current_json_updated = $false
            all_required_checks_pass = $false
        }
        events = @()
        claims = @()
        scope_scan = [ordered]@{
            season_2016_exists = $false
            preexisting_derived_artifact_paths = @()
            derived_artifact_paths = @()
            raw_parquet_copied_to_run_root = $false
        }
        status = "blocked"
        known_limitations = @()
    }
}

function Set-ResultFields {
    param(
        [Parameter(Mandatory = $true)]$Package,
        [Parameter(Mandatory = $true)]$AdapterResult
    )

    $allowedStatuses = @("success_new_revision", "success_existing_revision", "cached_valid_after_failure", "failed")
    if ($allowedStatuses -notcontains [string]$AdapterResult.status) {
        throw "Adapter returned an unsupported status."
    }
    if ([int]$AdapterResult.season -ne $Season) {
        throw "Adapter result season does not equal the single requested season."
    }

    $Package.result.status = [string]$AdapterResult.status
    $Package.result.season = [int]$AdapterResult.season
    $Package.result.revision_sha256 = if ($null -eq $AdapterResult.revision_sha256) { $null } else { [string]$AdapterResult.revision_sha256 }
    $Package.result.manifest_path = if ($null -eq $AdapterResult.manifest_path) { $null } else { [string]$AdapterResult.manifest_path }
    $Package.result.failure_class = if ($null -eq $AdapterResult.failure_class) { $null } else { [string]$AdapterResult.failure_class }
    $Package.result.failure_detail = if ($null -eq $AdapterResult.failure_detail) { $null } else { [string]$AdapterResult.failure_detail }
    $Package.result.freshness = if ($null -eq $AdapterResult.freshness) { $null } else { [string]$AdapterResult.freshness }
    $Package.result.stale_banner_required = [bool]$AdapterResult.stale_banner_required

    $expectedAdapterModulePath = [IO.Path]::GetFullPath((Join-Path $RepositoryRoot "engine\ingestion\nflverse_pbp.py"))
    $reportedAdapterModulePath = [IO.Path]::GetFullPath([string]$AdapterResult.adapter_module_path)
    $reportedAdapterModuleSha256 = [string]$AdapterResult.adapter_module_sha256
    $expectedAdapterModuleSha256 = Get-FileSha256 -Path $expectedAdapterModulePath
    $adapterModuleMatchesRepository = (
        $reportedAdapterModulePath.Equals($expectedAdapterModulePath, [StringComparison]::OrdinalIgnoreCase) -and
        $reportedAdapterModuleSha256 -ceq $expectedAdapterModuleSha256
    )
    $Package.runtime.adapter_module_path = $reportedAdapterModulePath
    $Package.runtime.adapter_module_sha256 = $reportedAdapterModuleSha256
    $Package.runtime.adapter_module_matches_repository = $adapterModuleMatchesRepository
    if (-not $adapterModuleMatchesRepository) {
        throw "Adapter module path or SHA-256 does not match the reviewed repository module."
    }

    if ($Package.result.status -eq "cached_valid_after_failure") {
        $Package.result.freshness = "stale"
        $Package.result.stale_banner_required = $true
    }
}

function Collect-SuccessEvidence {
    param([Parameter(Mandatory = $true)]$Package)

    $seasonRoot = $Package.data_root.season_root
    $currentPath = Join-Path $seasonRoot "current.json"
    if (-not (Test-Path -LiteralPath $currentPath -PathType Leaf)) {
        throw "Fresh result did not produce current.json."
    }
    $currentEvidence = Read-JsonEvidence -Path $currentPath -Kind "current_pointer"
    $relativeManifest = [string]$currentEvidence.content.manifest_path
    if ([IO.Path]::IsPathRooted($relativeManifest)) {
        throw "current.json manifest_path must be relative to DataRoot."
    }
    $manifestPath = [IO.Path]::GetFullPath((Join-Path $NormalizedDataRoot $relativeManifest))
    if (-not (Test-SameOrNestedPath -Candidate $manifestPath -Parent $NormalizedDataRoot)) {
        throw "current.json points outside DataRoot."
    }
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Pointed manifest is absent."
    }
    $manifestEvidence = Read-JsonEvidence -Path $manifestPath -Kind "manifest"
    $payloadPath = Join-Path (Split-Path -Parent $manifestPath) "pbp.parquet"
    if (-not (Test-Path -LiteralPath $payloadPath -PathType Leaf)) {
        throw "Pointed payload is absent."
    }
    $payloadItem = Get-Item -LiteralPath $payloadPath
    $payloadHash = Get-FileSha256 -Path $payloadPath
    $pointerHash = [string]$currentEvidence.content.revision_sha256
    $manifestHash = [string]$manifestEvidence.content.revision_sha256
    $revisionDirectory = Split-Path -Parent $manifestPath
    $revisionDirectoryItem = Get-Item -LiteralPath $revisionDirectory

    $Package.success_evidence.current_json = $currentEvidence
    $Package.success_evidence.manifest = $manifestEvidence
    $Package.success_evidence.payload = [ordered]@{
        path = $payloadItem.FullName
        size_bytes = [long]$payloadItem.Length
        sha256 = $payloadHash
    }
    $Package.success_evidence.sha_identity = [ordered]@{
        pointer_equals_manifest = ($pointerHash -ceq $manifestHash)
        manifest_equals_payload = ($manifestHash -ceq $payloadHash)
        pointer_equals_payload = ($pointerHash -ceq $payloadHash)
    }
    $Package.success_evidence.revision_directory = [ordered]@{
        path = $revisionDirectoryItem.FullName
        name = $revisionDirectoryItem.Name
        identity_sha256 = $pointerHash
        name_matches_identity = ($revisionDirectoryItem.Name -ceq "sha256=$pointerHash")
        creation_time_utc = $revisionDirectoryItem.CreationTimeUtc.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        last_write_time_utc = $revisionDirectoryItem.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        retrieved_at_utc = $manifestEvidence.content.retrieved_at_utc
        effective_time = $manifestEvidence.content.effective_time
    }

    if ($Package.result.revision_sha256 -cne $pointerHash) {
        throw "Adapter result revision SHA does not equal current.json."
    }
    if (-not $Package.success_evidence.revision_directory.name_matches_identity) {
        throw "Revision directory identity does not equal current.json."
    }
    if (-not (
        $Package.success_evidence.sha_identity.pointer_equals_manifest -and
        $Package.success_evidence.sha_identity.manifest_equals_payload -and
        $Package.success_evidence.sha_identity.pointer_equals_payload
    )) {
        throw "Pointer, manifest, and payload SHA identities do not all agree."
    }

    $manifest = $manifestEvidence.content
    $rawSchemaNames = @($manifest.raw_schema | ForEach-Object { [string]$_.name })
    $requiredRawColumns = @(
        "season", "season_type", "game_id", "yardline_100", "touchdown",
        "rush_attempt", "pass_attempt", "play_type"
    )
    $authenticProviderLineage = (
        $manifest.provider -ceq "nflverse/nflverse-data" -and
        $manifest.source_id -ceq "nflverse/nflverse-data:release:pbp" -and
        $manifest.source_release_tag -ceq "pbp" -and
        [int64]$manifest.source_release_id -gt 0 -and
        [int64]$manifest.source_asset_id -gt 0 -and
        [string]$manifest.source_url -match "^https://(github\.com|objects\.githubusercontent\.com|release-assets\.githubusercontent\.com)/"
    )
    $digestEquality = (
        $manifest.digest_match -eq $true -and
        [string]$manifest.reported_digest_sha256 -ceq [string]$manifest.computed_digest_sha256 -and
        [string]$manifest.computed_digest_sha256 -ceq $payloadHash
    )
    $requiredRawSchemaPresent = @($requiredRawColumns | Where-Object { $rawSchemaNames -notcontains $_ }).Count -eq 0
    $logicalNoPlayApplied = (
        $manifest.no_play_normalization_version -ceq "b06-no-play-normalization-v0.1" -and
        [string]$manifest.parser_version -match "b06-no-play-normalization-v0\.1" -and
        [int64]$manifest.unknown_row_count -eq 0 -and
        ([int64]$manifest.logical_no_play_counts.true +
            [int64]$manifest.logical_no_play_counts.false +
            [int64]$manifest.logical_no_play_counts.unknown) -eq [int64]$manifest.row_count
    )
    $regularSeasonValid = (
        $manifest.regular_season_game_count_valid -eq $true -and
        [int64]$manifest.regular_season_game_count_expected -eq [int64]$manifest.regular_season_game_count_observed
    )
    $retrievalTimestamp = [DateTimeOffset]$manifest.retrieval_timestamp
    $retrievedAtUtc = [DateTimeOffset]$manifest.retrieved_at_utc
    $promotionResult = [string]$manifest.promotion_result
    $manifestRawJson = [IO.File]::ReadAllText($manifestPath, [Text.Encoding]::UTF8)
    $manifestImmutableAndTimestamped = (
        [bool]$Package.success_evidence.revision_directory.name_matches_identity -and
        ($manifestRawJson -match '"retrieval_timestamp"\s*:\s*"\d{4}-\d{2}-\d{2}T[^"\r\n]*Z"') -and
        ($retrievalTimestamp.UtcDateTime -eq $retrievedAtUtc.UtcDateTime) -and
        ($promotionResult -ceq "pass")
    )
    $pointerAtomic = (
        $Package.success_evidence.sha_identity.pointer_equals_manifest -and
        $Package.success_evidence.sha_identity.manifest_equals_payload -and
        $Package.success_evidence.sha_identity.pointer_equals_payload
    )
    $allRequiredChecksPass = (
        $authenticProviderLineage -and
        $digestEquality -and
        $requiredRawSchemaPresent -and
        $logicalNoPlayApplied -and
        $regularSeasonValid -and
        $manifestImmutableAndTimestamped -and
        $pointerAtomic
    )
    $Package.promotion_gate.authentic_provider_lineage = $authenticProviderLineage
    $Package.promotion_gate.reported_digest_equals_computed_digest = $digestEquality
    $Package.promotion_gate.required_raw_schema_present = $requiredRawSchemaPresent
    $Package.promotion_gate.logical_no_play_normalization_applied = $logicalNoPlayApplied
    $Package.promotion_gate.regular_season_game_count_valid = $regularSeasonValid
    $Package.promotion_gate.manifest_immutable_and_timestamped = $manifestImmutableAndTimestamped
    $Package.promotion_gate.current_json_pointer_update_atomic = $pointerAtomic
    $Package.promotion_gate.current_json_updated = $pointerAtomic
    $Package.promotion_gate.all_required_checks_pass = $allRequiredChecksPass
    if (-not $allRequiredChecksPass) {
        $failedChecks = @(
            $Package.promotion_gate.GetEnumerator() |
                Where-Object { $_.Key -notin @("contract_version", "controlling_interface", "current_json_updated", "all_required_checks_pass") -and -not [bool]$_.Value } |
                ForEach-Object { $_.Key }
        )
        $diagnostic = if ($failedChecks -contains "manifest_immutable_and_timestamped") {
            " revision_name_matches=$([bool]$Package.success_evidence.revision_directory.name_matches_identity); retrieval_timestamp='$($retrievalTimestamp.ToString("o"))'; retrieved_at_utc='$($retrievedAtUtc.ToString("o"))'; promotion_result='$promotionResult'."
        }
        else { "" }
        throw "The B-06 v0.2 seven-point promotion gate did not fully pass: $($failedChecks -join ', ').$diagnostic"
    }
}

try {
    if ([bool]$WhatIf -eq [bool]$ExecuteLive) {
        throw "Specify exactly one mode: -WhatIf or -ExecuteLive."
    }
    if ($Season -lt 2016 -or $Season -gt 2025) {
        throw "Season must be within the B-06 contract policy window 2016-2025."
    }
    if ($ExpectedCommitSha -notmatch "^[0-9a-fA-F]{40}$") {
        throw "ExpectedCommitSha must be a full 40-character hexadecimal Git SHA."
    }

    $NormalizedDataRoot = Normalize-LocalAbsolutePath -Path $DataRoot -Label "DataRoot"
    $NormalizedRunRoot = Normalize-LocalAbsolutePath -Path $RunRoot -Label "RunRoot"
    if (
        (Test-SameOrNestedPath -Candidate $NormalizedDataRoot -Parent $NormalizedRunRoot) -or
        (Test-SameOrNestedPath -Candidate $NormalizedRunRoot -Parent $NormalizedDataRoot)
    ) {
        throw "DataRoot and RunRoot must be disjoint; neither may equal, contain, or be contained by the other."
    }

    New-Item -ItemType Directory -Path $NormalizedRunRoot -Force | Out-Null
    $runName = "{0}-season={1}-sha={2}-{3}" -f (
        [DateTimeOffset]::UtcNow.ToString("yyyyMMddTHHmmssfffZ"),
        $Season,
        $ExpectedCommitSha.Substring(0, 12).ToLowerInvariant(),
        [Guid]::NewGuid().ToString("N").Substring(0, 8)
    )
    $RunDirectory = Join-Path $NormalizedRunRoot $runName
    New-Item -ItemType Directory -Path $RunDirectory | Out-Null
    $TranscriptPath = Join-Path $RunDirectory "console-transcript.txt"
    $ReviewPackagePath = Join-Path $RunDirectory "review-package.json"
    $AdapterRunnerPath = Join-Path $RunDirectory "b06-adapter-runner.py"
    $AdapterResultPath = Join-Path $RunDirectory "adapter-result.json"
    Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null
    $TranscriptStarted = $true

    $OperationMode = if ($ExecuteLive) { "execute_live" } else { "what_if" }
    $Package = New-BaseReviewPackage -OperationMode $OperationMode
    Write-Host "HARNESS_VERSION=$HarnessVersion"
    Write-Host "RUN_DIRECTORY=$RunDirectory"

    $HeadSha = (& git -C $RepositoryRoot rev-parse HEAD 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $HeadSha -notmatch "^[0-9a-f]{40}$") {
        throw "Unable to resolve repository HEAD."
    }
    $Package.repository.head_sha = $HeadSha
    $Package.repository.is_expected_sha = $HeadSha.Equals($ExpectedCommitSha, [StringComparison]::OrdinalIgnoreCase)
    if (-not $Package.repository.is_expected_sha) {
        throw "ExpectedCommitSha does not equal git rev-parse HEAD."
    }

    $WorkingTreeStatus = @(& git -C $RepositoryRoot status --porcelain=v1 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect repository working tree."
    }
    $WorkingTreeDirty = $WorkingTreeStatus.Count -gt 0
    $Package.repository.working_tree_dirty = $WorkingTreeDirty
    $Package.repository.working_tree_porcelain_v1 = @($WorkingTreeStatus)
    $Package.repository.working_tree_status = @($WorkingTreeStatus)
    Write-Host "WORKING_TREE_DIRTY=$($WorkingTreeDirty.ToString().ToLowerInvariant())"
    Write-Host "WORKING_TREE_PORCELAIN_V1_BEGIN"
    foreach ($statusLine in $WorkingTreeStatus) {
        Write-Host $statusLine
    }
    Write-Host "WORKING_TREE_PORCELAIN_V1_END"
    if ($WorkingTreeDirty) {
        throw "The repository working tree must be clean for a controlled run."
    }

    $PythonVersion = (& python --version 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $PythonVersion -notmatch "^Python 3\.12\.[0-9]+") {
        throw "Python 3.12.x is required. Observed: $PythonVersion"
    }
    $Package.runtime.python_version = $PythonVersion

    $seasonRoot = Join-Path $NormalizedDataRoot "season=$Season"
    $currentPath = Join-Path $seasonRoot "current.json"
    $revisionsPath = Join-Path $seasonRoot "revisions"
    $PreexistingCurrent = Test-Path -LiteralPath $currentPath
    $PreexistingRevisions = Test-Path -LiteralPath $revisionsPath
    $PriorFailedAttempts = @(Get-FailureEvidence -SeasonRoot $seasonRoot)
    foreach ($failure in $PriorFailedAttempts) {
        $PriorFailureHashes[$failure.path] = $failure.sha256
    }
    foreach ($event in @(Get-AllEventEvidence -SeasonRoot $seasonRoot)) {
        $PreexistingEventHashes[$event.path] = $event.sha256
    }
    $Package.data_root.preexisting_current_json = $PreexistingCurrent
    $Package.data_root.preexisting_revisions_directory = $PreexistingRevisions
    $Package.data_root.prior_failed_attempts = @($PriorFailedAttempts)
    $derivedScanRoots = @(Get-DerivedScanRoots -Root $NormalizedDataRoot -CurrentRunDirectory $RunDirectory -RepoRoot $RepositoryRoot)
    $PreexistingDerivedArtifactPaths = @(Get-DerivedArtifactPaths -Roots $derivedScanRoots)
    $Package.scope_scan.preexisting_derived_artifact_paths = @($PreexistingDerivedArtifactPaths)

    if ($ExecuteLive -and ($PreexistingCurrent -or $PreexistingRevisions)) {
        throw "Live execution is prohibited when current.json or the season revisions directory already exists."
    }

    Push-Location $RepositoryRoot
    try {
        $FocusedTestExitCode = Invoke-FocusedTests
    }
    finally {
        Pop-Location
    }
    $Package.runtime.focused_test_exit_code = $FocusedTestExitCode
    if ($FocusedTestExitCode -ne 0) {
        throw "The exact focused B-06 synthetic suite did not pass."
    }

    if ($WhatIf) {
        $FinalStatus = "what_if_pass"
        $ExitCode = 0
    }
    else {
        Push-Location $RepositoryRoot
        try {
            $adapterExitCode = Invoke-AdapterOnce -RequestedSeason $Season -Root $NormalizedDataRoot -ResultPath $AdapterResultPath
        }
        finally {
            Pop-Location
        }
        if ($adapterExitCode -ne 0 -or -not (Test-Path -LiteralPath $AdapterResultPath -PathType Leaf)) {
            $FinalStatus = "failed_or_stale"
            throw "The single adapter invocation did not emit a readable result."
        }
        $adapterResult = [IO.File]::ReadAllText($AdapterResultPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
        Set-ResultFields -Package $Package -AdapterResult $adapterResult

        if ($Package.result.status -in @("success_new_revision", "success_existing_revision")) {
            if ($Package.result.freshness -ne "fresh" -or $Package.result.stale_banner_required) {
                $FinalStatus = "failed_or_stale"
                throw "A success outcome was not explicitly fresh."
            }
            Collect-SuccessEvidence -Package $Package
            $FinalStatus = "fresh_success_pending_review"
            $ExitCode = 0
        }
        else {
            $FinalStatus = "failed_or_stale"
            $ExitCode = 1
        }
    }
}
catch {
    $message = $_.Exception.Message
    Write-Error $message -ErrorAction Continue
    $KnownLimitations += "Harness outcome detail: $message"
    if ($AdapterInvocationAttempted -and $FinalStatus -eq "blocked") {
        $FinalStatus = "failed_or_stale"
        $ExitCode = 1
    }
    elseif ($FinalStatus -eq "blocked") {
        $ExitCode = 2
    }
}
finally {
    if ($null -ne $RunDirectory) {
        try {
            if ($null -eq $Package) {
                $fallbackMode = if ($ExecuteLive) { "execute_live" } else { "what_if" }
                $Package = New-BaseReviewPackage -OperationMode $fallbackMode
            }

            $seasonRoot = Join-Path $NormalizedDataRoot "season=$Season"
            $PostexistingCurrent = Test-Path -LiteralPath (Join-Path $seasonRoot "current.json")
            $PostexistingRevisions = Test-Path -LiteralPath (Join-Path $seasonRoot "revisions")
            $Events = @(Get-AllEventEvidence -SeasonRoot $seasonRoot)
            $Claims = @(Get-ClaimEvidence -Root $NormalizedDataRoot -RequestedSeason $Season)
            $newRequestEvidence = @(
                $Events | Where-Object {
                    $AdapterInvocationAttempted -and
                    -not $PreexistingEventHashes.ContainsKey($_.path) -and
                    (Test-ProviderRequestEvidenceEvent -Event $_)
                }
            )
            $ProviderRequestEvidencePaths = @($newRequestEvidence | ForEach-Object { $_.path })
            $ProviderRequestMade = $ProviderRequestEvidencePaths.Count -gt 0
            $evidenceKinds = @($newRequestEvidence | ForEach-Object { $_.kind } | Sort-Object -Unique)
            if ($evidenceKinds.Count -eq 1) {
                $ProviderRequestEvidenceSource = if ($evidenceKinds[0] -eq "retrieval") {
                    "retrieval_event"
                }
                else {
                    "failed_attempt_event"
                }
            }
            elseif ($evidenceKinds.Count -gt 1) {
                $ProviderRequestEvidenceSource = "multiple_adapter_event_types"
            }
            $afterFailures = @($Events | Where-Object { $_.kind -eq "failed_attempt" })
            foreach ($priorPath in $PriorFailureHashes.Keys) {
                $matching = @($afterFailures | Where-Object { $_.path -eq $priorPath })
                if ($matching.Count -ne 1 -or $matching[0].sha256 -ne $PriorFailureHashes[$priorPath]) {
                    $PriorFailuresUnchanged = $false
                }
            }

            $derivedScanRoots = @(Get-DerivedScanRoots -Root $NormalizedDataRoot -CurrentRunDirectory $RunDirectory -RepoRoot $RepositoryRoot)
            $allDerivedPaths = @(Get-DerivedArtifactPaths -Roots $derivedScanRoots)
            $derivedPaths = @($allDerivedPaths | Where-Object { $PreexistingDerivedArtifactPaths -notcontains $_ })
            $runParquet = @(
                Get-ChildItem -LiteralPath $NormalizedRunRoot -File -Recurse -Filter "*.parquet" -ErrorAction SilentlyContinue
            )
            $Package.adapter_invocation_attempted = $AdapterInvocationAttempted
            $Package.provider_request_made = $ProviderRequestMade
            $Package.provider_request_evidence_source = $ProviderRequestEvidenceSource
            $Package.provider_request_evidence_paths = @($ProviderRequestEvidencePaths)
            $Package.repository.head_sha = $HeadSha
            $Package.repository.is_expected_sha = (
                $null -ne $HeadSha -and $HeadSha.Equals($ExpectedCommitSha, [StringComparison]::OrdinalIgnoreCase)
            )
            $Package.repository.working_tree_dirty = $WorkingTreeDirty
            $Package.repository.working_tree_porcelain_v1 = @($WorkingTreeStatus)
            $Package.repository.working_tree_status = @($WorkingTreeStatus)
            $Package.runtime.python_version = $PythonVersion
            $Package.runtime.focused_test_exit_code = $FocusedTestExitCode
            $Package.data_root.preexisting_current_json = $PreexistingCurrent
            $Package.data_root.preexisting_revisions_directory = $PreexistingRevisions
            $Package.data_root.postexisting_current_json = $PostexistingCurrent
            $Package.data_root.postexisting_revisions_directory = $PostexistingRevisions
            $Package.data_root.prior_failed_attempts = @($PriorFailedAttempts)
            $Package.data_root.prior_failed_attempts_unchanged = $PriorFailuresUnchanged
            $Package.events = @($Events)
            $Package.claims = @($Claims)
            $Package.scope_scan.season_2016_exists = Test-Path -LiteralPath (Join-Path $NormalizedDataRoot "season=2016")
            $Package.scope_scan.preexisting_derived_artifact_paths = @($PreexistingDerivedArtifactPaths)
            $Package.scope_scan.derived_artifact_paths = @($derivedPaths)
            $Package.scope_scan.raw_parquet_copied_to_run_root = ($runParquet.Count -gt 0)

            if (-not $PriorFailuresUnchanged) {
                $KnownLimitations += "One or more preexisting failed-attempt events changed or disappeared."
                if ($ExitCode -eq 0) {
                    $FinalStatus = "blocked"
                    $ExitCode = 2
                }
            }
            if ($derivedPaths.Count -gt 0) {
                $KnownLimitations += "New derived-artifact-like paths were detected during the controlled run."
                if ($ExitCode -eq 0) {
                    $FinalStatus = "blocked"
                    $ExitCode = 2
                }
            }
            if ($runParquet.Count -gt 0) {
                $KnownLimitations += "A Parquet file was detected in the controlled run directory."
                $FinalStatus = "blocked"
                $ExitCode = 2
            }
            if (
                $ExecuteLive -and
                $null -ne $Package.result.status -and
                -not $ProviderRequestMade
            ) {
                $KnownLimitations += "The adapter result lacked a qualifying new provider-request evidence event."
                $FinalStatus = "failed_or_stale"
                $ExitCode = 1
            }
            if ($ExecuteLive -and $Package.result.status -in @("failed", "cached_valid_after_failure")) {
                if ($PostexistingCurrent -or $PostexistingRevisions) {
                    $KnownLimitations += "Failed or stale outcome left a pointer or revisions directory; reviewer investigation is required."
                }
                $FinalStatus = "failed_or_stale"
                $ExitCode = 1
            }

            $EndedAtUtc = [DateTimeOffset]::UtcNow
            $Package.generated_at_utc = $EndedAtUtc.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            $Package.ended_at_utc = $Package.generated_at_utc
            $Package.status = $FinalStatus
            $Package.known_limitations = @($KnownLimitations)
            $json = $Package | ConvertTo-Json -Depth 100
            [IO.File]::WriteAllText($ReviewPackagePath, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
            Write-Host "REVIEW_PACKAGE=$ReviewPackagePath"
        }
        catch {
            $FinalStatus = "blocked"
            $ExitCode = 2
            Write-Error "Unable to finalize review package: $($_.Exception.Message)" -ErrorAction Continue
        }
        finally {
            if ($null -ne $AdapterRunnerPath) {
                Remove-Item -LiteralPath $AdapterRunnerPath -Force -ErrorAction SilentlyContinue
            }
            if ($null -ne $AdapterResultPath) {
                Remove-Item -LiteralPath $AdapterResultPath -Force -ErrorAction SilentlyContinue
            }
        }
    }

    $statusLine = "B06_CONTROLLED_RUN_STATUS=$($FinalStatus.ToUpperInvariant())"
    Write-Host $statusLine
    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
    }
}

exit $ExitCode
