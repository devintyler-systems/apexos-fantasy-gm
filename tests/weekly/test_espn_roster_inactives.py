import espn_roster_inactives as R


def test_dnp_ids_takes_only_flagged_players():
    j = {"entries": [dict(playerId=1, didNotPlay=True), dict(playerId=2, didNotPlay=False), dict(playerId=3, didNotPlay=True), dict(playerId=4)]}
    assert R.dnp_ids(j) == ["1", "3"]
    assert R.dnp_ids({}) == []
