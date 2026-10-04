from paths import OUT, NFLV, DELIV, CONF
import os
import numpy as np, pandas as pd
pd.set_option("display.width",260); pd.set_option("display.max_colwidth",60)
O=OUT; D=DELIV
E=pd.read_csv(O+"edges_all_rows.csv")
E["pay"]=np.where(E.odds<0,100/(-E.odds),E.odds/100)
key=["game","player","team","opp","market","side","line","is_alt"]
def agg(g):
    return pd.Series(dict(books=len(g),model_p=g.model_p.iloc[0],novig_p=g.novig_p.mean(),p_active=g.p_active.iloc[0],played=g.played.iloc[0],confidence=g.confidence.iloc[0],method=g.novig_method.iloc[0]))
A=E[E.market.isin(["pass_yds","pass_tds","rec_yds","rec","rush_yds","rush_rec_yds"])].groupby(key,dropna=False).apply(agg).reset_index()
# same per-market level-bias centering used in v2 (median over-side raw edge)
A["edge_raw"]=A.model_p-A.novig_p
BIAS=A[A.side=="over"].groupby("market").edge_raw.median()
A["bias"]=A.market.map(BIAS)
A["hit_adj"]=np.where(A.side=="over",A.model_p-A.bias,A.model_p+A.bias).clip(0.01,0.99)
A["edge_adj"]=A.hit_adj-A.novig_p
f=A[(~A.played)&(A.books>=3)&(A.p_active>=0.9)&(A.confidence.isin(["A","B"]))&(A.edge_adj>=0.03)&(A.edge_raw>0)&(A.edge_adj<=0.20)&(A.is_alt==0)].copy()
f=f.sort_values("hit_adj",ascending=False)
f1=f.drop_duplicates(["player"]).head(30)   # one line per player
fl=pd.read_csv(O+"w4_player_props_fair_lines.csv")[["player","team","market","mean","median","p25","p75"]]
f1=f1.merge(fl,on=["player","team","market"],how="left")
LBL={"pass_yds":"Pass Yds","pass_tds":"Pass TDs","rec_yds":"Rec Yds","rec":"Receptions","rush_yds":"Rush Yds","rush_rec_yds":"Rush+Rec Yds"}
out=pd.DataFrame({"#":range(1,len(f1)+1),"Player":f1.player,"Game":f1.team+" vs "+f1.opp,"Pick":[f"{s.upper()} {l:g} {LBL[m]}" for s,l,m in zip(f1.side,f1.line,f1.market)],
  "Hit % (model)":(f1.hit_adj*100).round(0).astype(int),"Hit % (raw model)":(f1.model_p*100).round(0).astype(int),"Books at this line":f1.books,
  "Model proj (mean)":f1["mean"].round(1),"Model range P25-P75":[f"{a:.0f} to {b:.0f}" if m not in("rec","pass_tds") else f"{a:.0f} to {b:.0f}" for a,b,m in zip(f1.p25,f1.p75,f1.market)],
  "Availability %":(f1.p_active*100).round(0).astype(int),"Role grade":f1.confidence})
out.to_csv(D+"model_top30_line_plays.csv",index=False)
print(len(f),"candidates;",len(out)); print(out.to_string(index=False))
print(BIAS.round(3).to_dict()); print(out["Pick"].str.extract(r"^(OVER|UNDER)")[0].value_counts().to_dict(), out.Game.str.split(" vs ").str[0].value_counts().head(5).to_dict())
