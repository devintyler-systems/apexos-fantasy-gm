"""Deterministic CI validation for the SPAMML 2026 draft-seat contract.

This module is validation infrastructure only. It is intentionally not wired into
runtime draft state, recommendations, storage, UI, or platform integrations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml


EXPECTED_SEATS = tuple(range(1, 17))
EXPECTED_MANAGER_NAME = "Professor FleX"
EXPECTED_MANAGER_SEAT = 4
EXPECTED_FORMAT = "non_standard_snake"
EXPECTED_LOCAL_TIME = datetime(2026, 8, 30, 16, 0, 0)
EXPECTED_UTC = "2026-08-30T23:00:00Z"
EXPECTED_ZONE = "America/Los_Angeles"
EXPECTED_OFFSET = "-07:00"
EXPECTED_ABBREVIATION = "PDT"
ROUND_ORDER_AUTHORITIES = (
    "contracts/draft/draft-round-order-map-contract-v1.0.md",
    "contracts/draft/draft-round-order-map-contract-v1.1-clarification.md",
    "contracts/draft/draft-round-order-map-contract-v1.2-correction.md",
)
_MISSING = object()


def _display_path(path: str | Path) -> str:
    return Path(path).as_posix()


def _actual(value: Any) -> str:
    return "<missing>" if value is _MISSING else repr(value)


class ContractValidationError(ValueError):
    """A deterministic, criterion- and YAML-path-rich contract failure."""

    def __init__(
        self,
        criterion: str,
        artifact_path: str | Path,
        field_path: str,
        actual: Any,
        expected: str,
        *,
        detail: str | None = None,
    ) -> None:
        self.criterion = criterion
        self.artifact_path = _display_path(artifact_path)
        self.field_path = field_path
        self.actual = actual
        self.expected = expected
        self.detail = detail
        message = (
            f"{criterion} | artifact={self.artifact_path} | field={field_path} | "
            f"actual={_actual(actual)} | expected={expected}"
        )
        if detail:
            message = f"{message} | {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class DraftActivityClassification:
    """Evidence-rich DSA-07 classification derived from explicit state inputs."""

    artifact_path: str
    raw_selection_state: Any
    derived_classification: str
    live_claim_allowed: bool
    missing_valid_selection_transition: bool
    missing_confirmed_real_time_pick_feed: bool

    def evidence_message(self) -> str:
        """Return stable evidence separating raw state from derived classification."""
        return (
            "DSA-07 | "
            f"artifact={self.artifact_path} | "
            "field=draft_state.selection_state | "
            f"raw_selection_state={self.raw_selection_state!r} | "
            f"derived_classification={self.derived_classification!r} | "
            f"live_claim_allowed={self.live_claim_allowed!r} | "
            f"missing_valid_selection_transition={self.missing_valid_selection_transition!r} | "
            f"missing_confirmed_real_time_pick_feed={self.missing_confirmed_real_time_pick_feed!r} | "
            "schedule, UTC time, timezone metadata, and clock status alone never establish live status"
        )


@dataclass(frozen=True)
class DraftSeatAssignmentValidation:
    """Stable summary returned after every DSA criterion passes."""

    manager_team_name: str
    manager_draft_seat: int
    activity_classification: str


def load_yaml_contract(path: str | Path) -> dict[str, Any]:
    """Load a YAML mapping using the repository-approved PyYAML safe loader."""
    artifact_path = Path(path)
    with artifact_path.open("r", encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict):
        raise ContractValidationError(
            "DSA-01",
            artifact_path,
            "$",
            document,
            "a YAML mapping at the document root",
        )
    return document


def _mapping(
    value: Any,
    criterion: str,
    artifact_path: str | Path,
    field_path: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractValidationError(
            criterion, artifact_path, field_path, value, "a YAML mapping"
        )
    return value


def _validate_dsa01(
    seat_contract: Mapping[str, Any], seat_path: str | Path
) -> list[Mapping[str, Any]]:
    assignments_value = seat_contract.get("seat_assignments", _MISSING)
    if not isinstance(assignments_value, list):
        raise ContractValidationError(
            "DSA-01",
            seat_path,
            "seat_assignments",
            assignments_value,
            "a list containing exactly 16 seat assignments",
        )

    assignments: list[Mapping[str, Any]] = []
    seats: list[int] = []
    first_index_by_seat: dict[int, int] = {}
    for index, value in enumerate(assignments_value):
        assignment = _mapping(value, "DSA-01", seat_path, f"seat_assignments[{index}]")
        assignments.append(assignment)
        seat = assignment.get("draft_seat", _MISSING)
        if type(seat) is not int or not 1 <= seat <= 16:
            raise ContractValidationError(
                "DSA-01",
                seat_path,
                f"seat_assignments[{index}].draft_seat",
                seat,
                "an integer draft seat in the inclusive range 1..16",
            )
        if seat in first_index_by_seat:
            raise ContractValidationError(
                "DSA-01",
                seat_path,
                f"seat_assignments[{index}].draft_seat",
                seat,
                f"a unique seat value; first occurrence is seat_assignments[{first_index_by_seat[seat]}].draft_seat",
            )
        first_index_by_seat[seat] = index
        seats.append(seat)

    missing = sorted(set(EXPECTED_SEATS) - set(seats))
    if len(assignments) != 16 or missing:
        raise ContractValidationError(
            "DSA-01",
            seat_path,
            "seat_assignments[*].draft_seat",
            {"entry_count": len(assignments), "missing_seats": missing},
            "exactly 16 assignments containing every integer seat 1..16 once",
        )
    return assignments


def _validate_dsa02(
    assignments: Sequence[Mapping[str, Any]], seat_path: str | Path
) -> None:
    first_index_by_name: dict[str, int] = {}
    for index, assignment in enumerate(assignments):
        team_name = assignment.get("team_name", _MISSING)
        if not isinstance(team_name, str) or not team_name.strip():
            raise ContractValidationError(
                "DSA-02",
                seat_path,
                f"seat_assignments[{index}].team_name",
                team_name,
                "a non-empty, non-whitespace display name",
            )
        if team_name in first_index_by_name:
            raise ContractValidationError(
                "DSA-02",
                seat_path,
                f"seat_assignments[{index}].team_name",
                team_name,
                f"an exact-display-name unique value; first occurrence is seat_assignments[{first_index_by_name[team_name]}].team_name",
            )
        first_index_by_name[team_name] = index


def _validate_dsa03(
    seat_contract: Mapping[str, Any],
    assignments: Sequence[Mapping[str, Any]],
    seat_path: str | Path,
) -> None:
    marked = [
        (index, assignment)
        for index, assignment in enumerate(assignments)
        if assignment.get("is_manager_team") is True
    ]
    if len(marked) != 1:
        marked_paths = [f"seat_assignments[{index}].is_manager_team" for index, _ in marked]
        raise ContractValidationError(
            "DSA-03",
            seat_path,
            "seat_assignments[*].is_manager_team",
            marked_paths,
            "exactly one literal boolean true manager marker",
        )

    index, manager_assignment = marked[0]
    marked_name = manager_assignment.get("team_name", _MISSING)
    if marked_name != EXPECTED_MANAGER_NAME:
        raise ContractValidationError(
            "DSA-03",
            seat_path,
            f"seat_assignments[{index}].team_name",
            marked_name,
            repr(EXPECTED_MANAGER_NAME),
        )
    marked_seat = manager_assignment.get("draft_seat", _MISSING)
    if marked_seat != EXPECTED_MANAGER_SEAT:
        raise ContractValidationError(
            "DSA-03",
            seat_path,
            f"seat_assignments[{index}].draft_seat",
            marked_seat,
            f"manager seat {EXPECTED_MANAGER_SEAT}",
        )

    identity = _mapping(
        seat_contract.get("identity", _MISSING), "DSA-03", seat_path, "identity"
    )
    identity_name = identity.get("manager_team_name", _MISSING)
    if identity_name != EXPECTED_MANAGER_NAME or identity_name != marked_name:
        raise ContractValidationError(
            "DSA-03",
            seat_path,
            "identity.manager_team_name",
            identity_name,
            f"{EXPECTED_MANAGER_NAME!r} and equality with the marked team name {marked_name!r}",
        )
    identity_seat = identity.get("manager_draft_seat", _MISSING)
    if identity_seat != EXPECTED_MANAGER_SEAT or identity_seat != marked_seat:
        raise ContractValidationError(
            "DSA-03",
            seat_path,
            "identity.manager_draft_seat",
            identity_seat,
            f"seat {EXPECTED_MANAGER_SEAT} and equality with the marked draft seat {marked_seat!r}",
        )


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        return None
    return parsed.astimezone(timezone.utc)


def _validate_dsa04(
    seat_contract: Mapping[str, Any], seat_path: str | Path
) -> None:
    draft_state = _mapping(
        seat_contract.get("draft_state", _MISSING), "DSA-04", seat_path, "draft_state"
    )
    status = draft_state.get("draft_date_time_status", _MISSING)
    if status != "confirmed":
        raise ContractValidationError(
            "DSA-04",
            seat_path,
            "draft_state.draft_date_time_status",
            status,
            "'confirmed' for this canonical schedule",
        )

    provenance = _mapping(
        seat_contract.get("draft_date_time_provenance", _MISSING),
        "DSA-04",
        seat_path,
        "draft_date_time_provenance",
    )
    required_fields = (
        "source_type",
        "source_provider",
        "source_reference",
        "retrieved_at_utc",
        "effective_time_utc",
        "parser_version",
    )
    for field in required_fields:
        value = provenance.get(field, _MISSING)
        if not isinstance(value, str) or not value.strip():
            raise ContractValidationError(
                "DSA-04",
                seat_path,
                f"draft_date_time_provenance.{field}",
                value,
                "a non-empty explicit provenance value for a confirmed schedule",
            )

    retrieved = provenance["retrieved_at_utc"]
    if _parse_utc(retrieved) is None:
        raise ContractValidationError(
            "DSA-04",
            seat_path,
            "draft_date_time_provenance.retrieved_at_utc",
            retrieved,
            "an explicit ISO-8601 UTC timestamp",
        )

    effective = provenance["effective_time_utc"]
    draft_utc = draft_state.get("draft_date_time_utc", _MISSING)
    if _parse_utc(effective) is None or effective != draft_utc:
        raise ContractValidationError(
            "DSA-04",
            seat_path,
            "draft_date_time_provenance.effective_time_utc",
            effective,
            f"exact equality with draft_state.draft_date_time_utc actual={draft_utc!r}",
        )


def _find_embedded_pick_order(value: Any, path: str = "$") -> tuple[str, Any] | None:
    forbidden_keys = {"pick_order", "pick_sequence", "round_order", "pick_numbers"}
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = str(key) if path == "$" else f"{path}.{key}"
            if key in forbidden_keys and isinstance(child, list):
                return child_path, child
            found = _find_embedded_pick_order(child, child_path)
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _find_embedded_pick_order(child, f"{path}[{index}]")
            if found:
                return found
    return None


def _validate_dsa05(
    seat_contract: Mapping[str, Any],
    league_contract: Mapping[str, Any],
    seat_path: str | Path,
    league_path: str | Path,
) -> None:
    embedded = _find_embedded_pick_order(seat_contract)
    if embedded:
        field_path, value = embedded
        raise ContractValidationError(
            "DSA-05",
            seat_path,
            field_path,
            value,
            "no locally embedded pick-order list; derive picks only through the versioned round-order-map authority",
        )

    seat_draft = _mapping(
        seat_contract.get("draft_state", _MISSING), "DSA-05", seat_path, "draft_state"
    )
    league_draft = _mapping(
        league_contract.get("draft", _MISSING), "DSA-05", league_path, "draft"
    )
    seat_format = seat_draft.get("format", _MISSING)
    league_format = league_draft.get("format", _MISSING)
    if league_format != EXPECTED_FORMAT:
        raise ContractValidationError(
            "DSA-05",
            league_path,
            "draft.format",
            league_format,
            repr(EXPECTED_FORMAT),
        )
    if seat_format != league_format:
        raise ContractValidationError(
            "DSA-05",
            seat_path,
            "draft_state.format",
            seat_format,
            f"exact equality with League Rules v0.4 draft.format actual={league_format!r}",
        )

    artifact = _mapping(
        seat_contract.get("artifact", _MISSING), "DSA-05", seat_path, "artifact"
    )
    depends_on = artifact.get("depends_on", _MISSING)
    missing_authorities = (
        list(ROUND_ORDER_AUTHORITIES)
        if not isinstance(depends_on, list)
        else [authority for authority in ROUND_ORDER_AUTHORITIES if authority not in depends_on]
    )
    if missing_authorities:
        raise ContractValidationError(
            "DSA-05",
            seat_path,
            "artifact.depends_on",
            depends_on,
            f"delegation to every versioned round-order-map authority {list(ROUND_ORDER_AUTHORITIES)!r}; missing={missing_authorities!r}",
        )

    contract = _mapping(
        seat_contract.get("contract", _MISSING), "DSA-05", seat_path, "contract"
    )
    consumers = _mapping(
        contract.get("consumer_contract", _MISSING),
        "DSA-05",
        seat_path,
        "contract.consumer_contract",
    )
    adapter = _mapping(
        consumers.get("draft_recommendation_adapter", _MISSING),
        "DSA-05",
        seat_path,
        "contract.consumer_contract.draft_recommendation_adapter",
    )
    delegation = adapter.get("order_derivation", _MISSING)
    delegation_text = delegation.lower() if isinstance(delegation, str) else ""
    if "versioned draft-round order map" not in delegation_text or "do not derive" not in delegation_text:
        raise ContractValidationError(
            "DSA-05",
            seat_path,
            "contract.consumer_contract.draft_recommendation_adapter.order_derivation",
            delegation,
            "an explicit instruction to use the versioned draft-round order map and not derive pick order locally",
        )


def _validate_dsa06(
    seat_contract: Mapping[str, Any], seat_path: str | Path
) -> None:
    provenance = _mapping(
        seat_contract.get("draft_date_time_provenance", _MISSING),
        "DSA-06",
        seat_path,
        "draft_date_time_provenance",
    )
    expected_fields = {
        "timezone": EXPECTED_ZONE,
        "utc_offset": EXPECTED_OFFSET,
        "timezone_abbreviation": EXPECTED_ABBREVIATION,
    }
    for field, expected in expected_fields.items():
        value = provenance.get(field, _MISSING)
        if not isinstance(value, str):
            raise ContractValidationError(
                "DSA-06",
                seat_path,
                f"draft_date_time_provenance.{field}",
                value,
                f"a separate string field with value {expected!r}; timezone, UTC offset, and abbreviation must never be merged",
            )
        if value != expected:
            raise ContractValidationError(
                "DSA-06",
                seat_path,
                f"draft_date_time_provenance.{field}",
                value,
                repr(expected),
                detail="IANA zone, observed UTC offset, and display abbreviation are distinct fields",
            )

    try:
        zone = ZoneInfo(provenance["timezone"])
    except ZoneInfoNotFoundError as exc:
        raise ContractValidationError(
            "DSA-06",
            seat_path,
            "draft_date_time_provenance.timezone",
            provenance["timezone"],
            f"a valid IANA timezone, specifically {EXPECTED_ZONE!r}",
        ) from exc

    local = EXPECTED_LOCAL_TIME.replace(tzinfo=zone)
    converted = local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if converted != EXPECTED_UTC:
        raise ContractValidationError(
            "DSA-06",
            seat_path,
            "draft_date_time_provenance.effective_time_utc",
            converted,
            f"{EXPECTED_LOCAL_TIME.isoformat()} in {EXPECTED_ZONE} converts exactly to {EXPECTED_UTC}",
        )

    derived_offset = local.strftime("%z")
    derived_offset = f"{derived_offset[:3]}:{derived_offset[3:]}"
    if provenance["utc_offset"] != derived_offset:
        raise ContractValidationError(
            "DSA-06",
            seat_path,
            "draft_date_time_provenance.utc_offset",
            provenance["utc_offset"],
            f"observed offset {derived_offset!r} derived from {EXPECTED_ZONE} at the scheduled local time",
        )
    if provenance["timezone_abbreviation"] != local.tzname():
        raise ContractValidationError(
            "DSA-06",
            seat_path,
            "draft_date_time_provenance.timezone_abbreviation",
            provenance["timezone_abbreviation"],
            f"display abbreviation {local.tzname()!r} derived from {EXPECTED_ZONE} at the scheduled local time",
        )


def classify_draft_activity(
    seat_contract: Mapping[str, Any], seat_path: str | Path = "<memory>"
) -> DraftActivityClassification:
    """Classify activity without inferring live status from schedule or clock data."""
    draft_state = _mapping(
        seat_contract.get("draft_state", _MISSING), "DSA-07", seat_path, "draft_state"
    )
    selection_state = draft_state.get("selection_state", _MISSING)
    if selection_state == "not_started":
        return DraftActivityClassification(
            artifact_path=_display_path(seat_path),
            raw_selection_state=selection_state,
            derived_classification="non_live",
            live_claim_allowed=False,
            missing_valid_selection_transition=True,
            missing_confirmed_real_time_pick_feed=True,
        )
    if selection_state in {"degraded", "manual"}:
        return DraftActivityClassification(
            artifact_path=_display_path(seat_path),
            raw_selection_state=selection_state,
            derived_classification=str(selection_state),
            live_claim_allowed=False,
            missing_valid_selection_transition=True,
            missing_confirmed_real_time_pick_feed=True,
        )
    if selection_state in {"live", "in_progress"}:
        transition = draft_state.get("selection_transition")
        feed = draft_state.get("real_time_pick_feed")
        transition_valid = (
            isinstance(transition, Mapping)
            and transition.get("from_state") in {"not_started", "degraded", "manual"}
            and transition.get("to_state") == selection_state
            and isinstance(transition.get("transitioned_at_utc"), str)
            and _parse_utc(transition.get("transitioned_at_utc")) is not None
            and bool(transition.get("source_type"))
        )
        feed_valid = (
            isinstance(feed, Mapping)
            and feed.get("status") == "confirmed"
            and isinstance(feed.get("as_of_timestamp_utc"), str)
            and _parse_utc(feed.get("as_of_timestamp_utc")) is not None
            and bool(feed.get("source_type"))
        )
        if transition_valid and feed_valid:
            return DraftActivityClassification(
                artifact_path=_display_path(seat_path),
                raw_selection_state=selection_state,
                derived_classification=str(selection_state),
                live_claim_allowed=True,
                missing_valid_selection_transition=False,
                missing_confirmed_real_time_pick_feed=False,
            )
        return DraftActivityClassification(
            artifact_path=_display_path(seat_path),
            raw_selection_state=selection_state,
            derived_classification="degraded",
            live_claim_allowed=False,
            missing_valid_selection_transition=not transition_valid,
            missing_confirmed_real_time_pick_feed=not feed_valid,
        )
    raise ContractValidationError(
        "DSA-07",
        seat_path,
        "draft_state.selection_state",
        selection_state,
        "one of 'not_started', 'degraded', 'manual', 'live', or 'in_progress' under the explicit-transition rules",
    )


def _validate_dsa08(
    seat_contract: Mapping[str, Any],
    league_contract: Mapping[str, Any],
    seat_path: str | Path,
    league_path: str | Path,
) -> None:
    seat_draft = _mapping(
        seat_contract.get("draft_state", _MISSING), "DSA-08", seat_path, "draft_state"
    )
    league_draft = _mapping(
        league_contract.get("draft", _MISSING), "DSA-08", league_path, "draft"
    )
    clock = _mapping(
        league_draft.get("draft_clock_config", _MISSING),
        "DSA-08",
        league_path,
        "draft.draft_clock_config",
    )
    seat_status = seat_draft.get("draft_clock_status", _MISSING)
    timer_enabled = clock.get("timer_enabled", _MISSING)
    relation_holds = (
        type(timer_enabled) is bool
        and (seat_status == "confirmed_untimed") == (timer_enabled is False)
    )
    if not relation_holds:
        raise ContractValidationError(
            "DSA-08",
            seat_path,
            "draft_state.draft_clock_status",
            seat_status,
            "'confirmed_untimed' iff League Rules v0.4 draft.draft_clock_config.timer_enabled is false",
            detail=(
                f"league_artifact={_display_path(league_path)} | "
                "league_field=draft.draft_clock_config.timer_enabled | "
                f"league_actual={_actual(timer_enabled)} | "
                "authority=League Rules v0.4 is the sole clock authority; the seat-assignment value is a consistency mirror only"
            ),
        )


def validate_draft_seat_assignment(
    seat_artifact_path: str | Path,
    league_rules_path: str | Path,
) -> DraftSeatAssignmentValidation:
    """Validate DSA-01 through DSA-08 without deriving pick order or runtime state."""
    seat_contract = load_yaml_contract(seat_artifact_path)
    league_contract = load_yaml_contract(league_rules_path)

    assignments = _validate_dsa01(seat_contract, seat_artifact_path)
    _validate_dsa02(assignments, seat_artifact_path)
    _validate_dsa03(seat_contract, assignments, seat_artifact_path)
    _validate_dsa04(seat_contract, seat_artifact_path)
    _validate_dsa05(
        seat_contract, league_contract, seat_artifact_path, league_rules_path
    )
    _validate_dsa06(seat_contract, seat_artifact_path)
    activity = classify_draft_activity(seat_contract, seat_artifact_path)
    _validate_dsa08(
        seat_contract, league_contract, seat_artifact_path, league_rules_path
    )
    identity = seat_contract["identity"]
    return DraftSeatAssignmentValidation(
        manager_team_name=identity["manager_team_name"],
        manager_draft_seat=identity["manager_draft_seat"],
        activity_classification=activity.derived_classification,
    )
