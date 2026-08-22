"""Read-only runtime view of B-05 draft state and draft-seat authority.

The consumer deliberately joins existing authorities instead of deriving pick
order or altering draft state.  It is scoped to the SPAMML 2026 artifacts that
the draft-seat validator currently supports.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any, Callable, Mapping

import yaml

from engine.contracts.draft_seat_assignment import (
    ContractValidationError,
    classify_draft_activity,
    load_yaml_contract,
    validate_draft_seat_assignment,
)
from engine.draft.round_order_map import PROVENANCE_UNAVAILABLE, build_full_map


STALE_B05_SESSION_SECONDS = 900
DSA_VALIDATOR_VERSION = "1.1"
ROUND_ORDER_MAP_VERSION = "1.2"

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEAT_ARTIFACT_PATH = (
    _REPOSITORY_ROOT / "contracts" / "draft" / "spamml-2026-draft-seat-assignment-v1.1.yaml"
)
DEFAULT_LEAGUE_RULES_PATH = (
    _REPOSITORY_ROOT / "contracts" / "league_rules" / "spamml-2026-v0.5.yaml"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _age_seconds(value: Any, now: datetime) -> float | None:
    timestamp = _parse_timestamp(value)
    if timestamp is None:
        return None
    return max(0.0, (now - timestamp).total_seconds())


def _artifact_age_seconds(path: Path, now: datetime) -> float | None:
    try:
        modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None
    return max(0.0, (now - modified_at).total_seconds())


class RuntimeDraftStateConsumer:
    """Expose the five runtime draft-state access patterns without any writes."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        draft_session_id: str,
        *,
        seat_artifact_path: str | Path = DEFAULT_SEAT_ARTIFACT_PATH,
        league_rules_path: str | Path = DEFAULT_LEAGUE_RULES_PATH,
        staleness_threshold_seconds: int = STALE_B05_SESSION_SECONDS,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        if staleness_threshold_seconds != STALE_B05_SESSION_SECONDS:
            raise ValueError(
                "Only the Architect-approved B-05 session staleness threshold of 900 seconds is supported."
            )
        self._connection = connection
        self._draft_session_id = draft_session_id
        self._seat_artifact_path = Path(seat_artifact_path)
        self._league_rules_path = Path(league_rules_path)
        self._now = now

    def snapshot(self) -> dict[str, Any]:
        """Build the contract v1.2 snapshot at the time this method is called."""
        now = self._now().astimezone(timezone.utc)

        # The validator is intentionally the first authority called for every
        # snapshot.  A rejected assignment never contributes a seat or manager.
        try:
            validation = validate_draft_seat_assignment(
                self._seat_artifact_path, self._league_rules_path
            )
        except ContractValidationError as exc:
            snapshot = self._base_snapshot(
                now, None, _artifact_age_seconds(self._seat_artifact_path, now)
            )
            if exc.criterion == "DSA-08":
                snapshot.update(
                    live_status="DEGRADED",
                    reason_codes=["DSA08_CLOCK_MISMATCH"],
                    degraded_banner_required=True,
                )
            else:
                snapshot.update(
                    live_status="UNKNOWN",
                    reason_codes=[f"DSA_VALIDATION_FAILED_{exc.criterion}"],
                    degraded_banner_required=True,
                )
            return snapshot

        session = self._read_session()
        snapshot = self._base_snapshot(
            now, session, _artifact_age_seconds(self._seat_artifact_path, now)
        )
        if session is None:
            snapshot.update(
                live_status="UNKNOWN",
                reason_codes=["B05_SESSION_NOT_FOUND"],
                degraded_banner_required=True,
            )
            return snapshot

        try:
            order_map = build_full_map()
            if order_map.get("league_rules_version") == PROVENANCE_UNAVAILABLE:
                raise RuntimeError("Round-order-map provenance is unavailable")
            current_pick = session["current_pick_number"]
            on_clock_seat = order_map["pick_to_position_map"].get(str(current_pick))
            if on_clock_seat is None:
                raise RuntimeError("Current B-05 pick is not present in the round-order map")
        except (KeyError, RuntimeError, ValueError, TypeError):
            snapshot.update(
                live_status="UNKNOWN",
                reason_codes=["ROUND_ORDER_MAP_UNAVAILABLE"],
                degraded_banner_required=True,
            )
            return snapshot

        snapshot["on_the_clock_seat"] = on_clock_seat
        if on_clock_seat == validation.manager_draft_seat:
            snapshot["on_the_clock_manager"] = validation.manager_team_name

        reasons: list[str] = []
        status = "LIVE"
        banner_required = False

        # A second classifier call is made only for the richer evidence used in
        # degraded-banner reasoning; validation already supplied its string.
        if validation.activity_classification not in {"live", "in_progress"}:
            activity = classify_draft_activity(
                load_yaml_contract(self._seat_artifact_path), self._seat_artifact_path
            )
            status = "DEGRADED"
            banner_required = True
            reasons.append("DSA07_LIVE_CLAIM_NOT_ALLOWED")
            if activity.missing_valid_selection_transition:
                reasons.append("DSA07_MISSING_VALID_SELECTION_TRANSITION")
            if activity.missing_confirmed_real_time_pick_feed:
                reasons.append("DSA07_MISSING_CONFIRMED_REAL_TIME_PICK_FEED")

        if bool(session["degraded_mode"]):
            status = "DEGRADED"
            banner_required = True
            reasons.append("B05_DEGRADED_MODE")

        session_age = snapshot["data_freshness"]["b05_session_age_seconds"]
        if session_age is None:
            status = "DEGRADED"
            banner_required = True
            reasons.append("B05_SESSION_AGE_UNAVAILABLE")
        elif session_age > STALE_B05_SESSION_SECONDS:
            status = "DEGRADED"
            banner_required = True
            reasons.append("B05_SESSION_STALE")

        snapshot.update(
            live_status=status,
            reason_codes=reasons,
            degraded_banner_required=banner_required,
        )
        return snapshot

    def current_manager_seat(self) -> int | None:
        """Resolve the manager seat only when DSA validation passes."""
        try:
            return validate_draft_seat_assignment(
                self._seat_artifact_path, self._league_rules_path
            ).manager_draft_seat
        except ContractValidationError:
            return None

    def next_picks_for_seat(self, draft_seat: int, count: int) -> list[int]:
        """Resolve the next *count* picks through ``build_full_map`` only."""
        if count < 0:
            raise ValueError("count must be non-negative")
        session = self._read_session()
        if session is None:
            return []
        order_map = build_full_map()
        pick_numbers = order_map["position_pick_map"].get(str(draft_seat))
        if pick_numbers is None:
            raise ValueError("draft_seat is not represented by the round-order map")
        return [pick for pick in pick_numbers if pick >= session["current_pick_number"]][:count]

    def next_manager_picks(self, count: int) -> list[int]:
        """Resolve the manager's next picks, returning no values on DSA failure."""
        manager_seat = self.current_manager_seat()
        return [] if manager_seat is None else self.next_picks_for_seat(manager_seat, count)

    def pick_number_owner(self, pick_number: int) -> int | None:
        """Delegate pick-number ownership to the round-order-map authority."""
        return build_full_map()["pick_to_position_map"].get(str(pick_number))

    def _read_session(self) -> Mapping[str, Any] | None:
        cursor = self._connection.execute(
            """SELECT draft_session_id, current_pick_number, degraded_mode, updated_at
               FROM draft_session_state WHERE draft_session_id = ?""",
            (self._draft_session_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))

    def _base_snapshot(
        self,
        now: datetime,
        session: Mapping[str, Any] | None,
        seat_artifact_age: float | None,
    ) -> dict[str, Any]:
        updated_at = session["updated_at"] if session is not None else None
        current_pick = session["current_pick_number"] if session is not None else None
        return {
            "as_of_timestamp": _timestamp(now),
            "input_snapshot_id": f"{self._draft_session_id}:{updated_at or 'unavailable'}",
            "dsa_validator_version": DSA_VALIDATOR_VERSION,
            "round_order_map_version": ROUND_ORDER_MAP_VERSION,
            "league_rules_version": build_full_map()["league_rules_version"],
            "current_pick_number": current_pick,
            "on_the_clock_seat": None,
            "on_the_clock_manager": None,
            "live_status": "UNKNOWN",
            "reason_codes": [],
            "data_freshness": {
                "b05_session_age_seconds": _age_seconds(updated_at, now),
                "seat_assignment_artifact_age_seconds": seat_artifact_age,
            },
            "known_limitations": self._known_limitations(),
            "degraded_banner_required": False,
        }

    def _known_limitations(self) -> list[str]:
        try:
            artifact = load_yaml_contract(self._seat_artifact_path)
        except (OSError, yaml.YAMLError, ContractValidationError):
            return ["Seat-assignment limitations are unavailable because the artifact could not be read."]
        limitations = artifact.get("known_limitations")
        return list(limitations) if isinstance(limitations, list) else []


# Concise aliases make the boundary convenient for adapters without creating a
# second implementation path.
LiveStateConsumer = RuntimeDraftStateConsumer


def build_draft_state_snapshot(
    connection: sqlite3.Connection, draft_session_id: str, **kwargs: Any
) -> dict[str, Any]:
    return RuntimeDraftStateConsumer(connection, draft_session_id, **kwargs).snapshot()
