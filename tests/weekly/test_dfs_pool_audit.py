"""DECISIONS #93: a scoring-eligible DK player missing from the sims is a pool gap; manual-out players are explained, not gaps."""
import pandas as pd

from dfs_pool_audit import audit


def _sal():
    return pd.DataFrame([
        dict(Name="Brandon McManus", Position="K", TeamAbbrev="LAR", Salary=4600, AvgPointsPerGame=7.5, Status=""),
        dict(Name="Rams", Position="DST", TeamAbbrev="LAR", Salary=4000, AvgPointsPerGame=6.5, Status=""),
        dict(Name="Kyren Williams", Position="RB", TeamAbbrev="LAR", Salary=8600, AvgPointsPerGame=16.6, Status=""),
        dict(Name="Puka Nacua", Position="WR", TeamAbbrev="LAR", Salary=200, AvgPointsPerGame=26.2, Status="IR"),
        dict(Name="Some Depth", Position="WR", TeamAbbrev="GB", Salary=200, AvgPointsPerGame=0.5, Status=""),
        dict(Name="Zay Jones", Position="WR", TeamAbbrev="GB", Salary=2000, AvgPointsPerGame=4.0, Status="")])


def test_missing_kicker_is_a_gap_and_ir_or_low_scorers_are_not(tmp_path):
    gaps, expl = audit(_sal(), {("kyren williams", "LA"), ("rams", "LA")}, qb1=set())
    assert set(gaps.Name) == {"Brandon McManus", "Zay Jones"}


def test_manual_out_players_are_explained(tmp_path):
    mo = tmp_path / "mo.csv"; pd.DataFrame([dict(player="Zay Jones", team="GB")]).to_csv(mo, index=False)
    gaps, expl = audit(_sal(), {("kyren williams", "LA"), ("rams", "LA"), ("brandon mcmanus", "LA")}, str(mo), qb1=set())
    assert gaps.empty and list(expl.Name) == ["Zay Jones"]


def test_backup_qb_and_zero_average_kicker_are_not_required():
    sal = pd.DataFrame([dict(Name="Case Keenum", Position="QB", TeamAbbrev="CHI", Salary=4000, AvgPointsPerGame=9.1, Status=""),
                        dict(Name="Caleb Williams", Position="QB", TeamAbbrev="CHI", Salary=5800, AvgPointsPerGame=19.5, Status=""),
                        dict(Name="Justin Tucker", Position="K", TeamAbbrev="KC", Salary=4800, AvgPointsPerGame=0.0, Status="")])
    gaps, _ = audit(sal, set(), qb1={("caleb williams", "CHI")})
    assert list(gaps.Name) == ["Caleb Williams"]


def test_no_missing_players_returns_empty_frames():
    sal = pd.DataFrame([dict(Name="Rams", Position="DST", TeamAbbrev="LAR", Salary=4000, AvgPointsPerGame=6.5, Status="")])
    gaps, expl = audit(sal, {("rams", "LA")}, qb1=set())
    assert gaps.empty and expl.empty and "Name" in gaps.columns
