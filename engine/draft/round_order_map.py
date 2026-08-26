"""Validated planned SPAMML 2026 round-order map authority."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any, Final

import yaml


LEAGUE_SIZE: Final = 16
TOTAL_ROUNDS: Final = 8
TOTAL_PICKS: Final = LEAGUE_SIZE * TOTAL_ROUNDS
PROVENANCE_UNAVAILABLE: Final = "PROVENANCE_UNAVAILABLE"
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MAP_ARTIFACT_PATH: Final = _REPOSITORY_ROOT / "contracts" / "draft" / "spamml-2026-round-order-map-v1.0.yaml"


def _league_rules_version() -> str:
    rules_directory = Path(__file__).resolve().parents[2] / "contracts" / "league_rules"
    candidates = list(rules_directory.glob("*.yaml"))
    if not candidates:
        raise RuntimeError(f"No league rules YAML found in {rules_directory}.")

    def version_key(path: Path) -> tuple[int, ...]:
        match = re.search(r"v(\d+(?:\.\d+)*)$", path.stem)
        return () if match is None else tuple(int(part) for part in match.group(1).split("."))

    current_rules_file = max(candidates, key=version_key)
    try:
        with current_rules_file.open(encoding="utf-8") as rules_file:
            rules = yaml.safe_load(rules_file)
    except (OSError, yaml.YAMLError):
        return PROVENANCE_UNAVAILABLE
    version = rules.get("contract_version") if isinstance(rules, dict) else None
    return version if isinstance(version, str) and re.fullmatch(r"\d+(?:\.\d+)*", version) else PROVENANCE_UNAVAILABLE


def _validated_finalized_map() -> dict[str, Any]:
    """Load the only authorized planned-order source for SPAMML 2026."""
    try:
        with MAP_ARTIFACT_PATH.open(encoding="utf-8") as stream:
            artifact = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError("Finalized SPAMML 2026 round-order artifact is unavailable") from exc
    if not isinstance(artifact, dict):
        raise RuntimeError("Finalized SPAMML 2026 round-order artifact is not a mapping")
    managers = artifact.get("canonical_managers")
    orders = artifact.get("round_seat_orders")
    if not isinstance(managers, dict) or set(managers) != set(range(1, LEAGUE_SIZE + 1)):
        raise RuntimeError("Finalized map must contain the 16 canonical draft seats")
    if not all(isinstance(name, str) and name.strip() for name in managers.values()) or len(set(managers.values())) != LEAGUE_SIZE:
        raise RuntimeError("Finalized map has invalid canonical manager names")
    if not isinstance(orders, list) or len(orders) != TOTAL_ROUNDS:
        raise RuntimeError("Finalized map must contain exactly eight round orders")

    position_pick_map = {str(seat): [] for seat in range(1, LEAGUE_SIZE + 1)}
    manager_pick_map = {name: [] for name in managers.values()}
    pick_to_position_map: dict[str, int] = {}
    pick_to_manager_map: dict[str, str] = {}
    for round_number, order in enumerate(orders, start=1):
        if not isinstance(order, list) or len(order) != LEAGUE_SIZE or set(order) != set(range(1, LEAGUE_SIZE + 1)):
            raise RuntimeError(f"Finalized map round {round_number} is not a complete unique seat order")
        for slot_in_round, seat in enumerate(order, start=1):
            pick = (round_number - 1) * LEAGUE_SIZE + slot_in_round
            manager = managers[seat]
            position_pick_map[str(seat)].append(pick)
            manager_pick_map[manager].append(pick)
            pick_to_position_map[str(pick)] = seat
            pick_to_manager_map[str(pick)] = manager

    if set(map(int, pick_to_position_map)) != set(range(1, TOTAL_PICKS + 1)):
        raise RuntimeError("Finalized map does not cover every overall pick 1..128")
    if any(len(picks) != TOTAL_ROUNDS for picks in position_pick_map.values()):
        raise RuntimeError("Finalized map does not assign eight picks to every seat")
    if Counter(pick_to_manager_map.values()) != Counter({name: TOTAL_ROUNDS for name in managers.values()}):
        raise RuntimeError("Finalized map does not assign eight picks to every manager")
    return {
        "league_rules_version": _league_rules_version(),
        "position_pick_map": position_pick_map,
        "pick_to_position_map": pick_to_position_map,
        "manager_pick_map": manager_pick_map,
        "pick_to_manager_map": pick_to_manager_map,
        "authority_path": MAP_ARTIFACT_PATH.as_posix(),
    }


def build_full_map() -> dict[str, Any]:
    """Return the validated finalized 2026 map; no generic fallback exists."""
    return _validated_finalized_map()


def get_pick_numbers(draft_position: int) -> list[int]:
    if not 1 <= draft_position <= LEAGUE_SIZE:
        raise ValueError(f"draft_position must be 1-{LEAGUE_SIZE}: {draft_position}")
    return list(build_full_map()["position_pick_map"][str(draft_position)])


def get_draft_position(pick_number: int) -> int:
    if not 1 <= pick_number <= TOTAL_PICKS:
        raise ValueError(f"pick_number must be 1-{TOTAL_PICKS}: {pick_number}")
    return build_full_map()["pick_to_position_map"][str(pick_number)]


def get_picks_between(current_pick: int, my_draft_position: int) -> list[int]:
    if not 1 <= current_pick <= TOTAL_PICKS:
        raise ValueError(f"current_pick must be 1-{TOTAL_PICKS}: {current_pick}")
    next_pick = next((pick for pick in get_pick_numbers(my_draft_position) if pick > current_pick), None)
    return [] if next_pick is None else list(range(current_pick + 1, next_pick))
