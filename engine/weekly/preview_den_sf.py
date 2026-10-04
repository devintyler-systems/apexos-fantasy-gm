from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd
import run_all as R
from params import *
pd.set_option("display.width",260)
for _,g in SCHED.iterrows():
    R.run_game(g.away,g.home,neutral=is_neutral(g.away, g.home))
    if (g.away,g.home)==("DEN","SF"): break
d=R.STORE[("DEN","SF")]; A=d["A"]; H=d["H"]   # A=DEN(away) H=SF(home)
M=H["pts"]-A["pts"]; tot=H["pts"]+A["pts"]
print("SF win",((M>0).mean()+.5*(M==0).mean()).round(3),"DEN win",((M<0).mean()+.5*(M==0).mean()).round(3),"tie",(M==0).mean().round(3))
for n,s in (("DEN",A),("SF",H)): print(n,"pts mean",s["pts"].mean().round(1),"med",np.median(s["pts"]),"p25/75",np.percentile(s["pts"],[25,75]),"p90",np.percentile(s["pts"],90),"TD",s["td"].mean().round(2),"FG",s["fg"].mean().round(2),"plays",s["plays"].mean().round(1),"att",s["att"].mean().round(1),"rush",s["rush"].mean().round(1),"pr",s["prate"].mean().round(3),"pyds",s["team_pass_yds"].mean().round(0),"ryds",s["rush_yds"].mean().round(0),"sacks",s["sacks"].mean().round(2),"int",s["int_n"].mean().round(2),"pTD",s["ptd_n"].mean().round(2),"rTD",s["rtd_n"].mean().round(2),"exp ypa",round(s["ypa"],2),"exp ypc",round(s["ypc"],2),"p_start",round(s["p_start"],2))
print("margin med",np.median(M),"mean",M.mean().round(2),"P(SF by 7+)",(M>=7).mean().round(3),"P(SF by 14+)",(M>=14).mean().round(3),"P(DEN win)",(M<0).mean().round(3),"total med",np.median(tot),"p25/75",np.percentile(tot,[25,75]))
# most common exact scores
sc=pd.Series(list(zip(A["pts"],H["pts"]))).value_counts(normalize=True).head(5); print("modal scores (DEN,SF):",sc.round(3).to_dict())
# score buckets: P(SF>DEN) conditional
Ttot=np.maximum(A["td"]+H["td"]+A["dtd"]+H["dtd"],1)
rows=[]
for t in ("DEN","SF"):
    for p in d["players"][t]:
        m=p["mask"]
        if m.sum()<500 or p["p_active"]<.03: continue
        tdc=p["rush_td"]+p["rec_td"]
        q=lambda x:(float(x[m].mean()),float(np.percentile(x[m],25)),float(np.percentile(x[m],75)))
        r=p["row"]
        rows.append(dict(team=t,player=p["player"],pos=p["pos"],act=p["p_active"],status=p.get("status"),practice=p.get("practice"),
            cmp=q(p["pass_cmp"]),att=q(p["pass_att"]),pyd=q(p["pass_yds"]),ptd=q(p["pass_td"]),pint=q(p["pass_int"]),
            ratt=q(p["rush_att"]),ryd=q(p["rush_yds"]),tgt=q(p["tgt"]),rec=q(p["rec"]),recyd=q(p["rec_yds"]),
            rtd=float(p["rush_td"][m].mean()),rectd=float(p["rec_td"][m].mean()),anytime=float((tdc[m]>=1).mean()),first=float((tdc[m]/Ttot[m]).mean()),
            tgt_sh=float(getattr(r,"tgt_sh",np.nan)) if r is not None and not isinstance(r,float) else np.nan, car_sh=float(getattr(r,"car_sh",np.nan)) if r is not None and not isinstance(r,float) else np.nan,
            rz_tgt=float(getattr(r,"rz_tgt",np.nan)) if r is not None and not isinstance(r,float) else np.nan, rz10=float(getattr(r,"rz10_car",np.nan)) if r is not None and not isinstance(r,float) else np.nan))
P=pd.DataFrame(rows); P.to_pickle(OUT+"den_sf.pkl")
f=lambda t:f"{t[0]:.1f} ({t[1]:.0f}-{t[2]:.0f})"
for pos in ("QB","RB","WR","TE"):
    for r in P[P.pos==pos].itertuples():
        if pos=="QB": print(r.team,r.player,f"act {r.act:.0%}","cmp",f(r.cmp),"att",f(r.att),"yds",f(r.pyd),"td",f(r.ptd),"int",f(r.pint),"rush",f(r.ratt),f(r.ryd),"anytime",f"{r.anytime:.1%}","first",f"{r.first:.1%}",r.status,r.practice)
        else: print(r.team,pos,r.player,f"act {r.act:.0%}","rush",f(r.ratt),f(r.ryd),"tgt",f(r.tgt),"rec",f(r.rec),"yds",f(r.recyd),"rTD %.2f recTD %.2f"%(r.rtd,r.rectd),"any %.1f%% first %.1f%%"%(r.anytime*100,r.first*100),"tgt_sh %.2f car_sh %.2f rzT %.0f rz10c %.0f"%(r.tgt_sh,r.car_sh,r.rz_tgt,r.rz10),r.status,r.practice)
# team first TD / first score
print("P(first TD by SF)",None)
# team-level reasoning data
for t in ("DEN","SF"):
    P_=TEAM[t]; print(t,{k:round(v,3) for k,v in P_.items() if isinstance(v,(int,float,np.floating))})
print(INJ[INJ.team.isin(["DEN","SF"])][["team","player","pos","injury","practice","game_status","p_active"]].to_string())
print(L)
