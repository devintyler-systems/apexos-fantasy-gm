# Acceptance test scaffold for Draft Round Order Map
# Artifact: draft_round_order_map v1.2 (T09 corrected per v1.2-correction.md)
# Status: SCAFFOLD -- Builder fills in imports and any helper assertions
# All T01-T09, T12 are BLOCKING; T10 is advisory

import pytest
# Builder: update import path if module location changes
from engine.draft.round_order_map import (
    build_full_map,
    get_draft_position,
    get_pick_numbers,
    get_picks_between,
)


class TestGroundTruth:
    """T01 -- Must pass before any other work proceeds."""

    def test_position_11_picks_match_2025_actuals(self):
        result = get_pick_numbers(11)
        assert result == [11, 22, 35, 62, 75, 86, 99, 126], (
            f"Ground truth failure: Professor FleX 2025 actuals are [11,22,35,62,75,86,99,126], got {result}"
        )


class TestMapIntegrity:
    """T02-T04 -- Full map structural validation."""

    def test_total_pick_count(self):
        full_map = build_full_map()
        picks = list(full_map["pick_to_position_map"].keys())
        assert len(picks) == 128
        assert sorted([int(p) for p in picks]) == list(range(1, 129))

    def test_every_position_appears_exactly_8_times(self):
        full_map = build_full_map()
        from collections import Counter
        counts = Counter(full_map["pick_to_position_map"].values())
        for pos in range(1, 17):
            assert counts[pos] == 8, f"Position {pos} appears {counts[pos]} times, expected 8"

    def test_every_round_has_16_picks(self):
        for r in range(1, 9):
            base = (r - 1) * 16
            full_map = build_full_map()
            for pick in range(base + 1, base + 17):
                assert str(pick) in full_map["pick_to_position_map"], f"Pick {pick} missing from map"


class TestPivotRounds:
    """T05-T06 -- Pivot and reverse-pivot round correctness."""

    PIVOT_SEQUENCE    = [9,10,11,12,13,14,15,16, 1, 2, 3, 4, 5, 6, 7, 8]
    REV_PIVOT_SEQ     = [8, 7, 6, 5, 4, 3, 2, 1,16,15,14,13,12,11,10, 9]

    def test_round_3_pivot(self):
        full_map = build_full_map()
        for slot, expected_pos in enumerate(self.PIVOT_SEQUENCE, start=1):
            pick = 32 + slot
            actual = full_map["pick_to_position_map"][str(pick)]
            assert actual == expected_pos, f"Round 3 slot {slot} (pick {pick}): expected pos {expected_pos}, got {actual}"

    def test_round_7_pivot(self):
        full_map = build_full_map()
        for slot, expected_pos in enumerate(self.PIVOT_SEQUENCE, start=1):
            pick = 96 + slot
            actual = full_map["pick_to_position_map"][str(pick)]
            assert actual == expected_pos, f"Round 7 slot {slot} (pick {pick}): expected pos {expected_pos}, got {actual}"

    def test_round_4_reverse_pivot(self):
        full_map = build_full_map()
        for slot, expected_pos in enumerate(self.REV_PIVOT_SEQ, start=1):
            pick = 48 + slot
            actual = full_map["pick_to_position_map"][str(pick)]
            assert actual == expected_pos, f"Round 4 slot {slot} (pick {pick}): expected pos {expected_pos}, got {actual}"

    def test_round_8_reverse_pivot(self):
        full_map = build_full_map()
        for slot, expected_pos in enumerate(self.REV_PIVOT_SEQ, start=1):
            pick = 112 + slot
            actual = full_map["pick_to_position_map"][str(pick)]
            assert actual == expected_pos, f"Round 8 slot {slot} (pick {pick}): expected pos {expected_pos}, got {actual}"


class TestInverseMap:
    """T07 -- Forward and inverse map consistency."""

    def test_inverse_map_consistency(self):
        full_map = build_full_map()
        for pick_str, pos in full_map["pick_to_position_map"].items():
            pick = int(pick_str)
            assert get_draft_position(pick) == pos
            assert pick in get_pick_numbers(pos)


class TestPicksBetween:
    """T08 -- get_picks_between helper for availability model."""

    def test_picks_between_round_1_to_2(self):
        result = get_picks_between(11, 11)
        assert result == list(range(12, 22)), f"Expected picks 12-21, got {result}"

    def test_picks_between_round_2_to_3(self):
        result = get_picks_between(22, 11)
        assert result == list(range(23, 35)), f"Expected picks 23-34, got {result}"

    def test_picks_between_last_pick_returns_empty(self):
        result = get_picks_between(126, 11)
        assert result == [], f"Expected empty list after last pick, got {result}"


class TestEdgePositions:
    """T09 -- Validate most extreme draft positions.
    CORRECTED per draft-round-order-map-contract-v1.2-correction.md.
    Original v1.0 values were fabricated placeholders, never verified against
    the Section 5 algorithm. These values ARE independently computed and
    verified via ground-truth match, invariant sums, and full-map uniqueness.
    """

    def test_position_1_picks(self):
        assert get_pick_numbers(1) == [1, 32, 41, 56, 65, 96, 105, 120]

    def test_position_2_picks(self):
        assert get_pick_numbers(2) == [2, 31, 42, 55, 66, 95, 106, 119]

    def test_position_16_picks(self):
        assert get_pick_numbers(16) == [16, 17, 40, 57, 80, 81, 104, 121]


class TestInvariantSums:
    """T12 -- NEW. Structural sanity check catching the exact class of error
    found in the original T09 (plausible-looking but unverified pick numbers).
    """

    @pytest.mark.parametrize("position", range(1, 17))
    def test_round_pair_sums(self, position):
        picks = get_pick_numbers(position)
        assert picks[0] + picks[1] == 33, f"Position {position}: R1+R2 should sum to 33"
        assert picks[2] + picks[3] == 97, f"Position {position}: R3+R4 should sum to 97"
        assert picks[4] + picks[5] == 161, f"Position {position}: R5+R6 should sum to 161"
        assert picks[6] + picks[7] == 225, f"Position {position}: R7+R8 should sum to 225"


class TestInputValidation:
    """T10 -- Advisory: out-of-range input handling."""

    def test_get_pick_numbers_rejects_zero(self):
        with pytest.raises(ValueError):
            get_pick_numbers(0)

    def test_get_pick_numbers_rejects_17(self):
        with pytest.raises(ValueError):
            get_pick_numbers(17)

    def test_get_draft_position_rejects_zero(self):
        with pytest.raises(ValueError):
            get_draft_position(0)

    def test_get_draft_position_rejects_129(self):
        with pytest.raises(ValueError):
            get_draft_position(129)
