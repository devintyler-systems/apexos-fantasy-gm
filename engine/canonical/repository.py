"""
Canonical Data Model — repository (B-02, Issue #5).

Insert/query functions for the 4 canonical tables. Position validation
uses only engine.canonical.schema.load_valid_positions (League Rules
Contract); no position list is hardcoded here.

Identity doctrine: add_player_alias never collapses ambiguous name
matches. Multiple candidate_player_id rows for the same raw_name/source
are expected and normal; resolving ambiguity to a single player is a
separate, explicit, human-in-the-loop action outside this module's scope.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Optional


class PositionNotEligibleError(ValueError):
    """Raised when a player's position is not in the League Rules Contract."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_team(
    conn: sqlite3.Connection,
    team_id: str,
    team_name: str,
    source_system: str,
    conference: Optional[str] = None,
    division: Optional[str] = None,
) -> None:
    conn.execute(
        """INSERT INTO dim_team (team_id, team_name, conference, division,
               source_system, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (team_id, team_name, conference, division, source_system, _now()),
    )
    conn.commit()


def insert_player(
    conn: sqlite3.Connection,
    player_id: str,
    full_name: str,
    position: str,
    source_system: str,
    valid_positions,
    nfl_team_id: Optional[str] = None,
    birthdate: Optional[str] = None,
    source_record_id: Optional[str] = None,
) -> None:
    if position not in valid_positions:
        raise PositionNotEligibleError(
            f"Position '{position}' is not in the League Rules Contract "
            f"eligible set: {sorted(valid_positions)}"
        )
    now = _now()
    conn.execute(
        """INSERT INTO dim_player (player_id, full_name, position, nfl_team_id,
               birthdate, source_system, source_record_id, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (player_id, full_name, position, nfl_team_id, birthdate,
         source_system, source_record_id, now, now),
    )
    conn.commit()


def insert_game(
    conn: sqlite3.Connection,
    game_id: str,
    season: int,
    week: int,
    home_team_id: str,
    away_team_id: str,
    source_system: str,
    game_date: Optional[str] = None,
) -> None:
    conn.execute(
        """INSERT INTO dim_game (game_id, season, week, home_team_id,
               away_team_id, game_date, source_system, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (game_id, season, week, home_team_id, away_team_id, game_date,
         source_system, _now()),
    )
    conn.commit()


def add_player_alias(
    conn: sqlite3.Connection,
    raw_name: str,
    source_system: str,
    candidate_player_id: str,
    confidence: Optional[float] = None,
) -> None:
    """Record a raw-name-to-candidate-player mapping. Calling this
    repeatedly with the same raw_name/source_system and different
    candidate_player_id values is the supported way to represent an
    ambiguous identity; no row is ever overwritten or auto-collapsed.
    """
    conn.execute(
        """INSERT INTO player_alias_map (raw_name, source_system,
               candidate_player_id, confidence, resolution_status, created_at)
           VALUES (?, ?, ?, ?, 'unresolved', ?)""",
        (raw_name, source_system, candidate_player_id, confidence, _now()),
    )
    conn.commit()


def get_alias_candidates(conn: sqlite3.Connection, raw_name: str, source_system: str):
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        """SELECT * FROM player_alias_map
           WHERE raw_name = ? AND source_system = ?""",
        (raw_name, source_system),
    )
    return cur.fetchall()
