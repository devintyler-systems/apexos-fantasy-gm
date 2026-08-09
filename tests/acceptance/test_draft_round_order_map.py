# Acceptance test scaffold for Draft Round Order Map
# Artifact: draft_round_order_map v1.0
# Status: SCAFFOLD — Builder fills in imports and any helper assertions
# All T01–T09 are BLOCKING; T10 is advisory

import pytest
# Builder: update import path if module location changes
# from engine.draft.round_order_map import get_pick_numbers, get_draft_position, get_picks_between, build_full_map


class TestGroundTruth:
    """T01 — Must pass before any other work proceeds."""

    def test_position_11_picks_match_2025_actuals(self):
        result = get_pick_numbers(11)
        assert result == [11, 22, 35, 62, 75, 86, 99, 126], (
            f"Ground truth failure: Professor FleX 2025 actuals are [11,22,35,62,75,86,99,126], got {result}"
        )


class TestMapIntegrity:
    """T02–T04 — Full map structural validation."""

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
        # Each round spans exactly 16 consecutive pick numbers
        for r in range(1, 9):
            base = (r - 1) * 16
            full_map = build_full_map()
            for pick in range(base + 1, base + 17):
                assert str(pick) in full_map["pick_to_position_map"], f"Pick {pick} missing from map"


class TestPivotRounds:
    """T05–T06 — Pivot and reverse-pivot round correctness."""

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
    """T07 — Forward and inverse map consistency."""

    def test_inverse_map_consistency(self):
        full_map = build_full_map()
        for pick_str, pos in full_map["pick_to_position_map"].items():
            pick = int(pick_str)
            assert get_draft_position(pick) == pos
            assert pick in get_pick_numbers(pos)


class TestPicksBetween:
    """T08 — get_picks_between helper for availability model."""

    def test_picks_between_round_1_to_2(self):
        # After pick 11, next pick for pos 11 is 22 — 10 picks fire in between
        result = get_picks_between(11, 11)
        assert result == list(range(12, 22)), f"Expected picks 12–21, got {result}"

    def test_picks_between_round_2_to_3(self):
        # After pick 22, next pick for pos 11 is 35 — 12 picks fire in between
        result = get_picks_between(22, 11)
        assert result == list(range(23, 35)), f"Expected picks 23–34, got {result}"

    def test_picks_between_last_pick_returns_empty(self):
        # After final pick (pick 126 for pos 11), no more picks remain
        result = get_picks_between(126, 11)
        assert result == [], f"Expected empty list after last pick, got {result}"


class TestEdgePositions:
    """T09 — Validate most extreme draft positions."""

    def test_position_1_picks(self):
        assert get_pick_numbers(1) == [1, 32, 40, 57, 65, 96, 104, 121]

    def test_position_16_picks(self):
        assert get_pick_numbers(16) == [16, 17, 44, 49, 80, 81, 108, 113]


class TestInputValidation:
    """T10 — Advisory: out-of-range input handling."""

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
