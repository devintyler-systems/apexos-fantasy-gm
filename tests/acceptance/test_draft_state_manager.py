"""
Acceptance tests — B-05 Draft State Manager (Issue #11, contract v0.2-correction).

T01-T13, including 3 mandatory negative-path tests: T11 (override never mutates
original), T12 (undo CHECK constraint rejects partial audit fills), T13
(correction is additive-only).
"""
from __future__ import annotations

import sqlite3

import pytest

from engine.draft_state.schema import create_schema
from engine.draft_state import repository
from engine.draft_state.manager import DraftStateManager
from engine.canonical.schema import create_schema as create_canonical_schema
from engine.canonical.repository import insert_team, insert_player, add_player_alias

B04_MAP_VERSION = "v1.2-correction"
LEAGUE_ID = "spamml-2026"


@pytest.fixture()
def draft_conn():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    yield conn
    conn.close()


@pytest.fixture()
def canonical_conn():
    conn = sqlite3.connect(":memory:")
    create_canonical_schema(conn)
    insert_team(conn, "SF", "San Francisco 49ers", "test_fixture")
    insert_player(conn, "player-aaa", "Test Player A", "WR", "test_fixture", valid_positions={"WR"}, nfl_team_id="SF")
    insert_player(conn, "player-bbb", "Test Player B", "TE", "test_fixture", valid_positions={"TE"}, nfl_team_id="SF")
    add_player_alias(conn, raw_name="Clean Name", source_system="manual_entry", candidate_player_id="player-aaa")
    add_player_alias(conn, raw_name="Ambiguous Name", source_system="manual_entry", candidate_player_id="player-aaa")
    add_player_alias(conn, raw_name="Ambiguous Name", source_system="manual_entry", candidate_player_id="player-bbb")
    yield conn
    conn.close()


@pytest.fixture()
def manager(draft_conn, canonical_conn):
    return DraftStateManager(draft_conn, canonical_conn, "session-1", LEAGUE_ID, B04_MAP_VERSION)


def test_schema_creates_three_draft_state_tables(draft_conn):
    cur = draft_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert {"draft_pick_entries", "draft_session_state", "draft_pick_overrides"} <= tables


def test_t01_accepted_entry_matches_expected_sequence(manager):
    result = manager.submit_pick(1, "Clean Name")
    assert result["status"] == "accepted"
    assert result["normalized_player_id"] == "player-aaa"


def test_t02_out_of_sequence_entry_rejected(manager):
    result = manager.submit_pick(5, "Clean Name")
    assert result["status"] == "rejected_sequence_mismatch"
    assert result["expected_pick_number"] == 1


def test_t03_unresolved_identity_halts(manager):
    result = manager.submit_pick(1, "Totally Unknown Player")
    assert result["status"] == "rejected_identity_unresolved"


def test_t04_ambiguous_identity_halts_with_candidates(manager):
    result = manager.submit_pick(1, "Ambiguous Name")
    assert result["status"] == "rejected_identity_ambiguous"
    assert set(result["candidates"]) == {"player-aaa", "player-bbb"}


def test_t05_every_accepted_pick_persisted_immediately(draft_conn, canonical_conn):
    mgr = DraftStateManager(draft_conn, canonical_conn, "session-persist", LEAGUE_ID, B04_MAP_VERSION)
    mgr.submit_pick(1, "Clean Name")
    row = draft_conn.execute(
        "SELECT validation_status FROM draft_pick_entries WHERE draft_session_id='session-persist'"
    ).fetchone()
    assert row[0] == "accepted"


def test_t06_resume_requires_explicit_confirmation(draft_conn, canonical_conn):
    mgr = DraftStateManager(draft_conn, canonical_conn, "session-resume", LEAGUE_ID, B04_MAP_VERSION)
    mgr.submit_pick(1, "Clean Name")
    mgr2 = DraftStateManager(draft_conn, canonical_conn, "session-resume", LEAGUE_ID, B04_MAP_VERSION)
    with pytest.raises(repository.SessionNotResumedError):
        mgr2.submit_pick(2, "Ambiguous Name")
    mgr2.confirm_resume()
    result = mgr2.submit_pick(2, "Ambiguous Name")
    assert result["status"] == "rejected_identity_ambiguous"


def test_t07_undo_affects_only_immediately_preceding_pick(manager):
    manager.submit_pick(1, "Clean Name")
    manager.submit_pick(2, "Ambiguous Name")  # rejected, not accepted
    result = manager.undo_last("devin", "test undo")
    assert result["status"] == "undone"
    row = manager.conn.execute(
        "SELECT undone_at, undone_by, undone_reason FROM draft_pick_entries WHERE entry_id=?",
        (result["entry_id"],),
    ).fetchone()
    assert all(v is not None for v in row)


def test_t08_degraded_mode_flag_is_honest(manager):
    manager.set_degraded(True)
    row = manager.conn.execute(
        "SELECT degraded_mode FROM draft_session_state WHERE draft_session_id=?",
        (manager.draft_session_id,),
    ).fetchone()
    assert row[0] == 1


def test_t09_no_hardcoded_positions_in_canonical_layer(canonical_conn):
    from engine.canonical.schema import load_valid_positions
    positions = load_valid_positions("contracts/league_rules/spamml-2026-v0.3.yaml")
    assert positions == {"QB", "HB", "FB", "WR", "TE", "K", "TEAM"}


def test_t10_raw_normalized_timestamp_provenance_are_distinct_fields(manager):
    manager.submit_pick(1, "Clean Name")
    row = manager.conn.execute(
        "SELECT raw_player_name, normalized_player_id, entry_source, validation_status, entered_at "
        "FROM draft_pick_entries WHERE pick_number=1"
    ).fetchone()
    assert row[0] == "Clean Name"
    assert row[1] == "player-aaa"
    assert row[2] == "manual_entry"
    assert row[3] == "accepted"
    assert row[4] is not None


def test_t11_override_creates_new_row_never_mutates_original(manager):
    rejected = manager.submit_pick(5, "Clean Name")
    original_id = rejected["entry_id"]
    original_before = manager.conn.execute(
        "SELECT validation_status FROM draft_pick_entries WHERE entry_id=?", (original_id,)
    ).fetchone()[0]
    result = manager.override_pick(
        original_entry_id=original_id, pick_number=1, raw_player_name="Clean Name",
        normalized_player_id="player-aaa", override_reason="commissioner correction",
        overridden_by="devin",
    )
    assert result["status"] == "accepted"
    original_after = manager.conn.execute(
        "SELECT validation_status FROM draft_pick_entries WHERE entry_id=?", (original_id,)
    ).fetchone()[0]
    assert original_after == original_before == "rejected_sequence_mismatch"
    override_row = manager.conn.execute(
        "SELECT original_entry_id, new_entry_id FROM draft_pick_overrides WHERE original_entry_id=?",
        (original_id,),
    ).fetchone()
    assert override_row[0] == original_id
    assert override_row[1] == result["entry_id"]


def test_t11b_override_rejects_empty_reason_and_system_identity(manager):
    rejected = manager.submit_pick(5, "Clean Name")
    with pytest.raises(repository.InvalidOverrideError):
        manager.override_pick(
            original_entry_id=rejected["entry_id"], pick_number=1, raw_player_name="Clean Name",
            normalized_player_id="player-aaa", override_reason="", overridden_by="devin",
        )
    with pytest.raises(repository.InvalidOverrideError):
        manager.override_pick(
            original_entry_id=rejected["entry_id"], pick_number=1, raw_player_name="Clean Name",
            normalized_player_id="player-aaa", override_reason="valid reason", overridden_by="system",
        )


def test_t12_undo_check_constraint_rejects_partial_audit_fill(draft_conn):
    with pytest.raises(sqlite3.IntegrityError):
        draft_conn.execute(
            "INSERT INTO draft_pick_entries (draft_session_id, pick_number, raw_player_name, "
            "validation_status, b04_map_version, entered_at, created_at, undone_at) "
            "VALUES ('x', 1, 'Test', 'accepted', 'v1', 'now', 'now', 'now')"
        )


def test_t13_correction_is_additive_only_original_unchanged(manager):
    ambiguous = manager.submit_pick(1, "Ambiguous Name")
    original_id = ambiguous["entry_id"]
    result = manager.correct_identity(
        original_entry_id=original_id, pick_number=1, raw_player_name="Ambiguous Name",
        normalized_player_id="player-bbb",
    )
    assert result["status"] == "accepted"
    assert result["correction_of_entry_id"] == original_id
    original_after = manager.conn.execute(
        "SELECT validation_status, normalized_player_id FROM draft_pick_entries WHERE entry_id=?",
        (original_id,),
    ).fetchone()
    assert original_after[0] == "rejected_identity_ambiguous"
    assert original_after[1] is None
