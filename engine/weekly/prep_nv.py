"""nflverse-backed replacement for prep.py (same module-level names, so params/sim/run_all work unchanged).
Sources: stats_player_week, snap_counts, games (scores), pbp (red zone), injuries, players (id crosswalk).
As-of: all REG-season games with scores/stat rows present for the season (weeks 1-3 plus the played Thursday game).
"""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, os, re
from load import norm_name, abbr, OUT
N = NFLV
SEASON = int(os.environ.get("APEX_SEASON", 2026))
MAXWEEK = int(os.environ.get("APEX_THROUGH_WEEK", 99))   # backtests can cap the week

NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA", "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU"}
def tm(x): return NV2T.get(x, x)

_pl = pd.read_parquet(N + "players.parquet", columns=["gsis_id", "pfr_id", "display_name", "position"]).drop_duplicates("gsis_id")
G2P = dict(zip(_pl.gsis_id, _pl.pfr_id))

st = pd.read_parquet(N + f"stats_player_week_{SEASON}.parquet"); st = st[(st.season_type == "REG") & (st.week <= MAXWEEK)].copy()
st["team"] = st.team.map(tm); st["opponent_team"] = st.opponent_team.map(tm)
games = pd.read_parquet(N + "games.parquet"); games = games[(games.season == SEASON) & (games.game_type == "REG") & (games.week <= MAXWEEK) & games.home_score.notna()].copy()
games["home_team"] = games.home_team.map(tm); games["away_team"] = games.away_team.map(tm)
sn = pd.read_parquet(N + f"snap_counts_{SEASON}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.week <= MAXWEEK)].copy()
sn["snaps"] = sn.offense_snaps.fillna(0) + sn.defense_snaps.fillna(0) + sn.st_snaps.fillna(0)
sn["team"] = sn.team.map(tm)

# ---------- team game table ----------
rows = []
for _, g in games.iterrows():
    rows.append(dict(team=g.home_team, opp=g.away_team, week=g.week, pf=g.home_score, pa=g.away_score, home=1))
    rows.append(dict(team=g.away_team, opp=g.home_team, week=g.week, pf=g.away_score, pa=g.home_score, home=0))
TG = pd.DataFrame(rows)
GPT = TG.groupby("team").size()           # games played by team

def _by_team_week(df):
    return df.groupby(["team", "week"])

# ---------- player aggregates ----------
st["pfr_id"] = st.player_id.map(G2P).fillna(st.player_id)
st["nkey"] = st.player_display_name.map(norm_name)
sn["pid"] = sn.pfr_player_id
G_played = sn[sn.snaps > 0].groupby("pfr_player_id").size()
last_team = st.sort_values("week").groupby("pfr_id").team.last()

def _base(df):
    out = df.groupby("pfr_id").agg(player=("player_display_name", "last"), team=("team", "last"), Pos=("position", "last"), nrows=("week", "nunique")).reset_index()
    out["G"] = out.pfr_id.map(G_played).fillna(out.nrows).clip(lower=1).astype(float)
    out["Player"] = out.player; out["nkey"] = out.player.map(norm_name); out["Team"] = out.team
    return out

sc_ = st.groupby("pfr_id").agg(Receiving_Tgt=("targets", "sum"), Receiving_Rec=("receptions", "sum"), Receiving_Yds=("receiving_yards", "sum"), Receiving_TD=("receiving_tds", "sum"),
                               Rushing_Att=("carries", "sum"), Rushing_Yds=("rushing_yards", "sum"), Rushing_TD=("rushing_tds", "sum"), Fmb=("fumbles_lost_total", "sum")).reset_index()
_tt = st.groupby(["team", "week"]).agg(tteam=("targets", "sum"), cteam=("carries", "sum")).reset_index()
_st2 = st.merge(_tt, on=["team", "week"], how="left")
_st2["tsh"] = _st2.targets / _st2.tteam.replace(0, np.nan); _st2["csh"] = _st2.carries / _st2.cteam.replace(0, np.nan)
_sh = _st2.groupby("pfr_id").agg(tsh_sum=("tsh", "sum"), csh_sum=("csh", "sum")).reset_index()
sc = _base(st).merge(sc_, on="pfr_id").merge(_sh, on="pfr_id", how="left")
sc["tsh_pg"] = (sc.tsh_sum.fillna(0) / sc.G).fillna(0); sc["csh_pg"] = (sc.csh_sum.fillna(0) / sc.G).fillna(0)
sc = sc[sc.Pos.isin(["QB", "RB", "FB", "WR", "TE", "OL", "P", "NT"])].copy()
sc["GS"] = 0.0

pas_ = st[st.attempts > 0].groupby("pfr_id").agg(Cmp=("completions", "sum"), Att=("attempts", "sum"), Yds=("passing_yards", "sum"), TD=("passing_tds", "sum"), Int=("passing_interceptions", "sum"),
                                                  Sk=("sacks_suffered", "sum"), **{"Yds.1": ("sack_yards_lost", "sum")}).reset_index()
pas = _base(st).merge(pas_, on="pfr_id")
pas["Pos"] = "QB"

# kickers
k_ = st[(st.fg_att > 0) | (st.pat_att > 0)].groupby("pfr_id").agg(FG_FGM=("fg_made", "sum"), FG_FGA=("fg_att", "sum"), PAT_XPM=("pat_made", "sum"), PAT_XPA=("pat_att", "sum")).reset_index()
sco = _base(st).merge(k_, on="pfr_id"); sco["Pos"] = "K"
sco["Pts"] = 3 * sco.FG_FGM + sco.PAT_XPM

# ---------- red zone from pbp ----------
import pyarrow.parquet as pq
_want = ["week", "season_type", "posteam", "defteam", "play_type", "yardline_100", "pass_attempt", "rush_attempt", "receiver_player_id", "rusher_player_id", "complete_pass", "touchdown",
         "td_player_id", "sack", "interception", "fumble_lost", "two_point_attempt", "passer_player_id", "qb_scramble"]
_have = set(pq.read_schema(N + f"play_by_play_{SEASON}.parquet").names)
pb = pd.read_parquet(N + f"play_by_play_{SEASON}.parquet", columns=[c for c in _want if c in _have])
pb = pb[(pb.season_type == "REG") & (pb.week <= MAXWEEK)]
pb["posteam"] = pb.posteam.map(tm); pb["defteam"] = pb.defteam.map(tm)
rec = pb[(pb.pass_attempt == 1) & pb.receiver_player_id.notna() & (pb.two_point_attempt != 1)]
def _rz(df, idcol, cols):
    out = {}
    for name, cond in cols.items(): out[name] = df[cond(df)].groupby(idcol).size()
    return pd.DataFrame(out).fillna(0)
rr = _rz(rec, "receiver_player_id", {"Inside 20_Tgt": lambda d: d.yardline_100 <= 20, "Inside 10_Tgt": lambda d: d.yardline_100 <= 10})
rr["Inside 20_TD"] = rec[(rec.yardline_100 <= 20) & (rec.touchdown == 1) & (rec.td_player_id == rec.receiver_player_id)].groupby("receiver_player_id").size()
rr = rr.fillna(0).reset_index().rename(columns={"receiver_player_id": "gsis"})
ru = pb[(pb.rush_attempt == 1) & pb.rusher_player_id.notna() & (pb.two_point_attempt != 1)]
rz_u = _rz(ru, "rusher_player_id", {"Inside 20_Att": lambda d: d.yardline_100 <= 20, "Inside 10_Att": lambda d: d.yardline_100 <= 10, "Inside 5_Att": lambda d: d.yardline_100 <= 5}).reset_index().rename(columns={"rusher_player_id": "gsis"})
def _attach(rz):
    rz["pfr_id"] = rz.gsis.map(G2P).fillna(rz.gsis)
    info = sc[["pfr_id", "player", "team"]]
    rz = rz.merge(info, on="pfr_id", how="inner"); rz["Player"] = rz.player; rz["Tm"] = rz.team
    return rz
rzr = _attach(rr); rzu = _attach(rz_u); rzp = pd.DataFrame(columns=["Player", "Tm", "team", "pfr_id"])

# ---------- team offense (and defense allowed) ----------
tp = st[st.attempts > 0]
off = pd.DataFrame(index=sorted(GPT.index)); off.index.name = "team"
off["G"] = GPT
agg = st.groupby("team").agg(pass_att=("attempts", "sum"), pass_cmp=("completions", "sum"), pass_yds=("passing_yards", "sum"), pass_td=("passing_tds", "sum"), int=("passing_interceptions", "sum"),
                              sacks_taken=("sacks_suffered", "sum"), sack_yds=("sack_yards_lost", "sum"), rush_att=("carries", "sum"), rush_yds=("rushing_yards", "sum"), rush_td=("rushing_tds", "sum"),
                              tgt_team=("targets", "sum"), fgm=("fg_made", "sum"), fga=("fg_att", "sum"), xpm=("pat_made", "sum"), xpa=("pat_att", "sum"), fl=("fumbles_lost_total", "sum"))
off = off.join(agg)
off["pts"] = TG.groupby("team").pf.sum(); off["pa"] = TG.groupby("team").pa.sum()
off["plays"] = off.pass_att + off.sacks_taken + off.rush_att
off["adot"] = np.nan
# defense: sum of opposing offenses
opp_map = TG[["team", "opp", "week"]]
sw = st.groupby(["team", "week"]).agg(att=("attempts", "sum"), cmp=("completions", "sum"), pyds=("passing_yards", "sum"), ptd=("passing_tds", "sum"), pint=("passing_interceptions", "sum"),
                                      sk=("sacks_suffered", "sum"), sky=("sack_yards_lost", "sum"), ratt=("carries", "sum"), ryds=("rushing_yards", "sum"), rtd=("rushing_tds", "sum"), fl=("fumbles_lost_total", "sum")).reset_index()
dd = opp_map.merge(sw, left_on=["opp", "week"], right_on=["team", "week"], suffixes=("", "_o")).groupby("team").sum(numeric_only=True)
td = pd.DataFrame(index=off.index)
td["G"] = GPT; td["PA"] = off.pa
td["Passing_Att"] = dd.att; td["Passing_Cmp"] = dd.cmp; td["Passing_Yds"] = dd.pyds; td["Passing_TD"] = dd.ptd; td["Passing_Int"] = dd.pint
td["Passing_NY/A"] = (dd.pyds - dd.sky) / (dd.att + dd.sk); td["Rushing_Att"] = dd.ratt; td["Rushing_Yds"] = dd.ryds; td["Rushing_TD"] = dd.rtd
td["Tot Yds & TO_Ply"] = dd.att + dd.sk + dd.ratt; td["FL"] = dd.fl
dsk = st.groupby("team").def_sacks.sum()      # sacks MADE by this defense (actual, not a proxy)
td["sk_actual"] = dsk.reindex(td.index).fillna(0)

# ---------- DvP (DK points per game allowed by position) ----------
def dk(df):
    p = 0.04 * df.passing_yards + 4 * df.passing_tds - 1 * df.passing_interceptions + 3 * (df.passing_yards >= 300)
    r = 0.1 * df.rushing_yards + 6 * df.rushing_tds + 3 * (df.rushing_yards >= 100)
    c = df.receptions + 0.1 * df.receiving_yards + 6 * df.receiving_tds + 3 * (df.receiving_yards >= 100)
    return p + r + c - df.fumbles_lost_total + 2 * (df.passing_2pt_conversions + df.rushing_2pt_conversions + df.receiving_2pt_conversions)
st["dk"] = dk(st)
def _dvp(pos):
    x = st[st.position.isin(pos)].groupby("opponent_team").dk.sum() / GPT
    d = pd.DataFrame({"Fantasy per Game_DKPt": x}); d.index.name = "team"; return d.reindex(off.index)
dvq, dvr, dvw, dvt = _dvp(["QB"]), _dvp(["RB", "FB"]), _dvp(["WR"]), _dvp(["TE"])
rec_t = pd.DataFrame({"Tgt": off.tgt_team}); rsh_t = pd.DataFrame({"Att": off.rush_att, "Yds": off.rush_yds, "TD": off.rush_td})
prs = pd.DataFrame({"Passing_Sk": off.sacks_taken}); air = acc = pty = pd.DataFrame(index=off.index)

if __name__ == "__main__":
    print("games", len(games), "team-games", len(TG), "players", len(sc), len(pas), len(sco)); print("G by team", GPT.value_counts().to_dict())
    # reconcile vs the sportsref tables for weeks 1-3 (set APEX_THROUGH_WEEK=3 to compare like for like)
    print(off[["G", "pass_att", "pass_yds", "rush_att", "rush_yds", "pts", "pa"]].head(6)); print(td.head(3).T)
