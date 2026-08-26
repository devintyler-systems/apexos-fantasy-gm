from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from engine.contracts.b07_v0_1 import B07ValidationError, validate_season_access
from engine.projections import b07_baseline
from engine.projections.b07_baseline import (
    BASELINE_VERSION,
    EXPECTED_CONTRACT_SHA256,
    REQUIRED_COLUMNS,
    BaselineValidationError,
    EligibleEvent,
    SourceIdentity,
    SourceSpec,
    build_lookup_tables,
    evaluate_holdout,
    inspect_validation_artifact,
    load_contract_checked,
    read_eligible_events,
    score_holdout_events,
    serialize_lookup,
    validate_source_spec,
    write_validation_artifact,
)
from tools.run_b07_baseline import retained_inspection_evidence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPOSITORY_ROOT / "contracts" / "projections" / "b07_v0_1_contract.yaml"


@pytest.fixture(scope="module")
def contract() -> dict:
    return load_contract_checked(CONTRACT_PATH)


def _raw_row(**changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "season": 2023,
        "season_type": "REG",
        "game_id": "2023_01_A_B",
        "play_id": 10.0,
        "play_type": "run",
        "rush_attempt": 1.0,
        "pass_attempt": 0.0,
        "rusher_player_id": "00-rush",
        "rusher_id": "00-rush",
        "receiver_player_id": None,
        "receiver_id": None,
        "touchdown": 0.0,
        "rush_touchdown": 0.0,
        "pass_touchdown": 0.0,
        "td_player_id": None,
        "yardline_100": 8.0,
        "down": 2.0,
        "ydstogo": 3.0,
        "goal_to_go": 1,
        "qtr": 2.0,
        "game_seconds_remaining": 1800.0,
        "score_differential": -3.0,
        "two_point_attempt": 0.0,
        "penalty": 0.0,
        "sack": 0.0,
        "qb_spike": 0.0,
        "aborted_play": 0.0,
    }
    row.update(changes)
    return row


def _write_payload(path: Path, rows: list[dict[str, object]]) -> None:
    normalized = [{name: row.get(name) for name in REQUIRED_COLUMNS} for row in rows]
    pq.write_table(pa.Table.from_pylist(normalized), path)


def _identity(season: int = 2023) -> SourceIdentity:
    return SourceIdentity(
        season=season,
        payload_path="synthetic.parquet",
        payload_sha256=f"{season}".ljust(64, "0"),
        payload_bytes=1,
        manifest_path="synthetic-manifest.json",
        manifest_sha256=f"m{season}".ljust(64, "0"),
        pointer_path="synthetic-current.json",
        pointer_sha256=f"p{season}".ljust(64, "0"),
        row_count=1,
        game_counts_by_season_type={"REG": 1},
        parser_version="synthetic-parser",
        normalization_version="b06-no-play-normalization-v0.1",
        canonical_identity_mapping_version="nflverse-canonical-player-id-no-merge-v0.1",
        provider="synthetic-local-fixture",
        canonical_source_id="synthetic",
        retrieved_at_utc="2026-08-24T00:00:00Z",
        effective_time="2026-08-23T00:00:00Z",
    )


def _source_fixture(tmp_path: Path, *, manifest_changes: dict | None = None) -> SourceSpec:
    payload = tmp_path / "pbp.parquet"
    _write_payload(payload, [_raw_row()])
    digest = "bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776"
    manifest = {
        "revision_sha256": digest,
        "computed_digest_sha256": digest,
        "row_count": 1,
        "game_counts_by_season_type": {"REG": 1},
        "promotion_result": "pass",
        "regular_season_game_count_valid": True,
        "unknown_row_count": 0,
        "digest_match": True,
        "parser_version": "synthetic-parser",
        "no_play_normalization_version": "b06-no-play-normalization-v0.1",
        "provider": "synthetic-local-fixture",
        "canonical_source_id": "synthetic",
        "retrieved_at_utc": "2026-08-24T00:00:00Z",
        "effective_time": "2026-08-23T00:00:00Z",
    }
    if manifest_changes:
        manifest.update(manifest_changes)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    pointer = tmp_path / "current.json"
    pointer.write_text(json.dumps({"revision_sha256": digest}), encoding="utf-8")
    return SourceSpec(2023, payload, manifest_path, pointer)


def _patch_payload_digest(monkeypatch: pytest.MonkeyPatch, payload: Path, digest: str) -> None:
    original = b07_baseline.sha256_file

    def patched(path: str | Path) -> str:
        return digest if Path(path) == payload else original(path)

    monkeypatch.setattr(b07_baseline, "sha256_file", patched)


def _event(
    *,
    season: int,
    estimator: str,
    index: int,
    band: str = "0_5",
    goal_to_go: bool = True,
    down: int = 1,
    label: int = 0,
) -> EligibleEvent:
    return EligibleEvent(
        season=season,
        estimator=estimator,
        game_id=f"{season}_{index // 4:03d}",
        play_id=str(index),
        source_event_locator=f"{season}:game:{index}",
        yardline_band=band,
        goal_to_go=goal_to_go,
        down=down,
        label=label,
        features={
            "yardline_100": 3,
            "down": down,
            "ydstogo": 2,
            "goal_to_go": goal_to_go,
            "quarter": 1,
            "game_seconds_remaining": 3500,
            "score_differential": 0,
        },
        payload_sha256=f"payload-{season}",
        manifest_sha256=f"manifest-{season}",
    )


def _scored_fixture(contract: dict) -> tuple[dict, list[dict]]:
    development = [
        _event(
            season=2023 + (index % 2),
            estimator=estimator,
            index=index + offset,
            label=1 if index % 10 == 0 else 0,
        )
        for offset, estimator in ((0, "rush"), (100, "pass_target"))
        for index in range(40)
    ]
    lookup = build_lookup_tables(development, contract)
    holdout = [
        _event(
            season=2025,
            estimator=estimator,
            index=index + offset,
            label=1 if index % 9 == 0 else 0,
        )
        for offset, estimator in ((200, "rush"), (300, "pass_target"))
        for index in range(20)
    ]
    scored = score_holdout_events(
        holdout,
        lookup,
        input_snapshot_id="snapshot",
        contract_sha256=EXPECTED_CONTRACT_SHA256,
        as_of_timestamp="2026-08-24T00:00:00Z",
    )
    return serialize_lookup(lookup), scored


def test_contract_sha_and_version_are_required(contract: dict) -> None:
    assert b07_baseline.sha256_contract_file(CONTRACT_PATH) == EXPECTED_CONTRACT_SHA256
    assert contract["b07_v0_1_contract"]["schema_version"] == "0.1.0"


def test_contract_digest_uses_canonical_lf_bytes_for_lf_and_crlf_copies(tmp_path: Path) -> None:
    lf_bytes = CONTRACT_PATH.read_bytes().replace(b"\r\n", b"\n")
    lf_path = tmp_path / "contract-lf.yaml"
    crlf_path = tmp_path / "contract-crlf.yaml"
    lf_path.write_bytes(lf_bytes)
    crlf_path.write_bytes(lf_bytes.replace(b"\n", b"\r\n"))

    assert b07_baseline.sha256_contract_file(lf_path) == EXPECTED_CONTRACT_SHA256
    assert b07_baseline.sha256_contract_file(crlf_path) == EXPECTED_CONTRACT_SHA256


@pytest.mark.parametrize(
    ("filename", "contents", "detail"),
    [
        ("contract-bom.yaml", b"\xef\xbb\xbf" + CONTRACT_PATH.read_bytes(), "UTF-8 BOM"),
        ("contract-lone-cr.yaml", CONTRACT_PATH.read_bytes() + b"\r", "lone CR"),
    ],
)
def test_contract_digest_rejects_noncanonical_bytes(
    tmp_path: Path, filename: str, contents: bytes, detail: str
) -> None:
    path = tmp_path / filename
    path.write_bytes(contents)
    with pytest.raises(b07_baseline.BaselineValidationError) as exc_info:
        load_contract_checked(path)
    assert exc_info.value.reason_code == "B07_CONTRACT_CANONICALIZATION_FAILED"
    assert detail in exc_info.value.detail


def test_contract_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    changed = tmp_path / "contract.yaml"
    changed.write_bytes(CONTRACT_PATH.read_bytes() + b"\n")
    with pytest.raises(BaselineValidationError) as exc_info:
        load_contract_checked(changed)
    assert exc_info.value.reason_code == "B07_CONTRACT_DIGEST_MISMATCH"


def test_source_manifest_payload_and_event_counts_validate(
    contract: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = _source_fixture(tmp_path)
    digest = "bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776"
    _patch_payload_digest(monkeypatch, spec.payload_path, digest)
    identity = validate_source_spec(spec, contract)
    assert identity.payload_sha256 == digest
    assert identity.row_count == 1
    assert identity.game_counts_by_season_type == {"REG": 1}
    assert identity.manifest_sha256 == b07_baseline.sha256_bytes(spec.manifest_path.read_bytes())


@pytest.mark.parametrize(
    ("kind", "reason"),
    [
        ("payload", "B07_SOURCE_PAYLOAD_DIGEST_MISMATCH"),
        ("row_count", "B07_SOURCE_ROW_COUNT_MISMATCH"),
        ("event_count", "B07_SOURCE_EVENT_COUNT_MISMATCH"),
        ("pointer", "B07_SOURCE_POINTER_DIGEST_MISMATCH"),
    ],
)
def test_source_integrity_failures_have_stable_codes(
    contract: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    reason: str,
) -> None:
    changes = {"row_count": 2} if kind == "row_count" else None
    changes = {"game_counts_by_season_type": {"REG": 2}} if kind == "event_count" else changes
    spec = _source_fixture(tmp_path, manifest_changes=changes)
    digest = "bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776"
    _patch_payload_digest(monkeypatch, spec.payload_path, "0" * 64 if kind == "payload" else digest)
    if kind == "pointer":
        spec.pointer_path.write_text(json.dumps({"revision_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(BaselineValidationError) as exc_info:
        validate_source_spec(spec, contract)
    assert exc_info.value.reason_code == reason


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"play_type": "pass"}, "B07_EXCLUDE_UNSUPPORTED_OPPORTUNITY_TYPE"),
        ({"pass_attempt": 1.0}, "B07_EXCLUDE_CONFLICTING_OPPORTUNITY_FLAGS"),
        ({"play_type": "no_play"}, "B07_EXCLUDE_LOGICAL_NO_PLAY"),
        ({"play_type": "unexpected"}, "B07_EXCLUDE_LOGICAL_NO_PLAY_UNKNOWN"),
        ({"penalty": 1.0}, "B07_EXCLUDE_PENALIZED_EVENT"),
        ({"aborted_play": 1.0}, "B07_EXCLUDE_INELIGIBLE_EVENT"),
        ({"two_point_attempt": 1.0}, "B07_EXCLUDE_TWO_POINT_ATTEMPT"),
        ({"rusher_player_id": None}, "B07_EXCLUDE_MISSING_RUSHER_ID"),
        ({"rusher_id": "alternate"}, "B07_EXCLUDE_AMBIGUOUS_RUSHER_ID"),
        ({"touchdown": None}, "B07_EXCLUDE_MISSING_TOUCHDOWN_LABEL"),
        ({"touchdown": 2.0}, "B07_EXCLUDE_INVALID_TOUCHDOWN_LABEL"),
        ({"touchdown": 1.0}, "B07_EXCLUDE_TOUCHDOWN_LABEL_CONTRADICTION"),
        (
            {"touchdown": 1.0, "rush_touchdown": 1.0, "td_player_id": "other"},
            "B07_EXCLUDE_TOUCHDOWN_PLAYER_ID_MISMATCH",
        ),
        ({"yardline_100": None}, "B07_EXCLUDE_MISSING_YARDLINE_100"),
        ({"yardline_100": 100.0}, "B07_EXCLUDE_INVALID_YARDLINE_BAND"),
        ({"down": None}, "B07_EXCLUDE_MISSING_DOWN"),
        ({"down": 5.0}, "B07_EXCLUDE_INVALID_DOWN"),
        ({"ydstogo": 0.0}, "B07_EXCLUDE_INVALID_YDSTOGO"),
        ({"goal_to_go": None}, "B07_EXCLUDE_MISSING_GOAL_TO_GO"),
        ({"qtr": 6.0}, "B07_EXCLUDE_INVALID_QUARTER"),
        (
            {"game_seconds_remaining": -1.0},
            "B07_EXCLUDE_INVALID_GAME_SECONDS_REMAINING",
        ),
        (
            {"score_differential": None},
            "B07_EXCLUDE_MISSING_SCORE_DIFFERENTIAL",
        ),
    ],
)
def test_rush_exclusions_are_explicit_and_never_silent(
    contract: dict, tmp_path: Path, changes: dict, reason: str
) -> None:
    payload = tmp_path / "case.parquet"
    _write_payload(payload, [_raw_row(**changes)])
    spec = SourceSpec(2023, payload, tmp_path / "unused.json", tmp_path / "unused-current.json")
    events, summary = read_eligible_events(spec, _identity(), contract, access_mode="development")
    rush = summary["estimators"]["rush"]
    assert events == []
    assert rush["candidate_count"] == 1
    assert rush["eligible_count"] + rush["excluded_candidate_count"] == 1
    assert rush["exclusion_reason_counts"][reason] == 1


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"receiver_player_id": None}, "B07_EXCLUDE_MISSING_INTENDED_RECEIVER_ID"),
        ({"receiver_id": "alternate"}, "B07_EXCLUDE_AMBIGUOUS_INTENDED_RECEIVER_ID"),
        ({"sack": 1.0}, "B07_EXCLUDE_SACK"),
        ({"qb_spike": 1.0}, "B07_EXCLUDE_QB_SPIKE"),
    ],
)
def test_pass_target_exclusions_are_explicit(
    contract: dict, tmp_path: Path, changes: dict, reason: str
) -> None:
    pass_row = {
        "play_type": "pass",
        "rush_attempt": 0.0,
        "pass_attempt": 1.0,
        "receiver_player_id": "00-receiver",
        "receiver_id": "00-receiver",
        **changes,
    }
    row = _raw_row(**pass_row)
    payload = tmp_path / "case.parquet"
    _write_payload(payload, [row])
    spec = SourceSpec(2023, payload, tmp_path / "unused.json", tmp_path / "unused-current.json")
    _, summary = read_eligible_events(spec, _identity(), contract, access_mode="development")
    assert summary["estimators"]["pass_target"]["exclusion_reason_counts"][reason] == 1


def test_goal_to_go_is_read_raw_and_never_inferred(contract: dict, tmp_path: Path) -> None:
    payload = tmp_path / "case.parquet"
    _write_payload(payload, [_raw_row(yardline_100=3.0, ydstogo=3.0, goal_to_go=None)])
    spec = SourceSpec(2023, payload, tmp_path / "unused.json", tmp_path / "unused-current.json")
    events, summary = read_eligible_events(spec, _identity(), contract, access_mode="development")
    assert events == []
    assert summary["estimators"]["rush"]["exclusion_reason_counts"][
        "B07_EXCLUDE_MISSING_GOAL_TO_GO"
    ] == 1


def test_baseline_features_exclude_all_post_play_fields(contract: dict, tmp_path: Path) -> None:
    payload = tmp_path / "case.parquet"
    _write_payload(payload, [_raw_row()])
    spec = SourceSpec(2023, payload, tmp_path / "unused.json", tmp_path / "unused-current.json")
    events, _ = read_eligible_events(spec, _identity(), contract, access_mode="development")
    assert len(events) == 1
    assert set(events[0].features) == set(contract["b07_v0_1_contract"]["feature_allowlist"])
    assert set(events[0].features).isdisjoint(b07_baseline.POST_PLAY_FIELDS)


def test_lookup_tables_are_separate_by_estimator(contract: dict) -> None:
    events = [
        _event(season=2023, estimator=estimator, index=index, label=index % 7 == 0)
        for estimator in ("rush", "pass_target")
        for index in range(35)
    ]
    lookup = build_lookup_tables(events, contract)
    global_level = lookup.hierarchy[-1]
    assert lookup.cells[global_level][("rush",)] != lookup.cells[global_level][("pass_target",)] or (
        "rush",
    ) != ("pass_target",)
    assert {key[0] for key in lookup.cells[global_level]} == {"rush", "pass_target"}


def test_exact_support_threshold_and_backoff_order(contract: dict) -> None:
    events = [
        _event(season=2023, estimator="rush", index=index, down=1)
        for index in range(29)
    ]
    events.append(_event(season=2024, estimator="rush", index=99, down=2, label=1))
    lookup = build_lookup_tables(events, contract)
    holdout = [_event(season=2025, estimator="rush", index=200, down=1)]
    scored = score_holdout_events(
        holdout,
        lookup,
        input_snapshot_id="snapshot",
        contract_sha256=EXPECTED_CONTRACT_SHA256,
        as_of_timestamp="2026-08-24T00:00:00Z",
    )
    assert lookup.threshold == 30
    assert lookup.hierarchy == (
        ("opportunity_type", "yardline_band", "goal_to_go", "down"),
        ("opportunity_type", "yardline_band", "goal_to_go"),
        ("opportunity_type", "yardline_band"),
        ("opportunity_type_global_rate",),
    )
    assert scored[0]["lookup_level_selected"] == 1
    assert scored[0]["development_opportunity_count"] == 30


def test_identical_snapshot_and_contract_are_deterministic(contract: dict) -> None:
    lookup_payload, scored = _scored_fixture(contract)
    lookup_payload_again, scored_again = _scored_fixture(contract)
    assert lookup_payload_again == lookup_payload
    assert scored_again == scored


def test_2025_cannot_enter_lookup_or_development_paths(contract: dict) -> None:
    with pytest.raises(BaselineValidationError) as exc_info:
        build_lookup_tables([_event(season=2025, estimator="rush", index=1)], contract)
    assert exc_info.value.reason_code == "B07_HOLDOUT_DEVELOPMENT_LEAKAGE"
    for purpose in (
        "fitting",
        "lookup_construction",
        "preprocessing",
        "category_inference",
        "domain_inference",
        "aggregation",
        "baseline_training",
    ):
        with pytest.raises(B07ValidationError):
            validate_season_access(contract, season=2025, purpose=purpose)


def test_2025_requires_explicit_evaluation_mode(contract: dict) -> None:
    assert (
        validate_season_access(
            contract,
            season=2025,
            purpose="holdout_evaluation",
            evaluation_mode=True,
            labels_requested=True,
        )
        is None
    )
    with pytest.raises(B07ValidationError):
        validate_season_access(
            contract,
            season=2025,
            purpose="holdout_evaluation",
            labels_requested=True,
        )


def _artifact_fixture(contract: dict) -> tuple[dict, dict, list[dict]]:
    lookup, scored = _scored_fixture(contract)
    eligibility = {
        "2025": {
            "estimators": {
                estimator: {
                    "candidate_count": 20,
                    "eligible_count": 20,
                    "excluded_candidate_count": 0,
                    "realized_touchdown_count": 3,
                    "realized_touchdown_rate": 0.15,
                    "exclusion_reason_counts": {},
                    "exclusion_reason_rates": {},
                }
                for estimator in ("rush", "pass_target")
            }
        }
    }
    evaluation = evaluate_holdout(
        scored, eligibility, contract, bootstrap_seed=12345
    )
    artifact = {
        "artifact_version": "b07-v0.1-baseline-1",
        "artifact_id": "synthetic",
        "run_id": "synthetic-run",
        "created_at": "2026-08-24T00:00:00Z",
        "as_of_timestamp": "2026-08-24T00:00:00Z",
        "result": "FRESH_SUCCESS_PENDING_REVIEW",
        "repository": {"checkout_sha": "sha", "worktree": "synthetic"},
        "contract": {
            "path": "contracts/projections/b07_v0_1_contract.yaml",
            "schema_version": "0.1.0",
            "sha256": EXPECTED_CONTRACT_SHA256,
        },
        "source_inputs": {
            "input_snapshot_ids": ["snapshot"],
            "accepted_payload_digests": {},
            "manifest_digests": {},
            "parser_versions": {},
            "normalization_versions": {},
            "canonical_identity_mapping_versions": {},
        },
        "split": {
            "development_seasons": [2023, 2024],
            "holdout_season": 2025,
            "holdout_access_mode": "evaluation_only",
            "holdout_fitting_access": False,
        },
        "baseline": {
            "version": BASELINE_VERSION,
            "estimators": ["rush", "pass_target"],
            "support_threshold": 30,
            "backoff_hierarchy": lookup["hierarchy"],
        },
        "eligibility": {
            "counts_by_season_estimator": eligibility,
            "exclusions_by_season_estimator_reason": {},
        },
        "evaluation": evaluation,
        "local_inspection": {"command": "read-only", "read_only": True},
        "promotion": {
            "production_promotion_authorized": False,
            "current_pointer_created": False,
            "recommendation_behavior_authorized": False,
        },
    }
    return artifact, lookup, scored


def test_artifact_has_required_linkage_reason_and_limitation_fields(
    contract: dict, tmp_path: Path
) -> None:
    artifact, lookup, scored = _artifact_fixture(contract)
    result = write_validation_artifact(tmp_path / "immutable-b07", artifact, lookup, scored)
    package = json.loads((Path(result["root"]) / "validation-artifact.json").read_text())[
        "b07_validation_artifact"
    ]
    assert package["contract"]["sha256"] == EXPECTED_CONTRACT_SHA256
    assert package["split"]["development_seasons"] == [2023, 2024]
    assert package["split"]["holdout_season"] == 2025
    assert package["created_at"] and package["artifact_version"]
    assert "exclusions_by_season_estimator_reason" in package["eligibility"]
    assert package["evaluation"]["limitations"]
    assert package["promotion"]["current_pointer_created"] is False
    assert not (Path(result["root"]) / "current.json").exists()
    assert inspect_validation_artifact(result["root"])["result"] == (
        "FRESH_SUCCESS_PENDING_REVIEW"
    )


def test_retained_inspection_exposes_all_package_digests_and_no_pointer(
    contract: dict, tmp_path: Path
) -> None:
    artifact, lookup, scored = _artifact_fixture(contract)
    result = write_validation_artifact(tmp_path / "immutable-b07", artifact, lookup, scored)

    evidence = retained_inspection_evidence(result["root"])

    assert evidence["artifact_root"] == str(Path(result["root"]).resolve())
    assert evidence["run_id"] == "synthetic-run"
    assert evidence["input_snapshot_id"] == "snapshot"
    assert set(evidence["package_digests"]) == {
        "lookup-tables.json",
        "metrics.json",
        "review-report.md",
        "scored-events.jsonl",
        "manifest.json",
        "validation-artifact.json",
    }
    assert evidence["current_or_latest_pointer_exists"] is False
    assert evidence["current_or_latest_pointer_paths"] == []


@pytest.mark.parametrize("pointer_name", ["current.json", "latest", "latest.json"])
def test_retained_inspection_fails_closed_when_mutable_pointer_exists(
    contract: dict, tmp_path: Path, pointer_name: str
) -> None:
    artifact, lookup, scored = _artifact_fixture(contract)
    result = write_validation_artifact(tmp_path / "immutable-b07", artifact, lookup, scored)
    (Path(result["root"]) / pointer_name).write_text("{}", encoding="utf-8")

    with pytest.raises(BaselineValidationError) as exc_info:
        retained_inspection_evidence(result["root"])

    assert exc_info.value.reason_code == "B07_ARTIFACT_MUTABLE_POINTER_PRESENT"


def test_retained_inspection_preserves_digest_mismatch_reason(
    contract: dict, tmp_path: Path
) -> None:
    artifact, lookup, scored = _artifact_fixture(contract)
    result = write_validation_artifact(tmp_path / "immutable-b07", artifact, lookup, scored)
    (Path(result["root"]) / "metrics.json").write_text("{}", encoding="utf-8")

    with pytest.raises(BaselineValidationError) as exc_info:
        retained_inspection_evidence(result["root"])

    assert exc_info.value.reason_code == "B07_ARTIFACT_FILE_DIGEST_MISMATCH"


@pytest.mark.parametrize("name", ["current.json", "latest", "recommendation", "projection"])
def test_artifact_writer_rejects_pointer_production_and_recommendation_paths(
    contract: dict, tmp_path: Path, name: str
) -> None:
    artifact, lookup, scored = _artifact_fixture(contract)
    with pytest.raises(BaselineValidationError) as exc_info:
        write_validation_artifact(tmp_path / name, artifact, lookup, scored)
    assert exc_info.value.reason_code == "B07_ARTIFACT_PATH_PROHIBITED"


def test_no_endpoint_or_external_write_client_is_introduced() -> None:
    module_text = Path(b07_baseline.__file__).read_text(encoding="utf-8")
    runner_text = (REPOSITORY_ROOT / "tools" / "run_b07_baseline.py").read_text(
        encoding="utf-8"
    )
    prohibited_tokens = ("httpx", "requests.", "urlopen", "FastAPI", "Flask", "endpoint_route")
    assert all(token not in module_text for token in prohibited_tokens)
    assert all(token not in runner_text for token in prohibited_tokens)
