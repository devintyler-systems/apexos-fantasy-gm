from paths import OUT, NFLV, DELIV, CONF
import os
"""Model-only Week 4 projections (no lines): QB cmp/yds/TD, RB rush+rec yds + TDs, WR/TE rec yds/rec/TDs, anytime TD lists. Confidence 1-100."""
import numpy as np, pandas as pd
import run_all as R
from params import SCHED, INJ, norm_name, is_neutral
O=DELIV
rows=[]
def st(x,m):
    v=x[m]; mu=float(v.mean()); sd=float(v.std())
    return dict(mean=mu,p25=float(np.percentile(v,25)),p50=float(np.percentile(v,50)),p75=float(np.percentile(v,75)),cv=(sd/mu if mu>1e-9 else 9.0))
def conf(s, sample, env, avail):
    """Reliability 1-100: availability x (60% tightness of the middle-50% range relative to the projection + 40% sample/role stability)."""
    rel=(s["p75"]-s["p25"])/(2*max(s["mean"],1e-6))
    pred=max(0.0,1-rel)
    c=100*avail*(0.60*pred+0.40*min(1.0,sample*env))
    return int(np.clip(round(c),1,97))
for _,g in SCHED.iterrows():
    a,h=g.away,g.home
    R.run_game(a,h,neutral=is_neutral(a, h),ns=20000)
    d=R.STORE.pop((a,h)); played=(a,h) in R.PLAYED
    for t in (a,h):
        sd=d["A"] if t==a else d["H"]; opp=h if t==a else a
        pstart=float(sd["p_start"]); env=0.85+0.15*pstart
        for pl in d["players"][t]:
            m=pl["mask"]
            if m.sum()<500 or pl["p_active"]<0.03: continue
            r=pl["row"]; G=float(getattr(r,"G",3) or 3) if r is not None and not isinstance(r,float) else 3.0
            gf=0.5+0.5*min(G,3)/3
            base=dict(player=pl["player"],pos=pl["pos"],team=t,opp=opp,game=f"{a}@{h}",played=played,p_active=pl["p_active"],
                      status=("; ".join(x for x in [str(pl.get("status")) if isinstance(pl.get("status"),str) else "", {"DNP":"DNP","LP":"Limited","FP":"Full"}.get(pl.get("practice"),"")] if x) or ""),proxy=bool(pl.get("proxy")))
            tdc=pl["rush_td"]+pl["rec_td"]
            tdst=st(tdc,m); p_any=float((tdc[m]>=1).mean())
            if pl["pos"]=="QB":
                att=float(getattr(r,"Att",0) or 0) if r is not None and not isinstance(r,float) else 0
                sample=min(1,att/90)*gf if not base["proxy"] else 0.15
                rec={}
                for k in ("pass_cmp","pass_yds","pass_td"):
                    s=st(pl[k],m); rec.update({f"{k}_mean":s["mean"],f"{k}_p25":s["p25"],f"{k}_p75":s["p75"],f"{k}_conf":conf(s,sample,1.0,pl["p_active"])})
                rows.append(dict(base,**rec,rush_td_mean=tdst["mean"],any_td_pct=p_any,exp_td=tdst["mean"],td_conf=int(np.clip(round(88*pl["p_active"]*(0.5*min(1.0,sample)+0.5*0.4)),1,85))))
            else:
                tg=float(r.Receiving_Tgt); ca=float(r.Rushing_Att)
                if pl["pos"]=="RB": sample=min(1,(ca+2*tg)/60)*gf
                else: sample=min(1,tg/25)*gf
                rec={}
                for k in ("rush_yds","rec_yds","rec"):
                    s=st(pl[k],m); rec.update({f"{k}_mean":s["mean"],f"{k}_p25":s["p25"],f"{k}_p75":s["p75"],f"{k}_conf":conf(s,sample,env,pl["p_active"])})
                rows.append(dict(base,**rec,rush_td_mean=float(pl["rush_td"][m].mean()),rec_td_mean=float(pl["rec_td"][m].mean()),any_td_pct=p_any,exp_td=tdst["mean"],td_conf=int(np.clip(round(88*pl["p_active"]*(0.5*min(1.0,sample*env)+0.5*min(1.0,float(r.rz_tgt+r.rz_car)/8.0))),1,85)),
                                 rush_att_mean=float(pl["rush_att"][m].mean()),tgt_mean=float(pl["tgt"][m].mean()),car_sh=float(r.car_sh),tgt_sh=float(r.tgt_sh)))
P=pd.DataFrame(rows); P["any_td_pct_wt"]=P.any_td_pct*P.p_active
P.to_pickle(OUT+"proj_all.pkl"); print(len(P))
