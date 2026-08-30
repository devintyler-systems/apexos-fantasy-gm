"""Bounded, single-asset nflverse raw-evidence capture.

This module captures immutable historical evidence only. It does not discover
assets, resolve canonical identities, calculate features, or produce any
projection, score, rank, or recommendation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx
import pyarrow as pa
import pyarrow.parquet as pq

SOURCE_ID = "nflverse_direct_github_release_assets"
SOURCE_PROVIDER_OR_URL = "https://github.com/nflverse/nflverse-data/releases"
RIGHTS_OR_TERMS_REFERENCE = "docs/data_source_connector_register.md"
RELEASE_TAG = "pbp"
MIN_SEASON = 2016
MAX_SEASON = 2025
REQUIRED_COLUMNS = ("season", "week", "game_id", "posteam", "defteam", "play_type")
REQUIRED_REASON_CODES = frozenset(
    {
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
    }
)
IDENTITY_COLUMNS = {
    "game_id": "game",
    "posteam": "team",
    "defteam": "team",
}
APPROVED_GITHUB_HOSTS = frozenset(
    {
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)
LOCAL_FIXTURE_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_RFC3339_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)$"
)
_CANONICAL_RELEASE_PATH_PREFIX = "/nflverse/nflverse-data/releases/download/pbp/"


@dataclass(frozen=True)
class NflverseAssetRequest:
    season: int
    release_tag: str
    asset_name: str
    asset_url: str
    expected_sha256: str | None
    expected_byte_count: int | None
    as_of_timestamp: str
    source_contract_version: str
    parser_version: str


@dataclass(frozen=True)
class EvidenceLineage:
    source_id: str
    source_provider_or_url: str
    release_tag: str
    asset_name: str
    asset_url: str
    retrieval_timestamp: str
    effective_timestamp: str | None
    as_of_timestamp: str
    snapshot_id: str
    raw_sha256: str
    raw_byte_count: int
    expected_sha256: str | None
    expected_byte_count: int | None
    parser_version: str
    source_contract_version: str
    freshness_status: str
    rights_or_terms_reference: str


@dataclass(frozen=True)
class IdentityQuarantineRecord:
    source_entity_type: str
    source_entity_id: str | None
    source_display_name: str | None
    reason_code: str
    source_row_number: int | None


@dataclass(frozen=True)
class RawEvidenceCaptureResult:
    status: str
    reason_codes: tuple[str, ...]
    snapshot_id: str | None
    raw_asset_path: str | None
    manifest_path: str | None
    lineage: EvidenceLineage | None
    parsed_row_count: int | None
    quarantined_identity_count: int
    quarantine_path: str | None
    known_limitations: tuple[str, ...]
    degraded_mode: bool


@dataclass(frozen=True)
class HttpFetchResponse:
    status_code: int
    body: bytes
    effective_timestamp: str | None = None


class HttpTransport(Protocol):
    def fetch(self, url: str) -> HttpFetchResponse:
        """Fetch exactly one explicitly supplied asset URL."""


class HttpxHttpTransport:
    """Small production transport for one explicit, bounded asset request."""

    def __init__(self, *, timeout_seconds: float = 30.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> HttpFetchResponse:
        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                follow_redirects=True,
                max_redirects=5,
                headers={"User-Agent": "ApexOS-Raw-Evidence-v0.1"},
            ) as client:
                response = client.get(url)
            for hop in (*response.history, response):
                _validate_asset_url(
                    str(hop.url),
                    fixture_mode=False,
                    redirect_target=True,
                )
            status = response.status_code
            body = response.content
            last_modified = response.headers.get("Last-Modified")
        except (httpx.HTTPError, CaptureFailure, OSError, ValueError) as exc:
            raise HttpRetrievalError(_safe_error(exc)) from exc
        effective_timestamp = None
        if last_modified:
            try:
                effective_timestamp = _format_utc(parsedate_to_datetime(last_modified))
            except (TypeError, ValueError, OverflowError):
                effective_timestamp = None
        return HttpFetchResponse(
            status_code=status,
            body=body,
            effective_timestamp=effective_timestamp,
        )


class HttpRetrievalError(RuntimeError):
    """Safe transport failure translated to a structured degraded result."""


class CaptureFailure(RuntimeError):
    def __init__(self, reason_code: str, limitation: str) -> None:
        super().__init__(limitation)
        self.reason_code = reason_code
        self.limitation = limitation


def capture_nflverse_raw_evidence(
    request: NflverseAssetRequest,
    output_root: Path,
    transport: HttpTransport,
    *,
    clock: Callable[[], datetime] | None = None,
    fixture_mode: bool = False,
) -> RawEvidenceCaptureResult:
    """Capture exactly one selected asset into immutable local raw evidence."""

    clock = clock or (lambda: datetime.now(UTC))
    try:
        as_of = _parse_rfc3339_utc(request.as_of_timestamp)
        _validate_request(request, fixture_mode=fixture_mode)
        retrieval_timestamp = _format_utc(clock())
    except CaptureFailure as exc:
        return _failed(exc.reason_code, exc.limitation)
    except (TypeError, ValueError, OverflowError) as exc:
        return _failed("INVALID_TIMESTAMP", _safe_error(exc))

    try:
        response = transport.fetch(request.asset_url)
    except (HttpRetrievalError, OSError, ValueError) as exc:
        return _failed("HTTP_RETRIEVAL_FAILED", _safe_error(exc))
    except Exception as exc:  # noqa: BLE001 - injected transports are external
        return _failed("HTTP_RETRIEVAL_FAILED", _safe_error(exc))

    if not 200 <= response.status_code < 300:
        return _failed(
            "HTTP_RETRIEVAL_FAILED",
            f"Asset retrieval returned HTTP status {response.status_code}.",
        )
    raw_bytes = bytes(response.body)
    if not raw_bytes:
        return _failed("SOURCE_SNAPSHOT_MISSING", "Asset response contained no bytes.")

    try:
        effective_timestamp, effective = _optional_timestamp(response.effective_timestamp)
    except CaptureFailure as exc:
        return _failed(exc.reason_code, exc.limitation)
    if effective is not None and effective > as_of:
        return _failed(
            "TIME_INTEGRITY_FAILED",
            "Effective timestamp is later than the declared as-of timestamp.",
        )

    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    raw_byte_count = len(raw_bytes)
    if request.expected_sha256 is not None and raw_sha256 != request.expected_sha256:
        return _failed("HASH_MISMATCH", "Captured bytes do not match expected_sha256.")
    if (
        request.expected_byte_count is not None
        and raw_byte_count != request.expected_byte_count
    ):
        return _failed(
            "BYTE_COUNT_MISMATCH",
            "Captured byte count does not match expected_byte_count.",
        )

    try:
        table, observed_columns = _read_and_validate_parquet(raw_bytes)
        quarantine = _inspect_identity_safety(table)
    except CaptureFailure as exc:
        return _failed(exc.reason_code, exc.limitation)

    snapshot_id = _snapshot_id(request, raw_sha256)
    output_root = Path(output_root)
    raw_path = output_root / "raw" / snapshot_id / request.asset_name
    manifest_path = output_root / "manifests" / f"{snapshot_id}.json"
    quarantine_path = output_root / "quarantine" / f"{snapshot_id}.jsonl"

    reason_codes: list[str] = []
    known_limitations: list[str] = [
        "Raw evidence only; canonical identity resolution was not performed."
    ]
    if quarantine:
        reason_codes.append("CANONICAL_IDENTITY_UNRESOLVED")
        known_limitations.append(
            "Unresolved source identity values are quarantined; no canonical mapping was created."
        )
    if effective_timestamp is None:
        reason_codes.append("SOURCE_FRESHNESS_UNKNOWN")
        known_limitations.append(
            "Source effective timestamp was unavailable; this is historical evidence only."
        )
    if fixture_mode:
        reason_codes.append("FIXTURE_MODE_NOT_PRODUCTION")
        known_limitations.append(
            "Fixture transport output is test evidence and is not production capture evidence."
        )

    reason_codes = list(dict.fromkeys(reason_codes))
    known_limitations = list(dict.fromkeys(known_limitations))
    lineage = EvidenceLineage(
        source_id=SOURCE_ID,
        source_provider_or_url=SOURCE_PROVIDER_OR_URL,
        release_tag=request.release_tag,
        asset_name=request.asset_name,
        asset_url=request.asset_url,
        retrieval_timestamp=retrieval_timestamp,
        effective_timestamp=effective_timestamp,
        as_of_timestamp=_format_utc(as_of),
        snapshot_id=snapshot_id,
        raw_sha256=raw_sha256,
        raw_byte_count=raw_byte_count,
        expected_sha256=request.expected_sha256,
        expected_byte_count=request.expected_byte_count,
        parser_version=request.parser_version,
        source_contract_version=request.source_contract_version,
        freshness_status="historical_snapshot",
        rights_or_terms_reference=RIGHTS_OR_TERMS_REFERENCE,
    )
    quarantine_bytes = _jsonl_bytes(quarantine)
    manifest = _build_manifest(
        request=request,
        lineage=lineage,
        observed_columns=observed_columns,
        parsed_row_count=table.num_rows,
        quarantine=quarantine,
        quarantine_path=quarantine_path,
        reason_codes=reason_codes,
        known_limitations=known_limitations,
    )
    manifest_bytes = _json_bytes(manifest)

    try:
        idempotent_manifest = _existing_equivalent_manifest(
            raw_path=raw_path,
            manifest_path=manifest_path,
            quarantine_path=quarantine_path,
            raw_bytes=raw_bytes,
            manifest=manifest,
            quarantine_bytes=quarantine_bytes,
        )
        if idempotent_manifest is not None:
            return _success_result(
                status="success_idempotent",
                manifest=idempotent_manifest,
                raw_path=raw_path,
                manifest_path=manifest_path,
                quarantine_path=quarantine_path,
            )
        _publish_snapshot(
            raw_path=raw_path,
            manifest_path=manifest_path,
            quarantine_path=quarantine_path,
            raw_bytes=raw_bytes,
            manifest_bytes=manifest_bytes,
            quarantine_bytes=quarantine_bytes,
        )
    except CaptureFailure as exc:
        return _failed(exc.reason_code, exc.limitation)
    except OSError as exc:
        return _failed("FILESYSTEM_WRITE_FAILED", _safe_error(exc))

    return RawEvidenceCaptureResult(
        status="success_degraded" if reason_codes else "success",
        reason_codes=tuple(reason_codes),
        snapshot_id=snapshot_id,
        raw_asset_path=str(raw_path),
        manifest_path=str(manifest_path),
        lineage=lineage,
        parsed_row_count=table.num_rows,
        quarantined_identity_count=len(quarantine),
        quarantine_path=str(quarantine_path),
        known_limitations=tuple(known_limitations),
        degraded_mode=bool(reason_codes),
    )


def result_to_dict(result: RawEvidenceCaptureResult) -> dict[str, Any]:
    """Convert a result to a stable JSON-compatible representation."""

    payload = asdict(result)
    payload["reason_codes"] = list(result.reason_codes)
    payload["known_limitations"] = list(result.known_limitations)
    return payload


def _validate_request(request: NflverseAssetRequest, *, fixture_mode: bool) -> None:
    if not isinstance(request.season, int) or not MIN_SEASON <= request.season <= MAX_SEASON:
        raise CaptureFailure(
            "UNSUPPORTED_SEASON",
            f"Season must be between {MIN_SEASON} and {MAX_SEASON} inclusive.",
        )
    expected_name = f"play_by_play_{request.season}.parquet"
    if request.release_tag != RELEASE_TAG or request.asset_name != expected_name:
        raise CaptureFailure(
            "INVALID_ASSET_IDENTITY",
            "release_tag must be pbp and asset_name must exactly match the selected season.",
        )
    _validate_asset_url(
        request.asset_url,
        fixture_mode=fixture_mode,
        asset_name=request.asset_name,
    )
    if request.expected_sha256 is not None and not _SHA256_RE.fullmatch(
        request.expected_sha256
    ):
        raise CaptureFailure(
            "INVALID_ASSET_IDENTITY",
            "expected_sha256 must be 64 lowercase hexadecimal characters.",
        )
    if request.expected_byte_count is not None and (
        not isinstance(request.expected_byte_count, int)
        or request.expected_byte_count < 0
    ):
        raise CaptureFailure(
            "INVALID_ASSET_IDENTITY",
            "expected_byte_count must be a non-negative integer.",
        )
    if not request.parser_version.strip() or not request.source_contract_version.strip():
        raise CaptureFailure(
            "INVALID_ASSET_IDENTITY",
            "parser_version and source_contract_version are required.",
        )


def _validate_asset_url(
    url: str,
    *,
    fixture_mode: bool,
    asset_name: str | None = None,
    redirect_target: bool = False,
) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if fixture_mode:
        if parsed.scheme not in {"http", "https"} or host not in LOCAL_FIXTURE_HOSTS:
            raise CaptureFailure(
                "INVALID_ASSET_IDENTITY",
                "Fixture mode permits local HTTP simulation only.",
            )
        return
    if parsed.scheme != "https" or host not in APPROVED_GITHUB_HOSTS:
        raise CaptureFailure(
            "INVALID_ASSET_IDENTITY",
            "Production asset_url must be HTTPS on an approved GitHub release-asset host.",
        )
    if host == "github.com":
        if not parsed.path.startswith(_CANONICAL_RELEASE_PATH_PREFIX):
            raise CaptureFailure(
                "INVALID_ASSET_IDENTITY",
                "GitHub asset_url must target the nflverse-data pbp release.",
            )
        if asset_name is not None and not parsed.path.endswith(f"/{asset_name}"):
            raise CaptureFailure(
                "INVALID_ASSET_IDENTITY",
                "GitHub asset_url must end with the explicitly selected asset name.",
            )
    elif not redirect_target:
        raise CaptureFailure(
            "INVALID_ASSET_IDENTITY",
            "The requested asset_url must be the canonical nflverse GitHub release URL.",
        )


def _read_and_validate_parquet(raw_bytes: bytes) -> tuple[pa.Table, tuple[str, ...]]:
    try:
        parquet = pq.ParquetFile(pa.BufferReader(raw_bytes))
        observed = tuple(parquet.schema_arrow.names)
        missing = sorted(set(REQUIRED_COLUMNS) - set(observed))
        if missing:
            raise CaptureFailure(
                "REQUIRED_SCHEMA_FIELD_MISSING",
                "Missing required schema fields: " + ", ".join(missing),
            )
        table = parquet.read()
    except CaptureFailure:
        raise
    except Exception as exc:
        raise CaptureFailure(
            "MALFORMED_PARQUET", "Captured bytes are not readable parquet."
        ) from exc
    return table, observed


def _inspect_identity_safety(table: pa.Table) -> list[IdentityQuarantineRecord]:
    records: list[IdentityQuarantineRecord] = []
    names = set(table.column_names)
    for column_name, entity_type in IDENTITY_COLUMNS.items():
        if column_name not in names:
            continue
        for row_number, value in enumerate(table[column_name].to_pylist(), start=1):
            if value is None or (isinstance(value, str) and not value.strip()):
                records.append(
                    IdentityQuarantineRecord(
                        source_entity_type=entity_type,
                        source_entity_id=None if value is None else str(value),
                        source_display_name=None,
                        reason_code="CANONICAL_IDENTITY_UNRESOLVED",
                        source_row_number=row_number,
                    )
                )
    return records


def _snapshot_id(request: NflverseAssetRequest, raw_sha256: str) -> str:
    identity = {
        "asset_name": request.asset_name,
        "parser_version": request.parser_version,
        "raw_sha256": raw_sha256,
        "release_tag": request.release_tag,
        "source_contract_version": request.source_contract_version,
        "source_id": SOURCE_ID,
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"nflverse-{digest}"


def _build_manifest(
    *,
    request: NflverseAssetRequest,
    lineage: EvidenceLineage,
    observed_columns: tuple[str, ...],
    parsed_row_count: int,
    quarantine: list[IdentityQuarantineRecord],
    quarantine_path: Path,
    reason_codes: list[str],
    known_limitations: list[str],
) -> dict[str, Any]:
    manifest = asdict(lineage)
    manifest.update(
        {
            "season": request.season,
            "schema_validation": {
                "status": "pass",
                "required_columns": list(REQUIRED_COLUMNS),
                "observed_columns": list(observed_columns),
                "missing_columns": [],
            },
            "parsed_row_count": parsed_row_count,
            "identity_quarantine": {
                "count": len(quarantine),
                "path": str(quarantine_path),
                "reason_code": (
                    "CANONICAL_IDENTITY_UNRESOLVED" if quarantine else None
                ),
                "canonical_mapping_created": False,
            },
            "reason_codes": reason_codes,
            "known_limitations": known_limitations,
            "degraded_mode": bool(reason_codes),
            "projection_authority": "none_raw_evidence_only",
            "provider_projection_fields_used": False,
        }
    )
    return manifest


def _existing_equivalent_manifest(
    *,
    raw_path: Path,
    manifest_path: Path,
    quarantine_path: Path,
    raw_bytes: bytes,
    manifest: dict[str, Any],
    quarantine_bytes: bytes,
) -> dict[str, Any] | None:
    paths = (raw_path, manifest_path, quarantine_path)
    if not any(path.exists() for path in paths):
        return None
    if not all(path.is_file() for path in paths):
        raise CaptureFailure(
            "SNAPSHOT_CONFLICT",
            "Snapshot destination is incomplete or contains a non-file path.",
        )
    try:
        existing_raw = raw_path.read_bytes()
        existing_quarantine = quarantine_path.read_bytes()
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CaptureFailure(
            "SNAPSHOT_CONFLICT", "Existing snapshot evidence is unreadable."
        ) from exc
    if existing_raw != raw_bytes or existing_quarantine != quarantine_bytes:
        raise CaptureFailure(
            "SNAPSHOT_CONFLICT", "Existing snapshot bytes differ from the capture."
        )
    if _stable_manifest(existing_manifest) != _stable_manifest(manifest):
        raise CaptureFailure(
            "SNAPSHOT_CONFLICT", "Existing snapshot lineage differs from the capture."
        )
    return existing_manifest


def _stable_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    stable = json.loads(json.dumps(manifest))
    stable.pop("retrieval_timestamp", None)
    return stable


def _publish_snapshot(
    *,
    raw_path: Path,
    manifest_path: Path,
    quarantine_path: Path,
    raw_bytes: bytes,
    manifest_bytes: bytes,
    quarantine_bytes: bytes,
) -> None:
    temporary_paths: list[Path] = []
    published_paths: list[Path] = []
    try:
        raw_temp = _write_temp(raw_path.parent, raw_bytes)
        quarantine_temp = _write_temp(quarantine_path.parent, quarantine_bytes)
        manifest_temp = _write_temp(manifest_path.parent, manifest_bytes)
        temporary_paths.extend((raw_temp, quarantine_temp, manifest_temp))
        for temporary, final in (
            (raw_temp, raw_path),
            (quarantine_temp, quarantine_path),
            (manifest_temp, manifest_path),
        ):
            try:
                os.link(temporary, final)
            except FileExistsError as exc:
                raise CaptureFailure(
                    "SNAPSHOT_CONFLICT",
                    "Snapshot destination appeared during atomic publication.",
                ) from exc
            published_paths.append(final)
    except Exception:
        for path in reversed(published_paths):
            path.unlink(missing_ok=True)
        raise
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def _write_temp(parent: Path, payload: bytes) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".capture-", suffix=".tmp", dir=parent)
    path = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path


def _success_result(
    *,
    status: str,
    manifest: dict[str, Any],
    raw_path: Path,
    manifest_path: Path,
    quarantine_path: Path,
) -> RawEvidenceCaptureResult:
    lineage_fields = set(EvidenceLineage.__dataclass_fields__)
    lineage = EvidenceLineage(
        **{name: manifest[name] for name in lineage_fields}
    )
    return RawEvidenceCaptureResult(
        status=status,
        reason_codes=tuple(manifest["reason_codes"]),
        snapshot_id=manifest["snapshot_id"],
        raw_asset_path=str(raw_path),
        manifest_path=str(manifest_path),
        lineage=lineage,
        parsed_row_count=manifest["parsed_row_count"],
        quarantined_identity_count=manifest["identity_quarantine"]["count"],
        quarantine_path=str(quarantine_path),
        known_limitations=tuple(manifest["known_limitations"]),
        degraded_mode=bool(manifest["degraded_mode"]),
    )


def _failed(reason_code: str, limitation: str) -> RawEvidenceCaptureResult:
    return RawEvidenceCaptureResult(
        status="failed",
        reason_codes=(reason_code,),
        snapshot_id=None,
        raw_asset_path=None,
        manifest_path=None,
        lineage=None,
        parsed_row_count=None,
        quarantined_identity_count=0,
        quarantine_path=None,
        known_limitations=(limitation,),
        degraded_mode=True,
    )


def _optional_timestamp(value: str | None) -> tuple[str | None, datetime | None]:
    if value is None:
        return None, None
    parsed = _parse_rfc3339_utc(value)
    return _format_utc(parsed), parsed


def _parse_rfc3339_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CaptureFailure("INVALID_TIMESTAMP", "Timestamp must be RFC3339 UTC.")
    candidate = value.strip()
    if not _RFC3339_UTC_RE.fullmatch(candidate):
        raise CaptureFailure("INVALID_TIMESTAMP", "Timestamp must be RFC3339 UTC.")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise CaptureFailure("INVALID_TIMESTAMP", "Timestamp must be RFC3339 UTC.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise CaptureFailure("INVALID_TIMESTAMP", "Timestamp must use the UTC offset.")
    return parsed.astimezone(UTC)


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CaptureFailure("INVALID_TIMESTAMP", "Timestamp must be timezone-aware UTC.")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _jsonl_bytes(records: list[IdentityQuarantineRecord]) -> bytes:
    return b"".join(
        (json.dumps(asdict(record), sort_keys=True) + "\n").encode("utf-8")
        for record in records
    )


def _safe_error(exc: BaseException) -> str:
    text = " ".join(str(exc).split())
    return text[:300] or exc.__class__.__name__
