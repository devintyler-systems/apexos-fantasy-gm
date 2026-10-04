"""Does expected-opportunity data (ffopportunity xRec/xYds/xTD, air-yard share) + snap share improve week-4+ role/efficiency forecasts? Backtest 2019-2025."""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, json, warnings; warnings.filterwarnings("ignore")
N=NFLV
pl=pd.read_parquet(N+"players.parquet",columns=["gsis_id","pfr_id"]).dropna(); P2G=dict(zip(pl.pfr_id,pl.gsis_id))
fr=[]
for y in range(2018,2026):
    f=pd.read_parquet(N+f"ffo_weekly_{y}.parquet"); f=f[f.position.isin(["QB","RB","FB","WR","TE"])].copy()
    f["tsh"]=(f.rec_attempt/f.rec_attempt_team.replace(0,np.nan)).fillna(0); f["csh"]=(f.rush_attempt/f.rush_attempt_team.replace(0,np.nan)).fillna(0); f["ash"]=(f.rec_air_yards/f.rec_air_yards_team.replace(0,np.nan)).fillna(0)
    sn=pd.read_parquet(N+f"snap_counts_{y}.parquet"); sn=sn[(sn.game_type=="REG")&(sn.offense_snaps>0)].copy(); sn["gsis"]=sn.pfr_player_id.map(P2G)
    f=f.rename(columns={"player_id":"gsis"}).merge(sn[["week","gsis","offense_pct"]],on=["week","gsis"],how="left"); f["snap"]=f.offense_pct.fillna(0)
    f["pos"]=f.position.replace({"FB":"RB"}); fr.append(f)
D=pd.concat(fr,ignore_index=True); D["week"]=D.week.astype(int); D["season"]=D.season.astype(int); print("player-weeks",len(D),"snap coverage",round(D.offense_pct.notna().mean(),3))
def agg(df):
    return df.groupby("gsis").agg(pos=("pos","last"),team=("posteam","last"),n=("week","size"),tsh=("tsh","mean"),csh=("csh","mean"),ash=("ash","mean"),snap=("snap","mean"),
        tgt=("rec_attempt","sum"),rec=("receptions","sum"),rec_x=("receptions_exp","sum"),ryds=("rec_yards_gained","sum"),ryds_x=("rec_yards_gained_exp","sum"),rtd=("rec_touchdown","sum"),rtd_x=("rec_touchdown_exp","sum"),
        car=("rush_attempt","sum"),cyds=("rush_yards_gained","sum"),cyds_x=("rush_yards_gained_exp","sum"),ctd=("rush_touchdown","sum"),ctd_x=("rush_touchdown_exp","sum"))
rows=[]
for s in range(2019,2026):
    last=agg(D[D.season==s-1]); last=last[last.n>=6]
    obs=agg(D[(D.season==s)&(D.week<=3)]); fut=agg(D[(D.season==s)&(D.week.between(4,9))]); fut=fut[fut.n>=3]
    x=obs.join(fut,rsuffix="_f",how="inner").join(last,rsuffix="_l",how="left"); x["season"]=s; rows.append(x.reset_index())
X=pd.concat(rows,ignore_index=True); X=X[X.pos.isin(["RB","WR","TE","QB"])]
TRN=X[X.season<=2023]; TST=X[X.season>=2024]
def ridge(Xm,y,w,lam=1.0):
    A=Xm.T@(Xm*w[:,None])+lam*np.eye(Xm.shape[1]); return np.linalg.solve(A,Xm.T@(w*y))
def feat(df,cols): 
    M=np.c_[np.ones(len(df))]; 
    for c in cols: M=np.c_[M,np.nan_to_num(df[c].values)]
    return M
def role_test(pos_list,ycol,base_cols,extra_cols,label):
    out={}
    for pos in pos_list:
        tr=TRN[TRN.pos==pos]; te=TST[TST.pos==pos]
        if len(tr)<50: continue
        def run(cols):
            Xtr=feat(tr,cols); w=tr.n_f.values.astype(float); b=ridge(Xtr,tr[ycol].values,w,lam=0.05); p=feat(te,cols)@b; wt=te.n_f.values; return float(np.sum(wt*(p-te[ycol].values)**2)/wt.sum()),b
        m0,_=run(base_cols); m1,b1=run(base_cols+extra_cols); out[pos]=dict(base=m0,with_extra=m1,pct=(m1/m0-1)*100,coef=dict(zip(["const"]+base_cols+extra_cols,[round(float(v),4) for v in b1])))
        print(f"{label:10s} {pos}: TEST mse base(obs+last-season share) {m0:.5f}  +extras {m1:.5f}  ({(m1/m0-1)*100:+.1f}%)")
    return out
res={}
X["tsh_l0"]=X.tsh_l.fillna(0); X["csh_l0"]=X.csh_l.fillna(0)
for d in (TRN,TST): d["tsh_l0"]=d.tsh_l.fillna(0); d["csh_l0"]=d.csh_l.fillna(0); d["has_l"]=d.tsh_l.notna().astype(float)
res["tgt_share"]=role_test(["WR","TE","RB"],"tsh_f",["tsh","tsh_l0","has_l"],["snap","ash"],"tgt share")
res["tgt_share_snap_only"]=role_test(["WR","TE","RB"],"tsh_f",["tsh","tsh_l0","has_l"],["snap"],"tgt+snap")
res["carry_share"]=role_test(["RB","QB"],"csh_f",["csh","csh_l0","has_l"],["snap"],"car share")
# efficiency: actual vs expected numerators (pooled-ratio shrink, same grid as fit_player_priors)
def ratio_test(num,numx,den,label,positions,kgrid):
    for pos in positions:
        tr=TRN[(TRN.pos==pos)&(TRN[den]>0)]; te=TST[(TST.pos==pos)&(TST[den]>0)]
        pm_a=TRN[TRN.pos==pos][num].sum()/TRN[TRN.pos==pos][den].sum()
        def mse(df,k,a,use_x):
            d=df[df[den+"_f"]>0]; w=d[den+"_f"].values; y=(d[num+"_f"]/d[den+"_f"]).values
            o=(d[numx] if use_x else d[num]).values; lr=((d[numx+"_l"] if use_x else d[num+"_l"])/d[den+"_l"].replace(0,np.nan)).values
            aa=np.where(np.isnan(lr)|(d[den+"_l"].fillna(0).values<20),0,a); pr=aa*np.nan_to_num(lr)+(1-aa)*pm_a
            return float(np.sum(w*((o+k*pr)/(d[den].values+k)-y)**2)/w.sum())
        best={}
        for ux in (False,True):
            bb=min(((mse(tr,k,a,ux),k,a) for k in kgrid for a in (0,.25,.5,.75)),key=lambda z:z[0]); best[ux]=(mse(te,bb[1],bb[2],ux),bb[1],bb[2])
        print(f"{label:10s} {pos}: TEST mse actual-based {best[False][0]:.5f} (k={best[False][1]},a={best[False][2]})  expected-based {best[True][0]:.5f} (k={best[True][1]},a={best[True][2]})  ({(best[True][0]/best[False][0]-1)*100:+.1f}%)")
        res.setdefault("ratio",{})[f"{label}_{pos}"]=dict(actual=best[False],expected=best[True])
ratio_test("rec","rec_x","tgt","catch rate",["WR","TE","RB"],(5,10,22,40,80,160,400))
ratio_test("ryds","ryds_x","rec","yds/rec",["WR","TE","RB"],(3,7,14,30,60,120,400))
ratio_test("rtd","rtd_x","tgt","rec TD/tgt",["WR","TE","RB"],(10,30,60,120,250,600,2000))
ratio_test("cyds","cyds_x","car","yds/carry",["RB","QB"],(10,25,45,90,200,500,2000))
ratio_test("ctd","ctd_x","car","rush TD/car",["RB","QB"],(20,60,120,250,500,1500,5000))
json.dump(res,open(CONF+"opportunity_fit.json","w"),indent=1,default=float); print("saved opportunity_fit.json")
