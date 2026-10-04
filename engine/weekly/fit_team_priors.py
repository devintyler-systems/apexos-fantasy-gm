"""Fit team-strength shrinkage + prior retention on 2016-2025 NFL results; fit market blend weight. Opponent-adjusted ridge."""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, itertools, json
N=NFLV
NV2T={"LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV","OAK":"LV","SD":"LAC","STL":"LA"}
g=pd.read_parquet(N+"games.parquet"); g=g[(g.game_type=="REG")&(g.season>=2015)&(g.season<=2025)&g.home_score.notna()].copy()
for c in ("home_team","away_team"): g[c]=g[c].replace(NV2T)
teams=sorted(set(g.home_team)|set(g.away_team)); ti={t:i for i,t in enumerate(teams)}; T=len(teams)
g["h"]=g.home_team.map(ti); g["a"]=g.away_team.map(ti)
prev={}   # season -> (pf per game, pa per game, mean pts) for each team
for s,x in g.groupby("season"):
    pf=np.zeros(T); pa=np.zeros(T); n=np.zeros(T)
    for r in x.itertuples():
        pf[r.h]+=r.home_score; pa[r.h]+=r.away_score; n[r.h]+=1; pf[r.a]+=r.away_score; pa[r.a]+=r.home_score; n[r.a]+=1
    ok=n>0; prev[s]=(np.where(ok,pf/np.maximum(n,1),np.nan),np.where(ok,pa/np.maximum(n,1),np.nan),np.nanmean(np.r_[x.home_score,x.away_score]))
def mkt(r):
    if np.isnan(r.spread_line) or np.isnan(r.total_line): return (np.nan,np.nan)
    return ((r.total_line+r.spread_line)/2,(r.total_line-r.spread_line)/2)
g[["mk_h","mk_a"]]=[mkt(r) for r in g.itertuples()]
def predict_week(s,w,lo,ld,ro,rd,hfa=1.0):
    """ratings from games before week w of season s (+ prior season), returns arrays for week-w games"""
    past=g[(g.season==s)&(g.week<w)]; cur=g[(g.season==s)&(g.week==w)]
    if s-1 not in prev or len(cur)==0: return None
    pf0,pa0,mu0=prev[s-1]; pf0=np.where(np.isnan(pf0),mu0,pf0); pa0=np.where(np.isnan(pa0),mu0,pa0)
    mu=np.mean(np.r_[past.home_score,past.away_score]) if len(past)>=16 else mu0
    o0=ro*(pf0-mu0); d0=rd*(pa0-mu0)
    rows=len(past)*2; A=np.zeros((rows,2*T)); y=np.zeros(rows); k=0
    for r in past.itertuples():
        A[k,r.h]=1; A[k,T+r.a]=1; y[k]=r.home_score-mu-hfa; k+=1
        A[k,r.a]=1; A[k,T+r.h]=1; y[k]=r.away_score-mu+hfa; k+=1
    lam=np.r_[np.full(T,lo),np.full(T,ld)]; x0=np.r_[o0,d0]
    x=np.linalg.solve(A.T@A+np.diag(lam),A.T@y+lam*x0)
    o,d=x[:T],x[T:]
    return (mu+hfa+o[cur.h.values]+d[cur.a.values], mu-hfa+o[cur.a.values]+d[cur.h.values], cur)
def baseline_v3(s,w,k=5.0,ro=.45,rd=.35,hfa=1.0):
    """current production method: raw per-game PF/PA shrunk toward regressed prior, no opponent adjustment"""
    past=g[(g.season==s)&(g.week<w)]; cur=g[(g.season==s)&(g.week==w)]
    if s-1 not in prev or len(cur)==0: return None
    pf0,pa0,mu0=prev[s-1]; pf0=np.where(np.isnan(pf0),mu0,pf0); pa0=np.where(np.isnan(pa0),mu0,pa0)
    mu=np.mean(np.r_[past.home_score,past.away_score]) if len(past)>=16 else mu0
    pf=np.zeros(T); pa=np.zeros(T); n=np.zeros(T)
    for r in past.itertuples():
        pf[r.h]+=r.home_score; pa[r.h]+=r.away_score; n[r.h]+=1; pf[r.a]+=r.away_score; pa[r.a]+=r.home_score; n[r.a]+=1
    n1=np.maximum(n,1); po=mu+ro*(pf0-mu0); pdd=mu+rd*(pa0-mu0)
    off=(pf/n1*n+po*k)/(n+k); de=(pa/n1*n+pdd*k)/(n+k)
    return (mu+(off[cur.h.values]-mu)+(de[cur.a.values]-mu)+hfa, mu+(off[cur.a.values]-mu)+(de[cur.h.values]-mu)-hfa, cur)
def score(fn,seasons,weeks,**kw):
    se=[];sm=[];st=[]
    for s in seasons:
        for w in weeks:
            r=fn(s,w,**kw)
            if r is None: continue
            ph,pa_,cur=r; yh,ya=cur.home_score.values,cur.away_score.values
            se+=list((ph-yh)**2)+list((pa_-ya)**2); sm+=list(((ph-pa_)-(yh-ya))**2); st+=list(((ph+pa_)-(yh+ya))**2)
    return np.sqrt(np.mean(se)),np.sqrt(np.mean(sm)),np.sqrt(np.mean(st))
TRAIN=range(2016,2023); TEST=range(2023,2026); WK=range(4,19)
print("== baselines (weeks 4-18) ==")
for nm,ss in (("train 2016-22",TRAIN),("test 2023-25",TEST)):
    print(nm,"v3 method  RMSE pts/margin/total: %.3f %.3f %.3f"%score(baseline_v3,ss,WK))
best=None; res=[]
for lo,ld,ro,rd in itertools.product([2,4,8,16,32],[2,4,8,16,32],[0,.2,.4,.6],[0,.1,.25,.4]):
    e=score(predict_week,TRAIN,WK,lo=lo,ld=ld,ro=ro,rd=rd)[0]; res.append((e,lo,ld,ro,rd))
res.sort(); print("\n== top ridge configs on TRAIN (RMSE pts) =="); [print("%.4f lo=%s ld=%s ret_off=%s ret_def=%s"%r) for r in res[:5]]
e,lo,ld,ro,rd=res[0]
print("\nFITTED ridge  test 2023-25 RMSE pts/margin/total: %.3f %.3f %.3f"%score(predict_week,TEST,WK,lo=lo,ld=ld,ro=ro,rd=rd))
print("week-4 only, test seasons: v3 %.3f/%.3f/%.3f  fitted %.3f/%.3f/%.3f"%(*score(baseline_v3,TEST,[4]),*score(predict_week,TEST,[4],lo=lo,ld=ld,ro=ro,rd=rd)))
print("week 4-6, all seasons 2016-25: v3 %.3f  fitted %.3f"%(score(baseline_v3,range(2016,2026),range(4,7))[0],score(predict_week,range(2016,2026),range(4,7),lo=lo,ld=ld,ro=ro,rd=rd)[0]))
# market + blend
def mk_eval(seasons,weeks,w_blend=None,**kw):
    ys=[];mm=[];md=[]
    for s in seasons:
        for wk in weeks:
            r=predict_week(s,wk,**kw)
            if r is None: continue
            ph,pa_,cur=r
            ok=cur.mk_h.notna().values
            ys+=list(np.r_[cur.home_score.values[ok],cur.away_score.values[ok]]); mm+=list(np.r_[cur.mk_h.values[ok],cur.mk_a.values[ok]]); md+=list(np.r_[ph[ok],pa_[ok]])
    return np.array(ys),np.array(mm),np.array(md)
y,m,d=mk_eval(TRAIN,WK,lo=lo,ld=ld,ro=ro,rd=rd)
print("\n== market vs model, TRAIN weeks 4-18, n=%d team-games =="%len(y)); print("market RMSE %.3f  ratings RMSE %.3f"%(np.sqrt(np.mean((y-m)**2)),np.sqrt(np.mean((y-d)**2))))
ws=np.linspace(0,1,21); mse=[np.mean((y-(w*m+(1-w)*d))**2) for w in ws]; wb=float(ws[int(np.argmin(mse))]); print("best market weight w=%.2f  blended RMSE %.3f"%(wb,np.sqrt(min(mse))))
y2,m2,d2=mk_eval(TEST,WK,lo=lo,ld=ld,ro=ro,rd=rd); print("TEST 2023-25: market %.3f ratings %.3f blend(w=%.2f) %.3f"%(np.sqrt(np.mean((y2-m2)**2)),np.sqrt(np.mean((y2-d2)**2)),wb,np.sqrt(np.mean((y2-(wb*m2+(1-wb)*d2))**2))))
y3,m3,d3=mk_eval(range(2016,2026),[4],lo=lo,ld=ld,ro=ro,rd=rd); print("week 4 only all seasons: market %.3f ratings %.3f blend %.3f (n=%d)"%(np.sqrt(np.mean((y3-m3)**2)),np.sqrt(np.mean((y3-d3)**2)),np.sqrt(np.mean((y3-(wb*m3+(1-wb)*d3))**2)),len(y3)))
json.dump(dict(lo=lo,ld=ld,ret_off=ro,ret_def=rd,hfa=1.0,market_weight=wb),open(CONF+"team_prior_fit.json","w"),indent=1); print("saved team_prior_fit.json")
