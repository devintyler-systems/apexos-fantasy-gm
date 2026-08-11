"""
Draft State Manager — SQLite schema (B-05, Issue #11, contract v0.2-correction).

Session-scoped, isolated SQLite state, separate from the B-02 canonical DB
(resolves U-B05-02). One file per draft_session_id under data/draft_state/.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DDL_DRAFT_PICK_ENTRIES = """
CREATE TABLE IF NOT EXISTS draft_pick_entries (
    entry_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_session_id        TEXT NOT NULL,
    pick_number              INTEGER NOT NULL,
    raw_player_name          TEXT NOT NULL,
    normalized_player_id     TEXT,
    drafting_team_id         TEXT,
    entry_source             TEXT NOT NULL DEFAULT 'manual_entry',
    validation_status        TEXT NOT NULL CHECK (validation_status IN
                              ('accepted','rejected_sequence_mismatch','rejected_identity_ambiguous',
                               'rejected_identity_unresolved','pending_disambiguation')),
    validation_reason_codes  TEXT,
    b04_map_version           TEXT NOT NULL,
    correction_of_entry_id    INTEGER REFERENCES draft_pick_entries(entry_id),
    entered_at                 TEXT NOT NULL,
    accepted_at                TEXT,
    undone_at                  TEXT,
    undone_by                  TEXT,
    undone_reason              TEXT,
    created_at                  TEXT NOT NULL,
    CHECK (
        (undone_at IS NULL AND undone_by IS NULL AND undone_reason IS NULL)
        OR
        (undone_at IS NOT NULL AND undone_by IS NOT NULL AND undone_reason IS NOT NULL)
    )
);
"""

DDL_DRAFT_SESSION_STATE = """
CREATE TABLE IF NOT EXISTS draft_session_state (
    draft_session_id       TEXT PRIMARY KEY,
    league_id                TEXT NOT NULL,
    current_pick_number      INTEGER NOT NULL,
    last_accepted_entry_id    INTEGER REFERENCES draft_pick_entries(entry_id),
    degraded_mode              INTEGER NOT NULL DEFAULT 0,
    resume_confirmed_at         TEXT,
    started_at                   TEXT NOT NULL,
    updated_at                   TEXT NOT NULL
);
"""

DDL_DRAFT_PICK_OVERRIDES = """
CREATE TABLE IF NOT EXISTS draft_pick_overrides (
    override_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    original_entry_id    INTEGER NOT NULL REFERENCES draft_pick_entries(entry_id),
    new_entry_id           INTEGER NOT NULL REFERENCES draft_pick_entries(entry_id),
    override_reason         TEXT NOT NULL,
    overridden_by            TEXT NOT NULL,
    overridden_at             TEXT NOT NULL
);
"""

ALL_DDL = (DDL_DRAFT_PICK_ENTRIES, DDL_DRAFT_SESSION_STATE, DDL_DRAFT_PICK_OVERRIDES)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the 3 draft-state tables if they do not already exist."""
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    for ddl in ALL_DDL:
        cur.execute(ddl)
    conn.commit()


def get_session_db_path(session_id: str, base_dir: str | Path = "data/draft_state") -> Path:
    """Return the isolated per-session SQLite file path (contract §3 / U-B05-02)."""
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{session_id}.db"


def connect_session(session_id: str, base_dir: str | Path = "data/draft_state") -> sqlite3.Connection:
    path = get_session_db_path(session_id, base_dir)
    conn = sqlite3.connect(str(path))
    create_schema(conn)
    return conn
