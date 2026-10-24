"""Game-designation overlay for teams whose NFL report has not reached the nflverse feed (see apply_status_overlay)."""
import pandas as pd

from load import norm_name


def apply_status_overlay(i, m, team_map):
    """Operator-supplied game designations (APEX_STATUS_OVERLAY=<csv: player,team,pos,report_status,source,as_of_utc>) for teams whose NFL report is not in the nflverse feed yet (it lags the Friday
    report by hours). Only teams with NO report_status in `i` are touched, so the NFL feed governs the moment it carries a team. A matching player row gets the designation (practice status stays the
    nflverse one); an unmatched player is added with no practice row. The fitted availability table turns (designation, practice, position) into p_active exactly as for nflverse rows."""
    m = m[m.report_status.isin(["Out", "Doubtful", "Questionable"])].copy()
    m["team"] = m.team.map(lambda t: team_map.get(t, t) if hasattr(team_map, "get") else t); m["nkey"] = m.player.map(norm_name)
    have = set(i.loc[i.report_status.notna(), "team"]); m = m[~m.team.isin(have)]
    if not len(m):
        return i
    i = i.copy(); i["nkey"] = i.full_name.map(norm_name); key = dict(zip(zip(m.nkey, m.team), m.report_status))
    hit = pd.Series([(a, b) in key for a, b in zip(i.nkey, i.team)], index=i.index)
    i.loc[hit, "report_status"] = [key[(a, b)] for a, b in zip(i.nkey[hit], i.team[hit])]
    seen = set(zip(i.nkey, i.team)); add = m[[(a, b) not in seen for a, b in zip(m.nkey, m.team)]]
    if len(add):
        i = pd.concat([i, pd.DataFrame(dict(full_name=add.player.values, position=add.pos.values, team=add.team.values, report_status=add.report_status.values, practice_status=None,
                                            report_primary_injury=None, practice_primary_injury=None, game_type="REG", week=int(i.week.max()), nkey=add.nkey.values))], ignore_index=True)
    return i.drop(columns=["nkey"])
