import numpy as np
import pandas as pd

from qb_fill import adjust_qbs


def _pas():
    return pd.DataFrame([dict(player="Jalen Hurts", nkey="jalen hurts", team="PHI", Att=154.0, pfr_id="HurtJa00"),
                         dict(player="Andy Dalton", nkey="andy dalton", team="PHI", Att=1.0, pfr_id="DaltAn00")])


def _dc():
    return pd.DataFrame([dict(player_name="Jalen Hurts", nkey="jalen hurts", pos_rank=1), dict(player_name="Tanner McKee", nkey="tanner mckee", pos_rank=2),
                         dict(player_name="Cole Payton", nkey="cole payton", pos_rank=3)])


def test_released_qb_is_dropped_and_depth_chart_qbs_without_attempts_are_added():
    q = adjust_qbs(_pas(), _dc(), {"andy dalton"}, True)
    assert "Andy Dalton" not in set(q.player)
    assert list(q.player) == ["Jalen Hurts", "Tanner McKee", "Cole Payton"]
    mck = q[q.player == "Tanner McKee"].iloc[0]
    assert mck.Att == 0.0 and mck.team == "PHI" and mck.nkey == "tanner mckee" and np.isnan(mck.pfr_id)


def test_historical_mode_changes_nothing():
    q = adjust_qbs(_pas(), _dc(), set(), False)
    assert list(q.player) == ["Jalen Hurts", "Andy Dalton"]


def test_gone_qb_is_not_re_added_from_the_depth_chart():
    dc = pd.concat([_dc(), pd.DataFrame([dict(player_name="Andy Dalton", nkey="andy dalton", pos_rank=4)])])
    q = adjust_qbs(_pas(), dc, {"andy dalton"}, True)
    assert "Andy Dalton" not in set(q.player)
