"""fetch_data.games_csv_to_parquet: the nfldata CSV fallback keeps the games.parquet dtypes the engine reads."""
import pandas as pd

from fetch_data import games_csv_to_parquet


def test_csv_fallback_dtypes(tmp_path):
    pd.DataFrame([dict(game_id="2026_12_GB_LA", season=2026, game_type="REG", week=12, gameday="2026-11-25", gametime="20:00", away_team="GB", home_team="LA",
                       old_game_id=2026112500, espn=401999999, away_rest=7, home_rest=7, div_game=0, spread_line=2.5, total_line=44.5)]).to_csv(tmp_path / "g.csv", index=False)
    n = games_csv_to_parquet(str(tmp_path / "g.csv"), str(tmp_path / "games.parquet"))
    g = pd.read_parquet(tmp_path / "games.parquet")
    assert n == 1 and str(g.season.dtype) == "int32" and str(g.week.dtype) == "int32" and g.old_game_id.iloc[0] == "2026112500" and g.spread_line.iloc[0] == 2.5
