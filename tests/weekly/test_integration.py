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
