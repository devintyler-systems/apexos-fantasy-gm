"""Grade published picks against actuals (generalised from docs/weekly/reference_scripts/w06_grade_*.py).

Usage:
  python pick_grade.py SEASON WEEK --sims DIR=AWAY@HOME,AWAY@HOME [--sims DIR2=...] [--runs RUN_DIR[=GAMES] ...] [--out report.md]

  --sims   a sim directory (OUT of a `slate_full.py sim` / `tnf_full.py sim` pair, holding tnf_AWAY_HOME_{market,model}.pkl) and the games it was published from.
           Grades every screened single line (PLAY / LEAN / all), anytime-TD calibration and the QB passing-TD ladder. Repeat for each publication.
  --runs   frozen run directories (runs/weekly/<run_id>), optionally =AWAY@HOME,... to take only those games from that run; grades the anytime-TD board (w4_td_markets.csv) for their games when the sims are gone. Read-only.

Actuals: nflverse `stats_player_week` for the week; a game nflverse has not posted yet (Monday night on Tuesday morning) falls back to the ESPN box score (name-joined, labelled in the output).
No book prices exist for any prop, so this is hit rate against the model's own (shrunk) probability, never ROI. Frozen runs are never written to.
"""
import argparse
import json
import urllib.request

import numpy as np
import pandas as pd

from load import norm_name
from paths import NFLV

COLS = ["completions", "attempts", "passing_yards", "passing_tds", "carries", "rushing_yards", "rushing_tds", "receptions", "targets", "receiving_yards", "receiving_tds"]
M = {"rec": "receptions", "rec_yds": "receiving_yards", "rush_yds": "rushing_yards", "rush_att": "carries", "pass_att": "attempts", "pass_cmp": "completions", "pass_yds": "passing_yards"}
ESPN2NV = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
SB = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={d}"
SUM = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={e}"


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def espn_box(away, home, gameday):
    """ESPN box score for one game as rows shaped like nflverse stats (name-joined; no gsis ids). Empty frame if the game is not found or not final."""
    d = _get(SB.format(d=gameday.replace("-", "")))
    for ev in d.get("events", []):
        comp = ev["competitions"][0]
        teams = {ESPN2NV.get(c["team"]["abbreviation"], c["team"]["abbreviation"]) for c in comp["competitors"]}
        if teams != {away, home}:
            continue
        if not comp["status"]["type"].get("completed"):
            return pd.DataFrame()
        s = _get(SUM.format(e=ev["id"]))
        rows = {}
        for t in s["boxscore"]["players"]:
            tm = ESPN2NV.get(t["team"]["abbreviation"], t["team"]["abbreviation"])
            for st in t["statistics"]:
                lab = st["labels"]
                for a in st["athletes"]:
                    r = rows.setdefault((a["athlete"]["displayName"], tm), dict.fromkeys(COLS, 0.0))
                    v = dict(zip(lab, a["stats"]))
                    if st["name"] == "passing":
                        c, att = (v["C/ATT"].split("/") + ["0"])[:2]
                        r["completions"], r["attempts"], r["passing_yards"], r["passing_tds"] = _num(c), _num(att), _num(v["YDS"]), _num(v["TD"])
                    elif st["name"] == "rushing":
                        r["carries"], r["rushing_yards"], r["rushing_tds"] = _num(v["CAR"]), _num(v["YDS"]), _num(v["TD"])
                    elif st["name"] == "receiving":
                        r["receptions"], r["receiving_yards"], r["receiving_tds"], r["targets"] = _num(v["REC"]), _num(v["YDS"]), _num(v["TD"]), _num(v.get("TGTS", 0))
        out = pd.DataFrame([dict(player_display_name=n, team=tm, **r) for (n, tm), r in rows.items()])
        out["source"] = "espn"
        return out
    return pd.DataFrame()


def load_actuals(season, week, games):
    """nflverse stats for the week plus an ESPN box for every game of `games` (AWAY@HOME) that nflverse has no rows for."""
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet")
    st = st[st.week == week][["player_display_name", "team"] + COLS].copy()
    st["source"] = "nflverse"
    have = set(st.team)
    g = pd.read_parquet(NFLV + "games.parquet")
    g = g[(g.season == season) & (g.week == week)]
    parts, fb = [st], []
    for k in games:
        a, h = k.split("@")
        if a in have or h in have:
            continue
        gd = g[(g.away_team == a) & (g.home_team == h)].gameday.iloc[0]
        b = espn_box(a, h, str(gd)[:10])
        if len(b):
            parts.append(b)
            fb.append(k)
    A = pd.concat(parts, ignore_index=True).fillna(0)
    A["k"] = A.player_display_name.map(norm_name)
    A = A.groupby(["k", "team"], as_index=False).sum(numeric_only=True)
    return A, fb


def _ll(p, y):
    return float(-(y * np.log(np.clip(p, 1e-6, 1)) + (1 - y) * np.log(np.clip(1 - p, 1e-6, 1))).mean())


def grade_sims(sims, A, rep):
    import slate_full as SF
    act = {(r.k, r.team): r for r in A.itertuples()}
    byname = {}
    for (kk, tt), rr in act.items():
        byname.setdefault(kk, []).append(rr)
    rows, tdrows, qbrows = [], [], []
    for d, gl in sims:
        SF.OUT = d if d.endswith("/") else d + "/"
        for g in gl:
            a, h = g.split("@")
            try:
                mk, md, Sg, legs, meta, fav = SF._game_pool(a, h)
            except Exception as e:
                rep(f"skip {g}: {e}")
                continue
            Sg = Sg.copy(); Sg["src"] = d
            rows.append(Sg)
            for k, v in meta.items():
                if v["kind"] == "td" and v["market"] == "any_td":
                    tdrows.append(dict(game=g, player=v["player"], team=v.get("team"), p=v["p"], src=d))
                if v["market"] == "pass_td" and k.endswith(("1+", "2+")):
                    qbrows.append(dict(game=g, player=v["player"], k=k.rsplit(" ", 1)[-1], p=v["p"]))
    if not rows:
        return
    S_ = pd.concat(rows, ignore_index=True)

    def actual(player, team, market):
        r = act.get((norm_name(player), team))
        return np.nan if r is None else float(getattr(r, M[market]))   # not in the box = did not play = void

    S_["act"] = [actual(r.player, r.team, r.market) for r in S_.itertuples()]
    S_["res"] = np.where(S_.act.isna(), np.nan, np.where(S_.act == S_.line, np.nan, ((S_.act > S_.line) == (S_.side == "OVER")).astype(float)))

    def line(df, name):
        d = df.dropna(subset=["res"])
        rep(f"| {name} | {len(d)} | {d.res.mean():.1%} | {d.shrunk.mean():.1%} | {d.model_p.mean():.1%} |" if len(d) else f"| {name} | 0 | | | |")

    rep("\n### Single lines (pushes and DNP void)\n\n| Group | n | Hit | Expected (shrunk) | Raw model |\n|---|---|---|---|---|")
    line(S_, "ALL screened")
    for lab in ("PLAY", "LEAN"):
        line(S_[S_.label == lab], lab)
    rcv = S_.market.isin(["rec", "rec_yds"])
    line(S_[(S_.label == "PLAY") & rcv], "PLAY receiving")
    line(S_[(S_.label == "PLAY") & ~rcv], "PLAY rush and passing")
    line(S_[(S_.label == "LEAN") & rcv], "LEAN receiving")
    line(S_[(S_.label == "LEAN") & ~rcv], "LEAN rush and passing")
    L = S_[S_.label != ""].dropna(subset=["res"])
    rep("\nBy market (labeled lines):\n\n```\n" + L.groupby("market").agg(n=("res", "size"), hit=("res", "mean"), exp=("shrunk", "mean")).round(3).to_string() + "\n```")
    rep("\nBias (model mean minus actual) on screened lines is in `act` vs `mean` of the sim; per-market hit above is the calibration read.")
    d = S_.dropna(subset=["res"]).copy()
    d["bin"] = pd.cut(d.model_p, [0, .55, .6, .65, .7, .75, .8, 1])
    rep("\nBy raw model probability:\n\n```\n" + d.groupby("bin", observed=True).agg(n=("res", "size"), hit=("res", "mean"), raw=("model_p", "mean"), shrunk=("shrunk", "mean")).round(3).to_string() + "\n```")

    T_ = pd.DataFrame(tdrows)
    if len(T_):
        def tds(player, team):
            c = byname.get(norm_name(player))
            c = [x for x in (c or []) if x.team == team] or c
            return np.nan if not c else float(sum(x.rushing_tds + x.receiving_tds for x in c))
        T_["act"] = [tds(r.player, r.team) for r in T_.itertuples()]
        T_ = T_.dropna(subset=["act"]).drop_duplicates(["player", "game"])
        T_["y"] = (T_.act >= 1).astype(float)
        _td_report(T_, rep)
    Q = pd.DataFrame(qbrows).drop_duplicates(["player", "k"])
    if len(Q):
        def qbact(r):
            m = [x for (kk, t), x in act.items() if kk == norm_name(r.player)]
            return np.nan if not m else float(max(x.passing_tds for x in m))
        Q["act"] = [qbact(r) for r in Q.itertuples()]
        Q = Q.dropna(subset=["act"])
        Q["y"] = np.where(Q.k == "1+", Q.act >= 1, Q.act >= 2).astype(float)
        for k in ("1+", "2+"):
            q = Q[Q.k == k]
            rep(f"\nQB passing TD {k}: n={len(q)} sum of probabilities {q.p.sum():.1f} vs actual {q.y.sum():.0f}")


def _td_report(T_, rep, label="Anytime TD board"):
    rep(f"\n### {label}\n\nn={len(T_)} players, predicted {T_.p.sum():.1f} vs actual {T_.y.sum():.0f}; log loss {_ll(T_.p, T_.y):.4f} vs {_ll(np.full(len(T_), T_.y.mean()), T_.y):.4f} for a flat base rate")
    T_ = T_.copy()
    T_["bin"] = pd.cut(T_.p, [0, .1, .2, .3, .4, .5, .6, 1])
    rep("\n```\n" + T_.groupby("bin", observed=True).agg(n=("y", "size"), p=("p", "mean"), act=("y", "mean")).round(3).to_string() + "\n```")
    top = T_.sort_values("p", ascending=False)
    for n in (10, 30):
        rep(f"top {n}: hit {top.head(n).y.mean():.0%} (predicted {top.head(n).p.mean():.0%})")


def grade_runs(runs, A, rep):
    import os
    act = {(r.k, r.team): r for r in A.itertuples()}
    rows = []
    for rd in runs:
        rd, _, gl = rd.partition("=")
        t = pd.read_csv(os.path.join(rd, "w4_td_markets.csv"))
        if gl:
            t = t[t.game.isin(gl.split(","))]
        t = t[(t.market == "anytime_td") & (t.p_active >= .95) & (t.pos != "QB")]
        for r in t.itertuples():
            a = act.get((norm_name(r.player), r.team))
            if a is not None:
                rows.append(dict(player=r.player, team=r.team, game=r.game, p=r.prob, y=float(a.rushing_tds + a.receiving_tds >= 1), run=os.path.basename(rd)))
    if rows:
        T_ = pd.DataFrame(rows).drop_duplicates(["player", "game"])
        _td_report(T_, rep, "Anytime TD board from frozen runs (active >= 95%, non-QB, appeared in the box score)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("season", type=int); ap.add_argument("week", type=int)
    ap.add_argument("--sims", action="append", default=[], help="DIR=AWAY@HOME,AWAY@HOME")
    ap.add_argument("--runs", nargs="*", default=[]); ap.add_argument("--out")
    a = ap.parse_args()
    sims = [(s.split("=", 1)[0], s.split("=", 1)[1].split(",")) for s in a.sims]
    games = sorted({g for _, gl in sims for g in gl})
    if a.runs:
        import os
        for rd in a.runs:
            rd, _, gl = rd.partition("=")
            m = gl.split(",") if gl else pd.read_csv(os.path.join(rd, "w4_td_markets.csv"), usecols=["game"]).game.unique()
            games += [g for g in m if g not in games]
    A, fb = load_actuals(a.season, a.week, games)
    lines = [f"# Pick grading, {a.season} week {a.week}\n", f"Actuals: nflverse stats; ESPN box-score fallback for: {', '.join(fb) if fb else 'none (nflverse complete)'}. No book prices exist, so hit rate is against the model's own probability, not ROI."]
    rep = lines.append
    if sims:
        grade_sims(sims, A, rep)
    if a.runs:
        grade_runs(a.runs, A, rep)
    txt = "\n".join(lines)
    print(txt)
    if a.out:
        open(a.out, "w").write(txt + "\n")


if __name__ == "__main__":
    main()
