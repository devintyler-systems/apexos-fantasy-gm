from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, run_all as R
from params import *
for _, r in SCHED.iterrows(): R.run_game(r.away, r.home, neutral=is_neutral(r.away, r.home))
S=R.STORE; fails=[]
rows=[]
for (a,h),d in S.items():
    for t,s in ((a,d["A"]),(h,d["H"])):
        pls=d["players"][t]
        # reconcile pass yards: QB yards == team yds
        qb=[p for p in pls if p["pos"]=="QB" and p["p_active"]>=.5][0]
        rec_sum=sum(p["rec_yds"] for p in pls if p["pos"]!="QB")
        # receivers' yards vs team (other bucket excluded): ratio
        ratio=float(rec_sum.mean()/s["team_pass_yds"].mean())
        anyp=0.0; rtd=0.0
        for p in pls:
            if p["pos"]=="QB": continue
            m=p["mask"]
            if m.sum()>0: anyp+=float(((p["rush_td"]+p["rec_td"])>=1)[m].mean()*p["p_active"])
        td_mean=float(s["td"].mean())
        # QB1 vs WR1 yards correlation
        wr=max([p for p in pls if p["pos"] in("WR","TE")],key=lambda p:p["rec_yds"].mean())
        m=qb["mask"]&wr["mask"]
        corr=float(np.corrcoef(qb["pass_yds"][m],wr["rec_yds"][m])[0,1])
        # pass att vs RB rush att negative relation (script)
        rb=max([p for p in pls if p["pos"]=="RB"],key=lambda p:p["rush_att"].mean())
        corr2=float(np.corrcoef(s["att"],rb["rush_att"])[0,1])
        corr3=float(np.corrcoef(s["pts"],qb["pass_yds"])[0,1])
        rows.append(dict(team=t,qb=qb["player"],qb_med_yds=float(np.median(qb["pass_yds"][qb["mask"]])),qb_max_p99=float(np.percentile(qb["pass_yds"],99)),
                         rb_med_car=float(np.median(rb["rush_att"][rb["mask"]])),rec_yds_ratio=ratio,sum_anytime_p=anyp,team_off_td=td_mean,ratio_anytime=anyp/td_mean,
                         corr_qb_wr1=corr,corr_att_rbatt=corr2,corr_pts_qbyds=corr3,
                         plays=float(s["plays"].mean()),pts=float(s["pts"].mean())))
Q=pd.DataFrame(rows); pd.set_option("display.width",250)
print(Q.round(2).to_string())
print("QB med yds max",Q.qb_med_yds.max(),"RB med car max",Q.rb_med_car.max())
print("rec yds ratio range",Q.rec_yds_ratio.min().round(3),Q.rec_yds_ratio.max().round(3))
print("anytime TD sum ratio mean",Q.ratio_anytime.mean().round(3),Q.ratio_anytime.min().round(3),Q.ratio_anytime.max().round(3))
print("corr qb-wr1",Q.corr_qb_wr1.mean().round(2),"corr att-rbatt",Q.corr_att_rbatt.mean().round(2),"corr pts-qbyds",Q.corr_pts_qbyds.mean().round(2))
# league totals vs observed
print("mean pts/team",Q.pts.mean().round(2),"L ppg",round(L["ppg"],2))
Q.to_csv(OUT+"qa_reconcile.csv",index=False)
# injury check: OUT players have zero volume
rk=pd.DataFrame(R.rank_rows)
out=rk[rk.p_active==0]; print(out[["player","pos","team","injury","ev_pts"]].to_string())
# market benchmark (QA only)
