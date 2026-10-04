from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, json, warnings; warnings.filterwarnings("ignore")
from load import norm_name
N=NFLV; O=OUT
NV2T={"LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV","OAK":"LV","SD":"LAC","STL":"LA"}
rows=[]
for S in (2023,2024,2025):
    st=pd.read_parquet(N+f"stats_player_week_{S}.parquet"); st=st[st.season_type=="REG"].copy(); st["team"]=st.team.replace(NV2T); st["nkey"]=st.player_display_name.map(norm_name)
    sn=pd.read_parquet(N+f"snap_counts_{S}.parquet"); sn=sn[(sn.game_type=="REG")&(sn.offense_snaps>0)].copy(); sn["team"]=sn.team.replace(NV2T); sn["nkey"]=sn.player.map(norm_name)
    for W in range(4,13):
        P=pd.read_pickle(O+f"bt_{S}_w{W}_v4.pkl"); pl=set(zip(sn[sn.week==W].nkey,sn[sn.week==W].team))
        P=P[[ (a,b) in pl for a,b in zip(P.nkey,P.team)]]
        a=st[st.week==W][["nkey","team","completions","passing_yards","passing_tds","rushing_yards","carries","receptions","receiving_yards","rushing_tds","receiving_tds"]]
        P=P.merge(a,on=["nkey","team"],how="left"); 
        for c in a.columns[2:]: P[c]=P[c].fillna(0)
        P["season"]=S; P["week"]=W; rows.append(P)
D=pd.concat(rows,ignore_index=True); D["a_td"]=((D.rushing_tds+D.receiving_tds)>=1).astype(float); print("player-games",len(D))
sk=D[D.pos!="QB"]
spec={"pass_yds":(D[D.pass_yds>=100],"pass_yds","passing_yards"),"pass_cmp":(D[D.pass_yds>=100],"pass_cmp","completions"),"pass_td":(D[D.pass_yds>=100],"pass_td","passing_tds"),
      "rec_yds":(sk[sk.rec>=1.0],"rec_yds","receiving_yards"),"rec":(sk[sk.rec>=1.0],"rec","receptions"),"rush_yds":(sk[sk.rush_att>=4],"rush_yds","rushing_yards")}
fac={}
print("factor = sum(actual)/sum(projected); MAE before/after scaling (fit 2023-24, test 2025)")
for k,(d,pc,ac) in spec.items():
    tr=d[d.season<=2024]; te=d[d.season==2025]; f=tr[ac].sum()/tr[pc].sum(); fa=d[ac].sum()/d[pc].sum()
    mae0=(te[pc]-te[ac]).abs().mean(); mae1=(te[pc]*f-te[ac]).abs().mean()
    fac[k]=float(fa); print(f"{k:9s} n={len(d):5d} factor(all)={fa:.3f} factor(train)={f:.3f}  2025 MAE {mae0:.3f} -> {mae1:.3f}  bias {np.mean(te[pc]-te[ac]):+.2f} -> {np.mean(te[pc]*f-te[ac]):+.2f}")
# by volume bucket (projected) for rec_yds and rush_yds
for k in ("rec_yds","rush_yds","rec"):
    d,pc,ac=spec[k]; q=pd.qcut(d[pc],4,duplicates="drop"); print(k,"by projection quartile (actual/proj):",(d.groupby(q)[ac].sum()/d.groupby(q)[pc].sum()).round(3).to_dict())
# TD calibration: logistic on logit(p)
t=sk[sk.any_td>=0.02].copy(); t["lp"]=np.log(np.clip(t.any_td,.005,.995)/(1-np.clip(t.any_td,.005,.995)))
def fit_logit(df):
    a,b=0.0,1.0
    for _ in range(300):
        z=a+b*df.lp.values; p=1/(1+np.exp(-z)); g=np.array([np.sum(p-df.a_td.values),np.sum((p-df.a_td.values)*df.lp.values)]); H=np.array([[np.sum(p*(1-p)),np.sum(p*(1-p)*df.lp.values)],[np.sum(p*(1-p)*df.lp.values),np.sum(p*(1-p)*df.lp.values**2)]]); s=np.linalg.solve(H+1e-9*np.eye(2),g); a,b=a-s[0],b-s[1]
    return a,b
tr=t[t.season<=2024]; te=t[t.season==2025]; a,b=fit_logit(tr)
def ll(p,y): p=np.clip(p,.01,.99); return -np.mean(y*np.log(p)+(1-y)*np.log(1-p))
p0=np.clip(te.any_td,.01,.99); p1=1/(1+np.exp(-(a+b*te.lp)))
print(f"TD logit calibration a={a:.3f} b={b:.3f}  2025 logloss {ll(p0,te.a_td):.4f} -> {ll(p1,te.a_td):.4f}; mean proj {p0.mean():.3f} actual {te.a_td.mean():.3f}")
a2,b2=fit_logit(t); print("TD all-data fit a=%.3f b=%.3f"%(a2,b2))
bins=pd.cut(t.any_td,[0,.1,.2,.3,.4,.5,.6,.8,1]); print(t.groupby(bins).agg(n=("a_td","size"),proj=("any_td","mean"),actual=("a_td","mean")).round(3).to_string())
fac.update({"td_a":float(a2),"td_b":float(b2)}); json.dump(fac,open(CONF+"calibration.json","w"),indent=1); print(fac)
