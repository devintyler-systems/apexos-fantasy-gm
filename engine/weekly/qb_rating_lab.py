"""QB-aware and rest-aware game-margin adjustment on top of the model-only ridge ratings (DECISIONS #58 candidate; NOT in the production path).

Usage: python qb_rating_lab.py   (reads APEX_NFLV; weeks 4-12 of 2023-25 through team_rating_lab.evaluate, 393 games)
Idea: the ridge rating of a team is built from games started by whichever quarterbacks played them. When the quarterback starting NOW differs from the one who produced those games, the rating is stale.
adj = beta * (shrunk EPA/dropback of the starter now - dropback-weighted shrunk EPA/dropback of the quarterbacks behind the team's rated games), added to the model margin (home minus away).
Quarterback ratings use only games before the target week (3 seasons of memory, shrink constant 150 dropbacks toward 0). Also scans a rest-day term. Compared against the betting line with the same
margin MAE / blend-weight reading as game_bt.py.
"""
import sys
import numpy as np, pandas as pd
import team_rating_lab as L
from paths import NFLV as N
g=L.g
print([c for c in g.columns if 'qb' in c or 'rest' in c])
# QB EPA per dropback by game (qb id), all seasons
rows=[]
for s in (2022,2023,2024,2025,2026):
    try: p=pd.read_parquet(N+f"play_by_play_{s}.parquet",columns=["game_id","week","season","season_type","posteam","passer_player_id","qb_dropback","epa"])
    except Exception as e: print("skip",s,e); continue
    p=p[(p.season_type=="REG")&(p.qb_dropback==1)&p.epa.notna()&p.passer_player_id.notna()]
    x=p.groupby(["season","week","posteam","passer_player_id"]).epa.agg(["sum","count"]).reset_index(); rows.append(x)
Q=pd.concat(rows); Q["posteam"]=Q.posteam.replace(L.TM)
def qb_rating(qid,season,week,k=150):
    # shrunk EPA/dropback from all games before (season,week), 3-year memory
    m=Q[(Q.passer_player_id==qid)&((Q.season<season)|((Q.season==season)&(Q.week<week)))]
    return (m["sum"].sum())/(m["count"].sum()+k)   # shrink toward 0 (league avg ~0)
gg=g[g.home_score.notna()].copy()
def starter(r,side):
    return r.home_qb_id if side=="h" else r.away_qb_id
def team_hist_qb(team,season,week,k=150):
    # dropback-weighted avg rating of QBs who generated this team's games used by the ridge (this season before week; else prior season)
    m=Q[(Q.posteam==team)&(Q.season==season)&(Q.week<week)]
    if m["count"].sum()<30: m=Q[(Q.posteam==team)&(Q.season==season-1)]
    if m.empty: return 0.0
    w=m["count"].values; r=np.array([qb_rating(q,season,week,k) for q in m.passer_player_id])
    return float((w*r).sum()/w.sum())
base=L.evaluate("baseline")
base=base.reset_index(drop=True)
# attach QB deltas in same row order as predict(): per season, week, games in g order with home_score notna
recs=[]
for s in (2023,2024,2025):
    for w in range(4,13):
        for r in gg[(gg.season==s)&(gg.week==w)].itertuples():
            hq,aq=r.home_qb_id,r.away_qb_id
            dh=qb_rating(hq,s,w)-team_hist_qb(r.home_team,s,w) if isinstance(hq,str) else 0.0
            da=qb_rating(aq,s,w)-team_hist_qb(r.away_team,s,w) if isinstance(aq,str) else 0.0
            recs.append((dh,da,r.home_rest,r.away_rest))
R=pd.DataFrame(recs,columns=["dh","da","rh","ra"]); assert len(R)==len(base),(len(R),len(base))
am=base.hs-base.as_; at=base.hs+base.as_; mm=base.hp-base.ap; mt=base.hp+base.ap
print("QB change games (|d|>0.05):",int(((R.dh.abs()>.05)|(R.da.abs()>.05)).sum()),"of",len(R))
# EPA/dropback -> points: ~ dropbacks(35)*EPA ; scan beta
for beta in (0,10,20,30,40,60):
    adj=beta*(R.dh-R.da)
    per=" ".join(f"{s}:{(mm[base.season==s]+adj[base.season==s]-am[base.season==s]).abs().mean():.3f}" for s in (2023,2024,2025))
    print(f"beta {beta:3d} margin MAE {(mm+adj-am).abs().mean():.3f} winner {(((mm+adj)>0)==(am>0)).mean():.3f} | {per}")
# total effect: both qbs
for bt in (0,5,10,20):
    adj=bt*(R.dh+R.da); print(f"total beta {bt} MAE {(mt+adj-at).abs().mean():.3f}")
# rest
for b in (0,0.2,0.4,0.6):
    adj=b*(R.rh-R.ra).clip(-4,4); print(f"rest beta {b} margin MAE {(mm+adj-am).abs().mean():.3f}")
# does the line-minus-model margin gap relate to qb delta (fit)
gap=base.sl*-1 - mm  # line home margin = -spread_line? check sign
print("corr(spread_line, mm)",np.corrcoef(base.sl,mm)[0,1])
print("---- extra")
adj=20*(R.dh-R.da)+0.3*(R.rh-R.ra).clip(-4,4); m2=mm+adj
for nm,m in (("base",mm),("qb20",mm+20*(R.dh-R.da)),("qb20+rest",m2)):
    best=min((float(np.abs(w*m+(1-w)*(base.sl)-am).mean()),round(float(w),1)) for w in np.arange(0,1.01,.1))
    sl=np.polyfit(m,am,1)[0]; print(nm,"MAE",round(float(np.abs(m-am).mean()),3),"blend(model,line)",best,"slope actual~model",round(sl,2),"slope actual~line",round(np.polyfit(base.sl,am,1)[0],2))
print("sd model margin",mm.std(),"sd line",base.sl.std(),"sd actual",am.std())
for sc in (1.0,1.1,1.2,1.3):
    m=(mm+20*(R.dh-R.da))*sc; print("scale",sc,"MAE",round(float(np.abs(m-am).mean()),3),"per",[round(float(np.abs(m-am)[base.season==s].mean()),3) for s in (2023,2024,2025)])
