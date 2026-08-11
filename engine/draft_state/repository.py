"""
Draft State Manager — repository (B-05, Issue #11, contract v0.2-correction).

Doctrine constraints enforced here:
- Overrides and disambiguation corrections are always additive: a new row is
  inserted, the original rejected row is never mutated (T11, T13).
- Undo populates undone_at/undone_by/undone_reason together or not at all;
  the DB-level CHECK constraint in schema.py is the real enforcement (T12).
- Undo may only ever target draft_session_state.last_accepted_entry_id.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Optional


class SessionNotResumedError(RuntimeError):
    """Raised when new entries are submitted before an explicit resume confirmation."""


class UndoTargetMismatchError(ValueError):
    """Raised when attempting to undo anything other than the last accepted pick."""


class InvalidOverrideError(ValueError):
    """Raised when an override lacks a real reason or a real human identity."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_or_create_session(
    conn: sqlite3.Connection,
    draft_session_id: str,
    league_id: str,
) -> sqlite3.Row:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM draft_session_state WHERE draft_session_id = ?",
        (draft_session_id,),
    ).fetchone()
    if row is not None:
        return row

    now = _now()
    conn.execute(
        """INSERT INTO draft_session_state
               (draft_session_id, league_id, current_pick_number, degraded_mode,
                started_at, updated_at)
           VALUES (?, ?, 1, 0, ?, ?)""",
        (draft_session_id, league_id, now, now),
    )
    conn.commit()
    return conn.execute(
        "SELECT * FROM draft_session_state WHERE draft_session_id = ?",
        (draft_session_id,),
    ).fetchone()


def confirm_resume(conn: sqlite3.Connection, draft_session_id: str) -> None:
    """Explicit human confirmation required before accepting new entries after restart."""
    conn.execute(
        "UPDATE draft_session_state SET resume_confirmed_at = ?, updated_at = ? "
        "WHERE draft_session_id = ?",
        (_now(), _now(), draft_session_id),
    )
    conn.commit()


def set_degraded_mode(conn: sqlite3.Connection, draft_session_id: str, flag: bool) -> None:
    conn.execute(
        "UPDATE draft_session_state SET degraded_mode = ?, updated_at = ? "
        "WHERE draft_session_id = ?",
        (1 if flag else 0, _now(), draft_session_id),
    )
    conn.commit()


def record_entry(
    conn: sqlite3.Connection,
    draft_session_id: str,
    pick_number: int,
    raw_player_name: str,
    validation_status: str,
    b04_map_version: str,
    normalized_player_id: Optional[str] = None,
    drafting_team_id: Optional[str] = None,
    validation_reason_codes: Optional[str] = None,
    entry_source: str = "manual_entry",
    correction_of_entry_id: Optional[int] = None,
) -> int:
    """Insert a single draft_pick_entries row. Never updates an existing row."""
    now = _now()
    cur = conn.execute(
        """INSERT INTO draft_pick_entries
               (draft_session_id, pick_number, raw_player_name, normalized_player_id,
                drafting_team_id, entry_source, validation_status, validation_reason_codes,
                b04_map_version, correction_of_entry_id, entered_at, accepted_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            draft_session_id, pick_number, raw_player_name, normalized_player_id,
            drafting_team_id, entry_source, validation_status, validation_reason_codes,
            b04_map_version, correction_of_entry_id, now,
            now if validation_status == "accepted" else None, now,
        ),
    )
    conn.commit()
    return cur.lastrowid


def advance_session_after_accept(
    conn: sqlite3.Connection, draft_session_id: str, accepted_entry_id: int, next_pick_number: int
) -> None:
    conn.execute(
        """UPDATE draft_session_state
               SET current_pick_number = ?, last_accepted_entry_id = ?, updated_at = ?
               WHERE draft_session_id = ?""",
        (next_pick_number, accepted_entry_id, _now(), draft_session_id),
    )
    conn.commit()


def create_override(
    conn: sqlite3.Connection,
    original_entry_id: int,
    draft_session_id: str,
    pick_number: int,
    raw_player_name: str,
    normalized_player_id: Optional[str],
    drafting_team_id: Optional[str],
    b04_map_version: str,
    override_reason: str,
    overridden_by: str,
    next_pick_number: int,
) -> tuple[int, int]:
    """Resolves T11 / U-B05-01: the original rejected row is never mutated."""
    if not override_reason or not override_reason.strip():
        raise InvalidOverrideError("override_reason is required and cannot be empty")
    if not overridden_by or overridden_by.strip().lower() == "system":
        raise InvalidOverrideError("overridden_by must be a real human identity, not 'system'")

    new_entry_id = record_entry(
        conn,
        draft_session_id=draft_session_id,
        pick_number=pick_number,
        raw_player_name=raw_player_name,
        validation_status="accepted",
        b04_map_version=b04_map_version,
        normalized_player_id=normalized_player_id,
        drafting_team_id=drafting_team_id,
        entry_source="manual_entry",
    )
    now = _now()
    conn.execute(
        """INSERT INTO draft_pick_overrides
               (original_entry_id, new_entry_id, override_reason, overridden_by, overridden_at)
           VALUES (?, ?, ?, ?, ?)""",
        (original_entry_id, new_entry_id, override_reason, overridden_by, now),
    )
    conn.commit()
    advance_session_after_accept(conn, draft_session_id, new_entry_id, next_pick_number)
    return original_entry_id, new_entry_id


def create_correction(
    conn: sqlite3.Connection,
    original_entry_id: int,
    draft_session_id: str,
    pick_number: int,
    raw_player_name: str,
    normalized_player_id: str,
    drafting_team_id: Optional[str],
    b04_map_version: str,
    next_pick_number: int,
) -> int:
    """Resolves T13 / U-B05-03: disambiguation correction is additive-only."""
    new_entry_id = record_entry(
        conn,
        draft_session_id=draft_session_id,
        pick_number=pick_number,
        raw_player_name=raw_player_name,
        validation_status="accepted",
        b04_map_version=b04_map_version,
        normalized_player_id=normalized_player_id,
        drafting_team_id=drafting_team_id,
        entry_source="manual_entry",
        correction_of_entry_id=original_entry_id,
    )
    advance_session_after_accept(conn, draft_session_id, new_entry_id, next_pick_number)
    return new_entry_id


def undo_last_pick(
    conn: sqlite3.Connection,
    draft_session_id: str,
    undone_by: str,
    undone_reason: str,
) -> int:
    """Resolves T07 / T12: undo may only affect the immediately preceding accepted pick."""
    if not undone_by or not undone_by.strip():
        raise ValueError("undone_by is required")
    if not undone_reason or not undone_reason.strip():
        raise ValueError("undone_reason is required")

    conn.row_factory = sqlite3.Row
    session = conn.execute(
        "SELECT last_accepted_entry_id FROM draft_session_state WHERE draft_session_id = ?",
        (draft_session_id,),
    ).fetchone()
    if session is None or session["last_accepted_entry_id"] is None:
        raise UndoTargetMismatchError("No accepted pick exists to undo")

    target_entry_id = session["last_accepted_entry_id"]
    now = _now()
    conn.execute(
        """UPDATE draft_pick_entries
               SET undone_at = ?, undone_by = ?, undone_reason = ?
               WHERE entry_id = ?""",
        (now, undone_by, undone_reason, target_entry_id),
    )

    prior = conn.execute(
        """SELECT entry_id FROM draft_pick_entries
               WHERE draft_session_id = ? AND validation_status = 'accepted'
                 AND undone_at IS NULL AND entry_id != ?
               ORDER BY entry_id DESC LIMIT 1""",
        (draft_session_id, target_entry_id),
    ).fetchone()
    prior_entry_id = prior["entry_id"] if prior else None

    conn.execute(
        """UPDATE draft_session_state
               SET last_accepted_entry_id = ?, updated_at = ?
               WHERE draft_session_id = ?""",
        (prior_entry_id, now, draft_session_id),
    )
    conn.commit()
    return target_entry_id
