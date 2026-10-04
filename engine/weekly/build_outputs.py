from paths import OUT, NFLV, DELIV, CONF
import pandas as pd, numpy as np, shutil, os, zipfile
from prep_nv import *
from params import INJ, SCHED, L, TEAM, build_roster
O=OUT
pd.set_option("display.width",250)
r=pd.read_pickle(O+"rank_raw.pkl")
r["note"]=r["note"].fillna("")
lim={"QB":40,"RB":60,"WR":90,"TE":40,"K":32,"DST":32}
cols=["rank","player","pos","team","opp","game","note","p_active","ev_pts","median_if_active","p25","p75","p90","injury","team_implied_pts","proxy"]
allr=[]
for pos,n in lim.items():
    d=r[r.pos==pos].sort_values("ev_pts",ascending=False).head(n).copy()
    d.insert(0,"rank",range(1,len(d)+1)); d=d[[c for c in cols if c in d.columns]]
    d.round(2).to_csv(O+f"w4_rankings_{pos}.csv",index=False); allr.append(d)
pd.concat(allr).round(2).to_csv(O+"w4_rankings_ALL.csv",index=False)
# team totals
e=pd.read_csv(O+"w4_game_environment.csv"); rows=[]
for _,g in e.iterrows():
    for t,o,hm in ((g.away,g.home,False),(g.home,g.away,True)):
        rows.append(dict(team=t,opp=o,home=hm,game=f"{g.away}@{g.home}",note=g.note if isinstance(g.note,str) else "",pts_mean=g[f"{t}_pts_mean"],p25=g[f"{t}_pts_p25"],p50=g[f"{t}_pts_p50"],p75=g[f"{t}_pts_p75"],p90=g[f"{t}_pts_p90"],
                         win_prob=g.home_win_prob if hm else g.away_win_prob,fair_ml=g.ml_fair_home_american if hm else g.ml_fair_away_american))
pd.DataFrame(rows).round(3).to_csv(O+"w4_team_totals.csv",index=False)
# team props: split environment rows vs market rows
tp=pd.read_csv(O+"w4_team_props_raw.csv")
tp[tp.market.isna()].dropna(axis=1,how="all").round(3).to_csv(O+"w4_team_environment.csv",index=False)
tp[tp.market.notna()].dropna(axis=1,how="all").round(3).to_csv(O+"w4_team_count_props.csv",index=False)
os.path.exists(O+"w4_team_props_raw.csv") and os.rename(O+"w4_team_props_raw.csv",O+"_team_props_raw.tmp")
# injury adjustment log
inj=INJ.copy(); inj["skill"]=inj.pos.isin(["QB","RB","WR","TE","K","FB"])
logs=[]
for t in sorted(inj.team.unique()):
    d,oth_t,oth_c=build_roster(t)
    for _,p in inj[(inj.team==t)&(inj.skill)].iterrows():
        m=d[d.nkey==p.nkey] if "nkey" in d.columns else d.iloc[0:0]
        tg=float(m.tgt_sh.iloc[0]) if len(m) else np.nan; cs=float(m.car_sh.iloc[0]) if len(m) else np.nan
        logs.append(dict(team=t,player=p.player,pos=p.pos,injury=p.injury,practice=p.practice,game_status=p.game_status,p_active=p.p_active,
                         tgt_share_at_risk=tg,carry_share_at_risk=cs,matched_to_stats=bool(len(m)),
                         rule="shares renormalized across active teammates + OTHER bucket per sim; Out=0; QB inactive -> backup proxy (ypa x0.92, int x1.15)" ))
pd.DataFrame(logs).round(3).to_csv(O+"w4_injury_adjustments.csv",index=False)
# defensive/OL injury group effects
from params import inj_groups
pd.DataFrame([dict(team=t,**inj_groups(t)) for t in TEAM]).round(3).to_csv(O+"w4_injury_unit_effects.csv",index=False)
# ---- observed pace (3 games) ----
mk=pd.read_csv(O+"w4_player_props_fair_lines.csv")
s=sc.copy(); q=pas.copy()
obs={}
for _,x in s.iterrows():
    G=max(float(x.G),1); obs[(x.player,x.team,"rec_yds")]=x["Receiving_Yds"]/G; obs[(x.player,x.team,"rec")]=x["Receiving_Rec"]/G
    obs[(x.player,x.team,"rush_yds")]=x["Rushing_Yds"]/G; obs[(x.player,x.team,"rush_att")]=x["Rushing_Att"]/G
for _,x in q.iterrows():
    G=max(float(x.G),1); obs[(x.player,x.team,"pass_yds")]=x["Yds"]/G; obs[(x.player,x.team,"pass_att")]=x["Att"]/G; obs[(x.player,x.team,"pass_td")]=x["TD"]/G
mk["obs_per_game_3g"]=[obs.get((a,b,c),np.nan) for a,b,c in zip(mk.player,mk.team,mk.market)]
mk["iqr"]=(mk.p75-mk.p25).clip(lower=1e-6)
mk["z_gap"]=(mk["median"]-mk.obs_per_game_3g)/(mk.iqr/1.35)
mk["p25_to_p75"]=mk.p25.round(1).astype(str)+" to "+mk.p75.round(1).astype(str)
std=mk[["player","team","opp","market","fair_line","median","p25_to_p75","over_pct","fair_odds_over","edge","confidence","key_drivers","injury_flag"]]
std.round(3).to_csv(O+"w4_player_props_standard_rows.csv",index=False)
mk.drop(columns=["iqr"]).round(3).to_csv(O+"w4_player_props_fair_lines.csv",index=False)
mk["g_played"]=[ (float(sc[(sc.player==a)&(sc.team==b)].G.iloc[0]) if len(sc[(sc.player==a)&(sc.team==b)]) else (float(pas[(pas.player==a)&(pas.team==b)].G.iloc[0]) if len(pas[(pas.player==a)&(pas.team==b)]) else np.nan)) for a,b in zip(mk.player,mk.team)]
base=mk[(mk.p_active>=.95)&(mk.note.isna())&(mk.confidence=="A")].copy()
picks=[]
for mkt,n in (("rec_yds",3),("rush_yds",3),("pass_yds",2),("rec",1)):
    x=base[base.market==mkt].sort_values("p25",ascending=False).head(n); picks.append(x)
top=pd.concat(picks).copy()
cand=mk[(mk.confidence.isin(["A","B"]))&(mk.p_active>=.9)&(mk.note.isna())&mk.market.isin(["rec_yds","rush_yds","pass_yds"])&mk.obs_per_game_3g.notna()&(mk.g_played>=2)&(mk["median"]>=15)].copy()
fad=cand.sort_values("z_gap").drop_duplicates(["player"]).head(5)
cols_=["player","team","opp","market","fair_line","median","p25_to_p75","obs_per_game_3g","z_gap","over_pct","confidence","key_drivers","injury_flag"]
top[cols_].round(2).to_csv(O+"w4_top_plays_unpriced.csv",index=False); fad[cols_].round(2).to_csv(O+"w4_fades_unpriced.csv",index=False)
print(top[cols_].round(2).to_string()); print(fad[cols_].round(2).to_string())
# TD regression fades (TD luck)
td=pd.read_csv(O+"w4_td_markets.csv"); a=td[td.market=="anytime_td"].copy()
obs_td=(s.set_index(["player","team"])[["Rushing_TD","Receiving_TD"]].sum(axis=1)).rename("td_3g")
a=a.merge(obs_td.reset_index(),on=["player","team"],how="left"); a["exp_td_3g"]=a.prob*3
a["td_over_exp"]=a.td_3g-a.exp_td_3g
a.sort_values("td_over_exp",ascending=False).head(15).round(2).to_csv(O+"w4_td_regression_watch.csv",index=False)
print(a.sort_values("td_over_exp",ascending=False).head(8)[["player","team","pos","prob","td_3g","exp_td_3g","td_over_exp"]].round(2).to_string())
print(a.sort_values("prob",ascending=False).head(12)[["player","team","opp","prob","fair_odds","confidence","injury_flag"]].round(3).to_string())
