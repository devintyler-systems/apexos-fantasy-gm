"""Acceptance coverage for bounded nflverse raw-evidence capture."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier

import pytest

from engine.ingestion.nflverse_raw_evidence import (
    REQUIRED_COLUMNS,
    REQUIRED_REASON_CODES,
    HttpFetchResponse,
    NflverseAssetRequest,
    capture_nflverse_raw_evidence,
)
import engine.ingestion.nflverse_raw_evidence as raw_evidence
from tools import capture_nflverse_raw_evidence as capture_cli

FIXTURE_ROOT = Path("tests/fixtures/nflverse_raw_evidence")
SEASON = 2024
ASSET_NAME = f"play_by_play_{SEASON}.parquet"
ASSET_URL = (
    "https://github.com/nflverse/nflverse-data/releases/download/"
    f"pbp/{ASSET_NAME}"
)
LOCAL_FIXTURE_URL = f"http://127.0.0.1:8765/{ASSET_NAME}"
AS_OF = "2025-01-01T00:00:00Z"
EFFECTIVE = "2024-12-31T00:00:00Z"
FIXED_CLOCK = lambda: datetime(2025, 1, 1, tzinfo=UTC)


class FixtureTransport:
    def __init__(
        self,
        body: bytes,
        *,
        status_code: int = 200,
        effective_timestamp: str | None = EFFECTIVE,
        failure: Exception | None = None,
    ) -> None:
        self.body = body
        self.status_code = status_code
        self.effective_timestamp = effective_timestamp
        self.failure = failure
        self.seen_urls: list[str] = []

    def fetch(self, url: str) -> HttpFetchResponse:
        self.seen_urls.append(url)
        if self.failure is not None:
            raise self.failure
        return HttpFetchResponse(
            status_code=self.status_code,
            body=self.body,
            effective_timestamp=self.effective_timestamp,
        )


def _bytes(name: str) -> bytes:
    return (FIXTURE_ROOT / name).read_bytes()


def _request(
    body: bytes,
    **changes: object,
) -> NflverseAssetRequest:
    request = NflverseAssetRequest(
        season=SEASON,
        release_tag="pbp",
        asset_name=ASSET_NAME,
        asset_url=ASSET_URL,
        expected_sha256=hashlib.sha256(body).hexdigest(),
        expected_byte_count=len(body),
        as_of_timestamp=AS_OF,
        source_contract_version="nflverse-play-by-play-ingestion-contract-v0.2",
        parser_version="nflverse-raw-evidence-v0.1",
    )
    return replace(request, **changes)


def _capture(
    tmp_path: Path,
    body: bytes,
    *,
    request: NflverseAssetRequest | None = None,
    transport: FixtureTransport | None = None,
    fixture_mode: bool = False,
):
    transport = transport or FixtureTransport(body)
    result = capture_nflverse_raw_evidence(
        request or _request(body),
        tmp_path / "evidence",
        transport,
        clock=FIXED_CLOCK,
        fixture_mode=fixture_mode,
    )
    return result, transport


def _manifest(result) -> dict[str, object]:
    assert result.manifest_path is not None
    return json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))


def _assert_failed(result, reason_code: str, output_root: Path) -> None:
    assert result.status == "failed"
    assert result.degraded_mode is True
    assert reason_code in result.reason_codes
    assert result.known_limitations
    assert result.snapshot_id is None
    assert result.manifest_path is None
    assert not (output_root / "manifests").exists()


def test_happy_path_captures_one_immutable_historical_snapshot(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")

    result, transport = _capture(tmp_path, body)

    assert result.status == "success"
    assert result.degraded_mode is False
    assert transport.seen_urls == [ASSET_URL]
    assert result.raw_asset_path is not None
    assert Path(result.raw_asset_path).read_bytes() == body
    assert result.quarantine_path is not None
    assert Path(result.quarantine_path).read_bytes() == b""
    manifest = _manifest(result)
    assert manifest["freshness_status"] == "historical_snapshot"
    assert manifest["projection_authority"] == "none_raw_evidence_only"
    assert manifest["provider_projection_fields_used"] is False
    assert manifest["schema_validation"]["required_columns"] == list(REQUIRED_COLUMNS)
    assert manifest["identity_quarantine"]["canonical_mapping_created"] is False


def test_manifest_contains_complete_lineage_and_integrity(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    result, _ = _capture(tmp_path, body)

    manifest = _manifest(result)

    assert manifest["source_id"] == "nflverse_direct_github_release_assets"
    assert manifest["source_provider_or_url"] == "https://github.com/nflverse/nflverse-data/releases"
    assert manifest["release_tag"] == "pbp"
    assert manifest["asset_name"] == ASSET_NAME
    assert manifest["asset_url"] == ASSET_URL
    assert manifest["season"] == SEASON
    assert manifest["retrieval_timestamp"] == AS_OF
    assert manifest["effective_timestamp"] == EFFECTIVE
    assert manifest["as_of_timestamp"] == AS_OF
    assert manifest["raw_sha256"] == hashlib.sha256(body).hexdigest()
    assert manifest["raw_byte_count"] == len(body)
    assert manifest["expected_sha256"] == hashlib.sha256(body).hexdigest()
    assert manifest["expected_byte_count"] == len(body)
    assert manifest["parser_version"] == "nflverse-raw-evidence-v0.1"
    assert manifest["source_contract_version"] == "nflverse-play-by-play-ingestion-contract-v0.2"
    assert manifest["rights_or_terms_reference"] == "docs/data_source_connector_register.md"


@pytest.mark.parametrize(
    ("request_changes", "reason_code"),
    [
        ({"expected_sha256": "0" * 64}, "HASH_MISMATCH"),
        ({"expected_byte_count": 1}, "BYTE_COUNT_MISMATCH"),
    ],
)
def test_integrity_mismatch_never_promotes(
    tmp_path: Path,
    request_changes: dict[str, object],
    reason_code: str,
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"

    result, _ = _capture(
        tmp_path,
        body,
        request=_request(body, **request_changes),
    )

    _assert_failed(result, reason_code, root)


def test_malformed_parquet_fails_visibly(tmp_path: Path) -> None:
    body = _bytes("malformed-play_by_play_2024.parquet")
    root = tmp_path / "evidence"

    result, _ = _capture(tmp_path, body)

    _assert_failed(result, "MALFORMED_PARQUET", root)


def test_missing_required_schema_field_is_named(tmp_path: Path) -> None:
    body = _bytes("missing-schema-play_by_play_2024.parquet")
    root = tmp_path / "evidence"

    result, _ = _capture(tmp_path, body)

    _assert_failed(result, "REQUIRED_SCHEMA_FIELD_MISSING", root)
    assert "play_type" in result.known_limitations[0]


@pytest.mark.parametrize("timestamp", ["not-a-time", "2025-01-01T00:00:00", "2025-01-01T00:00:00-08:00"])
def test_invalid_as_of_timestamp_fails_before_transport(
    tmp_path: Path, timestamp: str
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    transport = FixtureTransport(body)

    result, transport = _capture(
        tmp_path,
        body,
        request=_request(body, as_of_timestamp=timestamp),
        transport=transport,
    )

    assert result.reason_codes == ("INVALID_TIMESTAMP",)
    assert result.degraded_mode is True
    assert transport.seen_urls == []


def test_effective_timestamp_after_as_of_fails_time_integrity(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    transport = FixtureTransport(body, effective_timestamp="2025-01-02T00:00:00Z")

    result, _ = _capture(tmp_path, body, transport=transport)

    assert result.reason_codes == ("TIME_INTEGRITY_FAILED",)
    assert result.degraded_mode is True


def test_missing_effective_timestamp_is_visible_historical_degradation(
    tmp_path: Path,
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    transport = FixtureTransport(body, effective_timestamp=None)

    result, _ = _capture(tmp_path, body, transport=transport)

    assert result.status == "success_degraded"
    assert result.reason_codes == ("SOURCE_FRESHNESS_UNKNOWN",)
    assert _manifest(result)["freshness_status"] == "historical_snapshot"


def test_null_and_blank_source_identities_are_quarantined_without_mapping(
    tmp_path: Path,
) -> None:
    body = _bytes("identity-null-play_by_play_2024.parquet")

    result, _ = _capture(tmp_path, body)

    assert result.status == "success_degraded"
    assert "CANONICAL_IDENTITY_UNRESOLVED" in result.reason_codes
    assert result.quarantined_identity_count == 3
    assert result.quarantine_path is not None
    records = [
        json.loads(line)
        for line in Path(result.quarantine_path).read_text(encoding="utf-8").splitlines()
    ]
    assert {record["source_entity_type"] for record in records} == {"game", "team"}
    assert all(record["reason_code"] == "CANONICAL_IDENTITY_UNRESOLVED" for record in records)
    manifest = _manifest(result)
    assert manifest["identity_quarantine"]["canonical_mapping_created"] is False


def test_snapshot_id_is_deterministic_and_idempotent_without_rewrite(
    tmp_path: Path,
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    first, _ = _capture(tmp_path, body)
    assert first.raw_asset_path is not None
    raw_path = Path(first.raw_asset_path)
    original_mtime = raw_path.stat().st_mtime_ns
    later_clock = lambda: datetime(2025, 2, 1, tzinfo=UTC)

    second = capture_nflverse_raw_evidence(
        _request(body),
        tmp_path / "evidence",
        FixtureTransport(body),
        clock=later_clock,
    )
    third, _ = _capture(tmp_path / "other", body)

    assert second.status == "success_idempotent"
    assert second.snapshot_id == first.snapshot_id == third.snapshot_id
    assert raw_path.stat().st_mtime_ns == original_mtime


def test_concurrent_identical_captures_converge_to_one_complete_snapshot(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    barrier = Barrier(2)

    class SynchronizedTransport(FixtureTransport):
        def fetch(self, url: str) -> HttpFetchResponse:
            barrier.wait(timeout=5)
            return super().fetch(url)

    def capture_once():
        return capture_nflverse_raw_evidence(
            _request(body),
            tmp_path / "evidence",
            SynchronizedTransport(body),
            clock=FIXED_CLOCK,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [future.result() for future in (executor.submit(capture_once), executor.submit(capture_once))]

    assert {result.status for result in results} <= {"success", "success_idempotent"}
    assert len({result.snapshot_id for result in results}) == 1
    raw_paths = {result.raw_asset_path for result in results}
    manifest_paths = {result.manifest_path for result in results}
    quarantine_paths = {result.quarantine_path for result in results}
    assert len(raw_paths) == len(manifest_paths) == len(quarantine_paths) == 1
    published_raw = Path(next(iter(raw_paths)))
    original_mtime = published_raw.stat().st_mtime_ns
    assert published_raw.read_bytes() == body
    assert _manifest(results[0])["raw_sha256"] == hashlib.sha256(body).hexdigest()
    with ThreadPoolExecutor(max_workers=2) as executor:
        repeated = [future.result() for future in (executor.submit(capture_once), executor.submit(capture_once))]
    assert {result.status for result in repeated} == {"success_idempotent"}
    assert published_raw.stat().st_mtime_ns == original_mtime


def test_partial_or_conflicting_final_snapshot_fails_closed_without_replacement(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    first, _ = _capture(tmp_path, body)
    assert first.raw_asset_path is not None
    assert first.manifest_path is not None
    raw_path = Path(first.raw_asset_path)
    manifest_path = Path(first.manifest_path)
    raw_path.write_bytes(b"conflicting-final-evidence")

    conflict, _ = _capture(tmp_path, body)

    assert conflict.reason_codes == ("SNAPSHOT_CONFLICT",)
    assert conflict.degraded_mode is True
    assert raw_path.read_bytes() == b"conflicting-final-evidence"
    manifest_path.unlink()
    partial, _ = _capture(tmp_path, body)
    assert partial.reason_codes == ("SNAPSHOT_CONFLICT",)
    assert partial.degraded_mode is True
    assert raw_path.read_bytes() == b"conflicting-final-evidence"


def test_mid_publication_failure_never_returns_success_or_deletes_final_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    real_publish = raw_evidence._publish_create_only
    calls = 0

    def fail_after_raw(temporary: Path, final: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("controlled quarantine publication failure")
        real_publish(temporary, final)

    monkeypatch.setattr(raw_evidence, "_publish_create_only", fail_after_raw)
    failed, _ = _capture(tmp_path, body)

    assert failed.reason_codes == ("FILESYSTEM_WRITE_FAILED",)
    assert failed.degraded_mode is True
    raw_root = tmp_path / "evidence" / "raw"
    assert next(raw_root.rglob(ASSET_NAME)).read_bytes() == body
    assert not list((tmp_path / "evidence" / "manifests").glob("*.json"))
    assert not list((tmp_path / "evidence").rglob(".capture-*.tmp"))


def test_final_snapshot_publication_has_no_os_link_dependency() -> None:
    source = Path("engine/ingestion/nflverse_raw_evidence.py").read_text(encoding="utf-8")
    assert "os.link" not in source


def test_inconsistent_existing_manifest_returns_snapshot_conflict(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    first, _ = _capture(tmp_path, body)
    manifest = _manifest(first)
    manifest["asset_url"] = "https://github.com/nflverse/nflverse-data/releases/download/pbp/other.parquet"
    assert first.manifest_path is not None
    Path(first.manifest_path).write_text(json.dumps(manifest), encoding="utf-8")

    second, _ = _capture(tmp_path, body)

    assert second.status == "failed"
    assert second.reason_codes == ("SNAPSHOT_CONFLICT",)
    assert second.degraded_mode is True


def _snapshot_paths(root: Path, body: bytes) -> tuple[Path, Path, Path]:
    snapshot_id = raw_evidence._snapshot_id(_request(body), hashlib.sha256(body).hexdigest())
    return (
        root / "raw" / snapshot_id / ASSET_NAME,
        root / "quarantine" / f"{snapshot_id}.jsonl",
        root / "manifests" / f"{snapshot_id}.json",
    )


def _lock_path(root: Path, body: bytes) -> Path:
    snapshot_id = raw_evidence._snapshot_id(_request(body), hashlib.sha256(body).hexdigest())
    return root / ".publication-locks" / f"{snapshot_id}.lock"


def _write_lock(
    path: Path,
    body: bytes,
    acquired_at: str,
    **overrides: object,
) -> bytes:
    owner = {
        "lock_protocol_version": "nflverse-raw-evidence-lock-v0.1",
        "snapshot_id": path.stem,
        "attempt_id": "test-owner",
        "acquired_at_timestamp": acquired_at,
        "process_id": 1,
        "host_identifier": "test-host",
        "raw_sha256": hashlib.sha256(body).hexdigest(),
        "asset_name": ASSET_NAME,
        "source_id": "nflverse_direct_github_release_assets",
    }
    owner.update(overrides)
    path.mkdir(parents=True)
    owner_path = path / "owner.json"
    owner_path.write_text(json.dumps(owner), encoding="utf-8")
    return owner_path.read_bytes()


def test_active_matching_lock_fails_closed_without_final_evidence(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    original_owner = _write_lock(lock_path, body, AS_OF)

    blocked, _ = _capture(tmp_path, body)

    assert blocked.reason_codes == ("SNAPSHOT_LOCK_UNAVAILABLE",)
    assert blocked.degraded_mode is True
    assert lock_path.joinpath("owner.json").read_bytes() == original_owner
    assert not any(path.exists() for path in _snapshot_paths(root, body))


def test_expired_matching_orphan_lock_is_reclaimed_into_complete_snapshot(
    tmp_path: Path,
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    _write_lock(lock_path, body, "2024-01-01T00:00:00Z")

    recovered, _ = _capture(tmp_path, body)

    assert recovered.status == "success"
    assert recovered.manifest_path is not None
    assert not lock_path.exists()
    raw_path, quarantine_path, manifest_path = _snapshot_paths(root, body)
    assert raw_path.read_bytes() == body
    assert quarantine_path.is_file()
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshot_id"] == recovered.snapshot_id


def test_expired_lock_with_complete_equivalent_snapshot_is_idempotent_and_preserved(
    tmp_path: Path,
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    first, _ = _capture(tmp_path, body)
    root = tmp_path / "evidence"
    raw_path, quarantine_path, manifest_path = _snapshot_paths(root, body)
    raw_before = raw_path.read_bytes()
    quarantine_before = quarantine_path.read_bytes()
    manifest_before = manifest_path.read_bytes()
    lock_path = _lock_path(root, body)
    owner_before = _write_lock(lock_path, body, "2024-01-01T00:00:00Z")

    result, _ = _capture(tmp_path, body)

    assert result.status == "success_idempotent"
    assert result.snapshot_id == first.snapshot_id
    assert raw_path.read_bytes() == raw_before
    assert quarantine_path.read_bytes() == quarantine_before
    assert manifest_path.read_bytes() == manifest_before
    assert lock_path.joinpath("owner.json").read_bytes() == owner_before


@pytest.mark.parametrize("partial_state", ["raw_only", "raw_quarantine", "manifest_only", "manifest_missing_payload"])
def test_expired_lock_with_partial_final_evidence_fails_closed(
    tmp_path: Path, partial_state: str
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    raw_path, quarantine_path, manifest_path = _snapshot_paths(root, body)
    if partial_state in {"raw_only", "raw_quarantine"}:
        raw_path.parent.mkdir(parents=True)
        raw_path.write_bytes(body)
    if partial_state == "raw_quarantine":
        quarantine_path.parent.mkdir(parents=True)
        quarantine_path.write_bytes(b"")
    if partial_state in {"manifest_only", "manifest_missing_payload"}:
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text("{}", encoding="utf-8")
    if partial_state == "manifest_missing_payload":
        raw_path.parent.mkdir(parents=True)
        raw_path.write_bytes(body)
    lock_path = _lock_path(root, body)
    owner_before = _write_lock(lock_path, body, "2024-01-01T00:00:00Z")
    final_before = {
        path: path.read_bytes() for path in (raw_path, quarantine_path, manifest_path) if path.exists()
    }

    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == ("SNAPSHOT_CONFLICT",)
    assert result.degraded_mode is True
    assert lock_path.joinpath("owner.json").read_bytes() == owner_before
    assert {path: path.read_bytes() for path in final_before} == final_before


@pytest.mark.parametrize("conflict", ["raw", "quarantine", "lineage"])
def test_expired_lock_with_conflicting_complete_evidence_fails_closed(
    tmp_path: Path, conflict: str
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    first, _ = _capture(tmp_path, body)
    root = tmp_path / "evidence"
    raw_path, quarantine_path, manifest_path = _snapshot_paths(root, body)
    if conflict == "raw":
        raw_path.write_bytes(b"conflicting-raw")
    elif conflict == "quarantine":
        quarantine_path.write_bytes(b'{"conflicting":true}\n')
    else:
        manifest = _manifest(first)
        manifest["source_contract_version"] = "conflicting-lineage"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    lock_path = _lock_path(root, body)
    owner_before = _write_lock(lock_path, body, "2024-01-01T00:00:00Z")
    final_before = {
        path: path.read_bytes() for path in (raw_path, quarantine_path, manifest_path)
    }

    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == ("SNAPSHOT_CONFLICT",)
    assert result.degraded_mode is True
    assert lock_path.joinpath("owner.json").read_bytes() == owner_before
    assert {path: path.read_bytes() for path in final_before} == final_before


@pytest.mark.parametrize("owner_state", ["invalid_json", "unreadable"])
def test_malformed_or_unreadable_owner_metadata_fails_closed(
    tmp_path: Path, owner_state: str
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    _write_lock(lock_path, body, "2024-01-01T00:00:00Z")
    owner_path = lock_path / "owner.json"
    if owner_state == "invalid_json":
        owner_path.write_bytes(b"not-json")
    else:
        owner_path.unlink()
        owner_path.mkdir()

    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == ("SNAPSHOT_LOCK_UNAVAILABLE",)
    assert result.degraded_mode is True
    assert owner_path.exists()
    assert not any(path.exists() for path in _snapshot_paths(root, body))


@pytest.mark.parametrize(
    ("field", "value", "reason_code"),
    [
        ("snapshot_id", "foreign-snapshot", "SNAPSHOT_LOCK_UNAVAILABLE"),
        ("asset_name", "foreign.parquet", "SNAPSHOT_CONFLICT"),
        ("source_id", "foreign-source", "SNAPSHOT_LOCK_UNAVAILABLE"),
        ("raw_sha256", "0" * 64, "SNAPSHOT_CONFLICT"),
    ],
)
def test_foreign_or_hash_mismatched_owner_metadata_fails_closed(
    tmp_path: Path, field: str, value: str, reason_code: str
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    owner_before = _write_lock(lock_path, body, "2024-01-01T00:00:00Z", **{field: value})

    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == (reason_code,)
    assert result.degraded_mode is True
    assert lock_path.joinpath("owner.json").read_bytes() == owner_before
    assert not any(path.exists() for path in _snapshot_paths(root, body))


@pytest.mark.parametrize("acquired_at", ["not-a-time", "2025-01-02T00:00:00Z"])
def test_invalid_or_future_dated_owner_timestamp_fails_closed(
    tmp_path: Path, acquired_at: str
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    owner_before = _write_lock(lock_path, body, acquired_at)

    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == ("SNAPSHOT_LOCK_UNAVAILABLE",)
    assert result.degraded_mode is True
    assert lock_path.joinpath("owner.json").read_bytes() == owner_before
    assert not any(path.exists() for path in _snapshot_paths(root, body))


def test_owner_replacement_during_reclaim_preserves_replacement_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    _write_lock(lock_path, body, "2024-01-01T00:00:00Z")

    def replace_owner(path: Path) -> None:
        owner_path = path / "owner.json"
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        owner["attempt_id"] = "replacement-owner"
        owner["acquired_at_timestamp"] = AS_OF
        owner_path.unlink()
        owner_path.write_text(json.dumps(owner), encoding="utf-8")

    monkeypatch.setattr(raw_evidence, "_before_stale_lock_reclaim", replace_owner)
    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == ("SNAPSHOT_LOCK_UNAVAILABLE",)
    assert json.loads((lock_path / "owner.json").read_text(encoding="utf-8"))["attempt_id"] == "replacement-owner"
    assert not any(path.exists() for path in _snapshot_paths(root, body))


def test_owner_replacement_during_release_is_not_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    root = tmp_path / "evidence"
    lock_path = _lock_path(root, body)
    real_publish = raw_evidence._publish_snapshot_under_lock

    def publish_then_replace(**kwargs: object) -> None:
        real_publish(**kwargs)
        owner_path = lock_path / "owner.json"
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        owner["attempt_id"] = "replacement-owner"
        owner_path.write_text(json.dumps(owner), encoding="utf-8")

    monkeypatch.setattr(raw_evidence, "_publish_snapshot_under_lock", publish_then_replace)
    result, _ = _capture(tmp_path, body)

    assert result.status == "success"
    assert json.loads((lock_path / "owner.json").read_text(encoding="utf-8"))["attempt_id"] == "replacement-owner"
    assert all(path.is_file() for path in _snapshot_paths(root, body))


@pytest.mark.parametrize(
    ("changes", "reason_code"),
    [
        ({"season": 2015, "asset_name": "play_by_play_2015.parquet"}, "UNSUPPORTED_SEASON"),
        ({"season": 2026, "asset_name": "play_by_play_2026.parquet"}, "UNSUPPORTED_SEASON"),
        ({"release_tag": "latest"}, "INVALID_ASSET_IDENTITY"),
        ({"asset_name": "play_by_play_2024.csv"}, "INVALID_ASSET_IDENTITY"),
        ({"asset_url": "https://example.invalid/play_by_play_2024.parquet"}, "INVALID_ASSET_IDENTITY"),
        (
            {
                "asset_url": (
                    "https://github.com/another/project/releases/download/"
                    f"pbp/{ASSET_NAME}"
                )
            },
            "INVALID_ASSET_IDENTITY",
        ),
        (
            {
                "asset_url": (
                    "https://github.com/nflverse/nflverse-data/releases/download/"
                    "pbp/other.parquet"
                )
            },
            "INVALID_ASSET_IDENTITY",
        ),
    ],
)
def test_request_boundary_rejects_unsupported_or_invalid_identity(
    tmp_path: Path,
    changes: dict[str, object],
    reason_code: str,
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    transport = FixtureTransport(body)

    result, transport = _capture(
        tmp_path,
        body,
        request=_request(body, **changes),
        transport=transport,
    )

    assert result.reason_codes == (reason_code,)
    assert result.degraded_mode is True
    assert transport.seen_urls == []


@pytest.mark.parametrize(
    "transport",
    [
        FixtureTransport(b"payload", status_code=503),
        FixtureTransport(b"", status_code=200),
        FixtureTransport(b"payload", failure=OSError("fixture transport failure")),
    ],
)
def test_retrieval_failures_are_structured_and_degraded(
    tmp_path: Path, transport: FixtureTransport
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")

    result, _ = _capture(tmp_path, body, transport=transport)

    assert result.degraded_mode is True
    assert result.reason_codes[0] in {"HTTP_RETRIEVAL_FAILED", "SOURCE_SNAPSHOT_MISSING"}
    assert result.known_limitations


def test_fixture_mode_is_visibly_not_production(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    request = _request(
        body,
        asset_url=LOCAL_FIXTURE_URL,
        expected_sha256=None,
    )

    result, _ = _capture(tmp_path, body, request=request, fixture_mode=True)

    assert result.status == "success_degraded"
    assert "FIXTURE_MODE_NOT_PRODUCTION" in result.reason_codes
    assert result.degraded_mode is True


def test_fixture_mode_rejects_a_production_host(tmp_path: Path) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")

    result, transport = _capture(tmp_path, body, fixture_mode=True)

    _assert_failed(result, "INVALID_ASSET_IDENTITY", tmp_path / "evidence")
    assert transport.seen_urls == []


def test_cli_requires_fixture_mode_for_unsigned_capture(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        capture_cli.main(
            [
                "--season",
                str(SEASON),
                "--asset-url",
                LOCAL_FIXTURE_URL,
                "--as-of-timestamp",
                AS_OF,
                "--output-root",
                str(tmp_path / "evidence"),
                "--allow-unsigned-for-local-fixture",
            ]
        )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert payload["reason_codes"] == ["INVALID_ASSET_IDENTITY"]
    assert payload["degraded_mode"] is True


def test_cli_fixture_capture_prints_one_json_result_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = _bytes("valid-play_by_play_2024.parquet")
    transport = FixtureTransport(body)
    monkeypatch.setattr(capture_cli, "HttpxHttpTransport", lambda: transport)

    exit_code = capture_cli.main(
        [
            "--season",
            str(SEASON),
            "--asset-url",
            LOCAL_FIXTURE_URL,
            "--as-of-timestamp",
            AS_OF,
            "--output-root",
            str(tmp_path / "evidence"),
            "--fixture-mode",
            "--allow-unsigned-for-local-fixture",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert payload["status"] == "success_degraded"
    assert payload["reason_codes"] == ["FIXTURE_MODE_NOT_PRODUCTION"]
    assert transport.seen_urls == [LOCAL_FIXTURE_URL]


def test_filesystem_failure_returns_explicit_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import engine.ingestion.nflverse_raw_evidence as module

    body = _bytes("valid-play_by_play_2024.parquet")

    def fail_write(_parent: Path, _payload: bytes) -> Path:
        raise OSError("fixture filesystem failure")

    monkeypatch.setattr(module, "_write_temp", fail_write)
    result, _ = _capture(tmp_path, body)

    assert result.reason_codes == ("FILESYSTEM_WRITE_FAILED",)
    assert result.degraded_mode is True


def test_required_reason_code_vocabulary_is_complete() -> None:
    assert REQUIRED_REASON_CODES == {
        "UNSUPPORTED_SEASON",
        "INVALID_ASSET_IDENTITY",
        "HTTP_RETRIEVAL_FAILED",
        "SOURCE_SNAPSHOT_MISSING",
        "HASH_MISMATCH",
        "BYTE_COUNT_MISMATCH",
        "MALFORMED_PARQUET",
        "REQUIRED_SCHEMA_FIELD_MISSING",
        "INVALID_TIMESTAMP",
        "TIME_INTEGRITY_FAILED",
        "SNAPSHOT_CONFLICT",
        "FILESYSTEM_WRITE_FAILED",
        "CANONICAL_IDENTITY_UNRESOLVED",
        "SOURCE_FRESHNESS_UNKNOWN",
        "PROVIDER_CONTAMINATION_DETECTED",
        "FIXTURE_MODE_NOT_PRODUCTION",
        "SNAPSHOT_LOCK_UNAVAILABLE",
    }
    runbook = Path(
        "contracts/ingestion/nflverse-raw-evidence-capture-runbook-v0.1.md"
    ).read_text(encoding="utf-8")
    assert "SNAPSHOT_LOCK_UNAVAILABLE" in runbook
    assert "cannot be safely acquired or reclaimed" in runbook


def test_implementation_has_no_prohibited_access_or_decision_logic() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            Path("engine/ingestion/nflverse_raw_evidence.py"),
            Path("tools/capture_nflverse_raw_evidence.py"),
        )
    )
    prohibited = (
        "nfl_" + "data_py",
        "Fan" + "trax",
        "provider_" + "projected_score",
        "apexos_" + "projected_score",
        " A" + "DP",
        "ranking" + "_engine",
        "recommendation" + "_engine",
        "scoring" + "_engine",
    )
    for term in prohibited:
        assert term not in source


def test_fixture_case_register_contains_no_player_or_projection_values() -> None:
    cases = json.loads((FIXTURE_ROOT / "cases.json").read_text(encoding="utf-8"))
    assert cases["fixture_scope"] == "synthetic raw evidence only"
    assert cases["contains_player_specific_values"] is False
    assert cases["contains_projection_outputs"] is False
