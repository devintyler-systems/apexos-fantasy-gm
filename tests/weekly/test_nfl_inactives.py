import pandas as pd

import nfl_inactives as N


def test_build_merges_ina_rows_without_duplicating_espn_rows(tmp_path, monkeypatch):
    r = pd.DataFrame(dict(team=["PIT", "PIT", "NO"], status=["INA", "ACT", "INA"], full_name=["A Back", "B Star", "C Wide"], position=["RB", "WR", "WR"], gsis_id=["g1", "g2", "g3"], week=[7, 7, 7]))
    g = pd.DataFrame(dict(season=[2026], week=[7], home_team=["NO"], away_team=["PIT"]))
    store = {"roster_2026.parquet": r, "games.parquet": g}
    monkeypatch.setattr(N.pd, "read_parquet", lambda p, **k: store[p.rsplit("/", 1)[-1]])
    m = tmp_path / "m.csv"
    pd.DataFrame(dict(player=["A Back"], team=["PIT"], pos=["RB"], source=["espn"], as_of_utc=["x"], note=[""], gsis_id=["g1"], game=["PIT@NO"], espn_status=["Out"])).to_csv(m, index=False)
    df, pending = N.build(2026, 7, str(m))
    assert sorted(df.gsis_id) == ["g1", "g3"] and pending == []      # g1 kept once, g3 added, the ACT player is never written
