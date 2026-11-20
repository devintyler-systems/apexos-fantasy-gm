"""In-game availability flags for a graded game: separates in-game injuries and missed time from projection error.

python tools/postmortem/ingame_availability.py SEASON WEEK AWAY HOME [--out CSV]
For every QB/RB/WR/TE who played or was projected:
  - injury events from play-by-play ("<TEAM>-<#>-<Name> was injured during the play" / "has returned to the game"),
    with quarter and clock of the injury and the return (if any) and whether he touched the ball after it;
  - offense-snap share vs his average over his previous 3 games (snap_drop_pts);
  - flag: EXIT (injured, no return), MISSED_TIME (injured, returned), SNAP_DROP (>= 15 pts below his last-3 average), or blank.
A flagged player-game should be graded separately from projection error (post-mortem section "availability in game").
"""
import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
NV = ROOT / "var/nflverse"
INJ = re.compile(r"(?P<team>[A-Z]{2,3})-(?P<num>\d+)-(?P<name>[A-Z][A-Za-z.'\- ]+?) was injured during the play")
RET = re.compile(r"(?P<team>[A-Z]{2,3})-(?P<num>\d+)-(?P<name>[A-Z][A-Za-z.'\- ]+?) has returned to the game")


def clock(q, t):
    return f"Q{int(q)} {t}"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("season", type=int); ap.add_argument("week", type=int)
    ap.add_argument("away"); ap.add_argument("home"); ap.add_argument("--out"); a = ap.parse_args()
    pb = pd.read_parquet(NV / f"play_by_play_{a.season}.parquet", columns=["week", "home_team", "away_team", "game_seconds_remaining", "qtr", "time", "desc",
                                                                              "receiver_player_name", "rusher_player_name", "passer_player_name"])
    g = pb[(pb.week == a.week) & (pb.home_team == a.home) & (pb.away_team == a.away)].sort_values("game_seconds_remaining", ascending=False)
    ev = []
    for r in g.itertuples():
        for kind, rx in (("injured", INJ), ("returned", RET)):
            for m in rx.finditer(str(r.desc)):
                ev.append(dict(team=m["team"], name=m["name"].strip(), kind=kind, qtr=r.qtr, time=r.time, gsr=r.game_seconds_remaining))
    E = pd.DataFrame(ev, columns=["team", "name", "kind", "qtr", "time", "gsr"])
    N = pd.read_parquet(NV / f"snap_counts_{a.season}.parquet"); N = N[N.game_type == "REG"]
    S = pd.read_parquet(NV / f"stats_player_week_{a.season}.parquet"); S = S[(S.season_type == "REG") & (S.week == a.week) & S.team.isin([a.away, a.home])]
    cur = N[(N.week == a.week) & N.team.isin([a.away, a.home]) & N.position.isin(["QB", "RB", "FB", "WR", "TE"])]
    rows = []
    for r in cur.itertuples():
        prev = N[(N.player == r.player) & (N.week < a.week) & (N.offense_snaps > 0)].sort_values("week").tail(3)
        base = prev.offense_pct.mean() if len(prev) else float("nan")
        abbr = r.player.split()[0][0] + "." + " ".join(r.player.split()[1:])      # play-by-play style "T.Warren"
        e = E[(E.team == r.team) & (E.name.str.replace(" ", "") == abbr.replace(" ", ""))]
        inj = e[e.kind == "injured"]; ret = e[e.kind == "returned"]
        flag, inj_at, ret_at, touch_after = "", "", "", ""
        if len(inj):
            i0 = inj.iloc[0]; inj_at = clock(i0.qtr, i0.time)
            later = ret[ret.gsr < i0.gsr]
            touches = g[(g.game_seconds_remaining < i0.gsr) & ((g.receiver_player_name == abbr) | (g.rusher_player_name == abbr) | (g.passer_player_name == abbr))]
            touch_after = len(touches)
            if len(later):
                ret_at = clock(later.iloc[0].qtr, later.iloc[0].time); flag = "MISSED_TIME"
            else:
                flag = "EXIT" if touch_after == 0 else "MISSED_TIME"
        drop = (base - r.offense_pct) * 100 if pd.notna(base) else float("nan")
        if not flag and pd.notna(drop) and drop >= 15:
            flag = "SNAP_DROP"
        rows.append(dict(player=r.player, team=r.team, pos=r.position, snaps=int(r.offense_snaps), snap_pct=round(r.offense_pct * 100), last3_pct=round(base * 100) if pd.notna(base) else None,
                         snap_drop_pts=round(drop) if pd.notna(drop) else None, injured_at=inj_at, returned_at=ret_at, touches_after_injury=touch_after, flag=flag))
    out = pd.DataFrame(rows).sort_values(["flag", "team", "snaps"], ascending=[False, True, False])
    if a.out:
        out.to_csv(a.out, index=False)
    print(out[out.flag != ""].to_string(index=False) if (out.flag != "").any() else "no in-game availability flags")


if __name__ == "__main__":
    main()
