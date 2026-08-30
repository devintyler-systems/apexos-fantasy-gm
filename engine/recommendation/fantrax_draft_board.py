"""Offline, deterministic Fantrax SPAMML draft-board decision service.

The module accepts only caller-supplied local CSV paths/handles and a vetted
SPAMML configuration result. It has no provider, network, live-state, or
automated-draft behaviour.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any, Iterable, Mapping, TextIO

from engine.draft.spamml_configuration import load_spamml_configuration

REQUIRED_HEADERS = ("Player", "Team", "Position", "RkOv", "FPts", "FP/G", "ADP", "Bye")
BASE_REASON_CODES = (
    "USER_PROVIDED_LOCAL_SNAPSHOT", "PROVIDER_LEAGUE_SCORE_NOT_DECOMPOSABLE",
    "EXPORT_TIMESTAMP_NOT_EMBEDDED", "PROVIDER_METHODOLOGY_VERSION_NOT_EMBEDDED",
    "TWO_POINT_PROJECTION_UNAVAILABLE", "ADP_MARKET_CONTEXT_ONLY",
    "PLANNED_SCHEDULE_ONLY", "MANUAL_LIVE_STATE_REQUIRED",
)
POOL_ORDER = ("QB", "RB", "REC", "K", "D_O")


class FantraxBoardError(ValueError):
    """A fail-closed validation error containing an operator-safe reason code."""


@dataclass(frozen=True)
class BoardOptions:
    scarcity_weight: float = 2.0
    roster_fit_weight: float = 1.0
    early_kicker_wait_cost_threshold: float = 3.0
    early_defense_advantage_threshold: float = 4.0
    optimizer_version: str = "fantrax-marginal-value-v0.1"


def _as_text(source: str | Path | TextIO) -> TextIO:
    if hasattr(source, "read"):
        return source  # type: ignore[return-value]
    return Path(source).open("r", encoding="utf-8-sig", newline="")


def read_fantrax_csv(source: str | Path | TextIO) -> list[dict[str, str]]:
    """Read a caller-provided local Fantrax CSV and preserve every source field."""
    close_after = not hasattr(source, "read")
    stream = _as_text(source)
    try:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != REQUIRED_HEADERS:
            raise FantraxBoardError("SOURCE_HEADER_INVALID")
        rows = [dict(row) for row in reader]
    except (csv.Error, UnicodeDecodeError, OSError) as exc:
        raise FantraxBoardError("SOURCE_ROW_INVALID") from exc
    finally:
        if close_after:
            stream.close()
    if not rows:
        raise FantraxBoardError("SOURCE_INPUT_MISSING")
    for row in rows:
        if any(row.get(column) is None for column in REQUIRED_HEADERS):
            raise FantraxBoardError("SOURCE_ROW_INVALID")
        try:
            float(row["FPts"])
            int(float(row["RkOv"]))
        except (TypeError, ValueError) as exc:
            raise FantraxBoardError("SOURCE_ROW_INVALID") from exc
    return rows


def normalize_pool(raw_position: str) -> tuple[str, list[str]]:
    position = raw_position.strip().upper()
    aliases = {"QB": "QB", "RB": "RB", "HB": "RB", "FB": "RB", "WR": "REC", "TE": "REC",
               "WT": "REC", "REC": "REC", "K": "K", "KCK": "K", "DST": "D_O", "D_O": "D_O", "TEAM": "D_O"}
    if position not in aliases:
        raise FantraxBoardError("SOURCE_ROW_INVALID")
    codes: list[str] = []
    if position == "WT": codes.append("WT_NORMALIZED_TO_REC")
    if position == "DST": codes.append("DST_NORMALIZED_TO_D_O")
    return aliases[position], codes


def _pool_demands(configuration: Mapping[str, Any]) -> dict[str, int]:
    starters, team_count = configuration["starter_counts"], int(configuration["team_count"])
    demand = {"QB": team_count * int(starters["QB"]), "RB": team_count * int(starters["RB"]),
              "REC": team_count * int(starters["REC"]), "K": team_count * int(starters["KCK"]),
              "D_O": team_count * int(starters["D_O"])}
    if demand != {"QB": 16, "RB": 32, "REC": 48, "K": 16, "D_O": 16}:
        raise FantraxBoardError("CONFIGURATION_REJECTED")
    return demand


def _rank_key(item: Mapping[str, Any]) -> tuple[float, int, str]:
    return (-float(item["provider_projected_score"]), int(item["provider_rank"]), str(item["player"]))


def _next_pick(sequence: Iterable[int], current_pick: int) -> int | None:
    return next((pick for pick in sequence if pick > current_pick), None)


def _round(current_pick: int) -> int:
    if not 1 <= current_pick <= 128:
        raise FantraxBoardError("CONFIGURATION_REJECTED")
    return (current_pick - 1) // 16 + 1


def _source_item(raw: Mapping[str, str], state: str) -> dict[str, Any]:
    pool, codes = normalize_pool(raw["Position"])
    team, player = raw["Team"].strip(), raw["Player"].strip()
    if pool == "D_O" and not team: codes.append("DST_TEAM_LABEL_NULL_ALLOWED")
    if player.upper() == "N/A" or team.upper() == "N/A": codes.append("IDENTITY_OR_TEAM_REVIEW")
    return {"player": player, "team": raw["Team"], "raw_position": raw["Position"], "normalized_position_pool": pool,
            "provider_rank": int(float(raw["RkOv"])), "provider_projected_score": float(raw["FPts"]),
            "ADP": raw["ADP"], "availability_state": state, "raw_source_columns": dict(raw), "reason_codes": codes}


def build_board(
    projection_rows: Iterable[Mapping[str, str]], *, current_pick: int,
    manual_availability: Mapping[str, str] | None = None,
    filled_pools: Iterable[str] = (), options: BoardOptions = BoardOptions(),
) -> dict[str, Any]:
    """Build a deterministic board using the adapter's planned sequence only."""
    configuration_result = load_spamml_configuration()
    if configuration_result.status != "valid" or configuration_result.configuration is None:
        raise FantraxBoardError("CONFIGURATION_REJECTED")
    config = configuration_result.configuration
    sequence = tuple(config["planned_pick_sequence"])
    if not sequence or current_pick not in sequence:
        raise FantraxBoardError("CONFIGURATION_REJECTED")
    demand = _pool_demands(config)
    availability = manual_availability or {}
    slots = {"QB": 1, "RB": 2, "REC": 3, "K": 1, "D_O": 1}
    for pool in filled_pools:
        if pool not in slots: raise FantraxBoardError("CONFIGURATION_REJECTED")
        slots[pool] = 0
    items = [_source_item(row, availability.get(row["Player"], "available")) for row in projection_rows]
    if any(item["availability_state"] not in {"available", "manually_drafted", "manually_excluded"} for item in items):
        raise FantraxBoardError("CONFIGURATION_REJECTED")
    by_pool = {pool: sorted([item for item in items if item["normalized_position_pool"] == pool], key=_rank_key) for pool in POOL_ORDER}
    replacement = {pool: (by_pool[pool][min(demand[pool], len(by_pool[pool])) - 1]["provider_projected_score"] if by_pool[pool] else 0.0) for pool in POOL_ORDER}
    next_pick = _next_pick(sequence, current_pick)
    gap = (next_pick - current_pick - 1) if next_pick else 0
    open_demand = sum(demand[pool] for pool in POOL_ORDER if slots[pool])
    expected_taken = {pool: (max(1, ceil(gap * demand[pool] / open_demand)) if gap and open_demand else 0) for pool in POOL_ORDER}
    normal_waits: list[float] = []
    for pool in ("QB", "RB", "REC"):
        available = [item for item in by_pool[pool] if item["availability_state"] == "available"]
        if slots[pool] and available:
            expected = available[min(expected_taken[pool], len(available) - 1)]
            normal_waits.append(available[0]["provider_projected_score"] - expected["provider_projected_score"])
    max_normal_wait = max(normal_waits, default=0.0)
    normal_slots_filled = all(slots[pool] == 0 for pool in ("QB", "RB", "REC"))
    current_round = _round(current_pick)
    entries: list[dict[str, Any]] = []
    for pool in POOL_ORDER:
        available_pool = [item for item in by_pool[pool] if item["availability_state"] == "available"]
        for position_rank, item in enumerate(by_pool[pool], start=1):
            entry, codes = dict(item), list(BASE_REASON_CODES) + list(item["reason_codes"])
            entry.update({"position_rank": position_rank, "replacement_anchor_score": replacement[pool],
                          "generic_replacement_value": max(0.0, item["provider_projected_score"] - replacement[pool]),
                          "remaining_slot_demand": slots[pool], "available_player_count_by_pool": len(available_pool),
                          "scarcity_pressure": slots[pool] / len(available_pool) if available_pool else 0.0,
                          "roster_fit_score": (1.0 / slots[pool]) if slots[pool] else 0.0,
                          "ADP_market_context_only": True,
                          "eligible": item["availability_state"] == "available" and bool(slots[pool])})
            if item["availability_state"] != "available": codes.append("PLAYER_MANUALLY_UNAVAILABLE")
            if not slots[pool]: codes.append("FILLED_SLOT_INELIGIBLE")
            next_option, wait_cost = None, 0.0
            if entry["eligible"]:
                alternatives = [candidate for candidate in available_pool if candidate["player"] != item["player"]]
                if alternatives:
                    next_option = alternatives[min(expected_taken[pool], len(alternatives) - 1)]
                    wait_cost = item["provider_projected_score"] - next_option["provider_projected_score"]
                codes.extend(("NEXT_PICK_WAIT_COST", "REPLACEMENT_VALUE", "ROSTER_FIT"))
                if entry["scarcity_pressure"] >= 1.0: codes.append("REMAINING_SLOT_SCARCITY")
            entry["expected_next_pick_option"] = ({"player": next_option["player"], "provider_projected_score": next_option["provider_projected_score"]} if next_option else None)
            entry["next_pick_wait_cost"] = wait_cost
            entry["early_position_suppression_status"] = "NOT_SUPPRESSED"
            penalty = 0.0
            if entry["eligible"] and pool == "K" and current_round < 6:
                exception = (normal_slots_filled or wait_cost > max_normal_wait) and wait_cost >= options.early_kicker_wait_cost_threshold
                if exception:
                    codes.append("EARLY_KICKER_SCARCITY_EXCEPTION"); entry["early_position_suppression_status"] = "EARLY_KICKER_SCARCITY_EXCEPTION"
                else:
                    codes.append("KICKER_SUPPRESSED_BEFORE_ROUND_6"); entry["early_position_suppression_status"] = "KICKER_SUPPRESSED_BEFORE_ROUND_6"; penalty = 1_000_000.0
            if entry["eligible"] and pool == "D_O" and current_round < 8:
                exception = wait_cost >= max_normal_wait + options.early_defense_advantage_threshold
                if exception:
                    codes.append("EARLY_DEFENSE_SCARCITY_EXCEPTION"); entry["early_position_suppression_status"] = "EARLY_DEFENSE_SCARCITY_EXCEPTION"
                else:
                    codes.append("DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND"); entry["early_position_suppression_status"] = "DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND"; penalty = 1_000_000.0
            entry["remaining_slot_scarcity_pressure"] = options.scarcity_weight * entry["scarcity_pressure"]
            entry["valid_roster_fit_score"] = options.roster_fit_weight * entry["roster_fit_score"]
            entry["early_position_suppression_penalty"] = penalty
            entry["recommended_pick_value"] = (
                wait_cost
                + entry["generic_replacement_value"]
                + entry["remaining_slot_scarcity_pressure"]
                + entry["valid_roster_fit_score"]
                - entry["early_position_suppression_penalty"]
            ) if entry["eligible"] else None
            entry["recommendation_reason_codes"] = sorted(set(codes))
            entry["next_pick_contingency"] = (f"If unavailable at planned pick {next_pick}, use {next_option['player']}." if next_option and next_pick else "No later planned manager pick.")
            entries.append(entry)
    entries.sort(key=lambda item: (item["recommended_pick_value"] is None, -(item["recommended_pick_value"] or -1_000_001), item["provider_rank"], item["player"]))
    suppressed = {"KICKER_SUPPRESSED_BEFORE_ROUND_6", "DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND"}
    recommendation = next((item for item in entries if item["eligible"] and item["early_position_suppression_status"] not in suppressed), None)
    if recommendation is None: raise FantraxBoardError("CONFIGURATION_REJECTED")
    alternatives = {pool: next((item for item in entries if item["normalized_position_pool"] == pool and item["eligible"] and item["early_position_suppression_status"] == "NOT_SUPPRESSED"), None) for pool in POOL_ORDER if slots[pool]}
    decision_inputs = {
        "players": [{"player": item["player"], "team": item["team"], "raw_position": item["raw_position"],
                     "normalized_position_pool": item["normalized_position_pool"], "provider_rank": item["provider_rank"],
                     "provider_projected_score": item["provider_projected_score"], "ADP": item["ADP"],
                     "availability_state": item["availability_state"], "raw_source_columns": item["raw_source_columns"],
                     "source_reason_codes": item["reason_codes"]} for item in items],
        "pool_demands": demand, "starter_slots": {"QB": 1, "RB": 2, "REC": 3, "K": 1, "D_O": 1},
        "planned_pick_sequence": list(sequence), "options": {"scarcity_weight": options.scarcity_weight,
        "roster_fit_weight": options.roster_fit_weight, "early_kicker_wait_cost_threshold": options.early_kicker_wait_cost_threshold,
        "early_defense_advantage_threshold": options.early_defense_advantage_threshold}, "base_reason_codes": list(BASE_REASON_CODES),
    }
    return {"current_pick": current_pick, "next_manager_pick": next_pick, "planned_pick_sequence": list(sequence),
            "pool_demands": demand, "remaining_required_slots": slots, "board": entries, "recommendation": recommendation,
            "alternatives_by_open_pool": alternatives, "reason_codes": list(BASE_REASON_CODES),
            "data_freshness_status": "degraded", "source_mode": "user_provided_local_snapshot",
            "export_timestamp_not_embedded": True, "provider_score_not_event_decomposable": True,
            "limitations": list(configuration_result.known_limitations) + ["Provider FPts is not decomposed into raw scoring events.", "Manual availability is local state, not live provider state."],
            "configuration_version": config["league_rules_version"], "optimizer_version": options.optimizer_version,
            "decision_inputs": decision_inputs}
