"""Non-TD prop screen for one game: model vs book at the main line, bias-centered gap (diagnostic ONLY, never a calibration), W1-4 actual game log vs the line, role flags,
best prices, and joint-simulation prices for 2-3 leg combos. Usage: APEX_ENV=market python tnf_props.py AWAY HOME"""
import sys, itertools, numpy as np, pandas as pd
from paths import OUT, NFLV
import run_all as R
from params import is_neutral, norm_name, SEASON
AWAY, HOME = sys.argv[1], sys.argv[2]; GAME = f"{AWAY}@{HOME}"
E = pd.read_csv("../../var/out_market/edges_all_rows.csv"); Ea = E.copy(); E = E[(E.game == GAME) & E.is_main_line & E.market.isin(["rec", "rec_yds", "rush_yds", "rush_att", "pass_yds", "pass_cmp", "pass_att"])].copy()
E["key"] = E.player.map(norm_name)
# market-level median over-side gap across the whole slate (the model's level bias), used only to center a screen
G = Ea[Ea.is_main_line & (Ea.side == "over") & Ea.market.isin(["rec", "rec_yds", "rush_yds", "rush_att", "pass_yds", "pass_cmp", "pass_att"])]
bias = (G.model_p - G.novig_p).groupby(G.market).median()
st = pd.read_parquet(NFLV + f"stats_player_week_{SEASON}.parquet"); st = st[st.week <= 4]; st["key"] = st.player_display_name.map(norm_name)
COL = {"rec": "receptions", "rec_yds": "receiving_yards", "rush_yds": "rushing_yards", "rush_att": "carries", "pass_yds": "passing_yards", "pass_cmp": "completions", "pass_att": "attempts"}
PLAYED = {"rec": "targets", "rec_yds": "targets", "rush_yds": "carries", "rush_att": "carries", "pass_yds": "attempts", "pass_cmp": "attempts", "pass_att": "attempts"}
R.run_game(AWAY, HOME, neutral=is_neutral(AWAY, HOME), ns=20000); d = R.STORE.pop((AWAY, HOME))
pls = {norm_name(p["player"]): p for t in (AWAY, HOME) for p in d["players"][t]}
rows = []
for (k, mk), g in E.groupby(["key", "market"]):
    ov = g[g.side == "over"]; un = g[g.side == "under"]
    if not len(ov) or k not in pls: continue
    line = float(ov.line.iloc[0]); feeds = int(ov.book.nunique()); mp = float(ov.model_p.iloc[0]); nv = float(ov.novig_p.mean())
    bo = ov.sort_values("odds", ascending=False).iloc[0]; bu = un.sort_values("odds", ascending=False).iloc[0] if len(un) else None
    log = st[(st.key == k) & (st[PLAYED[mk]] > 0)]; n = len(log); hit = int((log[COL[mk]] > line).sum()); avg = float(log[COL[mk]].mean()) if n else np.nan
    rows.append(dict(player=ov.player.iloc[0], team=pls[k]["team"] if "team" in pls[k] else "", market=mk, line=line, feeds=feeds, model=mp, book=nv, gap=mp - nv, gap_c=mp - nv - bias[mk],
                     over=int(bo.odds), over_book=bo.book, under=None if bu is None else int(bu.odds), under_book=None if bu is None else bu.book, games=n, over_games=hit, w14_avg=avg, pa=float(pls[k]["p_active"])))
T = pd.DataFrame(rows)
T["lean"] = np.where(T.gap_c >= 0, "OVER", "UNDER")
def supported(r):
    if r.player in ("Jalon Daniels",) or r.pa < 0.95 or r.feeds < 4 or r.games < 3: return ""
    big = abs(r.gap_c) >= 0.08
    agree = (r.lean == "OVER" and r.over_games / r.games >= 0.5 and r.w14_avg >= r.line) or (r.lean == "UNDER" and r.over_games / r.games <= 0.5 and r.w14_avg <= r.line)
    return "YES" if big and agree else ("weak" if agree and abs(r.gap_c) >= 0.05 else "")
T["support"] = T.apply(supported, axis=1)
pd.set_option("display.width", 250)
print("market level bias (median model-minus-book P(over), slate-wide):", bias.round(3).to_dict())
print(T[T.support != ""].sort_values("gap_c", key=lambda s: -s.abs())[["player", "team", "market", "line", "lean", "model", "book", "gap", "gap_c", "over", "over_book", "under", "under_book", "games", "over_games", "w14_avg", "feeds", "support"]].round(3).to_string(index=False))
print("\nALL TB/DAL non-TD props (for the file):", len(T)); T.to_pickle(OUT + f"props_screen_{AWAY}_{HOME}.pkl")
