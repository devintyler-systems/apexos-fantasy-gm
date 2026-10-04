import os
import pandas as pd, numpy as np
from load import *
F=pd.read_pickle(OUT+"frames_raw.pkl")
def pl(k):
    t=F[k].copy()
    nc="Player"; tc="Team" if "Team" in t.columns else "Tm"
    t=t[t.pfr_id.notna()].copy()
    t["player"]=t[nc].astype(str).str.replace(r"[*+]","",regex=True).str.strip()
    t["team"]=t[tc].map(abbr); t["nkey"]=t.player.map(norm_name)
    return t
base=pl("player_scrimmagestats")
# master identity: union of ids across all player files
ids=[]
for k in [x for x in F if x.startswith("player_")]:
    t=pl(k); ids.append(t[["pfr_id","player","team","nkey"]+(["Pos"] if "Pos" in t.columns else [])])
M=pd.concat(ids).drop_duplicates("pfr_id")
pos=pd.concat([pl(k)[["pfr_id","Pos"]] for k in ["player_scrimmagestats","player_passing","player_scoring"]]).dropna().drop_duplicates("pfr_id")
M=M.drop(columns=[c for c in ["Pos"] if c in M]).merge(pos,on="pfr_id",how="left")
M.to_csv(OUT+"identity_master.csv",index=False)
print("identity rows",len(M),"dup nkey+team",M.duplicated(["nkey","team"]).sum())
# team change check: same pfr_id with >1 team across files
allteam=pd.concat([pl(k)[["pfr_id","team"]] for k in F if k.startswith("player_")]).drop_duplicates()
print("pfr_ids on >1 team:",allteam.pfr_id.duplicated().sum())
# injury match
inj,sch=parse_injury(); inj.to_csv(OUT+"injuries_parsed.csv",index=False); sch.to_csv(OUT+"schedule_week4.csv",index=False)
skill=inj[inj.pos.isin(["QB","RB","WR","TE","K","FB"])]
mm=skill.merge(M,on=["nkey","team"],how="left",indicator=True)
print("injury skill rows",len(skill),"unmatched",(mm._merge=="left_only").sum())
print(mm[mm._merge=="left_only"][["player_x","pos","team"]].to_string())
# odds match
x=pd.ExcelFile(os.environ["APEX_ODDS_XLSX"]).parse("PlayerProp_Odds")
x["nkey"]=x.description.map(norm_name)
names=x[["description","nkey"]].drop_duplicates()
mo=names.merge(M[["nkey","player"]].drop_duplicates("nkey"),on="nkey",how="left")
print("odds distinct players",len(names),"unmatched",mo.player.isna().sum())
print(mo[mo.player.isna()].description.tolist()[:60])
