"""Acceptance coverage for the CI-only draft-seat-assignment validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.contracts.draft_seat_assignment import (
    ROUND_ORDER_AUTHORITIES,
    ContractValidationError,
    classify_draft_activity,
    load_yaml_contract,
    validate_draft_seat_assignment,
)


ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SEAT = (
    ROOT / "contracts" / "draft" / "spamml-2026-draft-seat-assignment-v1.1.yaml"
)
CANONICAL_LEAGUE = (
    ROOT / "contracts" / "league_rules" / "spamml-2026-v0.4.yaml"
)
FIXTURES = ROOT / "tests" / "fixtures" / "draft_seat_assignment"


def fixture(name: str) -> Path:
    return FIXTURES / name


def assert_validation_error(
    criterion: str,
    *,
    seat_path: Path = CANONICAL_SEAT,
    league_path: Path = CANONICAL_LEAGUE,
) -> str:
    with pytest.raises(ContractValidationError) as exc_info:
        validate_draft_seat_assignment(seat_path, league_path)
    message = str(exc_info.value)
    assert message.startswith(f"{criterion} |")
    assert "artifact=" in message
    assert "field=" in message
    assert "actual=" in message
    assert "expected=" in message
    return message


def test_dsa_01_canonical_has_exactly_one_of_each_seat_1_through_16():
    result = validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    contract = load_yaml_contract(CANONICAL_SEAT)
    seats = [assignment["draft_seat"] for assignment in contract["seat_assignments"]]
    assert seats == list(range(1, 17))
    assert result.manager_draft_seat == 4


@pytest.mark.parametrize(
    ("fixture_name", "expected_field", "expected_actual"),
    [
        (
            "dsa01_missing_seat.yaml",
            "seat_assignments[*].draft_seat",
            "'missing_seats': [16]",
        ),
        (
            "dsa01_duplicate_seat.yaml",
            "seat_assignments[15].draft_seat",
            "actual=15",
        ),
        (
            "dsa01_out_of_range_seat.yaml",
            "seat_assignments[15].draft_seat",
            "actual=17",
        ),
    ],
)
def test_dsa_01_rejects_incomplete_duplicate_or_out_of_range_seats(
    fixture_name, expected_field, expected_actual
):
    message = assert_validation_error(
        "DSA-01", seat_path=fixture(fixture_name)
    )
    assert f"field={expected_field}" in message
    assert expected_actual in message


def test_dsa_02_canonical_team_names_are_non_empty_and_exact_unique():
    validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    names = [
        assignment["team_name"]
        for assignment in load_yaml_contract(CANONICAL_SEAT)["seat_assignments"]
    ]
    assert all(name and name.strip() for name in names)
    assert len(names) == len(set(names)) == 16


@pytest.mark.parametrize(
    ("fixture_name", "expected_field", "expected_actual"),
    [
        ("dsa02_whitespace_team_name.yaml", "seat_assignments[0].team_name", "actual='   '"),
        ("dsa02_duplicate_team_name.yaml", "seat_assignments[1].team_name", "actual='Cockney Punter'"),
    ],
)
def test_dsa_02_rejects_whitespace_or_exact_duplicate_labels(
    fixture_name, expected_field, expected_actual
):
    message = assert_validation_error(
        "DSA-02", seat_path=fixture(fixture_name)
    )
    assert f"field={expected_field}" in message
    assert expected_actual in message
    assert "exact-display-name" in message or "non-whitespace" in message


def test_dsa_03_canonical_resolves_professor_flex_as_only_manager_at_seat_4():
    result = validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    assert result.manager_team_name == "Professor FleX"
    assert result.manager_draft_seat == 4


@pytest.mark.parametrize(
    ("fixture_name", "expected_field", "expected_actual"),
    [
        ("dsa03_no_manager_marker.yaml", "seat_assignments[*].is_manager_team", "actual=[]"),
        ("dsa03_multiple_manager_markers.yaml", "seat_assignments[*].is_manager_team", "seat_assignments[4].is_manager_team"),
        ("dsa03_marked_name_seat_mismatch.yaml", "seat_assignments[4].team_name", "actual='Shaq in His Prime'"),
        ("dsa03_identity_mismatch.yaml", "identity.manager_team_name", "actual='Professor FleX II'"),
    ],
)
def test_dsa_03_rejects_manager_marker_or_identity_divergence(
    fixture_name, expected_field, expected_actual
):
    message = assert_validation_error(
        "DSA-03", seat_path=fixture(fixture_name)
    )
    assert f"field={expected_field}" in message
    assert expected_actual in message


def test_dsa_04_confirmed_schedule_has_complete_matching_provenance():
    validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    contract = load_yaml_contract(CANONICAL_SEAT)
    assert (
        contract["draft_date_time_provenance"]["effective_time_utc"]
        == contract["draft_state"]["draft_date_time_utc"]
        == "2026-09-01T01:00:00Z"
    )


@pytest.mark.parametrize(
    ("fixture_name", "expected_field", "expected_actual"),
    [
        ("dsa04_missing_provenance.yaml", "draft_date_time_provenance.source_reference", "actual=<missing>"),
        ("dsa04_effective_utc_mismatch.yaml", "draft_date_time_provenance.effective_time_utc", "actual='2026-09-01T02:00:00Z'"),
    ],
)
def test_dsa_04_rejects_missing_or_mismatched_schedule_provenance(
    fixture_name, expected_field, expected_actual
):
    message = assert_validation_error(
        "DSA-04", seat_path=fixture(fixture_name)
    )
    assert f"field={expected_field}" in message
    assert expected_actual in message


def test_dsa_05_format_matches_league_and_delegates_without_deriving_picks():
    validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    seat = load_yaml_contract(CANONICAL_SEAT)
    league = load_yaml_contract(CANONICAL_LEAGUE)
    assert seat["draft_state"]["format"] == league["draft"]["format"] == "non_standard_snake"
    assert all(path in seat["artifact"]["depends_on"] for path in ROUND_ORDER_AUTHORITIES)
    assert "pick_order" not in seat["draft_state"]


@pytest.mark.parametrize(
    ("fixture_name", "expected_field", "expected_actual"),
    [
        ("dsa05_embedded_pick_order.yaml", "draft_state.pick_order", "actual=[1, 2]"),
        ("dsa05_format_mismatch.yaml", "draft_state.format", "actual='standard_snake'"),
        ("dsa05_missing_map_delegation.yaml", "artifact.depends_on", "actual=<missing>"),
    ],
)
def test_dsa_05_rejects_local_pick_order_format_drift_or_missing_delegation(
    fixture_name, expected_field, expected_actual
):
    message = assert_validation_error(
        "DSA-05", seat_path=fixture(fixture_name)
    )
    assert f"field={expected_field}" in message
    assert expected_actual in message
    assert "round-order-map" in message or "League Rules v0.4" in message


def test_dsa_06_canonical_timezone_fields_are_separate_and_convert_exactly():
    validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    provenance = load_yaml_contract(CANONICAL_SEAT)["draft_date_time_provenance"]
    assert provenance["timezone"] == "America/Los_Angeles"
    assert provenance["utc_offset"] == "-07:00"
    assert provenance["timezone_abbreviation"] == "PDT"
    assert provenance["effective_time_utc"] == "2026-09-01T01:00:00Z"


@pytest.mark.parametrize(
    ("fixture_name", "expected_field", "expected_actual"),
    [
        ("dsa06_invalid_timezone.yaml", "draft_date_time_provenance.timezone", "actual='-07:00'"),
        (
            "dsa06_merged_timezone_fields.yaml",
            "draft_date_time_provenance.timezone",
            "actual='America/Los_Angeles | -07:00 | PDT'",
        ),
    ],
)
def test_dsa_06_rejects_invalid_misplaced_or_merged_timezone_representation(
    fixture_name, expected_field, expected_actual
):
    message = assert_validation_error(
        "DSA-06", seat_path=fixture(fixture_name)
    )
    assert f"field={expected_field}" in message
    assert expected_actual in message
    assert "distinct fields" in message


def test_dsa_07_canonical_not_started_is_safe_non_live():
    contract = load_yaml_contract(CANONICAL_SEAT)
    classification = classify_draft_activity(contract, CANONICAL_SEAT)
    assert classification.raw_selection_state == "not_started"
    assert classification.derived_classification == "non_live"
    assert classification.live_claim_allowed is False
    result = validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    assert result.activity_classification == "non_live"


def test_dsa_07_schedule_and_clock_changes_alone_remain_non_live():
    changed = fixture("dsa07_altered_schedule_clock_not_started.yaml")
    contract = load_yaml_contract(changed)
    assert contract["draft_state"]["selection_state"] == "not_started"
    classification = classify_draft_activity(contract, changed)
    assert classification.derived_classification == "non_live"
    assert classification.live_claim_allowed is False
    assert classification.derived_classification not in {"live", "in_progress"}


def test_dsa_07_raw_in_progress_without_required_evidence_degrades_safely():
    changed = fixture("dsa07_in_progress_without_transition_feed.yaml")
    contract = load_yaml_contract(changed)
    classification = classify_draft_activity(contract, changed)
    assert classification.raw_selection_state == "in_progress"
    assert classification.derived_classification == "degraded"
    assert classification.live_claim_allowed is False
    assert classification.missing_valid_selection_transition is True
    assert classification.missing_confirmed_real_time_pick_feed is True
    assert classification.derived_classification not in {"live", "in_progress"}
    message = classification.evidence_message()
    assert "field=draft_state.selection_state" in message
    assert "raw_selection_state='in_progress'" in message
    assert "derived_classification='degraded'" in message
    assert "live_claim_allowed=False" in message
    assert "missing_valid_selection_transition=True" in message
    assert "missing_confirmed_real_time_pick_feed=True" in message


def test_dsa_07_in_progress_requires_valid_transition_and_confirmed_feed():
    changed = fixture("dsa07_in_progress_with_transition_feed.yaml")
    contract = load_yaml_contract(changed)
    classification = classify_draft_activity(contract, changed)
    assert classification.raw_selection_state == "in_progress"
    assert classification.derived_classification == "in_progress"
    assert classification.live_claim_allowed is True
    assert classification.missing_valid_selection_transition is False
    assert classification.missing_confirmed_real_time_pick_feed is False
    result = validate_draft_seat_assignment(changed, CANONICAL_LEAGUE)
    assert result.activity_classification == "in_progress"


def test_dsa_08_canonical_clock_mirror_matches_league_rules_v04_authority():
    validate_draft_seat_assignment(CANONICAL_SEAT, CANONICAL_LEAGUE)
    seat = load_yaml_contract(CANONICAL_SEAT)
    league = load_yaml_contract(CANONICAL_LEAGUE)
    assert seat["draft_state"]["draft_clock_status"] == "confirmed_untimed"
    assert league["draft"]["draft_clock_config"]["timer_enabled"] is False


@pytest.mark.parametrize(
    ("seat_path", "league_path", "seat_actual", "league_actual"),
    [
        (
            CANONICAL_SEAT,
            fixture("dsa08_timer_enabled_true.yaml"),
            "actual='confirmed_untimed'",
            "league_actual=True",
        ),
        (
            fixture("dsa08_non_untimed_status.yaml"),
            CANONICAL_LEAGUE,
            "actual='confirmed_timed'",
            "league_actual=False",
        ),
    ],
)
def test_dsa_08_rejects_both_directions_of_clock_authority_divergence(
    seat_path, league_path, seat_actual, league_actual
):
    message = assert_validation_error(
        "DSA-08", seat_path=seat_path, league_path=league_path
    )
    assert "field=draft_state.draft_clock_status" in message
    assert seat_actual in message
    assert "league_field=draft.draft_clock_config.timer_enabled" in message
    assert league_actual in message
    assert "'confirmed_untimed' iff League Rules v0.4" in message
    assert "League Rules v0.4 is the sole clock authority" in message
    assert "consistency mirror only" in message
