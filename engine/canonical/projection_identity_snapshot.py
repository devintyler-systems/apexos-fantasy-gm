"""Fixture-only canonical identity validation for projection artifact v0.1.

This module deliberately reads no database and performs no identity merge.  A
caller supplies a frozen identity snapshot; any ambiguous alias is a blocking
condition rather than a candidate for automatic resolution.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


class ProjectionIdentityError(ValueError):
    """A fail-closed canonical-identity validation error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]{2,127}$")
_POSITIONS = frozenset({"QB", "HB", "FB", "WR", "TE", "K", "TEAM"})


def _mapping(value: Any, code: str, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProjectionIdentityError(code, f"{field} must be a mapping")
    return value


def _identifier(value: Any, code: str, field: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ProjectionIdentityError(code, f"{field} must be a canonical lowercase identifier")
    return value


def validate_identity_snapshot(snapshot: Mapping[str, Any]) -> dict[str, tuple[str, str]]:
    """Return player -> (team, position) only for an unambiguous snapshot."""
    snapshot = _mapping(snapshot, "PA08_IDENTITY_SNAPSHOT_INVALID", "identity_snapshot")
    _identifier(
        snapshot.get("canonical_identity_snapshot_id"),
        "PA08_IDENTITY_SNAPSHOT_INVALID",
        "canonical_identity_snapshot_id",
    )
    teams = snapshot.get("teams")
    players = snapshot.get("players")
    aliases = snapshot.get("aliases", [])
    if not isinstance(teams, Sequence) or isinstance(teams, (str, bytes)):
        raise ProjectionIdentityError("PA08_IDENTITY_SNAPSHOT_INVALID", "teams must be a list")
    if not isinstance(players, Sequence) or isinstance(players, (str, bytes)):
        raise ProjectionIdentityError("PA08_IDENTITY_SNAPSHOT_INVALID", "players must be a list")
    if not isinstance(aliases, Sequence) or isinstance(aliases, (str, bytes)):
        raise ProjectionIdentityError("PA08_IDENTITY_SNAPSHOT_INVALID", "aliases must be a list")

    team_ids: set[str] = set()
    for entry in teams:
        team = _mapping(entry, "PA08_TEAM_IDENTITY_INVALID", "teams entry")
        team_id = _identifier(team.get("canonical_team_id"), "PA08_TEAM_IDENTITY_INVALID", "canonical_team_id")
        if team_id in team_ids:
            raise ProjectionIdentityError("PA08_DUPLICATE_TEAM_IDENTITY", f"duplicate team {team_id}")
        team_ids.add(team_id)

    player_index: dict[str, tuple[str, str]] = {}
    for entry in players:
        player = _mapping(entry, "PA08_PLAYER_IDENTITY_INVALID", "players entry")
        player_id = _identifier(player.get("canonical_player_id"), "PA08_PLAYER_IDENTITY_INVALID", "canonical_player_id")
        team_id = _identifier(player.get("canonical_team_id"), "PA08_PLAYER_IDENTITY_INVALID", "canonical_team_id")
        position = player.get("position")
        if position not in _POSITIONS:
            raise ProjectionIdentityError("PA08_PLAYER_IDENTITY_INVALID", "position is not permitted")
        if team_id not in team_ids:
            raise ProjectionIdentityError("PA08_UNRESOLVED_TEAM_IDENTITY", f"team {team_id} is unresolved")
        if player_id in player_index:
            raise ProjectionIdentityError("PA08_DUPLICATE_PLAYER_IDENTITY", f"duplicate player {player_id}")
        player_index[player_id] = (team_id, position)

    for entry in aliases:
        alias = _mapping(entry, "PA08_ALIAS_INVALID", "aliases entry")
        candidates = alias.get("candidate_player_ids")
        if alias.get("ambiguous") is True or not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)) or len(candidates) != 1:
            raise ProjectionIdentityError("PA08_AMBIGUOUS_IDENTITY", "alias ambiguity must be resolved outside v0.1")
        candidate = _identifier(candidates[0], "PA08_ALIAS_INVALID", "candidate_player_ids[0]")
        if candidate not in player_index:
            raise ProjectionIdentityError("PA08_UNRESOLVED_PLAYER_IDENTITY", f"alias candidate {candidate} is unresolved")
    return player_index


def validate_projection_identity(row: Mapping[str, Any], snapshot: Mapping[str, Any]) -> None:
    """Validate one supplied row against an already frozen identity snapshot."""
    player_index = validate_identity_snapshot(snapshot)
    player_id = _identifier(row.get("canonical_player_id"), "PA08_UNRESOLVED_PLAYER_IDENTITY", "canonical_player_id")
    team_id = _identifier(row.get("canonical_team_id"), "PA08_UNRESOLVED_TEAM_IDENTITY", "canonical_team_id")
    position = row.get("position")
    resolved = player_index.get(player_id)
    if resolved is None:
        raise ProjectionIdentityError("PA08_UNRESOLVED_PLAYER_IDENTITY", f"player {player_id} is unresolved")
    if resolved != (team_id, position):
        raise ProjectionIdentityError("PA08_IDENTITY_MISMATCH", f"player {player_id} does not match team/position snapshot")
