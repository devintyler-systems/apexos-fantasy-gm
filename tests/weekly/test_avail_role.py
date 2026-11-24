import pandas as pd

import avail_role


def _snaps():
    rows = []
    for w, pct in ((1, 1.0), (2, 1.0), (3, 0.0), (4, 0.9)):      # starter: sits out week 3 (injured), plays week 4
        if pct > 0: rows.append(dict(season=2025, game_type="REG", week=w, pfr_player_id="STARTER", offense_snaps=60, offense_pct=pct))
    for w in (1, 2, 3, 4): rows.append(dict(season=2025, game_type="REG", week=w, pfr_player_id="BACKUP", offense_snaps=3, offense_pct=0.05))
    rows.append(dict(season=2024, game_type="REG", week=17, pfr_player_id="PRIOR", offense_snaps=60, offense_pct=1.0))      # last season does not count
    return pd.DataFrame(rows)


PL = pd.DataFrame([dict(gsis_id="g1", pfr_id="STARTER"), dict(gsis_id="g2", pfr_id="BACKUP"), dict(gsis_id="g3", pfr_id="PRIOR")])


def test_recent_pct_uses_only_earlier_games_of_the_same_season():
    r = avail_role.recent_pct(_snaps(), PL, 2025, 4)
    assert round(r["g1"], 2) == 1.0 and round(r["g2"], 2) == 0.05
    assert "g3" not in r.index
    r5 = avail_role.recent_pct(_snaps(), PL, 2025, 5)
    assert round(r5["g1"], 3) == round((1.0 + 1.0 + 0.9) / 3, 3)      # week 4 counts for week 5, the week he missed does not


def test_role_labels():
    assert avail_role.role(0.9, 6) == "S"
    assert avail_role.role(0.2, 6) == "O"
    assert avail_role.role(float("nan"), 6) == "O"      # no snaps by week 6: a non-starter
    assert avail_role.role(float("nan"), 2) == "U"      # no history yet in week 2
    assert avail_role.role(None, 1) == "U"
