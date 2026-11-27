"""Build the anchor-lines CSV for the #91 backtest from the #84 closing-price tables (var/bt/odds_td_{TAG}.pkl, odds_yds_{TAG}.pkl).

  python tools/backtest/build_anchor_lines.py prn3A var/anchor/lines_close_2023_25.csv
Columns: season, week, away, home, nkey, market, line, p. Anytime TD p = leave-one-season-out de-vigged consensus (#84), so the TD level is not
fitted on the season it anchors; yardage p = two-way no-vig consensus at the main line (no outcome fitting).
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import odds_price_eval as ope  # noqa: E402

tag, out = sys.argv[1], sys.argv[2]
D = ope.engine(tag); BT = os.path.join(ope.REPO, "var", "bt")
g = ope.games().set_index("game_id")
def meta(df):
    df = df.assign(season=D.loc[df.di, "season"].values, week=D.loc[df.di, "week"].values, nkey=D.loc[df.di, "nkey"].values)
    df["away"] = g.loc[df.game_id, "away_team"].values; df["home"] = g.loc[df.game_id, "home_team"].values
    return df
T = meta(pd.read_pickle(os.path.join(BT, f"odds_td_{tag}.pkl"))).assign(market="anytime_td", line=float("nan")).rename(columns={"cons": "p"})
Y = meta(pd.read_pickle(os.path.join(BT, f"odds_yds_{tag}.pkl")))
Y = Y.assign(market=Y.market.map({"player_reception_yds": "rec_yds", "player_rush_yds": "rush_yds", "player_pass_yds": "pass_yds"}), line=Y.point, p=Y.book)
cols = ["season", "week", "away", "home", "nkey", "market", "line", "p"]
L = pd.concat([T[cols], Y[cols]], ignore_index=True)
os.makedirs(os.path.dirname(out), exist_ok=True); L.to_csv(out, index=False)
print(len(L), "lines;", L.market.value_counts().to_dict())
