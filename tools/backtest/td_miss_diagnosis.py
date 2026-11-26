"""DECISIONS #87: when is the engine's anytime-TD disagreement with the book information, and when is it error? Post-sim, no engine change, no API calls.

  python tools/backtest/td_miss_diagnosis.py TAG [TAG ...]
Needs var/bt/odds_td_{TAG}.pkl (odds_price_eval.py td) and var/bt/odds_early_{TAG}.pkl (odds_early_eval.py).

Model (logistic, fitted by penalised likelihood): logit p = i + a*Lb + b*Le + sum_k c_k * f_k * (Le - Lb) + d_k * f_k,
Lb = logit(book consensus), Le = logit(engine). L2 on c, d only (features standardised); lambda picked by inner leave-one-season-out.
Every score is leave-one-season-out. Baselines: book, the fixed w0.2 blend, and the 2-parameter stack (i, a, b).
Features (all knowable before kickoff of week W; look-ahead check in FEAT_DOC).
"""
import os, sys
import numpy as np, pandas as pd
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(__file__))
import odds_price_eval as ope  # noqa: E402
from odds_price_eval import ll, br, NFLV, NV2T, REPO, norm_name  # noqa: E402

RNG = np.random.default_rng(87)
lg = lambda p: np.log(np.clip(p, .005, .995) / (1 - np.clip(p, .005, .995))); ex = lambda x: 1 / (1 + np.exp(-x))
FEAT_DOC = {
    "big_gap": "|engine - book| >= 10 pts (both inputs pre-kickoff)",
    "neg_gap": "engine below the book",
    "role_chg": "offense snap share, mean of last 3 games played minus season mean, weeks < W (snap_counts)",
    "low_gp": "missed 2+ of the team's games before W (games played < W-2); 'games played < 4' alone is just 'week 4-5' here",
    "rookie": "roster years_exp == 0 (season-level roster)",
    "new_team": "team differs from the player's last team in season S-1 (stats_player_week)",
    "on_report": "any entry on week W's injury report (final report, published before kickoff)",
    "mate_out": "a teammate at the same position listed Out on week W's report",
    "backup_qb": "the team's projected QB1 this week is not the QB with the most week-1 attempts",
    "implied": "team implied points from nflverse total_line / spread_line (closing-ish, pre-kickoff), standardised",
    "rz_minus": "player's share of team inside-20 targets+carries minus overall share, weeks < W (pbp), standardised",
    "is_RB": "position RB (WR is the base)", "is_TE": "position TE",
}   # p_active < 1 was dropped: in these pickles it is identical to on_report (same 17.5% of rows, same coefficients)
FEATS = list(FEAT_DOC)


def season_tables(S):
    st = pd.read_parquet(NFLV + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy()
    st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name)
    sn = pd.read_parquet(NFLV + f"snap_counts_{S}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.offense_snaps > 0)].copy()
    sn["team"] = sn.team.replace(NV2T); sn["nkey"] = sn.player.map(norm_name)
    pbp = pd.read_parquet(NFLV + f"play_by_play_{S}.parquet", columns=["season_type", "week", "posteam", "yardline_100", "rush_attempt", "pass_attempt", "receiver_player_id", "rusher_player_id"])
    pbp = pbp[pbp.season_type == "REG"].copy(); pbp["posteam"] = pbp.posteam.replace(NV2T)
    inj = pd.read_parquet(NFLV + f"injuries_{S}.parquet"); inj = inj[(inj.season_type if "season_type" in inj else inj.game_type) == "REG"].copy()
    inj["team"] = inj.team.replace(NV2T); inj["nkey"] = inj.full_name.map(norm_name)
    ro = pd.read_parquet(NFLV + f"roster_{S}.parquet"); ro["team"] = ro.team.replace(NV2T); ro["nkey"] = ro.full_name.map(norm_name)
    prev = pd.read_parquet(NFLV + f"stats_player_week_{S - 1}.parquet"); prev = prev[prev.season_type == "REG"].copy()
    prev["team"] = prev.team.replace(NV2T); prev["nkey"] = prev.player_display_name.map(norm_name)
    return st, sn, pbp, inj, ro, prev


def features(D, need):
    """one row per D index (all positions present in D); D carries season, week, team, nkey, pos, p_active, pass_yds."""
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[g.game_type == "REG"].copy()
    for c in ("home_team", "away_team"): g[c] = g[c].replace(NV2T)
    imp_t = {}
    for r in g.itertuples():
        if pd.notna(r.total_line) and pd.notna(r.spread_line):
            imp_t[(r.season, r.week, r.home_team)] = (r.total_line + r.spread_line) / 2; imp_t[(r.season, r.week, r.away_team)] = (r.total_line - r.spread_line) / 2
    out = []
    for S in sorted(D.season.unique()):
        st, sn, pbp, inj, ro, prev = season_tables(S)
        gid2n = dict(zip(st.player_id, st.nkey))
        last_team = prev.sort_values("week").groupby("nkey").team.last().to_dict()
        rook = set(zip(ro[ro.years_exp == 0].nkey, ro[ro.years_exp == 0].team))
        w1 = st[(st.week == st.week.min()) & (st.position == "QB")].sort_values("attempts", ascending=False).drop_duplicates("team")
        wk1qb = dict(zip(w1.team, w1.nkey))
        # inside-20 and overall usage (targets + carries) by player-week, from pbp
        ev = pd.concat([pbp[pbp.pass_attempt == 1][["week", "posteam", "yardline_100", "receiver_player_id"]].rename(columns={"receiver_player_id": "pid"}),
                        pbp[pbp.rush_attempt == 1][["week", "posteam", "yardline_100", "rusher_player_id"]].rename(columns={"rusher_player_id": "pid"})])
        ev = ev[ev.pid.notna()]; ev["rz"] = (ev.yardline_100 <= 20).astype(float); ev["nkey"] = ev.pid.map(gid2n)
        pw = ev.groupby(["week", "posteam", "nkey"]).agg(u=("rz", "size"), rz=("rz", "sum")).reset_index()
        tw = ev.groupby(["week", "posteam"]).agg(U=("rz", "size"), RZ=("rz", "sum")).reset_index()
        Ds = D[D.season == S]
        qb1 = Ds[Ds.pos == "QB"].sort_values("pass_yds", ascending=False).drop_duplicates(["week", "team"])
        qb1 = {(w, t): k for w, t, k in zip(qb1.week, qb1.team, qb1.nkey)}
        for W in sorted(Ds.week.unique()):
            d = Ds[Ds.week == W]
            s_ = sn[sn.week < W].sort_values("week"); gp = s_.groupby(["nkey", "team"]).size()
            last3 = s_.groupby(["nkey", "team"]).offense_pct.apply(lambda x: x.tail(3).mean()); allm = s_.groupby(["nkey", "team"]).offense_pct.mean()
            p_ = pw[pw.week < W].groupby(["posteam", "nkey"])[["u", "rz"]].sum(); t_ = tw[tw.week < W].groupby("posteam")[["U", "RZ"]].sum()
            iw = inj[inj.week == W]; onrep = set(zip(iw.team, iw.nkey)); outs = iw[iw.report_status == "Out"]
            outpos = set(zip(outs.team, outs.position, outs.nkey))
            for i, r in d[d.index.isin(need)].iterrows():
                k = (r.nkey, r.team); pk = (r.team, r.nkey)
                us = p_.loc[pk] if pk in p_.index else None; tt = t_.loc[r.team] if r.team in t_.index else None
                share = us.u / tt.U if us is not None and tt is not None and tt.U else 0.0
                rzs = us.rz / tt.RZ if us is not None and tt is not None and tt.RZ else 0.0
                out.append(dict(di=i, role_chg=float(last3.get(k, np.nan) - allm.get(k, np.nan)) if k in allm.index else 0.0,
                                low_gp=float(gp.get(k, 0) < W - 2), rookie=float(k in rook),
                                new_team=float(r.nkey in last_team and last_team[r.nkey] != r.team), on_report=float(pk in onrep),
                                mate_out=float(any(t == r.team and p == r.pos and n != r.nkey for t, p, n in outpos)),
                                backup_qb=float(qb1.get((W, r.team)) is not None and wk1qb.get(r.team) is not None and qb1[(W, r.team)] != wk1qb[r.team]),
                                implied=imp_t.get((S, W, r.team), np.nan), rz_minus=rzs - share,
                                is_RB=float(r.pos == "RB"), is_TE=float(r.pos == "TE")))
    F = pd.DataFrame(out).set_index("di")
    F["implied"] = F.implied.fillna(F.implied.mean()); F["role_chg"] = F.role_chg.fillna(0)
    return F


def design(T, F, mu=None, sd=None):
    X = F.loc[T.di].reset_index(drop=True).copy()
    gp = T.eng.values - T.book.values; X["big_gap"] = (np.abs(gp) >= .10).astype(float); X["neg_gap"] = (gp < 0).astype(float)
    X = X[FEATS]
    if mu is None: mu, sd = X.mean(), X.std().replace(0, 1)
    Z = ((X - mu) / sd).values
    Lb, Le = lg(T.book.values), lg(T.eng.values); dlt = (Le - Lb)[:, None]
    return np.column_stack([np.ones(len(T)), Lb, Le, Z * dlt, Z]), mu, sd


def fit(M, y, lam, npen=3):
    def f(w):
        z = M @ w; nll = np.sum(np.logaddexp(0, z) - y * z); return nll + lam * np.sum(w[npen:] ** 2)
    def g(w):
        z = M @ w; gr = M.T @ (ex(z) - y); gr[npen:] += 2 * lam * w[npen:]; return gr
    w0 = np.zeros(M.shape[1]); w0[1] = 1.0
    return minimize(f, w0, jac=g, method="L-BFGS-B").x


LAMS = (3.0, 30.0, 300.0, 3000.0)


def loso(T, F):
    rows, preds = [], np.full(len(T), np.nan)
    for S in sorted(T.season.unique()):
        tr, te = T[T.season != S].reset_index(drop=True), T[T.season == S].reset_index(drop=True)
        # inner LOSO for lambda
        sc = {}
        for lam in LAMS:
            l_ = []
            for S2 in sorted(tr.season.unique()):
                a, b = tr[tr.season != S2].reset_index(drop=True), tr[tr.season == S2].reset_index(drop=True)
                Ma, mu, sd = design(a, F); Mb, _, _ = design(b, F, mu, sd)
                l_.append(ll(ex(Mb @ fit(Ma, a.y.values, lam)), b.y.values) * len(b))
            sc[lam] = sum(l_)
        lam = min(sc, key=sc.get)
        Mtr, mu, sd = design(tr, F); Mte, _, _ = design(te, F, mu, sd)
        w = fit(Mtr, tr.y.values, lam); p = ex(Mte @ w); preds[(T.season == S).values] = p
        w2 = fit(Mtr[:, :3], tr.y.values, 0.0, 3); p2 = ex(Mte[:, :3] @ w2)
        y = te.y.values; bl = te.book + .2 * (te.eng - te.book)
        rows.append(dict(season=S, n=len(te), lam=lam, book_ll=ll(te.book, y), w02_ll=ll(bl, y), stack2_ll=ll(p2, y), model_ll=ll(p, y),
                         book_br=br(te.book, y), w02_br=br(bl, y), stack2_br=br(p2, y), model_br=br(p, y)))
    return pd.DataFrame(rows), preds


def coefs(T, F, lam, reps=150):
    M, mu, sd = design(T, F); w = fit(M, T.y.values, lam)
    games = T.game_id.values; ug = np.unique(games); idx = {g: np.where(games == g)[0] for g in ug}; W = []
    for _ in range(reps):
        sel = np.concatenate([idx[g] for g in RNG.choice(ug, len(ug))]); W.append(fit(M[sel], T.y.values[sel], lam))
    W = np.array(W); k = len(FEATS)
    lo, hi = np.percentile(W, 5, 0), np.percentile(W, 95, 0)
    tab = pd.DataFrame({"feature": FEATS, "c_gap_x_feat": w[3:3 + k], "c_lo": lo[3:3 + k], "c_hi": hi[3:3 + k],
                        "d_level": w[3 + k:], "d_lo": lo[3 + k:], "d_hi": hi[3 + k:], "share_or_mean": T.assign(**{}).pipe(lambda t: [float(F.loc[t.di, f].mean()) if f in F else np.nan for f in FEATS])})
    return w, tab


def deciles(T, F, feat):
    X = F.loc[T.di].reset_index(drop=True); t = T.reset_index(drop=True).assign(gap=lambda d: d.eng - d.book, f=X[feat].values)
    if t.f.nunique() > 2: t["f"] = (t.f > t.f.median()).astype(int)
    t["dec"] = pd.qcut(t.gap, 10, labels=False, duplicates="drop")
    return t.groupby(["f", "dec"]).agg(n=("y", "size"), gap_pts=("gap", lambda x: round(100 * x.mean(), 1)), hit=("y", "mean"), book=("book", "mean"), eng=("eng", "mean")).round(3)


def run(tag):
    D = ope.engine(tag)
    T = pd.read_pickle(os.path.join(REPO, "var", "bt", f"odds_td_{tag}.pkl")).rename(columns={"cons": "book"})[["di", "book", "eng", "y", "season", "game_id", "pa"]]
    E0 = pd.read_pickle(os.path.join(REPO, "var", "bt", f"odds_early_{tag}.pkl"))
    F = features(D, set(T.di) | set(E0.di))
    print(f"\n=== {tag}: {len(T)} player-games (2023-25 close). Feature means:", F.loc[T.di].mean().round(3).to_dict())
    R, preds = loso(T, F)
    print("held-out (leave-one-season-out); lower is better\n" + R.round(5).to_string(index=False))
    w = R.n / R.n.sum(); print("pooled:", {c: round(float((R[c] * w).sum()), 5) for c in R.columns if c.endswith("_ll") or c.endswith("_br")})
    lam = float(pd.Series(R.lam).mode()[0]); wt, tab = coefs(T, F, lam)
    print(f"\nfull-sample fit, lambda {lam}: i {wt[0]:.3f}, a(book) {wt[1]:.3f}, b(engine) {wt[2]:.3f}. c = trust in the engine's gap when the feature is 1 SD up "
          "(c > 0: gap is information; c < 0: gap is error); d = level shift. 90% cluster-bootstrap by game, standardised features.\n" + tab.round(3).to_string(index=False))
    strong = tab.assign(z=lambda t: t.c_gap_x_feat.abs() / ((t.c_hi - t.c_lo) / 3.29 + 1e-9)).query("feature not in ['big_gap', 'neg_gap']").sort_values("z", ascending=False).feature.head(3).tolist()
    for f in strong:
        print(f"\ngap decile x {f} (f=1: feature on / above median)\n" + deciles(T, F, f).to_string())
    # CLV check on the 2025 early set, model trained on 2023-24 closing prices only
    E = pd.read_pickle(os.path.join(REPO, "var", "bt", f"odds_early_{tag}.pkl"))
    E = E[E.healthy & E.xmove.notna()].rename(columns={"b_e": "book"}).copy(); E["season"] = 2025
    tr = T[T.season < 2025].reset_index(drop=True); Mtr, mu, sd = design(tr, F); wtr = fit(Mtr, tr.y.values, lam)
    Me, _, _ = design(E.reset_index(drop=True), F, mu, sd); E["mp"] = ex(Me @ wtr); E["medge"] = E.mp - E.book
    plain = E[(E.gap >= .05) & (E.gap < .10)]; n = len(plain)
    sel_top = E.sort_values("medge", ascending=False).head(n); sel2 = E[E.medge >= .02]
    both = plain[plain.medge > 0]; plain_neg = plain[plain.medge <= 0]
    rows = []
    for nm, g in (("plain rule: gap 5-10", plain), (f"model: top {n} by model edge", sel_top), ("model edge >= 2 pts", sel2),
                  ("gap 5-10 AND model edge > 0", both), ("gap 5-10 but model edge <= 0", plain_neg), ("all healthy", E)):
        lo = __import__("odds_early_eval").cboot(g, "xmove") if len(g) else (np.nan, np.nan)
        pl = np.where(g.y == 1, ope.pay(g.best_e), -1.0) if len(g) else np.array([])
        rows.append(dict(group=nm, n=len(g), rel_move_pts=round(100 * g.xmove.mean(), 2) if len(g) else np.nan, rel_90=tuple(np.round(100 * np.array(lo), 2)),
                         roi_pct=round(100 * pl.mean(), 1) if len(g) else np.nan, model_ll=round(ll(g.mp, g.y), 4) if len(g) else np.nan, book_ll=round(ll(g.book, g.y), 4) if len(g) else np.nan))
    print("\nCLV on the 2025 early set (healthy, model fit on 2023-24 close; implied total and injury features use the final report / closing line, see DECISIONS #87)\n"
          + pd.DataFrame(rows).to_string(index=False))
    print("model vs early book on all healthy early rows: LL", round(ll(E.mp, E.y), 5), "vs", round(ll(E.book, E.y), 5), "| w0.2", round(ll(E.book + .2 * (E.eng - E.book), E.y), 5))


if __name__ == "__main__":
    for t in sys.argv[1:]: run(t)
