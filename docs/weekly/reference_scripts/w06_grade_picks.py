import os, sys, itertools, numpy as np, pandas as pd
import slate_full as SF, tnf_full as T
from load import norm_name
S='/tmp/claude-0/-home-user/265c050e-5259-56cf-a35f-3f6e5f40d8fe/scratchpad/'
N=S+'nflv/'
st=pd.read_parquet(N+'stats_player_week_2026.parquet'); st=st[st.week==6]
box=pd.read_csv(S+'w6c/mnf_box.csv')
cols=["player_display_name","team","completions","attempts","passing_yards","passing_tds","carries","rushing_yards","rushing_tds","receptions","targets","receiving_yards","receiving_tds"]
A=pd.concat([st[cols],box[[c for c in cols if c in box.columns]]],ignore_index=True).fillna(0)
A["k"]=A.player_display_name.map(norm_name)
A=A.groupby(["k","team"],as_index=False).sum(numeric_only=True)
act={(r.k,r.team):r for r in A.itertuples()}
M={"rec":"receptions","rec_yds":"receiving_yards","rush_yds":"rushing_yards","rush_att":"carries","pass_att":"attempts","pass_cmp":"completions","pass_yds":"passing_yards"}
def actual(player,team,market):
    r=act.get((norm_name(player),team))
    if r is None: return np.nan   # did not appear in box = DNP (treated as void below)
    return float(getattr(r,M[market]))
byname={}
for (kk,tt),rr in act.items(): byname.setdefault(kk,[]).append(rr)
def tds(player,team):
    c=byname.get(norm_name(player)); r=c[0] if c and len(c)==1 else None
    return 0.0 if r is None else float(r.rushing_tds+r.receiving_tds)
SRC={"sx7":["HOU@JAX","CHI@ATL","BAL@CLE","TEN@IND","NYJ@NE","NO@NYG","CAR@PHI","PIT@TB"],"sx8":["ARI@LA","LAC@KC","BUF@LV","DAL@GB"],"sx10":["WAS@SF"]}
rows=[];tdrows=[];qbrows=[]
SF.BACKUP_QBS={"Jalon Daniels","Tanner McKee","Tyler Huntley"}
for d,gl in SRC.items():
    SF.OUT=S+d
    for g in gl:
        a,h=g.split("@")
        try: mk,md,Sg,legs,meta,fav=SF._game_pool(a,h)
        except Exception as e: print("skip",g,e); continue
        Sg=Sg.copy(); Sg["src"]=d
        rows.append(Sg)
        for k,v in meta.items():
            if v["kind"]=="td" and v["market"]=="any_td":
                tdrows.append(dict(game=g,player=v["player"],team=v.get("team"),p=v["p"],src=d))
            if v["market"]=="pass_td" and k.endswith(("1+","2+")):
                qbrows.append(dict(game=g,player=v["player"],k=k.rsplit(" ",1)[-1],p=v["p"]))
S_=pd.concat(rows,ignore_index=True)
S_["act"]=[actual(r.player,r.team,r.market) for r in S_.itertuples()]
S_["res"]=np.where(S_.act.isna(),np.nan,np.where(S_.act==S_.line,np.nan,np.where(((S_.act>S_.line)==(S_.side=="OVER")),1.0,0.0)))
S_.to_pickle(S+"w6c/graded_singles.pkl")
def rep(df,name):
    d=df.dropna(subset=["res"])
    print(f"{name}: n={len(d)} hit={d.res.mean():.1%} expected(shrunk)={d.shrunk.mean():.1%} raw={d.model_p.mean():.1%}")
rep(S_,"ALL lines")
for lab in ["PLAY","LEAN"]: rep(S_[S_.label==lab],lab)
rep(S_[(S_.label!="")&(S_.agree=="yes")],"labeled+agree")
rep(S_[S_.label=="PLAY"][lambda x:x.src!="sx10"],"PLAY excl MNF")
print("by market (labeled):")
L=S_[S_.label!=""].dropna(subset=["res"])
print(L.groupby("market").agg(n=("res","size"),hit=("res","mean"),exp=("shrunk","mean")).round(3).to_string())
print("by side:",L.groupby("side").agg(n=("res","size"),hit=("res","mean"),exp=("shrunk","mean")).round(3).to_string())
print("by game:",L.groupby("game").agg(n=("res","size"),hit=("res","mean")).round(2).T.to_string())
# calibration all lines raw model_p (the picked side prob)
d=S_.dropna(subset=["res"]); d["bin"]=pd.cut(d.model_p,[0,.55,.6,.65,.7,.75,.8,1])
print(d.groupby("bin",observed=True).agg(n=("res","size"),hit=("res","mean"),raw=("model_p","mean"),shrunk=("shrunk","mean")).round(3).to_string())
# TOP30 AM / PM (same rules as published)
def top30(df):
    df=df[df.label.isin(["PLAY","LEAN"])&(df.agree=="yes")&(df.n_log>=3)&(df.model_p<0.85)&~df.player.isin(SF.BACKUP_QBS)&~df.team.isin(["CHI"])]
    df=df[~((df.team=="HOU")&df.market.isin(["rec","rec_yds"]))]
    return df.sort_values("shrunk",ascending=False).drop_duplicates("player").head(30)
amg=S_[S_.src=="sx7"]; pmg=S_[S_.src.isin(["sx8","sx10"])]
for nm,df in (("TOP30 AM (1PM games)",amg),("TOP30 PM+MNF",pmg)):
    t=top30(df); tt=t.dropna(subset=["res"]); print(nm,f"n={len(tt)} hit={tt.res.mean():.1%} exp={tt.shrunk.mean():.1%}")
    t.to_pickle(S+f"w6c/top30_{nm[:5].strip().replace(' ','_')}.pkl")
# TD
T_=pd.DataFrame(tdrows); T_["act"]=[tds(r.player,r.team) for r in T_.itertuples()]
T_=T_.dropna(subset=["act"]); T_["y"]=(T_.act>=1).astype(float)
T_=T_.drop_duplicates(["player","game"])
ll=lambda p,y: float(-(y*np.log(np.clip(p,1e-6,1))+(1-y)*np.log(np.clip(1-p,1e-6,1))).mean())
print(f"ANYTIME TD n={len(T_)} sumP={T_.p.sum():.1f} actual={T_.y.sum():.0f} logloss={ll(T_.p,T_.y):.4f} base={ll(np.full(len(T_),T_.y.mean()),T_.y):.4f}")
T_["bin"]=pd.cut(T_.p,[0,.1,.2,.3,.4,.5,.6,1])
print(T_.groupby("bin",observed=True).agg(n=("y","size"),p=("p","mean"),act=("y","mean")).round(3).to_string())
top=T_.sort_values("p",ascending=False)
for n in (10,30): print(f"top{n} anytime hit {top.head(n).y.mean():.0%} (pred {top.head(n).p.mean():.0%})")
print(top.head(30)[["player","team","game","p","act"]].round(2).to_string())
T_.to_pickle(S+"w6c/td_graded.pkl")
Q=pd.DataFrame(qbrows).drop_duplicates(["player","k"])
def qbact(r):
    x=act.get((norm_name(r.player),next((t for (kk,t) in act if kk==norm_name(r.player)),None)))
    return np.nan if x is None else float(x.passing_tds)
Q["act"]=[qbact(r) for r in Q.itertuples()]; Q=Q.dropna(subset=["act"])
Q["y"]=np.where(Q.k=="1+",Q.act>=1,Q.act>=2).astype(float)
for k in ("1+","2+"):
    q=Q[Q.k==k]; print(f"QB pass TD {k}: n={len(q)} sumP={q.p.sum():.1f} actual={q.y.sum():.0f}")
