"""
Canonical Data Model — SQLite schema (B-02, Issue #5).

Defines the 4 approved canonical tables: dim_player, dim_team, dim_game,
player_alias_map.

Doctrine constraints enforced here:
- No hardcoded position lists: valid player positions are loaded at runtime
  from the League Rules Contract YAML (contracts/league_rules/<league_id>.yaml).
- player_alias_map supports one raw name mapping to multiple candidate
  player_ids (ambiguous identity). Nothing in this module auto-merges or
  auto-resolves ambiguous candidates.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import yaml

DDL_DIM_TEAM = """
CREATE TABLE IF NOT EXISTS dim_team (
    team_id         TEXT PRIMARY KEY,
    team_name       TEXT NOT NULL,
    conference      TEXT,
    division        TEXT,
    source_system   TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
"""

DDL_DIM_PLAYER = """
CREATE TABLE IF NOT EXISTS dim_player (
    player_id         TEXT PRIMARY KEY,
    full_name         TEXT NOT NULL,
    position          TEXT NOT NULL,
    nfl_team_id       TEXT REFERENCES dim_team(team_id),
    birthdate         TEXT,
    source_system     TEXT NOT NULL,
    source_record_id  TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);
"""

DDL_DIM_GAME = """
CREATE TABLE IF NOT EXISTS dim_game (
    game_id         TEXT PRIMARY KEY,
    season          INTEGER NOT NULL,
    week            INTEGER NOT NULL,
    home_team_id    TEXT NOT NULL REFERENCES dim_team(team_id),
    away_team_id    TEXT NOT NULL REFERENCES dim_team(team_id),
    game_date       TEXT,
    source_system   TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
"""

DDL_PLAYER_ALIAS_MAP = """
CREATE TABLE IF NOT EXISTS player_alias_map (
    alias_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name             TEXT NOT NULL,
    source_system        TEXT NOT NULL,
    candidate_player_id  TEXT NOT NULL REFERENCES dim_player(player_id),
    confidence           REAL,
    resolution_status    TEXT NOT NULL DEFAULT 'unresolved'
                         CHECK (resolution_status IN ('unresolved','resolved','ambiguous')),
    resolved_by          TEXT,
    resolved_at          TEXT,
    created_at           TEXT NOT NULL,
    UNIQUE (raw_name, source_system, candidate_player_id)
);
"""

ALL_DDL = (DDL_DIM_TEAM, DDL_DIM_PLAYER, DDL_DIM_GAME, DDL_PLAYER_ALIAS_MAP)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the 4 canonical tables if they do not already exist."""
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    for ddl in ALL_DDL:
        cur.execute(ddl)
    conn.commit()


def load_valid_positions(league_rules_path) -> set:
    """Load the set of valid player position codes from a League Rules
    Contract YAML. This is the only sanctioned source of truth for
    eligible positions; application code must never hardcode a list.
    """
    path = Path(league_rules_path)
    with path.open("r", encoding="utf-8") as fh:
        contract = yaml.safe_load(fh)

    roster = contract.get("roster", {})
    eligibility = roster.get("positional_eligibility", {})

    positions = set()
    for codes in eligibility.values():
        positions.update(codes)
    return positions
