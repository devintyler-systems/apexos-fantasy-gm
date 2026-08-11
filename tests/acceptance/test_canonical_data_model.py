"""
Acceptance tests — B-02 Canonical Data Model (Issue #5).

Done-when criteria:
  Schema created; test inserts succeed for all 5 SPAMML position types
  (QB/RB/WR/TE/K per league rules v0.3).

TRACKED ASSUMPTION (flagged for reviewer / Devin, not silently resolved):
  contracts/league_rules/spamml-2026-v0.3.yaml expresses the two RB roster
  slots (RB1, RB2) via positional_eligibility codes HB and FB, not a
  literal "RB" string. This test therefore exercises HB and FB as the two
  concrete stored position codes standing in for the acceptance
  criterion's "RB" bucket, alongside QB, WR, TE, K (6 codes covering the
  5 named position groups). If "RB" should instead be a distinct stored
  position code, the League Rules Contract needs an explicit correction
  before this mapping is finalized.
"""
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

import pytest

from engine.canonical.schema import create_schema, load_valid_positions
from engine.canonical.repository import (
    PositionNotEligibleError,
    add_player_alias,
    get_alias_candidates,
    insert_game,
    insert_player,
    insert_team,
)

LEAGUE_RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts" / "league_rules" / "spamml-2026-v0.3.yaml"
)


@pytest.fixture()
def conn():
    connection = sqlite3.connect(":memory:")
    create_schema(connection)
    yield connection
    connection.close()


@pytest.fixture()
def valid_positions():
    return load_valid_positions(LEAGUE_RULES_PATH)


def test_schema_creates_four_canonical_tables(conn):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert {"dim_player", "dim_team", "dim_game", "player_alias_map"} <= tables


def test_five_spamml_position_types_insert_successfully(conn, valid_positions):
    insert_team(conn, team_id="SF", team_name="San Francisco 49ers",
                source_system="test_fixture")

    position_fixtures = [
        ("QB", "Test Quarterback"),
        ("HB", "Test Halfback"),
        ("FB", "Test Fullback"),
        ("WR", "Test Wide Receiver"),
        ("TE", "Test Tight End"),
        ("K", "Test Kicker"),
    ]
    for position, name in position_fixtures:
        insert_player(
            conn,
            player_id=str(uuid.uuid4()),
            full_name=name,
            position=position,
            source_system="test_fixture",
            valid_positions=valid_positions,
            nfl_team_id="SF",
        )

    cur = conn.execute("SELECT position FROM dim_player")
    inserted_positions = {row[0] for row in cur.fetchall()}
    assert {"QB", "HB", "FB", "WR", "TE", "K"} <= inserted_positions


def test_game_insert_references_teams(conn):
    insert_team(conn, "SF", "San Francisco 49ers", "test_fixture")
    insert_team(conn, "SEA", "Seattle Seahawks", "test_fixture")
    insert_game(conn, game_id="2026-W01-SF-SEA", season=2026, week=1,
                home_team_id="SF", away_team_id="SEA", source_system="test_fixture")
    cur = conn.execute("SELECT game_id FROM dim_game")
    assert cur.fetchone()[0] == "2026-W01-SF-SEA"


def test_position_not_in_league_rules_contract_is_rejected(conn, valid_positions):
    with pytest.raises(PositionNotEligibleError):
        insert_player(
            conn,
            player_id=str(uuid.uuid4()),
            full_name="Invalid Position Player",
            position="LB",
            source_system="test_fixture",
            valid_positions=valid_positions,
        )


def test_ambiguous_alias_produces_multiple_candidates_never_auto_merged(conn):
    insert_team(conn, "SF", "San Francisco 49ers", "test_fixture")
    player_a = str(uuid.uuid4())
    player_b = str(uuid.uuid4())
    insert_player(conn, player_a, "J. Smith", "WR", "test_fixture",
                  valid_positions={"WR"}, nfl_team_id="SF")
    insert_player(conn, player_b, "J. Smith", "TE", "test_fixture",
                  valid_positions={"TE"}, nfl_team_id="SF")

    add_player_alias(conn, raw_name="J. Smith", source_system="manual_entry",
                      candidate_player_id=player_a, confidence=0.5)
    add_player_alias(conn, raw_name="J. Smith", source_system="manual_entry",
                      candidate_player_id=player_b, confidence=0.5)

    candidates = get_alias_candidates(conn, "J. Smith", "manual_entry")
    candidate_ids = {row["candidate_player_id"] for row in candidates}
    assert candidate_ids == {player_a, player_b}
    assert all(row["resolution_status"] == "unresolved" for row in candidates)


def test_no_hardcoded_position_list_reflects_league_rules_contract(valid_positions):
    assert valid_positions == {"QB", "HB", "FB", "WR", "TE", "K", "TEAM"}
