"""Deterministic SPAMML draft-round order map."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Final

LEAGUE_SIZE: Final = 16
TOTAL_ROUNDS: Final = 8


def _league_rules_version() -> str:
    rules_directory = Path(__file__).resolve().parents[2] / "contracts" / "league_rules"
    candidates = list(rules_directory.glob("*.yaml"))
    if not candidates:
        raise RuntimeError(f"No league rules YAML found in {rules_directory}.")

    def version_key(path: Path) -> tuple[int, ...]:
        match = re.search(r"v(\d+(?:\.\d+)*)$", path.stem)
        if match is None:
            return ()
        return tuple(int(part) for part in match.group(1).split("."))

    current_rules_file = max(candidates, key=version_key)
    return current_rules_file.stem


def _round_patterns() -> list[tuple[str, list[int]]]:
    forward = list(range(1, LEAGUE_SIZE + 1))
    reverse = list(reversed(forward))
    pivot = forward[LEAGUE_SIZE // 2 :] + forward[: LEAGUE_SIZE // 2]
    reverse_pivot = list(reversed(pivot))
    return [
        ("forward", forward),
        ("reverse", reverse),
        ("pivot", pivot),
        ("reverse_pivot", reverse_pivot),
    ] * 2


def build_full_map() -> dict:
    """Build the immutable-in-content lookup maps for all draft positions."""
    position_pick_map = {str(position): [] for position in range(1, LEAGUE_SIZE + 1)}
    pick_to_position_map = {}
    for round_number, (_, positions) in enumerate(_round_patterns(), start=1):
        for slot_in_round, draft_position in enumerate(positions, start=1):
            pick_number = (round_number - 1) * LEAGUE_SIZE + slot_in_round
            position_pick_map[str(draft_position)].append(pick_number)
            pick_to_position_map[str(pick_number)] = draft_position
    return {
        "league_rules_version": _league_rules_version(),
        "position_pick_map": position_pick_map,
        "pick_to_position_map": pick_to_position_map,
    }


def get_pick_numbers(draft_position: int) -> list[int]:
    """Return the eight pick numbers for a valid draft position."""
    if not 1 <= draft_position <= LEAGUE_SIZE:
        raise ValueError(f"draft_position must be 1-{LEAGUE_SIZE}: {draft_position}")
    return list(build_full_map()["position_pick_map"][str(draft_position)])


def get_draft_position(pick_number: int) -> int:
    """Return the owning draft position for a valid pick number."""
    total_picks = LEAGUE_SIZE * TOTAL_ROUNDS
    if not 1 <= pick_number <= total_picks:
        raise ValueError(f"pick_number must be 1-{total_picks}: {pick_number}")
    return build_full_map()["pick_to_position_map"][str(pick_number)]


def get_picks_between(current_pick: int, my_draft_position: int) -> list[int]:
    """Return picks strictly after current_pick and before the next owned pick."""
    total_picks = LEAGUE_SIZE * TOTAL_ROUNDS
    if not 1 <= current_pick <= total_picks:
        raise ValueError(f"current_pick must be 1-{total_picks}: {current_pick}")
    pick_numbers = get_pick_numbers(my_draft_position)
    next_pick = next((pick for pick in pick_numbers if pick > current_pick), None)
    if next_pick is None:
        return []
    return list(range(current_pick + 1, next_pick))
