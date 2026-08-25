"""Deterministic, non-production validation for the frozen B-07 v0.1 contract.

This module validates contract and synthetic boundary claims only. It does not read
B-06 payloads, fit or score estimators, calculate xTD, or write B-07 artifacts.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml


CONTRACT_ROOT_KEY = "b07_v0_1_contract"
DEFAULT_CONTRACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "projections"
    / "b07_v0_1_contract.yaml"
)

EXPECTED_PAYLOAD_DIGESTS = {
    "2023": "bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776",
    "2024": "3fd2896bc0b911b615142d2f1fabae54a4bbba5ab7b73b28187b118ef8af6a3b",
    "2025": "c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29",
}
EXPECTED_FEATURES = (
    "yardline_100",
    "down",
    "ydstogo",
    "goal_to_go",
    "quarter",
    "game_seconds_remaining",
    "score_differential",
)
EXPECTED_PROHIBITED_PREDICTORS = (
    "player_id",
    "posteam_id",
    "team_strength_proxy",
    "player_history",
    "realized_touchdown",
    "yards_gained",
    "epa",
    "wpa",
    "success",
    "fantasy_points",
    "post_play_scores",
    "future_game_information",
    "season_end_aggregates",
)
EXPECTED_BACKOFF_HIERARCHY = (
    ("opportunity_type", "yardline_band", "goal_to_go", "down"),
    ("opportunity_type", "yardline_band", "goal_to_go"),
    ("opportunity_type", "yardline_band"),
    ("opportunity_type_global_rate",),
)
DEVELOPMENT_PURPOSES = frozenset(
    {
        "fitting",
        "lookup_construction",
        "preprocessing",
        "category_inference",
        "domain_inference",
        "aggregation",
        "baseline_training",
    }
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_MISSING = object()


class B07ValidationError(ValueError):
    """A stable fail-closed B-07 reason code with field-level context."""

    def __init__(
        self,
        reason_code: str,
        field_path: str,
        actual: Any,
        expected: str,
    ) -> None:
        self.reason_code = reason_code
        self.field_path = field_path
        self.actual = actual
        self.expected = expected
        super().__init__(
            f"{reason_code} | field={field_path} | actual={actual!r} | expected={expected}"
        )


def _fail(reason_code: str, field_path: str, actual: Any, expected: str) -> None:
    raise B07ValidationError(reason_code, field_path, actual, expected)


def _mapping(value: Any, field_path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("B07_CONTRACT_STRUCTURE_INVALID", field_path, value, "a YAML mapping")
    return value


def _expect(
    mapping: Mapping[str, Any], field: str, expected: Any, *, prefix: str = ""
) -> None:
    actual = mapping.get(field, _MISSING)
    if actual != expected or type(actual) is not type(expected):
        field_path = f"{prefix}.{field}" if prefix else field
        _fail("B07_CONTRACT_FROZEN_VALUE_MISMATCH", field_path, actual, repr(expected))


def load_b07_contract(path: str | Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    """Safely load and validate the canonical frozen contract."""
    artifact_path = Path(path)
    with artifact_path.open("r", encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict):
        _fail("B07_CONTRACT_STRUCTURE_INVALID", "$", document, "a YAML mapping")
    validate_b07_contract(document)
    return document


def _contract(document: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(document.get(CONTRACT_ROOT_KEY, _MISSING), CONTRACT_ROOT_KEY)


def validate_b07_contract(document: Mapping[str, Any]) -> None:
    """Enforce the frozen values and contract-level kill switches."""
    if set(document) != {CONTRACT_ROOT_KEY}:
        _fail(
            "B07_CONTRACT_STRUCTURE_INVALID",
            "$",
            sorted(document),
            f"the sole root key {CONTRACT_ROOT_KEY!r}",
        )

    contract = _contract(document)
    _expect(contract, "schema_version", "0.1.0", prefix=CONTRACT_ROOT_KEY)
    _expect(contract, "status", "frozen_pending_tests", prefix=CONTRACT_ROOT_KEY)

    source_inputs = _mapping(
        contract.get("source_inputs", _MISSING), f"{CONTRACT_ROOT_KEY}.source_inputs"
    )
    _expect(source_inputs, "development_seasons", [2023, 2024], prefix="source_inputs")
    _expect(source_inputs, "final_out_of_time_holdout", 2025, prefix="source_inputs")
    _expect(
        source_inputs,
        "allowed_payload_digests",
        EXPECTED_PAYLOAD_DIGESTS,
        prefix="source_inputs",
    )
    _expect(contract, "estimators", ["rush", "pass_target"], prefix=CONTRACT_ROOT_KEY)

    features = _mapping(
        contract.get("feature_allowlist", _MISSING),
        f"{CONTRACT_ROOT_KEY}.feature_allowlist",
    )
    if tuple(features) != EXPECTED_FEATURES:
        _fail(
            "B07_CONTRACT_FEATURE_ALLOWLIST_MISMATCH",
            "feature_allowlist",
            tuple(features),
            repr(EXPECTED_FEATURES),
        )
    expected_feature_specs = {
        "yardline_100": {
            "type": "int",
            "source": "raw_b06_yardline_100",
            "timing": "pre_event",
            "required": True,
            "domain_policy": {
                "authoritative_domain": "observed_b06_domain_per_season",
                "unsupported_value_action": "exclude_with_reason_code",
                "exclusion_reason_code": "B07_EXCLUDE_INVALID_YARDLINE_100",
            },
        },
        "down": {
            "type": "int",
            "range": [1, 4],
            "source": "raw_b06_down",
            "timing": "pre_event",
            "required": True,
        },
        "ydstogo": {
            "type": "int",
            "minimum": 1,
            "source": "raw_b06_ydstogo",
            "timing": "pre_event",
            "required": True,
        },
        "goal_to_go": {
            "type": "bool",
            "source": "raw_b06_goal_to_go",
            "timing": "pre_event",
            "required": True,
            "fallback_derivation": {
                "status": "prohibited_in_v0_1_without_source_semantics_test",
                "reason": (
                    "goal_to_go must not be inferred from yardline_100 == ydstogo "
                    "by assumption"
                ),
            },
        },
        "quarter": {
            "type": "int",
            "range": [1, 5],
            "source": "raw_b06_quarter",
            "timing": "pre_event",
            "required": True,
        },
        "game_seconds_remaining": {
            "type": "int",
            "range": [0, 3600],
            "source": "raw_b06_game_seconds_remaining",
            "timing": "pre_event",
            "required": True,
        },
        "score_differential": {
            "type": "int",
            "source": "raw_b06_score_differential",
            "timing": "pre_event",
            "required": True,
        },
    }
    for name, expected in expected_feature_specs.items():
        if features[name] != expected:
            _fail(
                "B07_CONTRACT_FEATURE_POLICY_MISMATCH",
                f"feature_allowlist.{name}",
                features[name],
                repr(expected),
            )

    _expect(contract, "deferred_features", ["shotgun", "no_huddle"])
    _expect(
        contract,
        "prohibited_predictors",
        list(EXPECTED_PROHIBITED_PREDICTORS),
        prefix=CONTRACT_ROOT_KEY,
    )

    baseline = _mapping(
        contract.get("contextual_baseline", _MISSING), "contextual_baseline"
    )
    _expect(baseline, "separate_estimators", True, prefix="contextual_baseline")
    _expect(baseline, "fitting_seasons", [2023, 2024], prefix="contextual_baseline")
    _expect(baseline, "holdout_season", 2025, prefix="contextual_baseline")
    _expect(
        baseline,
        "grouping_features",
        ["yardline_band", "goal_to_go", "down"],
        prefix="contextual_baseline",
    )
    expected_bands = [[0, 5], [6, 10], [11, 20], [21, 40], [41, 60], [61, 80], [81, 99]]
    _expect(baseline, "yardline_bands", expected_bands, prefix="contextual_baseline")
    covered = [yard for lower, upper in expected_bands for yard in range(lower, upper + 1)]
    if covered != list(range(100)) or len(covered) != len(set(covered)):
        _fail(
            "B07_CONTRACT_YARDLINE_BANDS_INVALID",
            "contextual_baseline.yardline_bands",
            expected_bands,
            "non-overlapping inclusive coverage of 0..99",
        )
    _expect(
        baseline,
        "out_of_band_action",
        "exclude_with_reason_code",
        prefix="contextual_baseline",
    )
    _expect(
        baseline,
        "out_of_band_reason_code",
        "B07_EXCLUDE_INVALID_YARDLINE_BAND",
        prefix="contextual_baseline",
    )
    _expect(
        baseline,
        "min_cell_support_opportunities",
        30,
        prefix="contextual_baseline",
    )
    actual_backoff = baseline.get("backoff_hierarchy", _MISSING)
    if actual_backoff is _MISSING or tuple(tuple(row) for row in actual_backoff) != EXPECTED_BACKOFF_HIERARCHY:
        _fail(
            "B07_CONTRACT_BACKOFF_HIERARCHY_MISMATCH",
            "contextual_baseline.backoff_hierarchy",
            actual_backoff,
            repr(EXPECTED_BACKOFF_HIERARCHY),
        )
    _expect(
        baseline,
        "missing_context_action",
        "exclude_with_reason_code",
        prefix="contextual_baseline",
    )
    _expect(
        baseline,
        "excluded_context_must_be_reported",
        True,
        prefix="contextual_baseline",
    )

    validation = _mapping(
        contract.get("validation_protocol", _MISSING), "validation_protocol"
    )
    _expect(validation, "holdout_season", 2025, prefix="validation_protocol")
    _expect(validation, "primary_metric", "brier_score", prefix="validation_protocol")
    _expect(validation, "resampling_cluster_unit", "game_id", prefix="validation_protocol")

    access = _mapping(contract.get("access", _MISSING), "access")
    _expect(
        access,
        "v0_1",
        "immutable_validation_artifact_and_local_inspection",
        prefix="access",
    )
    _expect(access, "endpoint", "explicitly_out_of_scope", prefix="access")

    execution = _mapping(
        contract.get("execution_control", _MISSING), "execution_control"
    )
    _expect(execution, "one_run_stop_condition", True, prefix="execution_control")
    _expect(
        execution,
        "candidate_estimator_training",
        "out_of_scope_until_baseline_artifact_review",
        prefix="execution_control",
    )


def validate_feature_selection(
    document: Mapping[str, Any], requested_features: Iterable[str]
) -> tuple[str, ...]:
    """Accept only allowlisted pre-event names; reject prohibited or unknown names."""
    validate_b07_contract(document)
    contract = _contract(document)
    allowlisted = tuple(_mapping(contract["feature_allowlist"], "feature_allowlist"))
    prohibited = set(contract["prohibited_predictors"])
    requested = tuple(requested_features)
    for name in requested:
        if name in prohibited:
            _fail(
                "B07_FEATURE_PROHIBITED_PREDICTOR",
                "requested_features",
                name,
                "an allowlisted pre-event feature",
            )
        if name not in allowlisted:
            _fail(
                "B07_FEATURE_NOT_ALLOWLISTED",
                "requested_features",
                name,
                "an allowlisted pre-event feature",
            )
    return tuple(name for name in allowlisted if name in requested)


def select_pre_event_inputs(
    document: Mapping[str, Any], synthetic_event: Mapping[str, Any]
) -> dict[str, Any]:
    """Select only declared raw pre-event values from a bounded synthetic event."""
    validate_b07_contract(document)
    features = _mapping(_contract(document)["feature_allowlist"], "feature_allowlist")
    return {
        name: synthetic_event.get(_mapping(spec, f"feature_allowlist.{name}")["source"])
        for name, spec in features.items()
    }


def validate_goal_to_go_source(
    document: Mapping[str, Any], *, source: str, derivation: str | None = None
) -> None:
    """Fail closed on any non-raw goal-to-go source or proposed derivation."""
    validate_b07_contract(document)
    if source != "raw_b06_goal_to_go":
        _fail(
            "B07_GOAL_TO_GO_SOURCE_INVALID",
            "goal_to_go.source",
            source,
            "raw_b06_goal_to_go",
        )
    if derivation is not None:
        _fail(
            "B07_GOAL_TO_GO_DERIVATION_PROHIBITED",
            "goal_to_go.derivation",
            derivation,
            "no alternate derivation in v0.1",
        )


def _validate_digest(value: Any, field_path: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        _fail(
            "B07_SOURCE_DIGEST_MALFORMED",
            field_path,
            value,
            "a lowercase 64-character SHA-256 digest",
        )
    return value


def validate_b06_source_claim(
    document: Mapping[str, Any],
    *,
    season: int,
    declared_revision_digest: str,
    computed_payload_digest: str,
    manifest_revision_digest: str,
    payload_row_count: int,
    manifest_row_count: int,
    payload_event_count: int,
    manifest_event_count: int,
) -> None:
    """Validate synthetic B-06 identity/count claims without reading provider data."""
    validate_b07_contract(document)
    allowed = _contract(document)["source_inputs"]["allowed_payload_digests"]
    if str(season) not in allowed:
        _fail(
            "B07_SOURCE_SEASON_NOT_ALLOWED",
            "season",
            season,
            "one of 2023, 2024, or holdout-only 2025",
        )
    declared = _validate_digest(declared_revision_digest, "declared_revision_digest")
    computed = _validate_digest(computed_payload_digest, "computed_payload_digest")
    manifest = _validate_digest(manifest_revision_digest, "manifest_revision_digest")
    expected = allowed[str(season)]
    if declared != expected:
        _fail(
            "B07_SOURCE_SEASON_DIGEST_MISMATCH",
            "declared_revision_digest",
            declared,
            expected,
        )
    if computed != declared:
        _fail(
            "B07_SOURCE_PAYLOAD_DIGEST_MISMATCH",
            "computed_payload_digest",
            computed,
            declared,
        )
    if manifest != declared:
        _fail(
            "B07_SOURCE_MANIFEST_DIGEST_MISMATCH",
            "manifest_revision_digest",
            manifest,
            declared,
        )
    for field_path, value in (
        ("payload_row_count", payload_row_count),
        ("manifest_row_count", manifest_row_count),
        ("payload_event_count", payload_event_count),
        ("manifest_event_count", manifest_event_count),
    ):
        if type(value) is not int or value < 0:
            _fail(
                "B07_SOURCE_COUNT_INVALID",
                field_path,
                value,
                "a non-negative integer",
            )
    if payload_row_count != manifest_row_count:
        _fail(
            "B07_SOURCE_ROW_COUNT_MISMATCH",
            "manifest_row_count",
            manifest_row_count,
            str(payload_row_count),
        )
    if payload_event_count != manifest_event_count:
        _fail(
            "B07_SOURCE_EVENT_COUNT_MISMATCH",
            "manifest_event_count",
            manifest_event_count,
            str(payload_event_count),
        )


def validate_season_access(
    document: Mapping[str, Any],
    *,
    season: int,
    purpose: str,
    evaluation_mode: bool = False,
    labels_requested: bool = False,
) -> None:
    """Enforce development/holdout isolation; evaluation remains unimplemented."""
    validate_b07_contract(document)
    source_inputs = _contract(document)["source_inputs"]
    development = tuple(source_inputs["development_seasons"])
    holdout = source_inputs["final_out_of_time_holdout"]
    if season == holdout:
        if purpose != "holdout_evaluation" or evaluation_mode is not True:
            reason = (
                "B07_HOLDOUT_LABEL_ACCESS_PROHIBITED"
                if labels_requested
                else "B07_HOLDOUT_ISOLATION_REQUIRED"
            )
            _fail(
                reason,
                "season",
                season,
                "future explicit holdout_evaluation mode only",
            )
        return
    if season not in development:
        _fail(
            "B07_DEVELOPMENT_SEASON_NOT_ALLOWED",
            "season",
            season,
            "2023 or 2024",
        )
    if purpose not in DEVELOPMENT_PURPOSES or evaluation_mode:
        _fail(
            "B07_DEVELOPMENT_PURPOSE_NOT_ALLOWED",
            "purpose",
            purpose,
            f"one of {sorted(DEVELOPMENT_PURPOSES)!r} in development mode",
        )


def exclusion_reason_codes(
    document: Mapping[str, Any], synthetic_event: Mapping[str, Any]
) -> tuple[str, ...]:
    """Return stable reason codes for invalid synthetic opportunity metadata."""
    validate_b07_contract(document)
    contract = _contract(document)
    features = _mapping(contract["feature_allowlist"], "feature_allowlist")
    baseline = _mapping(contract["contextual_baseline"], "contextual_baseline")

    def in_declared_range(feature_name: str, value: Any) -> bool:
        policy = _mapping(features[feature_name], f"feature_allowlist.{feature_name}")
        lower, upper = policy["range"]
        return type(value) is int and lower <= value <= upper

    reasons: list[str] = []
    opportunity_type = synthetic_event.get("opportunity_type")
    if opportunity_type not in {"rush", "pass_target"}:
        reasons.append("B07_EXCLUDE_UNSUPPORTED_OPPORTUNITY_TYPE")

    yardline = synthetic_event.get("yardline_100")
    if yardline is None:
        reasons.append("B07_EXCLUDE_MISSING_YARDLINE_100")
    elif type(yardline) is not int:
        reasons.append("B07_EXCLUDE_INVALID_YARDLINE_100")
    elif not any(
        lower <= yardline <= upper for lower, upper in baseline["yardline_bands"]
    ):
        reasons.append("B07_EXCLUDE_INVALID_YARDLINE_BAND")

    down = synthetic_event.get("down")
    if not in_declared_range("down", down):
        reasons.append("B07_EXCLUDE_INVALID_DOWN")
    ydstogo = synthetic_event.get("ydstogo")
    ydstogo_policy = _mapping(features["ydstogo"], "feature_allowlist.ydstogo")
    if type(ydstogo) is not int or ydstogo < ydstogo_policy["minimum"]:
        reasons.append("B07_EXCLUDE_INVALID_YDSTOGO")
    if type(synthetic_event.get("goal_to_go")) is not bool:
        reasons.append("B07_EXCLUDE_MISSING_GOAL_TO_GO")
    quarter = synthetic_event.get("quarter")
    if not in_declared_range("quarter", quarter):
        reasons.append("B07_EXCLUDE_INVALID_QUARTER")
    seconds = synthetic_event.get("game_seconds_remaining")
    if not in_declared_range("game_seconds_remaining", seconds):
        reasons.append("B07_EXCLUDE_INVALID_GAME_SECONDS_REMAINING")
    if type(synthetic_event.get("score_differential")) is not int:
        reasons.append("B07_EXCLUDE_INVALID_SCORE_DIFFERENTIAL")

    identity = synthetic_event.get("player_identity")
    if identity is None:
        reasons.append("B07_EXCLUDE_MISSING_PLAYER_IDENTITY")
    elif synthetic_event.get("identity_ambiguous") is True:
        reasons.append("B07_EXCLUDE_AMBIGUOUS_PLAYER_IDENTITY")
    label = synthetic_event.get("touchdown_label")
    if label is None:
        reasons.append("B07_EXCLUDE_MISSING_TOUCHDOWN_LABEL")
    elif type(label) is not bool:
        reasons.append("B07_EXCLUDE_INVALID_TOUCHDOWN_LABEL")
    if synthetic_event.get("label_contradiction") is True:
        reasons.append("B07_EXCLUDE_TOUCHDOWN_LABEL_CONTRADICTION")
    if synthetic_event.get("two_point_attempt") is True:
        reasons.append("B07_EXCLUDE_TWO_POINT_ATTEMPT")
    logical_no_play = synthetic_event.get("logical_no_play")
    if logical_no_play is True:
        reasons.append("B07_EXCLUDE_LOGICAL_NO_PLAY")
    elif type(logical_no_play) is not bool:
        reasons.append("B07_EXCLUDE_LOGICAL_NO_PLAY_UNKNOWN")
    if synthetic_event.get("penalty") is True:
        reasons.append("B07_EXCLUDE_PENALIZED_EVENT")
    if synthetic_event.get("eligible_event") is not True:
        reasons.append("B07_EXCLUDE_INELIGIBLE_EVENT")
    return tuple(reasons)


def validate_execution_action(document: Mapping[str, Any], action: str) -> None:
    """Deny every B-07 execution action; this support is validation-only."""
    validate_b07_contract(document)
    reason_by_action = {
        "candidate_estimator_training": "B07_EXECUTION_BASELINE_REVIEW_REQUIRED",
        "baseline_calculation": "B07_EXECUTION_BASELINE_NOT_AUTHORIZED",
        "xtd_scoring": "B07_EXECUTION_XTD_SCORING_NOT_AUTHORIZED",
        "validation_artifact_write": "B07_EXECUTION_ARTIFACT_WRITE_NOT_AUTHORIZED",
        "endpoint_creation": "B07_EXECUTION_ENDPOINT_OUT_OF_SCOPE",
        "current_pointer_update": "B07_EXECUTION_CURRENT_POINTER_PROHIBITED",
        "promotion": "B07_EXECUTION_PROMOTION_PROHIBITED",
        "draft_live_recommendation": "B07_EXECUTION_RECOMMENDATION_PROHIBITED",
    }
    _fail(
        reason_by_action.get(action, "B07_EXECUTION_ACTION_NOT_AUTHORIZED"),
        "execution_action",
        action,
        "contract validation only",
    )
