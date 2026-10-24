import pandas as pd

from status_overlay import apply_status_overlay


def _inj():
    return pd.DataFrame([
        dict(full_name="Mike Evans", position="WR", team="SF", report_status=None, practice_status="Did Not Participate In Practice", report_primary_injury=None, practice_primary_injury="Hamstring", game_type="REG", week=7),
        dict(full_name="Tyreek Hill", position="WR", team="NE", report_status="Questionable", practice_status="Limited Participation in Practice", report_primary_injury="Ankle", practice_primary_injury="Ankle", game_type="REG", week=7)])


def _ov():
    return pd.DataFrame([dict(player="Mike Evans", team="SF", pos="WR", report_status="Out"), dict(player="Deebo Samuel Sr.", team="SF", pos="WR", report_status="Out"),
                         dict(player="Tyreek Hill", team="NE", pos="WR", report_status="Out"), dict(player="Zach Charbonnet", team="SEA", pos="RB", report_status="IR")])


def test_overlay_sets_designation_for_teams_without_an_nfl_report_and_adds_unmatched_players():
    out = apply_status_overlay(_inj(), _ov(), {})
    assert out[out.full_name == "Mike Evans"].report_status.iloc[0] == "Out"
    assert out[out.full_name == "Mike Evans"].practice_status.iloc[0] == "Did Not Participate In Practice"      # practice status stays the nflverse one
    assert "Deebo Samuel Sr." in set(out.full_name)


def test_nfl_feed_governs_a_team_it_already_covers():
    out = apply_status_overlay(_inj(), _ov(), {})
    assert out[out.full_name == "Tyreek Hill"].report_status.iloc[0] == "Questionable"      # NE already has designations: overlay ignored


def test_only_out_doubtful_questionable_are_used():
    out = apply_status_overlay(_inj(), _ov(), {})
    assert "Zach Charbonnet" not in set(out.full_name)
