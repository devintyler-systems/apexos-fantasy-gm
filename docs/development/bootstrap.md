# Python bootstrap

`pyproject.toml` is the canonical Python dependency and tooling contract for
this repository. The supported Python runtime is `>=3.12,<3.13`. Its sole
core runtime dependency is `PyYAML`; test tooling is installed through the
explicit `dev` extra, which contains `pytest`.

Install the project for development and test work with the canonical command:

```powershell
python -m pip install -e ".[dev]"
```

This editable install explicitly discovers the top-level `engine/` package.
The import validation below runs outside the checkout so it proves editable
installation and package discovery rather than succeeding through
current-directory import shadowing.

## Verification

Run this procedure from the repository root:

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = (git rev-parse --show-toplevel).Trim()
$venv = Join-Path $env:TEMP "apexos-b01-clean-$([guid]::NewGuid().ToString('N'))"
$outside = Join-Path $env:TEMP "apexos-b01-import-$([guid]::NewGuid().ToString('N'))"

try {
    py -3.12 -m venv $venv
    & "$venv\Scripts\python.exe" --version
    & "$venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$venv\Scripts\python.exe" -m pip install -e "${repo}[dev]"

    & "$venv\Scripts\python.exe" -m pip show apexos-fantasy-gm

    New-Item -ItemType Directory -Path $outside | Out-Null
    Push-Location $outside
    & "$venv\Scripts\python.exe" -c "from engine.draft_state.manager import DraftStateManager; print('import-ok')"
    Pop-Location

    Push-Location $repo
    & "$venv\Scripts\python.exe" -m pytest tests/acceptance/ -q
    git diff --check
    git status --short
    Pop-Location
}
finally {
    if ((Get-Location).Path -eq $outside) {
        Pop-Location
    }
    Remove-Item -Recurse -Force $venv, $outside -ErrorAction SilentlyContinue
}
```

## Scope boundary

B-01 creates no ingestion, NFL data access, Parquet, caching, manifests,
schema, migration, or B-06 artifact. B-06 will separately define and validate
its Python-3.12-compatible direct nflverse Parquet adapter dependency contract.
Dependency resolution and lockfile policy remain separate decisions.
