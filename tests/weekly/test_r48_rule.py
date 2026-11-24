import pandas as pd

import r48_rule


def _roster():
    return pd.DataFrame([
        dict(nkey="roman wilson", team="PIT", status="RES", status_description_abbr="R48"),
        dict(nkey="michael pittman", team="PIT", status="RES", status_description_abbr="R48"),
        dict(nkey="will shipley", team="PHI", status="RES", status_description_abbr="R48"),
        dict(nkey="jonathon brooks", team="CAR", status="RES", status_description_abbr="R48"),
        dict(nkey="other reserve", team="CAR", status="RES", status_description_abbr="R40"),
        dict(nkey="healthy player", team="PIT", status="ACT", status_description_abbr="A01"),
    ])


def _inj():
    return pd.DataFrame([
        dict(nkey="roman wilson", team="PIT", game_status="Questionable", practice="FP"),
        dict(nkey="michael pittman", team="PIT", game_status="Doubtful", practice="LP"),      # Doubtful stays Out
        dict(nkey="will shipley", team="PHI", game_status="Questionable", practice="LP"),
        dict(nkey="jonathon brooks", team="CAR", game_status="Questionable", practice="DNP"),      # practice status is not a condition (W11: Shipley DNP, played)
        dict(nkey="other reserve", team="CAR", game_status="Questionable", practice="FP"),      # different reserve code: stays Out
    ])


def test_only_r48_questionable_players_are_exempt(monkeypatch):
    monkeypatch.delenv("APEX_R48_P", raising=False)
    got = r48_rule.exempt_keys(_roster(), _inj())
    assert set(got) == {("roman wilson", "PIT"), ("will shipley", "PHI"), ("jonathon brooks", "CAR")}


def test_off_switch_restores_the_hard_out(monkeypatch):
    monkeypatch.setenv("APEX_R48_P", "off")
    assert r48_rule.exempt_keys(_roster(), _inj()) == {}
    assert r48_rule.prob() is None


def test_probability_default_and_override(monkeypatch):
    monkeypatch.delenv("APEX_R48_P", raising=False)
    assert r48_rule.prob() == 0.5
    monkeypatch.setenv("APEX_R48_P", "0.3")
    assert r48_rule.prob() == 0.3


def test_a_player_not_on_the_report_stays_out(monkeypatch):
    monkeypatch.delenv("APEX_R48_P", raising=False)
    assert r48_rule.exempt_keys(_roster(), _inj().iloc[:0]) == {}
