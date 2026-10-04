from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from load import norm_name
N=NFLV; O=OUT
NV2T={"LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV","OAK":"LV","SD":"LAC","STL":"LA"}
pl=pd.read_parquet(N+"players.parquet",columns=["gsis_id","pfr_id"]).dropna(); P2G=dict(zip(pl.pfr_id,pl.gsis_id))
res=[]; tres=[]
for S in (2023,2024,2025):
    st=pd.read_parquet(N+f"stats_player_week_{S}.parquet"); st=st[(st.season_type=="REG")&(st.week==4)].copy(); st["team"]=st.team.replace(NV2T); st["nkey"]=st.player_display_name.map(norm_name)
    sn=pd.read_parquet(N+f"snap_counts_{S}.parquet"); sn=sn[(sn.game_type=="REG")&(sn.week==4)&((sn.offense_snaps>0)|(sn.st_snaps>0)|(sn.defense_snaps>0))]; sn["team"]=sn.team.replace(NV2T); sn["nkey"]=sn.player.map(norm_name)
    played=set(zip(sn.nkey,sn.team))
    g=pd.read_parquet(N+"games.parquet"); g=g[(g.season==S)&(g.week==4)&(g.game_type=="REG")].copy(); g["home_team"]=g.home_team.replace(NV2T); g["away_team"]=g.away_team.replace(NV2T)
    for tag in ("v3_model","v4_model","v4_market"):
        P=pd.read_pickle(O+f"bt_{S}_{tag}.pkl"); P["played"]=[(a,b) in played for a,b in zip(P.nkey,P.team)]
        P=P[P.played].merge(st[["nkey","team","completions","passing_yards","passing_tds","rushing_yards","carries","receptions","receiving_yards","rushing_tds","receiving_tds"]],on=["nkey","team"],how="left")
        for c in ["completions","passing_yards","passing_tds","rushing_yards","carries","receptions","receiving_yards","rushing_tds","receiving_tds"]: P[c]=P[c].fillna(0)
        P["a_td"]=((P.rushing_tds+P.receiving_tds)>=1).astype(float)
        def m(mask,pc,ac): d=P[mask]; return dict(n=len(d),mae=(d[pc]-d[ac]).abs().mean(),bias=(d[pc]-d[ac]).mean())
        out=dict(season=S,tag=tag)
        for nm,mask,pc,ac in (("rec_yds",(P.rec>=1.0)&(P.pos!="QB"),"rec_yds","receiving_yards"),("rec",(P.rec>=1.0)&(P.pos!="QB"),"rec","receptions"),("rush_yds",(P.rush_att>=4)&(P.pos!="QB"),"rush_yds","rushing_yards"),
                              ("pass_yds",(P.pass_yds>=100),"pass_yds","passing_yards"),("pass_cmp",(P.pass_yds>=100),"pass_cmp","completions")):
            r=m(mask,pc,ac); out[nm+"_mae"]=r["mae"]; out[nm+"_bias"]=r["bias"]; out[nm+"_n"]=r["n"]
        td=P[(P.pos!="QB")&(P.any_td>=0.03)]; p=np.clip(td.any_td,0.01,0.99); out["td_brier"]=float(np.mean((p-td.a_td)**2)); out["td_ll"]=float(-np.mean(td.a_td*np.log(p)+(1-td.a_td)*np.log(1-p))); out["td_sum_p"]=float(p.sum()); out["td_actual"]=float(td.a_td.sum())
        res.append(out)
        T=pd.read_pickle(O+f"btteam_{S}_{tag}.pkl").merge(g[["away_team","home_team","away_score","home_score"]],left_on=["away","home"],right_on=["away_team","home_team"])
        tres.append(dict(season=S,tag=tag,rmse=float(np.sqrt(np.mean(np.r_[(T.away_pts-T.away_score)**2,(T.home_pts-T.home_score)**2]))),margin_rmse=float(np.sqrt(np.mean(((T.home_pts-T.away_pts)-(T.home_score-T.away_score))**2))),total_rmse=float(np.sqrt(np.mean(((T.home_pts+T.away_pts)-(T.home_score+T.away_score))**2)))))
R=pd.DataFrame(res); pd.set_option("display.width",250)
print(R.groupby("tag")[[c for c in R.columns if c.endswith("_mae") or c in("td_brier","td_ll")]].mean().round(4).to_string())
print("\nBIAS (proj - actual):"); print(R.groupby("tag")[[c for c in R.columns if c.endswith("_bias")]].mean().round(2).to_string())
print("\nTD: sum of projected probs vs actual scorers"); print(R.groupby("tag")[["td_sum_p","td_actual"]].sum().round(1).to_string())
print("\nTEAM points RMSE (week 4):"); print(pd.DataFrame(tres).groupby("tag")[["rmse","margin_rmse","total_rmse"]].mean().round(3).to_string())
print("\nby season rec_yds MAE:"); print(R.pivot(index="season",columns="tag",values="rec_yds_mae").round(2).to_string()); print(R.pivot(index="season",columns="tag",values="rush_yds_mae").round(2).to_string())
R.to_csv(O+"backtest_week4_results.csv",index=False)
