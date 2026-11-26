"""R-32 probe (DECISIONS #83): does a defense's position-level receiving yards over expected (ffopportunity ep_weekly, weeks < W) explain the engine's receiving-yards residual on the b12a backtest? Leave-one-season-out. Needs var/nflverse/ep_weekly_{2023..2025}.parquet."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,'/home/user/apexos-fantasy-gm/tools/backtest')
from evaluate import load
N='/home/user/apexos-fantasy-gm/var/nflverse/'
NV2T={"LAR":"LA","WSH":"WAS","JAC":"JAX","LVR":"LV","OAK":"LV","SD":"LAC","STL":"LA"}
D,_=load('b12a'); sk=D[(D.pos.isin(['WR','TE','RB']))&(D.rec>=1)].copy()
feat=[]
for S in (2023,2024,2025):
    e=pd.read_parquet(N+f'ep_weekly_{S}.parquet'); e=e[e.position.isin(['WR','TE','RB'])].copy()
    p=e.game_id.str.split('_',expand=True); e['away']=p[2]; e['home']=p[3]
    e['posteam']=e.posteam.replace(NV2T); e['away']=e.away.replace(NV2T); e['home']=e.home.replace(NV2T)
    e['dt']=np.where(e.posteam==e.home,e.away,e.home)
    for W in range(4,13):
        h=e[e.week<W]
        tot=h.groupby('dt').agg(y=('rec_yards_gained_diff','sum'),t=('rec_attempt','sum'))
        pos=h.groupby(['dt','position']).agg(y=('rec_yards_gained_diff','sum'),t=('rec_attempt','sum'),
                tgt_x=('rec_attempt','sum')).reset_index()
        lg_pos=h.groupby('position').rec_attempt.sum()/h['dt'].nunique()   # targets per defense by position
        for r in pos.itertuples():
            k=60
            ypt_pos=r.y/(r.t+k); ypt_all=tot.loc[r.dt,'y']/(tot.loc[r.dt,'t']+k*3)
            feat.append(dict(season=S,week=W,opp=r.dt,pos=r.position,f_ypt=ypt_pos-ypt_all,f_vol=(r.t/ max(lg_pos[r.position],1))-1))
F=pd.DataFrame(feat)
# opponent of each player row
g=pd.read_parquet(N+'games.parquet'); g=g[g.game_type=='REG'][['season','week','home_team','away_team']].copy()
for c in ('home_team','away_team'): g[c]=g[c].replace(NV2T)
m=pd.concat([g.rename(columns={'home_team':'team','away_team':'opp'}),g.rename(columns={'away_team':'team','home_team':'opp'})])
sk=sk.merge(m,on=['season','week','team']).merge(F,on=['season','week','opp','pos'],how='left').dropna(subset=['f_ypt'])
sk['res']=sk.receiving_yards-sk.rec_yds
# expected effect: f_ypt yards per target x projected targets (approx rec/catch); use rec as proxy *1.5
sk['x']=sk.f_ypt*sk.rec*1.5
for S,gg in sk.groupby('season'):
    b=np.polyfit(gg.x,gg.res,1); print(S,'n',len(gg),'slope',round(b[0],3),'corr',round(np.corrcoef(gg.x,gg.res)[0,1],4))
b=np.polyfit(sk.x,sk.res,1); print('pooled slope',round(b[0],3),'corr',round(np.corrcoef(sk.x,sk.res)[0,1],4))
# LOSO gain in MAE from adding slope*x
tot=0
for S in (2023,2024,2025):
    tr,te=sk[sk.season!=S],sk[sk.season==S]; bb=np.polyfit(tr.x,tr.res,1)[0]
    print(S,'MAE',round(te.res.abs().mean(),4),'->',round((te.res-bb*te.x).abs().mean(),4),'b',round(bb,3))
# volume feature on target count residual
sk['rres']=sk.receptions-sk.rec
for S,gg in sk.groupby('season'): print('vol',S,round(np.corrcoef(gg.f_vol,gg.rres)[0,1],4))
