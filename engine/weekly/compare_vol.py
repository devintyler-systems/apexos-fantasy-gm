"""Compare volume-dispersion / share-cap variants on the 27 backtest slates (2023-25 weeks 4-12).
usage: python3 compare_vol.py base new new_cap33 ...   (reads bt_<season>_w<week>_<tag>.pkl and btteam_*.pkl from APEX_OUT)"""
from paths import OUT, NFLV, DELIV, CONF
import sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from load import norm_name
N = NFLV; O = OUT
NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
tags = sys.argv[1:] or ["base", "new"]
def pin(y, q, tau): d = y - q; return np.mean(np.maximum(tau * d, (tau - 1) * d))
ACT = {}; SNAP = {}; TEAM = {}; GAM = pd.read_parquet(N + "games.parquet")
for S in (2023, 2024, 2025):
    st = pd.read_parquet(N + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy(); st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name); ACT[S] = st
    sn = pd.read_parquet(N + f"snap_counts_{S}.parquet"); sn = sn[(sn.game_type == "REG") & ((sn.offense_snaps > 0) | (sn.st_snaps > 0) | (sn.defense_snaps > 0))].copy(); sn["team"] = sn.team.replace(NV2T); sn["nkey"] = sn.player.map(norm_name); SNAP[S] = sn
    tw = pd.read_parquet(N + f"stats_team_week_{S}.parquet"); tw = tw[tw.season_type == "REG"].copy(); tw["team"] = tw.team.replace(NV2T); TEAM[S] = tw
res = []
for tag in tags:
    prow = []; trow = []; gm = []
    for S in (2023, 2024, 2025):
        g = GAM[(GAM.season == S) & (GAM.game_type == "REG")].copy()
        for c in ("home_team", "away_team"): g[c] = g[c].replace(NV2T)
        for W in range(4, 13):
            try: P = pd.read_pickle(O + f"bt_{S}_w{W}_{tag}.pkl"); T = pd.read_pickle(O + f"btteam_{S}_w{W}_{tag}.pkl")
            except Exception: continue
            played = set(zip(SNAP[S][SNAP[S].week == W].nkey, SNAP[S][SNAP[S].week == W].team))
            a = ACT[S][ACT[S].week == W][["nkey", "team", "receiving_yards", "receptions", "rushing_yards", "passing_yards", "rushing_tds", "receiving_tds", "carries"]]
            P = P[[(x, y) in played for x, y in zip(P.nkey, P.team)]].merge(a, on=["nkey", "team"], how="left")
            for c in ["receiving_yards", "receptions", "rushing_yards", "passing_yards", "rushing_tds", "receiving_tds"]: P[c] = P[c].fillna(0)
            P["a_td"] = ((P.rushing_tds + P.receiving_tds) >= 1).astype(float); P["season"] = S; P["week"] = W; prow.append(P)
            tt = T[T.team.notna()].copy(); tt["season"] = S; tt["week"] = W
            tw = TEAM[S][TEAM[S].week == W][["team", "attempts", "carries"]]; tt = tt.merge(tw, on="team", how="left"); trow.append(tt)
            ga = g[g.week == W]; tp = T[T.away.notna()]
            for r in tp.itertuples():
                x = ga[(ga.away_team == r.away) & (ga.home_team == r.home)]
                if len(x): gm.append((r.away_pts, x.away_score.iloc[0], r.home_pts, x.home_score.iloc[0]))
    P = pd.concat(prow); T = pd.concat(trow); out = dict(tag=tag, n_slates=len(prow))
    for nm, mask, mc, ac, qk in [("rec_yds", (P.rec >= 1.0) & (P.pos != "QB"), "rec_yds", "receiving_yards", "rec_yds"), ("rec", (P.rec >= 1.0) & (P.pos != "QB"), "rec", "receptions", "rec"),
                                  ("rush_yds", (P.rush_att >= 4) & (P.pos != "QB"), "rush_yds", "rushing_yards", "rush_yds"), ("pass_yds", P.pass_yds >= 100, "pass_yds", "passing_yards", "pass_yds")]:
        d = P[mask & (P.p_active >= 0.9)]; y = d[ac]; out[nm + "_mae"] = (d[mc] - y).abs().mean(); out[nm + "_bias"] = (d[mc] - y).mean()
        out[nm + "_cov50"] = ((y >= d[qk + "_q25"]) & (y <= d[qk + "_q75"])).mean(); out[nm + "_cov80"] = ((y >= d[qk + "_q10"]) & (y <= d[qk + "_q90"])).mean()
        out[nm + "_pinball"] = sum(pin(y, d[qk + f"_q{q}"], q / 100) for q in (10, 25, 75, 90))
    d = P[(P.pos != "QB") & (P.any_td >= 0.03) & (P.p_active >= 0.9)]; p = np.clip(d.any_td, 0.01, 0.99); out["td_ll"] = float(-np.mean(d.a_td * np.log(p) + (1 - d.a_td) * np.log(1 - p))); out["td_brier"] = float(np.mean((p - d.a_td) ** 2))
    gm = np.array(gm); out["team_pts_rmse"] = float(np.sqrt(np.mean(np.r_[(gm[:, 0] - gm[:, 1]) ** 2, (gm[:, 2] - gm[:, 3]) ** 2])))
    T = T.dropna(subset=["attempts"]); out["att_sim_sd"] = T.t_att_sd.mean(); out["att_err_sd"] = (T.attempts - T.t_att).std(); out["att_outside_p5_95"] = ((T.attempts < T.t_att_q05) | (T.attempts > T.t_att_q95)).mean()
    out["rush_sim_sd"] = T.t_rush_sd.mean(); out["rush_err_sd"] = (T.carries - T.t_rush).std(); out["rush_outside_p5_95"] = ((T.carries < T.t_rush_q05) | (T.carries > T.t_rush_q95)).mean()
    # top projected receiver per team: bias (stars)
    P["rk"] = P.groupby(["season", "week", "team"]).rec.rank(ascending=False, method="first"); s1 = P[(P.rk == 1) & (P.pos != "QB") & (P.p_active >= 0.9)]
    out["top1_rec_bias_pct"] = (s1.rec.mean() / s1.receptions.mean() - 1) * 100; out["top1_recyds_bias_pct"] = (s1.rec_yds.mean() / s1.receiving_yards.mean() - 1) * 100
    res.append(out)
R = pd.DataFrame(res).set_index("tag").T; pd.set_option("display.width", 200); pd.set_option("display.max_rows", 100)
print(R.round(4).to_string()); R.to_csv(O + "compare_vol.csv")
