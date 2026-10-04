import json
import os

import numpy as np
import pandas as pd
import pytest

import manifest
import grade
from paths import NFLV


def _out(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    P = pd.DataFrame([
        dict(player="Patrick Mahomes", pos="QB", team="KC", opp="LAC", game="LAC@KC", played=False, p_active=1.0, pass_cmp_mean=24.0, pass_cmp_p25=21, pass_cmp_p75=27,
             pass_yds_mean=270.0, pass_yds_p25=230, pass_yds_p75=310, pass_td_mean=2.0, pass_td_p25=1, pass_td_p75=3, rush_att_mean=3.0, rush_yds_mean=10.0, rush_yds_p25=0, rush_yds_p75=15,
             any_td_pct=0.05, rec_mean=np.nan, rec_yds_mean=np.nan, rec_yds_p25=np.nan, rec_yds_p75=np.nan, rec_p25=np.nan, rec_p75=np.nan),
        dict(player="Travis Kelce", pos="TE", team="KC", opp="LAC", game="LAC@KC", played=False, p_active=1.0, pass_cmp_mean=np.nan, pass_cmp_p25=np.nan, pass_cmp_p75=np.nan,
             pass_yds_mean=np.nan, pass_yds_p25=np.nan, pass_yds_p75=np.nan, pass_td_mean=np.nan, pass_td_p25=np.nan, pass_td_p75=np.nan, rush_att_mean=0.0, rush_yds_mean=0.0, rush_yds_p25=0, rush_yds_p75=0,
             any_td_pct=0.40, rec_mean=5.0, rec_yds_mean=60.0, rec_yds_p25=40.0, rec_yds_p75=80.0, rec_p25=4, rec_p75=7),
    ])
    P.to_pickle(out / "proj_all.pkl")
    P.to_pickle(out / "rank_raw.pkl")
    pd.DataFrame([dict(away="LAC", home="KC", KC_pts_mean=27.0, LAC_pts_mean=20.0)]).to_csv(out / "w4_game_environment.csv", index=False)
    return str(out)


def _nflverse(season=2026, week=4):
    os.makedirs(NFLV, exist_ok=True)
    st = pd.DataFrame([
        dict(player_display_name="Patrick Mahomes", team="KC", season=season, week=week, season_type="REG", completions=20, passing_yards=250, passing_tds=1, rushing_yards=5, carries=3, receptions=0, receiving_yards=0, rushing_tds=0, receiving_tds=0),
        dict(player_display_name="Travis Kelce", team="KC", season=season, week=week, season_type="REG", completions=0, passing_yards=0, passing_tds=0, rushing_yards=0, carries=0, receptions=7, receiving_yards=80, rushing_tds=0, receiving_tds=1),
    ])
    st.to_parquet(os.path.join(NFLV, f"stats_player_week_{season}.parquet"))
    pd.DataFrame([dict(player="Travis Kelce", team="KC", week=week, game_type="REG", offense_snaps=60, st_snaps=0, defense_snaps=0),
                  dict(player="Patrick Mahomes", team="KC", week=week, game_type="REG", offense_snaps=70, st_snaps=0, defense_snaps=0)]
                 ).to_parquet(os.path.join(NFLV, f"snap_counts_{season}.parquet"))
    pd.DataFrame([dict(season=season, week=week, game_type="REG", home_team="KC", away_team="LAC", home_score=30.0, away_score=17.0)]
                 ).to_parquet(os.path.join(NFLV, "games.parquet"))


def test_freeze_is_immutable_hashed_and_verifiable(tmp_path):
    out = _out(tmp_path)
    import datetime as dt
    t = dt.datetime(2026, 10, 4, 12, 0, 0, tzinfo=dt.timezone.utc)
    d = manifest.freeze(2026, 4, "market", out_dir=out, runs_dir=str(tmp_path / "runs"), as_of=t)
    man = json.load(open(os.path.join(d, "manifest.json")))
    assert man["run_id"] == "2026_w04_market_20261004T120000Z" and man["uses_future_information"] is False
    assert man["artifacts"]["projections.csv"]["rows"] == 2
    assert manifest.verify(d) == []
    with pytest.raises(FileExistsError):
        manifest.freeze(2026, 4, "market", out_dir=out, runs_dir=str(tmp_path / "runs"), as_of=t)
    with open(os.path.join(d, "projections.csv"), "a") as f:
        f.write("tamper\n")
    assert manifest.verify(d) == ["projections.csv"]


def test_freeze_deterministic_hashes(tmp_path):
    out = _out(tmp_path)
    import datetime as dt
    a = manifest.freeze(2026, 4, "model", out_dir=out, runs_dir=str(tmp_path / "r1"), as_of=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc))
    b = manifest.freeze(2026, 4, "model", out_dir=out, runs_dir=str(tmp_path / "r2"), as_of=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc))
    ma, mb = json.load(open(a + "/manifest.json")), json.load(open(b + "/manifest.json"))
    assert ma["artifacts"] == mb["artifacts"]


def test_freeze_refuses_without_projections(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(RuntimeError):
        manifest.freeze(2026, 4, "market", out_dir=str(empty), runs_dir=str(tmp_path / "runs"))


def test_grade_known_values(tmp_path):
    out = _out(tmp_path)
    _nflverse()
    import datetime as dt
    d = manifest.freeze(2026, 4, "market", out_dir=out, runs_dir=str(tmp_path / "runs"), as_of=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc))
    r = grade.grade(d)
    assert r["status"] == "graded" and r["games_graded"] == 1
    assert r["markets"]["pass_yds"]["mae"] == pytest.approx(20.0)          # 270 vs 250
    assert r["markets"]["pass_yds"]["bias"] == pytest.approx(20.0)
    assert r["markets"]["rec_yds"]["mae"] == pytest.approx(20.0)           # 60 vs 80
    assert r["markets"]["rec"]["p25_p75_coverage"] == pytest.approx(1.0)   # 7 within 4..7
    assert r["anytime_td"]["actual_scorers"] == 1.0
    assert r["team_points"]["winner_hit_rate"] == 1.0
    assert os.path.exists(os.path.join(d, "grade.json"))
    assert manifest.verify(d) == []   # grading must not disturb frozen artifacts


def test_grade_skips_games_not_final(tmp_path):
    out = _out(tmp_path)
    _nflverse()
    g = pd.read_parquet(os.path.join(NFLV, "games.parquet"))
    g["home_score"] = np.nan
    g["away_score"] = np.nan
    g.to_parquet(os.path.join(NFLV, "games.parquet"))
    import datetime as dt
    d = manifest.freeze(2026, 4, "market", out_dir=out, runs_dir=str(tmp_path / "runs"), as_of=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc))
    assert grade.grade(d)["status"] == "no_final_games"
