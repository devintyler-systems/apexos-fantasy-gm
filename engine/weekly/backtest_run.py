"""usage: APEX_SEASON=2025 APEX_THROUGH_WEEK=3 APEX_BACKTEST=1 APEX_TARGET_WEEK=4 APEX_INJ_WEEK=4 APEX_ROSTER=v4 APEX_ENV=model python3 backtest_run.py tag"""
from paths import OUT, NFLV, DELIV, CONF
import sys, os, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
import run_all as R
from params import SCHED, SEASON, norm_name, is_neutral, ENV_MODE, ROSTER_MODE
tag=sys.argv[1]; NS=int(os.environ.get("APEX_NS",6000)); rows=[]; teamrows=[]
for _,g in SCHED.iterrows():
    R.run_game(g.away,g.home,neutral=bool(g.neutral),ns=NS)
    d=R.STORE.pop((g.away,g.home)); A,H=d["A"],d["H"]
    teamrows.append(dict(away=g.away,home=g.home,away_pts=float(A["pts"].mean()),home_pts=float(H["pts"].mean())))
    for nm,sd in ((g.away,A),(g.home,H)): teamrows.append(dict(team=nm,t_att_sd=float(sd["att"].std()),t_att_q05=float(np.percentile(sd["att"],5)),t_att_q95=float(np.percentile(sd["att"],95)),t_rush_sd=float(sd["rush"].std()),t_rush_q05=float(np.percentile(sd["rush"],5)),t_rush_q95=float(np.percentile(sd["rush"],95)),t_pts_sd=float(sd["pts"].std()),t_att=float(sd["att"].mean()),t_rush=float(sd["rush"].mean()),t_pyds=float(sd["team_pass_yds"].mean()),t_ryds=float(sd["rush_yds"].mean()),t_ptd=float(sd["ptd_n"].mean()),t_rtd=float(sd["rtd_n"].mean()),t_sacks=float(sd["sacks"].mean()),t_plays=float(sd["plays"].mean())))
    for t in (g.away,g.home):
        for p in d["players"][t]:
            m=p["mask"]
            if m.sum()<200: continue
            tdc=(p["rush_td"]+p["rec_td"])
            rows.append(dict(player=p["player"],nkey=norm_name(p["player"]),team=t,pos=p["pos"],p_active=p["p_active"],pass_yds=p["pass_yds"][m].mean(),pass_cmp=p["pass_cmp"][m].mean(),pass_td=p["pass_td"][m].mean(),
                             rush_yds=p["rush_yds"][m].mean(),rush_att=p["rush_att"][m].mean(),rec=p["rec"][m].mean(),rec_yds=p["rec_yds"][m].mean(),any_td=float((tdc[m]>=1).mean()),exp_td=float(tdc[m].mean()),
                             **{f"{k}_q{q}":float(np.percentile(p[k][m],q)) for k in ("rec_yds","rec","rush_yds","pass_yds") for q in (10,25,75,90)}))
pd.DataFrame(rows).to_pickle(f"{OUT}bt_{tag}.pkl"); pd.DataFrame(teamrows).to_pickle(f"{OUT}btteam_{tag}.pkl"); print("done",tag,len(rows))
