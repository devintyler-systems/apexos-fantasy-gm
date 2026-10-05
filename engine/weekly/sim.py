"""Correlated Monte Carlo game simulator (deterministic seed). One call = one game, NS sims.

Order (per v1 s4): environment (total/script/pace) -> team plays -> pass/rush split -> player share ->
efficiency -> TD. All player stat lines are drawn conditional on a shared per-team latent (z) so QB and
pass-catcher outputs move together, and on the shared scoring draw so team totals bound player TDs.
"""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, json
from params import *
CAL = json.load(open(CONF+"calibration_params.json"))
# Team-volume dispersion and target-share cap. APEX_VOLFILE overrides the file (used by the backtests to compare variants).
# Defaults reproduce the pre-2026-10-05 behaviour so an absent file changes nothing.
import os as _os
VOL = dict(plays_sd=4.0, pr_margin_slope=0.0022, pr_extra_sd=0.0, pr_cap=0.08, plays_lo=42, plays_hi=85, tgt_share_cap=0.0)
_vf = _os.environ.get("APEX_VOLFILE", CONF + "volume_params.json")
if _os.path.exists(_vf):
    VOL.update({k: v for k, v in json.load(open(_vf)).items() if not k.startswith("_")})

NS = 20000
SEED = 20261004
ALPHA_T = 100.0  # Dirichlet concentration for target shares (calibrated vs 2025 weekly logs)
ALPHA_C = 60.0   # carries
MAXC = 12   # per-catch draws kept
MAXR = 26   # per-carry draws kept

def _norm(w):
    w = np.clip(w, 1e-12, None); return w / w.sum(axis=1, keepdims=True)

def _alloc(rng, counts, weights):
    """counts (ns,), weights (ns,K) -> (ns,K) multinomial draw."""
    p = _norm(weights)
    p[:, -1] = np.clip(1 - p[:, :-1].sum(axis=1), 0, 1)
    return rng.multinomial(counts.astype(np.int64), p)

def _gamma_sum(rng, cnt, mean, shape, maxc):
    """sum and max of cnt iid gamma(shape, mean/shape) draws; cnt (ns,), mean scalar or (ns,)"""
    ns = cnt.shape[0]
    d = rng.gamma(shape, 1.0, size=(ns, maxc)) * (np.asarray(mean).reshape(-1, 1) / shape if np.ndim(mean) else mean / shape)
    m = np.arange(maxc)[None, :] < cnt[:, None]
    tot = (d * m).sum(axis=1); lng = np.where(m, d, 0).max(axis=1)
    extra = np.clip(cnt - maxc, 0, None) * (mean if np.ndim(mean) == 0 else np.asarray(mean))
    return tot + extra, lng

def _rush_draws(rng, cnt, mean, maxc):
    ns = cnt.shape[0]
    mean = np.broadcast_to(np.asarray(mean, dtype=float), (ns,))
    pe = 0.045; mu_b = np.maximum((mean - pe * 19.0) / (1 - pe), 1.2).reshape(-1, 1)
    base = rng.gamma(1.7, 1.0, size=(ns, maxc)) * (mu_b + 1.0) / 1.7 - 1.0
    ex = rng.random((ns, maxc)) < pe
    exd = rng.gamma(2.0, 9.5, size=(ns, maxc)) + 6.0
    d = np.clip(np.where(ex, exd, base), -6, 99)
    m = np.arange(maxc)[None, :] < cnt[:, None]
    tot = (d * m).sum(axis=1) + np.clip(cnt - maxc, 0, None) * mean
    lng = np.where(m, d, -99).max(axis=1); lng = np.where(cnt > 0, lng, 0)
    return tot, lng

def q(x, mask=None):
    if mask is not None: x = x[mask]
    if x.size == 0: return dict(mean=np.nan, p10=np.nan, p25=np.nan, p50=np.nan, p75=np.nan, p90=np.nan)
    a = np.percentile(x, [10, 25, 50, 75, 90])
    return dict(mean=float(x.mean()), p10=a[0], p25=a[1], p50=a[2], p75=a[3], p90=a[4])

def sim_game(away, home, neutral, rng, ns=NS):
    env = game_env(away, home, neutral)
    sides = {away: dict(opp=home, home=False), home: dict(opp=away, home=True)}
    g = rng.normal(0, .07, ns)
    S = {}
    for t, s in sides.items():
        P, O = TEAM[t], TEAM[s["opp"]]
        io, idf = inj_groups(t), inj_groups(s["opp"])
        e = rng.normal(0, .12, ns)
        qbs = qb_list(t)
        p_start = float(qbs.loc[0, "p_active"]) if len(qbs) else 1.0
        start = rng.random(ns) < p_start
        qm = np.where(start, 1.0, 0.92)           # backup QB efficiency multiplier (Proxy)
        s.update(dict(P=P, O=O, io=io, idf=idf, e=e, qbs=qbs, start=start, p_start=p_start))
        # environment-level expected rates
        s["ypa"] = P["ypa"] * O["d_ypa"] ** 0.9 * (1 - 0.015 * io["ol"]) * (1 + 0.025 * idf["cb"] + 0.012 * idf["s"] + 0.01 * idf["pr"])
        s["cmp"] = np.clip(P["cmp"] * O["d_cmp"] ** 0.8, .5, .78)
        s["int"] = P["int"] * O["d_int"] ** 0.6 * (1 - 0.04 * idf["cb"])
        s["sk"] = P["sk"] * O["d_sk"] ** 0.7 * (1 + 0.10 * io["ol"]) * (1 - 0.05 * idf["pr"])
        s["ypc"] = P["ypc"] * O["d_ypc"] ** 0.9 * (1 - 0.02 * io["ol"]) * (1 + 0.01 * idf["lb"])
        s["ptd"] = float(np.clip(P["ptd"] * O["d_ptd"] ** 0.5, .38, .85))
        s["plays"] = 0.5 * (P["plays_off"] + O["plays_def"])
        s["qm"] = qm
        pts = env[t]
        lam_fg = P["fg"] * (O["def_ppg"] / L["ppg"]) ** 0.0
        s["lam_fg"] = lam_fg
        s["lam_td"] = max((pts - 3 * lam_fg - 6.96 * L["dtd"] - 2 * L["saf"]) / 6.96, 0.4)
    # --- scoring draw ---
    for t, s in sides.items():
        lam = s["lam_td"] * np.exp(g + s["e"] - 0.5 * (.07 ** 2 + .12 ** 2))
        s["td"] = rng.binomial(8, np.clip(lam / 8.0, 0.01, 0.95))   # drive-limited (~12 scoring chances), under-dispersed vs Poisson
        s["fg"] = rng.binomial(4, np.clip(s["lam_fg"] * np.exp(-0.25 * s["e"]) / 4.0, 0.01, 0.95))
        s["dtd"] = rng.poisson(L["dtd"], ns)
        s["saf"] = rng.poisson(L["saf"], ns)
        s["xp_off"] = rng.binomial(s["td"], L["xp"]); s["xp_d"] = rng.binomial(s["dtd"], L["xp"])
        s["off_pts"] = 6 * s["td"] + s["xp_off"] + 3 * s["fg"]
    for t, s in sides.items():
        o = sides[s["opp"]]
        s["pts"] = s["off_pts"] + 6 * s["dtd"] + s["xp_d"] + 2 * s["saf"]  # offense + own def/ST TDs + own defensive safeties
        s["pa_off"] = o["off_pts"]
    A, H = sides[away], sides[home]
    marg_h = H["pts"] - A["pts"]
    for t, s in sides.items():
        M = marg_h if not s["home"] else marg_h
        M = (H["pts"] - A["pts"]) if s["home"] else (A["pts"] - H["pts"])
        s["M"] = M
        s["z"] = 0.8 * (s["e"] / .12) + 0.6 * rng.normal(size=ns)
        extra = rng.normal(0.0, VOL["pr_extra_sd"], ns) if VOL["pr_extra_sd"] > 0 else 0.0     # play-calling noise beyond the binomial
        pr = np.clip(s["P"]["pr"] + VOL["pr_margin_slope"] * (-M) + extra, s["P"]["pr"] - VOL["pr_cap"], s["P"]["pr"] + VOL["pr_cap"])
        plays = np.clip(rng.normal(s["plays"] * (1 + 0.03 * g), VOL["plays_sd"]), VOL["plays_lo"], VOL["plays_hi"]).round().astype(int)
        db = rng.binomial(plays, np.clip(pr, .35, .78))
        sk = rng.binomial(db, np.clip(s["sk"] * s["qm"] ** -1, .01, .2))
        att = db - sk
        s.update(plays=plays, db=db, sacks=sk, att=att, rush=plays - db, prate=pr)
        logit0 = np.log(s["ptd"] / (1 - s["ptd"]))
        pp = 1 / (1 + np.exp(-(logit0 + 0.30 * s["z"] + 2.0 * (pr - s["P"]["pr"]))))
        s["ptd_n"] = rng.binomial(s["td"], pp); s["rtd_n"] = s["td"] - s["ptd_n"]
        s["fl_n"] = rng.poisson(L["fl"] * s["O"]["d_fl"] ** 0.5, ns)
        s["int_n"] = rng.binomial(att, np.clip(s["int"] * (1 / s["qm"]) ** 1.5 * np.exp(-0.15 * s["z"]), .002, .12))
    return env, sides, g

def play_side(rng, t, sd, ns):
    """Players for one offense. Returns list of player result dicts and QB/K/team arrays."""
    z = sd["z"]; att = sd["att"]
    roster, oth_t, oth_c = build_roster(t)
    rec = roster[roster.pos.isin(["WR", "TE", "RB"])].reset_index(drop=True)
    rus = roster[(roster.Rushing_Att > 0) | (roster.pos.isin(["QB"])) | ((roster.pos == "RB") & (roster.car_sh > .005))].reset_index(drop=True)
    qbs = sd["qbs"]; start = sd["start"]
    out = []
    avail = {}   # ONE availability draw per player, shared by receiving and rushing
    def av(pid, p):
        if pid not in avail: avail[pid] = rng.random(ns) < p
        return avail[pid]
    # ---------------- receiving ----------------
    K = len(rec)
    base_sh = np.append(rec.tgt_sh.values, oth_t) * np.append(rec.tilt.values, 1.0)
    # reconcile catch rate and ypr to team means
    catch0 = np.append(rec.catch.values, 0.64)
    ypr0 = np.append(rec.ypr.values, 11.0)
    sh = base_sh / base_sh.sum()
    cs = np.clip(sd["cmp"] * (1 / (sh @ catch0)), .88, 1.12)
    catch = np.clip(catch0 * cs, .25, .93)
    att_mean = float(att.mean())
    sc_y = np.clip(sd["ypa"] * att_mean / (att_mean * (sh * catch) @ ypr0), .8, 1.3)
    ypr = ypr0 * sc_y
    pa = np.append(rec.p_active.values, 1.0)
    act = np.ones((ns, K + 1), dtype=bool)
    for k in range(K): act[:, k] = av(rec.pfr_id.iloc[k], float(rec.p_active.iloc[k]))
    # limited/questionable haircut
    hair = np.ones(K + 1)
    for i, r in rec.iterrows():
        if r.p_active < 1.0 and r.game_status in ("Questionable", "Doubtful"): hair[i] = 0.93
    if VOL["tgt_share_cap"] > 0:      # cap each pass catcher's EXPECTED share (given he plays); vacated targets spill to the others
        capv = float(VOL["tgt_share_cap"]); w0 = base_sh.copy()
        for _ in range(8):
            W = w0[None, :] * act * hair[None, :]; W = W / np.maximum(W.sum(axis=1, keepdims=True), 1e-12)
            over = False
            for k in range(K):
                a_k = act[:, k]
                if a_k.sum() == 0: continue
                m_k = float(W[a_k, k].mean())
                if m_k > capv * 1.005: w0[k] *= capv / m_k; over = True
            if not over: break
        sh = w0 / w0.sum()
    G = rng.gamma(np.maximum(ALPHA_T * sh, 1e-3)[None, :], 1.0, size=(ns, K + 1))
    wts = G * act * hair[None, :]
    wts = wts / wts.sum(axis=1, keepdims=True)
    tg = _alloc(rng, att, wts)
    ceff = np.clip(catch[None, :] * np.exp(0.07 * z)[:, None], .2, .95)
    rc = rng.binomial(tg, ceff)
    ptd_adj = np.clip(1 + 0.11 * (sd["ptd_n"] - sd["ptd_n"].mean()), .75, 1.35)
    rtd_adj = np.clip(1 + 0.08 * (sd["rtd_n"] - sd["rtd_n"].mean()), .75, 1.4)
    yd = np.zeros((ns, K + 1)); lg = np.zeros((ns, K + 1))
    for k in range(K + 1):
        yd[:, k], lg[:, k] = _gamma_sum(rng, rc[:, k], ypr[k] * np.exp(0.10 * z) * ptd_adj, 1.8, MAXC)
    lg = np.clip(lg, 0, 99)
    # TDs: pass TDs to receivers
    wtd = np.append(rec.w_rec_td.values, oth_t * 0.9) * act
    rtd = _alloc(rng, sd["ptd_n"], wtd + 1e-9)
    team_pass_yds = yd.sum(axis=1); team_cmp = rc.sum(axis=1)
    # ---------------- rushing ----------------
    R = len(rus)
    cb = np.append(rus.car_sh.values, oth_c)
    if R == 0: cb = np.array([1.0])
    sh_c = cb / cb.sum()
    pr_ = np.append(rus.p_active.values, 1.0)
    act_c = np.ones((ns, R + 1), dtype=bool)
    for j in range(R):
        if rus.pos.iloc[j] != "QB": act_c[:, j] = av(rus.pfr_id.iloc[j], float(rus.p_active.iloc[j]))   # QB availability handled by start flag
    # starter QB inactive: his carries move to backup QB proxy (appended row)
    qb_idx = [i for i, r in rus.iterrows() if r.pos == "QB" and r.player == (qbs.loc[0, "player"] if len(qbs) else "")]
    bk = np.zeros((ns, 1))
    car_w = rng.gamma(np.maximum(ALPHA_C * sh_c, 1e-3)[None, :], 1.0, size=(ns, R + 1)) * act_c
    if qb_idx:
        qi = qb_idx[0]
        car_w[:, qi] = car_w[:, qi] * start
        extra = (rng.gamma(ALPHA_C * sh_c[qi], 1.0, size=ns) * (~start)).reshape(-1, 1)
        car_w = np.hstack([car_w, extra])
    else:
        car_w = np.hstack([car_w, np.zeros((ns, 1))])
    car_w = car_w / car_w.sum(axis=1, keepdims=True)
    ca = _alloc(rng, sd["rush"], car_w)
    ypc0 = np.append(rus.ypc.values, 4.0); ypc0 = np.append(ypc0, rus.ypc.values[qb_idx[0]] * 0.9 if qb_idx else 4.0)
    mcar = (car_w.mean(axis=0) * sd["rush"].mean())
    scy = np.clip(sd["ypc"] * CAL["team_ypc"] / ((mcar * ypc0).sum() / mcar.sum()), .75, 1.3)
    ypc = ypc0 * scy
    ry = np.zeros((ns, R + 2)); rl = np.zeros((ns, R + 2))
    for k in range(R + 2):
        ry[:, k], rl[:, k] = _rush_draws(rng, ca[:, k], ypc[k] * np.exp(0.05 * z) * rtd_adj, MAXR)
    wr = np.append(np.append(rus.w_rush_td.values, oth_c * 0.9), 0.0)
    wr_m = np.tile(wr, (ns, 1)) * (car_w > 0) * 1.0
    if qb_idx: wr_m[:, R + 1] = rus.w_rush_td.values[qb_idx[0]] * (~start); wr_m[:, qb_idx[0]] = wr_m[:, qb_idx[0]] * start
    wr_m[:, :R + 1] = wr_m[:, :R + 1] * act_c
    rtds = _alloc(rng, sd["rtd_n"], wr_m + 1e-9)
    # ---------------- assemble player dicts ----------------
    def fp(p_yds=0, p_td=0, p_int=0, r_yds=0, r_td=0, rec_=0, rec_yds=0, rec_td=0, fl=0):
        return 0.04 * p_yds + 4 * p_td - 2 * p_int + 0.1 * (r_yds + rec_yds) + 6 * (r_td + rec_td) + 1.0 * rec_ - 2 * fl
    # QB(s)
    qb_rows = []
    nq = len(qbs)
    qb1 = qbs.loc[0] if nq else None
    qb_name = qb1.player if nq else f"{t} QB1"
    sd["qb_name"] = qb_name
    # backup QB identity: second QB with attempts else proxy
    bq = qbs.loc[1] if nq > 1 else None
    bname = bq.player if bq is not None else f"{t} QB2 (Proxy)"
    qb_ci = qb_idx[0] if qb_idx else None
    for nm, who, mask, pact in ((qb_name, qb1, start, sd["p_start"]), (bname, bq, ~start, 1 - sd["p_start"])):
        if pact < 0.03 and nm != qb_name: continue
        if pact < 0.02: pass
        rc_idx = qb_ci if (nm == qb_name and qb_ci is not None) else None
        rush_a = ca[:, qb_ci] if (nm == qb_name and qb_ci is not None) else (ca[:, R + 1] if nm != qb_name else np.zeros(ns))
        rush_y = ry[:, qb_ci] if (nm == qb_name and qb_ci is not None) else (ry[:, R + 1] if nm != qb_name else np.zeros(ns))
        rush_l = rl[:, qb_ci] if (nm == qb_name and qb_ci is not None) else (rl[:, R + 1] if nm != qb_name else np.zeros(ns))
        rush_t = rtds[:, qb_ci] if (nm == qb_name and qb_ci is not None) else (rtds[:, R + 1] if nm != qb_name else np.zeros(ns))
        fl = rng.poisson(0.012 * sd["db"] / 1.0 * 0.45)
        pint = sd["int_n"]
        if nm == qb_name:     # starter takes ~93% of team dropbacks (early exits, garbage time): calibrated on 2023-25 weeks 4-12
            fq = CAL["qb_share"]; q_py = team_pass_yds * fq; q_pc = rng.binomial(team_cmp.astype(np.int64), fq); q_pa = rng.binomial(att.astype(np.int64), fq)
            q_ptd = rng.binomial(sd["ptd_n"].astype(np.int64), CAL["qb_td"]); pint = rng.binomial(pint.astype(np.int64), fq)
        else:
            q_py, q_pc, q_pa, q_ptd = team_pass_yds, team_cmp, att, sd["ptd_n"]
        pf = fp(p_yds=q_py, p_td=q_ptd, p_int=pint, r_yds=rush_y, r_td=rush_t, fl=fl)
        out.append(dict(player=nm, pos="QB", team=t, mask=mask, p_active=float(pact),
                        pass_yds=q_py, pass_att=q_pa, pass_cmp=q_pc, pass_td=q_ptd, pass_int=pint,
                        pass_long=lg.max(axis=1), rush_yds=rush_y, rush_att=rush_a, rush_long=rush_l, rush_td=rush_t,
                        rec=np.zeros(ns), rec_yds=np.zeros(ns), rec_long=np.zeros(ns), rec_td=np.zeros(ns), tgt=np.zeros(ns), fp=pf,
                        row=qb1 if nm == qb_name else bq, status=(qb1.game_status if nm == qb_name and nq else None),
                        practice=(qb1.practice if nm == qb_name and nq else None), proxy=(nm != qb_name and bq is None)))
    # skill players: merge receiving + rushing entries by pfr_id
    seen = {}
    for i, r in rec.iterrows():
        seen[r.pfr_id] = dict(row=r, ri=i, ci=None)
    for i, r in rus.iterrows():
        if r.pos == "QB": continue
        if r.pfr_id in seen: seen[r.pfr_id]["ci"] = i
        else: seen[r.pfr_id] = dict(row=r, ri=None, ci=i)
    for pid, d in seen.items():
        r = d["row"]; ri, ci = d["ri"], d["ci"]
        z0 = np.zeros(ns)
        rcv = dict(rec=rc[:, ri], rec_yds=yd[:, ri], rec_long=lg[:, ri], rec_td=rtd[:, ri], tgt=tg[:, ri]) if ri is not None else dict(rec=z0, rec_yds=z0, rec_long=z0, rec_td=z0, tgt=z0)
        rsh = dict(rush_att=ca[:, ci], rush_yds=ry[:, ci], rush_long=rl[:, ci], rush_td=rtds[:, ci]) if ci is not None else dict(rush_att=z0, rush_yds=z0, rush_long=z0, rush_td=z0)
        touches = rcv["rec"] + rsh["rush_att"]
        fl = rng.poisson(0.005 * touches)
        pf = fp(r_yds=rsh["rush_yds"], r_td=rsh["rush_td"], rec_=rcv["rec"], rec_yds=rcv["rec_yds"], rec_td=rcv["rec_td"], fl=fl)
        mask = act[:, ri] if ri is not None else act_c[:, ci]
        if ri is not None and ci is not None: mask = act[:, ri]
        out.append(dict(player=r.player, pos=r.pos, team=t, mask=mask, p_active=float(r.p_active), pfr_id=pid,
                        pass_yds=z0, pass_att=z0, pass_cmp=z0, pass_td=z0, pass_int=z0, pass_long=z0,
                        fp=pf, row=r, status=r.game_status, practice=r.practice, proxy=False, **rcv, **rsh))
    # team-level bookkeeping
    sd["team_pass_yds"] = team_pass_yds; sd["team_cmp"] = team_cmp
    sd["rush_yds"] = ry.sum(axis=1); sd["rush_td_alloc"] = rtds.sum(axis=1); sd["rec_td_alloc"] = rtd.sum(axis=1)
    sd["long_comp"] = lg.max(axis=1)
    return out
