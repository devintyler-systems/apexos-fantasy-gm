"""Full single-game prop and parlay screen from the joint simulation (any game; built for Thursday night).

Usage (two steps, one process per track because the track is read at import):
  APEX_ENV=market python tnf_full.py sim AWAY HOME [--lines espn_dk_line_moves.csv]
  APEX_ENV=model  python tnf_full.py sim AWAY HOME [--lines espn_dk_line_moves.csv]
  python tnf_full.py render AWAY HOME [--out docs/weekly/TNF_AWAY_HOME_2026_W06.md]

What it does and does not know (read before betting):
  * Prices are NOT available from the ESPN feed (DraftKings lines only, no juice, no touchdown markets). Singles are screened at an ASSUMED -110 (break-even 52.4%) after shrinking the model
    50/50 toward 50% (the W5 postmortem: the 50/50 blend is the only version that matched the books), so a PLAY needs a model P of about 61%+. Everything else is a LEAN.
  * Passing count/yardage overs get a +0.08 shift to the model's P(over): W5 postmortem 3.2 found the model's passing-count P(over) 5 to 14 points below the books.
  * Touchdown props and parlays are priced from the model's joint simulation as FAIR odds. The 'play at or better than' price adds a 12% cushion for model error. Book SGP prices are not known here.
  * A player who is inactive in a simulated game makes his leg lose (conservative); legs are only built for players at least 95% likely to play.
"""
import argparse
import itertools
import os
import pickle
import sys

import numpy as np
import pandas as pd

from paths import OUT, NFLV

PUSH_NOTE = "pushes excluded from both sides"
MAP = {"player_pass_yds": "pass_yds", "player_reception_yds": "rec_yds", "player_receptions": "rec", "player_rush_yds": "rush_yds",
       "player_rush_attempts": "rush_att", "player_pass_completions": "pass_cmp", "player_pass_attempts": "pass_att"}
COL = {"rec": "receptions", "rec_yds": "receiving_yards", "rush_yds": "rushing_yards", "rush_att": "carries", "pass_yds": "passing_yards", "pass_cmp": "completions", "pass_att": "attempts"}
USED = {"rec": "targets", "rec_yds": "targets", "rush_yds": "carries", "rush_att": "carries", "pass_yds": "attempts", "pass_cmp": "attempts", "pass_att": "attempts"}
PASS_SHIFT = 0.08
BE110 = 110 / 210
CUSHION = 1.12


def rb_out_teams(season, week):
    """Teams with a running back Out (injury report or the manual-out file). The engine has no with/without role model, so RB rush lines on those teams are not published (W6: Washington backs 15 carries vs 24 normal; W7 red-team: CHI Roschon Johnson 8% to exceed 7.5 carries with 13 last week)."""
    out = set()
    try:
        ij = pd.read_parquet(NFLV + f"injuries_{season}.parquet"); ij = ij[(ij.week == week) & (ij.position == "RB") & (ij.report_status == "Out")]
        out |= set(ij.team)
    except Exception:
        pass
    mo = os.environ.get("APEX_MANUAL_OUT")
    if mo and os.path.exists(mo):
        m = pd.read_csv(mo); out |= set(m[m.pos == "RB"].team)
    return out


def american(p):
    if p is None or np.isnan(p):
        return 0
    p = float(np.clip(p, 1e-4, 1 - 1e-4))
    return int(round(-100 * p / (1 - p))) if p >= .5 else int(round(100 * (1 - p) / p))


def dec_to_am(d):
    return int(round((d - 1) * 100)) if d >= 2 else int(round(-100 / (d - 1)))


def play_price(p):
    """Smallest American price worth taking: fair decimal x cushion."""
    return dec_to_am(1 / max(p, 1e-4) * CUSHION)


def sim(away, home, lines_csv, tag):
    import run_all as R
    from params import is_neutral, norm_name, SEASON, TD_FLOOR, floor_anytime
    R.run_game(away, home, neutral=is_neutral(away, home), ns=20000)
    d = R.STORE.pop((away, home))
    A, H = d["A"], d["H"]
    pls = {norm_name(p["player"]): p for t in (away, home) for p in d["players"][t]}
    ttot = np.maximum(A["td"] + H["td"] + A["dtd"] + H["dtd"], 1)
    L = pd.read_csv(lines_csv).drop_duplicates(["player", "market"]) if lines_csv else pd.DataFrame(columns=["player", "market", "line_current", "line_open"])
    st = pd.read_parquet(NFLV + f"stats_player_week_{SEASON}.parquet")
    st = st[st.week <= int(os.environ.get("APEX_THROUGH_WEEK", 5))].copy(); st["key"] = st.player_display_name.map(norm_name)
    rows = []
    for r in L.itertuples():
        k = norm_name(r.player); mk = MAP.get(r.market)
        if mk is None or k not in pls: continue
        p = pls[k]; m = p["mask"]
        x = p[mk][m]
        over = float((x > r.line_current).mean()); under = float((x < r.line_current).mean()); push = 1 - over - under
        log = st[(st.key == k) & (st[USED[mk]] > 0)]; n = len(log)
        rows.append(dict(player=p["player"], team=p["team"], pos=p["pos"], market=mk, line=float(r.line_current), line_open=float(r.line_open), pa=float(p["p_active"]),
                         p_over=over, p_under=under, p_push=push, mean=float(x.mean()), n_log=n, over_games=int((log[COL[mk]] > r.line_current).sum()),
                         under_games=int((log[COL[mk]] < r.line_current).sum()), log_avg=float(log[COL[mk]].mean()) if n else np.nan))
    singles = pd.DataFrame(rows)
    # touchdowns
    trows = []
    for k, p in pls.items():
        if p["p_active"] < 0.5: continue
        m = p["mask"]; tdc = p["rush_td"] + p["rec_td"]
        any_td = floor_anytime(float((tdc[m] >= 1).mean()), p["pos"], float(p["rec"][m].mean()), TD_FLOOR, p["p_active"] >= 0.5); two = float((tdc[m] >= 2).mean()); first = float((tdc[m] / ttot[m]).mean())
        ptd = float(p["pass_td"][m].mean()) if p["pos"] == "QB" else np.nan
        trows.append(dict(player=p["player"], team=p["team"], pos=p["pos"], pa=float(p["p_active"]), any_td=any_td, two_plus=two, first_td=first, exp_td=float(tdc[m].mean()),
                          exp_pass_td=ptd, p1_pass=float((p["pass_td"][m] >= 1).mean()) if p["pos"] == "QB" else np.nan,
                          p2_pass=float((p["pass_td"][m] >= 2).mean()) if p["pos"] == "QB" else np.nan,
                          p3_pass=float((p["pass_td"][m] >= 3).mean()) if p["pos"] == "QB" else np.nan))
    tds = pd.DataFrame(trows)
    stt = st.copy()
    for c in ("rushing_tds", "receiving_tds"): stt[c] = pd.to_numeric(stt[c], errors="coerce").fillna(0)
    stt["td"] = stt.rushing_tds + stt.receiving_tds
    yt = stt[(stt.attempts.fillna(0) + stt.carries.fillna(0) + stt.targets.fillna(0)) > 0].groupby("key").agg(g=("week", "nunique"), td=("td", "sum"), tgt=("targets", "sum"), car=("carries", "sum"))
    tds["ytd"] = [f"{int(yt.td[norm_name(n)])} TD / {int(yt.g[norm_name(n)])} g ({int(yt.tgt[norm_name(n)])} tgt, {int(yt.car[norm_name(n)])} car)" if norm_name(n) in yt.index else "" for n in tds.player]
    # legs for parlays: name -> bool array (inactive = loss)
    legs, meta = {}, {}

    def add(name, arr, pl, mk, kind, **kw):
        legs[name] = arr; meta[name] = dict(player=pl, market=mk, kind=kind, p=float(arr.mean()), **kw)

    for r in singles.itertuples():
        p = pls[norm_name(r.player)]
        if p["p_active"] < 0.95: continue
        m = p["mask"]; x = p[r.market]
        add(f"{r.player} {r.market} O{r.line}", m & (x > r.line), r.player, r.market, "line", side="OVER", line=r.line)
        add(f"{r.player} {r.market} U{r.line}", m & (x < r.line), r.player, r.market, "line", side="UNDER", line=r.line)
    for k, p in pls.items():
        if p["p_active"] < 0.95: continue
        m = p["mask"]; tdc = p["rush_td"] + p["rec_td"]
        a = m & (tdc >= 1)
        if 0.08 <= a.mean(): add(f"{p['player']} anytime TD", a, p["player"], "any_td", "td")
        if p["pos"] == "QB":
            for t in (1, 2):
                add(f"{p['player']} pass TD {t}+", m & (p["pass_td"] >= t), p["player"], "pass_td", "td")
    gm = pd.read_parquet(NFLV + "games.parquet"); gm = gm[(gm.season == SEASON) & (gm.week == int(os.environ.get("APEX_TARGET_WEEK", 6))) & (gm.away_team == away) & (gm.home_team == home)]
    sp = float(gm.spread_line.iloc[0]) if len(gm) else np.nan; tl = float(gm.total_line.iloc[0]) if len(gm) else np.nan
    tot = A["pts"] + H["pts"]; mean_tot = float(tot.mean()); marg = H["pts"] - A["pts"]
    add(f"{away} to win", A["pts"] > H["pts"], "GAME", "ml", "game"); add(f"{home} to win", H["pts"] > A["pts"], "GAME", "ml", "game")
    if not np.isnan(tl):
        add(f"Total over {tl}", tot > tl, "GAME", "total", "game"); add(f"Total under {tl}", tot < tl, "GAME", "total", "game")
    if not np.isnan(sp) and sp != round(sp):   # nflverse spread_line = expected home margin; whole-number lines are skipped (a push is neither a win nor a loss, so the fair odds would be wrong)
        hs = -sp
        add(f"{home} {hs:+.1f}", marg + hs > 0, "GAME", "spread", "game"); add(f"{away} {-hs:+.1f}", marg + hs < 0, "GAME", "spread", "game")
    game = dict(away=away, home=home, mkt_spread=sp, mkt_total=tl, away_pts=float(A["pts"].mean()), home_pts=float(H["pts"].mean()), total=mean_tot, p_away=float((A["pts"] > H["pts"]).mean()),
                p_home=float((H["pts"] > A["pts"]).mean()), away_p10_p90=tuple(np.percentile(A["pts"], [10, 90])), home_p10_p90=tuple(np.percentile(H["pts"], [10, 90])),
                total_p10_p90=tuple(np.percentile(tot, [10, 90])))
    out = dict(game=game, singles=singles, tds=tds, meta=meta, tag=tag)
    if tag == "market":
        out["legs"] = {k: np.packbits(v) for k, v in legs.items()}; out["n"] = len(tot)
    pickle.dump(out, open(os.path.join(OUT, f"tnf_{away}_{home}_{tag}.pkl"), "wb"))
    print(f"{tag}: {len(singles)} line rows, {len(tds)} TD rows, {len(legs)} parlay legs, game {game['away_pts']:.1f}-{game['home_pts']:.1f}")


def gate(row):
    """Return (side, shrunk_p, label) for the side the model favours at the posted line."""
    shift = PASS_SHIFT if row.market in ("pass_yds", "pass_att", "pass_cmp") else 0.0
    po = min(max(row.p_over / max(1 - row.p_push, 1e-6) + shift, 0), 1)
    side, mp = ("OVER", po) if po >= 0.5 else ("UNDER", 1 - po)
    sh = 0.5 * mp + 0.25
    n = row.n_log; hit = row.over_games if side == "OVER" else row.under_games
    supported = n >= 3 and hit / n >= 0.5
    label = "PLAY" if (sh >= BE110 + 0.03 and row.pa >= 0.95 and supported) else ("LEAN" if sh >= BE110 + 0.01 and row.pa >= 0.9 else "")
    return side, sh, mp, label, f"{hit}/{n}"


def render(away, home, out_path):
    mk = pickle.load(open(os.path.join(OUT, f"tnf_{away}_{home}_market.pkl"), "rb"))
    try:
        md = pickle.load(open(os.path.join(OUT, f"tnf_{away}_{home}_model.pkl"), "rb"))
    except FileNotFoundError:
        md = None
    g = mk["game"]
    S = mk["singles"].copy()
    res = [gate(r) for r in S.itertuples()]
    S["side"], S["shrunk"], S["model_p"], S["label"], S["log"] = [x[0] for x in res], [x[1] for x in res], [x[2] for x in res], [x[3] for x in res], [x[4] for x in res]
    if md is not None:
        M = md["singles"].set_index(["player", "market"])
        S["model_only_p_over"] = [M.p_over.get((r.player, r.market), np.nan) for r in S.itertuples()]
        S["agree"] = [("yes" if ((r.model_only_p_over >= .5) == (r.side == "OVER")) else "NO") if not np.isnan(r.model_only_p_over) else "" for r in S.itertuples()]
    else:
        S["agree"] = ""
    S["fair"] = [american(p) for p in S.shrunk]
    S["move"] = S.line - S.line_open
    L = []
    w = L.append
    w(f"# Thursday night: {away} @ {home}, Week {os.environ.get("APEX_TARGET_WEEK", 6)} 2026 (market-anchored track, 20,000 correlated simulations)\n")
    w("**Read this first.** Lines are DraftKings via ESPN (no prices, no touchdown markets). Singles are screened at an assumed -110 after shrinking the model 50/50 toward the market; "
      "a PLAY needs about 61% model probability, active 95%+, and the side hitting in at least half of the player's games this season. Touchdown and parlay prices are FAIR odds from the joint "
      "simulation; 'play at' adds a 12% cushion. The W4 and W5 postmortems found no edge over the books on yardage and count props; anytime-TD probabilities are calibrated. Treat everything here as a ranked lean, not a lock.\n")
    w("## Game\n")
    w(f"| | {away} | {home} |\n|---|---|---|\n| Win probability | {g['p_away']:.0%} | {g['p_home']:.0%} |\n| Mean points (P10-P90) | {g['away_pts']:.1f} ({g['away_p10_p90'][0]:.0f}-{g['away_p10_p90'][1]:.0f}) | {g['home_pts']:.1f} ({g['home_p10_p90'][0]:.0f}-{g['home_p10_p90'][1]:.0f}) |\n")
    w(f"Total {g['total']:.1f} (P10-P90 {g['total_p10_p90'][0]:.0f}-{g['total_p10_p90'][1]:.0f}). Market: {home} {-g['mkt_spread']:+.1f}, total {g['mkt_total']}.\n")
    if md is not None:
        gm = md["game"]
        w(f"Model-only track: {away} {gm['away_pts']:.1f}, {home} {gm['home_pts']:.1f}, {away} win {gm['p_away']:.0%}.\n")
    # singles
    junk = S.market.isin(["rush_yds", "rush_att"]) & ~S.pos.isin(["QB", "RB"])
    S.loc[junk | (S.model_p >= 0.85) | ((S.n_log < 2) & (S.label == "LEAN")), "label"] = ""
    if os.environ.get("APEX_PASS_UNDER_GATE", "1") != "0":      # DECISIONS #44: 2026 team pass attempts run 2 to 3 above the projection and the Thursday pass-volume unders went 1 of 6; no PLAY/LEAN on a passing attempts, completions or yards UNDER until the level correction is backtested (=0 restores)
        S.loc[S.market.isin(["pass_att", "pass_cmp", "pass_yds"]) & (S.side == "UNDER"), "label"] = ""
    if os.environ.get("APEX_RB_OUT_GATE") == "1":      # off by default since the Week 7 Thursday result (DECISIONS #43: the four gated CHI RB lines all won); =1 restores the old rule
        S.loc[S.market.isin(["rush_yds", "rush_att"]) & (S.pos == "RB") & S.team.isin(rb_out_teams(int(os.environ.get("APEX_SEASON", 2026)), int(os.environ.get("APEX_TARGET_WEEK", 7)))), "label"] = ""
    S.loc[(S.label == "LEAN") & S.market.isin(["rec", "rec_yds"]), "label"] = ""      # W6: LEAN receiving props hit 35% on 105 lines (POSTMORTEM_2026_W06 3.3); never published
    P = S[S.label != ""].sort_values(["label", "shrunk"], ascending=[False, False])
    w("## Singles (main lines)\n")
    w("Side = the side the model favours; model P is before the 50/50 shrink (passing overs include the +0.08 bias shift); 'season' = games that side cleared the line / games played; "
      "'fair' = fair American price at the shrunk probability; 'move' = line change since open.\n")
    w("| Label | Player | Market | Side | Line | Model P | Shrunk P | Fair | Season | Model-only agrees | Move |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for r in P.itertuples():
        w(f"| {r.label} | {r.player} ({r.team}) | {r.market} | {r.side} | {r.line} | {r.model_p:.0%} | {r.shrunk:.0%} | {r.fair:+d} | {r.log} | {r.agree} | {r.move:+.1f} |")
    if P.empty:
        w("| none clears the gate | | | | | | | | | | |")
    w(f"\n{(S.label == 'PLAY').sum()} PLAY, {(S.label == 'LEAN').sum()} LEAN of {len(S)} priced lines. Everything else was inside the market.\n")
    w("<details><summary>All lines screened</summary>\n")
    w("| Player | Market | Line | Model P(over) | Side | Shrunk P | Season games over / under / n | Active |\n|---|---|---|---|---|---|---|---|")
    for r in S.sort_values(["player", "market"]).itertuples():
        w(f"| {r.player} | {r.market} | {r.line} | {r.p_over:.0%} | {r.side} | {r.shrunk:.0%} | {r.over_games}/{r.under_games}/{r.n_log} | {r.pa:.0%} |")
    w("\n</details>\n")
    # TD
    T = mk["tds"].copy().sort_values("any_td", ascending=False)
    w("## Touchdown scorers (model probability, fair odds, price to play at)\n")
    w("Anytime counts rushing and receiving TDs (QB rushing included). First TD uses each player's share of simulated touchdowns. Prices below the 'play at' column are not worth taking.\n")
    w("| Player | Pos | Active | 2026 so far | Anytime | Fair | Play at or better | 2+ TD | Fair 2+ | First TD | Fair first |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for r in T[T.any_td >= 0.05].itertuples():
        w(f"| {r.player} ({r.team}) | {r.pos} | {r.pa:.0%} | {r.ytd} | {r.any_td:.1%} | {american(r.any_td):+d} | {play_price(r.any_td):+d} | {r.two_plus:.1%} | {american(r.two_plus):+d} | {r.first_td:.1%} | {american(r.first_td):+d} |")
    Q = T[T.pos == "QB"]
    if len(Q):
        w("\n**Quarterback passing TDs** (not priced in the feed)\n\n| QB | Mean | 1+ | 2+ | 3+ |\n|---|---|---|---|---|")
        for r in Q.itertuples():
            w(f"| {r.player} | {r.exp_pass_td:.2f} | {r.p1_pass:.0%} ({american(r.p1_pass):+d}) | {r.p2_pass:.0%} ({american(r.p2_pass):+d}) | {r.p3_pass:.0%} ({american(r.p3_pass):+d}) |")
    # sneaky longshots
    w("\n**Sneaky TD longshots the model likes** (anytime 8% to 30%, role-based, not price-based): ")
    ls = T[(T.any_td >= 0.08) & (T.any_td <= 0.30)].sort_values("any_td", ascending=False)
    w("; ".join(f"{r.player} {r.any_td:.0%} (fair {american(r.any_td):+d}, take at {play_price(r.any_td):+d} or better)" for r in ls.itertuples()) + "\n")
    # parlays: legs are the model-favoured side of each posted DK line (haircut by the same 50/50 shrink as the singles), touchdown legs, and game legs
    n = mk["n"]
    legs = {k: np.unpackbits(v)[:n].astype(bool) for k, v in mk["legs"].items()}
    meta = mk["meta"]
    fav = {}
    for r in S.itertuples():
        if r.label == "" or r.n_log < 3 or r.model_p >= 0.85: continue
        nm = f"{r.player} {r.market} {r.side[0]}{r.line}"
        if nm in legs:
            raw = (r.p_over if r.side == "OVER" else r.p_under) / max(1 - r.p_push, 1e-6)
            fav[nm] = dict(r=min(r.shrunk / max(raw, 1e-6), 1.0), label=r.label, shrunk=r.shrunk)

    def shr(names):
        """joint probability after the single-leg shrink (TD and game legs carry no shrink; the TD model is calibrated, game legs are market-anchored)"""
        a = legs[names[0]].copy()
        for x in names[1:]: a &= legs[x]
        j = float(a.mean())
        return j, j * float(np.prod([_r(x) for x in names]))

    def _r(x):
        """parlay shrink factor of a leg: lines carry their fitted shrink; anytime-TD legs shrink only downward (a 50/50 shrink would lift a longshot); the raw sim stays in the 'Raw sim' column"""
        if x in fav: return fav[x]["r"]
        if meta[x]["market"] == "any_td":
            p0 = meta[x]["p"]; return min(p0, 0.5 + 0.5 * (p0 - 0.5)) / max(p0, 1e-6)
        return 1.0

    def okset(names):
        pl = [meta[x]["player"] for x in names if meta[x]["player"] != "GAME"]
        vol = [meta[x]["side"] for x in names if meta[x]["kind"] == "line"]      # W6: one volume/yardage line per script side (all unders, or all overs) per ticket
        return len(set(pl)) == len(pl) and sum(meta[x]["kind"] == "game" for x in names) <= 1 and len(set(vol)) == len(vol)

    def search(pool, sizes, lo, hi, need_td=False, rank="p", top=3):
        res = []
        for sz in sizes:
            for combo in itertools.combinations(pool, sz):
                if not okset(combo): continue
                if need_td and not any(meta[x]["kind"] == "td" for x in combo): continue
                j, js = shr(combo)
                if lo <= js <= hi:
                    res.append((combo, js, j, js / np.prod([meta[x]["p"] * (_r(x)) for x in combo])))
        res.sort(key=(lambda t: -t[1]) if rank == "p" else (lambda t: -t[3]))
        out, seen = [], set()
        for c, js, j, u in res:
            ids = frozenset(meta[x]["player"] for x in c)
            if ids in seen: continue
            seen.add(ids); out.append((c, js, j, u))
            if len(out) == top: break
        return out

    line_pool = sorted(fav, key=lambda k: -fav[k]["shrunk"])
    qb1 = [k for k in meta if meta[k]["market"] == "pass_td" and k.endswith("1+")]
    safe_pool = [k for k in line_pool if fav[k]["shrunk"] >= 0.56][:14] + qb1 + [k for k in meta if meta[k]["kind"] == "game" and meta[k]["p"] >= 0.5]
    td_pool = [k for k in meta if meta[k]["kind"] == "td" and 0.12 <= meta[k]["p"] <= 0.60 and meta[k]["market"] == "any_td"]
    td_pool = sorted(td_pool, key=lambda k: -meta[k]["p"])[:8]
    qbtd = [k for k in meta if meta[k]["market"] == "pass_td" and k.endswith("2+")]
    game_pool = [k for k in meta if meta[k]["kind"] == "game"]
    w("\n## Parlays (same game, joint simulation)\n")
    w("Legs are the model-favoured side of each posted DraftKings line (only legs that cleared the single-bet gate, 3+ games of season support), anytime-TD legs, QB 2+ passing TDs and game legs. "
      "Hit probability is the joint simulation after the same 50/50 shrink the singles get; 'Raw sim' is before it. Fair odds, not book prices: a same-game parlay at a book usually pays less than the "
      "product of the legs, so only take it at or better than the 'play at' price. 'Uplift' = joint / product of legs (above 1.0 = the legs move together).\n")

    def show(title, items, note):
        w(f"### {title}\n{note}\n")
        w("| Legs | Hit probability | Raw sim | Fair odds | Play at or better | Uplift |\n|---|---|---|---|---|---|")
        for c, js, j, u in items:
            w(f"| {' + '.join(c)} | {js:.1%} | {j:.1%} | {american(js):+d} | {play_price(js):+d} | {u:.2f} |")
        if not items: w("| none in band | | | | | |")
        w("")
    show("Safest (highest chance to hit)", search(safe_pool, (2, 3), 0.28, 0.60, rank="p"), "2 to 3 legs: the highest-probability posted lines, QB 1+ passing TD (the one market where the model beat the books in W4: log loss 0.647 vs 0.673) and game legs.")
    show("Mid-tier (more pay)", search(line_pool[:16] + td_pool[:4] + game_pool, (3,), 0.07, 0.24, rank="p"), "3 legs, mixing posted-line legs with a touchdown or game leg.")
    show("Aggressive (longer shot, model likes)", search(line_pool[:14] + td_pool + qbtd + game_pool, (3, 4), 0.025, 0.08, need_td=True, rank="p"), "3 to 4 legs with at least one touchdown leg, ranked by hit probability inside a 2.5-8% band (ranking by uplift alone picked incoherent shootout scenarios).")
    w("## Line movement since open (DraftKings via ESPN)\n")
    mv = S.assign(a=S.move.abs()).sort_values("a", ascending=False).head(8)
    w("| Player | Market | Open | Now |\n|---|---|---|---|")
    for r in mv.itertuples():
        w(f"| {r.player} | {r.market} | {r.line_open} | {r.line} |")
    w("\nBook prices (and any anytime/first TD prices) were not available. Send a screenshot of the DraftKings board for this game and I will re-price every pick against the real number.\n")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    open(out_path, "w").write("\n".join(L))
    S.to_csv(out_path.replace(".md", "_singles.csv"), index=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sim", "render"]); ap.add_argument("away"); ap.add_argument("home")
    ap.add_argument("--lines"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "sim":
        import run_all as _R
        R_LADDER = _R.LADDER
        sim(a.away, a.home, a.lines, os.environ.get("APEX_ENV", "market"))
    else:
        render(a.away, a.home, a.out or f"TNF_{a.away}_{a.home}.md")
