"""B-07 v0.1 deterministic contextual-baseline validation pipeline.

The module is deliberately local and artifact-first. It reads pinned immutable B-06
evidence, fits only the frozen 2023-2024 contextual rate tables, evaluates only the
2025 holdout, and writes one append-only validation package. It has no candidate
estimator, production xTD, pointer, endpoint, or recommendation integration.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import shutil
import uuid
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from engine.contracts.b07_v0_1 import (
    B07ValidationError,
    load_b07_contract,
    validate_b06_source_claim,
    validate_season_access,
)
from engine.ingestion.nflverse_pbp import normalize_no_play


ARTIFACT_VERSION = "b07-v0.1-baseline-1"
BASELINE_VERSION = "b07-v0.1-contextual-baseline-1"
IDENTITY_MAPPING_VERSION = "nflverse-canonical-player-id-no-merge-v0.1"
EXPECTED_CONTRACT_SHA256 = (
    "7cd8e294ca1b6fefadb1d35472e9a421c4829dd6f37dc6690abf2513b9da0abc"
)
EXPECTED_SEASONS = (2023, 2024, 2025)
DEVELOPMENT_SEASONS = (2023, 2024)
HOLDOUT_SEASON = 2025
ESTIMATORS = ("rush", "pass_target")
REQUIRED_COLUMNS = (
    "season",
    "season_type",
    "game_id",
    "play_id",
    "play_type",
    "rush_attempt",
    "pass_attempt",
    "rusher_player_id",
    "rusher_id",
    "receiver_player_id",
    "receiver_id",
    "touchdown",
    "rush_touchdown",
    "pass_touchdown",
    "td_player_id",
    "yardline_100",
    "down",
    "ydstogo",
    "goal_to_go",
    "qtr",
    "game_seconds_remaining",
    "score_differential",
    "two_point_attempt",
    "penalty",
    "sack",
    "qb_spike",
    "aborted_play",
)
POST_PLAY_FIELDS = frozenset(
    {
        "realized_touchdown",
        "yards_gained",
        "epa",
        "wpa",
        "success",
        "fantasy_points",
        "post_play_scores",
        "future_game_information",
        "season_end_aggregates",
    }
)
KNOWN_LIMITATIONS = (
    "baseline_only_no_candidate_comparison",
    "material_cohort_distinct_game_minimum_not_numerically_declared",
    "local_b06_evidence_does_not_reconfirm_current_provider_state",
    "raw_nflverse_player_ids_are_not_merged_with_alternate_identity_fields",
    "equal_frequency_reliability_bins_can_share_identical_probability_values",
)


class BaselineValidationError(ValueError):
    """Stable fail-closed reason for B-07 baseline validation."""

    def __init__(self, reason_code: str, detail: str) -> None:
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code} | {detail}")


@dataclass(frozen=True)
class SourceSpec:
    season: int
    payload_path: Path
    manifest_path: Path
    pointer_path: Path


@dataclass(frozen=True)
class SourceIdentity:
    season: int
    payload_path: str
    payload_sha256: str
    payload_bytes: int
    manifest_path: str
    manifest_sha256: str
    pointer_path: str
    pointer_sha256: str
    row_count: int
    game_counts_by_season_type: dict[str, int]
    parser_version: str
    normalization_version: str
    canonical_identity_mapping_version: str
    provider: str
    canonical_source_id: str
    retrieved_at_utc: str
    effective_time: str


@dataclass(frozen=True)
class EligibleEvent:
    season: int
    estimator: str
    game_id: str
    play_id: str
    source_event_locator: str
    yardline_band: str
    goal_to_go: bool
    down: int
    label: int
    features: dict[str, int | bool]
    payload_sha256: str
    manifest_sha256: str


@dataclass(frozen=True)
class LookupBundle:
    threshold: int
    hierarchy: tuple[tuple[str, ...], ...]
    cells: dict[tuple[str, ...], dict[tuple[Any, ...], tuple[int, int]]]


def _fail(reason_code: str, detail: str) -> None:
    raise BaselineValidationError(reason_code, detail)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonicalize_contract_bytes(value: bytes) -> bytes:
    """Return the UTF-8 LF-byte form used by the frozen B-07 contract digest."""
    if value.startswith(b"\xef\xbb\xbf"):
        _fail("B07_CONTRACT_CANONICALIZATION_FAILED", "UTF-8 BOM is prohibited")
    canonical = value.replace(b"\r\n", b"\n")
    if b"\r" in canonical:
        _fail("B07_CONTRACT_CANONICALIZATION_FAILED", "residual lone CR byte is prohibited")
    return canonical


def sha256_contract_file(path: str | Path) -> str:
    return sha256_bytes(canonicalize_contract_bytes(Path(path).read_bytes()))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def load_contract_checked(
    contract_path: str | Path,
    expected_sha256: str = EXPECTED_CONTRACT_SHA256,
) -> dict[str, Any]:
    """Attest contract bytes before loading its frozen semantic validator."""
    path = Path(contract_path)
    actual = sha256_contract_file(path)
    if actual != expected_sha256:
        _fail(
            "B07_CONTRACT_DIGEST_MISMATCH",
            f"path={path} actual={actual} expected={expected_sha256}",
        )
    try:
        return load_b07_contract(path)
    except B07ValidationError as exc:
        _fail("B07_CONTRACT_VALIDATION_FAILED", str(exc))


def _load_json_mapping(path: Path, reason_code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(reason_code, f"path={path} error={exc}")
    if not isinstance(value, dict):
        _fail(reason_code, f"path={path} root must be a JSON object")
    return value


def _nonempty_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _integral(value: Any) -> int | None:
    if type(value) is int:
        return value
    if type(value) is float and math.isfinite(value) and value.is_integer():
        return int(value)
    return None


def _explicit_flag(value: Any) -> bool:
    return value is True or (type(value) in {int, float} and value == 1)


def _binary_label(value: Any) -> int | None:
    if value is False or (type(value) in {int, float} and value == 0):
        return 0
    if value is True or (type(value) in {int, float} and value == 1):
        return 1
    return None


def validate_source_spec(
    spec: SourceSpec, contract: Mapping[str, Any]
) -> SourceIdentity:
    """Validate a pinned B-06 payload/manifest/pointer chain without label reads."""
    if spec.season not in EXPECTED_SEASONS:
        _fail("B07_SOURCE_SEASON_NOT_ALLOWED", f"season={spec.season}")
    for path in (spec.payload_path, spec.manifest_path, spec.pointer_path):
        if not path.is_file():
            _fail("B07_SOURCE_MISSING", f"season={spec.season} path={path}")

    manifest_bytes = spec.manifest_path.read_bytes()
    manifest = _load_json_mapping(spec.manifest_path, "B07_SOURCE_MANIFEST_INVALID")
    pointer_bytes = spec.pointer_path.read_bytes()
    pointer = _load_json_mapping(spec.pointer_path, "B07_SOURCE_POINTER_INVALID")
    payload_digest = sha256_file(spec.payload_path)
    manifest_digest = sha256_bytes(manifest_bytes)
    pointer_digest = sha256_bytes(pointer_bytes)

    parquet = pq.ParquetFile(spec.payload_path)
    schema_names = set(parquet.schema_arrow.names)
    missing = sorted(set(REQUIRED_COLUMNS) - schema_names)
    if missing:
        _fail(
            "B07_SOURCE_REQUIRED_SCHEMA_MISSING",
            f"season={spec.season} missing={missing}",
        )
    identity_table = parquet.read(columns=["season", "season_type", "game_id"])
    rows = identity_table.to_pylist()
    observed_seasons = {row["season"] for row in rows}
    if observed_seasons != {spec.season}:
        _fail(
            "B07_SOURCE_SEASON_CONTENT_MISMATCH",
            f"season={spec.season} observed={sorted(observed_seasons, key=str)}",
        )
    games_by_type: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        season_type = _nonempty_string(row["season_type"])
        game_id = _nonempty_string(row["game_id"])
        if season_type is None or game_id is None:
            _fail(
                "B07_SOURCE_EVENT_IDENTITY_MISMATCH",
                f"season={spec.season} season_type={row['season_type']!r} game_id={row['game_id']!r}",
            )
        games_by_type[season_type].add(game_id)
    observed_game_counts = {
        name: len(values) for name, values in sorted(games_by_type.items())
    }
    manifest_game_counts = manifest.get("game_counts_by_season_type")
    if observed_game_counts != manifest_game_counts:
        _fail(
            "B07_SOURCE_EVENT_COUNT_MISMATCH",
            f"season={spec.season} observed={observed_game_counts} manifest={manifest_game_counts}",
        )

    try:
        validate_b06_source_claim(
            contract,
            season=spec.season,
            declared_revision_digest=str(manifest.get("revision_sha256")),
            computed_payload_digest=payload_digest,
            manifest_revision_digest=str(manifest.get("computed_digest_sha256")),
            payload_row_count=parquet.metadata.num_rows,
            manifest_row_count=manifest.get("row_count"),
            payload_event_count=sum(observed_game_counts.values()),
            manifest_event_count=sum(manifest_game_counts.values()),
        )
    except (B07ValidationError, AttributeError, TypeError) as exc:
        reason = getattr(exc, "reason_code", "B07_SOURCE_MANIFEST_INVALID")
        _fail(reason, f"season={spec.season} {exc}")

    if pointer.get("revision_sha256") != payload_digest:
        _fail(
            "B07_SOURCE_POINTER_DIGEST_MISMATCH",
            f"season={spec.season} pointer={pointer.get('revision_sha256')} payload={payload_digest}",
        )
    if manifest.get("promotion_result") != "pass":
        _fail(
            "B07_SOURCE_PROMOTION_NOT_ACCEPTED",
            f"season={spec.season} promotion_result={manifest.get('promotion_result')!r}",
        )
    if manifest.get("regular_season_game_count_valid") is not True:
        _fail("B07_SOURCE_GAME_COUNT_INVALID", f"season={spec.season}")
    if manifest.get("unknown_row_count") != 0:
        _fail(
            "B07_SOURCE_NO_PLAY_UNKNOWN",
            f"season={spec.season} unknown_row_count={manifest.get('unknown_row_count')!r}",
        )
    if manifest.get("digest_match") is not True:
        _fail("B07_SOURCE_DIGEST_MISMATCH", f"season={spec.season}")

    required_strings = (
        "parser_version",
        "no_play_normalization_version",
        "provider",
        "canonical_source_id",
        "retrieved_at_utc",
        "effective_time",
    )
    values: dict[str, str] = {}
    for field in required_strings:
        value = _nonempty_string(manifest.get(field))
        if value is None:
            _fail(
                "B07_SOURCE_MANIFEST_IDENTITY_MISSING",
                f"season={spec.season} field={field}",
            )
        values[field] = value

    return SourceIdentity(
        season=spec.season,
        payload_path=str(spec.payload_path.resolve()),
        payload_sha256=payload_digest,
        payload_bytes=spec.payload_path.stat().st_size,
        manifest_path=str(spec.manifest_path.resolve()),
        manifest_sha256=manifest_digest,
        pointer_path=str(spec.pointer_path.resolve()),
        pointer_sha256=pointer_digest,
        row_count=parquet.metadata.num_rows,
        game_counts_by_season_type=observed_game_counts,
        parser_version=values["parser_version"],
        normalization_version=values["no_play_normalization_version"],
        canonical_identity_mapping_version=IDENTITY_MAPPING_VERSION,
        provider=values["provider"],
        canonical_source_id=values["canonical_source_id"],
        retrieved_at_utc=values["retrieved_at_utc"],
        effective_time=values["effective_time"],
    )


def source_snapshot_id(
    identities: Sequence[SourceIdentity], contract_sha256: str
) -> str:
    payload = {
        "contract_sha256": contract_sha256,
        "sources": [asdict(item) for item in sorted(identities, key=lambda item: item.season)],
    }
    return sha256_bytes(_json_bytes(payload))


def _yardline_band(value: int, contract: Mapping[str, Any]) -> str | None:
    bands = contract["b07_v0_1_contract"]["contextual_baseline"]["yardline_bands"]
    for lower, upper in bands:
        if lower <= value <= upper:
            return f"{lower}_{upper}"
    return None


def _validate_context(
    row: Mapping[str, Any], contract: Mapping[str, Any]
) -> tuple[dict[str, int | bool], str | None, list[str]]:
    policies = contract["b07_v0_1_contract"]["feature_allowlist"]
    reasons: list[str] = []
    values: dict[str, int | bool] = {}
    raw_names = {
        "yardline_100": "yardline_100",
        "down": "down",
        "ydstogo": "ydstogo",
        "goal_to_go": "goal_to_go",
        "quarter": "qtr",
        "game_seconds_remaining": "game_seconds_remaining",
        "score_differential": "score_differential",
    }
    for feature, raw_name in raw_names.items():
        raw_value = row.get(raw_name)
        if raw_value is None:
            reasons.append(f"B07_EXCLUDE_MISSING_{feature.upper()}")
            continue
        if feature == "goal_to_go":
            parsed = _integral(raw_value)
            if parsed not in {0, 1}:
                reasons.append("B07_EXCLUDE_INVALID_GOAL_TO_GO")
            else:
                values[feature] = bool(parsed)
            continue
        parsed = _integral(raw_value)
        if parsed is None:
            reasons.append(f"B07_EXCLUDE_INVALID_{feature.upper()}")
            continue
        policy = policies[feature]
        if "range" in policy:
            lower, upper = policy["range"]
            if not lower <= parsed <= upper:
                reasons.append(f"B07_EXCLUDE_INVALID_{feature.upper()}")
                continue
        if "minimum" in policy and parsed < policy["minimum"]:
            reasons.append(f"B07_EXCLUDE_INVALID_{feature.upper()}")
            continue
        values[feature] = parsed
    band = None
    if "yardline_100" in values:
        band = _yardline_band(int(values["yardline_100"]), contract)
        if band is None:
            reasons.append("B07_EXCLUDE_INVALID_YARDLINE_BAND")
    return values, band, reasons


def read_eligible_events(
    spec: SourceSpec,
    identity: SourceIdentity,
    contract: Mapping[str, Any],
    *,
    access_mode: str,
) -> tuple[list[EligibleEvent], dict[str, Any]]:
    """Read one accepted season under an explicit development/evaluation guard."""
    if access_mode == "development":
        purpose = "lookup_construction"
        evaluation_mode = False
    elif access_mode == "evaluation":
        purpose = "holdout_evaluation"
        evaluation_mode = True
    else:
        _fail("B07_SEASON_ACCESS_MODE_INVALID", f"access_mode={access_mode!r}")
    try:
        validate_season_access(
            contract,
            season=spec.season,
            purpose=purpose,
            evaluation_mode=evaluation_mode,
            labels_requested=True,
        )
    except B07ValidationError as exc:
        _fail(exc.reason_code, str(exc))

    rows = pq.ParquetFile(spec.payload_path).read(columns=list(REQUIRED_COLUMNS)).to_pylist()
    events: list[EligibleEvent] = []
    summaries = {
        estimator: {
            "candidate_count": 0,
            "eligible_count": 0,
            "realized_touchdown_count": 0,
            "exclusion_reason_counts": Counter(),
        }
        for estimator in ESTIMATORS
    }
    regular_rows = 0
    postseason_rows = 0
    for row in rows:
        if row["season_type"] != "REG":
            postseason_rows += 1
            continue
        regular_rows += 1
        candidate_estimators: list[str] = []
        rush_flag = _explicit_flag(row["rush_attempt"])
        pass_flag = _explicit_flag(row["pass_attempt"])
        if rush_flag:
            candidate_estimators.append("rush")
        if pass_flag:
            candidate_estimators.append("pass_target")
        for estimator in candidate_estimators:
            summary = summaries[estimator]
            summary["candidate_count"] += 1
            reasons: list[str] = []
            expected_play_type = "run" if estimator == "rush" else "pass"
            if row["play_type"] != expected_play_type:
                reasons.append("B07_EXCLUDE_UNSUPPORTED_OPPORTUNITY_TYPE")
            if rush_flag and pass_flag:
                reasons.append("B07_EXCLUDE_CONFLICTING_OPPORTUNITY_FLAGS")
            logical_no_play = normalize_no_play(row)
            if logical_no_play == "true":
                reasons.append("B07_EXCLUDE_LOGICAL_NO_PLAY")
            elif logical_no_play == "unknown":
                reasons.append("B07_EXCLUDE_LOGICAL_NO_PLAY_UNKNOWN")
            if _explicit_flag(row["penalty"]):
                reasons.append("B07_EXCLUDE_PENALIZED_EVENT")
            if _explicit_flag(row["aborted_play"]):
                reasons.append("B07_EXCLUDE_INELIGIBLE_EVENT")
            if _explicit_flag(row["two_point_attempt"]):
                reasons.append("B07_EXCLUDE_TWO_POINT_ATTEMPT")
            if estimator == "pass_target":
                if _explicit_flag(row["sack"]):
                    reasons.append("B07_EXCLUDE_SACK")
                if _explicit_flag(row["qb_spike"]):
                    reasons.append("B07_EXCLUDE_QB_SPIKE")

            canonical_field = (
                "rusher_player_id" if estimator == "rush" else "receiver_player_id"
            )
            alternate_field = "rusher_id" if estimator == "rush" else "receiver_id"
            canonical_id = _nonempty_string(row[canonical_field])
            alternate_id = _nonempty_string(row[alternate_field])
            if canonical_id is None:
                code = (
                    "B07_EXCLUDE_MISSING_RUSHER_ID"
                    if estimator == "rush"
                    else "B07_EXCLUDE_MISSING_INTENDED_RECEIVER_ID"
                )
                reasons.append(code)
            elif alternate_id is not None and alternate_id != canonical_id:
                code = (
                    "B07_EXCLUDE_AMBIGUOUS_RUSHER_ID"
                    if estimator == "rush"
                    else "B07_EXCLUDE_AMBIGUOUS_INTENDED_RECEIVER_ID"
                )
                reasons.append(code)

            type_label_field = (
                "rush_touchdown" if estimator == "rush" else "pass_touchdown"
            )
            type_label = _binary_label(row[type_label_field])
            generic_label = _binary_label(row["touchdown"])
            if row[type_label_field] is None or row["touchdown"] is None:
                reasons.append("B07_EXCLUDE_MISSING_TOUCHDOWN_LABEL")
            elif type_label is None or generic_label is None:
                reasons.append("B07_EXCLUDE_INVALID_TOUCHDOWN_LABEL")
            elif type_label != generic_label:
                reasons.append("B07_EXCLUDE_TOUCHDOWN_LABEL_CONTRADICTION")
            if type_label == 1:
                scorer_id = _nonempty_string(row["td_player_id"])
                if scorer_id is None:
                    reasons.append("B07_EXCLUDE_TOUCHDOWN_PLAYER_ID_MISSING")
                elif canonical_id is not None and scorer_id != canonical_id:
                    reasons.append("B07_EXCLUDE_TOUCHDOWN_PLAYER_ID_MISMATCH")

            features, band, context_reasons = _validate_context(row, contract)
            reasons.extend(context_reasons)
            game_id = _nonempty_string(row["game_id"])
            play_id_int = _integral(row["play_id"])
            if game_id is None or play_id_int is None:
                reasons.append("B07_EXCLUDE_SOURCE_EVENT_LOCATOR_INVALID")

            unique_reasons = tuple(dict.fromkeys(reasons))
            summary["exclusion_reason_counts"].update(unique_reasons)
            if unique_reasons:
                continue
            assert canonical_id is not None
            assert type_label is not None
            assert band is not None
            assert game_id is not None
            assert play_id_int is not None
            summary["eligible_count"] += 1
            summary["realized_touchdown_count"] += type_label
            events.append(
                EligibleEvent(
                    season=spec.season,
                    estimator=estimator,
                    game_id=game_id,
                    play_id=str(play_id_int),
                    source_event_locator=f"{spec.season}:{game_id}:{play_id_int}",
                    yardline_band=band,
                    goal_to_go=bool(features["goal_to_go"]),
                    down=int(features["down"]),
                    label=type_label,
                    features=features,
                    payload_sha256=identity.payload_sha256,
                    manifest_sha256=identity.manifest_sha256,
                )
            )

    output: dict[str, Any] = {
        "season": spec.season,
        "raw_row_count": len(rows),
        "regular_season_row_count": regular_rows,
        "postseason_row_count": postseason_rows,
        "estimators": {},
    }
    for estimator in ESTIMATORS:
        summary = summaries[estimator]
        candidate_count = summary["candidate_count"]
        exclusion_counts = dict(sorted(summary["exclusion_reason_counts"].items()))
        output["estimators"][estimator] = {
            "candidate_count": candidate_count,
            "eligible_count": summary["eligible_count"],
            "excluded_candidate_count": candidate_count - summary["eligible_count"],
            "realized_touchdown_count": summary["realized_touchdown_count"],
            "realized_touchdown_rate": (
                summary["realized_touchdown_count"] / summary["eligible_count"]
                if summary["eligible_count"]
                else None
            ),
            "exclusion_reason_counts": exclusion_counts,
            "exclusion_reason_rates": {
                code: count / candidate_count if candidate_count else 0.0
                for code, count in exclusion_counts.items()
            },
        }
    return sorted(events, key=lambda item: (item.estimator, item.source_event_locator)), output


def _cell_key(event: EligibleEvent, hierarchy: tuple[str, ...]) -> tuple[Any, ...]:
    values = {
        "opportunity_type": event.estimator,
        "yardline_band": event.yardline_band,
        "goal_to_go": event.goal_to_go,
        "down": event.down,
        "opportunity_type_global_rate": event.estimator,
    }
    return tuple(values[field] for field in hierarchy)


def build_lookup_tables(
    development_events: Sequence[EligibleEvent], contract: Mapping[str, Any]
) -> LookupBundle:
    """Build frozen count/rate cells using development seasons only."""
    seasons = {event.season for event in development_events}
    if not seasons or not seasons <= set(DEVELOPMENT_SEASONS):
        _fail(
            "B07_HOLDOUT_DEVELOPMENT_LEAKAGE",
            f"lookup seasons={sorted(seasons)} expected subset of {DEVELOPMENT_SEASONS}",
        )
    baseline = contract["b07_v0_1_contract"]["contextual_baseline"]
    threshold = baseline["min_cell_support_opportunities"]
    hierarchy = tuple(tuple(level) for level in baseline["backoff_hierarchy"])
    cells: dict[tuple[str, ...], dict[tuple[Any, ...], list[int]]] = {
        level: defaultdict(lambda: [0, 0]) for level in hierarchy
    }
    for event in development_events:
        for level in hierarchy:
            counts = cells[level][_cell_key(event, level)]
            counts[0] += 1
            counts[1] += event.label
    frozen_cells = {
        level: {key: (value[0], value[1]) for key, value in values.items()}
        for level, values in cells.items()
    }
    return LookupBundle(threshold=threshold, hierarchy=hierarchy, cells=frozen_cells)


def serialize_lookup(bundle: LookupBundle) -> dict[str, Any]:
    levels = []
    for index, level in enumerate(bundle.hierarchy):
        rows = []
        for key, (opportunities, touchdowns) in sorted(
            bundle.cells[level].items(), key=lambda item: tuple(map(str, item[0]))
        ):
            rows.append(
                {
                    "cell_keys": dict(zip(level, key, strict=True)),
                    "development_opportunity_count": opportunities,
                    "development_touchdown_count": touchdowns,
                    "touchdown_rate": touchdowns / opportunities,
                    "meets_support_threshold": opportunities >= bundle.threshold,
                }
            )
        levels.append(
            {
                "lookup_level": index,
                "key_fields": list(level),
                "cells": rows,
            }
        )
    return {
        "baseline_version": BASELINE_VERSION,
        "support_threshold": bundle.threshold,
        "hierarchy": [list(level) for level in bundle.hierarchy],
        "levels": levels,
    }


def score_holdout_events(
    holdout_events: Sequence[EligibleEvent],
    lookup: LookupBundle,
    *,
    input_snapshot_id: str,
    contract_sha256: str,
    as_of_timestamp: str,
) -> list[dict[str, Any]]:
    """Apply the first supported development-only cell to 2025 events."""
    if not holdout_events or {event.season for event in holdout_events} != {HOLDOUT_SEASON}:
        _fail(
            "B07_HOLDOUT_EVALUATION_SEASON_INVALID",
            f"observed seasons={sorted({event.season for event in holdout_events})}",
        )
    scored: list[dict[str, Any]] = []
    for event in holdout_events:
        selected: tuple[int, tuple[str, ...], tuple[Any, ...], int, int] | None = None
        for index, level in enumerate(lookup.hierarchy):
            key = _cell_key(event, level)
            opportunities, touchdowns = lookup.cells[level].get(key, (0, 0))
            if opportunities >= lookup.threshold:
                selected = (index, level, key, opportunities, touchdowns)
                break
        if selected is None:
            _fail(
                "B07_BASELINE_BACKOFF_EXHAUSTED",
                f"event={event.source_event_locator}",
            )
        index, level, key, opportunities, touchdowns = selected
        scored.append(
            {
                "estimator_type": event.estimator,
                "lookup_level_selected": index,
                "lookup_level_fields": list(level),
                "lookup_cell_keys": dict(zip(level, key, strict=True)),
                "development_opportunity_count": opportunities,
                "development_touchdown_count": touchdowns,
                "baseline_predicted_probability": touchdowns / opportunities,
                "realized_touchdown": event.label,
                "source_event_locator": event.source_event_locator,
                "game_id": event.game_id,
                "yardline_band": event.yardline_band,
                "features": event.features,
                "b06_payload_sha256": event.payload_sha256,
                "b06_manifest_sha256": event.manifest_sha256,
                "input_snapshot_id": input_snapshot_id,
                "contract_version": "0.1.0",
                "contract_sha256": contract_sha256,
                "as_of_timestamp": as_of_timestamp,
                "reason_codes": [],
                "known_limitations": list(KNOWN_LIMITATIONS),
            }
        )
    return sorted(scored, key=lambda row: (row["estimator_type"], row["source_event_locator"]))


def _metric_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    touchdowns = sum(int(row["realized_touchdown"]) for row in rows)
    predicted = sum(float(row["baseline_predicted_probability"]) for row in rows)
    squared = sum(
        (float(row["baseline_predicted_probability"]) - int(row["realized_touchdown"]))
        ** 2
        for row in rows
    )
    return {
        "event_count": count,
        "distinct_game_count": len({str(row["game_id"]) for row in rows}),
        "realized_touchdown_count": touchdowns,
        "realized_touchdown_rate": touchdowns / count if count else None,
        "mean_predicted_probability": predicted / count if count else None,
        "brier_score": squared / count if count else None,
        "observed_minus_expected_touchdowns": touchdowns - predicted,
    }


def _reliability(rows: Sequence[Mapping[str, Any]], requested_bins: int) -> dict[str, Any]:
    ordered = sorted(
        rows,
        key=lambda row: (
            float(row["baseline_predicted_probability"]),
            str(row["source_event_locator"]),
        ),
    )
    actual_bins = min(requested_bins, len(ordered))
    table = []
    ece = 0.0
    for index in range(actual_bins):
        start = index * len(ordered) // actual_bins
        end = (index + 1) * len(ordered) // actual_bins
        members = ordered[start:end]
        summary = _metric_summary(members)
        gap = summary["realized_touchdown_rate"] - summary["mean_predicted_probability"]
        ece += len(members) / len(ordered) * abs(gap)
        table.append(
            {
                "bin": index + 1,
                "event_count": len(members),
                "min_prediction": min(
                    float(row["baseline_predicted_probability"]) for row in members
                ),
                "max_prediction": max(
                    float(row["baseline_predicted_probability"]) for row in members
                ),
                "mean_prediction": summary["mean_predicted_probability"],
                "observed_touchdown_rate": summary["realized_touchdown_rate"],
                "observed_minus_expected_rate": gap,
            }
        )
    return {
        "method": "equal_frequency_quantiles",
        "requested_bins": requested_bins,
        "actual_returned_bin_count": actual_bins,
        "ece": ece,
        "bins": table,
    }


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _bootstrap(
    rows: Sequence[Mapping[str, Any]], *, resamples: int, seed: int
) -> dict[str, Any]:
    per_game: dict[str, list[tuple[float, int]]] = defaultdict(list)
    for row in rows:
        per_game[str(row["game_id"])].append(
            (
                float(row["baseline_predicted_probability"]),
                int(row["realized_touchdown"]),
            )
        )
    game_ids = sorted(per_game)
    aggregates = {}
    for game_id, values in per_game.items():
        aggregates[game_id] = (
            len(values),
            sum((prediction - label) ** 2 for prediction, label in values),
            sum(label - prediction for prediction, label in values),
        )
    generator = random.Random(seed)
    brier_distribution: list[float] = []
    observed_minus_expected_distribution: list[float] = []
    for _ in range(resamples):
        sampled = [game_ids[generator.randrange(len(game_ids))] for _ in game_ids]
        count = sum(aggregates[game_id][0] for game_id in sampled)
        squared = sum(aggregates[game_id][1] for game_id in sampled)
        difference = sum(aggregates[game_id][2] for game_id in sampled)
        brier_distribution.append(squared / count)
        observed_minus_expected_distribution.append(difference)
    return {
        "method": "paired_bootstrap",
        "cluster_unit": "game_id",
        "resamples": resamples,
        "confidence_interval": 0.95,
        "seed": seed,
        "baseline_brier_distribution": brier_distribution,
        "baseline_brier_mean": sum(brier_distribution) / len(brier_distribution),
        "baseline_brier_confidence_interval": [
            _percentile(brier_distribution, 0.025),
            _percentile(brier_distribution, 0.975),
        ],
        "observed_minus_expected_touchdowns_distribution": observed_minus_expected_distribution,
        "observed_minus_expected_touchdowns_confidence_interval": [
            _percentile(observed_minus_expected_distribution, 0.025),
            _percentile(observed_minus_expected_distribution, 0.975),
        ],
        "candidate_vs_baseline_delta": "not_applicable_until_candidate_phase",
    }


def _cohort_metrics(
    rows: Sequence[Mapping[str, Any]], support_threshold: int
) -> list[dict[str, Any]]:
    cohort_rows: list[dict[str, Any]] = []
    definitions = {
        "opportunity_type": lambda row: str(row["estimator_type"]),
        "yardline_band": lambda row: str(row["yardline_band"]),
        "goal_to_go": lambda row: str(row["features"]["goal_to_go"]).lower(),
        "down_when_support_eligible": lambda row: str(row["features"]["down"]),
    }
    for definition, getter in definitions.items():
        grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(str(row["estimator_type"]), getter(row))].append(row)
        for (estimator, value), members in sorted(grouped.items()):
            summary = _metric_summary(members)
            meets_opportunity_support = len(members) >= support_threshold
            status = (
                "diagnostic_only_distinct_game_threshold_undeclared"
                if meets_opportunity_support
                else "diagnostic_only_below_opportunity_support"
            )
            cohort_rows.append(
                {
                    "cohort_definition": definition,
                    "estimator_type": estimator,
                    "cohort_value": value,
                    **summary,
                    "minimum_opportunity_support": support_threshold,
                    "meets_opportunity_support": meets_opportunity_support,
                    "minimum_distinct_game_support": None,
                    "status": status,
                    "calibration_pass_claim_allowed": False,
                }
            )
    return cohort_rows


def evaluate_holdout(
    scored_rows: Sequence[Mapping[str, Any]],
    eligibility: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Calculate frozen baseline-only 2025 diagnostics without tuning."""
    protocol = contract["b07_v0_1_contract"]["validation_protocol"]
    scopes = {
        "rush": [row for row in scored_rows if row["estimator_type"] == "rush"],
        "pass_target": [
            row for row in scored_rows if row["estimator_type"] == "pass_target"
        ],
        "combined": list(scored_rows),
    }
    baseline_metrics = {name: _metric_summary(rows) for name, rows in scopes.items()}
    reliability = {
        name: _reliability(rows, protocol["reliability_binning"]["requested_bins"])
        for name, rows in scopes.items()
    }
    bootstrap = {
        name: _bootstrap(
            rows,
            resamples=protocol["resamples"],
            seed=bootstrap_seed + index,
        )
        for index, (name, rows) in enumerate(scopes.items())
    }
    usage = {}
    for name, rows in scopes.items():
        counts = Counter(int(row["lookup_level_selected"]) for row in rows)
        usage[name] = {
            str(level): {
                "count": count,
                "rate": count / len(rows),
            }
            for level, count in sorted(counts.items())
        }
    threshold = contract["b07_v0_1_contract"]["contextual_baseline"][
        "min_cell_support_opportunities"
    ]
    return {
        "baseline_metrics": baseline_metrics,
        "reliability_tables": reliability,
        "ece": {name: value["ece"] for name, value in reliability.items()},
        "bootstrap": bootstrap,
        "brier_by_material_cohort": _cohort_metrics(scored_rows, threshold),
        "holdout_exclusions": eligibility[str(HOLDOUT_SEASON)]["estimators"],
        "lookup_level_usage": usage,
        "limitations": list(KNOWN_LIMITATIONS),
        "candidate_comparison": "not_applicable_until_candidate_phase",
    }


def _write_bytes(path: Path, value: bytes) -> dict[str, Any]:
    path.write_bytes(value)
    return {"sha256": sha256_bytes(value), "bytes": len(value)}


def _review_report(artifact: Mapping[str, Any]) -> str:
    metrics = artifact["evaluation"]["baseline_metrics"]
    lines = [
        "# B-07 v0.1 contextual baseline validation",
        "",
        f"- Result: `{artifact['result']}`",
        f"- Run ID: `{artifact['run_id']}`",
        f"- Input snapshot: `{artifact['source_inputs']['input_snapshot_ids'][0]}`",
        f"- Contract SHA-256: `{artifact['contract']['sha256']}`",
        "- Development seasons: `2023, 2024`",
        "- Final holdout: `2025` (evaluation only)",
        "- Candidate comparison: `not_applicable_until_candidate_phase`",
        "",
        "## Baseline metrics",
        "",
        "| Scope | Events | Games | TDs | TD rate | Mean p | Brier | O-E TD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scope in ("rush", "pass_target", "combined"):
        value = metrics[scope]
        lines.append(
            f"| {scope} | {value['event_count']} | {value['distinct_game_count']} | "
            f"{value['realized_touchdown_count']} | {value['realized_touchdown_rate']:.8f} | "
            f"{value['mean_predicted_probability']:.8f} | {value['brier_score']:.8f} | "
            f"{value['observed_minus_expected_touchdowns']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- `{item}`" for item in artifact["evaluation"]["limitations"]],
            "",
            "No candidate estimator, production xTD artifact, current pointer, endpoint, or",
            "recommendation behavior is authorized by this validation package.",
            "",
        ]
    )
    return "\n".join(lines)


def _validate_output_root(path: Path) -> None:
    forbidden = {"current.json", "latest", "recommendation", "projection"}
    lowered = {part.lower() for part in path.parts}
    collision = sorted(forbidden & lowered)
    if collision:
        _fail("B07_ARTIFACT_PATH_PROHIBITED", f"path={path} forbidden={collision}")
    if path.exists():
        _fail("B07_ARTIFACT_IMMUTABILITY_COLLISION", f"path already exists: {path}")


def write_validation_artifact(
    output_root: str | Path,
    artifact: dict[str, Any],
    lookup_payload: Mapping[str, Any],
    scored_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Atomically publish one immutable local validation package, without a pointer."""
    root = Path(output_root).resolve()
    _validate_output_root(root)
    root.parent.mkdir(parents=True, exist_ok=True)
    temporary = root.with_name(f".{root.name}.tmp-{uuid.uuid4().hex}")
    temporary.mkdir()
    try:
        files: dict[str, dict[str, Any]] = {}
        files["lookup-tables.json"] = _write_bytes(
            temporary / "lookup-tables.json", _json_bytes(lookup_payload)
        )
        scored_bytes = b"".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
            for row in scored_rows
        )
        files["scored-events.jsonl"] = _write_bytes(
            temporary / "scored-events.jsonl", scored_bytes
        )
        files["metrics.json"] = _write_bytes(
            temporary / "metrics.json", _json_bytes(artifact["evaluation"])
        )
        report = _review_report(artifact).encode("utf-8")
        files["review-report.md"] = _write_bytes(temporary / "review-report.md", report)
        manifest = {
            "artifact_version": ARTIFACT_VERSION,
            "artifact_id": artifact["artifact_id"],
            "run_id": artifact["run_id"],
            "created_at": artifact["created_at"],
            "immutable": True,
            "files": files,
            "current_pointer_created": False,
        }
        manifest_bytes = _json_bytes(manifest)
        manifest_info = _write_bytes(temporary / "manifest.json", manifest_bytes)
        artifact["artifact_integrity"] = {
            "payload_digests": {name: value["sha256"] for name, value in files.items()},
            "manifest_digest": manifest_info["sha256"],
            "report_digest": files["review-report.md"]["sha256"],
            "metrics_digest": files["metrics.json"]["sha256"],
        }
        artifact_bytes = _json_bytes({"b07_validation_artifact": artifact})
        artifact_info = _write_bytes(
            temporary / "validation-artifact.json", artifact_bytes
        )
        os.replace(temporary, root)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return {
        "root": str(root),
        "files": {
            **files,
            "manifest.json": manifest_info,
            "validation-artifact.json": artifact_info,
        },
    }


def inspect_validation_artifact(root: str | Path) -> dict[str, Any]:
    """Read and verify an immutable package without mutation."""
    path = Path(root).resolve()
    manifest_path = path / "manifest.json"
    artifact_path = path / "validation-artifact.json"
    manifest = _load_json_mapping(manifest_path, "B07_ARTIFACT_MANIFEST_INVALID")
    package = _load_json_mapping(artifact_path, "B07_ARTIFACT_PACKAGE_INVALID")
    for name, expected in manifest.get("files", {}).items():
        actual_path = path / name
        if not actual_path.is_file() or sha256_file(actual_path) != expected.get("sha256"):
            _fail("B07_ARTIFACT_FILE_DIGEST_MISMATCH", f"file={actual_path}")
    artifact = package.get("b07_validation_artifact")
    if not isinstance(artifact, dict):
        _fail("B07_ARTIFACT_PACKAGE_INVALID", "missing b07_validation_artifact")
    if artifact.get("artifact_integrity", {}).get("manifest_digest") != sha256_file(
        manifest_path
    ):
        _fail("B07_ARTIFACT_MANIFEST_DIGEST_MISMATCH", f"path={manifest_path}")
    evaluation = artifact.get("evaluation", {})
    return {
        "result": artifact.get("result"),
        "run_id": artifact.get("run_id"),
        "input_snapshot_id": artifact.get("source_inputs", {}).get("input_snapshot_ids", [None])[0],
        "manifest_sha256": sha256_file(manifest_path),
        "validation_artifact_sha256": sha256_file(artifact_path),
        "artifact_files": manifest.get("files"),
        "source_inputs": artifact.get("source_inputs"),
        "split": artifact.get("split"),
        "eligibility": artifact.get("eligibility"),
        "metrics": evaluation.get("baseline_metrics"),
        "reliability": {
            scope: {
                "method": value.get("method"),
                "requested_bins": value.get("requested_bins"),
                "actual_returned_bin_count": value.get("actual_returned_bin_count"),
                "ece": value.get("ece"),
            }
            for scope, value in evaluation.get("reliability_tables", {}).items()
        },
        "bootstrap": {
            scope: {
                "method": value.get("method"),
                "cluster_unit": value.get("cluster_unit"),
                "resamples": value.get("resamples"),
                "confidence_interval": value.get("confidence_interval"),
                "baseline_brier_confidence_interval": value.get(
                    "baseline_brier_confidence_interval"
                ),
                "observed_minus_expected_touchdowns_confidence_interval": value.get(
                    "observed_minus_expected_touchdowns_confidence_interval"
                ),
                "candidate_vs_baseline_delta": value.get("candidate_vs_baseline_delta"),
            }
            for scope, value in evaluation.get("bootstrap", {}).items()
        },
        "lookup_level_usage": evaluation.get("lookup_level_usage"),
        "material_cohort_status_counts": dict(
            sorted(
                Counter(
                    row.get("status")
                    for row in evaluation.get("brier_by_material_cohort", [])
                ).items()
            )
        ),
        "limitations": evaluation.get("limitations"),
    }


def what_if(
    contract_path: str | Path,
    sources: Sequence[SourceSpec],
    prospective_output_root: str | Path,
) -> dict[str, Any]:
    """Validate contract and B-06 identities without labels or artifact writes."""
    contract = load_contract_checked(contract_path)
    root = Path(prospective_output_root).resolve()
    _validate_output_root(root)
    identities = [validate_source_spec(spec, contract) for spec in sources]
    if tuple(sorted(identity.season for identity in identities)) != EXPECTED_SEASONS:
        _fail("B07_SOURCE_SEASON_SET_MISMATCH", f"sources={[item.season for item in identities]}")
    return {
        "status": "WHAT_IF_PASS",
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "source_payload_digests": {
            str(item.season): item.payload_sha256 for item in identities
        },
        "prospective_output_root": str(root),
        "artifact_written": False,
        "holdout_label_reads": 0,
    }


def run_baseline_validation(
    *,
    contract_path: str | Path,
    sources: Sequence[SourceSpec],
    output_root: str | Path,
    repository_sha: str,
    repository_worktree: str,
    run_id: str,
) -> dict[str, Any]:
    """Execute one baseline-only development/evaluation and immutable write."""
    contract = load_contract_checked(contract_path)
    identities = [validate_source_spec(spec, contract) for spec in sources]
    identities.sort(key=lambda item: item.season)
    specs = {spec.season: spec for spec in sources}
    identity_by_season = {identity.season: identity for identity in identities}
    if tuple(identity_by_season) != EXPECTED_SEASONS:
        _fail("B07_SOURCE_SEASON_SET_MISMATCH", f"sources={list(identity_by_season)}")
    snapshot_id = source_snapshot_id(identities, EXPECTED_CONTRACT_SHA256)
    as_of_timestamp = max(identity.retrieved_at_utc for identity in identities)

    all_events: dict[int, list[EligibleEvent]] = {}
    eligibility: dict[str, Any] = {}
    for season in DEVELOPMENT_SEASONS:
        events, summary = read_eligible_events(
            specs[season], identity_by_season[season], contract, access_mode="development"
        )
        all_events[season] = events
        eligibility[str(season)] = summary
    holdout_events, holdout_summary = read_eligible_events(
        specs[HOLDOUT_SEASON],
        identity_by_season[HOLDOUT_SEASON],
        contract,
        access_mode="evaluation",
    )
    all_events[HOLDOUT_SEASON] = holdout_events
    eligibility[str(HOLDOUT_SEASON)] = holdout_summary

    development_events = [
        event for season in DEVELOPMENT_SEASONS for event in all_events[season]
    ]
    lookup = build_lookup_tables(development_events, contract)
    scored_rows = score_holdout_events(
        holdout_events,
        lookup,
        input_snapshot_id=snapshot_id,
        contract_sha256=EXPECTED_CONTRACT_SHA256,
        as_of_timestamp=as_of_timestamp,
    )
    seed = int(snapshot_id[:16], 16)
    evaluation = evaluate_holdout(
        scored_rows,
        eligibility,
        contract,
        bootstrap_seed=seed,
    )
    created_at = utc_now()
    artifact = {
        "artifact_version": ARTIFACT_VERSION,
        "artifact_id": f"{ARTIFACT_VERSION}:{run_id}",
        "run_id": run_id,
        "created_at": created_at,
        "as_of_timestamp": as_of_timestamp,
        "result": "FRESH_SUCCESS_PENDING_REVIEW",
        "repository": {
            "checkout_sha": repository_sha,
            "worktree": repository_worktree,
        },
        "contract": {
            "path": "contracts/projections/b07_v0_1_contract.yaml",
            "schema_version": "0.1.0",
            "sha256": EXPECTED_CONTRACT_SHA256,
        },
        "source_inputs": {
            "input_snapshot_ids": [snapshot_id],
            "accepted_payload_digests": {
                str(item.season): item.payload_sha256 for item in identities
            },
            "manifest_digests": {
                str(item.season): item.manifest_sha256 for item in identities
            },
            "pointer_digests": {
                str(item.season): item.pointer_sha256 for item in identities
            },
            "parser_versions": {
                str(item.season): item.parser_version for item in identities
            },
            "normalization_versions": {
                str(item.season): item.normalization_version for item in identities
            },
            "canonical_identity_mapping_versions": {
                str(item.season): item.canonical_identity_mapping_version
                for item in identities
            },
            "identities": [asdict(item) for item in identities],
        },
        "split": {
            "development_seasons": list(DEVELOPMENT_SEASONS),
            "holdout_season": HOLDOUT_SEASON,
            "holdout_access_mode": "evaluation_only",
            "holdout_fitting_access": False,
        },
        "baseline": {
            "version": BASELINE_VERSION,
            "estimators": list(ESTIMATORS),
            "support_threshold": lookup.threshold,
            "backoff_hierarchy": [list(level) for level in lookup.hierarchy],
            "development_event_counts": {
                estimator: sum(
                    1 for event in development_events if event.estimator == estimator
                )
                for estimator in ESTIMATORS
            },
        },
        "eligibility": {
            "counts_by_season_estimator": eligibility,
            "exclusions_by_season_estimator_reason": {
                season: {
                    estimator: summary["estimators"][estimator]["exclusion_reason_counts"]
                    for estimator in ESTIMATORS
                }
                for season, summary in eligibility.items()
            },
        },
        "evaluation": evaluation,
        "local_inspection": {
            "command": f"python -B tools/run_b07_baseline.py --inspect \"{Path(output_root).resolve()}\"",
            "read_only": True,
        },
        "promotion": {
            "production_promotion_authorized": False,
            "current_pointer_created": False,
            "recommendation_behavior_authorized": False,
        },
    }
    write_result = write_validation_artifact(
        output_root,
        artifact,
        serialize_lookup(lookup),
        scored_rows,
    )
    inspection = inspect_validation_artifact(output_root)
    return {
        "status": artifact["result"],
        "run_id": run_id,
        "input_snapshot_id": snapshot_id,
        "artifact": write_result,
        "inspection": inspection,
        "baseline_metrics": evaluation["baseline_metrics"],
        "bootstrap_summary": {
            scope: {
                "baseline_brier_confidence_interval": value[
                    "baseline_brier_confidence_interval"
                ],
                "observed_minus_expected_touchdowns_confidence_interval": value[
                    "observed_minus_expected_touchdowns_confidence_interval"
                ],
                "candidate_vs_baseline_delta": value["candidate_vs_baseline_delta"],
            }
            for scope, value in evaluation["bootstrap"].items()
        },
    }
