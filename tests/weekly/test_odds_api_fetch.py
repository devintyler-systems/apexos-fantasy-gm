import odds_api_fetch as O


def test_flatten_matches_the_workbook_schema_and_shifts_to_pacific():
    ev = dict(id="g1", commence_time="2026-10-25T17:00:00Z", home_team="Baltimore Ravens", away_team="Cincinnati Bengals", bookmakers=[dict(key="draftkings", title="DraftKings", last_update="2026-10-25T15:30:00Z", markets=[
        dict(key="player_rush_yds", last_update="2026-10-25T15:31:00Z", outcomes=[dict(name="Over", description="Chase Brown", price=-115, point=41.5), dict(name="Under", description="Chase Brown", price=-105, point=41.5)])])])
    rows = O.flatten(ev)
    assert len(rows) == 2 and rows[0]["market"] == "player_rush_yds" and rows[0]["label"] == "Over" and rows[0]["price"] == -115 and rows[0]["point"] == 41.5
    assert rows[0]["commence_time"].hour == 10 and rows[0]["last_update"].minute == 31      # 17:00Z is 10:00 Pacific
