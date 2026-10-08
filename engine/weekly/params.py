"""Week 4 team environment + player role parameters (Weeks 1-3 data, shrunk).

Doctrine inherited from apexos-fantasy-gm projection contract v1.0 / TouchdownOS:
  team environment first -> volume -> efficiency -> TD; volume / scheme / efficiency kept as separate fields;
  raw model values preserved; no manual override applied (override fields carried as null).
"""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd
from prep_nv import *
from load import parse_injury
import json, os

VERSION = "w4-props-v4-nflverse"
AS_OF = "2026-10-03"

def shr(obs, n, prior, k):
    return (obs * n + prior * k) / (n + k)

import os
_G = pd.read_parquet(N + "games.parquet"); _G = _G[(_G.season == SEASON) & (_G.game_type == "REG")].copy()
for _c in ("home_team", "away_team"): _G[_c] = _G[_c].map(tm)
BACKTEST = os.environ.get("APEX_BACKTEST", "0") == "1"
TARGET_WEEK = int(os.environ.get("APEX_TARGET_WEEK", 0)) or int(_G[_G.home_score.isna()].week.min())
# nflverse can label international games location="Home" (2026 W5 PHI@JAX at Tottenham); treat these venues as neutral
INTL_STADIUMS = ["Tottenham Hotspur Stadium", "Wembley Stadium", "Allianz Arena", "Deutsche Bank Park", "Estadio Azteca", "Santiago Bernabeu", "Maracana Stadium", "Croke Park", "Melbourne Cricket Ground"]
_tg = _G[_G.week == TARGET_WEEK].sort_values(["gameday", "gametime"])
SCHED = pd.DataFrame(dict(away=_tg.away_team.values, home=_tg.home_team.values, date=_tg.gameday.values, time_edt=_tg.gametime.values, neutral=((_tg.location.values == "Neutral") | (np.isin(_tg.stadium.values, INTL_STADIUMS) & (not BACKTEST))),
                          spread_line=_tg.spread_line.values, total_line=_tg.total_line.values)).reset_index(drop=True)
PLAYED = set() if BACKTEST else {(r.away_team, r.home_team) for r in _tg.itertuples() if not np.isnan(r.home_score)}
def is_neutral(a, h):
    x = SCHED[(SCHED.away == a) & (SCHED.home == h)]; return bool(x.neutral.iloc[0]) if len(x) else False
MARKET = {(r.away, r.home): (r.spread_line, r.total_line) for r in SCHED.itertuples()}     # nflverse schedule lines (spread_line > 0 = home favored)
_pgmap = {"QB":"QB","RB":"RB","FB":"RB","WR":"WRTE","TE":"WRTE","T":"OL","G":"OL","C":"OL","OL":"OL","DE":"DL","DT":"DL","NT":"DL","DL":"DL","LB":"LB","OLB":"LB","ILB":"LB","MLB":"LB","CB":"DB","S":"DB","FS":"DB","SS":"DB","DB":"DB","K":"KP","P":"KP","LS":"KP"}
_AV_LEAF = pd.read_csv(CONF+"availability_by_status_pos.csv", keep_default_na=False); _AV_ROOT = pd.read_csv(CONF+"availability_by_status.csv", keep_default_na=False)
def p_active(rs, ps, pg):
    """Empirical P(plays) fit on nflverse 2023-2026 injury history x snap counts (fit_availability.py)."""
    if rs == "Out": return 0.0
    x = _AV_LEAF[(_AV_LEAF.rs == rs) & (_AV_LEAF.ps == ps) & (_AV_LEAF.pg == pg)]
    if len(x): return float(x.p.iloc[0])
    x = _AV_ROOT[(_AV_ROOT.rs == rs) & (_AV_ROOT.ps == ps)]
    return float(x.p_parent.iloc[0]) if len(x) else 0.9
def build_inj():
    i = pd.read_parquet(N + f"injuries_{SEASON}.parquet"); i = i[(i.game_type == "REG")]
    i = i[i.week == (int(os.environ["APEX_INJ_WEEK"]) if "APEX_INJ_WEEK" in os.environ else i.week.max())].copy(); i["team"] = i.team.map(tm)
    i["rs"] = i.report_status.fillna("None"); i["ps"] = i.practice_status.fillna("None").map({"Did Not Participate In Practice":"DNP","Limited Participation in Practice":"LP","Full Participation in Practice":"FP"}).fillna("None")
    i["pg"] = i.position.map(_pgmap).fillna("OTH")
    o = pd.DataFrame(dict(player=i.full_name, pos=i.position, team=i.team, injury=i.report_primary_injury.fillna(i.practice_primary_injury), practice=i.ps, game_status=i.report_status, nkey=i.full_name.map(norm_name)))
    o["p_active"] = [p_active(a, b, c) for a, b, c in zip(i.rs, i.ps, i.pg)]
    o["injury_week"] = int(i.week.max())
    return _apply_manual_out(_apply_roster_out(o, int(i.week.max()))).reset_index(drop=True)
def _apply_manual_out(o):
    """Operator-supplied confirmed inactives (APEX_MANUAL_OUT=<csv: player,team,source,as_of_utc,note>). The file is frozen with the run, so every override is visible and auditable."""
    path = os.environ.get("APEX_MANUAL_OUT")
    if not path or not os.path.exists(path):
        return o
    m = pd.read_csv(path, keep_default_na=False); m["nkey"] = m.player.map(norm_name); m["team"] = m.team.map(lambda t: tm.get(t, t)) if hasattr(tm, "get") else m.team
    key = set(zip(m.nkey, m.team)); why = {(a, b): c for a, b, c in zip(m.nkey, m.team, m.source)}
    hit = pd.Series([(a, b) in key for a, b in zip(o.nkey, o.team)], index=o.index)
    o.loc[hit, "p_active"] = 0.0; o.loc[hit, "game_status"] = "Out"
    o.loc[hit, "injury"] = ["Manual override (" + why[(a, b)] + ")" for a, b in zip(o.nkey[hit], o.team[hit])]
    seen = set(zip(o.nkey, o.team)); add = m[[(a, b) not in seen for a, b in zip(m.nkey, m.team)]]
    if len(add):
        o = pd.concat([o, pd.DataFrame(dict(player=add.player.values, pos=add.get("pos", pd.Series("", index=add.index)).values, team=add.team.values,
                                            injury=("Manual override (" + add.source + ")").values, practice="None", game_status="Out", nkey=add.nkey.values, p_active=0.0,
                                            injury_week=int(o.injury_week.max()) if len(o) else 0))], ignore_index=True)
    return o
_ROSTER_OUT = {"RES": "Reserve (IR/PUP/NFI)", "CUT": "Released", "RET": "Retired", "EXE": "Exempt list"}
def _apply_roster_out(o, week):
    """Players whose nflverse roster status is RES/CUT/RET/EXE cannot play, whatever the injury report says
    (Week 4 2026: British Brooks went on IR the morning of the games while the report still listed him; Odell Beckham Jr. was released).
    Only used when the roster snapshot for that week is a full roster (current season); historical roster files are sparse, so backtests are unchanged."""
    try:
        r = pd.read_parquet(N + f"roster_{SEASON}.parquet"); r = r[(r.game_type == "REG") & (r.week == week)]
    except Exception:
        return o
    if len(r) < 1000:
        return o
    r = r[r.position.isin(["QB", "RB", "FB", "WR", "TE"])].copy()
    r["nkey"] = r.full_name.map(norm_name); r["team"] = r.team.map(tm)
    live = set(zip(r[r.status.isin(["ACT", "DEV", "INA"])].nkey, r[r.status.isin(["ACT", "DEV", "INA"])].team))     # same player re-signed by the same team stays live
    r = r[r.status.isin(_ROSTER_OUT) & ~pd.Series([(a, b) in live for a, b in zip(r.nkey, r.team)], index=r.index)]
    why = dict(zip(zip(r.nkey, r.team), r.status.map(_ROSTER_OUT)))
    hit = pd.Series([(a, b) in why for a, b in zip(o.nkey, o.team)], index=o.index)
    o.loc[hit, "p_active"] = 0.0
    o.loc[hit, "game_status"] = "Out"
    o.loc[hit, "injury"] = [why[(a, b)] for a, b in zip(o.nkey[hit], o.team[hit])]
    seen = set(zip(o.nkey, o.team)); add = r[[(a, b) not in seen for a, b in zip(r.nkey, r.team)]]
    if len(add):
        o = pd.concat([o, pd.DataFrame(dict(player=add.full_name.values, pos=add.position.values, team=add.team.values, injury=add.status.map(_ROSTER_OUT).values,
                                            practice="None", game_status="Out", nkey=add.nkey.values, p_active=0.0, injury_week=week))], ignore_index=True)
    return o
def _qb_fix(o):
    dq = _DC_QB[_DC_QB.pos_rank == 1][["team", "nkey"]].drop_duplicates()
    ks = set(zip(dq.team, dq.nkey))
    m = (o.pos == "QB") & o.game_status.isna() & pd.Series([(a, b) in ks for a, b in zip(o.team, o.nkey)], index=o.index)
    o.loc[m, "p_active"] = 0.98
    return o
try:      # current-season depth charts carry a snapshot timestamp (dt); older seasons use a different schema, so backtests fall back to attempts
    _DC = pd.read_parquet(N + f"depth_charts_{SEASON}.parquet"); _DC = _DC[_DC.dt == _DC.dt.max()]
    _DC_QB = _DC[_DC.pos_abb == "QB"].copy(); _DC_QB["team"] = _DC_QB.team.map(tm); _DC_QB["nkey"] = _DC_QB.player_name.map(norm_name)
except Exception:
    _DC_QB = pd.DataFrame(columns=["team", "nkey", "pos_rank"])
INJ = _qb_fix(build_inj()); INJ["p_miss"] = 1 - INJ.p_active

# ---------------- league constants ----------------
NT = 32
L = {}
L["ppg"] = off.pts.sum() / off.G.sum()
L["plays"] = off.plays.sum() / off.G.sum()
L["pr"] = (off.pass_att.sum() + off.sacks_taken.sum()) / off.plays.sum()
L["sk"] = off.sacks_taken.sum() / (off.pass_att.sum() + off.sacks_taken.sum())
L["ypa"] = off.pass_yds.sum() / off.pass_att.sum()
L["cmp"] = off.pass_cmp.sum() / off.pass_att.sum()
L["int"] = off.int.sum() / off.pass_att.sum()
L["ypc"] = off.rush_yds.sum() / off.rush_att.sum()
L["ptd_share"] = off.pass_td.sum() / (off.pass_td.sum() + off.rush_td.sum())
L["fg"] = off.fgm.sum() / off.G.sum()
L["fl"] = td.FL.sum() / td.G.sum()
L["dtd"] = 0.12; L["saf"] = 0.03; L["xp"] = off.xpm.sum() / max(off.xpa.sum(), 1)
L["ypa_def"] = td["Passing_Yds"].sum() / td["Passing_Att"].sum()
L["ypc_def"] = td["Rushing_Yds"].sum() / td["Rushing_Att"].sum()
L["int_def"] = td["Passing_Int"].sum() / td["Passing_Att"].sum()
L["ptd_def"] = td["Passing_TD"].sum() / (td["Passing_TD"].sum() + td["Rushing_TD"].sum())
L["cmp_def"] = td["Passing_Cmp"].sum() / td["Passing_Att"].sum()
# defensive sack proxy: Sk = (Yds - NY/A*Att)/(NY/A + 7)  (PFR team defense table has no sack column)
td["sk_proxy"] = td["sk_actual"]    # actual team sacks from nflverse (v3 backed this out from net yards)
L["sk_def"] = td.sk_proxy.sum() / (td.sk_proxy.sum() + td["Passing_Att"].sum())

# ---------------- prior-season team strength (public nflverse 2025 REG final scores; no 2026 line fields used) ----------------
_gp = pd.read_parquet(N + "games.parquet"); _gp = _gp[(_gp.season == SEASON - 1) & (_gp.game_type == "REG") & _gp.home_score.notna()].copy()
for _c in ("home_team", "away_team"): _gp[_c] = _gp[_c].map(tm)
_rows = [(r.home_team, r.home_score, r.away_score) for r in _gp.itertuples()] + [(r.away_team, r.away_score, r.home_score) for r in _gp.itertuples()]
_pr = pd.DataFrame(_rows, columns=["team", "pf", "pa"]).groupby("team").mean()       # prior-season PF/PA per game
TPF = json.load(open(CONF+"team_prior_fit.json"))
RET_OFF, RET_DEF = TPF["ret_off"], TPF["ret_def"]
def prior_pts(t):
    if t not in _pr.index: return L["ppg"], L["ppg"]
    return (L["ppg"] + RET_OFF * (_pr.loc[t, "pf"] - _pr.pf.mean()), L["ppg"] + RET_DEF * (_pr.loc[t, "pa"] - _pr.pa.mean()))
def ridge_ratings():
    """opponent-adjusted ridge ratings (fitted in fit_team_priors.py): o_i + d_j + mu +/- hfa; prior = retained prior-season deviation"""
    ts = sorted(off.index); ix = {t: i for i, t in enumerate(ts)}; T_ = len(ts); mu = L["ppg"]; hfa = TPF["hfa"]
    A = np.zeros((len(TG), 2 * T_)); y = np.zeros(len(TG))
    for k, r in enumerate(TG.itertuples()):
        A[k, ix[r.team]] = 1; A[k, T_ + ix[r.opp]] = 1; y[k] = r.pf - mu - (hfa if r.home else -hfa)
    mu0 = _pr.pf.mean(); o0 = np.array([RET_OFF * (_pr.pf.get(t, mu0) - mu0) for t in ts]); d0 = np.array([RET_DEF * (_pr.pa.get(t, mu0) - mu0) for t in ts])
    lam = np.r_[np.full(T_, TPF["lo"]), np.full(T_, TPF["ld"])]; x0 = np.r_[o0, d0]
    x = np.linalg.solve(A.T @ A + np.diag(lam), A.T @ y + lam * x0)
    return {t: (mu + x[ix[t]], mu + x[T_ + ix[t]]) for t in ts}
RIDGE = ridge_ratings()

# ---------------- team parameters ----------------
TEAM = {}
def team_params():
    out = {}
    for t in td.index:
        o, d = off.loc[t], td.loc[t]
        db = o.pass_att + o.sacks_taken
        p = {}
        GP = float(o.G)
        p["pf"] = o.pts / GP; p["pa"] = o.pa / GP
        po, pd_ = prior_pts(t)
        p["prior_off"], p["prior_def"] = po, pd_
        p["off_ppg"], p["def_ppg"] = RIDGE[t]
        p["plays_off"] = shr(o.plays / GP, GP, L["plays"], 4.0)
        p["plays_def"] = shr(d["Tot Yds & TO_Ply"] / GP, GP, L["plays"], 4.0)
        p["pr"] = shr(db / o.plays, o.plays, L["pr"], 90)
        p["sk"] = shr(o.sacks_taken / db, db, L["sk"], 70)
        p["ypa"] = shr(o.pass_yds / o.pass_att, o.pass_att, L["ypa"], 110)
        p["cmp"] = shr(o.pass_cmp / o.pass_att, o.pass_att, L["cmp"], 110)
        p["int"] = shr(o.int / o.pass_att, o.pass_att, L["int"], 220)
        p["ypc"] = shr(o.rush_yds / o.rush_att, o.rush_att, L["ypc"], 90)
        p["ptd"] = shr(o.pass_td / max(o.pass_td + o.rush_td, 1), o.pass_td + o.rush_td, L["ptd_share"], 14)
        p["fg"] = shr(o.fgm / GP, GP, L["fg"], 4.0)
        # defense indices (>1 = allows more)
        da = d["Passing_Att"]; dr = d["Rushing_Att"]
        p["d_ypa"] = shr(d["Passing_Yds"] / da, da, L["ypa_def"], 110) / L["ypa_def"]
        p["d_cmp"] = shr(d["Passing_Cmp"] / da, da, L["cmp_def"], 110) / L["cmp_def"]
        p["d_int"] = shr(d["Passing_Int"] / da, da, L["int_def"], 200) / L["int_def"]
        p["d_ypc"] = shr(d["Rushing_Yds"] / dr, dr, L["ypc_def"], 90) / L["ypc_def"]
        p["d_ptd"] = shr(d["Passing_TD"] / max(d["Passing_TD"] + d["Rushing_TD"], 1), d["Passing_TD"] + d["Rushing_TD"], L["ptd_def"], 14) / L["ptd_def"]
        p["d_sk"] = shr(d.sk_proxy / (d.sk_proxy + da), da, L["sk_def"], 70) / L["sk_def"]
        p["d_fl"] = shr(d["FL"] / GP, GP, L["fl"], 6.0) / L["fl"]
        # DvP tilt (DK pts per game vs position, shrunk to league)
        for pos, df in (("QB", dvq), ("RB", dvr), ("WR", dvw), ("TE", dvt)):
            col = "Fantasy per Game_DKPt"
            lg = df[col].mean()
            p["dvp_" + pos] = 1 + 0.35 * (df.loc[t, col] / lg - 1)
        out[t] = p
    return out
TEAM = team_params()

# ---------------- injuries -> team multipliers ----------------
OL = {"T", "G", "C", "OL"}; PR = {"DE", "DT", "DL", "NT", "EDGE", "OLB"}; CBs = {"CB", "S", "FS", "SS", "DB"}; LBs = {"LB", "ILB"}
def inj_groups(team):
    d = INJ[INJ.team == team]
    f = lambda s: float((d[d.pos.isin(s)].p_miss).sum() * 0.7)  # 0.7 = starter probability unknown
    return dict(ol=f(OL), pr=f(PR), cb=f({"CB"}), s=f({"S", "FS", "SS", "DB"}), lb=f(LBs))

# ---------------- roster build (v4: fitted shrinkage + last-season priors; see fit_player_priors.py) ----------------
import json
PP = json.load(open(CONF+"player_prior_fit.json"))
_CAL = json.load(open(CONF+"calibration_params.json")); OTHER_TGT = _CAL["other_tgt"]; OTHER_CAR = _CAL["other_car"]

def _last_season_table(season):
    """per-player prior-season aggregates (gsis -> pfr_id), >= 6 games, same definitions as the backtest"""
    y = season - 1
    st_ = pd.read_parquet(N + f"stats_player_week_{y}.parquet"); st_ = st_[st_.season_type == "REG"].copy(); st_["team"] = st_.team.map(tm)
    sn_ = pd.read_parquet(N + f"snap_counts_{y}.parquet"); sn_ = sn_[(sn_.game_type == "REG") & (sn_.offense_snaps > 0)].copy(); sn_["gsis"] = sn_.pfr_player_id.map({v: k for k, v in G2P.items() if isinstance(v, str)})
    sn_ = sn_[sn_.gsis.notna()]; sn_["team"] = sn_.team.map(tm)
    cols = ["targets", "receptions", "receiving_yards", "receiving_tds", "carries", "rushing_yards", "rushing_tds"]
    m = sn_[["week", "gsis", "team", "pfr_player_id"]].merge(st_[["week", "player_id"] + cols].rename(columns={"player_id": "gsis"}), on=["week", "gsis"], how="left"); m[cols] = m[cols].fillna(0)
    tt = st_.groupby(["team", "week"]).agg(tteam=("targets", "sum"), cteam=("carries", "sum")).reset_index(); m = m.merge(tt, on=["team", "week"], how="left")
    m["tsh"] = (m.targets / m.tteam.replace(0, np.nan)).fillna(0); m["csh"] = (m.carries / m.cteam.replace(0, np.nan)).fillna(0)
    g_ = m.groupby("pfr_player_id").agg(team=("team", "last"), n=("week", "size"), tsh=("tsh", "mean"), csh=("csh", "mean"), tgt=("targets", "sum"), rec=("receptions", "sum"), ryds=("receiving_yards", "sum"),
                                         rtd=("receiving_tds", "sum"), car=("carries", "sum"), cyds=("rushing_yards", "sum"), ctd=("rushing_tds", "sum"))
    return g_[g_.n >= 6]
LAST = _last_season_table(SEASON)

def _fk(stat, pos):
    f = PP[stat].get(pos) or PP[stat].get("RB") or PP[stat].get("WR"); return f["k"], f["a"], f.get("a_changed", f["a"] * 0.5)

def build_roster_v4(team):
    d = sc[(sc.team == team) & (sc.Pos.isin(["QB", "RB", "WR", "TE", "FB"]))].copy()
    d["pos"] = d.Pos.replace({"FB": "RB"})
    T = rec_t.loc[team, "Tgt"]; R = off.loc[team, "rush_att"]
    P = TEAM[team]
    d = d.merge(INJ[INJ.team == team][["nkey", "p_active", "game_status", "practice", "injury"]],
                left_on=d.player.map(norm_name), right_on="nkey", how="left").drop(columns=["key_0"], errors="ignore")
    d["p_active"] = d.p_active.fillna(1.0)
    # redzone (play-by-play)
    rr = rzr[rzr.team == team].set_index("pfr_id"); ru = rzu[rzu.team == team].set_index("pfr_id")
    d["rz_tgt"] = d.pfr_id.map(rr["Inside 20_Tgt"]).fillna(0); d["rz_rec_td"] = d.pfr_id.map(rr["Inside 20_TD"]).fillna(0)
    d["rz10_tgt"] = d.pfr_id.map(rr["Inside 10_Tgt"]).fillna(0)
    d["rz_car"] = d.pfr_id.map(ru["Inside 20_Att"]).fillna(0); d["rz10_car"] = d.pfr_id.map(ru["Inside 10_Att"]).fillna(0)
    d["rz5_car"] = d.pfr_id.map(ru["Inside 5_Att"]).fillna(0)
    # last-season priors
    for c in ("tsh", "csh", "tgt", "rec", "ryds", "rtd", "car", "cyds", "ctd", "n"): d["l_" + c] = d.pfr_id.map(LAST[c]) if c in LAST else np.nan
    d["l_team"] = d.pfr_id.map(LAST["team"]); d["same_team"] = np.where(d.l_team.isna(), np.nan, (d.l_team == team).astype(float))
    # rank among the team's skill players by observed per-game share (as in the backtest)
    d["trk"] = d.tsh_pg.rank(ascending=False, method="first"); d["crk"] = d.csh_pg.rank(ascending=False, method="first")
    def shr_share(kind):
        obs = d["tsh_pg" if kind == "tgt" else "csh_pg"].values; last = d["l_tsh" if kind == "tgt" else "l_csh"].values; rk = d["trk" if kind == "tgt" else "crk"].clip(upper=6).values
        out = np.zeros(len(d))
        for i, r in enumerate(d.itertuples()):
            stat = "tgt_share" if kind == "tgt" else "car_share"
            if (kind == "tgt" and r.pos == "QB") or (kind == "car" and r.pos in ("WR", "TE")):
                role = 0.002 if kind == "tgt" else 0.01; k, a, ach = 3.0, 0.0, 0.0
            else:
                k, a, ach = _fk(stat, r.pos); role = PP["roles"][kind][r.pos if r.pos in PP["roles"][kind] else "RB"].get(str(float(min(rk[i], 6))), 0.01); rawrk = float(d["trk" if kind == "tgt" else "crk"].iloc[i]); role = role * (6.0 / rawrk) ** 2 if rawrk > 6 else role
            aa = 0.0 if np.isnan(last[i]) else (a if (np.isnan(r.same_team) or r.same_team == 1) else ach)
            prior = aa * (0.0 if np.isnan(last[i]) else last[i]) + (1 - aa) * role
            n = float(r.G); out[i] = (n * obs[i] + k * prior) / (n + k)
        return out
    d["tgt_sh"] = shr_share("tgt"); d["car_sh"] = shr_share("car")
    for _k, _m in ({} if os.environ.get("APEX_NOMULT") else _CAL.get("share_mult", {})).items():      # position-level share calibration from 2023-25 weeks 4-12 backtests
        _kind, _pos = _k.split("_"); _col = "tgt_sh" if _kind == "tgt" else "car_sh"; d.loc[d.pos == _pos, _col] = d.loc[d.pos == _pos, _col] * _m
    d.attrs["tsum_raw"] = float(d.tgt_sh.sum()); d.attrs["csum_raw"] = float(d.car_sh.sum())
    oth = max(T - d.Receiving_Tgt.sum(), 0); other_sh = (oth + 18 * OTHER_TGT) / (T + 18)
    oth_c = max(R - d.Rushing_Att.sum(), 0); other_car = (oth_c + 12 * OTHER_CAR) / (R + 12)
    def _norm(sh, budget, keep):
        """star-preserving normalization: the top `keep` shares stay as fitted; the tail absorbs the compression"""
        sh = sh.copy(); tot = sh.sum()
        if tot <= 0 or keep <= 0: return sh * budget / tot if tot > 0 else sh
        order = sh.sort_values(ascending=False).index; top = order[:keep]; rest = order[keep:]
        st = sh[top].sum()
        if st >= budget * 0.97 or sh[rest].sum() <= 0: return sh * budget / tot
        s = (budget - st) / sh[rest].sum(); sh[rest] = sh[rest] * s; return sh
    KT = int(os.environ.get("APEX_KT", _CAL.get("keep_tgt", 0))); KC = int(os.environ.get("APEX_KC", _CAL.get("keep_car", 0)))
    d["car_sh"] = _norm(d.car_sh, 1 - other_car, KC) if d.car_sh.sum() > 0 else d.car_sh
    d["tgt_sh"] = _norm(d.tgt_sh, 1 - other_sh, KT)
    # DvP tilt on target shares
    tilt = d.pos.map(lambda p: P.get("dvp_" + p, 1.0) if p in ("WR", "TE", "RB") else 1.0) ** 0.5
    # efficiency: pooled-ratio shrinkage with fitted k and last-season weight a
    def eff(stat, num, den, lnum, lden, mincnt=20):
        out = np.zeros(len(d))
        for i, r in enumerate(d.itertuples()):
            pos = r.pos if r.pos in PP["posmean"][stat] else "RB"
            k, a = PP[stat].get(pos, PP[stat].get("RB"))["k"], PP[stat].get(pos, PP[stat].get("RB"))["a"]
            if stat == "ypc" and "APEX_YPC_K" in os.environ: k = float(os.environ["APEX_YPC_K"])
            if stat == "catch" and "APEX_CATCH_K" in os.environ: k = float(os.environ["APEX_CATCH_K"])
            pm = PP["posmean"][stat][pos]; ld = getattr(r, lden); ln = getattr(r, lnum)
            aa = a if (not np.isnan(ld) and ld >= mincnt) else 0.0
            if aa > 0 and not (np.isnan(r.same_team) or r.same_team == 1): aa *= 0.5
            prior = aa * (ln / ld if aa > 0 else 0.0) + (1 - aa) * pm
            out[i] = (getattr(r, num) + k * prior) / (getattr(r, den) + k)
        return out
    d["catch"] = np.clip(eff("catch", "Receiving_Rec", "Receiving_Tgt", "l_rec", "l_tgt"), 0.3, 0.92)
    d["ypr"] = eff("ypr", "Receiving_Yds", "Receiving_Rec", "l_ryds", "l_rec")
    d["ypc"] = np.where(d.pos.isin(["RB", "QB"]), eff("ypc", "Rushing_Yds", "Rushing_Att", "l_cyds", "l_car"), PP["posmean"]["ypc"].get("RB", 4.2) * 1.0)
    # TD weights (volume from red zone shares, shrunk to overall share)
    rzT = max(d.rz_tgt.sum(), 0); rzC = max(d.rz_car.sum(), 0); rz10C = max(d.rz10_car.sum(), 0)
    mr = 8.0
    rz_t_sh = (d.rz_tgt + mr * d.tgt_sh) / (rzT + mr)
    rz_c_sh = (d.rz_car + mr * d.car_sh) / (rzC + mr)
    rz10_c_sh = (d.rz10_car + 8 * d.car_sh) / (rz10C + 8)
    d["w_rec_td"] = (0.40 * rz_t_sh + 0.60 * d.tgt_sh) * tilt
    d["w_rush_td"] = 0.40 * rz10_c_sh + 0.60 * d.car_sh
    d["other_tgt_sh"] = other_sh; d["other_car_sh"] = other_car
    d["tilt"] = tilt
    return d.reset_index(drop=True), other_sh, other_car

PRI_TGT = {"WR": [.22, .17, .12, .07, .04, .02], "TE": [.15, .045, .015], "RB": [.10, .05, .02]}
PRI_CAR = {"RB": [.55, .22, .08, .03], "QB": [.10], "WR": [.01], "TE": [0.0]}
_CAL = json.load(open(CONF+"calibration_params.json")); OTHER_TGT = _CAL["other_tgt"]; OTHER_CAR = _CAL["other_car"]

# position priors (league)
def _ratio(num, den): return float(num.sum() / max(den.sum(), 1))
_s = sc.copy()
CATCH = {p: _ratio(_s[_s.Pos == p]["Receiving_Rec"], _s[_s.Pos == p]["Receiving_Tgt"]) for p in ("WR", "TE", "RB")}
YPR = {p: _ratio(_s[_s.Pos == p]["Receiving_Yds"], _s[_s.Pos == p]["Receiving_Rec"]) for p in ("WR", "TE", "RB")}
CATCH["FB"] = CATCH["RB"]; YPR["FB"] = YPR["RB"]
YPC_POS = {p: _ratio(_s[_s.Pos == p]["Rushing_Yds"], _s[_s.Pos == p]["Rushing_Att"]) for p in ("RB", "QB", "WR", "TE")}

def build_roster_v3(team):
    d = sc[(sc.team == team) & (sc.Pos.isin(["QB", "RB", "WR", "TE", "FB"]))].copy()
    d["pos"] = d.Pos.replace({"FB": "RB"})
    T = rec_t.loc[team, "Tgt"]; R = off.loc[team, "rush_att"]
    P = TEAM[team]
    d = d.merge(INJ[INJ.team == team][["nkey", "p_active", "game_status", "practice", "injury"]],
                left_on=d.player.map(norm_name), right_on="nkey", how="left").drop(columns=["key_0"], errors="ignore")
    d["p_active"] = d.p_active.fillna(1.0)
    # redzone
    rr = rzr[rzr.team == team].set_index("pfr_id"); ru = rzu[rzu.team == team].set_index("pfr_id")
    d["rz_tgt"] = d.pfr_id.map(rr["Inside 20_Tgt"]).fillna(0); d["rz_rec_td"] = d.pfr_id.map(rr["Inside 20_TD"]).fillna(0)
    d["rz10_tgt"] = d.pfr_id.map(rr["Inside 10_Tgt"]).fillna(0)
    d["rz_car"] = d.pfr_id.map(ru["Inside 20_Att"]).fillna(0); d["rz10_car"] = d.pfr_id.map(ru["Inside 10_Att"]).fillna(0)
    d["rz5_car"] = d.pfr_id.map(ru["Inside 5_Att"]).fillna(0)
    # rank within position by observed volume to assign role priors
    for pos in ("WR", "TE", "RB"):
        m = d.pos == pos
        d.loc[m, "tgt_rank"] = d.loc[m, "Receiving_Tgt"].rank(ascending=False, method="first")
        d.loc[m, "car_rank"] = d.loc[m, "Rushing_Att"].rank(ascending=False, method="first")
    def pri_t(r):
        lst = PRI_TGT.get(r.pos, [0.01]); i = int(r.tgt_rank) - 1 if r.pos in PRI_TGT and not np.isnan(r.tgt_rank) else 99
        return lst[i] if i < len(lst) else 0.01
    def pri_c(r):
        lst = PRI_CAR.get(r.pos, [0.0]); i = int(r.car_rank) - 1 if r.pos == "RB" and not np.isnan(r.car_rank) else (0 if r.pos in ("QB", "WR", "TE") else 99)
        return lst[i] if i < len(lst) else 0.0
    d["pri_t"] = d.apply(pri_t, axis=1); d["pri_c"] = d.apply(pri_c, axis=1)
    mT = 18.0
    gsc = (d.G.clip(lower=1, upper=3) / 3.0)          # games-played scale: share is measured vs team volume in the games he played
    d["tgt_sh"] = (d.Receiving_Tgt + mT * gsc * d.pri_t) / (T * gsc + mT * gsc)
    oth = max(T - d.Receiving_Tgt.sum(), 0)
    other_sh = (oth + mT * OTHER_TGT) / (T + mT)
    mC = np.where(d.pos == "QB", 6.0, 12.0)
    d["car_sh"] = (d.Rushing_Att + mC * gsc * d.pri_c) / (R * gsc + mC * gsc)
    oth_c = max(R - d.Rushing_Att.sum(), 0); other_car = (oth_c + 12 * OTHER_CAR) / (R + 12)
    d["car_sh"] = d.car_sh * (1 - other_car) / d.car_sh.sum() if d.car_sh.sum() > 0 else d.car_sh
    d["tgt_sh"] = d.tgt_sh * (1 - other_sh) / d.tgt_sh.sum()
    # DvP tilt on target shares
    tilt = d.pos.map(lambda p: P.get("dvp_" + p, 1.0) if p in ("WR", "TE", "RB") else 1.0) ** 0.5
    # efficiency
    d["catch"] = shr(d.Receiving_Rec / d.Receiving_Tgt.replace(0, np.nan), d.Receiving_Tgt, d.pos.map(CATCH), 22).fillna(d.pos.map(CATCH))
    d["catch"] = np.where(d.Receiving_Tgt > 0, (d.Receiving_Rec + 22 * d.pos.map(CATCH)) / (d.Receiving_Tgt + 22), d.pos.map(CATCH))
    d["ypr"] = np.where(d.Receiving_Rec > 0, (d.Receiving_Yds + 14 * d.pos.map(YPR)) / (d.Receiving_Rec + 14), d.pos.map(YPR))
    team_ypc = off.loc[team, "rush_yds"] / off.loc[team, "rush_att"]
    d["ypc"] = np.where(d.Rushing_Att > 0, (d.Rushing_Yds + 45 * d.pos.map(YPC_POS)) / (d.Rushing_Att + 45), d.pos.map(YPC_POS))
    # TD weights (volume from red zone shares, shrunk to overall share)
    rzT = max(d.rz_tgt.sum(), 0); rzC = max(d.rz_car.sum(), 0); rz10C = max(d.rz10_car.sum(), 0)
    mr = 8.0
    rz_t_sh = (d.rz_tgt + mr * d.tgt_sh) / (rzT + mr)
    rz_c_sh = (d.rz_car + mr * d.car_sh) / (rzC + mr)
    rz10_c_sh = (d.rz10_car + 8 * d.car_sh) / (rz10C + 8)
    d["w_rec_td"] = (0.40 * rz_t_sh + 0.60 * d.tgt_sh) * tilt
    d["w_rush_td"] = 0.40 * rz10_c_sh + 0.60 * d.car_sh
    d["other_tgt_sh"] = other_sh; d["other_car_sh"] = other_car
    d["tilt"] = tilt
    return d.reset_index(drop=True), other_sh, other_car


ROSTER_MODE = os.environ.get("APEX_ROSTER", "v4")
build_roster = build_roster_v3 if ROSTER_MODE == "v3" else build_roster_v4

def qb_list(team):
    """QBs for a team ordered by the CURRENT depth chart (nflverse), then attempts. Starter is no longer inferred from Weeks 1-3 attempts."""
    q = pas[(pas.team == team)].copy()
    dq = _DC_QB[_DC_QB.team == team].set_index("nkey").pos_rank
    q["depth"] = q.nkey.map(dq).fillna(99)
    q1 = q[q.depth == q.depth.min()] if (q.depth < 99).any() else q.sort_values("Att", ascending=False).head(1)
    q = pd.concat([q1.head(1), q.drop(q1.head(1).index).sort_values(["depth", "Att"], ascending=[True, False])])      # QB1 from the depth chart; fill-ins by depth-chart rank, then attempts (a Week 4 audit showed attempts alone picked Keenum over depth-chart QB2 Bagent)
    q = q.merge(INJ[INJ.team == team][["nkey", "p_active", "game_status", "practice", "injury"]],
                left_on=q.player.map(norm_name), right_on="nkey", how="left").drop(columns=["key_0"], errors="ignore")
    q["p_active"] = q.p_active.fillna(1.0)
    return q.reset_index(drop=True)

def kicker(team):
    k = sco[(sco.team == team) & (sco.Pos == "K")]
    return k.iloc[0] if len(k) else None

# ---------------- game environment ----------------
HFA = 1.0
try:
    _W = pd.read_csv(OUT + "w4_weather_forecast.csv"); WEATHER_ADJ = {tuple(r.game.split("@")): float(r.total_adj_pts) for r in _W.itertuples() if not np.isnan(getattr(r, "total_adj_pts", np.nan))}
except Exception:
    WEATHER_ADJ = {}
ENV_MODE = os.environ.get("APEX_ENV", "model")     # "model" = ridge ratings only; "market" = nflverse spread/total as the team-points prior (fitted blend weight 1.0)
def game_env(away, home, neutral=False):
    if ENV_MODE == "market" and (away, home) in MARKET and not np.isnan(MARKET[(away, home)][0]):
        sp, tot = MARKET[(away, home)]; return {home: (tot + sp) / 2.0, away: (tot - sp) / 2.0}
    A, H = TEAM[away], TEAM[home]
    h = 0.0 if neutral else HFA
    pts = {}
    pts[home] = L["ppg"] + (H["off_ppg"] - L["ppg"]) + (A["def_ppg"] - L["ppg"]) + h
    pts[away] = L["ppg"] + (A["off_ppg"] - L["ppg"]) + (H["def_ppg"] - L["ppg"]) - h
    wa = WEATHER_ADJ.get((away, home), 0.0)       # fitted wind/cold effect on the total (the market line already prices weather, so only the model track uses it)
    pts[home] += wa / 2; pts[away] += wa / 2
    return pts

if __name__ == "__main__":
    print(L)
    print(INJ.groupby("game_status", dropna=False).size())
    g = []
    for _, r in SCHED.iterrows():
        e = game_env(r.away, r.home, neutral=(r.away == "IND" and r.home == "WAS"))
        g.append((r.away, r.home, round(e[r.away], 1), round(e[r.home], 1)))
    print(pd.DataFrame(g, columns=["away", "home", "away_pts", "home_pts"]).to_string())
    for t in ("KC", "SF"):
        d, o1, o2 = build_roster(t); print(t, o1, o2); print(d[["player", "pos", "tgt_sh", "car_sh", "catch", "ypr", "ypc", "p_active", "w_rec_td", "w_rush_td"]].round(3).to_string())
    print(CATCH, YPR, YPC_POS)
