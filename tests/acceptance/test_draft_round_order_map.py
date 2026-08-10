import pytest

from engine.draft.round_order_map import (
    build_full_map,
    get_draft_position,
    get_pick_numbers,
    get_picks_between,
)


class TestGroundTruth:
    def test_position_11_picks_match_2025_actuals(self):
        assert get_pick_numbers(11) == [11, 22, 35, 62, 75, 86, 99, 126]


class TestMapIntegrity:
    def test_total_pick_count(self):
        picks = build_full_map()["pick_to_position_map"]
        assert len(picks) == 128
        assert sorted(map(int, picks)) == list(range(1, 129))

    def test_every_position_appears_exactly_8_times(self):
        position_pick_map = build_full_map()["position_pick_map"]
        assert all(len(position_pick_map[str(pos)]) == 8 for pos in range(1, 17))

    def test_every_round_has_16_picks(self):
        picks = build_full_map()["pick_to_position_map"]
        for round_number in range(1, 9):
            first_pick = (round_number - 1) * 16 + 1
            assert all(str(pick) in picks for pick in range(first_pick, first_pick + 16))


class TestPivotRounds:
    pivot = [9, 10, 11, 12, 13, 14, 15, 16, 1, 2, 3, 4, 5, 6, 7, 8]
    reverse_pivot = [8, 7, 6, 5, 4, 3, 2, 1, 16, 15, 14, 13, 12, 11, 10, 9]

    @pytest.mark.parametrize("start_pick", [33, 97])
    def test_pivot_rounds(self, start_pick):
        picks = build_full_map()["pick_to_position_map"]
        assert [picks[str(pick)] for pick in range(start_pick, start_pick + 16)] == self.pivot

    @pytest.mark.parametrize("start_pick", [49, 113])
    def test_reverse_pivot_rounds(self, start_pick):
        picks = build_full_map()["pick_to_position_map"]
        assert [picks[str(pick)] for pick in range(start_pick, start_pick + 16)] == self.reverse_pivot


class TestInverseMap:
    def test_inverse_map_consistency(self):
        for pick, position in build_full_map()["pick_to_position_map"].items():
            assert get_draft_position(int(pick)) == position
            assert int(pick) in get_pick_numbers(position)


class TestPicksBetween:
    def test_picks_between(self):
        assert get_picks_between(11, 11) == list(range(12, 22))
        assert get_picks_between(22, 11) == list(range(23, 35))
        assert get_picks_between(126, 11) == []


class TestEdgePositions:
    @pytest.mark.parametrize(("position", "expected"), [
        (1, [1, 32, 41, 56, 65, 96, 105, 120]),
        (2, [2, 31, 42, 55, 66, 95, 106, 119]),
        (16, [16, 17, 40, 57, 80, 81, 104, 121]),
    ])
    def test_position_picks(self, position, expected):
        assert get_pick_numbers(position) == expected


class TestInvariantSums:
    def test_each_symmetric_round_pair_has_expected_sum(self):
        expected_sums = [33, 97, 161, 225]
        for position in range(1, 17):
            picks = get_pick_numbers(position)
            assert [picks[index] + picks[index + 1] for index in range(0, 8, 2)] == expected_sums


class TestInputValidation:
    @pytest.mark.parametrize("position", [0, 17])
    def test_get_pick_numbers_rejects_out_of_range_position(self, position):
        with pytest.raises(ValueError):
            get_pick_numbers(position)

    @pytest.mark.parametrize("pick", [0, 129])
    def test_get_draft_position_rejects_out_of_range_pick(self, pick):
        with pytest.raises(ValueError):
            get_draft_position(pick)
