import numpy as np
import pandas as pd
import pytest

import league_spm as L

CFG = L.load_cfg()


def _P():
    return pd.DataFrame([
        dict(player="Jalen Hurts", pos="QB", team="PHI", opp="CAR", p_active=0.98, pass_td_mean=1.2, rush_td_mean=0.2, rec_td_mean=np.nan),
        dict(player="Marvin Harrison Jr.", pos="WR", team="HOU", opp="JAX", p_active=1.0, pass_td_mean=np.nan, rush_td_mean=0.0, rec_td_mean=0.15),
        dict(player="Tucker Kraft", pos="TE", team="GB", opp="DAL", p_active=1.0, pass_td_mean=np.nan, rush_td_mean=0.03, rec_td_mean=0.44),
    ])


def test_skill_points_are_six_per_td_times_availability():
    S = L.skill_points(_P(), CFG).set_index("player")
    assert S.loc["Jalen Hurts", "ev"] == pytest.approx(6 * 1.4 * 0.98)
    assert S.loc["Tucker Kraft", "slot"] == "WT"
    assert S.loc["Marvin Harrison Jr.", "key"] == "marvin harrison|HOU"


def test_kicker_ev_uses_implied_points_only():
    assert L.kicker_ev(22.22, CFG) == pytest.approx(4.078 + 0.1439 * 22.22)
    assert L.kicker_ev(29, CFG) > L.kicker_ev(21, CFG)


def test_name_and_team_normalisation():
    assert L.norm_name("Marvin Harrison") == L.norm_name("Marvin Harrison Jr.")
    assert L.norm_name("D'Andre Swift") == "dandre swift"
    assert L.norm_team("LAR", CFG) == "LA"


def _fx(tmp_path, rows):
    p = tmp_path / "fx.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    return L.read_fantrax(str(p), CFG)


def test_read_fantrax_availability_and_bye(tmp_path):
    fx = _fx(tmp_path, [
        dict(Player="A", Team="LAR", Position="K", Status="W <small>(Thu)</small>", Opponent="ARI (11th) Sun"),
        dict(Player="B", Team="MIN", Position="K", Status="FA", Opponent="Bye"),
        dict(Player="C", Team="PHI", Position="QB", Status="FLEX", Opponent="CAR (20th) Sun"),
        dict(Player="D", Team="KC", Position="WT", Status="Cockney", Opponent="LAC"),
    ])
    assert list(fx.avail) == ["W", "FA", "ROSTERED", "ROSTERED"]
    assert list(fx.bye) == [False, True, False, False]
    assert fx.loc[0, "team"] == "LA" and fx.loc[3, "slot"] == "WT"


def test_attach_ev_bye_zero_missing_nan_and_kicker_validity(tmp_path):
    fx = _fx(tmp_path, [
        dict(Player="Jalen Hurts", Team="PHI", Position="QB", Status="FLEX", Opponent="CAR"),
        dict(Player="Will Reichard", Team="MIN", Position="K", Status="FLEX", Opponent="Bye"),
        dict(Player="Matsuzawa", Team="LV", Position="K", Status="W", Opponent="BUF"),
        dict(Player="Matt Gay", Team="LV", Position="K", Status="W", Opponent="BUF"),
        dict(Player="Marvin Harrison", Team="HOU", Position="WT", Status="FA", Opponent="JAX"),
        dict(Player="Nobody Here", Team="HOU", Position="RB", Status="FA", Opponent="JAX"),
    ])
    out = L.attach_ev(fx, L.skill_points(_P(), CFG), {"PHI": 21.0, "LV": 23.8}, {"LV": "matt gay"}, CFG)
    assert out.loc[0, "ev"] == pytest.approx(6 * 1.4 * 0.98)
    assert out.loc[1, "ev"] == 0.0
    assert np.isnan(out.loc[2, "ev"]) and "current kicker" in out.loc[2, "note"]
    assert out.loc[3, "ev"] == pytest.approx(L.kicker_ev(23.8, CFG))
    assert out.loc[4, "ev"] == pytest.approx(6 * 0.15)
    assert np.isnan(out.loc[5, "ev"])


def test_decision_rule():
    assert L.decide(0.0, 0.2, False, CFG)[0] is True            # bye drop: any gain
    assert L.decide(0.0, 0.0, False, CFG)[0] is False
    assert L.decide(8.5, 9.5, False, CFG)[0] is True            # exactly 1.0 clears
    assert L.decide(8.5, 9.4, False, CFG)[0] is False           # irreversible drop below threshold
    ok, _, why = L.decide(8.5, 10.0, True, CFG)
    assert ok is False and "streak" in why


def test_kicker_tie_band_orders_by_team_points():
    c = pd.DataFrame([dict(player="Hi", ev=8.20, team_pts=21.0), dict(player="Env", ev=7.90, team_pts=29.0), dict(player="Low", ev=6.5, team_pts=33.0)])
    o = L.order_candidates(c, CFG, "K")
    assert list(o.player) == ["Env", "Hi", "Low"]
    assert list(L.order_candidates(c, CFG, "QB").player) == ["Hi", "Env", "Low"]


def test_moves_end_to_end_and_no_double_claim():
    def row(player, slot, ev, avail="ROSTERED", team="X", tp=22.0):
        return dict(player=player, slot=slot, ev=ev, avail=avail, team=team, team_pts=tp, nkey=L.norm_name(player), exp_tds=ev / 6 if ev else np.nan)
    ro = pd.DataFrame([row("Hurts", "QB", 8.5), row("Reichard", "K", 0.0), row("Warren", "WT", 1.9), row("Johnson", "WT", 2.5), row("Watson", "WT", 3.2)])
    av = pd.DataFrame([row("Rodgers", "QB", 9.4, "W"), row("Folk", "K", 7.9, "W", tp=23.3), row("Fitz", "K", 7.95, "FA", tp=21.0),
                       row("Kraft", "WT", 2.8, "W"), row("Henry", "WT", 2.3, "W"), row("Star", "WT", 3.0, "FA")])
    mv = L.moves(ro, av, None, CFG)
    by = {(m.slot, m["drop"]): m for _, m in mv.iterrows()}
    assert by[("QB", "Hurts")].act is False                      # 0.9 < 1.0
    assert by[("K", "Reichard")].act is True and by[("K", "Reichard")]["add"] == "Folk"   # tie band -> higher team points
    assert by[("WT", "Warren")]["add"] == "Star" and by[("WT", "Warren")].act is True   # 1.1 clears the irreversible threshold
    assert by[("WT", "Johnson")]["add"] == "Kraft" and by[("WT", "Johnson")].act is False   # 0.3 does not
    assert mv[mv.act]["add"].is_unique
