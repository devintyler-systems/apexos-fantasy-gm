"""Price Week 4 model distributions against props_lines.csv (v2 edge logic). Re-runs the deterministic sims game by game."""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, datetime as dt
import run_all as R
from params import SCHED, norm_name
O=OUT
NOW=pd.Timestamp(dt.datetime.now(dt.timezone.utc)).tz_localize(None)
L=pd.read_csv(O+"props_lines.csv"); L["as_of"]=pd.to_datetime(L.as_of_utc).dt.tz_localize(None)
L["nkey"]=L.player.map(norm_name)
def imp(a): a=np.asarray(a,float); return np.where(a<0,-a/(-a+100),100/(a+100))
def payout(a): a=np.asarray(a,float); return np.where(a<0,100/(-a),a/100)
def amer(p):
    p=float(np.clip(p,1e-4,1-1e-4)); return int(round(-100*p/(1-p))) if p>=.5 else int(round(100*(1-p)/p))
fl=pd.read_csv(O+"w4_player_props_fair_lines.csv"); tdm=pd.read_csv(O+"w4_td_markets.csv")
conf={(r.player,r.team,r.market):r.confidence for r in fl.itertuples()}
conf.update({(r.player,r.team,r.market):r.confidence for r in tdm.itertuples()})
MKT={"pass_yds":lambda p:p["pass_yds"],"pass_tds":lambda p:p["pass_td"],"rec_yds":lambda p:p["rec_yds"],"rec":lambda p:p["rec"],"rush_yds":lambda p:p["rush_yds"],
     "rush_rec_yds":lambda p:p["rush_yds"]+p["rec_yds"]}
out=[]
for _,g in SCHED.iterrows():
    a,h=g.away,g.home
    R.run_game(a,h,neutral=is_neutral(a, h))
    d=R.STORE.pop((a,h)); gid=f"2026W04_{a}_{h}"
    Ttot=np.maximum(d["A"]["td"]+d["H"]["td"]+d["A"]["dtd"]+d["H"]["dtd"],1)
    pls={}
    for t in (a,h):
        for p in d["players"][t]: pls[(t,norm_name(p["player"]))]=p
    sub=L[L.game_id==gid]
    for (team,nk,mk),grp in sub.groupby(["team","nkey","market"]):
        pl=pls.get((team,nk))
        if pl is None or pl["p_active"]<0.03: continue
        m=pl["mask"]
        if m.sum()<200: continue
        player=grp.player.iloc[0]
        if mk in ("anytime_td","first_td"):
            tdc=(pl["rush_td"]+pl["rec_td"])
            pm=float((tdc[m]>=1).mean()) if mk=="anytime_td" else float((tdc[m]/Ttot[m]).mean())
            for _,r in grp.iterrows():
                nv=float(imp(r.odds_american))*0.90   # one-sided: flat 10% vig haircut (Estimated)
                out.append(dict(game=f"{a}@{h}",player=player,team=team,opp=r.opp,market=mk,side="yes",line=np.nan,is_alt=0,book=r.book,odds=r.odds_american,model_p=pm,
                                novig_p=nv,novig_method="Estimated (10% flat haircut)",edge=pm-nv,ev=pm*float(payout(r.odds_american))-(1-pm),as_of=r.as_of,p_active=pl["p_active"],played=(a,h) in R.PLAYED))
            continue
        x=MKT[mk](pl)[m]
        for (line,alt),lg in grp.groupby(["line","is_alt"]):
            po=float((x>line).mean()); pu=float((x<line).mean()); den=max(po+pu,1e-9)
            both={}
            for b,bg in lg.groupby("book"):
                o=bg[bg.side=="over"]; u=bg[bg.side=="under"]
                if len(o) and len(u):
                    io,iu=float(imp(o.odds_american.iloc[0])),float(imp(u.odds_american.iloc[0])); both[b]=io/(io+iu)
            for _,r in lg.iterrows():
                side=r.side
                pm=po/den if side=="over" else pu/den
                pm_raw=po if side=="over" else pu
                if r.book in both: nv=both[r.book] if side=="over" else 1-both[r.book]; meth="two-way no-vig"
                elif both: 
                    c=np.mean(list(both.values())); nv=c if side=="over" else 1-c; meth="two-way no-vig (other-book consensus)"
                else: nv=float(imp(r.odds_american))*0.90; meth="Estimated (10% flat haircut, one-sided)"
                out.append(dict(game=f"{a}@{h}",player=player,team=team,opp=r.opp,market=mk,side=side,line=line,is_alt=int(alt),book=r.book,odds=r.odds_american,model_p=pm,
                                novig_p=nv,novig_method=meth,edge=pm-nv,ev=pm_raw*float(payout(r.odds_american))-(pu if side=="over" else po),
                                as_of=r.as_of,p_active=pl["p_active"],played=(a,h) in R.PLAYED))
E=pd.DataFrame(out)
E["age_h"]=(NOW-E.as_of).dt.total_seconds()/3600; E["stale"]=E.age_h>6
E["confidence"]=[conf.get((p,t,m),"C") for p,t,m in zip(E.player,E.team,E.market)]
E.to_csv(O+"edges_all_rows.csv",index=False)
print("rows",len(E),"now",NOW,"max age h",E.age_h.max().round(2),"stale rows",int(E.stale.sum()))
