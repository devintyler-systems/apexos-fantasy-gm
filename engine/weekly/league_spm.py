"""SPAMML league scoring layer and waiver report (DECISIONS #27).

Converts a weekly run (live `proj_all.pkl` or a frozen `projections.csv`) into this league's points and
ranks add/drop moves against a Fantrax roster and available-player export.

League scoring is actual NFL points only: 6 per TD for every credited player (passing, rushing, receiving, return,
fumble-recovery), 2 per two-point conversion, kicker XP 1 and FG 3 (flat), DST TD 6 and safety 2. Lineup is
QB1 RB2 WT3 (WR or TE) K1 DST1, no bench. A bye scores 0.

Fantrax exports are private league data: read them from anywhere, write reports only under var/ (gitignored) or a path you pass.
"""
import json
import os
import re
import unicodedata

import numpy as np
import pandas as pd

from paths import CONF, NFLV, OUT

CFG_PATH = os.path.join(CONF, "league_spm.json")
SLOT = {"QB": "QB", "RB": "RB", "WR": "WT", "TE": "WT", "WT": "WT", "K": "K", "DST": "DST"}


def load_cfg(path=None):
    with open(path or CFG_PATH) as f:
        return json.load(f)


def norm_name(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[.'`]", "", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_team(t, cfg):
    t = str(t).strip().upper()
    if t in ("NAN", "NULL", "NONE", "(N/A)", ""):
        return ""
    return cfg["team_aliases"].get(t, t)


# ---------------------------------------------------------------- projections -> league points
def skill_points(P, cfg):
    """Expected league points per skill player: 6 x (passing + rushing + receiving TD means) x availability."""
    d = P.copy()
    for c in ("pass_td_mean", "rush_td_mean", "rec_td_mean"):
        d[c] = pd.to_numeric(d.get(c), errors="coerce").fillna(0.0)
    act = pd.to_numeric(d.get("p_active"), errors="coerce").fillna(1.0)
    d["exp_tds"] = (d.pass_td_mean + d.rush_td_mean + d.rec_td_mean) * act
    d["ev"] = cfg["scoring"]["td"] * d.exp_tds
    d["slot"] = d["pos"].map(SLOT)
    d["key"] = d["player"].map(norm_name) + "|" + d["team"].map(lambda t: norm_team(t, cfg))
    d["nkey"] = d["player"].map(norm_name)
    return d[["player", "pos", "slot", "team", "opp", "key", "nkey", "p_active", "pass_td_mean", "rush_td_mean", "rec_td_mean", "exp_tds", "ev"]]


def kicker_ev(team_pts, cfg):
    k = cfg["kicker_env"]
    return k["intercept"] + k["slope"] * float(team_pts)


def current_kickers(stats):
    """team -> kicker name: the kicker with the most FG+XP attempts in the team's most recent game."""
    k = stats[stats["position"] == "K"].copy()
    if k.empty:
        return {}
    k["att"] = pd.to_numeric(k.get("fg_att"), errors="coerce").fillna(0) + pd.to_numeric(k.get("pat_att"), errors="coerce").fillna(0)
    k = k.sort_values(["team", "week", "att"])
    return {t: norm_name(g.iloc[-1]["player_display_name"]) for t, g in k.groupby("team")}


def ytd_td_rate(stats):
    """norm name -> (games, tds per game) from stats_player_week (any TD type credited)."""
    s = stats.copy()
    for c in ("passing_tds", "rushing_tds", "receiving_tds"):
        s[c] = pd.to_numeric(s.get(c), errors="coerce").fillna(0)
    s["tds"] = s.passing_tds + s.rushing_tds + s.receiving_tds
    s["touch"] = (pd.to_numeric(s.get("attempts"), errors="coerce").fillna(0) + pd.to_numeric(s.get("carries"), errors="coerce").fillna(0)
                  + pd.to_numeric(s.get("targets"), errors="coerce").fillna(0)) > 0
    s = s[s.touch]
    g = s.groupby("player_display_name").agg(games=("week", "nunique"), tds=("tds", "sum"))
    g["rate"] = g.tds / g.games
    g.index = [norm_name(i) for i in g.index]
    return g[~g.index.duplicated(keep=False)]


# ---------------------------------------------------------------- Fantrax
def read_fantrax(path, cfg):
    f = pd.read_csv(path)
    f["player"] = f["Player"].astype(str)
    f["team"] = f["Team"].map(lambda t: norm_team(t, cfg))
    f["slot"] = f["Position"].map(SLOT)
    st = f["Status"].astype(str)
    f["avail"] = np.where(st.eq("FA"), "FA", np.where(st.str.startswith("W"), "W", "ROSTERED"))
    f["bye"] = f["Opponent"].astype(str).str.strip().eq("Bye")
    f["nkey"] = f["player"].map(norm_name)
    f["key"] = f["nkey"] + "|" + f["team"]
    return f


def attach_ev(fx, S, team_pts, kickers, cfg):
    """League points for each Fantrax row. Bye or not on the slate = 0. Kickers: only the team's current kicker is valid."""
    S_key = S.set_index("key")
    nk = S.groupby("nkey").size()
    out = []
    for _, r in fx.iterrows():
        ev, note, exp_tds = np.nan, "", np.nan
        if r.bye:
            ev, note = 0.0, "bye"
        elif r.slot == "DST":
            ev = cfg["dst_ev"]
            note = "DST scores TDs and safeties only; ~flat"
        elif r.slot == "K":
            tp = team_pts.get(r.team)
            if tp is None:
                ev, note = np.nan, "team not on slate"
            elif kickers and kickers.get(r.team) and kickers[r.team] != r.nkey:
                ev, note = np.nan, "not the team's current kicker"
            else:
                ev = kicker_ev(tp, cfg)
        elif r.slot in ("QB", "RB", "WT"):
            row = None
            if r.key in S_key.index:
                row = S_key.loc[r.key]
            elif nk.get(r.nkey, 0) == 1:
                row = S[S.nkey == r.nkey].iloc[0]
                note = "team differs from projection (trade?)"
            if row is None:
                ev, note = np.nan, (note or "no projection (bye, inactive, or not in universe)")
            else:
                ev, exp_tds = float(row["ev"]), float(row["exp_tds"])
        out.append((ev, exp_tds, note))
    fx = fx.copy()
    fx["ev"] = [o[0] for o in out]
    fx["exp_tds"] = [o[1] for o in out]
    fx["note"] = [o[2] for o in out]
    fx["team_pts"] = fx.team.map(team_pts)
    return fx


# ---------------------------------------------------------------- decision rule
def hot_streak(row, ytd, cfg):
    if ytd is None or row.nkey not in ytd.index or not row.exp_tds or np.isnan(row.exp_tds) or row.exp_tds <= 0:
        return False
    return bool(ytd.loc[row.nkey, "rate"] >= cfg["rule"]["hot_streak_ratio"] * row.exp_tds)


def decide(cur_ev, cand_ev, streak, cfg):
    """Return (ok, gain, reason). Zero-scoring drops (bye/out) need any gain; others need the irreversible threshold and no streak flag."""
    gain = cand_ev - cur_ev
    r = cfg["rule"]
    if cur_ev <= 0:
        return gain > r["min_gain_zero_slot"], gain, "zero-slot (bye/out): any gain"
    if gain < r["min_gain_irreversible"]:
        return False, gain, f"gain {gain:.2f} below irreversible threshold {r['min_gain_irreversible']}"
    if streak:
        return False, gain, "candidate ytd TD rate is a streak vs projection"
    return True, gain, "clears irreversible threshold"


def order_candidates(c, cfg, slot):
    """Best first. Kickers within k_tie_band of the best are tied and ordered by team implied points."""
    c = c.dropna(subset=["ev"]).sort_values("ev", ascending=False)
    if c.empty or slot != "K":
        return c
    top = c.ev.iloc[0]
    tied = c[c.ev >= top - cfg["rule"]["k_tie_band"]].sort_values(["team_pts", "ev"], ascending=False)
    return pd.concat([tied, c.drop(tied.index)])


def moves(roster, avail, ytd, cfg, alts=3):
    """Greedy per slot: pair the weakest current player with the best remaining candidate while the rule passes."""
    res = []
    used = set()
    for slot, n in cfg["lineup"].items():
        if slot == "DST":
            continue    # league DST scores TDs and safeties only (about 1 point a game for everyone): never worth a move
        cur = roster[roster.slot == slot].sort_values("ev", ascending=True, na_position="first").head(n)
        cands = order_candidates(avail[avail.slot == slot], cfg, slot)
        for _, c in cur.iterrows():
            cev = 0.0 if np.isnan(c.ev) else c.ev
            pool = cands[~cands.player.isin(used)]
            if pool.empty:
                continue
            best = pool.iloc[0]
            ok, gain, why = decide(cev, best.ev, hot_streak(best, ytd, cfg), cfg)
            alt = pool.iloc[1:1 + alts]
            res.append(dict(slot=slot, drop=c.player, drop_ev=round(cev, 2), add=best.player, add_team=best.team, add_ev=round(best.ev, 2),
                            gain=round(gain, 2), add_exp_tds=round(best.exp_tds, 2) if not np.isnan(best.exp_tds) else np.nan,
                            add_ytd_tds_g=round(float(ytd.loc[best.nkey, "rate"]), 2) if ytd is not None and best.nkey in ytd.index else np.nan,
                            claim="FA (first come)" if best.avail == "FA" else "waiver claim (Tue 6pm)",
                            act=bool(ok), rule=why,
                            alternates="; ".join(f"{a.player} {a.ev:.2f} ({a.avail})" for _, a in alt.iterrows())))
            if ok:
                used.add(best.player)
    return pd.DataFrame(res).sort_values(["act", "gain"], ascending=[False, False]).reset_index(drop=True)


# ---------------------------------------------------------------- driver
def load_run(run_dir):
    pk = os.path.join(run_dir, "proj_all.pkl")
    P = pd.read_pickle(pk) if os.path.exists(pk) else pd.read_csv(os.path.join(run_dir, "projections.csv"))
    T = pd.read_csv(os.path.join(run_dir, "w4_team_totals.csv"))
    played = T["note"].astype(str).str.contains("PLAYED", na=False)
    return P, T[~played].set_index("team")["pts_mean"].to_dict()


def report(run_dir, roster_csv, avail_csv, season=2026, cfg=None, nflv=None):
    cfg = cfg or load_cfg()
    P, team_pts = load_run(run_dir)
    S = skill_points(P, cfg)
    kickers, ytd = {}, None
    sp = os.path.join(nflv or NFLV, f"stats_player_week_{season}.parquet")
    if os.path.exists(sp):
        st = pd.read_parquet(sp)
        kickers, ytd = current_kickers(st), ytd_td_rate(st)
    ro = attach_ev(read_fantrax(roster_csv, cfg), S, team_pts, kickers, cfg)
    av = attach_ev(read_fantrax(avail_csv, cfg), S, team_pts, kickers, cfg)
    av = av[av.avail.isin(["FA", "W"])]
    mv = moves(ro, av, ytd, cfg)
    return ro, av, mv


def render(ro, av, mv):
    L = ["# Waiver report (league points)", "", "## My lineup", "",
         "| Slot | Player | Team | Week EV | Note |", "|---|---|---|---|---|"]
    for _, r in ro.sort_values("slot").iterrows():
        L.append(f"| {r.slot} | {r.player} | {r.team} | {0 if np.isnan(r.ev) else r.ev:.2f} | {r.note} |")
    tot = ro.ev.fillna(0).sum()
    L += ["", f"Projected lineup total: **{tot:.1f}**", "", "## Moves", ""]
    if mv.empty:
        L.append("No candidate beats a current starter.")
    else:
        L += ["| Slot | Drop | Add | Gain | Add TDs/g proj vs ytd | Claim | Act | Rule | Alternates |", "|---|---|---|---|---|---|---|---|---|"]
        for _, m in mv[mv.gain > 0].iterrows():
            L.append(f"| {m.slot} | {m['drop']} ({m.drop_ev}) | {m['add']} {m.add_team} ({m.add_ev}) | {m.gain:+.2f} | {m.add_exp_tds} vs {m.add_ytd_tds_g} | {m.claim} | {'YES' if m.act else 'no'} | {m.rule} | {m.alternates} |")
    L += ["", "Notes: EV = 6 x expected TDs x availability (skill), 4.078 + 0.1439 x team points (K), flat (DST). Streak flag compares ytd TDs per game with the projection.",
          "Availability comes from the run's injury inputs; rerun after Friday and Sunday injury reports."]
    return "\n".join(L)


def main(run_dir, roster_csv, avail_csv, out_dir=None, season=2026):
    ro, av, mv = report(run_dir, roster_csv, avail_csv, season)
    out_dir = out_dir or os.path.join(OUT, "waiver")
    os.makedirs(out_dir, exist_ok=True)
    mv.to_csv(os.path.join(out_dir, "waiver_moves.csv"), index=False)
    av.sort_values("ev", ascending=False).to_csv(os.path.join(out_dir, "waiver_available_ranked.csv"), index=False)
    md = render(ro, av, mv)
    with open(os.path.join(out_dir, "waiver_report.md"), "w") as f:
        f.write(md)
    print(md)
    return mv
