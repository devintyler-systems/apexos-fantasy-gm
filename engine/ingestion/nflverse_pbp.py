"""B-06 direct-release play-by-play evidence ingestion.

The adapter retains provider Parquet bytes exactly as retrieved, validates only
the contract v0.3 subset, and makes a revision reachable through ``current.json``
only after validation and immutable promotion. Callers can inject an
``httpx.Client``; acceptance tests use ``MockTransport`` exclusively.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from typing import Any, Literal, TypeAlias
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import httpx
import pyarrow as pa
import pyarrow.parquet as pq


DISCOVERY_URL = "https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp"
CANONICAL_SOURCE_ID = "nflverse/nflverse-data:release:pbp"
PARSER_VERSION = "b06-v0.3-evidence-1"
REQUIRED_COLUMNS = (
    "season",
    "season_type",
    "game_id",
    "yardline_100",
    "touchdown",
    "rush_attempt",
    "pass_attempt",
)
EXPECTED_REGULAR_SEASON_GAMES = {
    **{season: 256 for season in range(2016, 2021)},
    2021: 272,
    2022: 271,
    **{season: 272 for season in range(2023, 2026)},
}
APPROVED_DOWNLOAD_HOSTS = frozenset(
    {
        "api.github.com",
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)
MAX_DOWNLOAD_BYTES = 128 * 1024 * 1024
MAX_REDIRECTS = 5
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PROVIDER_DIGEST_RE = re.compile(r"^sha256:([0-9a-f]{64})$")

IngestionOutcome: TypeAlias = Literal[
    "success_new_revision",
    "success_existing_revision",
    "cached_valid_after_failure",
    "failed",
]
Freshness: TypeAlias = Literal["fresh", "stale", "unavailable"]


@dataclass(frozen=True, slots=True)
class IngestionResult:
    status: IngestionOutcome
    season: int
    revision_sha256: str | None
    manifest_path: Path | None
    failure_class: str | None
    failure_detail: str | None
    freshness: Freshness
    stale_banner_required: bool


@dataclass(frozen=True, slots=True)
class ReleaseAsset:
    release_id: int
    release_tag: str
    asset_id: int
    name: str
    size: int
    digest: str | None
    download_url: str
    source_observed_at_utc: str | None


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    row_count: int
    game_counts_by_season_type: dict[str, int]
    expected_regular_season_games: int


@dataclass(frozen=True, slots=True)
class ValidCurrent:
    revision_sha256: str
    manifest_path: Path
    ordering_key: tuple[str, str, str]


class IngestionFailure(RuntimeError):
    def __init__(
        self,
        failure_class: str,
        detail: str,
        *,
        attempted_url: str | None = None,
    ) -> None:
        super().__init__(detail)
        self.failure_class = failure_class
        self.detail = detail
        self.attempted_url = attempted_url


def ingest_nflverse_pbp_season(
    season: int,
    data_root: Path = Path("data/raw/nflverse/pbp"),
    *,
    client: httpx.Client | None = None,
    clock: Callable[[], datetime] | None = None,
    id_factory: Callable[[], str] | None = None,
) -> IngestionResult:
    """Retrieve, validate, and immutably promote one nflverse PBP season.

    ``data_root`` is injectable so evidence tests and reviewers can constrain
    every write to a temporary directory.
    """

    data_root = Path(data_root)
    clock = clock or (lambda: datetime.now(timezone.utc))
    id_factory = id_factory or (lambda: uuid4().hex)
    retrieval_event_id = _safe_identifier(id_factory(), "retrieval event")
    attempted_url: str | None = DISCOVERY_URL
    candidate_path: Path | None = None
    prior = _read_valid_current(data_root, season)
    owns_client = client is None
    if client is None:
        client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=False,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "ApexOS-B06"},
        )

    try:
        expected_games = EXPECTED_REGULAR_SEASON_GAMES.get(season)
        if expected_games is None:
            raise IngestionFailure(
                "unsupported_season",
                "Requested season is outside the contract policy window 2016-2025.",
            )

        release = _request_json(client, DISCOVERY_URL)
        asset = _select_asset(release, season)
        attempted_url = asset.download_url
        retrieved_at = _utc_timestamp(clock())
        candidate_path, revision_sha256 = _download_candidate(
            client, asset, data_root, season, retrieval_event_id
        )
        summary = _validate_parquet(candidate_path, season)
        promotion_claim_id = _safe_identifier(id_factory(), "promotion claim")
        manifest_path, outcome = _promote_revision(
            data_root=data_root,
            season=season,
            candidate_path=candidate_path,
            revision_sha256=revision_sha256,
            asset=asset,
            summary=summary,
            retrieved_at=retrieved_at,
            retrieval_event_id=retrieval_event_id,
            promotion_claim_id=promotion_claim_id,
        )
        ordering_key = (
            asset.source_observed_at_utc or "0001-01-01T00:00:00Z",
            _utc_timestamp(clock()),
            revision_sha256,
        )
        pointer_published = _publish_pointer(
            data_root=data_root,
            season=season,
            revision_sha256=revision_sha256,
            manifest_path=manifest_path,
            ordering_key=ordering_key,
            promotion_claim_id=promotion_claim_id,
            retrieval_event_id=retrieval_event_id,
        )
        _write_retrieval_event(
            data_root=data_root,
            season=season,
            event_id=retrieval_event_id,
            asset=asset,
            revision_sha256=revision_sha256,
            outcome=outcome,
            retrieved_at=retrieved_at,
            prior_revision_sha256=prior.revision_sha256 if prior else None,
            ordering_key=ordering_key,
            pointer_published=pointer_published,
        )
        return IngestionResult(
            status=outcome,
            season=season,
            revision_sha256=revision_sha256,
            manifest_path=manifest_path,
            failure_class=None,
            failure_detail=None,
            freshness="fresh",
            stale_banner_required=False,
        )
    except IngestionFailure as exc:
        _write_failed_attempt(
            data_root=data_root,
            season=season,
            attempt_id=_safe_identifier(id_factory(), "failed attempt"),
            attempted_url=exc.attempted_url or attempted_url,
            failure_class=exc.failure_class,
            failure_detail=exc.detail,
            prior_revision_sha256=prior.revision_sha256 if prior else None,
            attempted_at=_utc_timestamp(clock()),
        )
        return _failure_result(season, prior, exc.failure_class, exc.detail)
    except (httpx.HTTPError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        failure_class = "retrieval_or_storage_failure"
        detail = _safe_detail(exc)
        _write_failed_attempt(
            data_root=data_root,
            season=season,
            attempt_id=_safe_identifier(id_factory(), "failed attempt"),
            attempted_url=attempted_url,
            failure_class=failure_class,
            failure_detail=detail,
            prior_revision_sha256=prior.revision_sha256 if prior else None,
            attempted_at=_utc_timestamp(clock()),
        )
        return _failure_result(season, prior, failure_class, detail)
    finally:
        if candidate_path is not None:
            candidate_path.unlink(missing_ok=True)
        if owns_client:
            client.close()


def _request_json(client: httpx.Client, url: str) -> dict[str, Any]:
    response = _request_with_approved_redirects(client, url)
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise IngestionFailure("release_metadata", "Release metadata is not valid JSON.") from exc
    finally:
        response.close()
    if not isinstance(payload, dict):
        raise IngestionFailure("release_metadata", "Release metadata must be a JSON object.")
    return payload


def _request_with_approved_redirects(
    client: httpx.Client, url: str, *, stream: bool = False
) -> httpx.Response:
    current_url = url
    for redirect_count in range(MAX_REDIRECTS + 1):
        _validate_source_url(current_url)
        try:
            request = client.build_request("GET", current_url)
            response = client.send(request, follow_redirects=False, stream=stream)
        except httpx.HTTPError as exc:
            raise IngestionFailure(
                "http_request", _safe_detail(exc), attempted_url=current_url
            ) from exc
        if response.is_redirect:
            location = response.headers.get("location")
            if not location:
                response.close()
                raise IngestionFailure(
                    "redirect_rejected",
                    "Redirect response omitted Location.",
                    attempted_url=current_url,
                )
            if redirect_count == MAX_REDIRECTS:
                response.close()
                raise IngestionFailure(
                    "redirect_rejected", "Redirect limit exceeded.", attempted_url=current_url
                )
            current_url = urljoin(current_url, location)
            response.close()
            continue
        if not 200 <= response.status_code < 300:
            response.close()
            raise IngestionFailure(
                "http_status",
                f"HTTP request failed with status {response.status_code}.",
                attempted_url=current_url,
            )
        return response
    raise IngestionFailure("redirect_rejected", "Redirect handling failed.", attempted_url=url)


def _validate_source_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in APPROVED_DOWNLOAD_HOSTS:
        raise IngestionFailure(
            "redirect_rejected",
            "Source URL must use HTTPS on an approved GitHub host.",
            attempted_url=url,
        )


def _select_asset(release: dict[str, Any], season: int) -> ReleaseAsset:
    if not isinstance(release.get("id"), int) or release.get("tag_name") != "pbp":
        raise IngestionFailure("release_metadata", "Release ID or pbp tag metadata is missing.")
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise IngestionFailure("release_metadata", "Release assets metadata is missing.")
    expected_name = f"play_by_play_{season}.parquet"
    matches = [
        item
        for item in assets
        if isinstance(item, dict)
        and item.get("name") == expected_name
        and item.get("state") == "uploaded"
    ]
    if len(matches) != 1:
        raise IngestionFailure(
            "asset_selection",
            f"Expected exactly one uploaded asset named {expected_name}; found {len(matches)}.",
        )
    item = matches[0]
    required = {
        "id": int,
        "name": str,
        "state": str,
        "size": int,
        "browser_download_url": str,
    }
    if any(not isinstance(item.get(key), kind) for key, kind in required.items()):
        raise IngestionFailure("asset_metadata", "Selected asset metadata is incomplete.")
    if (
        not item["name"].endswith(".parquet")
        or item["size"] <= 0
        or item["size"] > MAX_DOWNLOAD_BYTES
    ):
        raise IngestionFailure("asset_metadata", "Selected asset extension or size is invalid.")
    _validate_source_url(item["browser_download_url"])
    digest = item.get("digest")
    if digest is not None and (
        not isinstance(digest, str) or _PROVIDER_DIGEST_RE.fullmatch(digest) is None
    ):
        raise IngestionFailure("asset_metadata", "Provider digest metadata is invalid.")
    observed = item.get("updated_at") or release.get("published_at")
    if observed is not None:
        if not isinstance(observed, str):
            raise IngestionFailure("release_metadata", "Source observation time is invalid.")
        observed = _normalize_timestamp(observed)
    return ReleaseAsset(
        release_id=release["id"],
        release_tag="pbp",
        asset_id=item["id"],
        name=item["name"],
        size=item["size"],
        digest=digest,
        download_url=item["browser_download_url"],
        source_observed_at_utc=observed,
    )


def _download_candidate(
    client: httpx.Client,
    asset: ReleaseAsset,
    data_root: Path,
    season: int,
    event_id: str,
) -> tuple[Path, str]:
    response = _request_with_approved_redirects(client, asset.download_url, stream=True)
    temporary_dir = data_root / f"season={season}" / ".tmp"
    temporary_dir.mkdir(parents=True, exist_ok=True)
    fd, raw_path = tempfile.mkstemp(prefix=f"candidate-{event_id}-", suffix=".parquet", dir=temporary_dir)
    path = Path(raw_path)
    digest = hashlib.sha256()
    downloaded_bytes = 0
    try:
        with os.fdopen(fd, "wb") as stream:
            for block in response.iter_bytes(chunk_size=1024 * 1024):
                downloaded_bytes += len(block)
                if downloaded_bytes > MAX_DOWNLOAD_BYTES or downloaded_bytes > asset.size:
                    raise IngestionFailure(
                        "download_size", "Downloaded asset exceeds its bounded size limit."
                    )
                stream.write(block)
                digest.update(block)
            stream.flush()
            os.fsync(stream.fileno())
        if downloaded_bytes != asset.size:
            raise IngestionFailure(
                "download_size", "Downloaded byte count differs from provider-reported asset size."
            )
        revision_sha256 = digest.hexdigest()
        if asset.digest is not None and revision_sha256 != asset.digest.removeprefix("sha256:"):
            raise IngestionFailure("digest_mismatch", "Provider and locally computed digests differ.")
    except Exception:
        path.unlink(missing_ok=True)
        raise
    finally:
        response.close()
    return path, revision_sha256


def _validate_parquet(path: Path, season: int) -> ValidationSummary:
    try:
        parquet_file = pq.ParquetFile(path)
        names = set(parquet_file.schema_arrow.names)
        missing = sorted(set(REQUIRED_COLUMNS) - names)
        if missing:
            raise IngestionFailure(
                "missing_required_column", f"Missing required columns: {', '.join(missing)}."
            )
        if parquet_file.metadata.num_rows <= 0:
            raise IngestionFailure("parquet_completeness", "Parquet row count must be nonzero.")
        table = parquet_file.read(columns=list(REQUIRED_COLUMNS))
    except IngestionFailure:
        raise
    except Exception as exc:
        raise IngestionFailure("invalid_parquet", "Downloaded bytes are not readable Parquet.") from exc

    _validate_integral_column(table, "season", nullable=False)
    season_values = set(table["season"].to_pylist())
    if season_values != {season}:
        raise IngestionFailure(
            "season_mismatch", "Exactly one observed season equal to the request is required."
        )
    _validate_string_column(table, "season_type", nullable=False)
    season_types = table["season_type"].to_pylist()
    if any(value not in {"REG", "POST"} for value in season_types):
        raise IngestionFailure("season_type_domain", "Unrecognized season_type value.")
    if "REG" not in season_types:
        raise IngestionFailure("game_count_mismatch", "At least one REG game is required.")
    _validate_string_column(table, "game_id", nullable=False)
    game_ids = table["game_id"].to_pylist()
    if any(value == "" or value.strip() == "" for value in game_ids):
        raise IngestionFailure("game_id_domain", "game_id values must be non-empty.")
    _validate_finite_numeric_column(table, "yardline_100", minimum=0, maximum=100)
    for name in ("touchdown", "rush_attempt", "pass_attempt"):
        _validate_binary_column(table, name)

    counts: dict[str, int] = {}
    for season_type in sorted(set(season_types)):
        counts[season_type] = len(
            {
                game_id
                for row_type, game_id in zip(season_types, game_ids)
                if row_type == season_type
            }
        )
    if sum(counts.values()) <= 0:
        raise IngestionFailure("parquet_completeness", "Distinct game count must be nonzero.")
    expected = EXPECTED_REGULAR_SEASON_GAMES[season]
    if counts.get("REG", 0) != expected:
        raise IngestionFailure(
            "game_count_mismatch",
            f"Expected {expected} distinct REG games; observed {counts.get('REG', 0)}.",
        )
    return ValidationSummary(table.num_rows, counts, expected)


def _validate_integral_column(table: pa.Table, name: str, *, nullable: bool) -> None:
    arrow_type = table.schema.field(name).type
    values = table[name].to_pylist()
    if not pa.types.is_integer(arrow_type):
        raise IngestionFailure("column_type", f"{name} must use an integral Arrow type.")
    if not nullable and any(value is None for value in values):
        raise IngestionFailure("column_nullability", f"{name} must not contain nulls.")


def _is_string_type(arrow_type: pa.DataType) -> bool:
    if pa.types.is_string(arrow_type) or pa.types.is_large_string(arrow_type):
        return True
    return pa.types.is_dictionary(arrow_type) and (
        pa.types.is_string(arrow_type.value_type) or pa.types.is_large_string(arrow_type.value_type)
    )


def _validate_string_column(table: pa.Table, name: str, *, nullable: bool) -> None:
    arrow_type = table.schema.field(name).type
    values = table[name].to_pylist()
    if not _is_string_type(arrow_type):
        raise IngestionFailure("column_type", f"{name} must use a UTF-8 string Arrow type.")
    if not nullable and any(value is None for value in values):
        raise IngestionFailure("column_nullability", f"{name} must not contain nulls.")


def _validate_finite_numeric_column(
    table: pa.Table, name: str, *, minimum: float, maximum: float
) -> None:
    arrow_type = table.schema.field(name).type
    if not (
        pa.types.is_integer(arrow_type)
        or pa.types.is_floating(arrow_type)
        or pa.types.is_decimal(arrow_type)
    ) or pa.types.is_boolean(arrow_type):
        raise IngestionFailure("column_type", f"{name} must use a numeric Arrow type.")
    for value in table[name].to_pylist():
        if value is None:
            continue
        numeric = float(value)
        if not math.isfinite(numeric) or not minimum <= numeric <= maximum:
            raise IngestionFailure("column_domain", f"{name} contains an out-of-domain value.")


def _validate_binary_column(table: pa.Table, name: str) -> None:
    arrow_type = table.schema.field(name).type
    if not (
        pa.types.is_boolean(arrow_type)
        or pa.types.is_integer(arrow_type)
        or pa.types.is_floating(arrow_type)
    ):
        raise IngestionFailure("column_type", f"{name} must use boolean or numeric binary encoding.")
    for value in table[name].to_pylist():
        if value is None:
            continue
        if isinstance(value, float) and not math.isfinite(value):
            raise IngestionFailure("column_domain", f"{name} contains a non-finite value.")
        if value not in (0, 1, False, True):
            raise IngestionFailure("column_domain", f"{name} must encode only zero or one.")


def _promote_revision(
    *,
    data_root: Path,
    season: int,
    candidate_path: Path,
    revision_sha256: str,
    asset: ReleaseAsset,
    summary: ValidationSummary,
    retrieved_at: str,
    retrieval_event_id: str,
    promotion_claim_id: str,
) -> tuple[Path, Literal["success_new_revision", "success_existing_revision"]]:
    domain = (
        data_root
        / "claims"
        / "revision"
        / f"season={season}"
        / f"sha256={revision_sha256}"
    )
    revision_dir = (
        data_root
        / f"season={season}"
        / "revisions"
        / f"sha256={revision_sha256}"
    )
    manifest_path = revision_dir / "manifest.json"
    with _exclusive_claim(domain):
        if revision_dir.exists():
            _validate_existing_revision(data_root, season, revision_sha256, manifest_path)
            return manifest_path, "success_existing_revision"
        claim_path = domain / f"claim-{promotion_claim_id}.json"
        _write_json_new(
            claim_path,
            {
                "promotion_claim_id": promotion_claim_id,
                "claimant_id": retrieval_event_id,
                "requested_season": season,
                "revision_sha256": revision_sha256,
                "temporary_file_identity": candidate_path.name,
                "started_at_utc": retrieved_at,
                "source_asset_id": asset.asset_id,
            },
        )
        revision_dir.mkdir(parents=True, exist_ok=False)
        payload_path = revision_dir / "pbp.parquet"
        with candidate_path.open("rb") as source, payload_path.open("xb") as destination:
            shutil.copyfileobj(source, destination)
            destination.flush()
            os.fsync(destination.fileno())
        manifest = {
            "canonical_source_id": CANONICAL_SOURCE_ID,
            "source_url": DISCOVERY_URL,
            "source_release_tag": asset.release_tag,
            "source_release_id": asset.release_id,
            "source_asset_id": asset.asset_id,
            "source_asset_name": asset.name,
            "source_asset_size_bytes_reported": asset.size,
            "source_asset_digest_reported": asset.digest,
            "requested_season": season,
            "game_counts_by_season_type": summary.game_counts_by_season_type,
            "regular_season_expected_game_count": summary.expected_regular_season_games,
            "regular_season_game_count_valid": True,
            "revision_sha256": revision_sha256,
            "retrieved_at_utc": retrieved_at,
            "effective_time": asset.source_observed_at_utc,
            "parser_version": PARSER_VERSION,
            "promotion_claim_id": promotion_claim_id,
            "retrieval_event_id": retrieval_event_id,
        }
        _write_json_new(manifest_path, manifest)
        _fsync_directory(revision_dir)
        _validate_existing_revision(data_root, season, revision_sha256, manifest_path)
        _write_json_new(
            domain / f"completed-{promotion_claim_id}.json",
            {
                "promotion_claim_id": promotion_claim_id,
                "revision_sha256": revision_sha256,
                "outcome": "success_new_revision",
            },
        )
    return manifest_path, "success_new_revision"


def _validate_existing_revision(
    data_root: Path, season: int, revision_sha256: str, manifest_path: Path
) -> ValidationSummary:
    expected_manifest = (
        data_root
        / f"season={season}"
        / "revisions"
        / f"sha256={revision_sha256}"
        / "manifest.json"
    )
    if manifest_path != expected_manifest or not _SHA256_RE.fullmatch(revision_sha256):
        raise IngestionFailure("evidence_collision", "Revision path identity is inconsistent.")
    payload_path = manifest_path.with_name("pbp.parquet")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        persisted_hash = _sha256_file(payload_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise IngestionFailure("evidence_collision", "Existing revision is unreadable.") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("revision_sha256") != revision_sha256
        or manifest.get("requested_season") != season
        or persisted_hash != revision_sha256
    ):
        raise IngestionFailure("evidence_collision", "Existing revision identity does not match.")
    summary = _validate_parquet(payload_path, season)
    _validate_manifest(manifest, season, revision_sha256, summary)
    return summary


def _validate_manifest(
    manifest: dict[str, Any],
    season: int,
    revision_sha256: str,
    summary: ValidationSummary,
) -> None:
    required_fields = {
        "canonical_source_id",
        "source_url",
        "source_release_tag",
        "source_release_id",
        "source_asset_id",
        "source_asset_name",
        "source_asset_size_bytes_reported",
        "source_asset_digest_reported",
        "requested_season",
        "game_counts_by_season_type",
        "regular_season_expected_game_count",
        "regular_season_game_count_valid",
        "revision_sha256",
        "retrieved_at_utc",
        "effective_time",
        "parser_version",
        "promotion_claim_id",
        "retrieval_event_id",
    }
    if not required_fields <= set(manifest):
        raise IngestionFailure("evidence_collision", "Existing manifest omits required fields.")
    digest = manifest["source_asset_digest_reported"]
    if digest is not None and (
        not isinstance(digest, str) or _PROVIDER_DIGEST_RE.fullmatch(digest) is None
    ):
        raise IngestionFailure("evidence_collision", "Existing manifest digest is invalid.")
    if (
        manifest["canonical_source_id"] != CANONICAL_SOURCE_ID
        or manifest["source_url"] != DISCOVERY_URL
        or manifest["source_release_tag"] != "pbp"
        or not isinstance(manifest["source_release_id"], int)
        or not isinstance(manifest["source_asset_id"], int)
        or manifest["source_asset_name"] != f"play_by_play_{season}.parquet"
        or not isinstance(manifest["source_asset_size_bytes_reported"], int)
        or manifest["source_asset_size_bytes_reported"] <= 0
        or manifest["requested_season"] != season
        or manifest["revision_sha256"] != revision_sha256
        or manifest["game_counts_by_season_type"] != summary.game_counts_by_season_type
        or manifest["regular_season_expected_game_count"]
        != summary.expected_regular_season_games
        or manifest["regular_season_game_count_valid"] is not True
        or not isinstance(manifest["parser_version"], str)
        or not manifest["parser_version"]
    ):
        raise IngestionFailure("evidence_collision", "Existing manifest provenance is invalid.")
    try:
        _normalize_timestamp(manifest["retrieved_at_utc"])
        if manifest["effective_time"] is not None:
            _normalize_timestamp(manifest["effective_time"])
        _safe_identifier(manifest["promotion_claim_id"], "promotion claim")
        _safe_identifier(manifest["retrieval_event_id"], "retrieval event")
    except (IngestionFailure, TypeError, ValueError) as exc:
        raise IngestionFailure("evidence_collision", "Existing manifest timestamps or IDs are invalid.") from exc


def _publish_pointer(
    *,
    data_root: Path,
    season: int,
    revision_sha256: str,
    manifest_path: Path,
    ordering_key: tuple[str, str, str],
    promotion_claim_id: str,
    retrieval_event_id: str,
) -> bool:
    domain = data_root / "claims" / "pointer" / f"season={season}"
    current_path = data_root / f"season={season}" / "current.json"
    with _exclusive_claim(domain):
        claim_path = domain / f"claim-{retrieval_event_id}.json"
        _write_json_new(
            claim_path,
            {
                "candidate_revision_sha256": revision_sha256,
                "candidate_ordering_key": list(ordering_key),
                "promotion_claim_id": promotion_claim_id,
                "retrieval_event_id": retrieval_event_id,
            },
        )
        existing = _read_valid_current(data_root, season)
        if current_path.exists() and existing is None:
            raise IngestionFailure("pointer_collision", "Existing current.json is invalid.")
        published = existing is None or ordering_key > existing.ordering_key
        if published:
            relative_manifest = manifest_path.relative_to(data_root).as_posix()
            _atomic_write_current(
                current_path,
                {
                    "manifest_path": relative_manifest,
                    "revision_sha256": revision_sha256,
                    "pointer_ordering_key": list(ordering_key),
                },
            )
        _write_json_new(
            domain / f"completed-{retrieval_event_id}.json",
            {
                "retrieval_event_id": retrieval_event_id,
                "candidate_revision_sha256": revision_sha256,
                "pointer_published": published,
            },
        )
        return published


def _read_valid_current(data_root: Path, season: int) -> ValidCurrent | None:
    current_path = data_root / f"season={season}" / "current.json"
    if not current_path.is_file():
        return None
    try:
        current = json.loads(current_path.read_text(encoding="utf-8"))
        if not isinstance(current, dict) or set(current) != {
            "manifest_path",
            "revision_sha256",
            "pointer_ordering_key",
        }:
            return None
        revision_sha256 = current["revision_sha256"]
        if not isinstance(revision_sha256, str) or not _SHA256_RE.fullmatch(revision_sha256):
            return None
        relative_manifest = current["manifest_path"]
        if not isinstance(relative_manifest, str):
            return None
        expected_relative = (
            Path(f"season={season}")
            / "revisions"
            / f"sha256={revision_sha256}"
            / "manifest.json"
        )
        if Path(relative_manifest) != expected_relative:
            return None
        ordering = current["pointer_ordering_key"]
        if (
            not isinstance(ordering, list)
            or len(ordering) != 3
            or any(not isinstance(value, str) for value in ordering)
            or ordering[2] != revision_sha256
        ):
            return None
        manifest_path = data_root / expected_relative
        _validate_existing_revision(data_root, season, revision_sha256, manifest_path)
        return ValidCurrent(revision_sha256, manifest_path, tuple(ordering))
    except (IngestionFailure, OSError, json.JSONDecodeError, ValueError, TypeError):
        return None


def _write_retrieval_event(
    *,
    data_root: Path,
    season: int,
    event_id: str,
    asset: ReleaseAsset,
    revision_sha256: str,
    outcome: IngestionOutcome,
    retrieved_at: str,
    prior_revision_sha256: str | None,
    ordering_key: tuple[str, str, str],
    pointer_published: bool,
) -> None:
    path = data_root / f"season={season}" / "events" / f"retrieval-{event_id}.json"
    _write_json_new(
        path,
        {
            "retrieval_event_id": event_id,
            "retrieved_at_utc": retrieved_at,
            "source_release_id": asset.release_id,
            "source_asset_id": asset.asset_id,
            "source_asset_url": asset.download_url,
            "local_revision_sha256": revision_sha256,
            "outcome": outcome,
            "freshness": "fresh",
            "claimed_revision_sha256": revision_sha256,
            "actual_revision_sha256": revision_sha256,
            "prior_current_revision_sha256": prior_revision_sha256,
            "pointer_ordering_key": list(ordering_key),
            "pointer_published": pointer_published,
        },
    )


def _write_failed_attempt(
    *,
    data_root: Path,
    season: int,
    attempt_id: str,
    attempted_url: str | None,
    failure_class: str,
    failure_detail: str,
    prior_revision_sha256: str | None,
    attempted_at: str,
) -> None:
    path = data_root / f"season={season}" / "events" / f"failed-attempt-{attempt_id}.json"
    try:
        _write_json_new(
            path,
            {
                "attempt_id": attempt_id,
                "attempted_at_utc": attempted_at,
                "attempted_url": attempted_url,
                "failure_class": failure_class,
                "failure_detail": failure_detail,
                "prior_valid_revision_sha256": prior_revision_sha256,
            },
        )
    except OSError:
        # The result must still fail closed if even failure evidence cannot be written.
        return


def _failure_result(
    season: int,
    prior: ValidCurrent | None,
    failure_class: str,
    failure_detail: str,
) -> IngestionResult:
    if prior is not None:
        return IngestionResult(
            status="cached_valid_after_failure",
            season=season,
            revision_sha256=prior.revision_sha256,
            manifest_path=prior.manifest_path,
            failure_class=failure_class,
            failure_detail=failure_detail,
            freshness="stale",
            stale_banner_required=True,
        )
    return IngestionResult(
        status="failed",
        season=season,
        revision_sha256=None,
        manifest_path=None,
        failure_class=failure_class,
        failure_detail=failure_detail,
        freshness="unavailable",
        stale_banner_required=False,
    )


@contextmanager
def _exclusive_claim(domain: Path, timeout_seconds: float = 10.0) -> Iterator[None]:
    domain.mkdir(parents=True, exist_ok=True)
    lock = domain / ".lock"
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise IngestionFailure("claim_contention", "Timed out waiting for claim owner.")
            time.sleep(0.01)
    try:
        yield
    finally:
        try:
            lock.rmdir()
        except OSError:
            pass


def _atomic_write_current(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_path = tempfile.mkstemp(prefix=".current-", suffix=".json", dir=path.parent)
    temporary = Path(raw_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _write_json_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_directory(path.parent)


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is None:
        raise ValueError(f"Invalid {label} identifier.")
    return value


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Clock must return a timezone-aware datetime.")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_timestamp(value: str) -> str:
    if not isinstance(value, str):
        raise IngestionFailure("release_metadata", "Source observation time is invalid.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IngestionFailure("release_metadata", "Source observation time is invalid.") from exc
    if parsed.tzinfo is None:
        raise IngestionFailure("release_metadata", "Source observation time lacks a timezone.")
    return _utc_timestamp(parsed)


def _safe_detail(exc: BaseException) -> str:
    detail = str(exc).replace("\r", " ").replace("\n", " ").strip()
    return detail[:500] or exc.__class__.__name__
