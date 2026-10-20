import re, numpy as np, pandas as pd, slate_full as SF, tnf_full as T
from load import norm_name
S='/tmp/claude-0/-home-user/265c050e-5259-56cf-a35f-3f6e5f40d8fe/scratchpad/'
exec(open(S+"grade_picks.py").read().split("SRC=")[0])   # reuse act, actual, tds helpers
SF.BACKUP_QBS={"Jalon Daniels","Tanner McKee","Tyler Huntley"}
def eval_leg(nm):
    nm=nm.split(": ",1)[1]
    m=re.match(r"^(.*) (rec_yds|rec|rush_yds|rush_att|pass_att|pass_cmp|pass_yds) ([OU])([\d.]+)$",nm)
    if m:
        a=actual(m.group(1),None,m.group(2)) if False else None
        c=byn(m.group(1)); 
        if c is None: return np.nan
        v=float(getattr(c,M[m.group(2)])); ln=float(m.group(4))
        return np.nan if v==ln else float((v>ln)==(m.group(3)=="O"))
    m=re.match(r"^(.*) anytime TD$",nm)
    if m:
        c=byn(m.group(1)); return 0.0 if c is None else float(c.rushing_tds+c.receiving_tds>=1)
    m=re.match(r"^(.*) pass TD (\d)\+$",nm)
    if m:
        c=byn(m.group(1)); return np.nan if c is None else float(c.passing_tds>=int(m.group(2)))
    return np.nan
byn_={}
for (kk,tt),rr in act.items(): byn_.setdefault(kk,[]).append(rr)
def byn(p):
    c=byn_.get(norm_name(p)); return c[0] if c and len(c)==1 else None
def build(srcs):
    pool=SF.Pool()
    for d,gl in srcs.items():
        SF.OUT=S+d
        for g in gl:
            a,h=g.split("@")
            try: mk,md,Sg,legs,meta,fav=SF._game_pool(a,h)
            except Exception: continue
            pool.add_game(g,legs,meta,fav)
    return pool
def run(pool,label):
    names=list(pool.leg)
    line=sorted([k for k in names if pool.leg[k]["kind"]=="line"],key=lambda k:-pool.leg[k]["shrunk"])[:16]
    qb=sorted([k for k in names if pool.leg[k]["kind"]=="qb1"],key=lambda k:-pool.leg[k]["p"])[:6]
    td=sorted([k for k in names if pool.leg[k]["kind"]=="td"],key=lambda k:-pool.leg[k]["p"])[:12]
    out=[]
    for n in (2,3,4):
        for title,pl,need in (("highest",line+qb,False),("TD-led",line[:10]+td+qb[:3],True)):
            for c,js,j in pool.search(pl,n,need_td=need,top=4):
                r=[eval_leg(x) for x in c]; hit=np.nan if any(np.isnan(r)) else float(all(x==1 for x in r)); 
                out.append(dict(slate=label,n=n,kind=title,hitp=js,hit=hit,legs=" + ".join(x.split(': ',1)[1] for x in c),res=r))
    return pd.DataFrame(out)
am=run(build({"sx7":["HOU@JAX","CHI@ATL","BAL@CLE","TEN@IND","NYJ@NE","NO@NYG","CAR@PHI","PIT@TB","ARI@LA","LAC@KC","BUF@LV","DAL@GB","WAS@SF"]}),"AM published")
pm=run(build({"sx8":["ARI@LA","LAC@KC","BUF@LV","DAL@GB"],"sx10":["WAS@SF"]}),"PM refresh")
D=pd.concat([am,pm]); D.to_pickle(S+"w6c/parlays_graded.pkl")
pd.set_option("display.width",250,"display.max_colwidth",150)
for lab,g in D.groupby("slate"):
    d=g.dropna(subset=["hit"]); print(lab,"tickets",len(d),"hit",int(d.hit.sum()),f"expected {d.hitp.sum():.1f}")
    print(d.groupby(["n","kind"]).agg(t=("hit","size"),hits=("hit","sum"),exp=("hitp","sum")).round(2).to_string())
print(D[(D.slate=="AM published")&(D.hit==1)][["n","kind","legs"]].to_string())
print(D[(D.slate=="PM refresh")&(D.hit==1)][["n","kind","legs"]].to_string())
# leg-level: which legs failed most
from collections import Counter
c=Counter()
for r in D.itertuples():
    for l,x in zip(r.legs.split(" + "),r.res):
        if x==0: c[l]+=1
print(c.most_common(8))
