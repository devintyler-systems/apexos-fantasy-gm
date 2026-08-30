from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import socket
from threading import Barrier
from typing import Any

import httpx
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from engine.ingestion.active_use import scan_prohibited_active_use
from engine.ingestion.nflverse_pbp import (
    DISCOVERY_URL,
    NO_PLAY_NORMALIZATION_VERSION,
    PARSER_VERSION,
    REQUIRED_COLUMNS,
    ingest_nflverse_pbp_season,
)


SEASON = 2023
EXPECTED_REG_GAMES = 272
ASSET_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/synthetic.parquet"
NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _forbid_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("B-06 acceptance tests must not open a network socket")

    monkeypatch.setattr(socket, "create_connection", fail)
    monkeypatch.setattr(socket.socket, "connect", fail)


def _valid_table(
    *,
    reg_games: int = EXPECTED_REG_GAMES,
    include_post: bool = True,
    marker: str = "original-extra-column",
) -> pa.Table:
    season_types = ["REG"] * reg_games
    game_ids = [f"2023_REG_{index:03d}" for index in range(reg_games)]
    if include_post:
        season_types.append("POST")
        game_ids.append("2023_POST_001")
    rows = len(game_ids)
    return pa.table(
        {
            "season": pa.array([SEASON] * rows, type=pa.int32()),
            "season_type": pa.array(season_types, type=pa.string()),
            "game_id": pa.array(game_ids, type=pa.string()),
            "yardline_100": pa.array([index % 101 for index in range(rows)], type=pa.float64()),
            "touchdown": pa.array([index % 2 for index in range(rows)], type=pa.int8()),
            "rush_attempt": pa.array([(index + 1) % 2 for index in range(rows)], type=pa.int8()),
            "pass_attempt": pa.array([index % 2 for index in range(rows)], type=pa.int8()),
            "play_type": pa.array(["pass"] * rows, type=pa.string()),
            "provider_extra_column": pa.array([marker] * rows, type=pa.string()),
        }
    )


def _replace(table: pa.Table, name: str, values: list[Any], arrow_type: pa.DataType) -> pa.Table:
    index = table.schema.get_field_index(name)
    return table.set_column(index, name, pa.array(values, type=arrow_type))


def _parquet_bytes(table: pa.Table) -> bytes:
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    return sink.getvalue().to_pybytes()


def _asset(payload: bytes, *, url: str = ASSET_URL, **overrides: Any) -> dict[str, Any]:
    value = {
        "id": 9001,
        "name": f"play_by_play_{SEASON}.parquet",
        "state": "uploaded",
        "size": len(payload),
        "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "browser_download_url": url,
        "updated_at": "2026-02-01T00:00:00Z",
    }
    value.update(overrides)
    return value


def _release(payload: bytes, *, asset: dict[str, Any] | None = None, **overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": 58152862,
        "tag_name": "pbp",
        "published_at": "2026-01-01T00:00:00Z",
        "assets": [_asset(payload) if asset is None else asset],
    }
    value.update(overrides)
    return value


def _mock_client(
    payload: bytes,
    *,
    release: dict[str, Any] | None = None,
    discovery_status: int = 200,
    asset_status: int = 200,
    asset_url: str = ASSET_URL,
    asset_headers: dict[str, str] | None = None,
    barrier: Barrier | None = None,
) -> tuple[httpx.Client, list[str]]:
    seen: list[str] = []
    metadata = release if release is not None else _release(payload, asset=_asset(payload, url=asset_url))

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        seen.append(url)
        if url == DISCOVERY_URL:
            return httpx.Response(discovery_status, request=request, json=metadata)
        if url == asset_url:
            if barrier is not None:
                barrier.wait(timeout=5)
            return httpx.Response(
                asset_status,
                request=request,
                content=payload,
                headers=asset_headers,
            )
        raise AssertionError(f"Unexpected mocked URL: {url}")

    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False), seen


def _ingest(
    root: Path,
    payload: bytes,
    *,
    release: dict[str, Any] | None = None,
    discovery_status: int = 200,
    asset_status: int = 200,
    asset_url: str = ASSET_URL,
    asset_headers: dict[str, str] | None = None,
    barrier: Barrier | None = None,
):
    client, seen = _mock_client(
        payload,
        release=release,
        discovery_status=discovery_status,
        asset_status=asset_status,
        asset_url=asset_url,
        asset_headers=asset_headers,
        barrier=barrier,
    )
    try:
        result = ingest_nflverse_pbp_season(
            SEASON,
            root,
            client=client,
            clock=lambda: NOW,
        )
    finally:
        client.close()
    return result, seen


def _season_root(root: Path) -> Path:
    return root / f"season={SEASON}"


def _current(root: Path) -> dict[str, Any]:
    return json.loads((_season_root(root) / "current.json").read_text(encoding="utf-8"))


def _assert_failed_without_promotion(root: Path, result: Any) -> None:
    assert result.status == "failed"
    assert result.revision_sha256 is None
    assert not (_season_root(root) / "current.json").exists()
    assert not (_season_root(root) / "revisions").exists()
    assert len(list((_season_root(root) / "events").glob("failed-attempt-*.json"))) == 1


@pytest.mark.parametrize("missing", REQUIRED_COLUMNS)
def test_ac01_each_required_column_is_enforced(tmp_path: Path, missing: str) -> None:
    table = _valid_table().drop([missing])
    root = tmp_path / "pbp"

    result, _ = _ingest(root, _parquet_bytes(table))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class == "missing_required_column"


def test_ac01_success_preserves_exact_bytes_all_rows_and_extra_columns(tmp_path: Path) -> None:
    table = _valid_table()
    payload = _parquet_bytes(table)
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    release = _release(payload, asset=_asset(payload, digest=digest))
    root = tmp_path / "pbp"

    result, seen = _ingest(root, payload, release=release)

    assert result.status == "success_new_revision"
    assert seen == [DISCOVERY_URL, ASSET_URL]
    assert result.manifest_path is not None
    retained = result.manifest_path.with_name("pbp.parquet")
    assert retained.read_bytes() == payload
    retained_table = pq.ParquetFile(retained).read()
    assert retained_table.column_names == table.column_names
    assert retained_table.num_rows == table.num_rows
    assert retained_table["provider_extra_column"].to_pylist()[0] == "original-extra-column"
    assert "POST" in retained_table["season_type"].to_pylist()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_asset_digest_reported"] == digest
    assert manifest["reported_digest_sha256"] == digest.removeprefix("sha256:")
    assert manifest["computed_digest_sha256"] == digest.removeprefix("sha256:")
    assert manifest["digest_match"] is True
    assert manifest["game_counts_by_season_type"] == {"POST": 1, "REG": 272}
    assert manifest["regular_season_game_count_valid"] is True
    assert manifest["regular_season_game_count_expected"] == 272
    assert manifest["regular_season_game_count_observed"] == 272
    assert manifest["parser_version"] == PARSER_VERSION
    assert NO_PLAY_NORMALIZATION_VERSION in manifest["parser_version"]
    assert manifest["no_play_normalization_version"] == NO_PLAY_NORMALIZATION_VERSION
    assert manifest["logical_no_play_counts"] == {
        "false": table.num_rows,
        "true": 0,
        "unknown": 0,
    }
    assert manifest["unknown_row_count"] == 0
    assert manifest["promotion_result"] == "pass"
    assert manifest["row_count"] == table.num_rows
    assert manifest["required_raw_columns"] == list(REQUIRED_COLUMNS)
    assert any(field["name"] == "play_type" for field in manifest["raw_schema"])


@pytest.mark.parametrize("column", ["season", "season_type", "game_id"])
def test_ac02_nonnullable_columns_reject_nulls(tmp_path: Path, column: str) -> None:
    table = _valid_table()
    values = table[column].to_pylist()
    values[0] = None
    table = _replace(table, column, values, table.schema.field(column).type)
    root = tmp_path / "pbp"

    result, _ = _ingest(root, _parquet_bytes(table))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class == "column_nullability"


def test_ac02_nullable_columns_accept_nulls(tmp_path: Path) -> None:
    table = _valid_table()
    for column in ("yardline_100", "touchdown", "rush_attempt", "pass_attempt"):
        values = table[column].to_pylist()
        values[0] = None
        table = _replace(table, column, values, table.schema.field(column).type)

    result, _ = _ingest(tmp_path / "pbp", _parquet_bytes(table))

    assert result.status == "success_new_revision"


def test_ac03_dictionary_encoded_strings_are_accepted(tmp_path: Path) -> None:
    table = _valid_table()
    dictionary_type = pa.dictionary(pa.int8(), pa.string())
    for column in ("season_type", "game_id", "play_type"):
        table = _replace(table, column, table[column].to_pylist(), dictionary_type)

    result, _ = _ingest(tmp_path / "pbp", _parquet_bytes(table))

    assert result.status == "success_new_revision"


def _invalid_table(case: str) -> pa.Table:
    table = _valid_table()
    rows = table.num_rows
    if case == "season_float":
        return _replace(table, "season", [float(SEASON)] * rows, pa.float64())
    if case == "season_wrong":
        return _replace(table, "season", [2022] * rows, pa.int32())
    if case == "season_multiple":
        values = [SEASON] * rows
        values[0] = 2022
        return _replace(table, "season", values, pa.int32())
    if case == "season_type_integer":
        return _replace(table, "season_type", [1] * rows, pa.int8())
    if case == "season_type_blank":
        values = table["season_type"].to_pylist()
        values[0] = " "
        return _replace(table, "season_type", values, pa.string())
    if case == "season_type_unknown":
        values = table["season_type"].to_pylist()
        values[0] = "PRE"
        return _replace(table, "season_type", values, pa.string())
    if case == "game_id_integer":
        return _replace(table, "game_id", list(range(rows)), pa.int32())
    if case == "game_id_blank":
        values = table["game_id"].to_pylist()
        values[0] = ""
        return _replace(table, "game_id", values, pa.string())
    if case == "play_type_integer":
        return _replace(table, "play_type", [1] * rows, pa.int8())
    if case == "play_type_unknown":
        values = table["play_type"].to_pylist()
        values[0] = "provider_new_value"
        return _replace(table, "play_type", values, pa.string())
    if case == "yardline_string":
        return _replace(table, "yardline_100", ["50"] * rows, pa.string())
    if case in {"yardline_nan", "yardline_infinite", "yardline_low", "yardline_high"}:
        values = table["yardline_100"].to_pylist()
        values[0] = {
            "yardline_nan": float("nan"),
            "yardline_infinite": float("inf"),
            "yardline_low": -1.0,
            "yardline_high": 101.0,
        }[case]
        return _replace(table, "yardline_100", values, pa.float64())
    column, invalid, arrow_type = {
        "touchdown_string": ("touchdown", "1", pa.string()),
        "rush_attempt_two": ("rush_attempt", 2, pa.int8()),
        "pass_attempt_nan": ("pass_attempt", float("nan"), pa.float64()),
    }[case]
    values = table[column].to_pylist()
    values[0] = invalid
    if pa.types.is_string(arrow_type):
        values = [str(value) for value in values]
    return _replace(table, column, values, arrow_type)


@pytest.mark.parametrize(
    "case",
    [
        "season_float",
        "season_wrong",
        "season_multiple",
        "season_type_integer",
        "season_type_blank",
        "season_type_unknown",
        "game_id_integer",
        "game_id_blank",
        "play_type_integer",
        "play_type_unknown",
        "yardline_string",
        "yardline_nan",
        "yardline_infinite",
        "yardline_low",
        "yardline_high",
        "touchdown_string",
        "rush_attempt_two",
        "pass_attempt_nan",
    ],
)
def test_ac03_type_and_domain_rules_fail_closed(tmp_path: Path, case: str) -> None:
    root = tmp_path / "pbp"

    result, _ = _ingest(root, _parquet_bytes(_invalid_table(case)))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class in {
        "column_type",
        "column_domain",
        "season_mismatch",
        "season_type_domain",
        "game_id_domain",
        "logical_no_play_unknown",
    }


def test_no_play_null_without_opportunity_is_counted_true(tmp_path: Path) -> None:
    table = _valid_table()
    play_types = table["play_type"].to_pylist()
    pass_attempts = table["pass_attempt"].to_pylist()
    rush_attempts = table["rush_attempt"].to_pylist()
    play_types[0] = None
    pass_attempts[0] = 0
    rush_attempts[0] = 0
    table = _replace(table, "play_type", play_types, pa.string())
    table = _replace(table, "pass_attempt", pass_attempts, pa.int8())
    table = _replace(table, "rush_attempt", rush_attempts, pa.int8())

    result, _ = _ingest(tmp_path / "pbp", _parquet_bytes(table))

    assert result.status == "success_new_revision"
    assert result.manifest_path is not None
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["logical_no_play_counts"] == {
        "false": table.num_rows - 1,
        "true": 1,
        "unknown": 0,
    }


@pytest.mark.parametrize(("pass_attempt", "rush_attempt"), [(1, 0), (0, 1)])
def test_no_play_null_with_opportunity_blocks_promotion(
    tmp_path: Path, pass_attempt: int, rush_attempt: int
) -> None:
    table = _valid_table()
    play_types = table["play_type"].to_pylist()
    pass_attempts = table["pass_attempt"].to_pylist()
    rush_attempts = table["rush_attempt"].to_pylist()
    play_types[0] = None
    pass_attempts[0] = pass_attempt
    rush_attempts[0] = rush_attempt
    table = _replace(table, "play_type", play_types, pa.string())
    table = _replace(table, "pass_attempt", pass_attempts, pa.int8())
    table = _replace(table, "rush_attempt", rush_attempts, pa.int8())
    root = tmp_path / "pbp"

    result, _ = _ingest(root, _parquet_bytes(table))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class == "logical_no_play_unknown"
    assert "1 unknown row(s)" in (result.failure_detail or "")


@pytest.mark.parametrize("arrow_type", [pa.bool_(), pa.int8(), pa.float64()])
def test_ac03_binary_fields_accept_provisional_encodings(
    tmp_path: Path, arrow_type: pa.DataType
) -> None:
    table = _valid_table()
    for column in ("touchdown", "rush_attempt", "pass_attempt"):
        values = [index % 2 for index in range(table.num_rows)]
        if pa.types.is_boolean(arrow_type):
            values = [bool(value) for value in values]
        table = _replace(table, column, values, arrow_type)

    result, _ = _ingest(tmp_path / "pbp", _parquet_bytes(table))

    assert result.status == "success_new_revision"


def _discovery_case(case: str, payload: bytes) -> tuple[dict[str, Any], int, dict[str, str] | None]:
    asset = _asset(payload)
    if case == "zero_match":
        return _release(payload, assets=[]), 200, None
    if case == "multiple_match":
        return _release(payload, assets=[asset, dict(asset, id=9002)]), 200, None
    if case == "wrong_state":
        return _release(payload, asset=dict(asset, state="new")), 200, None
    if case == "wrong_extension":
        return _release(payload, asset=dict(asset, name=f"play_by_play_{SEASON}.csv")), 200, None
    if case == "missing_release_id":
        release = _release(payload)
        release.pop("id")
        return release, 200, None
    if case == "missing_asset_url":
        asset.pop("browser_download_url")
        return _release(payload, asset=asset), 200, None
    if case == "non_2xx":
        return _release(payload), 503, None
    if case == "redirect_rejected":
        return _release(payload), 200, {"location": "https://example.invalid/payload"}
    raise AssertionError(case)


@pytest.mark.parametrize(
    "case",
    [
        "zero_match",
        "multiple_match",
        "wrong_state",
        "wrong_extension",
        "missing_release_id",
        "missing_asset_url",
        "non_2xx",
        "redirect_rejected",
    ],
)
def test_ac07_discovery_and_redirect_failures_do_not_promote(
    tmp_path: Path, case: str
) -> None:
    payload = _parquet_bytes(_valid_table())
    release, discovery_status, asset_headers = _discovery_case(case, payload)
    root = tmp_path / "pbp"
    asset_status = 302 if case == "redirect_rejected" else 200

    result, _ = _ingest(
        root,
        payload,
        release=release,
        discovery_status=discovery_status,
        asset_status=asset_status,
        asset_headers=asset_headers,
    )

    _assert_failed_without_promotion(root, result)


def test_ac07_uses_exact_returned_browser_download_url(tmp_path: Path) -> None:
    payload = _parquet_bytes(_valid_table())
    opaque_url = "https://github.com/synthetic/releases/download/token-91/evidence.parquet"
    release = _release(payload, asset=_asset(payload, url=opaque_url))

    result, seen = _ingest(tmp_path / "pbp", payload, release=release, asset_url=opaque_url)

    assert result.status == "success_new_revision"
    assert seen == [DISCOVERY_URL, opaque_url]


def test_ac07_download_non_2xx_fails_without_promotion(tmp_path: Path) -> None:
    payload = _parquet_bytes(_valid_table())
    root = tmp_path / "pbp"

    result, seen = _ingest(root, payload, asset_status=503)

    _assert_failed_without_promotion(root, result)
    assert seen == [DISCOVERY_URL, ASSET_URL]
    assert result.failure_class == "http_status"


@pytest.mark.parametrize("case", ["reported_size", "provider_digest"])
def test_ac07_download_integrity_failures_do_not_promote(tmp_path: Path, case: str) -> None:
    payload = _parquet_bytes(_valid_table())
    asset = _asset(payload)
    if case == "reported_size":
        asset["size"] = len(payload) + 1
    else:
        asset["digest"] = "sha256:" + ("0" * 64)
    root = tmp_path / "pbp"

    result, _ = _ingest(root, payload, release=_release(payload, asset=asset))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class in {"download_size", "digest_mismatch"}


def test_promotion_window_requires_provider_reported_digest(tmp_path: Path) -> None:
    payload = _parquet_bytes(_valid_table())
    asset = _asset(payload, digest=None)
    root = tmp_path / "pbp"

    result, seen = _ingest(root, payload, release=_release(payload, asset=asset))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class == "provider_digest_missing"
    assert seen == [DISCOVERY_URL]


def test_ac08_corrupt_parquet_fails_without_promotion(tmp_path: Path) -> None:
    root = tmp_path / "pbp"

    result, _ = _ingest(root, b"synthetic-corrupt-parquet")

    _assert_failed_without_promotion(root, result)
    assert result.failure_class == "invalid_parquet"


def test_ac09_regular_season_game_count_mismatch_preserves_evidence_state(
    tmp_path: Path,
) -> None:
    root = tmp_path / "pbp"

    result, _ = _ingest(root, _parquet_bytes(_valid_table(reg_games=271)))

    _assert_failed_without_promotion(root, result)
    assert result.failure_class == "game_count_mismatch"


def test_ac10_same_hash_concurrency_creates_one_revision_and_distinct_events(
    tmp_path: Path,
) -> None:
    payload = _parquet_bytes(_valid_table())
    root = tmp_path / "pbp"
    barrier = Barrier(2)

    def run() -> Any:
        result, _ = _ingest(root, payload, barrier=barrier)
        return result

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _index: run(), range(2)))

    assert sorted(result.status for result in results) == [
        "success_existing_revision",
        "success_new_revision",
    ]
    revision_dirs = list((_season_root(root) / "revisions").glob("sha256=*"))
    assert len(revision_dirs) == 1
    assert len(list((_season_root(root) / "events").glob("retrieval-*.json"))) == 2
    revision_claims = list((root / "claims" / "revision").rglob("claim-*.json"))
    pointer_claims = list((root / "claims" / "pointer").rglob("claim-*.json"))
    assert len(revision_claims) == 1
    assert len(pointer_claims) == 2


def test_ac11_different_byte_concurrency_preserves_both_and_orders_pointer(
    tmp_path: Path,
) -> None:
    old_payload = _parquet_bytes(_valid_table(marker="old"))
    new_payload = _parquet_bytes(_valid_table(marker="new"))
    old_url = "https://github.com/synthetic/old.parquet"
    new_url = "https://github.com/synthetic/new.parquet"
    old_release = _release(
        old_payload,
        asset=_asset(old_payload, url=old_url, updated_at="2026-01-01T00:00:00Z"),
    )
    new_release = _release(
        new_payload,
        asset=_asset(new_payload, url=new_url, updated_at="2026-02-01T00:00:00Z"),
    )
    root = tmp_path / "pbp"
    barrier = Barrier(2)

    def run(payload: bytes, release: dict[str, Any], url: str) -> Any:
        result, _ = _ingest(root, payload, release=release, asset_url=url, barrier=barrier)
        return result

    with ThreadPoolExecutor(max_workers=2) as executor:
        old_future = executor.submit(run, old_payload, old_release, old_url)
        new_future = executor.submit(run, new_payload, new_release, new_url)
        results = [old_future.result(), new_future.result()]

    assert {result.status for result in results} == {"success_new_revision"}
    assert len(list((_season_root(root) / "revisions").glob("sha256=*"))) == 2
    assert _current(root)["revision_sha256"] == hashlib.sha256(new_payload).hexdigest()
    assert not list(root.rglob(".lock"))


def test_ac12_evidence_is_create_only_and_replace_targets_only_current(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import engine.ingestion.nflverse_pbp as module

    payload = _parquet_bytes(_valid_table())
    root = tmp_path / "pbp"
    replace_destinations: list[Path] = []
    real_replace = module.os.replace

    def recording_replace(source: str | Path, destination: str | Path) -> None:
        replace_destinations.append(Path(destination))
        real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", recording_replace)
    first, _ = _ingest(root, payload)
    assert first.manifest_path is not None
    manifest_before = first.manifest_path.read_bytes()
    payload_before = first.manifest_path.with_name("pbp.parquet").read_bytes()
    current_before = (_season_root(root) / "current.json").read_bytes()

    second, _ = _ingest(root, payload)

    assert second.status == "success_existing_revision"
    assert first.manifest_path.read_bytes() == manifest_before
    assert first.manifest_path.with_name("pbp.parquet").read_bytes() == payload_before
    assert (_season_root(root) / "current.json").read_bytes() == current_before
    assert replace_destinations
    assert all(path.name == "current.json" for path in replace_destinations)


def test_ac12_invalid_existing_manifest_is_never_repaired_or_overwritten(tmp_path: Path) -> None:
    payload = _parquet_bytes(_valid_table())
    root = tmp_path / "pbp"
    first, _ = _ingest(root, payload)
    assert first.manifest_path is not None
    current_path = _season_root(root) / "current.json"
    current_before = current_path.read_bytes()
    manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
    manifest.pop("parser_version")
    first.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    corrupted_manifest = first.manifest_path.read_bytes()

    second, _ = _ingest(root, payload)

    assert second.status == "failed"
    assert second.failure_class == "evidence_collision"
    assert first.manifest_path.read_bytes() == corrupted_manifest
    assert current_path.read_bytes() == current_before


def test_ac13_lower_ordered_revision_and_invalid_candidate_leave_pointer_byte_identical(
    tmp_path: Path,
) -> None:
    newer = _parquet_bytes(_valid_table(marker="newer"))
    older = _parquet_bytes(_valid_table(marker="older"))
    root = tmp_path / "pbp"
    newer_release = _release(
        newer,
        asset=_asset(newer, updated_at="2026-03-01T00:00:00Z"),
    )
    first, _ = _ingest(root, newer, release=newer_release)
    assert first.status == "success_new_revision"
    current_path = _season_root(root) / "current.json"
    current_before = current_path.read_bytes()
    older_release = _release(
        older,
        asset=_asset(older, updated_at="2026-01-01T00:00:00Z"),
    )

    second, _ = _ingest(root, older, release=older_release)
    after_older = current_path.read_bytes()
    failed, _ = _ingest(root, b"invalid-but-mocked")

    assert second.status == "success_new_revision"
    assert after_older == current_before
    assert failed.status == "cached_valid_after_failure"
    assert current_path.read_bytes() == current_before
    events = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (_season_root(root) / "events").glob("retrieval-*.json")
    ]
    assert any(event["pointer_published"] is False for event in events)


def test_ac14_failed_refresh_returns_exact_stale_cached_outcome(tmp_path: Path) -> None:
    payload = _parquet_bytes(_valid_table())
    root = tmp_path / "pbp"
    success, _ = _ingest(root, payload)
    current_path = _season_root(root) / "current.json"
    current_before = current_path.read_bytes()

    cached, _ = _ingest(root, payload, discovery_status=503)

    assert cached.status == "cached_valid_after_failure"
    assert cached.status != "success_existing_revision"
    assert cached.revision_sha256 == success.revision_sha256
    assert cached.manifest_path == success.manifest_path
    assert cached.freshness == "stale"
    assert cached.stale_banner_required is True
    assert cached.failure_class == "http_status"
    assert current_path.read_bytes() == current_before
    failed_event = next((_season_root(root) / "events").glob("failed-attempt-*.json"))
    evidence = json.loads(failed_event.read_text(encoding="utf-8"))
    assert evidence["prior_valid_revision_sha256"] == success.revision_sha256


def test_ac15_active_use_scan_rejects_use_and_permits_explicit_negative_evidence(
    tmp_path: Path,
) -> None:
    term = "nfl_" + "data_py"
    root = tmp_path / "scan"
    (root / "engine").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "tests").mkdir()
    (root / "engine" / "import.py").write_text(f"import {term}\n", encoding="utf-8")
    (root / "engine" / "from_import.py").write_text(
        f"from {term} import load_pbp\n", encoding="utf-8"
    )
    (root / "engine" / "dynamic_import.py").write_text(
        f"__import__({term!r})\n", encoding="utf-8"
    )
    (root / "engine" / "subprocess.py").write_text(
        f"subprocess.run(['python', '-m', {term!r}])\n", encoding="utf-8"
    )
    (root / "scripts.sh").write_text(f"python -m {term}\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        f'dependencies = ["{term}==1.0"]\n', encoding="utf-8"
    )
    (root / "docs" / "install.md").write_text(f"pip install {term}\n", encoding="utf-8")
    (root / "docs" / "operator.md").write_text(
        f"Use {term} to retrieve play-by-play data.\n", encoding="utf-8"
    )
    (root / "tests" / "not_governance.py").write_text(f"package = {term!r}\n", encoding="utf-8")
    (root / "tests" / "governance_evidence.py").write_text(
        "\n".join(
            (
                "Direct GitHub release-asset access only; `nfl_data_py` rejected.",
                "`nfl_data_py` is prohibited.",
                "`nfl_data_py` is rejected.",
                "`nfl_data_py` must not be used.",
                "`nfl_data_py` remains prohibited.",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    violations = scan_prohibited_active_use(root)

    assert {violation.path.as_posix() for violation in violations} == {
        "docs/install.md",
        "docs/operator.md",
        "engine/dynamic_import.py",
        "engine/from_import.py",
        "engine/import.py",
        "engine/subprocess.py",
        "pyproject.toml",
        "scripts.sh",
        "tests/not_governance.py",
    }


def test_ac15_repository_has_no_active_prohibited_use_and_tests_write_only_to_tmp_path(
    tmp_path: Path,
) -> None:
    production_path = Path("data/raw/nflverse/pbp")
    assert not production_path.exists()
    violations = scan_prohibited_active_use(Path("."))
    assert not violations, "\n".join(
        f"{violation.path}:{violation.line_number}: {violation.line}"
        for violation in violations
    )

    result, _ = _ingest(tmp_path / "explicit-data-root", _parquet_bytes(_valid_table()))

    assert result.status == "success_new_revision"
    assert not production_path.exists()
