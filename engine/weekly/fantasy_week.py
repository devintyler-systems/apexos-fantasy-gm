"""SPAMML weekly advice tables: ranked league EV with TD column, kicker side-by-side, DST bounty odds.

  python fantasy_week.py <run_dir> <roster.csv> <available.csv> <out_dir>

Fantrax exports are private league data: read from anywhere, write only under a path you pass (never commit).
DST bounty: $10 to the owner whose DST team scores the most points, $10 for allowing the fewest (ties split by chance here).
P(top of the slate) is simulated from market implied points (margin sd 13, total sd 10.5) over the 28 teams playing; the real field is
the 15 other owners' picks, so these are floors for a random field and relative ranks matter more than levels.
"""
import os
import sys

import numpy as np
import pandas as pd

import league_spm as L
from paths import NFLV


def kicker_table(stats, team_pts, ro, av, cfg):
    k = stats[stats.position == "K"].copy()
    for c in ("fg_made", "fg_att", "pat_made", "pat_att"):
        k[c] = pd.to_numeric(k[c], errors="coerce").fillna(0)
    k["pts"] = 3 * k.fg_made + k.pat_made
    g = k.groupby("player_display_name").agg(team=("team", "last"), games=("week", "nunique"), avg_pts=("pts", "mean"), fga_g=("fg_att", "mean"), xp_g=("pat_made", "mean"))
    g["nkey"] = [L.norm_name(i) for i in g.index]
    cur = L.current_kickers(stats)
    g = g[[cur.get(t) == n for t, n in zip(g.team, g.nkey)]].reset_index().rename(columns={"player_display_name": "kicker"})
    g["team_pts"] = g.team.map(team_pts)
    g["env_ev"] = g.team_pts.map(lambda x: L.kicker_ev(x, cfg) if pd.notna(x) else np.nan)
    st = pd.concat([ro.assign(who="MINE"), av]).drop_duplicates("nkey")[["nkey", "who", "avail"]]
    g = g.merge(st, on="nkey", how="left")
    g["who"] = np.where(g.who.eq("MINE"), "MINE", g.avail.fillna("rostered elsewhere"))
    return g.drop(columns=["nkey", "avail"]).sort_values("env_ev", ascending=False)


def dst_table(T, cfg, n=40000, seed=7):
    T = T.copy()
    rng = np.random.default_rng(seed)
    rows = []
    for gm, d in T.groupby("game"):
        rows.append(d)
    teams, pts, opp = [], [], []
    G = {}
    for _, r in T.iterrows():
        G.setdefault(r.game, {})[r.team] = r.pts_mean
    sims = {}
    for gm, dd in G.items():
        (a, pa), (b, pb) = list(dd.items())
        tot = rng.normal(pa + pb, 10.5, n).clip(10)
        mar = rng.normal(pa - pb, 13, n)
        sa = ((tot + mar) / 2).clip(0); sb = ((tot - mar) / 2).clip(0)
        sims[a] = (sa, sb); sims[b] = (sb, sa)
    ts = list(sims)
    F = np.vstack([sims[t][0] for t in ts]); A = np.vstack([sims[t][1] for t in ts])
    top_f = F.argmax(0); low_a = A.argmin(0)
    out = []
    for i, t in enumerate(ts):
        out.append(dict(team=t, pts_for=F[i].mean(), pts_against=A[i].mean(), p_most_points=(top_f == i).mean(), p_fewest_allowed=(low_a == i).mean()))
    o = pd.DataFrame(out)
    o["bounty_ev_usd"] = 10 * (o.p_most_points + o.p_fewest_allowed)
    return o.sort_values("bounty_ev_usd", ascending=False)


def main(run_dir, roster, avail, out_dir, season=2026):
    cfg = L.load_cfg()
    P, team_pts = L.load_run(run_dir)
    S = L.skill_points(P, cfg)
    stats = pd.read_parquet(os.path.join(NFLV, f"stats_player_week_{season}.parquet"))
    kickers, ytd = L.current_kickers(stats), L.ytd_td_rate(stats)
    ro = L.attach_ev(L.read_fantrax(roster, cfg), S, team_pts, kickers, cfg)
    av = L.attach_ev(L.read_fantrax(avail, cfg), S, team_pts, kickers, cfg)
    os.makedirs(out_dir, exist_ok=True)
    mine = set(ro.nkey)
    R = S.copy()
    R["status"] = np.where(R.nkey.isin(mine), "MINE", np.where(R.nkey.isin(set(av[av.avail == "FA"].nkey)), "FA", np.where(R.nkey.isin(set(av[av.avail == "W"].nkey)), "W", "rostered elsewhere")))
    R["pass_td"], R["rush_td"], R["rec_td"] = P.pass_td_mean.values, P.rush_td_mean.values, P.rec_td_mean.values
    R["any_td_pct"] = P.any_td_pct.values
    R["ytd_td_g"] = R.nkey.map(ytd["rate"]).round(2)
    R = R.sort_values("ev", ascending=False)
    R[["player", "pos", "team", "opp", "status", "p_active", "pass_td", "rush_td", "rec_td", "exp_tds", "any_td_pct", "ytd_td_g", "ev"]].round(3).to_csv(os.path.join(out_dir, "ev_ranked.csv"), index=False)
    K = kicker_table(stats, team_pts, ro, av, cfg)
    K.round(2).to_csv(os.path.join(out_dir, "kickers.csv"), index=False)
    gm = pd.read_csv(os.path.join(run_dir, "w4_team_totals.csv"))
    gm = gm[~gm.note.astype(str).str.contains("PLAYED", na=False)]
    if "game" not in gm:
        gm["game"] = gm.get("game_id", gm.team)
    D = dst_table(gm, cfg)
    D.round(3).to_csv(os.path.join(out_dir, "dst_bounty.csv"), index=False)
    print(R.head(60)[["player", "pos", "team", "status", "pass_td", "rush_td", "rec_td", "exp_tds", "ytd_td_g", "ev"]].round(2).to_string(index=False))
    print(K.round(2).to_string(index=False)); print(D.head(12).round(3).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:5])
