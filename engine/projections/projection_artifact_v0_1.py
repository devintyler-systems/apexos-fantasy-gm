"""Deterministic, fixture-only ApexOS projection artifact foundation v0.1.

The boundary intentionally validates supplied scoring-event expectations without
calculating fantasy scoring, PRV, availability, roster fit, or recommendations.
It has no provider, B-06, or B-07 dependency.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Mapping, Sequence
from typing import Any

from engine.canonical.projection_identity_snapshot import (
    ProjectionIdentityError,
    validate_identity_snapshot,
    validate_projection_identity,
)


class ProjectionArtifactError(ValueError):
    """A deterministic fail-closed validation error with a machine reason code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


ARTIFACT_VERSION = "0.1"
EVENT_KEYS = frozenset({
    "passing_touchdowns", "rushing_touchdowns", "receiving_touchdowns",
    "field_goals_made", "extra_points_made",
    "defensive_special_teams_touchdowns", "safeties", "two_point_conversions",
})
POSITIONS = frozenset({"QB", "HB", "FB", "WR", "TE", "K", "TEAM"})
METADATA_KEYS = frozenset({
    "artifact_id", "artifact_version", "created_at_utc", "as_of_timestamp_utc",
    "input_snapshot_id", "repository_commit_sha", "league_rules_version",
    "canonical_identity_snapshot_id", "frozen", "data_freshness_status",
    "source_manifest", "known_limitations", "projection_rows",
})
SOURCE_KEYS = frozenset({"source_id", "source_path", "source_sha256", "retrieved_at_utc", "effective_time_utc", "allowed_role"})
ROW_KEYS = frozenset({
    "canonical_player_id", "canonical_team_id", "position", "projection_model_version",
    "input_snapshot_id", "source_evidence_refs", "raw_model_expected_scoring_events",
    "manual_environment_override", "final_expected_scoring_events", "uncertainty",
    "data_freshness_status", "known_limitations",
})
OVERRIDE_KEYS = frozenset({"owner", "reason", "timestamp_utc", "raw_value", "override_value"})
SAFE_SOURCE_ROLES = frozenset({"fixture_evidence", "apexos_owned_evidence"})
PROHIBITED_SOURCE_ROLES = frozenset({"external_ranking", "ranking", "adp", "analyst_projection", "analyst-projection"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _fail(code: str, message: str) -> None:
    raise ProjectionArtifactError(code, message)


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        _fail("PA05_TIMESTAMP_INVALID", f"{field} must be an ISO-8601 UTC timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("PA05_TIMESTAMP_INVALID", f"{field} must be an ISO-8601 UTC timestamp")
    if result.tzinfo is None or result.utcoffset() != timezone.utc.utcoffset(result):
        _fail("PA05_TIMESTAMP_INVALID", f"{field} must be UTC")
    return result.astimezone(timezone.utc)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8") + b"\n"


def _canonical_source_bytes(path: Path) -> bytes:
    """Hash text fixtures by Git-portable LF bytes, never silently altering data."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def _exact_mapping(value: Any, keys: frozenset[str], code: str, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        _fail(code, f"{name} must contain exactly {sorted(keys)}")
    return value


def _event_values(value: Any, name: str) -> Mapping[str, float | int]:
    mapping = _exact_mapping(value, EVENT_KEYS, "PA11_SCORING_EVENT_SCHEMA_INVALID", name)
    for key, number in mapping.items():
        if type(number) not in {int, float} or number < 0:
            _fail("PA11_SCORING_EVENT_VALUE_INVALID", f"{name}.{key} must be a non-negative finite number")
        if isinstance(number, float) and (number != number or number in {float("inf"), float("-inf")}):
            _fail("PA11_SCORING_EVENT_VALUE_INVALID", f"{name}.{key} must be finite")
    return mapping


def _prohibited_fields(value: Any, path: str = "$") -> None:
    forbidden = {"fantasy_scoring", "fantasy_points", "scoring", "prv", "availability", "roster_fit", "recommendation", "endpoint", "external_write"}
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in forbidden:
                _fail("PA11_PROHIBITED_FIELD", f"{path}.{key} is outside v0.1")
            _prohibited_fields(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _prohibited_fields(child, f"{path}[{index}]")


def _source_path(base_path: Path, declared_path: str) -> Path:
    if not declared_path or declared_path.startswith(("http:", "https:")) or "data/raw" in declared_path.replace("\\", "/"):
        _fail("PA03_SOURCE_PATH_UNAPPROVED", "source_path must be a local approved fixture/evidence path")
    candidate = (base_path / declared_path).resolve()
    try:
        candidate.relative_to(base_path.resolve())
    except ValueError:
        _fail("PA03_SOURCE_PATH_UNAPPROVED", "source_path may not escape the supplied fixture directory")
    return candidate


def create_input_snapshot_id(document: Mapping[str, Any]) -> str:
    """Create a stable ID from evidence, identity snapshot, and projection rows."""
    material = {
        "canonical_identity_snapshot_id": document.get("canonical_identity_snapshot_id"),
        "identity_snapshot": document.get("identity_snapshot"),
        "source_manifest": document.get("source_manifest"),
        "projection_rows": document.get("projection_rows"),
        "as_of_timestamp_utc": document.get("as_of_timestamp_utc"),
    }
    return "sha256:" + hashlib.sha256(_canonical_bytes(material)).hexdigest()


def validate_source_manifest(document: Mapping[str, Any], base_path: Path) -> None:
    as_of = _timestamp(document.get("as_of_timestamp_utc"), "as_of_timestamp_utc")
    sources = document.get("source_manifest")
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)) or not sources:
        _fail("PA03_SOURCE_EVIDENCE_MISSING", "source_manifest must be a non-empty list")
    source_ids: set[str] = set()
    for source in sources:
        source = _exact_mapping(source, SOURCE_KEYS, "PA03_SOURCE_SCHEMA_INVALID", "source manifest entry")
        source_id = source["source_id"]
        if not isinstance(source_id, str) or not source_id or source_id in source_ids:
            _fail("PA03_SOURCE_EVIDENCE_MISSING", "source_id must be non-empty and unique")
        source_ids.add(source_id)
        role = source["allowed_role"]
        if role in PROHIBITED_SOURCE_ROLES:
            _fail("PA07_EXTERNAL_RANKING_INPUT", f"source role {role!r} is benchmark-only")
        if role not in SAFE_SOURCE_ROLES:
            _fail("PA06_SOURCE_ROLE_UNAPPROVED", f"source role {role!r} is not approved for v0.1")
        if not isinstance(source["source_sha256"], str) or not _SHA256.fullmatch(source["source_sha256"]):
            _fail("PA04_SHA256_INVALID", "source_sha256 must be lowercase SHA-256")
        _timestamp(source["retrieved_at_utc"], "retrieved_at_utc")
        if _timestamp(source["effective_time_utc"], "effective_time_utc") > as_of:
            _fail("PA05_POST_AS_OF_EVIDENCE", "source effective_time_utc is after artifact as_of_timestamp_utc")
        path = _source_path(base_path, source["source_path"])
        try:
            observed = hashlib.sha256(_canonical_source_bytes(path)).hexdigest()
        except OSError as exc:
            raise ProjectionArtifactError("PA03_SOURCE_EVIDENCE_MISSING", f"source evidence is unavailable: {path}") from exc
        if observed != source["source_sha256"]:
            _fail("PA04_SHA256_MISMATCH", f"source_sha256 does not match {source['source_path']}")


def _validate_override(row: Mapping[str, Any], as_of: datetime) -> None:
    override = row["manual_environment_override"]
    raw = _event_values(row["raw_model_expected_scoring_events"], "raw_model_expected_scoring_events")
    final = _event_values(row["final_expected_scoring_events"], "final_expected_scoring_events")
    if override is None:
        if dict(raw) != dict(final):
            _fail("PA09_OVERRIDE_REQUIRED", "final events may differ from raw events only through an audited additive override")
        return
    override = _exact_mapping(override, OVERRIDE_KEYS, "PA09_OVERRIDE_PROVENANCE_INVALID", "manual_environment_override")
    if not all(isinstance(override[key], str) and override[key].strip() for key in ("owner", "reason")):
        _fail("PA09_OVERRIDE_PROVENANCE_INVALID", "override owner and reason are required")
    if _timestamp(override["timestamp_utc"], "manual_environment_override.timestamp_utc") > as_of:
        _fail("PA09_OVERRIDE_PROVENANCE_INVALID", "override timestamp may not postdate as_of")
    raw_value = _event_values(override["raw_value"], "manual_environment_override.raw_value")
    override_value = _event_values(override["override_value"], "manual_environment_override.override_value")
    if dict(raw_value) != dict(raw):
        _fail("PA09_OVERRIDE_PROVENANCE_INVALID", "override raw_value must preserve the row raw value")
    expected_final = {key: raw[key] + override_value[key] for key in EVENT_KEYS}
    if dict(final) != expected_final:
        _fail("PA09_OVERRIDE_NOT_ADDITIVE", "final events must equal raw events plus override events")


def validate_document(document: Mapping[str, Any], base_path: str | Path) -> None:
    """Fail closed on every v0.1 metadata, evidence, identity, and row defect."""
    if not isinstance(document, Mapping):
        _fail("PA01_DOCUMENT_INVALID", "input must be an object")
    _prohibited_fields(document)
    allowed_input_keys = set(METADATA_KEYS) | {"identity_snapshot"}
    if set(document) != allowed_input_keys:
        _fail("PA01_ARTIFACT_SCHEMA_INVALID", "input must contain exactly v0.1 artifact fields and identity_snapshot")
    if document["artifact_version"] != ARTIFACT_VERSION:
        _fail("PA01_ARTIFACT_VERSION_INVALID", "artifact_version must be '0.1'")
    if not isinstance(document["artifact_id"], str) or not document["artifact_id"].strip():
        _fail("PA01_ARTIFACT_METADATA_INVALID", "artifact_id is required")
    if not isinstance(document["repository_commit_sha"], str) or not _COMMIT.fullmatch(document["repository_commit_sha"]):
        _fail("PA01_ARTIFACT_METADATA_INVALID", "repository_commit_sha must be a full lowercase Git SHA")
    if not isinstance(document["league_rules_version"], str) or document["league_rules_version"] != "0.6":
        _fail("PA01_ARTIFACT_METADATA_INVALID", "league_rules_version must bind v0.6")
    if document["frozen"] is not True or document["data_freshness_status"] not in {"fresh", "stale", "incomplete"}:
        _fail("PA01_ARTIFACT_METADATA_INVALID", "frozen=true and a valid data_freshness_status are required")
    if not isinstance(document["known_limitations"], list) or not all(isinstance(item, str) for item in document["known_limitations"]):
        _fail("PA01_ARTIFACT_METADATA_INVALID", "known_limitations must be a string list")
    _timestamp(document["created_at_utc"], "created_at_utc")
    as_of = _timestamp(document["as_of_timestamp_utc"], "as_of_timestamp_utc")
    validate_source_manifest(document, Path(base_path))
    snapshot = document["identity_snapshot"]
    try:
        validate_identity_snapshot(snapshot)
    except ProjectionIdentityError as exc:
        raise ProjectionArtifactError(exc.code, str(exc)) from exc
    if document["canonical_identity_snapshot_id"] != snapshot.get("canonical_identity_snapshot_id"):
        _fail("PA08_IDENTITY_SNAPSHOT_INVALID", "metadata identity snapshot ID must match supplied identity snapshot")
    expected_snapshot_id = create_input_snapshot_id(document)
    supplied_snapshot_id = document["input_snapshot_id"]
    if supplied_snapshot_id not in {"AUTO", expected_snapshot_id}:
        _fail("PA02_INPUT_SNAPSHOT_INVALID", "input_snapshot_id must be AUTO or the deterministic snapshot ID")
    rows = document["projection_rows"]
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        _fail("PA01_ROW_SCHEMA_INVALID", "projection_rows must be a non-empty list")
    source_ids = {source["source_id"] for source in document["source_manifest"]}
    player_ids: set[str] = set()
    for row in rows:
        row = _exact_mapping(row, ROW_KEYS, "PA01_ROW_SCHEMA_INVALID", "projection row")
        if row["position"] not in POSITIONS:
            _fail("PA08_PLAYER_IDENTITY_INVALID", "row position is not permitted")
        try:
            validate_projection_identity(row, snapshot)
        except ProjectionIdentityError as exc:
            raise ProjectionArtifactError(exc.code, str(exc)) from exc
        player_id = row["canonical_player_id"]
        if player_id in player_ids:
            _fail("PA08_DUPLICATE_PLAYER_IDENTITY", f"duplicate projection row for {player_id}")
        player_ids.add(player_id)
        if row["input_snapshot_id"] not in {"AUTO", expected_snapshot_id}:
            _fail("PA02_INPUT_SNAPSHOT_INVALID", "row input_snapshot_id must match the deterministic snapshot ID")
        references = row["source_evidence_refs"]
        if not isinstance(references, list) or not references or not all(isinstance(ref, str) and ref in source_ids for ref in references):
            _fail("PA03_SOURCE_EVIDENCE_MISSING", "every row needs references to declared source evidence")
        if not isinstance(row["projection_model_version"], str) or not row["projection_model_version"].strip():
            _fail("PA01_ROW_SCHEMA_INVALID", "projection_model_version is required")
        if not isinstance(row["uncertainty"], Mapping) or not row["uncertainty"]:
            _fail("PA01_ROW_SCHEMA_INVALID", "uncertainty must be a non-empty mapping")
        if row["data_freshness_status"] not in {"fresh", "stale", "incomplete"} or not isinstance(row["known_limitations"], list):
            _fail("PA01_ROW_SCHEMA_INVALID", "row freshness and known limitations are required")
        _validate_override(row, as_of)


def build_artifact(document: Mapping[str, Any], base_path: str | Path, existing_artifact: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], bytes, bytes]:
    """Build deterministic artifact and manifest bytes from already supplied inputs."""
    validate_document(document, base_path)
    if existing_artifact and existing_artifact.get("frozen") is True and existing_artifact.get("artifact_id") == document["artifact_id"] and existing_artifact.get("artifact_version") == document["artifact_version"]:
        _fail("PA10_FROZEN_ARTIFACT_OVERWRITE", "corrections require a new artifact version")
    snapshot_id = create_input_snapshot_id(document)
    artifact = {key: document[key] for key in METADATA_KEYS}
    artifact["input_snapshot_id"] = snapshot_id
    artifact["projection_rows"] = [dict(row, input_snapshot_id=snapshot_id) for row in document["projection_rows"]]
    artifact_bytes = _canonical_bytes(artifact)
    manifest = {
        "artifact_id": artifact["artifact_id"], "artifact_version": artifact["artifact_version"],
        "input_snapshot_id": snapshot_id, "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        "frozen": True, "row_count": len(artifact["projection_rows"]),
    }
    return artifact, artifact_bytes, _canonical_bytes(manifest)
