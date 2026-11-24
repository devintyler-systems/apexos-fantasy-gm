"""R-23 (DECISIONS #76): a player's recent role as an availability feature. No look-ahead: only games of the same season before `before_week` count.

recent_pct(snaps, players, season, before_week): mean offense snap share over each player's last 3 games with an offense snap, indexed by gsis_id.
role(pct, week): 'S' (starter, >= 0.5), 'O' (other, including no snaps from week 3 on), 'U' (weeks 1-2, no history: the table falls back to the position-level rate).
Used by fit_availability_role.py (the fit and its leave-one-season-out test) and by params.p_active when APEX_AVAIL_ROLE=1."""
import pandas as pd

THRESH = 0.5
SKILL_PG = ("QB", "RB", "WRTE")


def recent_pct(snaps, players, season, before_week, n=3):
    s = snaps[(snaps.season == season) & (snaps.game_type == "REG") & (snaps.week < before_week) & (snaps.offense_snaps > 0)]
    if s.empty:
        return pd.Series(dtype=float, name="recent_pct")
    s = s.sort_values("week").groupby("pfr_player_id").tail(n)
    r = s.groupby("pfr_player_id").offense_pct.mean().rename("recent_pct").reset_index()
    m = players[["pfr_id", "gsis_id"]].dropna().drop_duplicates("pfr_id")
    r = r.merge(m, left_on="pfr_player_id", right_on="pfr_id")
    return r.drop_duplicates("gsis_id").set_index("gsis_id").recent_pct


def role(pct, week=None):
    """A player with no offense snap in the games before `week` is a non-starter ('O') once the season is two games old (week >= 3); before that there is no history ('U')."""
    if pct is None or pct != pct:
        return "O" if (week is not None and week >= 3) else "U"
    return "S" if pct >= THRESH else "O"
