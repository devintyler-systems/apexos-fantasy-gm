"""value_board: touchdown markets blend at 0.5, every other market equals the book (DECISIONS #64)."""
import pandas as pd

from value_board import blend_weight, build


def test_weights():
    assert blend_weight("anytime_td") == 0.5 and blend_weight("pass_td") == 0.5 and blend_weight("rec_yds") == 0.0


def test_build_blend(tmp_path):
    rows = []
    for mk, side, line, model_p in (("anytime_td", "yes", None, 0.40), ("rec_yds", "over", 50.5, 0.70)):
        rows.append(dict(player="A B", team="XX", market=mk, side=side, line=line, book="b1", odds=-110 if mk == "rec_yds" else 200, novig_p=0.50 if mk == "rec_yds" else 0.30, model_p=model_p,
                         p_active=1.0, is_main_line=True, model_gap_flag=False, model_gt_85_suppress=False, novig_method="two_way" if mk == "rec_yds" else "Estimated one-sided"))
    pd.DataFrame(rows).to_csv(tmp_path / "edges_all_rows.csv", index=False)
    g = build(str(tmp_path)).set_index("market")
    assert abs(g.loc["anytime_td", "final_p"] - 0.35) < 1e-9
    assert abs(g.loc["rec_yds", "final_p"] - 0.50) < 1e-9
