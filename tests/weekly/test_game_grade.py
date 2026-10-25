import pandas as pd

from game_grade import _kickoff_utc, summarize


def test_kickoff_utc_uses_edt_before_the_first_sunday_of_november_and_est_after():
    r = lambda d, t: type("R", (), dict(gameday=d, gametime=t))()
    assert _kickoff_utc(r("2026-10-25", "13:00")).hour == 17      # EDT, UTC-4
    assert _kickoff_utc(r("2026-11-01", "13:00")).hour == 18      # the first Sunday of November: EST, UTC-5 (DST ends at 2 AM)


def test_summarize_scores_a_perfect_model_better_than_the_line():
    d = pd.DataFrame(dict(week=[1, 1], game=["A@B", "C@D"], home_score=[24, 17], away_score=[20, 27], actual_margin=[4, -10], actual_total=[44, 44], line_margin=[1.0, 1.0], line_total=[40.0, 40.0],
                          model_margin=[4.0, -10.0], model_total=[44.0, 44.0], model_pwin=[0.7, 0.2], model_home=[24.0, 17.0], model_away=[20.0, 27.0]))
    s = summarize(d).set_index("predictor")
    assert s.loc["model-only", "margin_MAE"] == 0 and s.loc["line", "margin_MAE"] > 0
    assert s.loc["model-only", "winner_acc"] == 1.0
