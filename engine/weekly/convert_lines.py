import os
"""Convert Week4_NFL_Player_Props_Odds.xlsx (PlayerProp_Odds sheet) to v2 props_lines.csv schema."""
from paths import OUT, NFLV, DELIV, CONF
import pandas as pd, numpy as np
from load import *
M=pd.read_csv(OUT+"identity_master.csv")
O=OUT
p=pd.ExcelFile(os.environ["APEX_ODDS_XLSX"]).parse("PlayerProp_Odds")
TZ_OFFSET_H=7   # sheet timestamps are US Pacific (PDT): TNF commence 17:18 == 8:15 PM ET kickoff
p["as_of_utc"]=(p.last_update+pd.Timedelta(hours=TZ_OFFSET_H)).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
MK={"player_pass_yds":"pass_yds","player_pass_tds":"pass_tds","player_reception_yds":"rec_yds","player_receptions":"rec","player_rush_yds":"rush_yds",
    "player_rush_reception_yds":"rush_rec_yds","player_anytime_td":"anytime_td","player_1st_td":"first_td"}
SD={"Over":"over","Under":"under","Yes":"yes"}
p["market_v2"]=p.market.map(MK); p["side"]=p.label.map(SD)
p["home"]=p.home_team.map(FULL2ABBR); p["away"]=p.away_team.map(FULL2ABBR)
p["nkey"]=p.description.map(norm_name)
p["game_id"]="2026W04_"+p.away+"_"+p.home
# player -> team via identity; must be one of the two teams in the game
idm=M[["nkey","team","Pos"]].copy()
m=p.merge(idm,on="nkey",how="left")
m["team_ok"]=(m.team==m.home)|(m.team==m.away)
rej_reason=np.where(m.market_v2.isna(),"market not in v2 list",np.where(m.team.isna(),"no Week 1-3 stat line (no identity)",np.where(~m.team_ok,"player team not in this game (identity conflict)","")))
m["reject"]=rej_reason
m["opp"]=np.where(m.team==m.home,m.away,m.home)
m["position"]=m.Pos.replace({"FB":"RB"})
# multiple identities per nkey (same name different team): keep the one whose team is in the game
m=m.sort_values("team_ok",ascending=False).drop_duplicates(["bookmaker","game_id","description","market","label","point","price","as_of_utc"])
good=m[m.reject==""].copy()
# is_alt: main = per (book, player, market) the point with over/under prices closest to even; others alt
def mark(g):
    pts=g.point.dropna().unique()
    if len(pts)<=1: return pd.Series(0,index=g.index)
    best=None;bd=9e9
    for pt in pts:
        s=g[g.point==pt]; o=s[s.side=="over"].price; u=s[s.side=="under"].price
        if len(o) and len(u):
            d=abs(o.iloc[0]-u.iloc[0]) if (o.iloc[0]<0)==(u.iloc[0]<0) else 200
            if d<bd: bd=d;best=pt
    return (g.point!=best).astype(int)
good["is_alt"]=0
two=good[good.point.notna()]
alt=two.groupby(["bookmaker","game_id","description","market_v2"],group_keys=False).apply(mark)
good.loc[alt.index,"is_alt"]=alt.values
res=pd.DataFrame(dict(book=good.bookmaker,game_id=good.game_id,team=good.team,opp=good.opp,player=good.description,position=good.position,
    market=good.market_v2,side=good.side,line=good.point,odds_american=good.price,as_of_utc=good.as_of_utc,is_alt=good.is_alt))
res.to_csv(O+"props_lines.csv",index=False)
rej=m[m.reject!=""][["bookmaker","game_id","description","market","label","point","price","reject"]]
rej.to_csv(O+"props_lines_rejected.csv",index=False)
print("rows in",len(p),"loaded",len(res),"rejected",len(rej)); print(rej.reject.value_counts().to_string())
print(res.market.value_counts().to_string()); print("alt rows",int(res.is_alt.sum()),"books",res.book.nunique(),"players",res.player.nunique())
print(res.head(3).to_string())
print("as_of_utc range",res.as_of_utc.min(),res.as_of_utc.max())
