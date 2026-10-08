"""Needs the nflverse cache (`apex-weekly fetch`). Run in the weekly workflow: pytest -m integration."""
import os
import subprocess
import sys

import pandas as pd
import pytest

from conftest import WEEKLY

pytestmark = pytest.mark.integration
CACHE = os.environ.get("APEX_INTEGRATION_NFLV")


@pytest.mark.skipif(not CACHE or not os.path.exists(os.path.join(CACHE or "", "games.parquet")), reason="no nflverse cache")
def test_run_all_produces_sane_projections(tmp_path):
    env = dict(os.environ, APEX_NFLV=CACHE, APEX_OUT=str(tmp_path), APEX_ENV="market", APEX_NS="2000")
    r = subprocess.run([sys.executable, "run_all.py"], cwd=WEEKLY, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    rk = pd.read_pickle(tmp_path / "rank_raw.pkl")
    assert len(rk) > 300 and rk.ev_pts.notna().all()
    env2 = pd.read_csv(tmp_path / "w4_game_environment.csv")
    assert env2.home_win_prob.between(0.02, 0.98).all()
    assert env2.total_mean.between(25, 75).all()


@pytest.mark.skipif(not CACHE or not os.path.exists(os.path.join(CACHE or "", "roster_2026.parquet")), reason="no nflverse cache")
def test_reserve_released_players_are_never_projected_active(tmp_path):
    env = dict(os.environ, APEX_NFLV=CACHE, APEX_OUT=str(tmp_path), APEX_ENV="market", APEX_NS="1000")
    r = subprocess.run([sys.executable, "run_all.py"], cwd=WEEKLY, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    ro = pd.read_parquet(os.path.join(CACHE, "roster_2026.parquet"))
    ro = ro[(ro.game_type == "REG") & (ro.week == ro.week.max())]
    if len(ro) < 1000:
        pytest.skip("roster snapshot is not a full roster")
    ro = ro[ro.position.isin(["QB", "RB", "FB", "WR", "TE"])]
    live = set(zip(ro[ro.status.isin(["ACT", "DEV", "INA"])].full_name, ro[ro.status.isin(["ACT", "DEV", "INA"])].team))
    gone = ro[ro.status.isin(["RES", "CUT", "RET", "EXE"])]
    gone = {(a, b) for a, b in zip(gone.full_name, gone.team)} - live
    pa = pd.read_pickle(tmp_path / "rank_raw.pkl")
    bad = pa[pd.Series([(a, b) in gone for a, b in zip(pa.player, pa.team)], index=pa.index) & (pa.p_active > 0.01)]
    assert bad.empty, bad[["player", "team", "p_active"]].to_string()


@pytest.mark.skipif(not CACHE or not os.path.exists(os.path.join(CACHE or "", "roster_2026.parquet")), reason="no nflverse cache")
def test_players_who_left_their_stats_team_are_projected_out(tmp_path):
    """2026 W5: Beckham (NYG->MIN), X. Smith (LA->SF) and Hodge (cut by SF) kept anytime-TD probability on their old teams. Joined on gsis_id."""
    env = dict(os.environ, APEX_NFLV=CACHE, APEX_OUT=str(tmp_path), APEX_ENV="market", APEX_NS="1000")
    r = subprocess.run([sys.executable, "run_all.py"], cwd=WEEKLY, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    R = pd.read_parquet(os.path.join(CACHE, "roster_2026.parquet")); R = R[R.game_type == "REG"]
    cur = R[R.week == R.week.max()]
    if len(cur) < 1000:
        pytest.skip("roster snapshot is not a full roster")
    S = pd.read_parquet(os.path.join(CACHE, "stats_player_week_2026.parquet"))
    S = S[S.position.isin(["QB", "RB", "FB", "WR", "TE"])].sort_values("week").groupby("player_id").tail(1)
    live = cur[cur.status.isin(["ACT", "DEV", "INA"])].groupby("gsis_id").team.agg(set)
    gone = {(r.player_display_name, r.team) for r in S.itertuples() if r.player_id in live.index and r.team not in live[r.player_id]}
    assert gone, "expected at least one mid-season team change in the 2026 data"
    td = pd.read_csv(tmp_path / "w4_td_markets.csv")
    bad = td[pd.Series([(a, b) in gone for a, b in zip(td.player, td.team)], index=td.index) & (td.p_active > 0.01)]
    assert bad.empty, bad.to_string()


@pytest.mark.skipif(not CACHE or not os.path.exists(os.path.join(CACHE or "", "depth_charts_2026.parquet")), reason="no nflverse cache")
def test_starting_qb_follows_the_depth_chart_when_qb1_is_out(tmp_path):
    env = dict(os.environ, APEX_NFLV=CACHE, APEX_OUT=str(tmp_path), APEX_ENV="market", APEX_NS="1000")
    r = subprocess.run([sys.executable, "run_all.py"], cwd=WEEKLY, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    dc = pd.read_parquet(os.path.join(CACHE, "depth_charts_2026.parquet"))
    dc = dc[(dc.dt == dc.dt.max()) & (dc.pos_abb == "QB")].sort_values(["team", "pos_rank"])
    inj = pd.read_parquet(os.path.join(CACHE, "injuries_2026.parquet"))
    out = set(inj[(inj.game_type == "REG") & (inj.week == inj.week.max()) & (inj.report_status == "Out")].full_name)
    pa = pd.read_pickle(tmp_path / "rank_raw.pkl")
    pa = pa[(pa.pos == "QB") & pa.ev_pts.notna()]
    st = pd.read_parquet(os.path.join(CACHE, "stats_player_week_2026.parquet"))
    threw = set(st[(st.season_type == "REG") & (st.attempts > 0)].player_display_name)      # a QB with no 2026 attempts is not in the role tables
    checked = 0
    for team, g in dc.groupby("team"):
        order = [n for n in g.player_name if n not in out]
        proj = pa[pa.team == team]
        if not order or order[0] not in threw or not len(proj):      # no projection rows = bye week
            continue
        top = proj.sort_values("ev_pts", ascending=False).iloc[0].player
        assert top == order[0], (team, order[:3], top)
        checked += 1
    assert checked >= 20


@pytest.mark.skipif(not CACHE or not os.path.exists(os.path.join(CACHE or "", "games.parquet")), reason="no nflverse cache")
def test_manual_out_override_removes_the_player_and_is_frozen(tmp_path):
    def run(out, extra=None):
        env = dict(os.environ, APEX_NFLV=CACHE, APEX_OUT=str(out), APEX_ENV="market", APEX_NS="1000", **(extra or {}))
        r = subprocess.run([sys.executable, "run_all.py"], cwd=WEEKLY, env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        return pd.read_pickle(os.path.join(out, "rank_raw.pkl"))
    base = run(tmp_path / "a")
    pick = base[(base.pos == "WR") & (base.p_active > 0.9) & (~base.game.str.contains("@") | True)].sort_values("ev_pts", ascending=False).iloc[0]
    csv = tmp_path / "manual.csv"
    csv.write_text("player,team,pos,source,as_of_utc,note\n%s,%s,WR,test,2026-01-01T00:00:00Z,test\n" % (pick.player, pick.team))
    after = run(tmp_path / "b", {"APEX_MANUAL_OUT": str(csv)})
    row = after[(after.player == pick.player) & (after.team == pick.team)]
    assert row.empty or float(row.p_active.iloc[0]) == 0.0


@pytest.mark.skipif(not CACHE or not os.path.exists(os.path.join(CACHE or "", "games.parquet")), reason="no nflverse cache")
def test_price_odds_pacific_to_utc_week_filter_and_two_way_devig(tmp_path):
    """Synthetic Odds-API workbook: Pacific stamps shift +7h, a week-6 game is excluded, and a two-way market is de-vigged exactly and averaged over independent feeds."""
    g = pd.read_parquet(os.path.join(CACHE, "games.parquet")); g = g[(g.season == 2026) & (g.game_type == "REG") & g.home_score.isna()]
    wk = int(g.week.min()); a, h = g[g.week == wk].sort_values(["gameday", "gametime"]).iloc[0][["away_team", "home_team"]]
    full = {"DAL": "Dallas Cowboys", "TB": "Tampa Bay Buccaneers", "GB": "Green Bay Packers", "CHI": "Chicago Bears", "PHI": "Philadelphia Eagles", "JAX": "Jacksonville Jaguars"}
    if a not in full or h not in full:
        pytest.skip("first Week game uses teams outside the test name table")
    row = g[(g.away_team == a) & (g.home_team == h)].iloc[0]
    et = pd.Timestamp(f"{row.gameday} {row.gametime}"); commence_pt = et - pd.Timedelta(hours=3)       # ET -> PT
    last = commence_pt - pd.Timedelta(hours=1)
    def rows(book, over, under, game_away, game_home, ct):
        base = dict(game_id="x", commence_time=ct, in_play=False, bookmaker=book, last_update=last, home_team=game_home, away_team=game_away, market="player_receptions", description="Test Player", point=3.5)
        return [dict(base, label="Over", price=over), dict(base, label="Under", price=under)]
    rs = rows("A", -110, -110, full[a], full[h], commence_pt) + rows("B", -130, 110, full[a], full[h], commence_pt) + rows("C", -110, -110, "Philadelphia Eagles", "Jacksonville Jaguars", commence_pt + pd.Timedelta(days=9))
    x = tmp_path / "odds.xlsx"; pd.DataFrame(rs).to_excel(x, index=False)
    env = dict(os.environ, APEX_NFLV=CACHE, APEX_OUT=str(tmp_path), APEX_ENV="market", APEX_NS="500", APEX_ODDS_XLSX=str(x))
    r = subprocess.run([sys.executable, "price_odds.py"], cwd=WEEKLY, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    rej = pd.read_csv(tmp_path / "props_lines_rejected.csv")
    assert len(rej) == 2 and rej.reject.str.contains("not a Week").all()          # the far-future game is excluded
    pl = pd.read_csv(tmp_path / "props_lines.csv")
    assert set(pl.as_of_utc) == {(last + pd.Timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")}      # Pacific + 7h
    meta = pd.read_csv(tmp_path / "odds_meta.csv"); assert int(meta.tz_offset_h.iloc[0]) == 7
