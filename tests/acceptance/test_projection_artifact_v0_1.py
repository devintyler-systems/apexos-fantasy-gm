"""PA01–PA13 acceptance coverage for the fixture-only artifact foundation."""
from __future__ import annotations

import copy
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from engine.projections import projection_artifact_v0_1 as artifact_module
from engine.projections.projection_artifact_v0_1 import ProjectionArtifactError, build_artifact


FIXTURES = Path("tests/fixtures/projection_artifact_v0_1")


def _document() -> dict:
    return json.loads((FIXTURES / "valid_input.json").read_text(encoding="utf-8"))


def _build(document: dict):
    return build_artifact(document, FIXTURES)


def _fails(document: dict, code: str) -> None:
    with pytest.raises(ProjectionArtifactError, match=code):
        _build(document)


def test_pa01_valid_fixture_builds_schema_valid_artifact():
    artifact, artifact_bytes, manifest_bytes = _build(_document())
    assert artifact["artifact_version"] == "0.1"
    assert artifact["frozen"] is True
    assert artifact["input_snapshot_id"].startswith("sha256:")
    assert json.loads(artifact_bytes)["projection_rows"][0]["canonical_player_id"] == "player-001"
    assert json.loads(manifest_bytes)["row_count"] == 1


def test_pa02_identical_inputs_are_byte_identical():
    first = _build(_document())
    second = _build(_document())
    assert first[0]["input_snapshot_id"] == second[0]["input_snapshot_id"]
    assert first[1:] == second[1:]


def test_pa03_missing_source_evidence_fails_closed():
    document = _document()
    document["source_manifest"] = []
    _fails(document, "PA03_SOURCE_EVIDENCE_MISSING")


def test_pa04_hash_mismatch_fails_closed():
    document = _document()
    document["source_manifest"][0]["source_sha256"] = "0" * 64
    _fails(document, "PA04_SHA256_MISMATCH")


def test_pa05_post_as_of_evidence_fails_closed():
    document = _document()
    document["source_manifest"][0]["effective_time_utc"] = "2026-08-25T00:00:01Z"
    _fails(document, "PA05_POST_AS_OF_EVIDENCE")


def test_pa06_unapproved_role_fails_closed():
    document = _document()
    document["source_manifest"][0]["allowed_role"] = "provider_evidence"
    _fails(document, "PA06_SOURCE_ROLE_UNAPPROVED")


@pytest.mark.parametrize("role", ["external_ranking", "adp", "analyst_projection"])
def test_pa07_ranking_adp_and_analyst_roles_fail_closed(role):
    document = _document()
    document["source_manifest"][0]["allowed_role"] = role
    _fails(document, "PA07_EXTERNAL_RANKING_INPUT")


@pytest.mark.parametrize("mutation", [
    lambda document: document["projection_rows"][0].update(canonical_player_id="player-404"),
    lambda document: document["identity_snapshot"].update(aliases=[{"candidate_player_ids": ["player-001", "player-002"]}]),
    lambda document: document["identity_snapshot"]["teams"].append({"canonical_team_id": "team-aaa"}),
])
def test_pa08_ambiguous_or_unresolved_identity_fails_closed(mutation):
    document = _document()
    mutation(document)
    with pytest.raises(ProjectionArtifactError) as error:
        _build(document)
    assert error.value.code.startswith("PA08_")


def test_pa09_manual_override_requires_complete_additive_provenance():
    document = _document()
    row = document["projection_rows"][0]
    row["manual_environment_override"] = {"owner": "operator"}
    _fails(document, "PA09_OVERRIDE_PROVENANCE_INVALID")


def test_pa10_frozen_artifact_overwrite_fails_closed():
    artifact, _, _ = _build(_document())
    with pytest.raises(ProjectionArtifactError, match="PA10_FROZEN_ARTIFACT_OVERWRITE"):
        build_artifact(_document(), FIXTURES, artifact)


def test_pa11_prohibited_scoring_prv_availability_and_recommendation_fields_fail_closed():
    for field in ("scoring", "prv", "availability", "roster_fit", "recommendation"):
        document = _document()
        document[field] = "prohibited"
        _fails(document, "PA11_PROHIBITED_FIELD")


def test_pa12_module_has_no_b06_b07_import_or_runtime_dependency():
    source = inspect.getsource(artifact_module)
    assert "engine.ingestion" not in source
    assert "b07_baseline" not in source
    assert "engine.contracts.b07" not in source


def test_pa13_cli_validate_and_build_are_deterministic_and_tmp_only(tmp_path):
    fixture = (FIXTURES / "valid_input.json").resolve()
    command = [sys.executable, "tools/build_projection_artifact_v0_1.py", "validate", "--input", str(fixture)]
    validated = subprocess.run(command, capture_output=True, text=True, check=False)
    assert validated.returncode == 0, validated.stderr
    first = tmp_path / "first"
    second = tmp_path / "second"
    for output in (first, second):
        built = subprocess.run(
            [sys.executable, "tools/build_projection_artifact_v0_1.py", "build", "--input", str(fixture), "--output", str(output)],
            capture_output=True, text=True, check=False,
        )
        assert built.returncode == 0, built.stderr
    assert (first / "projection_artifact.json").read_bytes() == (second / "projection_artifact.json").read_bytes()
    assert (first / "projection_artifact.manifest.json").read_bytes() == (second / "projection_artifact.manifest.json").read_bytes()
