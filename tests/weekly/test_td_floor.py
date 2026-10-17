import json
import os

import pytest

import td_floor as F

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_floor_applies_only_to_active_non_qb_with_a_receiving_role():
    assert F.floor_anytime(0.03, "WR", 0.9, 0.06) == pytest.approx(0.06)
    assert F.floor_anytime(0.03, "TE", 0.5, 0.06) == pytest.approx(0.06)
    assert F.floor_anytime(0.10, "WR", 2.0, 0.06) == pytest.approx(0.10)       # never lowers
    assert F.floor_anytime(0.03, "QB", 3.0, 0.06) == pytest.approx(0.03)       # QB rushing TDs are calibrated separately
    assert F.floor_anytime(0.03, "WR", 0.3, 0.06) == pytest.approx(0.03)       # no receiving role: outside the measured population
    assert F.floor_anytime(0.03, "WR", 1.5, 0.06, active=False) == pytest.approx(0.03)
    assert F.floor_anytime(0.03, "WR", 1.5, 0.0) == pytest.approx(0.03)        # 0.0 = baseline, no change


def test_load_floor_defaults_to_baseline(tmp_path):
    assert F.load_floor(None) == 0.0
    assert F.load_floor(str(tmp_path / "missing.json")) == 0.0
    p = tmp_path / "t.json"; p.write_text(json.dumps({"rec_td": {}}))
    assert F.load_floor(str(p)) == 0.0
    p.write_text(json.dumps({"anytime_floor": 0.06}))
    assert F.load_floor(str(p)) == pytest.approx(0.06)


def test_live_config_is_baseline_and_candidate_extends_v2():
    live = json.load(open(os.path.join(ROOT, "config", "weekly", "td_params.json")))
    cand = json.load(open(os.path.join(ROOT, "config", "weekly", "td_params.candidate_v3.json")))
    assert "anytime_floor" not in live                                         # candidate is not adopted
    assert cand["anytime_floor"] == pytest.approx(0.06)
    assert cand["rec_td"] == live["rec_td"] and cand["rush_td"] == live["rush_td"]   # same v2 multipliers
