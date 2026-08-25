from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from engine.contracts.b07_v0_1 import (
    DEVELOPMENT_PURPOSES,
    EXPECTED_BACKOFF_HIERARCHY,
    EXPECTED_PAYLOAD_DIGESTS,
    EXPECTED_PROHIBITED_PREDICTORS,
    B07ValidationError,
    exclusion_reason_codes,
    load_b07_contract,
    select_pre_event_inputs,
    validate_b06_source_claim,
    validate_b07_contract,
    validate_execution_action,
    validate_feature_selection,
    validate_goal_to_go_source,
    validate_season_access,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPOSITORY_ROOT / "contracts" / "projections" / "b07_v0_1_contract.yaml"


@pytest.fixture(scope="module")
def document() -> dict:
    return load_b07_contract(CONTRACT_PATH)


def _assert_reason(exc_info: pytest.ExceptionInfo[B07ValidationError], reason: str) -> None:
    assert exc_info.value.reason_code == reason
    assert reason in str(exc_info.value)


def _source_claim(season: int = 2023) -> dict:
    digest = EXPECTED_PAYLOAD_DIGESTS[str(season)]
    return {
        "season": season,
        "declared_revision_digest": digest,
        "computed_payload_digest": digest,
        "manifest_revision_digest": digest,
        "payload_row_count": 100,
        "manifest_row_count": 100,
        "payload_event_count": 60,
        "manifest_event_count": 60,
    }


def _valid_event() -> dict:
    return {
        "opportunity_type": "rush",
        "yardline_100": 10,
        "down": 2,
        "ydstogo": 4,
        "goal_to_go": False,
        "quarter": 2,
        "game_seconds_remaining": 1800,
        "score_differential": -3,
        "player_identity": "synthetic-player",
        "identity_ambiguous": False,
        "touchdown_label": False,
        "label_contradiction": False,
        "two_point_attempt": False,
        "logical_no_play": False,
        "penalty": False,
        "eligible_event": True,
    }


def test_contract_structure_and_immutable_split(document: dict) -> None:
    contract = document["b07_v0_1_contract"]
    sources = contract["source_inputs"]
    assert contract["schema_version"] == "0.1.0"
    assert contract["status"] == "frozen_pending_tests"
    assert sources["development_seasons"] == [2023, 2024]
    assert sources["final_out_of_time_holdout"] == 2025
    assert sources["allowed_payload_digests"] == EXPECTED_PAYLOAD_DIGESTS
    assert contract["estimators"] == ["rush", "pass_target"]
    assert contract["access"]["endpoint"] == "explicitly_out_of_scope"


def test_contract_validator_rejects_split_mutation(document: dict) -> None:
    changed = deepcopy(document)
    changed["b07_v0_1_contract"]["source_inputs"]["development_seasons"].append(2025)
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b07_contract(changed)
    _assert_reason(exc_info, "B07_CONTRACT_FROZEN_VALUE_MISMATCH")


def test_contract_validator_rejects_reversed_game_seconds_range(document: dict) -> None:
    changed = deepcopy(document)
    changed["b07_v0_1_contract"]["feature_allowlist"]["game_seconds_remaining"][
        "range"
    ] = [3600, 0]
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b07_contract(changed)
    _assert_reason(exc_info, "B07_CONTRACT_FEATURE_POLICY_MISMATCH")


def test_every_allowlisted_feature_is_typed_required_sourced_and_pre_event(document: dict) -> None:
    features = document["b07_v0_1_contract"]["feature_allowlist"]
    for name, policy in features.items():
        assert policy["timing"] == "pre_event", name
        assert policy["source"].startswith("raw_b06_"), name
        assert policy["type"] in {"int", "bool"}, name
        assert policy["required"] is True, name


@pytest.mark.parametrize("predictor", EXPECTED_PROHIBITED_PREDICTORS)
def test_prohibited_predictors_fail_closed(document: dict, predictor: str) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_feature_selection(document, ["yardline_100", predictor])
    _assert_reason(exc_info, "B07_FEATURE_PROHIBITED_PREDICTOR")


def test_unknown_predictor_fails_closed(document: dict) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_feature_selection(document, ["yardline_100", "synthetic_unknown"])
    _assert_reason(exc_info, "B07_FEATURE_NOT_ALLOWLISTED")


def test_post_play_perturbation_cannot_change_selected_inputs_or_validation(document: dict) -> None:
    event = {
        "raw_b06_yardline_100": 8,
        "raw_b06_down": 2,
        "raw_b06_ydstogo": 3,
        "raw_b06_goal_to_go": True,
        "raw_b06_quarter": 4,
        "raw_b06_game_seconds_remaining": 75,
        "raw_b06_score_differential": -4,
        "realized_touchdown": False,
        "yards_gained": 0,
        "epa": -0.2,
        "wpa": -0.01,
        "success": False,
        "fantasy_points": 0,
    }
    perturbed = dict(event)
    perturbed.update(
        realized_touchdown=True,
        yards_gained=99,
        epa=8.5,
        wpa=1.0,
        success=True,
        fantasy_points=99,
    )
    accepted_names = validate_feature_selection(
        document, document["b07_v0_1_contract"]["feature_allowlist"]
    )
    assert accepted_names == tuple(document["b07_v0_1_contract"]["feature_allowlist"])
    assert select_pre_event_inputs(document, event) == select_pre_event_inputs(document, perturbed)
    assert validate_b07_contract(document) is None


def test_goal_to_go_requires_raw_b06_source_and_prohibits_fallback(document: dict) -> None:
    policy = document["b07_v0_1_contract"]["feature_allowlist"]["goal_to_go"]
    assert policy["source"] == "raw_b06_goal_to_go"
    assert policy["fallback_derivation"]["status"] == (
        "prohibited_in_v0_1_without_source_semantics_test"
    )
    assert validate_goal_to_go_source(document, source="raw_b06_goal_to_go") is None


def test_goal_to_go_equality_derivation_fails_closed(document: dict) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_goal_to_go_source(
            document,
            source="raw_b06_goal_to_go",
            derivation="yardline_100 == ydstogo",
        )
    _assert_reason(exc_info, "B07_GOAL_TO_GO_DERIVATION_PROHIBITED")


def test_goal_to_go_alternate_source_fails_closed(document: dict) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_goal_to_go_source(document, source="derived_goal_to_go")
    _assert_reason(exc_info, "B07_GOAL_TO_GO_SOURCE_INVALID")


@pytest.mark.parametrize("season", [2023, 2024, 2025])
def test_only_declared_season_digest_pairs_are_accepted(document: dict, season: int) -> None:
    assert validate_b06_source_claim(document, **_source_claim(season)) is None


def test_unknown_source_season_fails_closed(document: dict) -> None:
    claim = _source_claim()
    claim["season"] = 2022
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_SEASON_NOT_ALLOWED")


def test_mismatched_season_digest_pair_fails_closed(document: dict) -> None:
    claim = _source_claim(2023)
    claim["declared_revision_digest"] = EXPECTED_PAYLOAD_DIGESTS["2024"]
    claim["computed_payload_digest"] = EXPECTED_PAYLOAD_DIGESTS["2024"]
    claim["manifest_revision_digest"] = EXPECTED_PAYLOAD_DIGESTS["2024"]
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_SEASON_DIGEST_MISMATCH")


@pytest.mark.parametrize(
    "field",
    ["declared_revision_digest", "computed_payload_digest", "manifest_revision_digest"],
)
def test_malformed_digest_fails_closed(document: dict, field: str) -> None:
    claim = _source_claim()
    claim[field] = "not-a-sha256"
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_DIGEST_MALFORMED")


def test_payload_digest_mismatch_fails_closed(document: dict) -> None:
    claim = _source_claim()
    claim["computed_payload_digest"] = "0" * 64
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_PAYLOAD_DIGEST_MISMATCH")


def test_manifest_digest_mismatch_fails_closed(document: dict) -> None:
    claim = _source_claim()
    claim["manifest_revision_digest"] = "0" * 64
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_MANIFEST_DIGEST_MISMATCH")


def test_row_count_mismatch_fails_closed(document: dict) -> None:
    claim = _source_claim()
    claim["manifest_row_count"] = 99
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_ROW_COUNT_MISMATCH")


def test_event_count_mismatch_fails_closed(document: dict) -> None:
    claim = _source_claim()
    claim["manifest_event_count"] = 59
    with pytest.raises(B07ValidationError) as exc_info:
        validate_b06_source_claim(document, **claim)
    _assert_reason(exc_info, "B07_SOURCE_EVENT_COUNT_MISMATCH")


@pytest.mark.parametrize("purpose", sorted(DEVELOPMENT_PURPOSES))
def test_2025_is_rejected_from_every_development_path(document: dict, purpose: str) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_season_access(document, season=2025, purpose=purpose)
    _assert_reason(exc_info, "B07_HOLDOUT_ISOLATION_REQUIRED")


def test_2025_labels_are_rejected_even_with_explicit_evaluation_mode(document: dict) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_season_access(
            document,
            season=2025,
            purpose="holdout_evaluation",
            evaluation_mode=True,
            labels_requested=True,
        )
    _assert_reason(exc_info, "B07_HOLDOUT_LABEL_ACCESS_PROHIBITED")


def test_holdout_evaluation_requires_later_implementation(document: dict) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_season_access(
            document,
            season=2025,
            purpose="holdout_evaluation",
            evaluation_mode=True,
        )
    _assert_reason(exc_info, "B07_HOLDOUT_EVALUATION_NOT_IMPLEMENTED")


@pytest.mark.parametrize("season", [2023, 2024])
def test_declared_development_seasons_are_accepted_for_synthetic_validation(
    document: dict, season: int
) -> None:
    assert (
        validate_season_access(document, season=season, purpose="preprocessing") is None
    )


def test_baseline_and_backoff_contract_invariants(document: dict) -> None:
    baseline = document["b07_v0_1_contract"]["contextual_baseline"]
    assert baseline["separate_estimators"] is True
    assert baseline["min_cell_support_opportunities"] == 30
    assert tuple(tuple(row) for row in baseline["backoff_hierarchy"]) == (
        EXPECTED_BACKOFF_HIERARCHY
    )
    assert baseline["out_of_band_action"] == "exclude_with_reason_code"
    assert baseline["out_of_band_reason_code"] == "B07_EXCLUDE_INVALID_YARDLINE_BAND"
    assert baseline["missing_context_action"] == "exclude_with_reason_code"
    assert baseline["excluded_context_must_be_reported"] is True

    covered = [
        yard
        for lower, upper in baseline["yardline_bands"]
        for yard in range(lower, upper + 1)
    ]
    assert covered == list(range(100))
    assert len(covered) == len(set(covered))


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"yardline_100": None}, "B07_EXCLUDE_MISSING_YARDLINE_100"),
        ({"yardline_100": "10"}, "B07_EXCLUDE_INVALID_YARDLINE_100"),
        ({"yardline_100": 100}, "B07_EXCLUDE_INVALID_YARDLINE_BAND"),
        ({"down": None}, "B07_EXCLUDE_INVALID_DOWN"),
        ({"down": 5}, "B07_EXCLUDE_INVALID_DOWN"),
        ({"ydstogo": None}, "B07_EXCLUDE_INVALID_YDSTOGO"),
        ({"ydstogo": 0}, "B07_EXCLUDE_INVALID_YDSTOGO"),
        ({"goal_to_go": None}, "B07_EXCLUDE_MISSING_GOAL_TO_GO"),
        ({"quarter": None}, "B07_EXCLUDE_INVALID_QUARTER"),
        ({"quarter": 6}, "B07_EXCLUDE_INVALID_QUARTER"),
        (
            {"game_seconds_remaining": None},
            "B07_EXCLUDE_INVALID_GAME_SECONDS_REMAINING",
        ),
        (
            {"game_seconds_remaining": 3601},
            "B07_EXCLUDE_INVALID_GAME_SECONDS_REMAINING",
        ),
        (
            {"score_differential": None},
            "B07_EXCLUDE_INVALID_SCORE_DIFFERENTIAL",
        ),
        (
            {"identity_ambiguous": True},
            "B07_EXCLUDE_AMBIGUOUS_PLAYER_IDENTITY",
        ),
        ({"touchdown_label": None}, "B07_EXCLUDE_MISSING_TOUCHDOWN_LABEL"),
        (
            {"label_contradiction": True},
            "B07_EXCLUDE_TOUCHDOWN_LABEL_CONTRADICTION",
        ),
        (
            {"opportunity_type": "pass_attempt"},
            "B07_EXCLUDE_UNSUPPORTED_OPPORTUNITY_TYPE",
        ),
        ({"two_point_attempt": True}, "B07_EXCLUDE_TWO_POINT_ATTEMPT"),
        ({"logical_no_play": True}, "B07_EXCLUDE_LOGICAL_NO_PLAY"),
        ({"logical_no_play": None}, "B07_EXCLUDE_LOGICAL_NO_PLAY_UNKNOWN"),
        ({"penalty": True}, "B07_EXCLUDE_PENALIZED_EVENT"),
        ({"eligible_event": False}, "B07_EXCLUDE_INELIGIBLE_EVENT"),
    ],
)
def test_invalid_opportunity_metadata_has_explicit_reason_code(
    document: dict, changes: dict, reason: str
) -> None:
    event = _valid_event()
    event.update(changes)
    assert reason in exclusion_reason_codes(document, event)


def test_valid_synthetic_opportunity_has_no_exclusion(document: dict) -> None:
    assert exclusion_reason_codes(document, _valid_event()) == ()


@pytest.mark.parametrize("seconds", [0, 3600])
def test_game_seconds_inclusive_contract_boundaries_are_valid(
    document: dict, seconds: int
) -> None:
    event = _valid_event()
    event["game_seconds_remaining"] = seconds
    assert "B07_EXCLUDE_INVALID_GAME_SECONDS_REMAINING" not in exclusion_reason_codes(
        document, event
    )


@pytest.mark.parametrize("seconds", [-1, 3601])
def test_game_seconds_outside_contract_boundaries_fail_closed(
    document: dict, seconds: int
) -> None:
    event = _valid_event()
    event["game_seconds_remaining"] = seconds
    assert "B07_EXCLUDE_INVALID_GAME_SECONDS_REMAINING" in exclusion_reason_codes(
        document, event
    )


@pytest.mark.parametrize(
    ("action", "reason"),
    [
        ("candidate_estimator_training", "B07_EXECUTION_BASELINE_REVIEW_REQUIRED"),
        ("baseline_calculation", "B07_EXECUTION_BASELINE_NOT_AUTHORIZED"),
        ("xtd_scoring", "B07_EXECUTION_XTD_SCORING_NOT_AUTHORIZED"),
        ("validation_artifact_write", "B07_EXECUTION_ARTIFACT_WRITE_NOT_AUTHORIZED"),
        ("endpoint_creation", "B07_EXECUTION_ENDPOINT_OUT_OF_SCOPE"),
        ("current_pointer_update", "B07_EXECUTION_CURRENT_POINTER_PROHIBITED"),
        ("promotion", "B07_EXECUTION_PROMOTION_PROHIBITED"),
        ("draft_live_recommendation", "B07_EXECUTION_RECOMMENDATION_PROHIBITED"),
    ],
)
def test_execution_boundary_fails_closed(document: dict, action: str, reason: str) -> None:
    with pytest.raises(B07ValidationError) as exc_info:
        validate_execution_action(document, action)
    _assert_reason(exc_info, reason)


def test_contract_exposes_only_local_inspection_and_defers_training(document: dict) -> None:
    contract = document["b07_v0_1_contract"]
    assert contract["access"] == {
        "v0_1": "immutable_validation_artifact_and_local_inspection",
        "endpoint": "explicitly_out_of_scope",
    }
    assert contract["execution_control"] == {
        "one_run_stop_condition": True,
        "candidate_estimator_training": "out_of_scope_until_baseline_artifact_review",
    }
