"""value_board: touchdown markets blend at 0.2 (DECISIONS #84/#86), every other market equals the book (#64)."""
import pandas as pd

from value_board import blend_weight, build


def test_weights():
    assert blend_weight("anytime_td") == 0.2 and blend_weight("pass_td") == 0.2 and blend_weight("rec_yds") == 0.0


def test_build_blend(tmp_path):
    rows = []
    for mk, side, line, model_p in (("anytime_td", "yes", None, 0.40), ("rec_yds", "over", 50.5, 0.70)):
        rows.append(dict(player="A B", team="XX", market=mk, side=side, line=line, book="b1", odds=-110 if mk == "rec_yds" else 200, novig_p=0.50 if mk == "rec_yds" else 0.30, model_p=model_p,
                         p_active=1.0, is_main_line=True, model_gap_flag=False, model_gt_85_suppress=False, novig_method="two_way" if mk == "rec_yds" else "Estimated one-sided"))
    pd.DataFrame(rows).to_csv(tmp_path / "edges_all_rows.csv", index=False)
    g = build(str(tmp_path)).set_index("market")
    assert abs(g.loc["anytime_td", "final_p"] - 0.32) < 1e-9
    assert abs(g.loc["rec_yds", "final_p"] - 0.50) < 1e-9


def test_forward_test_flag_only_for_5_to_10_point_gaps(tmp_path):
    rows = [dict(player=f"P{i}", team="XX", market="anytime_td", side="yes", line=None, book="b1", odds=200, novig_p=0.30, model_p=mp, p_active=1.0, is_main_line=True,
                 model_gap_flag=False, model_gt_85_suppress=False, novig_method="Estimated one-sided") for i, mp in enumerate((0.33, 0.37, 0.45))]
    pd.DataFrame(rows).to_csv(tmp_path / "edges_all_rows.csv", index=False)
    g = build(str(tmp_path)).set_index("player")
    assert list(g.fwd_test) == [False, True, False]


def test_forward_test_excludes_quarterbacks(tmp_path):
    rows = [dict(player=n, team="XX", market="anytime_td", side="yes", line=None, book="b1", odds=200, novig_p=0.30, model_p=0.37, p_active=1.0, is_main_line=True,
                 model_gap_flag=False, model_gt_85_suppress=False, novig_method="Estimated one-sided", pos=p) for n, p in (("Q B", "QB"), ("R B", "RB"))]
    pd.DataFrame(rows).to_csv(tmp_path / "edges_all_rows.csv", index=False)
    g = build(str(tmp_path)).set_index("player")
    assert not bool(g.loc["Q B", "fwd_test"]) and bool(g.loc["R B", "fwd_test"])
