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


def test_live_config_carries_v2_multipliers_and_the_adopted_floor():
    live = json.load(open(os.path.join(ROOT, "config", "weekly", "td_params.json")))
    assert live["anytime_floor"] == pytest.approx(0.06)                          # v3 adopted 2026-10-17 (DECISIONS #30)
    assert live["rec_td"] == {"WR": 1.17, "TE": 1.2, "RB": 0.88}                 # v2 multipliers unchanged
    assert live["rush_td"] == {"QB": 1.35, "RB": 0.92}
    assert not os.path.exists(os.path.join(ROOT, "config", "weekly", "td_params.candidate_v3.json"))
    assert F.load_floor(os.path.join(ROOT, "config", "weekly", "td_params.json")) == pytest.approx(0.06)
