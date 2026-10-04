from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd
pd.set_option("display.width",260); pd.set_option("display.max_colwidth",40)
O=OUT
E=pd.read_csv(O+"edges_all_rows.csv")
E["pay"]=np.where(E.odds<0,100/(-E.odds),E.odds/100)
key=["game","player","team","opp","market","side","line","is_alt"]
def agg(g):
    b=g.loc[g.pay.idxmax()]; w=g.loc[g.pay.idxmin()]
    return pd.Series(dict(best_book=b.book,best_odds=b.odds,worst_odds=w.odds,books=len(g),model_p=g.model_p.iloc[0],novig_p=g.novig_p.mean(),method=g.novig_method.iloc[0],
        p_active=g.p_active.iloc[0],played=g.played.iloc[0],confidence=g.confidence.iloc[0],stale=g.stale.any(),age_h=g.age_h.max(),
        ev=b.ev))
A=E.groupby(key,dropna=False).apply(agg).reset_index()
A["edge"]=A.model_p-A.novig_p
# market-level level-bias estimate: median over/yes-side edge per market (efficient-market centering); one offset per market, cross-player differences preserved
ov=A[A.side.isin(["over","yes"])]
BIAS=ov.groupby("market").edge.median()
A["bias"]=A.market.map(BIAS)
A["raw_edge"]=A.edge
A["model_p_adj"]=np.where(A.side.isin(["over","yes"]),A.model_p-A.bias,A.model_p+A.bias).clip(0.005,0.995)
A["edge"]=A.model_p_adj-A.novig_p
A["pay_best"]=np.where(A.best_odds<0,100/(-A.best_odds),A.best_odds/100)
A["ev"]=A.model_p_adj*A.pay_best-(1-A.model_p_adj)
A["price_gap_implied_pts"]=0.0
# implied gap best vs worst
imp=lambda a: np.where(a<0,-a/(-a+100),100/(a+100))
A["price_gap_implied_pts"]=(imp(A.worst_odds)-imp(A.best_odds))
def thr(r):
    if r.market=="first_td": return .07
    if r.is_alt==1 or r.market=="anytime_td": return .05
    return .03
A["min_edge"]=A.apply(thr,axis=1)
A["listed"]=(A.edge>=A.min_edge)&(A.raw_edge>0)
# single best rung per player-market-side
A=A.sort_values("ev",ascending=False)
best=A[A.listed].drop_duplicates(["game","player","market","side"]).copy()
best["flag"]=""
best.loc[best.edge>0.15,"flag"]+="MODEL-GAP>15pts (verify); "
best.loc[best.stale,"flag"]+="STALE; "
best.loc[best.played,"flag"]+="GAME PLAYED; "
best.loc[best.p_active<0.9,"flag"]+="availability<90%; "
best.loc[best.method.str.startswith("Estimated"),"flag"]+="vig Estimated; "
best.loc[best.books<3,"flag"]+="<3 books; "
best.to_csv(O+"edges_listed_all.csv",index=False)
cand=best[(~best.played)&(~best.stale)]
ok=cand[(cand.flag.str.contains("MODEL-GAP")==False)&(cand.books>=3)&(cand.confidence.isin(["A","B"]))&(cand.p_active>=.9)]
cols=["player","team","opp","market","side","line","best_book","best_odds","worst_odds","books","model_p","model_p_adj","novig_p","raw_edge","edge","ev","confidence","flag"]
ok=ok[(ok.market!="first_td")&(ok.is_alt==0)]
ok=ok[~((ok.market=="anytime_td")&(ok.model_p_adj<0.20))]
srt=ok.sort_values("ev",ascending=False).drop_duplicates("player")
tdp=srt[srt.market=="anytime_td"].head(3); oth=srt[srt.market!="anytime_td"].head(7)
top=pd.concat([tdp,oth]).sort_values("ev",ascending=False)
top[cols].round(3).to_csv(O+"edges_top_plays.csv",index=False)
# fades: strongest under/no-side edges on yardage markets (market too high), same quality filters
fd=ok[(ok.side=="under")&(ok.market.isin(["rec_yds","rush_yds","pass_yds","rush_rec_yds"]))].sort_values("ev",ascending=False).drop_duplicates("player").head(5)
fd[cols].round(3).to_csv(O+"edges_fades.csv",index=False)
print("market bias offsets (median over-side raw edge):",BIAS.round(3).to_dict()); BIAS.round(4).to_csv(O+"edges_market_bias_offsets.csv")
print("grouped lines",len(A),"listed (pass threshold)",int(A.listed.sum()),"best-rung plays",len(best))
print("by market:",best.groupby(["market","side"]).size().to_dict())
print("model-gap flagged",int(best.flag.str.contains("MODEL-GAP").sum()),"of",len(best))
print("\nTOP PLAYS"); print(top[cols].round(3).to_string())
print("\nFADES"); print(fd[cols].round(3).to_string())
# calibration: overall mean edge on over sides vs under; shows bias
m=A[(A.market.isin(["pass_yds","rec_yds","rush_yds","rec","pass_tds","rush_rec_yds"]))&(A.is_alt==0)]
print("\nmean edge on OVER sides",m[m.side=="over"].edge.mean().round(4),"UNDER",m[m.side=="under"].edge.mean().round(4)); print(m[m.side=="over"].groupby("market").edge.agg(["mean","median","count"]).round(3))
tdm=A[A.market.isin(["anytime_td"])]; print("anytime TD mean model_p",tdm.model_p.mean().round(3),"mean novig_p",tdm.novig_p.mean().round(3),"corr",tdm[["model_p","novig_p"]].corr().iloc[0,1].round(3))
