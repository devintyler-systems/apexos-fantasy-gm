"""Team-rating lab: re-implements the model-only ridge team ratings (params.ridge_ratings) outside the sim and scores candidate changes at the game level against the betting line.
Usage: python team_rating_lab.py   (reads APEX_NFLV; weeks 4-12 of 2023-25). Candidates: EPA-blended target (w_epa, kind all|clean), recency weights, ridge penalties, retention, HFA. DECISIONS #49.
"""
import pandas as pd,numpy as np,sys,json
from paths import NFLV as N
g=pd.read_parquet(N+"games.parquet"); g=g[(g.game_type=="REG")&g.season.isin([2022,2023,2024,2025,2026])]
TM={"OAK":"LV","SD":"LAC","STL":"LA","LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV"}
for c in("home_team","away_team"): g[c]=g[c].replace(TM)
print(sorted(g.season.unique()))
# EPA per team-game
E={}
for s in (2023,2024,2025,2026):
    p=pd.read_parquet(N+f"play_by_play_{s}.parquet",columns=["game_id","week","posteam","defteam","epa","wp","season_type","pass","rush","play_type"]); p=p[(p.season_type=="REG")&p.epa.notna()&p.posteam.notna()]
    p["posteam"]=p.posteam.replace(TM); p["defteam"]=p.defteam.replace(TM)
    p["ok"]=(p.wp>.05)&(p.wp<.95)
    a=p[(p["pass"]==1)|(p["rush"]==1)]
    for nm,m in(("all",a),("clean",a[a.ok])):
        x=m.groupby(["game_id","posteam","defteam"]).epa.agg(["sum","count"]).reset_index(); x["kind"]=nm; E.setdefault(s,[]).append(x)
EP={s:pd.concat(v) for s,v in E.items()}
cfg=json.load(open(__import__("paths").CONF+"team_prior_fit.json"))
def team_games(season,week_lt,w_epa,kind,recency):
    gg=g[(g.season==season)&(g.week<week_lt)]
    ep=EP[season]; ep=ep[ep.kind==kind].set_index(["game_id","posteam"])
    rows=[]
    for r in gg.itertuples():
        for t,o,pf,home in((r.home_team,r.away_team,r.home_score,1),(r.away_team,r.home_team,r.away_score,0)):
            e=ep["sum"].get((r.game_id,t),np.nan); n=ep["count"].get((r.game_id,t),np.nan)
            rows.append((t,o,pf,home,e,n,r.week))
    return pd.DataFrame(rows,columns=["team","opp","pf","home","epa","n","week"])
def ratings(season,week,w_epa=0.0,kind="clean",recency=0.0,lo=None,ld=None,ret=(None,None),hfa=None,epa_scale=1.0):
    cf=cfg; lo=lo or cf["lo"]; ld=ld or cf["ld"]; ro=ret[0] if ret[0] is not None else cf["ret_off"]; rd=ret[1] if ret[1] is not None else cf["ret_def"]; hfa=cf["hfa"] if hfa is None else hfa
    tg=team_games(season,week,w_epa,kind,recency)
    prev=g[(g.season==season-1)&g.home_score.notna()]
    rows=[(r.home_team,r.home_score,r.away_score) for r in prev.itertuples()]+[(r.away_team,r.away_score,r.home_score) for r in prev.itertuples()]
    pr=pd.DataFrame(rows,columns=["team","pf","pa"]).groupby("team").mean()
    ts=sorted(set(g[g.season==season].home_team)|set(g[g.season==season].away_team)); ix={t:i for i,t in enumerate(ts)}; T=len(ts)
    mu=tg.pf.mean()
    # epa -> points units: league mean epa per team-game maps to mu
    em=tg.epa.mean(); es=tg.epa.where(tg.epa.notna(), tg.pf-mu+em)   # missing epa falls back to points
    y_eff=mu+(es-em)*epa_scale
    y=(1-w_epa)*tg.pf+w_epa*y_eff
    A=np.zeros((len(tg),2*T)); yy=np.zeros(len(tg)); wts=np.ones(len(tg))
    for k,r in enumerate(tg.itertuples()):
        A[k,ix[r.team]]=1; A[k,T+ix[r.opp]]=1; yy[k]=y.iloc[k]-mu-(hfa if r.home else -hfa)
        if recency: wts[k]=np.exp(-recency*(week-1-r.week))
    mu0=pr.pf.mean(); o0=np.array([ro*(pr.pf.get(t,mu0)-mu0) for t in ts]); d0=np.array([rd*(pr.pa.get(t,mu0)-mu0) for t in ts])
    lam=np.r_[np.full(T,lo),np.full(T,ld)]; x0=np.r_[o0,d0]
    W=np.diag(wts) if recency else np.eye(len(tg))
    x=np.linalg.solve(A.T@W@A+np.diag(lam),A.T@W@yy+lam*x0)
    return {t:(mu+x[ix[t]],mu+x[T+ix[t]]) for t in ts},mu
def predict(season,week,**kw):
    R,mu=ratings(season,week,**kw); hfa=kw.get("hfa"); hfa=cfg["hfa"] if hfa is None else hfa
    out=[]
    for r in g[(g.season==season)&(g.week==week)&g.home_score.notna()].itertuples():
        H,A=R[r.home_team],R[r.away_team]
        h=0.0 if r.location=="Neutral" else hfa
        hp=mu+(H[0]-mu)+(A[1]-mu)+h; ap=mu+(A[0]-mu)+(H[1]-mu)-h
        out.append(dict(season=season,week=week,hp=hp,ap=ap,hs=r.home_score,as_=r.away_score,sl=r.spread_line,tl=r.total_line))
    return out
def evaluate(label,weeks=range(4,13),seasons=(2023,2024,2025),**kw):
    rows=[]
    for s in seasons:
        for w in weeks:
            try: rows+=predict(s,w,**kw)
            except Exception as ex: print("skip",s,w,ex); 
    d=pd.DataFrame(rows); am=d.hs-d.as_; at=d.hs+d.as_; mm=d.hp-d.ap; mt=d.hp+d.ap
    bl=lambda mod,ln,act:min((float(np.abs(w*mod+(1-w)*ln-act).mean()),round(float(w),1)) for w in np.arange(0,1.01,.1))
    bm,bt=bl(mm,d.sl,am),bl(mt,d.tl,at)
    per=" ".join(f"{s}:{(mm[d.season==s]-am[d.season==s]).abs().mean():.2f}" for s in seasons)
    print(f"{label:34s} n={len(d)} margin {np.abs(mm-am).mean():.3f} (line {np.abs(d.sl-am).mean():.3f}) total {np.abs(mt-at).mean():.3f} (line {np.abs(d.tl-at).mean():.3f}) blendw m{bm[1]} t{bt[1]} | {per}")
    return d
if __name__=="__main__":
    evaluate("baseline (points ridge)")
