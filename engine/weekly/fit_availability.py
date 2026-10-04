"""Empirical play-rate table: P(plays | final report status, practice status, position group), fit on nflverse 2023-2026."""
from paths import OUT, NFLV, DELIV, CONF
import pandas as pd, numpy as np
N=NFLV
pl=pd.read_parquet(N+"players.parquet",columns=["gsis_id","pfr_id"]).dropna()
inj=pd.concat([pd.read_parquet(N+f"injuries_{y}.parquet") for y in (2023,2024,2025,2026)])
sn=pd.concat([pd.read_parquet(N+f"snap_counts_{y}.parquet") for y in (2023,2024,2025,2026)])
inj=inj[inj.game_type=="REG"].copy()
sn["snaps"]=sn.offense_snaps.fillna(0)+sn.defense_snaps.fillna(0)+sn.st_snaps.fillna(0)
sn=sn[sn.game_type=="REG"].merge(pl,left_on="pfr_player_id",right_on="pfr_id",how="left")
played=sn.groupby(["season","week","gsis_id"]).snaps.sum().reset_index(); played["played"]=played.snaps>0
d=inj.merge(played[["season","week","gsis_id","played"]],on=["season","week","gsis_id"],how="left")
# only keep rows where the team actually had a game that week (snap data exists for team-week) to avoid byes/unplayed weeks
tw=sn.groupby(["season","week","team"]).size().reset_index(name="n")[["season","week","team"]]
d=d.merge(tw.assign(has_game=True),on=["season","week","team"],how="left"); d=d[d.has_game==True]
d["played"]=d.played.fillna(False).astype(int)
PG={"QB":"QB","RB":"RB","FB":"RB","WR":"WRTE","TE":"WRTE","T":"OL","G":"OL","C":"OL","OL":"OL","DE":"DL","DT":"DL","NT":"DL","DL":"DL","LB":"LB","OLB":"LB","ILB":"LB","MLB":"LB","CB":"DB","S":"DB","FS":"DB","SS":"DB","DB":"DB","K":"KP","P":"KP","LS":"KP"}
d["pg"]=d.position.map(PG).fillna("OTH")
d["rs"]=d.report_status.fillna("None"); d["ps"]=d.practice_status.fillna("None").map(lambda x:{"Did Not Participate In Practice":"DNP","Limited Participation in Practice":"LP","Full Participation in Practice":"FP"}.get(x,"None"))
print("rows",len(d),"played rate",d.played.mean().round(3)); print(d.groupby("rs").played.agg(["mean","size"]).round(3))
# hierarchical table
def table(df,m=12):
    root=df.groupby(["rs","ps"]).played.agg(["sum","size"]).reset_index(); root["p_parent"]=(root["sum"]+1)/(root["size"]+2)
    leaf=df.groupby(["rs","ps","pg"]).played.agg(["sum","size"]).reset_index().merge(root[["rs","ps","p_parent"]],on=["rs","ps"])
    leaf["p"]=(leaf["sum"]+m*leaf.p_parent)/(leaf["size"]+m)
    return root,leaf
def predict(df,root,leaf):
    x=df.merge(leaf[["rs","ps","pg","p"]],on=["rs","ps","pg"],how="left").merge(root[["rs","ps","p_parent"]],on=["rs","ps"],how="left")
    return x.p.fillna(x.p_parent).fillna(d.played.mean()).values
def hand(r):
    if r.rs=="Out": return 0.0
    if r.rs=="Doubtful": return 0.08
    if r.rs=="Questionable": return {"DNP":.5,"LP":.65,"FP":.85,"None":.6}[r.ps]
    return {"FP":.98,"LP":.90,"DNP":.70,"None":.80}[r.ps]
tr=d[d.season<=2024]; te=d[d.season==2025]   # fit 2023-24, hold out 2025
root,leaf=table(tr); p_fit=predict(te,root,leaf); p_hand=te.apply(hand,axis=1).values
def brier(p,y): return float(np.mean((p-y)**2)); 
def ll(p,y): p=np.clip(p,.02,.98); return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
y=te.played.values
print("HOLDOUT 2025  n=",len(te)); print("hand-set  brier %.4f logloss %.4f"%(brier(p_hand,y),ll(p_hand,y))); print("fitted    brier %.4f logloss %.4f"%(brier(p_fit,y),ll(p_fit,y)))
sk=te.pg.isin(["QB","RB","WRTE"]).values
print("skill only: hand brier %.4f fit brier %.4f"%(brier(p_hand[sk],y[sk]),brier(p_fit[sk],y[sk])))
# final table on all data (2023-2026)
root,leaf=table(d); root.to_csv(CONF+"availability_by_status.csv",index=False); leaf.to_csv(CONF+"availability_by_status_pos.csv",index=False)
print("\nFitted play rates (all data), skill positions:")
t=leaf[leaf.pg.isin(["QB","RB","WRTE"])].pivot_table(index=["rs","ps"],columns="pg",values="p").round(3); n=leaf[leaf.pg.isin(["QB","RB","WRTE"])].groupby(["rs","ps"])["size"].sum()
print(t.join(n.rename("n")).to_string())
print("\nhand-set vs fitted (all positions pooled):"); print(root.assign(p=(root["sum"]/root["size"]).round(3)).drop(columns=["p_parent"]).to_string(index=False))
