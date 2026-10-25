"""Full-slate prediction report for a week: games, team tables, player projections, touchdown boards, single-line screen and 1/2/3/4-leg parlays across every unplayed game.

Two steps (one process per track; the track is read at import):
  APEX_ENV=market python slate_full.py sim  --lines espn_dk_line_moves.csv   # simulates every unplayed game, writes tnf_{AWAY}_{HOME}_{track}.pkl to OUT
  APEX_ENV=model  python slate_full.py sim  --lines espn_dk_line_moves.csv
  python slate_full.py render --run-market <dir> --run-model <dir> --tables <dir> --out docs/weekly/SLATE_FULL_YYYY_WNN.md

Per-game screening logic (shrink, gate, bias shift, fair odds, 'play at' cushion) is `tnf_full.py`; read its docstring first. Prices are not available from the ESPN feed, so every number is
a probability or a FAIR price. Cross-game parlay legs are independent by construction; same-game legs use the joint simulation.
"""
import argparse
import itertools
import os
import pickle

import numpy as np
import pandas as pd

import tnf_full as T
from paths import NFLV, OUT
from load import norm_name


def fillin_qbs(season, week):
    """Depth-chart QB1 who is not the team's 2026 completions leader (a fill-in starter): {team: player}. Their team's pass-game singles carry a caution flag and they are kept off TD boards and parlays."""
    d = pd.read_parquet(NFLV + f"depth_charts_{season}.parquet"); d = d[(d.dt == d.dt.max()) & (d.pos_abb == "QB") & (d.pos_rank == 1)]
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); st = st[st.week < week]
    lead = st.groupby(["team", "player_display_name"]).completions.sum().reset_index().sort_values("completions", ascending=False).groupby("team").head(1).set_index("team").player_display_name
    return {r.team: r.player_name for r in d.itertuples() if r.team in lead.index and lead[r.team] != r.player_name}


def games_unplayed():
    import run_all as R
    from params import SCHED, PLAYED
    only = {x for x in os.environ.get("APEX_ONLY_GAMES", "").split(",") if x}      # e.g. ARI@LA,LAC@KC: restrict a rerun to the games still to come
    return [(g.away, g.home) for g in SCHED.itertuples() if (g.away, g.home) not in PLAYED and (not only or f"{g.away}@{g.home}" in only)]


def sim_all(lines):
    tag = os.environ.get("APEX_ENV", "market")
    for a, h in games_unplayed():
        T.sim(a, h, lines, tag)


# Week 6 excluded HOU receiving (Marvin Harrison Jr. was dropped by the stale-team rule); the Week 7 audit found him projected on HOU, so nothing is excluded now.
EXCLUDE = set()
QB_OUT_TEAMS = set()      # teams whose projected QB1 is out; set by render()
CAUTION = {}              # per-team flags, set by render() from the depth chart (fill-in QBs)
CAUTION_ALL = {}
DEMOTE = set()            # PLAY -> LEAN and kept out of parlays (teams whose QB status is unconfirmed); empty unless the operator sets it
BACKUP_QBS = set()        # fill-in QBs on those teams: they inherit the generic backup rushing profile (about 0.35 rush TD), so their anytime-TD numbers are not published


_ADJ = {}


def _team_atrisk(out_dir):
    """Teams -> [(nkey, pos, p_active, tgt_share_at_risk, carry_share_at_risk)] for players below 90% likely to play, read from the run's injury log."""
    if out_dir in _ADJ:
        return _ADJ[out_dir]
    d = {}
    try:
        a = pd.read_csv(os.path.join(out_dir, "w4_injury_adjustments.csv"))
        for r in a[a.p_active < 0.9].itertuples():
            d.setdefault(r.team, []).append((norm_name(r.player), r.pos, float(r.p_active), float(r.tgt_share_at_risk) if r.tgt_share_at_risk == r.tgt_share_at_risk else 0.0, float(r.carry_share_at_risk) if r.carry_share_at_risk == r.carry_share_at_risk else 0.0))
    except Exception:
        pass
    _ADJ[out_dir] = d
    return d


def _recent_usage(season, week):
    """(nkey, team) -> targets + carries over the last three completed weeks: separates a teammate who was playing until now (a role change) from one who has been gone for weeks (already in the player's log)."""
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); st = st[(st.week >= week - 3) & (st.week < week)]
    st = st.assign(k=st.player_display_name.map(norm_name), u=st.targets.fillna(0) + st.carries.fillna(0))
    return st.groupby(["k", "team"]).u.sum().to_dict()


def _game_pool(away, home):
    mk = pickle.load(open(os.path.join(OUT, f"tnf_{away}_{home}_market.pkl"), "rb"))
    try:
        md = pickle.load(open(os.path.join(OUT, f"tnf_{away}_{home}_model.pkl"), "rb"))
    except FileNotFoundError:
        md = None
    S = mk["singles"].copy()
    if len(S):
        res = [T.gate(r) for r in S.itertuples()]
        S["side"], S["shrunk"], S["model_p"], S["label"], S["log"] = [x[0] for x in res], [x[1] for x in res], [x[2] for x in res], [x[3] for x in res], [x[4] for x in res]
        junk = S.market.isin(["rush_yds", "rush_att"]) & ~S.pos.isin(["QB", "RB"])
        S.loc[junk | (S.model_p >= 0.85) | ((S.n_log < 2) & (S.label == "LEAN")), "label"] = ""
        if os.environ.get("APEX_PASS_UNDER_GATE", "1") != "0":      # DECISIONS #44: 2026 team pass attempts run 2 to 3 above the projection and the Thursday pass-volume unders went 1 of 6; no PLAY/LEAN on a passing attempts, completions or yards UNDER until the level correction is backtested (=0 restores)
            S.loc[S.market.isin(["pass_att", "pass_cmp", "pass_yds"]) & (S.side == "UNDER"), "label"] = ""
        if os.environ.get("APEX_RB_OUT_GATE") == "1":      # off by default since the Week 7 Thursday result (DECISIONS #43: the four gated CHI RB lines all won); =1 restores the old rule
            S.loc[S.market.isin(["rush_yds", "rush_att"]) & (S.pos == "RB") & S.team.isin(T.rb_out_teams(int(os.environ.get("APEX_SEASON", 2026)), int(os.environ.get("APEX_TARGET_WEEK", 7)))), "label"] = ""
        S.loc[(S.label == "LEAN") & S.market.isin(["rec", "rec_yds"]), "label"] = ""      # W6: LEAN receiving props hit 35% on 105 lines (POSTMORTEM_2026_W06 3.3); never published
        if md is not None and len(md["singles"]):
            M = md["singles"].set_index(["player", "market"])
            S["agree"] = ["yes" if ((M.p_over.get((r.player, r.market), np.nan) >= .5) == (r.side == "OVER")) else "NO" if (r.player, r.market) in M.index else "" for r in S.itertuples()]
        else:
            S["agree"] = ""
        S["fair"] = [T.american(p) for p in S.shrunk]
        S["game"] = f"{away}@{home}"
        S.loc[[(r.team, r.market) in EXCLUDE for r in S.itertuples()], "label"] = ""
        S["caution"] = ""
        S["caution"] = ""
        for t_, c_ in CAUTION.items():
            S.loc[S.team == t_, "caution"] = (S.caution + " " + c_).str.strip()
            S.loc[(S.team != t_) & (S.caution == ""), "caution"] = f"opp QB: {t_} {c_}" if t_ in (away, home) else ""
        S.loc[S.team.isin(DEMOTE) & (S.label == "PLAY"), "label"] = "LEAN"
        S["flag"] = ""
        # role change: an UNDER on a teammate of a player who was playing until this week and is now Out or Questionable (his share goes to the others; the line and the log predate that)
        risk = _team_atrisk(OUT); usage = _recent_usage(int(os.environ.get("APEX_SEASON", 2026)), int(os.environ.get("APEX_TARGET_WEEK", 7)))
        for i_, r in S.iterrows():
            if r.label == "" or r.side != "UNDER" or r.market not in ("rec", "rec_yds", "rush_att", "rush_yds"):
                continue
            for k_, pos_, pa_, tg_, cs_ in risk.get(r.team, []):
                if k_ == norm_name(r.player) or usage.get((k_, r.team), 0) <= 0:
                    continue
                if (r.market in ("rec", "rec_yds") and tg_ >= 0.10) or (r.market in ("rush_att", "rush_yds") and cs_ >= 0.20):      # any teammate's share (RB catches, QB scrambles included) goes to the others
                    S.loc[i_, "label"] = ""; S.loc[i_, "flag"] = "role change"; break
        # model far from the player's own record (85% for a side that cleared 3 of 6): a lean at most, and never a parlay leg
        hist = np.where(S.side == "OVER", S.over_games, S.under_games) / np.maximum(S.n_log, 1)
        gap = (S.label == "PLAY") & (S.model_p - hist >= 0.30) & (S.n_log >= 3)
        S.loc[gap, "label"] = "LEAN"; S.loc[gap, "flag"] = "model vs own record"
        # a player who is not 90% likely to play carries no published line (the verdict would be conditional on a designation that resolves at the inactives)
        shaky = (S.label != "") & (S.pa < 0.90)
        S.loc[shaky, "label"] = ""; S.loc[shaky, "flag"] = "availability"
        # one thesis, one line: rec/rec_yds and rush_att/rush_yds on the same player and side are the same bet; the lower-ranked one is a LEAN, flagged, and not a parlay leg
        fam = S.market.map({"rec": "rec", "rec_yds": "rec", "rush_att": "rush", "rush_yds": "rush"})
        live = S[(S.label == "PLAY") & fam.notna()].assign(fam=fam).sort_values("shrunk", ascending=False)
        dup = live[live.duplicated(["player", "side", "fam"], keep="first")].index
        S.loc[dup, "label"] = "LEAN"; S.loc[dup, "flag"] = "same bet as sibling line"
        S.loc[(S.label == "LEAN") & S.market.isin(["rec", "rec_yds"]), "label"] = ""      # receiving LEANs stay unpublished after every demotion above (POSTMORTEM_2026_W06 3.3)
    n = mk["n"]
    legs = {k: np.unpackbits(v)[:n].astype(bool) for k, v in mk["legs"].items()}
    fav = {}
    for r in S.itertuples() if len(S) else []:
        if r.label == "" or r.n_log < 3 or r.model_p >= 0.85 or r.player in BACKUP_QBS or r.team in DEMOTE or getattr(r, "flag", ""): continue
        nm = f"{r.player} {r.market} {r.side[0]}{r.line}"
        if nm in legs:
            raw = (r.p_over if r.side == "OVER" else r.p_under) / max(1 - r.p_push, 1e-6)
            fav[nm] = dict(r=min(r.shrunk / max(raw, 1e-6), 1.0), label=r.label, shrunk=r.shrunk)
    return mk, md, S, legs, mk["meta"], fav


class Pool:
    """Legs from every game: name -> (game, array, meta, shrink factor). Joint = product over games of the within-game simulated joint."""

    def __init__(self):
        self.leg = {}

    def add_game(self, game, legs, meta, fav, td_max=8, td_lo=0.12, td_hi=0.60):
        for nm in fav:
            self.leg[f"{game}: {nm}"] = dict(game=game, arr=legs[nm], meta=meta[nm], r=fav[nm]["r"], p=float(legs[nm].mean()), kind="line", shrunk=fav[nm]["shrunk"])
        td = [k for k in meta if meta[k]["kind"] == "td" and meta[k]["market"] == "any_td" and td_lo <= meta[k]["p"] <= td_hi and meta[k]["player"] not in BACKUP_QBS]
        for k in sorted(td, key=lambda x: -meta[x]["p"])[:td_max]:
            p0 = float(legs[k].mean()); sh = min(p0, 0.5 + 0.5 * (p0 - 0.5))      # TD legs shrink only downward (a 50/50 shrink would raise a longshot); the table shows raw next to shrunk
            self.leg[f"{game}: {k}"] = dict(game=game, arr=legs[k], meta=meta[k], r=sh / max(p0, 1e-6), p=p0, kind="td", shrunk=sh)
        for k in meta:
            if meta[k]["market"] == "pass_td" and k.endswith(("1+", "2+")) and meta[k]["player"] not in BACKUP_QBS:
                p0 = float(legs[k].mean()); sh = 0.5 + 0.5 * (p0 - 0.5)      # same 50/50 shrink as the line legs
                self.leg[f"{game}: {k}"] = dict(game=game, arr=legs[k], meta=meta[k], r=sh / max(p0, 1e-6), p=p0, kind="td" if k.endswith("2+") else "qb1", shrunk=sh)

    def _cluster(self, x):
        """Script cluster of a leg: volume/yardage lines go by (game, side) (a rush-attempt under, a pass-attempt under and a catch under are the same low-volume script), touchdown legs by (game, team), game legs by game."""
        L = self.leg[x]; m = L["meta"]
        if m["kind"] == "td":
            return (L["game"], "td", m.get("team", m["player"]))
        if m["kind"] == "game":
            return (L["game"], "game")
        return (L["game"], "vol", m.get("side"))

    def joint(self, names):
        by = {}
        for x in names: by.setdefault(self.leg[x]["game"], []).append(x)
        j = 1.0
        for g, xs in by.items():
            a = self.leg[xs[0]]["arr"].copy()
            for x in xs[1:]: a &= self.leg[x]["arr"]
            j *= float(a.mean())
        shr = float(np.prod([self.leg[x]["r"] for x in names]))
        return j, j * shr

    def ok(self, names):
        if sum(self.leg[x]["meta"]["market"] == "pass_td" for x in names) > 1:      # one QB passing-TD leg per ticket keeps the lists from collapsing onto QB legs
            return False
        cl = [self._cluster(x) for x in names]      # W6: legs that share a script sink together; at most one leg per script cluster per ticket
        if len(set(cl)) != len(cl):
            return False
        pl = [self.leg[x]["meta"]["player"] for x in names]
        key = [(self.leg[x]["game"], self.leg[x]["meta"]["player"], self.leg[x]["meta"]["market"]) for x in names]
        return len(set(pl)) == len(pl) and len(set(key)) == len(key)

    def search(self, pool, n, need_td=False, top=5, minp=0.0):
        res = []
        for combo in itertools.combinations(pool, n):
            if not self.ok(combo): continue
            if need_td and not any(self.leg[x]["kind"] == "td" for x in combo): continue
            j, js = self.joint(combo)
            if js >= minp: res.append((combo, js, j))
        res.sort(key=lambda t: -t[1])
        out, seen = [], set()
        for c, js, j in res:
            ids = frozenset(self.leg[x]["meta"]["player"] for x in c)
            if ids in seen: continue
            seen.add(ids); out.append((c, js, j))
            if len(out) == top: break
        return out


def _tab(df, cols, fmt=None, n=None):
    d = df.head(n) if n else df
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in d.iterrows():
        out.append("| " + " | ".join((fmt or {}).get(c, lambda v: str(v))(r[c]) if c in r else "" for c in cols) + " |")
    return "\n".join(out)


def render(run_market, run_model, tables, out_path, season=2026, week=int(os.environ.get("APEX_TARGET_WEEK", 7)), tnf_scorecard=None):
    from league_spm import load_cfg, skill_points, kicker_ev
    cfg = load_cfg()
    games = games_unplayed()
    global QB_OUT_TEAMS, BACKUP_QBS
    env_ = pd.read_csv(os.path.join(run_market, "w4_team_environment.csv"))
    QB_OUT_TEAMS = set(env_[env_.p_start_qb < 0.5].team) if "p_start_qb" in env_.columns else set()
    _P0 = pd.read_pickle(os.path.join(run_market, "proj_all.pkl"))
    BACKUP_QBS = set(_P0[(_P0.pos == "QB") & _P0.team.isin(QB_OUT_TEAMS) & (_P0.p_active >= 0.5)].player)
    if "p_start_qb" in env_.columns:      # a QB1 with a game designation: every pass-game line for that team carries a caution until the inactives confirm him
        for r_ in env_[(env_.p_start_qb < 0.9)].itertuples():
            CAUTION[r_.team] = (f"QB1 designation (start probability {r_.p_start_qb:.0%})" if r_.p_start_qb >= 0.05 else "fill-in QB (QB1 Out)")
            CAUTION_ALL[r_.team] = f"QB1 uncertain, start probability {r_.p_start_qb:.0%}"
            DEMOTE.add(r_.team)      # PLAY -> LEAN and out of parlays: the starter-role draws carry no QB-quality adjustment (BAL Huntley and TB Daniels project at or above the starters)
    FILL = fillin_qbs(season, week)
    BACKUP_QBS |= set(FILL.values())
    CAUTION.update({t: f"fill-in QB ({q})" for t, q in FILL.items()})
    CAUTION_ALL.update(FILL); DEMOTE.update(FILL)
    # --- games
    GE = pd.read_csv(os.path.join(run_market, "w4_game_environment.csv")); GM = pd.read_csv(os.path.join(run_model, "w4_game_environment.csv")).set_index(["away", "home"])
    sched = pd.read_parquet(NFLV + "games.parquet"); sched = sched[(sched.season == season) & (sched.week == week)].set_index(["away_team", "home_team"])
    L = []; w = L.append
    w(f"# Week {week} {season}: full slate predictions\n")
    w("**How to read this.** Two simulation tracks, always labeled: MARKET-ANCHORED (nflverse spread/total as the team-points prior) and MODEL-ONLY (ratings and weather, no lines). Player numbers are the market-anchored track unless stated. "
      "Props use DraftKings lines via ESPN: lines only, **no prices and no touchdown prices**. Singles are screened at an assumed -110 after shrinking the model 50/50 toward 50%; touchdown and parlay prices are FAIR odds from the joint "
      "simulation, 'play at' adds a 12% cushion. The W4 and W5 postmortems found no edge over the books on yardage and count props and calibrated anytime-TD probabilities, so read everything as a ranked lean. "
      "TD v2 multipliers and the anytime-TD floor (0.06, DECISIONS #29-30) are live.\n")
    def _asof(path, col):
        try:
            return str(pd.read_csv(path)[col].max())
        except Exception:
            return "not supplied"
    _man = os.environ.get("APEX_MANUAL_OUT", ""); _ov = os.environ.get("APEX_STATUS_OVERLAY", "")
    w(f"**Inputs used (UTC).** ESPN game-summary Outs (5 names per team cap, not the official inactives): {_asof(_man, 'as_of_utc') if _man else 'not supplied'}. Sleeper status overlay (newer Out replaces the NFL row): {_asof(_ov, 'as_of_utc') if _ov else 'not supplied'}. "
      "nflverse injuries and depth charts: latest published (no timestamp in the feed). Lines: ESPN/DraftKings (no prices). Official inactives: **not used** (about 90 minutes before each kickoff).\n")
    w("## 1. Predicted scores\n")
    w("| Game | Kickoff ET | Market (spread / total) | Market-anchored score | Win prob | Total | Model-only score | Model-only win | Fair spread |\n|---|---|---|---|---|---|---|---|---|")
    played_rows = GE[GE.note.astype(str).str.contains("PLAYED", na=False)]
    for r in GE[~GE.note.astype(str).str.contains("PLAYED", na=False)].itertuples():
        a, h = r.away, r.home
        if (a, h) not in games: continue
        m = GM.loc[(a, h)] if (a, h) in GM.index else None
        s = sched.loc[(a, h)] if (a, h) in sched.index else None
        mkt = f"{h} {-s.spread_line:+.1f} / {s.total_line}" if s is not None else ""
        note = f" ({r.note})" if isinstance(r.note, str) and r.note not in ("", "nan") else ""
        w(f"| {a}@{h}{note} | {r.date} {r.time_edt} | {mkt} | {a} {getattr(r, a + '_pts_mean'):.1f}, {h} {getattr(r, h + '_pts_mean'):.1f} | {a} {r.away_win_prob:.0%} / {h} {r.home_win_prob:.0%} | {r.total_mean:.1f} | "
          + (f"{a} {m[a + '_pts_mean']:.1f}, {h} {m[h + '_pts_mean']:.1f} | {a} {m.away_win_prob:.0%}" if m is not None else "") + f" | {h} {r.fair_spread_home:+.1f} |")
    for r in played_rows.itertuples():
        if os.environ.get("APEX_ONLY_GAMES"): break
        sc_ = sched.loc[(r.away, r.home)] if (r.away, r.home) in sched.index else None
        if sc_ is not None and pd.notna(sc_.away_score):
            w(f"\nAlready played: {r.away}@{r.home} final {r.away} {int(sc_.away_score)}, {r.home} {int(sc_.home_score)} (market {r.home} {-sc_.spread_line:+.1f}, total {sc_.total_line}; projected {getattr(r, r.away + '_pts_mean'):.1f}-{getattr(r, r.home + '_pts_mean'):.1f}).")
    # --- team tables
    off = pd.read_csv(os.path.join(tables, "team_offense.csv"), index_col=0); dfn = pd.read_csv(os.path.join(tables, "team_defense.csv"), index_col=0)
    dvp = pd.read_csv(os.path.join(tables, "dvp.csv")); mu = pd.read_csv(os.path.join(tables, "matchups.csv"))
    w(f"\n## 2. Team offense (through Week {week - 1}, per game)\n")
    o = off.sort_values("pts", ascending=False).reset_index()
    w(_tab(o, ["team", "g", "pts", "plays", "pass_rate", "pass_yds", "rush_yds", "td_per_g", "pass_epa", "rush_epa", "rz_td_pct", "turnovers"],
           {"pass_rate": lambda v: f"{v:.0%}", "rz_td_pct": lambda v: f"{v:.0%}", "pts": lambda v: f"{v:.1f}", "plays": lambda v: f"{v:.0f}", "pass_yds": lambda v: f"{v:.0f}", "rush_yds": lambda v: f"{v:.0f}",
            "td_per_g": lambda v: f"{v:.1f}", "pass_epa": lambda v: f"{v:+.2f}", "rush_epa": lambda v: f"{v:+.2f}", "turnovers": lambda v: f"{v:.1f}"}))
    w(f"\n## 3. Team defense (through Week {week - 1}, per game allowed; rank 1 = allows the most)\n")
    dd = dfn.sort_values("pts_allowed", ascending=False).reset_index().rename(columns={"opponent_team": "team", "index": "team"})
    dd["team"] = dd.iloc[:, 0]
    w(_tab(dd, ["team", "g", "pts_allowed", "pass_yds", "rush_yds", "td_allowed_pg", "pass_epa_allowed", "rush_epa_allowed", "rz_td_pct_allowed", "sacks", "takeaways"],
           {"pts_allowed": lambda v: f"{v:.1f}", "pass_yds": lambda v: f"{v:.0f}", "rush_yds": lambda v: f"{v:.0f}", "td_allowed_pg": lambda v: f"{v:.1f}", "pass_epa_allowed": lambda v: f"{v:+.2f}",
            "rush_epa_allowed": lambda v: f"{v:+.2f}", "rz_td_pct_allowed": lambda v: f"{v:.0%}", "sacks": lambda v: f"{v:.1f}", "takeaways": lambda v: f"{v:.1f}"}))
    w(f"\n## 4. Defense versus position (touchdowns allowed per game to the position, with the Week {week} opponent list)\n")
    w("Rank 1 = most TDs allowed. League TD points = 6 x TDs. Six games of data: descriptive, noisy.\n")
    for pos in ("QB", "RB", "WR", "TE"):
        x = dvp[dvp.pos == pos].sort_values("tds_pg", ascending=False)
        top = x.head(8)
        w(f"**{pos}** most TDs allowed: " + "; ".join(f"{r.defense} {r.tds_pg:.1f} TD, {r.ppr_pg:.1f} PPR" for r in top.itertuples()) + ". Fewest: " + "; ".join(f"{r.defense} {r.tds_pg:.1f}" for r in x.tail(5).itertuples()) + ".\n")
    w(f"**Week {week} matchup edges** (team vs the opponent's rank in TDs allowed to that position; top 6 per position):\n")
    for pos in ("QB", "RB", "WR", "TE"):
        c = f"opp_{pos}_td_rk"
        x = mu.dropna(subset=[c]).sort_values(c).head(6)
        w(f"- **{pos}**: " + "; ".join(f"{r.team} vs {r.opp} (rank {int(getattr(r, c))}, {getattr(r, f'opp_{pos}_td_pg'):.1f} TD/g)" for r in x.itertuples()))
    w("")
    f1 = lambda v: "" if pd.isna(v) else f"{v:.1f}"; f2 = lambda v: "" if pd.isna(v) else f"{v:.2f}"; fp = lambda v: "" if pd.isna(v) else f"{v:.0%}"
    # --- advanced (PFR via nflverse)
    if os.path.exists(os.path.join(tables, "adv_defense.csv")):
        ad = pd.read_csv(os.path.join(tables, "adv_defense.csv"), index_col=0).reset_index().rename(columns={"index": "team"})
        ao = pd.read_csv(os.path.join(tables, "adv_offense.csv"), index_col=0).reset_index().rename(columns={"index": "team"})
        w(f"## 4b. Advanced team stats (Pro Football Reference advanced tabs, via the nflverse copy; per game through Week {week - 1})\n")
        w("pro-football-reference.com serves a bot challenge (HTTP 403) to scripted requests, so the same PFR advanced data is read from the nflverse mirror. Defense coverage columns are what each defense allowed on targets against it; "
          "pass rush columns are what it generated. Sorted by passer rating allowed (highest = weakest coverage).\n")
        d1 = ad.sort_values("rating_allowed", ascending=False)
        w(_tab(d1, ["team", "g", "tgt_pg", "cmp_pct_allowed", "yds_per_tgt", "rating_allowed", "td_allowed_pg", "adot_allowed", "yac_pg", "pressures_pg", "sacks_pg", "blitzes_pg", "missed_tackle_pct"],
               {"tgt_pg": f1, "cmp_pct_allowed": fp, "yds_per_tgt": f1, "rating_allowed": f1, "td_allowed_pg": f1, "adot_allowed": f1, "yac_pg": f1, "pressures_pg": f1, "sacks_pg": f1, "blitzes_pg": f1, "missed_tackle_pct": fp}))
        w("\n**Offense: protection, accuracy, drops and run-game contact** (sorted by pressure rate allowed, highest first)\n")
        o1 = ao.sort_values("pressure_rate", ascending=False)
        w(_tab(o1, ["team", "pressured_pg", "sacked_pg", "pressure_rate", "bad_throw_rate", "drops_pg", "rec_drops_pg", "ybc_per_att", "yac_per_att", "broken_tackles_pg"],
               {"pressured_pg": f1, "sacked_pg": f1, "pressure_rate": fp, "bad_throw_rate": fp, "drops_pg": f1, "rec_drops_pg": f1, "ybc_per_att": f1, "yac_per_att": f1, "broken_tackles_pg": f1}))
        flags = []
        for r in mu.itertuples():
            a_ = ao[ao.team == r.team]; d_ = ad[ad.team == r.opp]
            if len(a_) and len(d_):
                flags.append(dict(team=r.team, opp=r.opp, pressure_rate=float(a_.pressure_rate.iloc[0]), opp_pressures=float(d_.pressures_pg.iloc[0]), opp_blitz=float(d_.blitzes_pg.iloc[0]), opp_rating=float(d_.rating_allowed.iloc[0])))
        F = pd.DataFrame(flags)
        if len(F):
            F["rush_mismatch"] = F.pressure_rate.rank() + F.opp_pressures.rank()
            top = F.sort_values("rush_mismatch", ascending=False).head(5)
            w("\n**Pass-rush mismatches this week** (offense that gets pressured often vs a defense that generates pressure): " + "; ".join(f"{r.team} vs {r.opp} (pressure rate {r.pressure_rate:.0%}, opp {r.opp_pressures:.1f} pressures/g)" for r in top.itertuples()))
            soft = F.sort_values("opp_rating", ascending=False).head(5)
            w("\n**Softest pass coverage faced** (passer rating allowed): " + "; ".join(f"{r.team} vs {r.opp} ({r.opp_rating:.0f})" for r in soft.itertuples()) + "\n")
    # --- players
    P = pd.read_pickle(os.path.join(run_market, "proj_all.pkl"))
    P = P[~P.played.astype(bool) & P.game.isin([f"{a}@{h}" for a, h in games])].copy()
    S0 = skill_points(P, cfg)
    P = P.merge(S0[["player", "team", "ev"]].rename(columns={"ev": "league_ev"}), on=["player", "team"], how="left")
    for c in ("pass_td_mean", "rush_td_mean", "rec_td_mean", "rec_mean", "rec_yds_mean", "rush_yds_mean", "pass_yds_mean", "pass_cmp_mean"):
        P[c] = pd.to_numeric(P.get(c), errors="coerce")
    RK = pd.read_csv(os.path.join(run_market, "w4_rankings_ALL.csv")).rename(columns={"ev_pts": "dk"})[["player", "team", "dk", "p25", "p75", "p90"]]
    P = P.merge(RK, on=["player", "team"], how="left")
    P["ppr"] = P.rec_mean.fillna(0) + P.rec_yds_mean.fillna(0) / 10 + P.rush_yds_mean.fillna(0) / 10 + 6 * (P.rec_td_mean.fillna(0) + P.rush_td_mean.fillna(0))
    w("## 5. Player projections (market-anchored; active-conditional means; p = chance he plays)\n")
    w("`League pts` = 6 x expected TDs x availability (this league). `DK` = DraftKings points. `PPR` = standard PPR from the same projection (no QB passing).\n")
    f1 = lambda v: "" if pd.isna(v) else f"{v:.1f}"; f2 = lambda v: "" if pd.isna(v) else f"{v:.2f}"; fp = lambda v: "" if pd.isna(v) else f"{v:.0%}"
    q = P[P.pos == "QB"].sort_values("league_ev", ascending=False).head(14)
    w("**Quarterbacks**\n"); w(_tab(q, ["player", "team", "opp", "p_active", "pass_cmp_mean", "pass_yds_mean", "pass_td_mean", "rush_yds_mean", "rush_td_mean", "any_td_pct", "league_ev", "dk"],
                                 {"p_active": fp, "pass_cmp_mean": f1, "pass_yds_mean": f1, "pass_td_mean": f2, "rush_yds_mean": f1, "rush_td_mean": f2, "any_td_pct": fp, "league_ev": f1, "dk": f1}))
    r_ = P[P.pos == "RB"].sort_values("league_ev", ascending=False).head(18)
    w("\n**Running backs**\n"); w(_tab(r_, ["player", "team", "opp", "p_active", "rush_att_mean", "rush_yds_mean", "rush_td_mean", "rec_mean", "rec_yds_mean", "rec_td_mean", "any_td_pct", "league_ev", "ppr", "dk"],
                                  {"p_active": fp, "rush_att_mean": f1, "rush_yds_mean": f1, "rush_td_mean": f2, "rec_mean": f1, "rec_yds_mean": f1, "rec_td_mean": f2, "any_td_pct": fp, "league_ev": f1, "ppr": f1, "dk": f1}))
    wr = P[P.pos == "WR"].sort_values("league_ev", ascending=False).head(24)
    w("\n**Wide receivers**\n"); w(_tab(wr, ["player", "team", "opp", "p_active", "tgt_mean", "rec_mean", "rec_yds_mean", "rec_td_mean", "any_td_pct", "league_ev", "ppr", "dk"],
                                   {"p_active": fp, "tgt_mean": f1, "rec_mean": f1, "rec_yds_mean": f1, "rec_td_mean": f2, "any_td_pct": fp, "league_ev": f1, "ppr": f1, "dk": f1}))
    te = P[P.pos == "TE"].sort_values("league_ev", ascending=False).head(14)
    w("\n**Tight ends**\n"); w(_tab(te, ["player", "team", "opp", "p_active", "tgt_mean", "rec_mean", "rec_yds_mean", "rec_td_mean", "any_td_pct", "league_ev", "ppr", "dk"],
                                {"p_active": fp, "tgt_mean": f1, "rec_mean": f1, "rec_yds_mean": f1, "rec_td_mean": f2, "any_td_pct": fp, "league_ev": f1, "ppr": f1, "dk": f1}))
    # --- kickers (league) from team points
    TT = pd.read_csv(os.path.join(run_market, "w4_team_totals.csv")); TT = TT[~TT.note.astype(str).str.contains("PLAYED", na=False)]
    kk = TT.assign(k_ev=[kicker_ev(p, cfg) for p in TT.pts_mean]).sort_values("k_ev", ascending=False).head(10)
    w("\n**Kickers (this league: FG 3, XP 1; ranked by team implied points, the only validated signal; differences are within noise)**: " + "; ".join(f"{r.team} {r.k_ev:.1f}" for r in kk.itertuples()) + "\n")
    # --- TD boards
    TD = pd.read_csv(os.path.join(run_market, "w4_td_markets.csv")).dropna(subset=["prob"])
    TD = TD[TD.game.isin([f"{a}@{h}" for a, h in games]) & ~TD.player.isin(BACKUP_QBS)]
    A = TD[TD.market == "anytime_td"].sort_values("prob", ascending=False)
    w("## 6. Touchdown boards (anytime counts rushing and receiving TDs; fair odds; 'play at' = fair + 12% cushion)\n")
    A = A.assign(adj=A.prob * A.p_active.fillna(1.0)).sort_values("adj", ascending=False)      # rank by the probability he scores in this game, not the one conditional on playing
    A2 = A.assign(fair=[T.american(p) for p in A.prob], playat=[T.play_price(p) for p in A.prob], note=[CAUTION.get(t, ("opp QB: " + CAUTION[o]) if o in CAUTION else "") for t, o in zip(A.team, A.opp)])
    w("**Top 30 anytime TD** (ranked by probability times chance he plays; 'prob' is conditional on playing)\n"); w(_tab(A2, ["player", "team", "opp", "pos", "prob", "adj", "fair", "playat", "p_active", "note"], {"prob": lambda v: f"{v:.1%}", "adj": lambda v: f"{v:.1%}", "fair": lambda v: f"{int(v):+d}", "playat": lambda v: f"{int(v):+d}", "p_active": fp}, n=30))
    X2 = TD[TD.market == "2plus_td"].sort_values("prob", ascending=False).head(10); X2 = X2.assign(fair=[T.american(p) for p in X2.prob])
    w("\n**2+ TD (top 10)**\n"); w(_tab(X2, ["player", "team", "opp", "prob", "fair"], {"prob": lambda v: f"{v:.1%}", "fair": lambda v: f"{int(v):+d}"}))
    F1 = TD[TD.market == "first_td"].sort_values("prob", ascending=False).head(10); F1 = F1.assign(fair=[T.american(p) for p in F1.prob])
    w("\n**First TD (top 10)**\n"); w(_tab(F1, ["player", "team", "opp", "prob", "fair"], {"prob": lambda v: f"{v:.1%}", "fair": lambda v: f"{int(v):+d}"}))
    lg = A[(A.prob >= 0.08) & (A.prob <= 0.25) & (A.p_active >= 0.9)].head(20)
    w("\n**Sneaky longshots** (8% to 25% anytime, active 90%+): " + "; ".join(f"{r.player} ({r.team}) {r.prob:.0%} fair {T.american(r.prob):+d}, take at {T.play_price(r.prob):+d}+" for r in lg.itertuples()) + "\n")
    # --- singles + parlays from per-game pools
    pool = Pool(); allS = []
    for a, h in games:
        try:
            mk, md, S, legs, meta, fav = _game_pool(a, h)
        except FileNotFoundError:
            continue
        pool.add_game(f"{a}@{h}", legs, meta, fav)
        if len(S): allS.append(S)
    S = pd.concat(allS, ignore_index=True)
    play = S[S.label == "PLAY"].sort_values("shrunk", ascending=False)
    lean = S[S.label == "LEAN"].sort_values("shrunk", ascending=False)
    w("## 7. Single-line screen (DraftKings lines via ESPN, assumed -110)\n")
    nthin = int(((play.market.isin(["rec", "rec_yds"]))).sum())
    w(f"{len(S)} lines screened: **{len(play)} PLAY** ({nthin} receiving, tagged thin: W6 receiving lines hit 35 to 52 percent, Thursday 7 of 11), {len(lean)} LEAN (the {min(25, len(lean))} best shown). Pulled by rule: receiving LEANs, pass-volume UNDERs, UNDERs on a teammate of a player now Out or Questionable ('role change'). PLAY = shrunk probability about 55.4%+ (about 61% raw), active 95%+, side cleared in at least half of the player's games. 'Agree' = the model-only track picks the same side.\n")
    cols = ["label", "game", "player", "market", "side", "line", "model_p", "shrunk", "fair", "log", "agree", "flag", "caution"]
    fm = {"model_p": lambda v: f"{v:.0%}", "shrunk": lambda v: f"{v:.0%}", "fair": lambda v: f"{int(v):+d}", "line": lambda v: f"{v}"}
    shown = pd.concat([play, lean.head(25)]).copy()
    shown["label"] = np.where((shown.label == "PLAY") & shown.market.isin(["rec", "rec_yds"]), "PLAY (thin)", shown.label)
    w(_tab(shown, cols, fm))
    w("\n## 8. Parlays across the slate (fair odds; legs from different games are independent, same-game legs use the joint simulation)\n")
    w("Pool: PLAY/LEAN single-line legs (shrunk), anytime-TD legs (12-60%), QB 1+ and 2+ passing TD legs. Hit probability is after the single-leg shrink. A real same-game parlay usually pays less than the product of its legs, so only take it at or better than 'play at'. "
      "Singles are in section 7; the best single touchdown plays are in section 6.\n")
    names = list(pool.leg)
    line_pool = sorted([k for k in names if pool.leg[k]["kind"] == "line"], key=lambda k: -pool.leg[k]["shrunk"])[:16]
    qb_pool = sorted([k for k in names if pool.leg[k]["kind"] == "qb1"], key=lambda k: -pool.leg[k]["p"])[:6]
    td_pool = sorted([k for k in names if pool.leg[k]["kind"] == "td"], key=lambda k: -pool.leg[k]["p"])[:12]
    for n in (2, 3, 4):
        w(f"### {n}-leg\n")
        for title, pl, need in ((f"Highest chance to hit", line_pool + qb_pool, False), ("Touchdown-led (at least one TD leg, longer shot)", line_pool[:10] + td_pool + qb_pool[:3], True)):
            res = pool.search(pl, n, need_td=need, top=4)
            w(f"**{title}**\n")
            w("| Legs | Hit probability | Raw sim | Fair odds | Play at or better |\n|---|---|---|---|---|")
            for c, js, j in res:
                w(f"| {' + '.join(c)} | {js:.1%} | {j:.1%} | {T.american(js):+d} | {T.play_price(js):+d} |")
            if not res: w("| none | | | | |")
            w("")
    # QB passing TD ladder
    qbl = sorted([(k, v) for k, v in pool.leg.items() if v["meta"]["market"] == "pass_td"], key=lambda kv: kv[0])
    byqb = {}
    for k, v in qbl:
        byqb.setdefault(v["meta"]["player"], {})[k.rsplit(" ", 1)[-1]] = v["p"]
    w("### Quarterback passing-TD ladder (calibrated market: the model beat the books here in W4; fair odds)\n")
    w("Raw simulation probability, with the 50/50-shrunk figure used in parlays in brackets. Treat anything above 85% raw as 'very likely', not a number to price. Backup QBs are not listed.\n")
    w("| QB | 1+ raw (shrunk) | 2+ raw (shrunk) |\n|---|---|---|")
    sh_ = lambda v: 0.5 + 0.5 * (v - 0.5)
    for qb, d in sorted(byqb.items(), key=lambda kv: -kv[1].get("1+", 0)):
        w(f"| {qb} | " + " | ".join(f"{d[t]:.0%} ({sh_(d[t]):.0%})" if t in d else "" for t in ("1+", "2+")) + " |")
    w("")
    w("## 9. This league (SPAMML) view\n")
    w("League points use expected TDs, so the player tables above (`League pts` column) are the lineup and waiver inputs; `apex-weekly waiver --run <run_dir> --roster ... --available ...` turns them into add/drop moves under the written rule (DECISIONS #27). "
      "Kickers: rank by team implied points only. DST is worth about 1 point a game for everyone in this league.\n")
    w(f"## 10. Last week's scorecard (Week {week - 1}, graded in POSTMORTEM_2026_W{week - 1:02d}.md)\n")
    w("| Group | Result | Expected |\n|---|---|---|\n| PLAY singles | 58.5% (n=94) | 59.7% |\n| LEAN rush and passing counts | 61.9% (n=63) | 56.0% |\n| LEAN receiving | **35.2% (n=105)** | 56.4% |\n| Anytime TD board, 204 active non-QB players | 38 scored | 40.6 predicted |\n| QB passing-TD ladder | 1+: 21 vs 19.0, 2+: 11 vs 10.4 | calibrated |\n| Parlays | 9 of 48 | 14.7 |\n\nThursday Week 7 (NE@CHI, graded in `TNF_NE_CHI_2026_W07_SCORECARD.md`): published singles 11 of 22 (50%, +0.43 units at best of six books), pass-volume unders 1 of 6, CHI RB lines withheld by the old gate 4 of 4.\n")
    w("What it says: where the model disagrees with a receiving line, the line was right, so receiving LEANs are no longer published (this report has none) and receiving PLAYs are flagged thin. Rush and passing-count lines and the QB passing-TD ladder held up. "
      "Parlays failed together on shared scripts: each ticket here holds at most one QB passing-TD leg, and every touchdown leg is shown raw next to the shrunk number.\n")
    w(f"## 11. Known gaps and audit results (read before betting)\n")
    w("Three agents (data audit, model sanity, red-team) reviewed this run before it was frozen. Each window is audited before it is frozen (QB1 against the depth chart, bye-team rows, Out players and their volume, team codes, unmatched names); the verdicts are in the run notes of the frozen manifest. Remaining, by how much they change a pick:\n")
    fill = ", ".join(f"{t} ({q})" for t, q in sorted(CAUTION_ALL.items())) if CAUTION_ALL else "none"
    w(f"1. **Fill-in quarterbacks (depth-chart QB1 who is not the 2026 completions leader):** {fill}. The backup is modeled at 92% of starter efficiency with the team's YPA and the model-only track does not discount him, so pass-game singles for these teams carry a caution flag and the QBs are left out of touchdown boards and parlay legs.")
    w("2. **Carries leak to 'other'.** The vacated-role candidate (DECISIONS #35) did not move the 27-slate backtest, so the engine is unchanged: team RBs get about 70% of team carries in the projection against about 80% in practice, so rushing props are not inflated for backs on teams with a lead back Out. Since the Thursday result (DECISIONS #43) these lines are no longer withheld; compare them with any book number you have.")
    w("3. **DAL@PHI** (Monday 8:15 PM ET) runs on this window's inputs, which stop on Sunday morning: treat its availability as provisional and use the Monday rerun. The raw `w4_*` files in the frozen run still contain the played NE@CHI rows (flagged PLAYED); this report excludes them.")
    w("4. **Availability prior.** Healthy players with no designation carry p_active of about 0.95 (fitted prior), so A.J. Brown's anytime TD is 5% below his conditional number. Inactives (about 90 minutes before each kickoff) replace the prior with certainty.")
    w("5. Anytime-TD board: the 0.10 to 0.20 bin was over-predicted 2.4x in Week 6 in the sim board (frozen-run board: predicted 15.0% vs 9.1% actual, n=55) and the top ten hit 70% against 64% predicted; the W9 postmortem checks the floor. Probabilities are conditional on playing, so discount by the p_active column.")
    w("6. Minor: about two dozen practice-squad or inactive players carry small volumes at 100% active (e.g. players listed IR/PUP who appear in the unmatched-names report).")
    w("7. Nothing here is priced: no book prices and no touchdown prices. A PLAY is a lean at an assumed -110, not an edge. Send a screenshot of any board and I will re-price against the real numbers.\n")
    w("Method: `apex-weekly run` both tracks, `espn_inactives.py`, `espn_props.py`, `slate_full.py sim/render`, `team_tables.py` (box score, play-by-play and PFR advanced), `league_spm.py`.")
    return "\n".join(L), S, A, P


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sim", "render"]); ap.add_argument("--lines"); ap.add_argument("--run-market"); ap.add_argument("--run-model"); ap.add_argument("--tables"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "sim":
        sim_all(a.lines)
    else:
        txt, *_ = render(a.run_market, a.run_model, a.tables, a.out)
        open(a.out, "w").write(txt); print("wrote", a.out)
