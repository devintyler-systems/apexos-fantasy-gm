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


def test_nfl_feed_governs_a_player_it_already_carries_and_the_overlay_fills_the_rest_of_that_team():
    out = apply_status_overlay(_inj(), _ov(), {})
    assert out[out.full_name == "Tyreek Hill"].report_status.iloc[0] == "Questionable"      # the NFL row is kept, the overlay's Out is ignored
    extra = pd.DataFrame([dict(player="Rhamondre Stevenson", team="NE", pos="RB", report_status="Questionable")])
    out2 = apply_status_overlay(_inj(), pd.concat([_ov(), extra]), {})
    assert out2[out2.full_name == "Rhamondre Stevenson"].report_status.iloc[0] == "Questionable"      # a team with some NFL rows still gets overlay rows for players the feed lacks


def test_only_out_doubtful_questionable_are_used():
    out = apply_status_overlay(_inj(), _ov(), {})
    assert "Zach Charbonnet" not in set(out.full_name)


def test_newer_overlay_status_replaces_the_nfl_row_when_flagged():
    ov = pd.concat([_ov(), pd.DataFrame([dict(player="Tyreek Hill", team="NE", pos="WR", report_status="Out", override=True)])])
    out = apply_status_overlay(_inj(), ov, {})
    assert out[out.full_name == "Tyreek Hill"].report_status.iloc[0] == "Out"


def test_active_row_clears_the_designation():
    ov = pd.DataFrame([dict(player="Tyreek Hill", team="NE", pos="WR", report_status="Active")])
    out = apply_status_overlay(_inj(), ov, {})
    assert "Tyreek Hill" not in set(out.full_name)      # the player leaves the injury table, so he is treated as healthy
