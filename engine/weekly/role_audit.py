"""Role audit (DECISIONS #94): warnings, not a gate. Runs after the starter audit on live runs and before any lineup build.

Flags the three W12 PHI@DAL failure types so a person looks at them before a lineup or a prop uses the number:
  STALE ROLE   projected >= 2 targets or >= 3 carries, but the player's last stat row is older than his team's 3rd-latest game while he had
               offense snaps since (zero-touch games do not create a stat row, so his share comes from old games; W12 Ertz: 3.3 targets
               projected, last target Week 5). R-42b in DECISIONS #94 is the model-side fix (pooled backtest neutral, owner card).
  NEW STARTER  depth-chart QB1 with under 60% of his team's pass attempts: his projection uses the TEAM passing efficiency (W12 Milton
               inherited Hurts' rates; the QB-own-efficiency fix R-43 failed the backtest, #94).
  PRACTICE SQ  player on the manual-out list as practice squad (DECISIONS #61) whom DraftKings lists with a 3+ point average: he scores
               only if elevated for the game (W12 Kendre Miller).
usage: APEX_OUT=<run out dir> [APEX_DK_SALARIES=<csv>] python role_audit.py [--teams PHI,DAL]
Writes role_audit.csv next to the projections.
"""
import os, sys
import pandas as pd
from load import norm_name
from paths import OUT, NFLV

TM = {"LAR": "LA", "JAC": "JAX", "WSH": "WAS"}


def main():
    season = int(os.environ.get("APEX_SEASON", 2026)); thru = int(os.environ.get("APEX_THROUGH_WEEK", 99))
    P = pd.read_pickle(OUT + "proj_all.pkl"); P["nkey"] = P.player.map(norm_name)
    teams = sys.argv[sys.argv.index("--teams") + 1].split(",") if "--teams" in sys.argv else sorted(P.team.unique())
    P = P[P.team.isin(teams) & (P.p_active.fillna(0) > 0.5)]
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); st = st[(st.season_type == "REG") & (st.week <= thru)].copy()
    st["team"] = st.team.replace(TM); st["nkey"] = st.player_display_name.map(norm_name)
    sn = pd.read_parquet(NFLV + f"snap_counts_{season}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.week <= thru)].copy()
    sn["nkey"] = sn.player.map(norm_name); sn["team"] = sn.team.replace(TM)
    last_row = st.groupby(["nkey", "team"]).week.max()
    team_wk = st.groupby("team").week.apply(lambda w: sorted(w.unique()))
    snap_last = sn[sn.offense_snaps.fillna(0) > 0].groupby(["nkey", "team"]).week.max()
    rows = []
    for r in P.itertuples():
        tgt, car = float(getattr(r, "tgt_mean", 0) or 0), float(getattr(r, "rush_att_mean", 0) or 0)
        if r.pos == "QB" or (tgt < 2 and car < 3):
            continue
        wk = team_wk.get(r.team, [])
        t3 = wk[-3] if len(wk) >= 3 else 0
        lr = last_row.get((r.nkey, r.team))
        if lr is None:
            continue
        if lr < t3 and snap_last.get((r.nkey, r.team), 0) > lr:
            rows.append(dict(flag="STALE ROLE", player=r.player, team=r.team, pos=r.pos, detail=f"projected {tgt:.1f} tgt / {car:.1f} car; last stat row week {lr}, offense snaps through week {snap_last.get((r.nkey, r.team))}"))
    pas = st[st.attempts > 0]
    tot = pas.groupby("team").attempts.sum()
    for t in teams:
        q = P[(P.team == t) & (P.pos == "QB")].sort_values("pass_yds_mean", ascending=False).head(1)
        if not len(q):
            continue
        q = q.iloc[0]; own = pas[(pas.nkey == q.nkey) & (pas.team == t)].attempts.sum()
        sh = own / tot.get(t, 1)
        if sh < 0.6:
            g = pas[(pas.nkey == q.nkey) & (pas.team == t)]
            rows.append(dict(flag="NEW STARTER", player=q.player, team=t, pos="QB", detail=f"{own:.0f} of {tot.get(t, 0):.0f} team attempts ({sh:.0%}); own {g.completions.sum():.0f}/{own:.0f}, {g.passing_yards.sum():.0f} yds, {g.passing_tds.sum():.0f} TD in {len(g)} games; projected {q.pass_cmp_mean:.1f} cmp, {q.pass_yds_mean:.0f} yds (team-rate based)"))
    mo, sal = os.environ.get("APEX_MANUAL_OUT"), os.environ.get("APEX_DK_SALARIES")
    if mo and os.path.exists(mo) and sal and os.path.exists(sal):
        m = pd.read_csv(mo, keep_default_na=False); m = m[m.note.str.contains("practice squad", case=False)]
        d = pd.read_csv(sal); d["team"] = d.TeamAbbrev.replace(TM); d = d.drop_duplicates(["Name", "team"])
        mk = set(zip(m.player.map(norm_name), m.team.replace(TM)))
        for r in d[(d.AvgPointsPerGame >= 3) & d.team.isin(teams)].itertuples():
            if (norm_name(r.Name), r.team) in mk:
                rows.append(dict(flag="PRACTICE SQ", player=r.Name, team=r.team, pos=r.Position, detail=f"DK average {r.AvgPointsPerGame}; on the practice squad, projected 0 unless elevated for the game"))
    R = pd.DataFrame(rows, columns=["flag", "player", "team", "pos", "detail"])
    R.to_csv(OUT + "role_audit.csv", index=False)
    if len(R):
        print(f"[role audit] {len(R)} warning(s): check before any lineup or prop uses these numbers")
        print(R.to_string(index=False))
    else:
        print("[role audit] no warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
