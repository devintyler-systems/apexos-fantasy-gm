from types import SimpleNamespace

import numpy as np
import pytest

import tnf_full as T


def test_american_and_play_price():
    assert T.american(0.5) == -100 or T.american(0.5) == 100
    assert T.american(0.75) == -300
    assert T.american(0.2) == 400
    assert T.play_price(0.2) < 0 or T.play_price(0.2) > T.american(0.2)   # the cushion always asks for a better price than fair
    assert T.play_price(0.2) > 400


def _row(**kw):
    base = dict(market="rec", p_over=0.30, p_under=0.70, p_push=0.0, pa=1.0, n_log=5, over_games=1, under_games=4)
    base.update(kw)
    return SimpleNamespace(**base)


def test_gate_play_lean_and_support():
    side, sh, mp, label, log = T.gate(_row())
    assert side == "UNDER" and mp == pytest.approx(0.70) and sh == pytest.approx(0.6) and label == "PLAY" and log == "4/5"
    assert T.gate(_row(under_games=1, over_games=4))[3] != "PLAY"          # season games do not support the side
    assert T.gate(_row(pa=0.9))[3] != "PLAY"                               # availability below 95%
    assert T.gate(_row(p_over=0.46, p_under=0.54))[3] == ""                # inside the market


def test_gate_passing_overs_get_the_bias_shift():
    plain = T.gate(_row(market="rec", p_over=0.50, p_under=0.50))[2]
    shifted = T.gate(_row(market="pass_yds", p_over=0.50, p_under=0.50))
    assert shifted[0] == "OVER" and shifted[2] == pytest.approx(0.58) and plain == pytest.approx(0.50)


def test_gate_pushes_are_excluded():
    side, sh, mp, label, _ = T.gate(_row(p_over=0.2, p_under=0.6, p_push=0.2))
    assert side == "UNDER" and mp == pytest.approx(0.75)
