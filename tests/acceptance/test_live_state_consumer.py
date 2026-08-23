from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

import pytest
import yaml

from engine.draft.live_state_consumer import (
    DEFAULT_LEAGUE_RULES_PATH,
    DEFAULT_SEAT_ARTIFACT_PATH,
    RuntimeDraftStateConsumer,
)
from engine.draft_state.schema import create_schema


NOW = datetime(2026, 8, 31, 20, 0, tzinfo=timezone.utc)

SNAPSHOT_KEYS = {
    "as_of_timestamp",
    "input_snapshot_id",
    "dsa_validator_version",
    "round_order_map_version",
    "league_rules_version",
    "current_pick_number",
    "on_the_clock_seat",
    "on_the_clock_manager",
    "live_status",
    "reason_codes",
    "data_freshness",
    "known_limitations",
    "degraded_banner_required",
}
DATA_FRESHNESS_KEYS = {
    "b05_session_age_seconds",
    "seat_assignment_artifact_age_seconds",
}
NON_DSA08_ERROR_FIXTURES = [
    pytest.param("dsa01_missing_seat.yaml", "DSA-01", id="dsa01-missing-seat"),
    pytest.param("dsa01_duplicate_seat.yaml", "DSA-01", id="dsa01-duplicate-seat"),
    pytest.param("dsa01_out_of_range_seat.yaml", "DSA-01", id="dsa01-out-of-range-seat"),
    pytest.param("dsa02_whitespace_team_name.yaml", "DSA-02", id="dsa02-whitespace-team-name"),
    pytest.param("dsa02_duplicate_team_name.yaml", "DSA-02", id="dsa02-duplicate-team-name"),
    pytest.param("dsa03_no_manager_marker.yaml", "DSA-03", id="dsa03-no-manager-marker"),
    pytest.param("dsa03_multiple_manager_markers.yaml", "DSA-03", id="dsa03-multiple-manager-markers"),
    pytest.param("dsa03_marked_name_seat_mismatch.yaml", "DSA-03", id="dsa03-marked-name-seat-mismatch"),
    pytest.param("dsa03_identity_mismatch.yaml", "DSA-03", id="dsa03-identity-mismatch"),
    pytest.param("dsa04_missing_provenance.yaml", "DSA-04", id="dsa04-missing-provenance"),
    pytest.param("dsa04_effective_utc_mismatch.yaml", "DSA-04", id="dsa04-effective-utc-mismatch"),
    pytest.param("dsa05_embedded_pick_order.yaml", "DSA-05", id="dsa05-embedded-pick-order"),
    pytest.param("dsa05_format_mismatch.yaml", "DSA-05", id="dsa05-format-mismatch"),
    pytest.param("dsa05_missing_map_delegation.yaml", "DSA-05", id="dsa05-missing-map-delegation"),
    pytest.param("dsa06_invalid_timezone.yaml", "DSA-06", id="dsa06-invalid-timezone"),
    pytest.param("dsa06_merged_timezone_fields.yaml", "DSA-06", id="dsa06-merged-timezone-fields"),
]


def _session(updated_at: datetime = NOW, *, current_pick: int = 4, degraded: bool = False):
    connection = sqlite3.connect(":memory:")
    create_schema(connection)
    connection.execute(
        """INSERT INTO draft_session_state
           (draft_session_id, league_id, current_pick_number, degraded_mode, started_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            "draft-23",
            "SPAMML",
            current_pick,
            int(degraded),
            NOW.isoformat(),
            updated_at.isoformat(),
        ),
    )
    connection.commit()
    return connection


def _consumer(connection, **kwargs):
    return RuntimeDraftStateConsumer(
        connection, "draft-23", now=lambda: NOW, **kwargs
    )


def _live_assignment(tmp_path: Path) -> Path:
    with DEFAULT_SEAT_ARTIFACT_PATH.open(encoding="utf-8") as stream:
        artifact = yaml.safe_load(stream)
    artifact["draft_state"].update(
        {
            "selection_state": "live",
            "selection_transition": {
                "from_state": "not_started",
                "to_state": "live",
                "transitioned_at_utc": "2026-08-31T19:59:00Z",
                "source_type": "manual_league_manager_confirmation",
            },
            "real_time_pick_feed": {
                "status": "confirmed",
                "as_of_timestamp_utc": "2026-08-31T19:59:00Z",
                "source_type": "manual_entry",
            },
        }
    )
    path = tmp_path / "live-seat-assignment.yaml"
    path.write_text(yaml.safe_dump(artifact), encoding="utf-8")
    return path


def test_generic_snapshot_and_all_five_access_patterns(tmp_path):
    consumer = _consumer(_session(), seat_artifact_path=_live_assignment(tmp_path))

    snapshot = consumer.snapshot()

    assert set(snapshot) == SNAPSHOT_KEYS
    assert type(snapshot["as_of_timestamp"]) is str
    assert type(snapshot["input_snapshot_id"]) is str
    assert type(snapshot["dsa_validator_version"]) is str
    assert type(snapshot["round_order_map_version"]) is str
    assert type(snapshot["league_rules_version"]) is str
    assert type(snapshot["current_pick_number"]) is int
    assert type(snapshot["on_the_clock_seat"]) is int
    assert type(snapshot["on_the_clock_manager"]) is str
    assert type(snapshot["live_status"]) is str
    assert type(snapshot["reason_codes"]) is list
    assert all(type(reason) is str for reason in snapshot["reason_codes"])
    assert type(snapshot["data_freshness"]) is dict
    assert set(snapshot["data_freshness"]) == DATA_FRESHNESS_KEYS
    assert all(
        value is None or type(value) in {int, float}
        for value in snapshot["data_freshness"].values()
    )
    assert type(snapshot["known_limitations"]) is list
    assert all(type(limitation) is str for limitation in snapshot["known_limitations"])
    assert type(snapshot["degraded_banner_required"]) is bool
    assert snapshot["live_status"] == "LIVE"
    assert snapshot["current_pick_number"] == 4
    assert snapshot["on_the_clock_seat"] == 4
    assert snapshot["on_the_clock_manager"] == "Professor FleX"
    assert snapshot["degraded_banner_required"] is False
    assert snapshot["league_rules_version"] == "0.5"
    assert snapshot["data_freshness"]["b05_session_age_seconds"] == 0
    assert consumer.current_manager_seat() == 4
    assert consumer.next_manager_picks(3) == [4, 29, 44]
    assert consumer.pick_number_owner(17) == 16


def test_causality_trace_keeps_pick_ownership_delegated(tmp_path):
    consumer = _consumer(_session(current_pick=17), seat_artifact_path=_live_assignment(tmp_path))

    snapshot = consumer.snapshot()

    assert snapshot["on_the_clock_seat"] == consumer.pick_number_owner(17)
    assert consumer.next_picks_for_seat(4, 2) == [29, 44]


def test_time_integrity_uses_only_b05_session_age_for_staleness():
    consumer = _consumer(_session(NOW - timedelta(seconds=901)))

    snapshot = consumer.snapshot()

    assert snapshot["live_status"] == "DEGRADED"
    assert "B05_SESSION_STALE" in snapshot["reason_codes"]
    assert snapshot["data_freshness"]["seat_assignment_artifact_age_seconds"] is not None


def test_session_not_found_is_unknown():
    connection = sqlite3.connect(":memory:")
    create_schema(connection)

    snapshot = _consumer(connection).snapshot()

    assert snapshot["live_status"] == "UNKNOWN"
    assert "B05_SESSION_NOT_FOUND" in snapshot["reason_codes"]


def test_unparseable_b05_updated_at_surfaces_age_unavailable():
    connection = _session()
    connection.execute(
        "UPDATE draft_session_state SET updated_at = ? WHERE draft_session_id = ?",
        ("not-an-iso-timestamp", "draft-23"),
    )
    connection.commit()

    snapshot = _consumer(connection).snapshot()

    assert snapshot["live_status"] == "DEGRADED"
    assert "B05_SESSION_AGE_UNAVAILABLE" in snapshot["reason_codes"]


def test_reversibility_consumer_does_not_write_b05_or_artifacts(tmp_path):
    connection = _session()
    before = connection.execute("SELECT * FROM draft_session_state").fetchall()
    artifact_path = _live_assignment(tmp_path)
    before_artifact = artifact_path.read_bytes()

    _consumer(connection, seat_artifact_path=artifact_path).snapshot()

    assert connection.execute("SELECT * FROM draft_session_state").fetchall() == before
    assert artifact_path.read_bytes() == before_artifact


def test_live_draft_failure_dsa08_is_degraded_without_seat_or_manager():
    fixture = Path("tests/fixtures/draft_seat_assignment/dsa08_non_untimed_status.yaml")
    snapshot = _consumer(_session(), seat_artifact_path=fixture).snapshot()

    assert snapshot["live_status"] == "DEGRADED"
    assert snapshot["reason_codes"] == ["DSA08_CLOCK_MISMATCH"]
    assert snapshot["on_the_clock_seat"] is None
    assert snapshot["on_the_clock_manager"] is None
    assert snapshot["degraded_banner_required"] is True


@pytest.mark.parametrize(("fixture_name", "criterion"), NON_DSA08_ERROR_FIXTURES)
def test_live_draft_failure_other_dsa_errors_are_unknown_without_seat_or_manager(
    fixture_name, criterion
):
    fixture = Path("tests/fixtures/draft_seat_assignment") / fixture_name
    snapshot = _consumer(_session(), seat_artifact_path=fixture).snapshot()

    assert snapshot["live_status"] == "UNKNOWN"
    assert snapshot["reason_codes"] == [f"DSA_VALIDATION_FAILED_{criterion}"]
    assert snapshot["on_the_clock_seat"] is None
    assert snapshot["on_the_clock_manager"] is None
    assert snapshot["degraded_banner_required"] is True


def test_independent_acceptance_b05_degraded_and_no_live_evidence_are_surfaced():
    snapshot = _consumer(_session(degraded=True)).snapshot()

    assert snapshot["live_status"] == "DEGRADED"
    assert "B05_DEGRADED_MODE" in snapshot["reason_codes"]
    assert "DSA07_LIVE_CLAIM_NOT_ALLOWED" in snapshot["reason_codes"]
    assert snapshot["degraded_banner_required"] is True


def test_round_order_map_unavailable_is_unknown(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "engine.draft.live_state_consumer.build_full_map",
        lambda: {"league_rules_version": "PROVENANCE_UNAVAILABLE"},
    )
    snapshot = _consumer(_session(), seat_artifact_path=_live_assignment(tmp_path)).snapshot()

    assert snapshot["live_status"] == "UNKNOWN"
    assert snapshot["reason_codes"] == ["ROUND_ORDER_MAP_UNAVAILABLE"]
