"""Single-game dossier: per-player distribution summary (P10 floor, mean main, median, P90 ceiling, among ACTIVE sims) for every stat, plus anytime and first TD
probabilities and DK points, from the correlated sims of one game. Usage: APEX_ENV=<track> python tnf_dive.py AWAY HOME  -> OUT/dive_AWAY_HOME_<track>.pkl
Floor/ceiling are the 10th/90th percentile of the simulated outcome given the player is active; they describe a game that goes differently than the main projection."""
import sys, numpy as np, pandas as pd
from paths import OUT
import run_all as R
from params import is_neutral, norm_name, ENV_MODE
AWAY, HOME = sys.argv[1], sys.argv[2]
R.run_game(AWAY, HOME, neutral=is_neutral(AWAY, HOME), ns=20000); d = R.STORE.pop((AWAY, HOME)); A, H = d["A"], d["H"]
Ttot = np.maximum(A["td"] + H["td"] + A["dtd"] + H["dtd"], 1)
def dk(pl):
    base = 0.04 * pl["pass_yds"] + 4 * pl["pass_td"] - 2 * pl["pass_int"] + 0.1 * (pl["rush_yds"] + pl["rec_yds"]) + 6 * (pl["rush_td"] + pl["rec_td"]) + pl["rec"]
    fl = np.clip((base - pl["fp"]) / 2.0, 0, None)
    return (0.04 * pl["pass_yds"] + 4 * pl["pass_td"] - 1 * pl["pass_int"] + 3 * (pl["pass_yds"] >= 300) + 0.1 * pl["rush_yds"] + 6 * pl["rush_td"] + 3 * (pl["rush_yds"] >= 100)
            + pl["rec"] + 0.1 * pl["rec_yds"] + 6 * pl["rec_td"] + 3 * (pl["rec_yds"] >= 100) - fl)
STATS = ["pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int", "rush_att", "rush_yds", "rush_td", "tgt", "rec", "rec_yds", "rec_td"]
rows = []
for t in (AWAY, HOME):
    for pl in d["players"][t]:
        m = pl["mask"]
        if pl["p_active"] < 0.03 or m.sum() < 200: continue
        r = dict(player=pl["player"], pos=pl["pos"], team=t, p_active=float(pl["p_active"]), key=norm_name(pl["player"]))
        for s in STATS:
            x = pl[s][m].astype(float)
            r.update({f"{s}_lo": float(np.percentile(x, 10)), f"{s}_mean": float(x.mean()), f"{s}_med": float(np.median(x)), f"{s}_hi": float(np.percentile(x, 90))})
        tdc = pl["rush_td"] + pl["rec_td"]
        r["any_td"] = float((tdc[m] >= 1).mean()); r["first_td"] = float((tdc[m] / Ttot[m]).mean())
        x = pl["rush_yds"][m] + pl["rec_yds"][m]; r.update(scr_lo=float(np.percentile(x, 10)), scr_mean=float(x.mean()), scr_hi=float(np.percentile(x, 90)))
        x = (pl["rush_td"] + pl["rec_td"] + pl["pass_td"])[m]; r.update(tot_td_lo=float(np.percentile(x, 10)), tot_td_mean=float(x.mean()), tot_td_hi=float(np.percentile(x, 90)))
        x = dk(pl)[m]; r.update(dk_lo=float(np.percentile(x, 10)), dk_mean=float(x.mean()), dk_med=float(np.median(x)), dk_hi=float(np.percentile(x, 90)))
        rows.append(r)
env = dict(away_pts=A["pts"], home_pts=H["pts"])
tot = A["pts"] + H["pts"]; mg = H["pts"] - A["pts"]
g = dict(away=AWAY, home=HOME, away_mean=float(A["pts"].mean()), home_mean=float(H["pts"].mean()), away_med=float(np.median(A["pts"])), home_med=float(np.median(H["pts"])),
         away_p10=float(np.percentile(A["pts"], 10)), away_p90=float(np.percentile(A["pts"], 90)), home_p10=float(np.percentile(H["pts"], 10)), home_p90=float(np.percentile(H["pts"], 90)),
         total_mean=float(tot.mean()), total_p10=float(np.percentile(tot, 10)), total_p90=float(np.percentile(tot, 90)), home_win=float((mg > 0).mean() + 0.5 * (mg == 0).mean()))
pd.to_pickle((pd.DataFrame(rows), g), OUT + f"dive_{AWAY}_{HOME}_{ENV_MODE}.pkl"); print("saved", len(rows), "players", ENV_MODE)
