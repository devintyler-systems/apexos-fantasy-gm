"""Collect DraftKings Classic point distributions per player/DST from the correlated sims (env mode via APEX_ENV)."""
from paths import OUT, NFLV, DELIV, CONF
import sys, numpy as np, pandas as pd, pickle, warnings; warnings.filterwarnings("ignore")
import run_all as R
from params import SCHED, norm_name, is_neutral, ENV_MODE
SLATE={("KC","LV"),("DEN","SF"),("LAC","SEA"),("DAL","HOU"),("LA","PHI"),("ARI","NYG"),("MIA","MIN"),("GB","TB"),("NYJ","CHI"),("TEN","BAL"),("JAX","CIN"),("NE","BUF")}
NS=20000; out={}; meta={}
def dk(pl):
    base=0.04*pl["pass_yds"]+4*pl["pass_td"]-2*pl["pass_int"]+0.1*(pl["rush_yds"]+pl["rec_yds"])+6*(pl["rush_td"]+pl["rec_td"])+pl["rec"]
    fl=np.clip((base-pl["fp"])/2.0,0,None)      # fumbles lost implied by the PPR fantasy-point draw (-2 each there)
    return (0.04*pl["pass_yds"]+4*pl["pass_td"]-1*pl["pass_int"]+3*(pl["pass_yds"]>=300)+0.1*pl["rush_yds"]+6*pl["rush_td"]+3*(pl["rush_yds"]>=100)
            +pl["rec"]+0.1*pl["rec_yds"]+6*pl["rec_td"]+3*(pl["rec_yds"]>=100)-1*fl)
def tier(pa): return np.select([pa==0,pa<=6,pa<=13,pa<=20,pa<=27,pa<=34],[10,7,4,1,0,-1],-4)
for _,g in SCHED.iterrows():
    if (g.away,g.home) not in SLATE: continue
    R.run_game(g.away,g.home,neutral=bool(g.neutral),ns=NS)
    d=R.STORE.pop((g.away,g.home)); A,H=d["A"],d["H"]; gk=f"{g.away}@{g.home}"
    for t in (g.away,g.home):
        for pl in d["players"][t]:
            if pl["p_active"]<0.03 or pl["mask"].sum()<200: continue
            arr=(dk(pl)*pl["mask"]).astype(np.float32); key=(norm_name(pl["player"]),t,pl["pos"] if pl["pos"]!="QB" else "QB")
            out[key]=arr; meta[key]=dict(player=pl["player"],team=t,game=gk,pos=pl["pos"],p_active=pl["p_active"],proxy=bool(pl.get("proxy")))
    for t,own,opp in ((g.away,A,H),(g.home,H,A)):
        pa=opp["off_pts"]; arr=(opp["sacks"]+2*opp["int_n"]+2*opp["fl_n"]+6*own["dtd"]+2*own["saf"]+tier(pa)).astype(np.float32)
        key=("DST",t,"DST"); out[key]=arr; meta[key]=dict(player=f"{t} DST",team=t,game=gk,pos="DST",p_active=1.0,proxy=False)
pickle.dump((out,meta),open(f"{OUT}dfs_sims_{ENV_MODE}.pkl","wb")); print("collected",len(out),"mode",ENV_MODE)
