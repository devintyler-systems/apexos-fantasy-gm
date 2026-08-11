"""
Draft State Manager — orchestration (B-05, Issue #11, contract v0.2-correction).

Consumes B-04's frozen round_order_map.py (read-only) and B-02's canonical
player_alias_map (read-only) for identity resolution. Never re-derives pick
order and never auto-merges ambiguous identity.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Optional

from engine.draft.round_order_map import get_draft_position
from engine.draft_state import repository


class DraftStateManager:
    """Orchestrates manual pick entry, identity resolution, and persistence
    for one draft session. No platform-write, sync, or autonomous-pick paths
    exist in this class — it is a manual-entry recorder only.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        canonical_conn: sqlite3.Connection,
        draft_session_id: str,
        league_id: str,
        b04_map_version: str,
    ):
        self.conn = conn
        self.canonical_conn = canonical_conn
        self.draft_session_id = draft_session_id
        self.league_id = league_id
        self.b04_map_version = b04_map_version

        conn.row_factory = sqlite3.Row
        pre_existing_activity = conn.execute(
            "SELECT 1 FROM draft_pick_entries WHERE draft_session_id = ? LIMIT 1",
            (draft_session_id,),
        ).fetchone() is not None

        repository.get_or_create_session(conn, draft_session_id, league_id)

        # Per-process gate: a brand-new session (no prior entries) never needs a
        # resume confirmation. A session with prior activity requires an explicit
        # confirm_resume() call on THIS instance before it accepts new entries,
        # regardless of what a previous process already confirmed in the DB --
        # every new process attaching to existing state must re-confirm.
        self._resume_gate_cleared = not pre_existing_activity

    def confirm_resume(self) -> None:
        repository.confirm_resume(self.conn, self.draft_session_id)
        self._resume_gate_cleared = True

    def _require_resumed(self) -> None:
        if not self._resume_gate_cleared:
            raise repository.SessionNotResumedError(
                f"Session {self.draft_session_id} has prior activity and has not been "
                "explicitly resume-confirmed on this process. Call confirm_resume() first."
            )

    def _resolve_identity(self, raw_name: str, source_system: str = "manual_entry"):
        from engine.canonical.repository import get_alias_candidates
        return get_alias_candidates(self.canonical_conn, raw_name, source_system)

    def _current_pick_number(self) -> int:
        self.conn.row_factory = sqlite3.Row
        row = self.conn.execute(
            "SELECT current_pick_number FROM draft_session_state WHERE draft_session_id = ?",
            (self.draft_session_id,),
        ).fetchone()
        return row["current_pick_number"]

    def submit_pick(
        self,
        pick_number: int,
        raw_player_name: str,
        drafting_team_id: Optional[str] = None,
    ) -> dict:
        """Validate sequence, resolve identity, and either accept or halt."""
        self._require_resumed()

        expected_pick_number = self._current_pick_number()
        if pick_number != expected_pick_number:
            entry_id = repository.record_entry(
                self.conn, self.draft_session_id, pick_number, raw_player_name,
                validation_status="rejected_sequence_mismatch",
                b04_map_version=self.b04_map_version,
                validation_reason_codes=json.dumps(
                    [f"expected_pick_{expected_pick_number}_got_{pick_number}"]
                ),
                drafting_team_id=drafting_team_id,
            )
            return {"status": "rejected_sequence_mismatch", "entry_id": entry_id,
                    "expected_pick_number": expected_pick_number}

        get_draft_position(pick_number)  # bounds-check against frozen B-04 map

        candidates = self._resolve_identity(raw_player_name)
        if len(candidates) == 0:
            entry_id = repository.record_entry(
                self.conn, self.draft_session_id, pick_number, raw_player_name,
                validation_status="rejected_identity_unresolved",
                b04_map_version=self.b04_map_version,
                drafting_team_id=drafting_team_id,
            )
            return {"status": "rejected_identity_unresolved", "entry_id": entry_id}

        unique_candidate_ids = {row["candidate_player_id"] for row in candidates}
        if len(unique_candidate_ids) > 1:
            entry_id = repository.record_entry(
                self.conn, self.draft_session_id, pick_number, raw_player_name,
                validation_status="rejected_identity_ambiguous",
                b04_map_version=self.b04_map_version,
                validation_reason_codes=json.dumps(sorted(unique_candidate_ids)),
                drafting_team_id=drafting_team_id,
            )
            return {"status": "rejected_identity_ambiguous", "entry_id": entry_id,
                    "candidates": sorted(unique_candidate_ids)}

        normalized_player_id = unique_candidate_ids.pop()
        entry_id = repository.record_entry(
            self.conn, self.draft_session_id, pick_number, raw_player_name,
            validation_status="accepted",
            b04_map_version=self.b04_map_version,
            normalized_player_id=normalized_player_id,
            drafting_team_id=drafting_team_id,
        )
        repository.advance_session_after_accept(
            self.conn, self.draft_session_id, entry_id, pick_number + 1
        )
        return {"status": "accepted", "entry_id": entry_id,
                "normalized_player_id": normalized_player_id}

    def override_pick(
        self,
        original_entry_id: int,
        pick_number: int,
        raw_player_name: str,
        normalized_player_id: Optional[str],
        override_reason: str,
        overridden_by: str,
        drafting_team_id: Optional[str] = None,
    ) -> dict:
        original_id, new_id = repository.create_override(
            self.conn, original_entry_id, self.draft_session_id, pick_number,
            raw_player_name, normalized_player_id, drafting_team_id,
            self.b04_map_version, override_reason, overridden_by,
            next_pick_number=pick_number + 1,
        )
        return {"status": "accepted", "original_entry_id": original_id, "entry_id": new_id}

    def correct_identity(
        self,
        original_entry_id: int,
        pick_number: int,
        raw_player_name: str,
        normalized_player_id: str,
        drafting_team_id: Optional[str] = None,
    ) -> dict:
        entry_id = repository.create_correction(
            self.conn, original_entry_id, self.draft_session_id, pick_number,
            raw_player_name, normalized_player_id, drafting_team_id,
            self.b04_map_version, next_pick_number=pick_number + 1,
        )
        return {"status": "accepted", "entry_id": entry_id,
                "correction_of_entry_id": original_entry_id}

    def undo_last(self, undone_by: str, undone_reason: str) -> dict:
        undone_entry_id = repository.undo_last_pick(
            self.conn, self.draft_session_id, undone_by, undone_reason
        )
        return {"status": "undone", "entry_id": undone_entry_id}

    def set_degraded(self, flag: bool) -> None:
        repository.set_degraded_mode(self.conn, self.draft_session_id, flag)
