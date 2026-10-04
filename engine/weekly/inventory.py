import glob, os, pandas as pd, numpy as np
from load import *
files = sorted(glob.glob(U+"*sportsref*.xls"))
rows=[]; frames={}
for f in files:
    key=re.sub(r"^.*sportsref_download_|_week4\.xls$","",os.path.basename(f))
    t=read_sr(key, with_ids=key.startswith("player_"))
    frames[key]=t
    issues=[]
    tc="Team" if "Team" in t.columns else ("Tm" if "Tm" in t.columns else None)
    if tc:
        agg=t[tc].astype(str).str.contains("Avg|Total|League",regex=True,na=False).sum()
        if agg: issues.append(f"{agg} aggregate rows (Avg/League) dropped")
        nteams=t[tc].map(abbr).nunique()
        issues.append(f"{nteams} distinct team codes")
    gcol="G" if "G" in t.columns else None
    gmax=pd.to_numeric(t[gcol],errors="coerce").max() if gcol else np.nan
    if "pfr_id" in t.columns: issues.append(f"pfr_id {t.pfr_id.notna().sum()}/{len(t)}")
    rep=t.iloc[:,1].astype(str).eq(t.columns[1]).sum() if len(t.columns)>1 else 0
    if rep: issues.append(f"{rep} repeated header rows")
    rows.append(dict(file=os.path.basename(f).split("-",1)[1],rows=len(t),cols=t.shape[1],games_max=gmax,issues="; ".join(issues)))
inv=pd.DataFrame(rows); inv.to_csv(OUT+"inventory.csv",index=False); print(inv.to_string())
pd.to_pickle(frames,OUT+"frames_raw.pkl")
