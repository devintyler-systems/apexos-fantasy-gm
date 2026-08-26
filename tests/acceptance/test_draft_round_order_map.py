"""Acceptance coverage for the finalized SPAMML 2026 round-order authority."""

from collections import Counter

import pytest

from engine.draft.round_order_map import (
    MAP_ARTIFACT_PATH,
    build_full_map,
    get_draft_position,
    get_pick_numbers,
    get_picks_between,
)


EXPECTED_PROFESSOR_FLEX_PICKS = [4, 29, 45, 52, 68, 93, 109, 116]


def test_finalized_versioned_artifact_is_the_runtime_authority():
    full_map = build_full_map()
    assert MAP_ARTIFACT_PATH.exists()
    assert full_map["authority_path"].endswith("spamml-2026-round-order-map-v1.0.yaml")
    assert len(full_map["pick_to_position_map"]) == 128


def test_all_128_picks_are_unique_complete_and_inverse_consistent():
    full_map = build_full_map()
    assert sorted(map(int, full_map["pick_to_position_map"])) == list(range(1, 129))
    assert len(full_map["position_pick_map"]) == 16
    assert all(len(picks) == 8 for picks in full_map["position_pick_map"].values())
    for pick, seat in full_map["pick_to_position_map"].items():
        assert get_draft_position(int(pick)) == seat
        assert int(pick) in get_pick_numbers(seat)


def test_all_16_canonical_managers_have_exactly_eight_picks():
    full_map = build_full_map()
    assert len(full_map["manager_pick_map"]) == 16
    assert Counter(len(picks) for picks in full_map["manager_pick_map"].values()) == {8: 16}
    assert len(full_map["pick_to_manager_map"]) == 128


def test_professor_flex_seat_4_matches_both_accepted_sources():
    full_map = build_full_map()
    assert get_pick_numbers(4) == EXPECTED_PROFESSOR_FLEX_PICKS
    assert full_map["manager_pick_map"]["Professor FleX"] == EXPECTED_PROFESSOR_FLEX_PICKS
    assert [full_map["pick_to_manager_map"][str(pick)] for pick in EXPECTED_PROFESSOR_FLEX_PICKS] == ["Professor FleX"] * 8


def test_source_specific_round_three_and_seven_orders_replace_generic_pivot():
    full_map = build_full_map()
    expected = [9, 10, 11, 12, 13, 14, 15, 16, 8, 7, 6, 5, 4, 3, 2, 1]
    assert [full_map["pick_to_position_map"][str(pick)] for pick in range(33, 49)] == expected
    assert [full_map["pick_to_position_map"][str(pick)] for pick in range(97, 113)] == expected


def test_picks_between_uses_finalized_schedule():
    assert get_picks_between(29, 4) == list(range(30, 45))
    assert get_picks_between(116, 4) == []


@pytest.mark.parametrize("position", [0, 17])
def test_get_pick_numbers_rejects_invalid_positions(position):
    with pytest.raises(ValueError):
        get_pick_numbers(position)


@pytest.mark.parametrize("pick", [0, 129])
def test_get_draft_position_rejects_invalid_picks(pick):
    with pytest.raises(ValueError):
        get_draft_position(pick)
