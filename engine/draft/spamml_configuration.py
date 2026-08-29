"""Pure adapter for the canonical SPAMML 2026 planned configuration.

This module reads only the three approved repository authorities.  It never
contacts a provider, reads player evidence, derives a generic draft order, or
observes live draft state.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import yaml

from engine.draft.round_order_map import build_full_map


_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEAGUE_RULES_PATH = _ROOT / "contracts/league_rules/spamml-2026-v0.7.yaml"
DEFAULT_SEAT_ASSIGNMENT_PATH = (
    _ROOT / "contracts/draft/spamml-2026-draft-seat-assignment-v1.2.yaml"
)
DEFAULT_ROUND_ORDER_MAP_PATH = _ROOT / "contracts/draft/spamml-2026-round-order-map-v1.0.yaml"

CANONICAL_AUTHORITY_SHA256: Mapping[str, str] = MappingProxyType(
    {
        "league_rules": "2E7D99E59EAA4B7CFE480C3A0F5D01F6FD56E50070C0CAE1F4A5D5AED35D024D",
        "seat_assignment": "6DC66B845CCA9F3E47F89833BFB4857283D4834861A9F9626CC423FF627A6292",
        "round_order_map": "4F29AAAAC682D0D9126F18B6CA6FC8810420DFE6FF7D4E51BD5830F5B19B49C0",
    }
)
EXPECTED_MANAGER_NAME = "Professor FleX"
EXPECTED_MANAGER_SEAT = 4
EXPECTED_PICK_SEQUENCE = (4, 29, 45, 52, 68, 93, 109, 116)


@dataclass(frozen=True)
class AuthorityAttestation:
    """The exact local authority bytes that were approved for one result."""

    path: str
    sha256: str


@dataclass(frozen=True)
class SpammlConfigurationResult:
    """Immutable, machine-readable planned-configuration result."""

    status: str
    reason_codes: tuple[str, ...]
    known_limitations: tuple[str, ...]
    configuration: Mapping[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-ready copy without exposing mutable internals."""
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "known_limitations": list(self.known_limitations),
            "configuration": _plain(self.configuration) if self.configuration else None,
        }


class _Rejected(ValueError):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(child) for key, child in value.items()})
    if isinstance(value, list) or isinstance(value, tuple):
        return tuple(_freeze(child) for child in value)
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_plain(child) for child in value]
    return value


def _paths(
    league_rules_path: str | Path | None,
    seat_assignment_path: str | Path | None,
    round_order_map_path: str | Path | None,
) -> Mapping[str, Path]:
    return MappingProxyType(
        {
            "league_rules": Path(league_rules_path or DEFAULT_LEAGUE_RULES_PATH),
            "seat_assignment": Path(seat_assignment_path or DEFAULT_SEAT_ASSIGNMENT_PATH),
            "round_order_map": Path(round_order_map_path or DEFAULT_ROUND_ORDER_MAP_PATH),
        }
    )


def _attest(paths: Mapping[str, Path], expected_hashes: Mapping[str, str]) -> Mapping[str, AuthorityAttestation]:
    attestations: dict[str, AuthorityAttestation] = {}
    for key, path in paths.items():
        if key not in expected_hashes:
            raise _Rejected("AUTHORITY_EXPECTED_DIGEST_MISSING")
        try:
            actual = sha256(path.read_bytes()).hexdigest().upper()
        except OSError as exc:
            raise _Rejected("AUTHORITY_FILE_MISSING") from exc
        if actual != expected_hashes[key].upper():
            raise _Rejected(f"AUTHORITY_DIGEST_MISMATCH_{key.upper()}")
        attestations[key] = AuthorityAttestation(path.as_posix(), actual)
    return MappingProxyType(attestations)


def _load_yaml(path: Path) -> Mapping[str, Any]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise _Rejected("AUTHORITY_YAML_MALFORMED") from exc
    if not isinstance(document, Mapping):
        raise _Rejected("AUTHORITY_SCHEMA_MALFORMED")
    return document


def _mapping(value: Any, reason_code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _Rejected(reason_code)
    return value


def _validate_authorities(
    league_rules: Mapping[str, Any],
    seat_assignment: Mapping[str, Any],
    order_map: Mapping[str, Any],
) -> None:
    if (
        league_rules.get("league_id") != "spamml-2026"
        or league_rules.get("season") != 2026
        or league_rules.get("contract_version") != "0.7"
    ):
        raise _Rejected("LEAGUE_RULES_IDENTITY_OR_VERSION_MISMATCH")
    seat_artifact = _mapping(seat_assignment.get("artifact"), "SEAT_ASSIGNMENT_SCHEMA_MALFORMED")
    seat_identity = _mapping(seat_assignment.get("identity"), "SEAT_ASSIGNMENT_SCHEMA_MALFORMED")
    if seat_artifact.get("version") != "1.2" or seat_identity.get("season") != 2026:
        raise _Rejected("SEAT_ASSIGNMENT_IDENTITY_OR_VERSION_MISMATCH")
    map_artifact = _mapping(order_map.get("artifact"), "ROUND_ORDER_MAP_SCHEMA_MALFORMED")
    if map_artifact.get("version") != "1.0":
        raise _Rejected("ROUND_ORDER_MAP_VERSION_MISMATCH")
    if map_artifact.get("status") != "FINALIZED_OPERATOR_CONFIRMED":
        raise _Rejected("ROUND_ORDER_MAP_NOT_FINALIZED")


def _starter_constraints(roster: Mapping[str, Any]) -> tuple[Mapping[str, int], Mapping[str, tuple[str, ...]]]:
    starters = _mapping(roster.get("starters"), "ROSTER_SCHEMA_MALFORMED")
    eligibility = _mapping(roster.get("positional_eligibility"), "ROSTER_SCHEMA_MALFORMED")
    expected_slots = {"QB": 1, "RB1": 1, "RB2": 1, "REC1": 1, "REC2": 1, "REC3": 1, "KCK": 1, "D_O": 1}
    if {key: starters.get(key) for key in expected_slots} != expected_slots:
        raise _Rejected("ROSTER_CONSTRAINT_MISMATCH")
    if roster.get("total_slots") != 8 or roster.get("bench") != 0 or roster.get("flex_eligibility") != "none":
        raise _Rejected("ROSTER_CONSTRAINT_MISMATCH")
    normalized = {"QB": ("QB",), "RB": ("HB", "FB"), "REC": ("WR", "TE"), "KCK": ("K",), "D_O": ("TEAM",)}
    slot_keys = {"QB": "QB", "RB1": "RB", "RB2": "RB", "REC1": "REC", "REC2": "REC", "REC3": "REC", "KCK": "KCK", "D_O": "D_O"}
    if any(tuple(eligibility.get(slot, ())) != normalized[group] for slot, group in slot_keys.items()):
        raise _Rejected("ROSTER_ELIGIBILITY_MISMATCH")
    return _freeze({"QB": 1, "RB": 2, "REC": 3, "KCK": 1, "D_O": 1}), _freeze(normalized)


def _scoring_configuration(scoring: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, int]]:
    declared = {
        "passing": _mapping(scoring.get("passing"), "SCORING_SCHEMA_MALFORMED"),
        "rushing": _mapping(scoring.get("rushing"), "SCORING_SCHEMA_MALFORMED"),
        "receiving": _mapping(scoring.get("receiving"), "SCORING_SCHEMA_MALFORMED"),
        "kicking": _mapping(scoring.get("kicking"), "SCORING_SCHEMA_MALFORMED"),
        "defense_special_teams": _mapping(scoring.get("defense_special_teams"), "SCORING_SCHEMA_MALFORMED"),
    }
    required = {
        "passing.td_pass": 6, "passing.two_point_conversion_pass": 2,
        "rushing.td_rush": 6, "rushing.two_point_conversion_rush": 2,
        "receiving.td_reception": 6, "receiving.two_point_conversion_catch": 2,
    }
    if any(
        declared[group].get(field) != expected
        for dotted, expected in required.items()
        for group, field in (dotted.split(".", 1),)
    ):
        raise _Rejected("SCORING_CONSTRAINT_MISMATCH")
    zeros = {
        "passing.yards": declared["passing"].get("yards"),
        "passing.completions": declared["passing"].get("completions"),
        "passing.interceptions": declared["passing"].get("interceptions"),
        "rushing.yards": declared["rushing"].get("yards"),
        "rushing.carries": declared["rushing"].get("carries"),
        "receiving.yards": declared["receiving"].get("yards"),
        "receiving.receptions": declared["receiving"].get("receptions"),
    }
    if any(value != 0 for value in zeros.values()):
        raise _Rejected("DECLARED_ZERO_SCORING_MISMATCH")
    return _freeze(declared), _freeze(zeros)


def _pick_sequence(seat_assignment: Mapping[str, Any], default_map: bool) -> tuple[int, ...]:
    identity = _mapping(seat_assignment.get("identity"), "SEAT_ASSIGNMENT_SCHEMA_MALFORMED")
    if identity.get("manager_team_name") != EXPECTED_MANAGER_NAME or identity.get("manager_draft_seat") != EXPECTED_MANAGER_SEAT:
        raise _Rejected("MANAGER_SEAT_UNRESOLVED")
    if not default_map:
        raise _Rejected("ROUND_ORDER_MAP_LOADER_UNAVAILABLE")
    try:
        sequence = tuple(build_full_map()["position_pick_map"][str(EXPECTED_MANAGER_SEAT)])
    except (KeyError, RuntimeError, TypeError, ValueError) as exc:
        raise _Rejected("MANAGER_PICK_SEQUENCE_UNRESOLVED") from exc
    if sequence != EXPECTED_PICK_SEQUENCE:
        raise _Rejected("MANAGER_PICK_SEQUENCE_UNRESOLVED")
    return sequence


def load_spamml_configuration(
    *,
    league_rules_path: str | Path | None = None,
    seat_assignment_path: str | Path | None = None,
    round_order_map_path: str | Path | None = None,
    expected_hashes: Mapping[str, str] = CANONICAL_AUTHORITY_SHA256,
) -> SpammlConfigurationResult:
    """Load the static SPAMML configuration or return an explicit rejection.

    Alternate paths and expected hashes exist solely for fixture validation;
    production callers use the immutable canonical defaults.
    """
    paths = _paths(league_rules_path, seat_assignment_path, round_order_map_path)
    try:
        attestations = _attest(paths, expected_hashes)
        league_rules = _load_yaml(paths["league_rules"])
        seat_assignment = _load_yaml(paths["seat_assignment"])
        order_map = _load_yaml(paths["round_order_map"])
        _validate_authorities(league_rules, seat_assignment, order_map)
        roster = _mapping(league_rules.get("roster"), "ROSTER_SCHEMA_MALFORMED")
        scoring = _mapping(league_rules.get("scoring"), "SCORING_SCHEMA_MALFORMED")
        draft_state = _mapping(seat_assignment.get("draft_state"), "SEAT_ASSIGNMENT_SCHEMA_MALFORMED")
        starter_counts, slot_eligibility = _starter_constraints(roster)
        declared_scoring, declared_zeros = _scoring_configuration(scoring)
        sequence = _pick_sequence(seat_assignment, paths["round_order_map"] == DEFAULT_ROUND_ORDER_MAP_PATH)
        limitations = tuple(league_rules.get("known_limitations", ())) + tuple(seat_assignment.get("known_limitations", ()))
        configuration = _freeze(
            {
                "league_id": league_rules["league_id"],
                "season": league_rules["season"],
                "league_rules_version": league_rules["contract_version"],
                "team_count": league_rules["league_size"],
                "draft_format": league_rules["draft"]["format"],
                "total_roster_slots": roster["total_slots"],
                "bench_slots": roster["bench"],
                "starter_counts": starter_counts,
                "slot_eligibility": slot_eligibility,
                "flex_eligibility": None,
                "declared_scoring": declared_scoring,
                "declared_zero_fields": declared_zeros,
                "undefined_capability_gaps": {
                    "fumbles": None, "ir": None, "idp": None, "superflex": None,
                    "flex": None, "unlisted_scoring_behavior": None,
                },
                "manager_team_name": EXPECTED_MANAGER_NAME,
                "manager_draft_seat": EXPECTED_MANAGER_SEAT,
                "planned_start_timestamp_utc": draft_state.get("draft_date_time_utc"),
                "planned_pick_sequence": sequence,
                "planned_schedule_only": True,
                "authority_attestations": {
                    key: {"path": value.path, "sha256": value.sha256}
                    for key, value in attestations.items()
                },
            }
        )
    except _Rejected as exc:
        return SpammlConfigurationResult("rejected", (exc.reason_code,), (), None)
    return SpammlConfigurationResult("valid", (), limitations, configuration)
