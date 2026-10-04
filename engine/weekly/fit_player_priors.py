"""Fit player-rate shrinkage (k) and last-season prior weight (a) by backtesting at the week-4 cutoff, 2019-2025."""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, itertools, json
N=NFLV
NV2T={"LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV","OAK":"LV","SD":"LAC","STL":"LA"}
pl=pd.read_parquet(N+"players.parquet",columns=["gsis_id","pfr_id"]).dropna(); P2G=dict(zip(pl.pfr_id,pl.gsis_id))
frames=[]
for y in range(2018,2026):
    st=pd.read_parquet(N+f"stats_player_week_{y}.parquet"); st=st[st.season_type=="REG"]
    sn=pd.read_parquet(N+f"snap_counts_{y}.parquet"); sn=sn[(sn.game_type=="REG")&(sn.offense_snaps>0)].copy()
    sn["gsis"]=sn.pfr_player_id.map(P2G); sn=sn[sn.gsis.notna()&sn.position.isin(["QB","RB","FB","WR","TE"])]
    sn["team"]=sn.team.replace(NV2T)
    st["team"]=st.team.replace(NV2T)
    cols=["targets","receptions","receiving_yards","receiving_tds","carries","rushing_yards","rushing_tds"]
    m=sn[["season","week","gsis","team","position"]].merge(st[["season","week","player_id"]+cols].rename(columns={"player_id":"gsis"}),on=["season","week","gsis"],how="left")
    m[cols]=m[cols].fillna(0)
    tt=st.groupby(["team","week"]).agg(tteam=("targets","sum"),cteam=("carries","sum")).reset_index()
    m=m.merge(tt,on=["team","week"],how="left"); frames.append(m)
D=pd.concat(frames,ignore_index=True); D["pos"]=D.position.replace({"FB":"RB"})
D["tsh"]=D.targets/D.tteam.replace(0,np.nan); D["csh"]=D.carries/D.cteam.replace(0,np.nan); D[["tsh","csh"]]=D[["tsh","csh"]].fillna(0)
print("player-games",len(D),"seasons",D.season.min(),D.season.max())
# ---- season aggregates ----
def agg(df):
    return df.groupby("gsis").agg(team=("team","last"),pos=("pos","last"),n=("week","size"),tsh=("tsh","mean"),csh=("csh","mean"),tgt=("targets","sum"),rec=("receptions","sum"),ryds=("receiving_yards","sum"),rtd=("receiving_tds","sum"),
                                  car=("carries","sum"),cyds=("rushing_yards","sum"),ctd=("rushing_tds","sum"))
CUT=3; FUT=range(4,10)
rows=[]
for s in range(2019,2026):
    last=agg(D[D.season==s-1]); last=last[last.n>=6]
    obs=agg(D[(D.season==s)&(D.week<=CUT)]); fut=agg(D[(D.season==s)&(D.week.isin(FUT))]); fut=fut[fut.n>=3]
    x=obs.join(fut,rsuffix="_f",how="inner").join(last,rsuffix="_l",how="left")
    x["season"]=s; x["same_team"]=(x.team_l==x.team).astype(float).where(x.team_l.notna()); rows.append(x.reset_index())
X=pd.concat(rows,ignore_index=True); X=X[X.pos.isin(["RB","WR","TE","QB"])]
# role prior = mean future share by (pos, rank of obs share within team-season)
def add_rank(df,col,key):
    df[key]=df.groupby(["season","team"])[col].rank(ascending=False,method="first"); return df
X=add_rank(X,"tsh","trk"); X=add_rank(X,"csh","crk")
TRN=X[X.season<=2023]; TST=X[X.season>=2024]
def role_table(df,col_f,rk,pos):
    d=df[df.pos==pos].copy(); d["r"]=d[rk].clip(upper=6); return d.groupby("r")[col_f].mean()
def fit_share(metric,fcol,lcol,rk,positions,label):
    out={}
    for pos in positions:
        tr=TRN[TRN.pos==pos]; te=TST[TST.pos==pos]
        rt=role_table(TRN,fcol,rk,pos)
        def pred(df,k,a,ach):
            role=df[rk].clip(upper=6).map(rt).fillna(rt.min()).values; last=df[lcol].values; same=df.same_team.values
            aa=np.where(np.isnan(last),0,np.where(np.isnan(same)|(same==0),ach,a)); prior=aa*np.nan_to_num(last)+(1-aa)*role
            return (df.n.values*df[metric].values+k*prior)/(df.n.values+k)
        def mse(df,k,a,ach): w=df.n_f.values; return float(np.sum(w*(pred(df,k,a,ach)-df[fcol].values)**2)/w.sum())
        best=min(((mse(tr,k,a,ach),k,a,ach) for k in (0.1,0.3,0.56,1,2,3,5,8) for a in (0,.25,.5,.75,1) for ach in (0,.25,.5)),key=lambda z:z[0])
        v3=mse(te,0.56,0,0); fit=mse(te,*best[1:]); obs_only=mse(te,1e-6,0,0)
        out[pos]=dict(k=best[1],a=best[2],a_changed=best[3]); print(f"{label:11s} {pos}: fitted k={best[1]} a={best[2]} a_chg={best[3]} | TEST mse v3-like {v3:.5f} fitted {fit:.5f} ({(fit/v3-1)*100:+.1f}%) obs-only {obs_only:.5f}")
    return out
fits={}
fits["tgt_share"]=fit_share("tsh","tsh_f","tsh_l","trk",["WR","TE","RB"],"tgt share")
fits["car_share"]=fit_share("csh","csh_f","csh_l","crk",["RB","QB"],"carry share")
# ---- pooled-ratio stats ----
def fit_ratio(num,den,label,positions,kgrid):
    out={}
    for pos in positions:
        tr=TRN[(TRN.pos==pos)&(TRN[den]>0)]; te=TST[(TST.pos==pos)&(TST[den]>0)]
        posmean=TRN[TRN.pos==pos][num].sum()/TRN[TRN.pos==pos][den].sum()
        def pred(df,k,a):
            lr=(df[num+"_l"]/df[den+"_l"].replace(0,np.nan)).values; lw=df[den+"_l"].fillna(0).values
            aa=np.where(np.isnan(lr)|(lw<20),0,a); prior=aa*np.nan_to_num(lr)+(1-aa)*posmean
            return (df[num].values+k*prior)/(df[den].values+k)
        def mse(df,k,a): m=df[den+"_f"]>0; d=df[m]; w=d[den+"_f"].values; y=(d[num+"_f"]/d[den+"_f"]).values; return float(np.sum(w*(pred(d,k,a)-y)**2)/w.sum())
        best=min(((mse(tr,k,a),k,a) for k in kgrid for a in (0,.25,.5,.75)),key=lambda z:z[0])
        base_k={"catch":22,"ypr":14,"ypc":45,"rtd_t":30,"ctd_c":60}[label]; v3=mse(te,base_k,0); fit=mse(te,best[1],best[2])
        out[pos]=dict(k=best[1],a=best[2]); print(f"{label:11s} {pos}: fitted k={best[1]} a={best[2]} | TEST mse v3(k={base_k},a=0) {v3:.5f} fitted {fit:.5f} ({(fit/v3-1)*100:+.1f}%)")
    return out
fits["catch"]=fit_ratio("rec","tgt","catch",["WR","TE","RB"],(5,10,22,40,80,160,400))
fits["ypr"]=fit_ratio("ryds","rec","ypr",["WR","TE","RB"],(3,7,14,30,60,120,400))
fits["ypc"]=fit_ratio("cyds","car","ypc",["RB","QB"],(10,25,45,90,200,500,2000))
fits["rtd_t"]=fit_ratio("rtd","tgt","rtd_t",["WR","TE","RB"],(10,30,60,120,250,600,2000))
fits["ctd_c"]=fit_ratio("ctd","car","ctd_c",["RB","QB"],(20,60,120,250,500,1500,5000))
json.dump(fits,open(CONF+"player_prior_fit.json","w"),indent=1); print("saved")

# ---- persist role tables and position means (all seasons) for use in params ----
ALL=X
roles={}
for nm,(fcol,rk) in {"tgt":("tsh_f","trk"),"car":("csh_f","crk")}.items():
    roles[nm]={pos:role_table(ALL,fcol,rk,pos).round(5).to_dict() for pos in ("WR","TE","RB","QB")}
posmean={}
for nm,(num,den) in {"catch":("rec","tgt"),"ypr":("ryds","rec"),"ypc":("cyds","car"),"rtd_t":("rtd","tgt"),"ctd_c":("ctd","car")}.items():
    posmean[nm]={pos:float(ALL[ALL.pos==pos][num].sum()/max(ALL[ALL.pos==pos][den].sum(),1)) for pos in ("WR","TE","RB","QB")}
fits["roles"]=roles; fits["posmean"]=posmean
json.dump(fits,open(CONF+"player_prior_fit.json","w"),indent=1); print("saved with role tables")
