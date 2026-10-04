from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, sys, warnings; warnings.filterwarnings("ignore")
from load import norm_name
N=NFLV; O=OUT
NV2T={"LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV","OAK":"LV","SD":"LAC","STL":"LA"}
tags=sys.argv[1:]
act={}
for S in (2023,2024,2025):
    st=pd.read_parquet(N+f"stats_player_week_{S}.parquet"); st=st[st.season_type=="REG"].copy(); st["team"]=st.team.replace(NV2T); st["nkey"]=st.player_display_name.map(norm_name)
    sn=pd.read_parquet(N+f"snap_counts_{S}.parquet"); sn=sn[(sn.game_type=="REG")&(sn.offense_snaps>0)].copy(); sn["team"]=sn.team.replace(NV2T); sn["nkey"]=sn.player.map(norm_name); act[S]=(st,sn)
def load(tag):
    rows=[]
    for S in (2023,2024,2025):
        st,sn=act[S]
        for W in range(4,13):
            P=pd.read_pickle(O+f"bt_{S}_w{W}_{tag}.pkl"); pl=set(zip(sn[sn.week==W].nkey,sn[sn.week==W].team)); P=P[[ (a,b) in pl for a,b in zip(P.nkey,P.team)]]
            a=st[st.week==W][["nkey","team","completions","passing_yards","passing_tds","carries","rushing_yards","receptions","receiving_yards","rushing_tds","receiving_tds"]]; P=P.merge(a,on=["nkey","team"],how="left").fillna(0); P["season"]=S; rows.append(P)
    return pd.concat(rows,ignore_index=True)
out=[]
for tag in tags:
    D=load(tag); sk=D[D.pos!="QB"]; r={"tag":tag}
    for nm,mask,pc,ac in (("rec_yds",(sk.rec>=1.0),"rec_yds","receiving_yards"),("rec",(sk.rec>=1.0),"rec","receptions"),("rush_yds",(sk.rush_att>=4),"rush_yds","rushing_yards"),("rush_att",(sk.rush_att>=4),"rush_att","carries")):
        d=sk[mask]; r[nm+"_ratio"]=d[ac].sum()/d[pc].sum(); r[nm+"_mae"]=(d[pc]-d[ac]).abs().mean()
    for pos in ("WR","TE","RB"):
        d=sk[(sk.pos==pos)&(sk.rec>=1.0)]; r[f"rec_ratio_{pos}"]=d.receptions.sum()/d.rec.sum()
    d=sk[(sk.pos=="RB")&(sk.rush_att>=4)]; r["rb_car_ratio"]=d.carries.sum()/d.rush_att.sum()
    t=sk[(sk.any_td>=0.03)]; p=np.clip(t.any_td,.01,.99); y=((t.rushing_tds+t.receiving_tds)>=1).astype(float); r["td_ll"]=float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
    out.append(r)
R=pd.DataFrame(out).set_index("tag"); pd.set_option("display.width",250); print(R.round(3).T.to_string())
