"""Rest-of-season forecast: team offense (points for), team defense (points against), kickers and tight ends.

  APEX_ENV=market APEX_TARGET_WEEK=7 python ros_forecast.py <proj_all.pkl> <out_dir>

Team points per remaining game come from params.game_env: nflverse market line where one exists (next week), the fitted opponent-adjusted
ridge ratings (model-only environment) for every later game. No weather, no future injuries beyond the availability assumptions below.
Kickers use the league rule (DECISIONS #27, kicker = 4.078 + 0.1439 x team points per game); tight ends scale the engine's neutral-environment
TD rate by each remaining opponent environment. SPAMML scoring: 6 per rushing or receiving TD, FG 3, XP 1 (kicker points = 3*FG + XP).
"""
import os
import sys

import numpy as np
import pandas as pd

import params as P
import league_spm as LS

GAME_SD = 7.3      # team points RMSE, W6 market track (POSTMORTEM_2026_W06)
K_SD = 3.4         # kicker points sd per game (3*FG + XP), 2023-26 weeks 4-12
AV_FUTURE = [(0.9, 0.95), (0.6, 0.85), (0.0, 0.70)]   # (W7 p_active floor, per-game availability afterwards)


def remaining():
    g = P._G[P._G.home_score.isna()].copy()
    rows = []
    for r in g.itertuples():
        a, h = P.tm(r.away_team), P.tm(r.home_team)
        e = P.game_env(a, h, neutral=P.is_neutral(a, h))
        rows.append(dict(week=r.week, team=h, opp=a, home=True, pf=e[h], pa=e[a]))
        rows.append(dict(week=r.week, team=a, opp=h, home=False, pf=e[a], pa=e[h]))
    return pd.DataFrame(rows)


def team_tables(G):
    ytd = P.off.assign(pf=P.off.pts / P.off.G, pa=P.off.pa / P.off.G)[["pf", "pa"]]
    t = G.groupby("team").agg(games=("week", "size"), ros_pf=("pf", "sum"), ros_pa=("pa", "sum"), pf_g=("pf", "mean"), pa_g=("pa", "mean"))
    t["off_rating"] = pd.Series({k: v[0] for k, v in P.RIDGE.items()})
    t["def_rating"] = pd.Series({k: v[1] for k, v in P.RIDGE.items()})
    t["ytd_pf_g"], t["ytd_pa_g"] = ytd.pf, ytd.pa
    t["sd_total"] = GAME_SD * np.sqrt(t.games)
    off = t.sort_values("ros_pf", ascending=False).reset_index().rename(columns={"index": "team"})
    off.insert(0, "rank", range(1, len(off) + 1))
    de = t.sort_values("ros_pa").reset_index().rename(columns={"index": "team"})
    de.insert(0, "rank", range(1, len(de) + 1))
    return off, de


def avail_future(p):
    return next(a for floor, a in AV_FUTURE if p >= floor)


def kickers(G):
    st = pd.read_parquet(os.path.join(P.N, f"stats_player_week_{P.SEASON}.parquet"))
    cur = LS.current_kickers(st)
    k = st[st.position == "K"].copy()
    for c in ("fg_made", "fg_att", "pat_made"):
        k[c] = pd.to_numeric(k[c], errors="coerce").fillna(0)
    k["pts"] = 3 * k.fg_made + k.pat_made
    agg = k.groupby("player_display_name").agg(team=("team", "last"), g=("week", "nunique"), avg=("pts", "mean"), fga=("fg_att", "mean"))
    out = []
    for team, nk in cur.items():
        nm = next((n for n in agg.index if LS.norm_name(n) == nk and agg.loc[n, "team"] == team), None)
        gg = G[G.team == team]
        if nm is None or gg.empty:
            continue
        cfg = LS.load_cfg()["kicker_env"]
        per = cfg["intercept"] + cfg["slope"] * gg.pf
        tot = float((per * 0.98).sum())
        out.append(dict(kicker=nm, team=team, games_left=len(gg), ros_pts=tot, pts_g=tot / len(gg), p10=tot - 1.28 * K_SD * np.sqrt(len(gg)), p90=tot + 1.28 * K_SD * np.sqrt(len(gg)),
                        ytd_avg=agg.loc[nm, "avg"], ytd_fga_g=agg.loc[nm, "fga"], ytd_games=int(agg.loc[nm, "g"])))
    o = pd.DataFrame(out).sort_values("ros_pts", ascending=False).reset_index(drop=True)
    o.insert(0, "rank", range(1, len(o) + 1))
    return o


def tight_ends(G, proj, w7_pts):
    ppg = P.L["ppg"]
    te = proj[proj.pos == "TE"].copy()
    out = []
    for r in te.itertuples():
        mean = float(np.nansum([r.rec_td_mean, r.rush_td_mean]))
        w7 = w7_pts.get(r.team)
        gg = G[G.team == r.team]
        if gg.empty or not w7:
            continue
        lam0 = mean / (w7 / ppg)                           # TDs per game, neutral environment, when active
        av_f = avail_future(float(r.p_active))
        env = (gg.pf / ppg).values
        avail = np.where(gg.week.values == gg.week.min(), float(r.p_active), av_f)
        tds = float((lam0 * env * avail).sum())
        out.append(dict(player=r.player, team=r.team, games_left=len(gg), w7_status=r.status if isinstance(r.status, str) else "", w7_p_active=round(float(r.p_active), 2),
                        ros_tds=tds, ros_pts=6 * tds, pts_g=6 * tds / len(gg), p10=max(0, 6 * (tds - 1.28 * np.sqrt(tds))), p90=6 * (tds + 1.28 * np.sqrt(tds)),
                        tgt_sh=float(r.tgt_sh) if pd.notna(r.tgt_sh) else np.nan, w7_td_mean=mean))
    o = pd.DataFrame(out).sort_values("ros_pts", ascending=False).reset_index(drop=True)
    o.insert(0, "rank", range(1, len(o) + 1))
    return o


def main(proj_pkl, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    proj = pd.read_pickle(proj_pkl)
    G = remaining()
    w7 = G[G.week == G.week.min()].set_index("team").pf.to_dict()
    off, de = team_tables(G)
    K, TE = kickers(G), tight_ends(G, proj, w7)
    for n, d in (("team_offense", off), ("team_defense", de), ("kickers", K), ("tight_ends", TE)):
        d.round(3).to_csv(os.path.join(out_dir, f"ros_{n}.csv"), index=False)
    return off, de, K, TE, G


if __name__ == "__main__":
    off, de, K, TE, G = main(sys.argv[1], sys.argv[2])
    print(f"remaining weeks {G.week.min()}-{G.week.max()}, {len(G)//2} games")
    print(off.round(1).to_string(index=False)); print(de.round(1).to_string(index=False)); print(K.round(1).to_string(index=False)); print(TE.head(40).round(1).to_string(index=False)); print(len(TE))
