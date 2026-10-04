from paths import OUT, NFLV, DELIV, CONF
import os
"""DK Classic lineup builder: pool from sims, ILP (PuLP/CBC), cash + stack + GPP set, evaluated on correlated scenarios. usage: python3 dfs_classic.py <market|model>"""
import sys, pickle, numpy as np, pandas as pd, pulp, warnings; warnings.filterwarnings("ignore")
from load import norm_name
MODE=sys.argv[1] if len(sys.argv)>1 else "market"
O=OUT; D=DELIV
sims,meta=pickle.load(open(O+f"dfs_sims_{MODE}.pkl","rb"))
sal=pd.read_csv(os.environ["APEX_DK_SALARIES"],encoding="utf-8-sig")   # input file, never committed
TM={"LAR":"LA","JAC":"JAX","WSH":"WAS"}; sal["team"]=sal.TeamAbbrev.replace(TM); sal["nkey"]=sal.Name.map(norm_name)
byname={(k[0],k[1]):k for k in sims if k[0]!="DST"}
rows=[];unm=[]
for r in sal.itertuples():
    if r.Position=="DST": key=("DST",r.team,"DST")
    else: key=byname.get((r.nkey,r.team))
    if key is None or key not in sims: unm.append((r.Name,r.Position,r.team,r.Salary,r.AvgPointsPerGame,r.Status)); continue
    a=sims[key]; m=meta[key]
    rows.append(dict(key=key,player=r.Name,pos=r.Position,team=r.team,game=m["game"],salary=int(r.Salary),dk_status=r.Status if isinstance(r.Status,str) else "",avg_dk=r.AvgPointsPerGame,p_active=m["p_active"],
                     mean=float(a.mean()),sd=float(a.std()),p25=float(np.percentile(a,25)),p50=float(np.percentile(a,50)),p75=float(np.percentile(a,75)),p90=float(np.percentile(a,90)),p95=float(np.percentile(a,95))))
P=pd.DataFrame(rows); P["opp"]=[g.split("@")[1] if g.split("@")[0]==t else g.split("@")[0] for g,t in zip(P.game,P.team)]
P["value_per_1k"]=P["mean"]/P.salary*1000
pool=P[(~P.dk_status.isin(["OUT","IR"]))&(P.p_active>=0.5)&(P.salary>=2000)&(P["mean"]>=0.5)].reset_index(drop=True)
REPORT=[]
def rep(*a): REPORT.append(" ".join(str(x) for x in a))   # lineup/salary detail goes to a report file, never stdout
print("DK rows",len(sal),"matched",len(P),"pool",len(pool)); um=pd.DataFrame(unm,columns=["name","pos","team","salary","avg_dk","status"]); um=um[(~um.status.isin(["OUT","IR"]))&(um.salary>=3000)]
rep("unmatched with salary>=3000 and not OUT/IR:",len(um)); rep(um.sort_values("salary",ascending=False).head(12).to_string(index=False))
P.drop(columns=["key"]).round(3).to_csv(D+f"dfs_classic_pool_{MODE}.csv",index=False); um.to_csv(D+f"dfs_classic_unmatched_{MODE}.csv",index=False)
# scenario matrix: same sim index within a game, independent across games
rng=np.random.default_rng(7); S=6000; NSIM=len(next(iter(sims.values()))); gi={g:rng.permutation(NSIM)[:S] for g in pool.game.unique()}
SC=np.stack([sims[k][gi[g]] for k,g in zip(pool.key,pool.game)],axis=1)   # S x players
CAP=50000
def solve(w,stack=False,bring=False,banned=(),prev=(),mindiff=3):
    pr=pulp.LpProblem("l",pulp.LpMaximize); x=[pulp.LpVariable(f"x{i}",cat="Binary") for i in range(len(pool))]
    pr+=pulp.lpSum(w[i]*x[i] for i in range(len(pool))); pr+=pulp.lpSum(int(pool.salary[i])*x[i] for i in range(len(pool)))<=CAP
    idx=lambda pos:[i for i in range(len(pool)) if pool.pos[i]==pos]
    pr+=pulp.lpSum(x[i] for i in idx("QB"))==1; pr+=pulp.lpSum(x[i] for i in idx("DST"))==1
    pr+=pulp.lpSum(x[i] for i in idx("RB"))>=2; pr+=pulp.lpSum(x[i] for i in idx("RB"))<=3
    pr+=pulp.lpSum(x[i] for i in idx("WR"))>=3; pr+=pulp.lpSum(x[i] for i in idx("WR"))<=4
    pr+=pulp.lpSum(x[i] for i in idx("TE"))>=1; pr+=pulp.lpSum(x[i] for i in idx("TE"))<=2
    pr+=pulp.lpSum(x[i] for i in idx("RB")+idx("WR")+idx("TE"))==7
    for q in idx("QB"):
        t=pool.team[q]; o=pool.opp[q]
        if stack: pr+=pulp.lpSum(x[j] for j in idx("WR")+idx("TE") if pool.team[j]==t)>=x[q]
        if bring: pr+=pulp.lpSum(x[j] for j in idx("WR")+idx("TE")+idx("RB") if pool.team[j]==o)>=x[q]
        for d in idx("DST"):
            if pool.team[d]==o: pr+=x[q]+x[d]<=1       # no DST facing your own QB
    for i in banned: pr+=x[i]==0
    for L in prev: pr+=pulp.lpSum(x[i] for i in L)<=9-mindiff
    pr.solve(pulp.PULP_CBC_CMD(msg=0,timeLimit=8))
    if pulp.LpStatus[pr.status]!="Optimal": return None
    return [i for i in range(len(pool)) if x[i].value()>0.5]
def describe(L):
    s=SC[:,L].sum(axis=1); sd=pool.loc[L]
    return dict(salary=int(sd.salary.sum()),remaining=CAP-int(sd.salary.sum()),mean=float(s.mean()),p25=float(np.percentile(s,25)),p50=float(np.percentile(s,50)),p75=float(np.percentile(s,75)),p90=float(np.percentile(s,90)),p95=float(np.percentile(s,95)),
                players=" | ".join(f"{sd.pos[i] if False else pool.pos[i]} {pool.player[i]} ({pool.team[i]}) ${pool.salary[i]}" for i in sorted(L,key=lambda i:["QB","RB","WR","TE","DST"].index(pool.pos[i]))),
                stack=("QB+"+"/".join(sorted({pool.player[i].split()[-1] for i in L if pool.pos[i] in("WR","TE") and pool.team[i]==pool.team[[j for j in L if pool.pos[j]=="QB"][0]]}))) )
# 1) cash: max mean
cash=solve(pool["mean"].values); rep("CASH",{k:v for k,v in describe(cash).items() if k in ("mean","p50","p90","p95","stack")})   # lineup detail goes to the CSVs, not stdout
# 2) best stack lineups by game (QB + pass catcher + bring-back), mean objective
stk=[]
for g in pool.game.unique():
    w=pool["mean"].values.copy(); ban=[i for i in range(len(pool)) if pool.pos[i]=="QB" and pool.game[i]!=g]
    L=solve(w,stack=True,bring=True,banned=ban)
    if L: stk.append((g,L))
stk=sorted(stk,key=lambda z:-SC[:,z[1]].sum(axis=1).mean())[:4]
# 3) GPP set: noisy mean+0.5sd objective with stack (+bring-back half the time), uniqueness, exposure cap
# sequential GPP build: 20 lineups, each player capped at 40% exposure, stack required, bring-back alternating, uniqueness vs all previous
chosen=[]; cnt={}; rng2=np.random.default_rng(11); NL=20; CAPN=int(0.4*NL)
for k in range(NL):
    ban=[i for i,c in cnt.items() if c>=CAPN]
    w=pool["mean"].values+0.4*pool.sd.values+rng2.normal(0,0.30,len(pool))*pool.sd.values
    Lx=solve(w,stack=True,bring=(k%2==0),banned=ban,prev=[c[0] for c in chosen],mindiff=2)
    if Lx is None: Lx=solve(w,stack=True,bring=False,banned=ban,prev=[c[0] for c in chosen],mindiff=1)
    if Lx is None: break
    chosen.append((Lx,describe(Lx)))
    for i in Lx: cnt[i]=cnt.get(i,0)+1
chosen=sorted(chosen,key=lambda z:-z[1]["mean"])
rowsout=[]
for n,(L,d) in enumerate(chosen,1): rowsout.append(dict(lineup=n,**d))
pd.DataFrame(rowsout).round(2).to_csv(D+f"dfs_classic_gpp_lineups_{MODE}.csv",index=False)
cs=describe(cash); pd.DataFrame([dict(type="cash (max mean)",**cs)]+[dict(type=f"stack {g}",**describe(L)) for g,L in stk]).round(2).to_csv(D+f"dfs_classic_cash_and_stacks_{MODE}.csv",index=False)
expo=pd.Series({pool.player[i]:c/len(chosen) for i,c in cnt.items()}).sort_values(ascending=False); expo.round(2).to_csv(D+f"dfs_classic_gpp_exposure_{MODE}.csv",header=["exposure"])
rep("\nGPP set:",len(chosen),"lineups; mean of means %.1f, mean P95 %.1f; max exposure %.2f"%(np.mean([d['mean'] for _,d in chosen]),np.mean([d['p95'] for _,d in chosen]),expo.max()))
rep(expo.head(10).round(2).to_dict())
for g,L in stk[:2]: rep("STACK",g,{k:(round(v,1) if isinstance(v,float) else v) for k,v in describe(L).items() if k in("mean","p90","stack")})
# value plays
med=pool.groupby("pos").value_per_1k.median().to_dict(); v=pool[(pool.pos!="DST")&(pool.salary<=6500)].sort_values("value_per_1k",ascending=False).head(12); rep("\nVALUE (pts per $1k, slate median by pos %s)"%{k:round(x,2) for k,x in med.items()}); rep(v[["player","pos","team","salary","mean","value_per_1k"]].round(2).to_string(index=False))
rep("\nTOP of pool by mean:"); rep(pool.sort_values("mean",ascending=False).head(14)[["player","pos","team","salary","mean","p90","dk_status"]].round(1).to_string(index=False))
open(D+f"dfs_classic_report_{MODE}.txt","w").write("\n".join(REPORT)); print("report written:",len(REPORT),"sections")
