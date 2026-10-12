"""Run all 16 Week 4 games -> projections, rankings, TD markets, ladders, team/game props."""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, time, sys
from sim import *

rng = np.random.default_rng(SEED)
# PLAYED comes from params (nflverse results for the target week)

def american(p):
    p = float(np.clip(p, 1e-4, 1 - 1e-4))
    return int(round(-100 * p / (1 - p))) if p >= .5 else int(round(100 * (1 - p) / p))

def fair_line(x):
    """half-point line with P(over) closest to 50%"""
    xs = np.sort(x); n = xs.size
    cand = np.unique(np.floor(xs)) + 0.5
    po = 1 - np.searchsorted(xs, cand, side="right") / n   # P(X > c)
    i = int(np.argmin(np.abs(po - .5)))
    return float(cand[i]), float(po[i])

LADDER = {
 "pass_yds": [175, 200, 225, 250, 275, 300, 325, 350, 375, 400], "pass_td": [1, 2, 3, 4], "pass_cmp": [14, 16, 18, 20, 22, 24, 26, 28, 30, 33],
 "pass_att": [24, 26, 28, 30, 32, 34, 36, 38, 40, 44], "pass_int": [1, 2], "pass_long": [35, 40, 45, 50, 60, 70],
 "rush_yds": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 125, 150], "rush_att": [3, 5, 8, 10, 12, 15, 18, 20, 22, 25],
 "rush_long": [10, 15, 20, 25, 30, 40], "rec_yds": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 125, 150],
 "rec": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "rec_long": [15, 20, 25, 30, 40, 50], "pass_rush_yds": [200, 225, 250, 275, 300, 325, 350, 375, 400],
 "rush_rec_yds": [30, 40, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175],
}
MIN_EDGE_GRADE = {"pass_long": "C", "rush_long": "C", "rec_long": "C"}

def grade(pl, market):
    r = pl["row"]
    sc_ = 0
    sc_ += 1 if pl["p_active"] >= .95 else 0
    g = float(getattr(r, "G", 3) or 3) if r is not None else 3
    sc_ += 1 if g >= 3 else 0
    if pl["pos"] == "QB": sc_ += 2 if float(getattr(r, "Att", 0) or 0) >= 60 else 0
    else:
        if market.startswith("rec") or market == "rush_rec_yds": sc_ += 1 if float(r.tgt_sh) >= .12 else 0; sc_ += 1 if float(r.Receiving_Tgt) >= 14 else 0
        if market.startswith("rush"): sc_ += 1 if float(r.car_sh) >= .15 else 0; sc_ += 1 if float(r.Rushing_Att) >= 15 else 0
        if market in ("anytime_td", "first_td", "last_td", "2plus_td"): sc_ += 1 if float(r.w_rec_td + r.w_rush_td) >= .15 else 0; sc_ += 1 if (r.Receiving_Tgt + r.Rushing_Att) >= 18 else 0
    g_ = "A" if sc_ >= 4 else "B" if sc_ >= 3 else "C"
    if market in MIN_EDGE_GRADE: g_ = "C"
    if market in ("anytime_td", "first_td", "last_td", "2plus_td") and g_ == "A": g_ = "B"
    if market in ("first_td", "last_td", "2plus_td"): g_ = "C" if g_ != "B" else "B"
    return g_

def inj_flag(pl):
    st, pr = pl.get("status"), pl.get("practice")
    if (st in (None, np.nan) or (isinstance(st, float) and np.isnan(st))) and (pr in (None, np.nan) or (isinstance(pr, float) and np.isnan(pr))): return "-"
    pr_ = {"DNP": "DNP", "LP": "Limited", "FP": "Full", "NONE": "no practice code"}.get(pr, "")
    st_ = st if isinstance(st, str) else "no game designation yet"
    return f"{st_} ({pr_})"

def drivers(pl, sd):
    r = pl["row"]
    if pl["pos"] == "QB":
        return f"team att {sd['att'].mean():.1f}; ypa {sd['ypa']:.2f}; opp d_ypa {sd['O']['d_ypa']:.2f}; pass rate {sd['prate'].mean():.1%}"
    parts = []
    if pl["rec"].mean() > .8: parts.append(f"tgt_sh {float(r.tgt_sh):.1%}; team att {sd['att'].mean():.1f}; opp DvP {r.tilt**2:.2f}; RZ tgt {int(r.rz_tgt)}")
    if pl["rush_att"].mean() > 2.5: parts.append(f"car_sh {float(r.car_sh):.1%}; team rush {sd['rush'].mean():.1f}; opp d_ypc {sd['O']['d_ypc']:.2f}; inside-10 car {int(r.rz10_car)}")
    if not parts: parts.append(f"w_td {float(r.w_rec_td + r.w_rush_td):.2f}; team TD {sd['td'].mean():.2f}")
    return "; ".join(parts)

rows_mk, rows_lad, rows_td, rank_rows, kd_rows, env_rows, inj_rows = [], [], [], [], [], [], []
team_prop_rows, game_prop_rows, ql_rows = [], [], []
STORE = {}   # for QA

def dst_pts(sacks, ints, fr, dtd, saf, pa):
    tier = np.select([pa == 0, pa <= 6, pa <= 13, pa <= 20, pa <= 27, pa <= 34], [10, 7, 4, 1, 0, -1], -4)
    return sacks + 2 * ints + 2 * fr + 6 * dtd + 2 * saf + tier

def timeline(sides, away, home, rng, ns):
    ev_t, ev_p, ev_team, ev_type = [], [], [], []
    for ti, t in enumerate((away, home)):
        s = sides[t]
        for typ, cnt, mx in ((0, s["td"], 8), (1, s["dtd"], 3), (2, s["fg"], 4), (3, s["saf"], 2)):
            m = np.arange(mx)[None, :] < cnt[:, None]
            qd = rng.choice(4, size=(ns, mx), p=[.215, .285, .215, .285])
            within = rng.random((ns, mx)) * 15
            two = (rng.random((ns, mx)) < .17) & (qd % 2 == 1)
            within = np.where(two, 13 + rng.random((ns, mx)) * 2, within)
            tm = np.where(m, qd * 15 + within, np.inf)
            if typ == 0: pts = 6 + (np.arange(mx)[None, :] < s["xp_off"][:, None])
            elif typ == 1: pts = 6 + (np.arange(mx)[None, :] < s["xp_d"][:, None])
            elif typ == 2: pts = np.full((ns, mx), 3)
            else: pts = np.full((ns, mx), 2)
            ev_t.append(tm); ev_p.append(pts * m); ev_team.append(np.full((ns, mx), ti)); ev_type.append(np.full((ns, mx), typ))
    T = np.hstack(ev_t); P_ = np.hstack(ev_p); TM = np.hstack(ev_team); TY = np.hstack(ev_type)
    o = np.argsort(T, axis=1)
    return (np.take_along_axis(T, o, 1), np.take_along_axis(P_, o, 1), np.take_along_axis(TM, o, 1), np.take_along_axis(TY, o, 1))

def run_game(away, home, neutral, ns=NS):
    t0 = time.time()
    env, sides, g = sim_game(away, home, neutral, rng, ns)
    A, H = sides[away], sides[home]
    players = {}
    for t in (away, home):
        players[t] = play_side(rng, t, sides[t], ns)
    played = (away, home) in PLAYED
    game_note = "PLAYED (final score in nflverse)" if played else ("INTL neutral site" if neutral else "")
    # ----- env row -----
    M = H["pts"] - A["pts"]; tot = H["pts"] + A["pts"]
    win_h = float((M > 0).mean() + 0.5 * (M == 0).mean())
    sched = SCHED[(SCHED.away == away) & (SCHED.home == home)].iloc[0]
    row = dict(away=away, home=home, date=sched.date, time_edt=sched.time_edt, note=game_note,
               home_win_prob=win_h, away_win_prob=1 - win_h, fair_spread_home=-float(np.median(M)), median_margin_home=float(np.median(M)),
               mean_margin_home=float(M.mean()), total_median=float(np.median(tot)), total_mean=float(tot.mean()),
               total_p25=float(np.percentile(tot, 25)), total_p75=float(np.percentile(tot, 75)),
               tie_prob=float((M == 0).mean()), ot_prob=float((M == 0).mean()))
    for nm, s in ((away, A), (home, H)):
        pc = np.percentile(s["pts"], [25, 50, 75, 90])
        row.update({f"{nm}_pts_mean": float(s["pts"].mean()), f"{nm}_pts_p25": pc[0], f"{nm}_pts_p50": pc[1], f"{nm}_pts_p75": pc[2], f"{nm}_pts_p90": pc[3]})
    row["ml_fair_home_american"] = american(win_h); row["ml_fair_away_american"] = american(1 - win_h)
    env_rows.append(row)
    # team environment rows
    for nm, s in ((away, A), (home, H)):
        opp = home if nm == away else away
        team_prop_rows.append(dict(game=f"{away}@{home}", team=nm, opp=opp, plays=s["plays"].mean(), pass_att=s["att"].mean(), rush_att=s["rush"].mean(),
                                   pass_rate=s["prate"].mean(), sacks_taken=s["sacks"].mean(), pass_yds=s["team_pass_yds"].mean(), rush_yds=s["rush_yds"].mean(),
                                   off_td=s["td"].mean(), pass_td=s["ptd_n"].mean(), rush_td=s["rtd_n"].mean(), fg=s["fg"].mean(), ints=s["int_n"].mean(), p_start_qb=s["p_start"],
                                   exp_ypa=s["ypa"], exp_ypc=s["ypc"], inj_ol=s["io"]["ol"], inj_cb_opp=s["idf"]["cb"], inj_pr_opp=s["idf"]["pr"]))
    # ----- timeline / team-game props -----
    Tt, Pp, Tm, Ty = timeline(sides, away, home, rng, ns)
    fin = np.isfinite(Tt)
    first_ix = np.where(fin.any(axis=1), 0, -1)
    first_team = np.where(fin[:, 0], Tm[:, 0], -1); first_type = np.where(fin[:, 0], Ty[:, 0], -1)
    last_idx = np.where(fin.any(axis=1), fin.sum(axis=1) - 1, 0)
    last_team = np.where(fin.any(axis=1), np.take_along_axis(Tm, last_idx[:, None], 1)[:, 0], -1)
    gp = []
    nm2 = {0: away, 1: home}
    def add(cat, name, p): gp.append(dict(game=f"{away}@{home}", category=cat, market=name, prob=float(p), fair_odds=american(p) if 0 < p < 1 else None))
    for ti in (0, 1):
        add("first_team_to_score", nm2[ti], (first_team == ti).mean()); add("last_team_to_score", nm2[ti], (last_team == ti).mean())
    add("first_team_to_score", "No score", (first_team == -1).mean())
    for ty, nmty in ((0, "TD"), (1, "Defense/ST TD"), (2, "FG"), (3, "Safety")): add("first_scoring_play", nmty, (first_type == ty).mean())
    cum = {}
    for ti in (0, 1):
        cum[ti] = np.cumsum(np.where(Tm == ti, Pp, 0), axis=1)
    for X in (10, 15, 20):
        tt = {}
        for ti in (0, 1):
            hit = (cum[ti] >= X) & fin; ix = np.argmax(hit, axis=1); ok = hit.any(axis=1)
            tt[ti] = np.where(ok, np.take_along_axis(Tt, ix[:, None], 1)[:, 0], np.inf)
        for ti in (0, 1): add(f"race_to_{X}", nm2[ti], ((tt[ti] < tt[1 - ti])).mean())
        add(f"race_to_{X}", "Neither", ((tt[0] == np.inf) & (tt[1] == np.inf)).mean())
    # quarter / half points
    qp = {}
    for ti in (0, 1):
        for qi in range(4):
            qp[(ti, qi)] = np.where((Tm == ti) & (np.floor(Tt / 15) == qi) & fin, Pp, 0).sum(axis=1)
    qtot = np.stack([qp[(0, qi)] + qp[(1, qi)] for qi in range(4)], axis=1)
    mx = qtot.max(axis=1, keepdims=True); tie = (qtot == mx)
    for qi in range(4): add("highest_scoring_quarter", f"Q{qi+1}", (tie[:, qi] / tie.sum(axis=1)).mean())
    for nm, arr in (("1H", qtot[:, 0] + qtot[:, 1]), ("2H", qtot[:, 2] + qtot[:, 3]), ("Q1", qtot[:, 0]), ("Q2", qtot[:, 1]), ("Q3", qtot[:, 2]), ("Q4", qtot[:, 3])):
        a = np.percentile(arr, [25, 50, 75]); game_prop_rows.append(dict(game=f"{away}@{home}", team="GAME", period=nm, mean=float(arr.mean()), p25=a[0], p50=a[1], p75=a[2]))
    for ti in (0, 1):
        for nm, arr in (("1H", qp[(ti, 0)] + qp[(ti, 1)]), ("2H", qp[(ti, 2)] + qp[(ti, 3)]), ("Q1", qp[(ti, 0)]), ("Q2", qp[(ti, 1)]), ("Q3", qp[(ti, 2)]), ("Q4", qp[(ti, 3)])):
            a = np.percentile(arr, [25, 50, 75]); game_prop_rows.append(dict(game=f"{away}@{home}", team=nm2[ti], period=nm, mean=float(arr.mean()), p25=a[0], p50=a[1], p75=a[2]))
    add("score_final_2min_1H", "Yes", (((Tt >= 28) & (Tt < 30)) & fin).any(axis=1).mean()); add("score_final_2min_2H", "Yes", (((Tt >= 58) & (Tt < 60)) & fin).any(axis=1).mean())
    add("overtime", "Yes", (M == 0).mean())
    for ti, (s, sg) in enumerate(((A, 1), (H, -1))):
        mg = (M if ti == 1 else -M)
        for lo, hi, lab in ((1, 6, "1-6"), (7, 12, "7-12"), (13, 18, "13-18"), (19, 24, "19-24"), (25, 99, "25+")): add("winning_margin", f"{nm2[ti]} {lab}", ((mg >= lo) & (mg <= hi)).mean())
    # team counting props
    for nm, s, o in ((away, A, H), (home, H, A)):
        for name, arr in (("team_tds", s["td"] + s["dtd"]), ("field_goals_made", s["fg"]), ("team_sacks_made", o["sacks"]), ("turnovers_forced", o["int_n"] + o["fl_n"] * 0 + s["fl_n"] * 0 + o["fl_n"] * 0)):
            pass
    for nm, s, o in ((away, A, H), (home, H, A)):
        team_prop_rows.append(dict(game=f"{away}@{home}", team=nm, opp=(home if nm == away else away), market="team_tds", **{k: v for k, v in zip(("mean", "p25", "p50", "p75"), (float((s['td'] + s['dtd']).mean()),) + tuple(np.percentile(s['td'] + s['dtd'], [25, 50, 75])))}))
        team_prop_rows.append(dict(game=f"{away}@{home}", team=nm, opp=(home if nm == away else away), market="field_goals_made", **{k: v for k, v in zip(("mean", "p25", "p50", "p75"), (float(s['fg'].mean()),) + tuple(np.percentile(s['fg'], [25, 50, 75])))}))
        dsk = o["sacks"]; tof = o["int_n"] + s["fl_n"] * 0 + 0   # offense o's turnovers = its INT + fumbles lost
        tof = o["int_n"] + o["fl_n"]
        team_prop_rows.append(dict(game=f"{away}@{home}", team=nm, opp=(home if nm == away else away), market="sacks_made (Proxy)", mean=float(dsk.mean()), p25=np.percentile(dsk, 25), p50=np.percentile(dsk, 50), p75=np.percentile(dsk, 75)))
        team_prop_rows.append(dict(game=f"{away}@{home}", team=nm, opp=(home if nm == away else away), market="turnovers_forced (Proxy)", mean=float(tof.mean()), p25=np.percentile(tof, 25), p50=np.percentile(tof, 50), p75=np.percentile(tof, 75)))
    # longest TD / FG (Proxy distributions)
    def longest_td():
        pl_ = np.where(np.arange(8)[None, :] < (A["ptd_n"] + H["ptd_n"])[:, None], np.minimum(1 + rng.exponential(15, (ns, 8)), 99), 0).max(axis=1)
        rl_ = np.where(np.arange(8)[None, :] < (A["rtd_n"] + H["rtd_n"])[:, None], np.minimum(1 + rng.exponential(6.5, (ns, 8)), 99), 0).max(axis=1)
        dl_ = np.where(np.arange(4)[None, :] < (A["dtd"] + H["dtd"])[:, None], rng.uniform(15, 99, (ns, 4)), 0).max(axis=1)
        return np.maximum.reduce([pl_, rl_, dl_])
    ltd = longest_td()
    lfg = np.where(np.arange(8)[None, :] < (A["fg"] + H["fg"])[:, None], np.clip(rng.normal(39.5, 8.5, (ns, 8)), 19, 66), 0).max(axis=1)
    for nm, arr in (("longest_td_yds (Proxy)", ltd), ("longest_fg_yds (Proxy)", lfg)):
        a = np.percentile(arr, [25, 50, 75]); game_prop_rows.append(dict(game=f"{away}@{home}", team="GAME", period=nm, mean=float(arr.mean()), p25=a[0], p50=a[1], p75=a[2]))
    for x in gp: x["note"] = game_note
    ql_rows.extend(gp)
    # ----- players -----
    Ttot = np.maximum(A["td"] + H["td"] + A["dtd"] + H["dtd"], 1)
    for t in (away, home):
        s = sides[t]; opp = home if t == away else away
        for pl in players[t]:
            m = pl["mask"]
            nact = int(m.sum())
            r = pl["row"]
            ev = pl["p_active"] * float(pl["fp"][m].mean()) if nact > 50 else 0.0
            qf = q(pl["fp"], m) if nact > 50 else q(np.zeros(1))
            rank_rows.append(dict(player=pl["player"], pos=pl["pos"], team=t, opp=opp, game=f"{away}@{home}", note=game_note, p_active=pl["p_active"], ev_pts=ev,
                                  median_if_active=qf["p50"], p25=qf["p25"], p75=qf["p75"], p90=qf["p90"], mean_if_active=qf["mean"], injury=inj_flag(pl),
                                  team_implied_pts=float(s["pts"].mean()), proxy=pl.get("proxy", False)))
            if nact < 200 or pl["p_active"] < .03: continue
            key = pl["player"]
            drv = drivers(pl, s)
            mk = {}
            if pl["pos"] == "QB":
                for k in ("pass_yds", "pass_att", "pass_cmp", "pass_td", "pass_int", "pass_long", "rush_yds", "rush_att", "rush_td"): mk[k] = pl[k]
                mk["pass_rush_yds"] = pl["pass_yds"] + pl["rush_yds"]
                mk["rush_long"] = pl["rush_long"]
                if pl["rush_att"][m].mean() < 2.0: [mk.pop(k) for k in ("rush_yds", "rush_att", "rush_long")]
            else:
                if pl["rush_att"][m].mean() >= 3.0:
                    for k in ("rush_yds", "rush_att", "rush_long"): mk[k] = pl[k]
                if pl["rec"][m].mean() >= 1.0:
                    for k in ("rec_yds", "rec", "rec_long"): mk[k] = pl[k]
                if "rush_yds" in mk and "rec_yds" in mk: mk["rush_rec_yds"] = pl["rush_yds"] + pl["rec_yds"]
            for k, x in mk.items():
                if k in ("rush_td",): continue
                xm = x[m]
                lc, po = fair_line(xm); qq = q(x, m)
                rows_mk.append(dict(player=key, team=t, opp=opp, pos=pl["pos"], game=f"{away}@{home}", market=k, fair_line=lc, median=qq["p50"], p25=qq["p25"], p75=qq["p75"], p90=qq["p90"], mean=qq["mean"],
                                    over_pct=po, fair_odds_over=american(po), fair_odds_under=american(1 - po), edge="n/a (no line supplied)", confidence=grade(pl, k),
                                    key_drivers=drv, injury_flag=inj_flag(pl), p_active=pl["p_active"], note=game_note, proxy_label=("Proxy" if pl.get("proxy") else "")))
                for th in LADDER.get(k, []):
                    pt = float((xm >= th).mean())
                    if .02 <= pt <= .985: rows_lad.append(dict(player=key, team=t, opp=opp, market=k, threshold=th, prob_at_least=pt, fair_odds=american(pt), p_active=pl["p_active"], note=game_note))
            # TD markets
            tdc = (pl["rush_td"] + pl["rec_td"] + (0 if pl["pos"] != "QB" else 0))[m]
            tdc_all = (pl["rush_td"] + pl["rec_td"])
            pany = float((tdc >= 1).mean())
            if pany >= .015:
                pfirst = float((tdc_all[m] / Ttot[m]).mean()); p2 = float((tdc >= 2).mean())
                for mkt, pr in (("anytime_td", pany), ("first_td", pfirst), ("last_td", pfirst), ("2plus_td", p2)):
                    rows_td.append(dict(player=key, team=t, opp=opp, pos=pl["pos"], game=f"{away}@{home}", market=mkt, prob=pr, fair_odds=american(pr) if pr > 0 else None,
                                        rush_td_mean=float(pl["rush_td"][m].mean()), rec_td_mean=float(pl["rec_td"][m].mean()), confidence=grade(pl, mkt), injury_flag=inj_flag(pl),
                                        key_drivers=drv, p_active=pl["p_active"], note=game_note))
    # ----- kickers -----
    for t in (away, home):
        s = sides[t]; k = kicker(t)
        if k is None: continue
        pts = 3 * s["fg"] + s["xp_off"] + s["xp_d"]
        a = percentile = np.percentile(pts, [25, 50, 75, 90])
        kp = INJ[(INJ.team == t) & (INJ.nkey == norm_name(k.player))]
        pact = float(kp.p_active.iloc[0]) if len(kp) else 1.0
        kd_rows.append(dict(player=k.player, pos="K", team=t, opp=(home if t == away else away), game=f"{away}@{home}", note=game_note, p_active=pact, ev_pts=pact * float(pts.mean()), median_if_active=a[1], p25=a[0], p75=a[2], p90=a[3],
                            fg_made_mean=float(s["fg"].mean()), xp_made_mean=float((s["xp_off"] + s["xp_d"]).mean()), injury="-" if not len(kp) else inj_flag(dict(status=kp.game_status.iloc[0], practice=kp.practice.iloc[0])), team_implied_pts=float(s["pts"].mean()), proxy=False))
    # ----- DST -----
    for t in (away, home):
        o = sides[home if t == away else away]; s = sides[t]
        pa = o["off_pts"]
        fp_ = dst_pts(o["sacks"], o["int_n"], o["fl_n"], s["dtd"], s["saf"], pa)
        a = np.percentile(fp_, [25, 50, 75, 90])
        kd_rows.append(dict(player=f"{t} DST", pos="DST", team=t, opp=(home if t == away else away), game=f"{away}@{home}", note=game_note, p_active=1.0, ev_pts=float(fp_.mean()), median_if_active=a[1], p25=a[0], p75=a[2], p90=a[3],
                            sacks_mean=float(o["sacks"].mean()), takeaways_mean=float((o["int_n"] + o["fl_n"]).mean()), pa_mean=float(pa.mean()), injury="-", team_implied_pts=float(s["pts"].mean()), proxy=True))
    STORE[(away, home)] = dict(A=A, H=H, players=players, M=M)
    print(f"{away}@{home} done {time.time()-t0:.1f}s  home_win={win_h:.3f}  total={np.median(tot):.1f}  margin={np.median(M):+.1f}", flush=True)

if __name__ == "__main__":
    for _, r in SCHED.iterrows():
        run_game(r.away, r.home, neutral=bool(r.neutral))
    O = OUT
    pd.DataFrame(env_rows).to_csv(O + "w4_game_environment.csv", index=False)
    pd.DataFrame(rows_mk).to_csv(O + "w4_player_props_fair_lines.csv", index=False)
    pd.DataFrame(rows_lad).to_csv(O + "w4_player_alt_ladders.csv", index=False)
    pd.DataFrame(rows_td).to_csv(O + "w4_td_markets.csv", index=False)
    pd.DataFrame(rank_rows + kd_rows).to_pickle(O + "rank_raw.pkl")
    pd.DataFrame(team_prop_rows).to_csv(O + "w4_team_props_raw.csv", index=False)
    pd.DataFrame(game_prop_rows).to_csv(O + "w4_period_totals.csv", index=False)
    pd.DataFrame(ql_rows).to_csv(O + "w4_game_props.csv", index=False)
    print("written")
