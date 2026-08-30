"""Regression coverage for canonical nflverse authorization and active U08 boundaries."""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


V06 = Path("contracts/league_rules/spamml-2026-v0.6.yaml")
V07 = Path("contracts/league_rules/spamml-2026-v0.7.yaml")
SOURCE_REGISTER = Path(
    "contracts/projections/apexos-projection-source-authorization-register-v0.1.md"
)
RECONCILIATION = Path(
    "contracts/projections/apexos-nflverse-authorization-reconciliation-v0.1.md"
)
LEGACY_CANDIDATE = Path(
    "contracts/projections/source-authorizations/"
    "nflverse-direct-github-release-assets-2026-player-facts-candidate-v0.1.md"
)


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_v07_resolves_u08_exactly_and_leaves_v06_outside_this_pr():
    rules = yaml.safe_load(V07.read_text(encoding="utf-8"))
    prior_rules = yaml.safe_load(V06.read_text(encoding="utf-8"))
    assert rules["league_id"] == "spamml-2026"
    assert rules["contract_version"] == "0.7"
    assert rules["amends"] == str(V06).replace("\\", "/")
    assert rules["keeper_dynasty"] == {"keeper": "none", "dynasty": False}
    resolution = rules["resolved_by_this_version"]
    assert len(resolution) == 1
    assert resolution[0]["id"] == "U08"
    assert resolution[0]["field"] == "keeper_dynasty"
    assert (
        resolution[0]["resolution"]
        == "SPAMML 2026 is a redraft league with no keepers and no dynasty behavior."
    )
    assert str(resolution[0]["resolved_date"]) == "2026-08-27"
    assert "U08" not in {item["id"] for item in rules["unknown_or_unconfirmed"]}
    assert rules["unknown_or_unconfirmed"] == [
        item for item in prior_rules["unknown_or_unconfirmed"] if item["id"] != "U08"
    ]
    assert subprocess.run(
        ["git", "diff", "--quiet", "origin/main", "--", str(V06)],
        check=False,
    ).returncode == 0


def test_v07_retains_v12_as_sole_planned_schedule_timestamp_authority():
    rules = yaml.safe_load(V07.read_text(encoding="utf-8"))
    authority = "contracts/draft/spamml-2026-draft-seat-assignment-v1.2.yaml"
    assert (
        rules["schedule_authority"]["sole_canonical_planned_timestamp_artifact"]
        == authority
    )
    assert rules["draft"]["schedule_timestamp_authority"] == authority
    assert (
        "sole canonical SPAMML 2026 planned schedule timestamp authority"
        in rules["schedule_authority"]["rule"]
    )


def test_legacy_candidate_artifact_is_removed_by_supersession():
    assert not LEGACY_CANDIDATE.exists()
    reconciliation = _text(RECONCILIATION)
    assert "**Ruling:** `SUPERSESSION`, not compatibility." in reconciliation
    assert "superseded_and_removed" in reconciliation
    assert "obsolete_and_removed" in reconciliation
    assert str(LEGACY_CANDIDATE).replace("\\", "/") in reconciliation


def test_canonical_source_register_is_the_sole_nflverse_authority():
    register = _text(SOURCE_REGISTER)
    reconciliation = _text(RECONCILIATION)
    canonical_path = (
        "contracts/projections/"
        "apexos-projection-source-authorization-register-v0.1.md"
    )
    assert canonical_path in reconciliation
    assert "sole repository-level source authorization boundary" in reconciliation
    assert 'source_id: "nflverse_direct_github_release_assets"' in register
    assert 'status: "approved_bounded"' in register
    assert 'approved: "Direct GitHub release-asset access"' in register
    assert '"nfl_data_py"' in register
    assert "Historical football-event evidence" in register
    assert "No source retrieval, source ingestion, source parsing, data storage" in register
    assert "No player feature, team feature, event target, player estimate, model" in register


def test_canonical_source_register_prohibits_provider_contamination_and_fallback():
    register = _text(SOURCE_REGISTER)
    for prohibited in (
        "Fantrax FPTs / FPts",
        "Fantrax FP/G",
        "Fantrax Rk / RkOv",
        "Fantrax ADP",
        "Any provider-generated player rank, fantasy point total, recommendation, or consensus output",
        "Training target or label for ApexOS player fantasy-point projections",
        "Calibration target for ApexOS football event rates or scoring outputs",
        "Silent fallback when ApexOS artifact generation, validation, identity mapping, scoring reconciliation, source authorization, or time-integrity validation fails",
    ):
        assert prohibited in register
    assert "PROVIDER_CONTAMINATION_DETECTED" in register
    assert "No provider-projection fallback." in register
    assert (
        "Explicit provider_snapshot mode with degraded status and mandatory "
        "provider-authority disclosure"
        in register
    )
    assert "Display-only comparison context in apexos_projection mode" in register


def test_reconciliation_preserves_future_ingestion_acceptance_requirements():
    reconciliation = _text(RECONCILIATION)
    for required in (
        "Direct GitHub release-asset access only; `nfl_data_py` rejected.",
        "Immutable raw-evidence snapshot manifest and source asset identity.",
        "Canonical identity mapping, ambiguity quarantine, and no destructive merge behavior.",
        "Time-integrity checks and rejection of post-decision information.",
        "Visible degraded behavior for source authorization, snapshot, schema, identity, freshness, and temporal failures.",
        "No provider-projection input, provider fallback, or provider-derived decision influence in ApexOS Projection Mode.",
        "Read-only behavior and no external fantasy-platform action.",
    ):
        assert required in reconciliation
