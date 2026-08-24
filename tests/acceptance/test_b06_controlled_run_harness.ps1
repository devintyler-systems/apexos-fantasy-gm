Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$HarnessPath = Join-Path $RepositoryRoot "tools\run_b06_controlled.ps1"
$PowerShellExecutable = (Get-Process -Id $PID).Path
$HeadSha = (& git -C $RepositoryRoot rev-parse HEAD 2>&1 | Out-String).Trim()
$Failures = [Collections.Generic.List[string]]::new()
$Passed = 0

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Assert-Equal {
    param($Actual, $Expected, [string]$Message)
    if ($Actual -ne $Expected) {
        throw "$Message Expected '$Expected'; got '$Actual'."
    }
}

function Invoke-TestCase {
    param([string]$Name, [scriptblock]$Body)
    try {
        & $Body
        $script:Passed++
        Write-Host "PASS $Name"
    }
    catch {
        $script:Failures.Add("$Name :: $($_.Exception.Message)")
        Write-Host "FAIL $Name :: $($_.Exception.Message)"
    }
}

function New-TestSandbox {
    $root = Join-Path ([IO.Path]::GetTempPath()) ("apexos-b06-harness-test-" + [Guid]::NewGuid().ToString("N"))
    $shim = Join-Path $root "shim"
    $run = Join-Path $root "runs"
    $data = Join-Path $root "data"
    $counters = Join-Path $root "counters"
    New-Item -ItemType Directory -Path $shim, $run, $counters -Force | Out-Null

    $mockPowerShell = @'
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Increment-Counter([string]$Name) {
    $path = Join-Path $env:B06_TEST_COUNTER_DIR "$Name.txt"
    $value = if (Test-Path -LiteralPath $path) { [int](Get-Content -Raw -LiteralPath $path) } else { 0 }
    Set-Content -LiteralPath $path -Value ($value + 1) -Encoding ascii
}

if ($args.Count -eq 1 -and $args[0] -eq "--version") {
    Increment-Counter "version"
    Write-Output "Python 3.12.9"
    exit 0
}

if ($args -contains "pytest") {
    Increment-Counter "focused"
    Write-Output "mock focused B-06 suite passed"
    exit 0
}

if ($args.Count -ge 5 -and $args[0] -eq "-B" -and $args[1] -like "*b06-adapter-runner.py") {
    Increment-Counter "adapter"
    $season = [int]$args[2]
    $dataRoot = [IO.Path]::GetFullPath($args[3])
    $resultPath = [IO.Path]::GetFullPath($args[4])
    $seasonRoot = Join-Path $dataRoot "season=$season"
    $outcome = $env:B06_TEST_ADAPTER_OUTCOME

    if ($outcome -eq "fresh") {
        $revisionRootBase = Join-Path $seasonRoot "revisions"
        New-Item -ItemType Directory -Path $revisionRootBase -Force | Out-Null
        $temporaryPayload = Join-Path $revisionRootBase "mock-payload.tmp"
        [IO.File]::WriteAllBytes($temporaryPayload, [Text.Encoding]::UTF8.GetBytes("synthetic parquet marker; not a provider payload"))
        $revisionSha = (Get-FileHash -LiteralPath $temporaryPayload -Algorithm SHA256).Hash.ToLowerInvariant()
        $revisionRoot = Join-Path $revisionRootBase "sha256=$revisionSha"
        New-Item -ItemType Directory -Path $revisionRoot | Out-Null
        $payloadPath = Join-Path $revisionRoot "pbp.parquet"
        Move-Item -LiteralPath $temporaryPayload -Destination $payloadPath
        $manifestPath = Join-Path $revisionRoot "manifest.json"
        $sourceUrl = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2023.parquet"
        $manifest = [ordered]@{
            provider = "nflverse/nflverse-data"
            source_id = "nflverse/nflverse-data:release:pbp"
            source_url = $sourceUrl
            source_release_tag = "pbp"
            source_release_id = 58152862
            source_asset_id = 354728689
            requested_season = $season
            revision_sha256 = $revisionSha
            reported_digest_sha256 = $revisionSha
            computed_digest_sha256 = $revisionSha
            digest_match = $true
            retrieved_at_utc = "2026-08-22T00:00:01Z"
            retrieval_timestamp = "2026-08-22T00:00:01Z"
            effective_time = "2026-08-21T23:59:00Z"
            parser_version = "b06-v0.2-evidence-1+b06-no-play-normalization-v0.1"
            no_play_normalization_version = "b06-no-play-normalization-v0.1"
            row_count = 1
            raw_schema = @(
                "season", "season_type", "game_id", "yardline_100", "touchdown",
                "rush_attempt", "pass_attempt", "play_type"
            ) | ForEach-Object { [ordered]@{ name = $_; type = "mock"; nullable = $true } }
            logical_no_play_counts = [ordered]@{ true = 0; false = 1; unknown = 0 }
            unknown_row_count = 0
            regular_season_game_count_valid = $true
            regular_season_game_count_expected = 272
            regular_season_game_count_observed = 272
            promotion_result = "pass"
        }
        $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8
        $relativeManifest = "season=$season/revisions/sha256=$revisionSha/manifest.json"
        $current = [ordered]@{
            manifest_path = $relativeManifest
            revision_sha256 = $revisionSha
            pointer_ordering_key = @("2026-08-21T23:59:00Z", "2026-08-22T00:00:01Z", $revisionSha)
        }
        $current | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $seasonRoot "current.json") -Encoding utf8
        $eventsRoot = Join-Path $seasonRoot "events"
        New-Item -ItemType Directory -Path $eventsRoot -Force | Out-Null
        [ordered]@{
            retrieval_event_id = "mock-retrieval"
            source_asset_url = $sourceUrl
            outcome = "success_new_revision"
            freshness = "fresh"
            local_revision_sha256 = $revisionSha
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $eventsRoot "retrieval-mock.json") -Encoding utf8
        $claimRoot = Join-Path $dataRoot "claims\revision\season=$season\sha256=$revisionSha"
        New-Item -ItemType Directory -Path $claimRoot -Force | Out-Null
        [ordered]@{
            requested_season = $season
            revision_sha256 = $revisionSha
            claimant_id = "mock-retrieval"
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $claimRoot "claim-mock.json") -Encoding utf8
        $result = [ordered]@{
            status = "success_new_revision"
            season = $season
            revision_sha256 = $revisionSha
            manifest_path = $manifestPath
            failure_class = $null
            failure_detail = $null
            freshness = "fresh"
            stale_banner_required = $false
        }
    }
    elseif ($outcome -eq "failed") {
        $eventsRoot = Join-Path $seasonRoot "events"
        New-Item -ItemType Directory -Path $eventsRoot -Force | Out-Null
        [ordered]@{
            attempt_id = "mock-failure"
            attempted_at_utc = "2026-08-22T00:00:02Z"
            attempted_url = "https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp"
            failure_class = "http_status"
            failure_detail = "mocked provider failure"
            prior_valid_revision_sha256 = $null
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $eventsRoot "failed-attempt-mock.json") -Encoding utf8
        $result = [ordered]@{
            status = "failed"
            season = $season
            revision_sha256 = $null
            manifest_path = $null
            failure_class = "http_status"
            failure_detail = "mocked provider failure"
            freshness = "unavailable"
            stale_banner_required = $false
        }
    }
    elseif ($outcome -eq "cached") {
        $revisionSha = "c" * 64
        $eventsRoot = Join-Path $seasonRoot "events"
        New-Item -ItemType Directory -Path $eventsRoot -Force | Out-Null
        [ordered]@{
            attempt_id = "mock-cached-failure"
            attempted_at_utc = "2026-08-22T00:00:03Z"
            attempted_url = "https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp"
            failure_class = "http_status"
            failure_detail = "mocked failure with cached result"
            prior_valid_revision_sha256 = $revisionSha
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $eventsRoot "failed-attempt-mock-cached.json") -Encoding utf8
        $result = [ordered]@{
            status = "cached_valid_after_failure"
            season = $season
            revision_sha256 = $revisionSha
            manifest_path = (Join-Path $seasonRoot "unreachable-manifest.json")
            failure_class = "http_status"
            failure_detail = "mocked failure with cached result"
            freshness = "fresh"
            stale_banner_required = $false
        }
    }
    else {
        throw "Unknown mock adapter outcome '$outcome'."
    }

    $result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $resultPath -Encoding utf8
    exit 0
}

Write-Error "Unexpected mock python arguments: $($args -join ' ')"
exit 97
'@

    $mockScriptPath = Join-Path $shim "mock-python.ps1"
    Set-Content -LiteralPath $mockScriptPath -Value $mockPowerShell -Encoding utf8
    $batch = @"
@echo off
"$PowerShellExecutable" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0mock-python.ps1" %*
exit /b %errorlevel%
"@
    Set-Content -LiteralPath (Join-Path $shim "python.cmd") -Value $batch -Encoding ascii

    return [pscustomobject]@{
        Root = $root
        Shim = $shim
        RunRoot = $run
        DataRoot = $data
        CounterRoot = $counters
    }
}

function Remove-TestSandbox {
    param($Sandbox)
    if ($null -ne $Sandbox -and (Test-Path -LiteralPath $Sandbox.Root)) {
        Remove-Item -LiteralPath $Sandbox.Root -Recurse -Force
    }
}

function Get-Counter {
    param($Sandbox, [string]$Name)
    $path = Join-Path $Sandbox.CounterRoot "$Name.txt"
    if (-not (Test-Path -LiteralPath $path)) { return 0 }
    return [int](Get-Content -Raw -LiteralPath $path)
}

function Invoke-Harness {
    param(
        $Sandbox,
        [string[]]$Arguments,
        [string]$AdapterOutcome = "failed"
    )

    $oldPath = $env:PATH
    $oldCounter = $env:B06_TEST_COUNTER_DIR
    $oldOutcome = $env:B06_TEST_ADAPTER_OUTCOME
    try {
        $env:PATH = $Sandbox.Shim + [IO.Path]::PathSeparator + $oldPath
        $env:B06_TEST_COUNTER_DIR = $Sandbox.CounterRoot
        $env:B06_TEST_ADAPTER_OUTCOME = $AdapterOutcome
        $output = @(& $PowerShellExecutable -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $HarnessPath @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
        return [pscustomobject]@{
            ExitCode = $exitCode
            Output = ($output | Out-String)
        }
    }
    finally {
        $env:PATH = $oldPath
        $env:B06_TEST_COUNTER_DIR = $oldCounter
        $env:B06_TEST_ADAPTER_OUTCOME = $oldOutcome
    }
}

function Get-LatestReviewPackage {
    param($Sandbox)
    $path = Get-ChildItem -LiteralPath $Sandbox.RunRoot -File -Recurse -Filter "review-package.json" |
        Sort-Object LastWriteTimeUtc |
        Select-Object -Last 1
    if ($null -eq $path) { throw "No review package was emitted." }
    return Get-Content -Raw -LiteralPath $path.FullName | ConvertFrom-Json
}

function Get-CommonArguments {
    param($Sandbox, [string]$Mode)
    return @(
        "-Season", "2023",
        "-DataRoot", $Sandbox.DataRoot,
        "-RunRoot", $Sandbox.RunRoot,
        "-ExpectedCommitSha", $HeadSha,
        $Mode
    )
}

Invoke-TestCase "what-if runs tests without adapter or raw evidence" {
    $sandbox = New-TestSandbox
    try {
        $result = Invoke-Harness -Sandbox $sandbox -Arguments (Get-CommonArguments $sandbox "-WhatIf")
        $package = Get-LatestReviewPackage $sandbox
        Assert-Equal $result.ExitCode 0 "WhatIf must pass. Output: $($result.Output) Limitations: $($package.known_limitations -join '; ') Derived: $($package.scope_scan.derived_artifact_paths -join '; ')"
        Assert-Equal (Get-Counter $sandbox "focused") 1 "WhatIf must run the focused suite once."
        Assert-Equal (Get-Counter $sandbox "adapter") 0 "WhatIf must not invoke the adapter."
        Assert-True (-not (Test-Path -LiteralPath $sandbox.DataRoot)) "WhatIf created raw evidence."
        Assert-Equal $package.operation_mode "what_if" "Operation mode drifted."
        Assert-Equal $package.adapter_invocation_attempted $false "WhatIf claimed an adapter invocation."
        Assert-Equal $package.provider_request_made $false "WhatIf claimed a provider request."
        Assert-Equal $package.provider_request_evidence_source "none" "WhatIf claimed a provider evidence source."
        Assert-Equal $package.status "what_if_pass" "WhatIf package status drifted."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "live interface requires every explicit parameter and one scalar supported season" {
    $sandbox = New-TestSandbox
    try {
        $requiredArgumentSets = @(
            @("-DataRoot", $sandbox.DataRoot, "-RunRoot", $sandbox.RunRoot, "-ExpectedCommitSha", $HeadSha, "-ExecuteLive"),
            @("-Season", "2023", "-RunRoot", $sandbox.RunRoot, "-ExpectedCommitSha", $HeadSha, "-ExecuteLive"),
            @("-Season", "2023", "-DataRoot", $sandbox.DataRoot, "-ExpectedCommitSha", $HeadSha, "-ExecuteLive"),
            @("-Season", "2023", "-DataRoot", $sandbox.DataRoot, "-RunRoot", $sandbox.RunRoot, "-ExecuteLive")
        )
        foreach ($arguments in $requiredArgumentSets) {
            $result = Invoke-Harness -Sandbox $sandbox -Arguments $arguments
            Assert-True ($result.ExitCode -ne 0) "A missing required parameter was accepted."
        }
        $multiple = Get-CommonArguments $sandbox "-ExecuteLive"
        $multiple[1] = "2023,2024"
        Assert-True ((Invoke-Harness $sandbox $multiple).ExitCode -ne 0) "Multiple seasons were accepted."
        $unsupported = Get-CommonArguments $sandbox "-ExecuteLive"
        $unsupported[1] = "2015"
        Assert-True ((Invoke-Harness $sandbox $unsupported).ExitCode -ne 0) "Unsupported season was accepted."
        $noMode = (Get-CommonArguments $sandbox "-WhatIf")[0..7]
        Assert-True ((Invoke-Harness $sandbox $noMode).ExitCode -ne 0) "Omitted mode was accepted."
        $bothModes = (Get-CommonArguments $sandbox "-WhatIf") + "-ExecuteLive"
        Assert-True ((Invoke-Harness $sandbox $bothModes).ExitCode -ne 0) "Conflicting modes were accepted."
        Assert-Equal (Get-Counter $sandbox "adapter") 0 "Invalid interfaces reached the adapter."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "relative and overlapping roots are rejected" {
    $sandbox = New-TestSandbox
    try {
        $relative = Get-CommonArguments $sandbox "-WhatIf"
        $relative[3] = ".\relative-data"
        Assert-True ((Invoke-Harness $sandbox $relative).ExitCode -ne 0) "Relative DataRoot was accepted."
        $overlap = Get-CommonArguments $sandbox "-WhatIf"
        $overlap[5] = Join-Path $sandbox.DataRoot "runs"
        Assert-True ((Invoke-Harness $sandbox $overlap).ExitCode -ne 0) "Nested RunRoot was accepted."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "nonmatching SHA blocks before tests and adapter" {
    $sandbox = New-TestSandbox
    try {
        $arguments = Get-CommonArguments $sandbox "-ExecuteLive"
        $arguments[7] = "0" * 40
        $result = Invoke-Harness $sandbox $arguments
        Assert-True ($result.ExitCode -ne 0) "Nonmatching SHA passed."
        Assert-Equal (Get-Counter $sandbox "focused") 0 "SHA mismatch reached tests."
        Assert-Equal (Get-Counter $sandbox "adapter") 0 "SHA mismatch reached adapter."
        Assert-Equal (Get-LatestReviewPackage $sandbox).status "blocked" "SHA mismatch was not blocked."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "dirty tracked file blocks before tests and adapter" {
    $sandbox = New-TestSandbox
    $trackedPath = Join-Path $RepositoryRoot "docs\runbooks\b06-controlled-historical-run.md"
    $originalBytes = [IO.File]::ReadAllBytes($trackedPath)
    try {
        [IO.File]::AppendAllText(
            $trackedPath,
            [Environment]::NewLine + "dirty-tree acceptance marker" + [Environment]::NewLine,
            [Text.UTF8Encoding]::new($false)
        )
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive")
        $package = Get-LatestReviewPackage $sandbox
        $transcript = Get-ChildItem -LiteralPath $sandbox.RunRoot -File -Recurse -Filter "console-transcript.txt" |
            Sort-Object LastWriteTimeUtc |
            Select-Object -Last 1 |
            Get-Content -Raw

        Assert-True ($result.ExitCode -ne 0) "Dirty working tree passed."
        Assert-Equal $package.status "blocked" "Dirty working tree was not blocked."
        Assert-Equal (Get-Counter $sandbox "focused") 0 "Dirty working tree reached tests."
        Assert-Equal (Get-Counter $sandbox "adapter") 0 "Dirty working tree reached adapter."
        Assert-Equal $package.repository.working_tree_dirty $true "Dirty-tree boolean was not recorded."
        Assert-True (@($package.repository.working_tree_porcelain_v1).Count -gt 0) "Raw porcelain output was not recorded."
        Assert-True (($package.repository.working_tree_porcelain_v1 | Out-String) -match "docs/runbooks/b06-controlled-historical-run\.md") "Tracked dirty path was not recorded."
        Assert-True ($transcript -match "WORKING_TREE_DIRTY=true") "Transcript omitted the dirty-tree boolean."
        Assert-True ($transcript -match "docs/runbooks/b06-controlled-historical-run\.md") "Transcript omitted raw porcelain output."
    }
    finally {
        [IO.File]::WriteAllBytes($trackedPath, $originalBytes)
        Remove-TestSandbox $sandbox
    }
}

Invoke-TestCase "preexisting current.json blocks live execution" {
    $sandbox = New-TestSandbox
    try {
        $seasonRoot = Join-Path $sandbox.DataRoot "season=2023"
        New-Item -ItemType Directory -Path $seasonRoot -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $seasonRoot "current.json") -Value "{}" -Encoding utf8
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive")
        Assert-True ($result.ExitCode -ne 0) "Existing current.json did not block."
        Assert-Equal (Get-Counter $sandbox "focused") 0 "Existing current.json reached tests."
        Assert-Equal (Get-Counter $sandbox "adapter") 0 "Existing current.json reached adapter."
        Assert-Equal (Get-LatestReviewPackage $sandbox).data_root.preexisting_current_json $true "Prestate was not recorded."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "preexisting revisions directory blocks live execution" {
    $sandbox = New-TestSandbox
    try {
        New-Item -ItemType Directory -Path (Join-Path $sandbox.DataRoot "season=2023\revisions") -Force | Out-Null
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive")
        Assert-True ($result.ExitCode -ne 0) "Existing revisions did not block."
        Assert-Equal (Get-Counter $sandbox "focused") 0 "Existing revisions reached tests."
        Assert-Equal (Get-Counter $sandbox "adapter") 0 "Existing revisions reached adapter."
        Assert-Equal (Get-LatestReviewPackage $sandbox).data_root.preexisting_revisions_directory $true "Prestate was not recorded."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "mock fresh result has complete SHA identity and bounded scope" {
    $sandbox = New-TestSandbox
    try {
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive") "fresh"
        $package = Get-LatestReviewPackage $sandbox
        Assert-Equal $result.ExitCode 0 "Fresh mock must exit zero. Output: $($result.Output) Limitations: $($package.known_limitations -join '; ') Derived: $($package.scope_scan.derived_artifact_paths -join '; ')"
        Assert-Equal (Get-Counter $sandbox "focused") 1 "Focused suite count drifted."
        Assert-Equal (Get-Counter $sandbox "adapter") 1 "Adapter was not invoked exactly once."
        Assert-Equal $package.status "fresh_success_pending_review" "Fresh status drifted."
        Assert-Equal $package.adapter_invocation_attempted $true "Live runner attempt was not recorded."
        Assert-Equal $package.provider_request_made $true "Live request was not recorded."
        Assert-Equal $package.provider_request_evidence_source "retrieval_event" "Fresh request evidence source drifted."
        Assert-Equal @($package.provider_request_evidence_paths).Count 1 "Fresh request evidence path was not recorded."
        Assert-Equal $package.success_evidence.sha_identity.pointer_equals_manifest $true "Pointer/manifest SHA mismatch."
        Assert-Equal $package.success_evidence.sha_identity.manifest_equals_payload $true "Manifest/payload SHA mismatch."
        Assert-Equal $package.success_evidence.sha_identity.pointer_equals_payload $true "Pointer/payload SHA mismatch."
        Assert-Equal $package.promotion_gate.all_required_checks_pass $true "Seven-point gate did not pass."
        Assert-Equal $package.promotion_gate.current_json_updated $true "Pointer update was not recorded."
        Assert-Equal $package.scope_scan.raw_parquet_copied_to_run_root $false "Package reports copied Parquet."
        Assert-Equal (@(Get-ChildItem -LiteralPath $sandbox.RunRoot -File -Recurse -Filter "*.parquet").Count) 0 "Raw Parquet was copied into RunRoot."
        Assert-Equal $package.scope_scan.season_2016_exists $false "2023 run did not report 2016 absence."
        Assert-Equal @($package.scope_scan.derived_artifact_paths).Count 0 "Derived artifacts were reported."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "mock failed result records failure and exits nonzero" {
    $sandbox = New-TestSandbox
    try {
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive") "failed"
        Assert-True ($result.ExitCode -ne 0) "Failed mock exited zero."
        $package = Get-LatestReviewPackage $sandbox
        Assert-Equal $package.status "failed_or_stale" "Failure status drifted."
        Assert-Equal $package.result.status "failed" "Adapter failure result was lost."
        Assert-Equal $package.result.failure_class "http_status" "Failure metadata was lost."
        Assert-Equal $package.adapter_invocation_attempted $true "Failed runner attempt was not recorded."
        Assert-Equal $package.provider_request_made $true "Failed provider request evidence was lost."
        Assert-Equal $package.provider_request_evidence_source "failed_attempt_event" "Failure request evidence source drifted."
        Assert-Equal @($package.provider_request_evidence_paths).Count 1 "Failure request evidence path was not recorded."
        Assert-True (@($package.events | Where-Object { $_.kind -eq "failed_attempt" }).Count -eq 1) "Failure event was not collected."
        Assert-True (@($package.events | Where-Object { $_.sha256 -match "^[0-9a-f]{64}$" }).Count -eq 1) "Failure event hash was not collected."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "local runner failure cannot assert a provider request" {
    $sandbox = New-TestSandbox
    try {
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive") "runner_failure"
        Assert-True ($result.ExitCode -ne 0) "Runner failure exited zero."
        $package = Get-LatestReviewPackage $sandbox
        Assert-Equal (Get-Counter $sandbox "adapter") 1 "Runner invocation attempt was not counted."
        Assert-Equal $package.status "failed_or_stale" "Runner failure status drifted."
        Assert-Equal $package.adapter_invocation_attempted $true "Runner failure lost the invocation attempt."
        Assert-Equal $package.provider_request_made $false "Runner failure falsely asserted a provider request."
        Assert-Equal $package.provider_request_evidence_source "none" "Runner failure invented an evidence source."
        Assert-Equal @($package.provider_request_evidence_paths).Count 0 "Runner failure invented an evidence path."
        Assert-Equal @($package.events).Count 0 "Runner failure unexpectedly emitted adapter evidence."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "cached-valid-after-failure is forced stale and nonzero" {
    $sandbox = New-TestSandbox
    try {
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-ExecuteLive") "cached"
        Assert-True ($result.ExitCode -ne 0) "Cached stale mock exited zero."
        $package = Get-LatestReviewPackage $sandbox
        Assert-Equal $package.status "failed_or_stale" "Cached result was emitted as success."
        Assert-Equal $package.result.status "cached_valid_after_failure" "Cached result status was lost."
        Assert-Equal $package.result.freshness "stale" "Cached result was not forced stale."
        Assert-Equal $package.result.stale_banner_required $true "Stale banner was not required."
        Assert-Equal $package.adapter_invocation_attempted $true "Cached runner attempt was not recorded."
        Assert-Equal $package.provider_request_made $true "Cached provider request evidence was lost."
        Assert-Equal $package.provider_request_evidence_source "failed_attempt_event" "Cached request evidence source drifted."
        Assert-Equal @($package.provider_request_evidence_paths).Count 1 "Cached request evidence path was not recorded."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "prior failed event is hashed and unchanged" {
    $sandbox = New-TestSandbox
    try {
        $eventsRoot = Join-Path $sandbox.DataRoot "season=2023\events"
        New-Item -ItemType Directory -Path $eventsRoot -Force | Out-Null
        $priorPath = Join-Path $eventsRoot "failed-attempt-approved.json"
        Set-Content -LiteralPath $priorPath -Value '{"failure_class":"approved_prior_failure"}' -Encoding utf8
        $before = (Get-FileHash -LiteralPath $priorPath -Algorithm SHA256).Hash
        $result = Invoke-Harness $sandbox (Get-CommonArguments $sandbox "-WhatIf")
        Assert-Equal $result.ExitCode 0 "WhatIf with prior failure did not pass."
        $package = Get-LatestReviewPackage $sandbox
        Assert-Equal @($package.data_root.prior_failed_attempts).Count 1 "Prior failure was not enumerated."
        Assert-Equal $package.data_root.prior_failed_attempts_unchanged $true "Prior failure was marked changed."
        Assert-Equal $package.provider_request_made $false "A preexisting failure event was treated as current request evidence."
        Assert-Equal $package.provider_request_evidence_source "none" "A preexisting failure event became an evidence source."
        Assert-Equal @($package.provider_request_evidence_paths).Count 0 "A preexisting failure event became a current evidence path."
        Assert-Equal (Get-FileHash -LiteralPath $priorPath -Algorithm SHA256).Hash $before "Prior failure bytes changed."
    }
    finally { Remove-TestSandbox $sandbox }
}

Invoke-TestCase "source has one adapter call and workflows have no live harness request" {
    $source = Get-Content -Raw -LiteralPath $HarnessPath
    Assert-Equal ([regex]::Matches($source, "result = ingest_nflverse_pbp_season\(").Count) 1 "Harness source does not contain exactly one adapter call."
    $workflowHits = @(
        Get-ChildItem -LiteralPath (Join-Path $RepositoryRoot ".github\workflows") -File -Recurse |
            Select-String -Pattern "(?i)-ExecuteLive"
    )
    Assert-Equal $workflowHits.Count 0 "A GitHub Actions workflow performs a live controlled run."
}

Write-Host "B06 harness acceptance: $Passed passed, $($Failures.Count) failed"
if ($Failures.Count -gt 0) {
    foreach ($failure in $Failures) { Write-Host "  $failure" }
    exit 1
}
exit 0
