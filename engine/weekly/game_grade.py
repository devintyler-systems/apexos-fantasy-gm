"""Grade game-level predictions: MODEL-ONLY vs MARKET-ANCHORED vs the betting line, from frozen runs.

Usage: python game_grade.py SEASON WEEK [WEEK ...] [--out report.md]

For each completed game the last frozen pair of runs taken before kickoff is used (runs/weekly/<season>_w<WW>_{market,model}_<UTC stamp>). Compared per game, all as predictors of the final score:
  model-only        team points means from the model track (no lines)
  market-anchored   team points means from the market track (anchored to spread and total)
  line              the nflverse spread_line and total_line (home margin = spread_line; points split from the total)
Metrics: winner accuracy, win-probability Brier score, margin MAE, total MAE, team-points RMSE. The question this answers is the one that matters for the model-only track: does it beat the LINE (not market-anchored, which is the
line plus noise by construction)? Pooled sample sizes are small in a season: read a week as a data point, and use the multi-season backtest for decisions.
Frozen runs are only read. Nothing is written except the optional report.
"""
import argparse
import datetime as dt
import glob
import os

import numpy as np
import pandas as pd

from paths import NFLV

RUNS = os.path.join(os.path.dirname(__file__), "..", "..", "runs", "weekly")


def _runs(season, week, track):
    out = []
    for d in glob.glob(os.path.join(RUNS, f"{season}_w{week:02d}_{track}_*")):
        stamp = os.path.basename(d).rsplit("_", 1)[1]
        out.append((dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc), d))
    return sorted(out)


def _kickoff_utc(r):
    """gameday + gametime are Eastern; EDT (UTC-4) until the first Sunday of November, EST (UTC-5) after."""
    t = dt.datetime.strptime(f"{r.gameday} {r.gametime}", "%Y-%m-%d %H:%M")
    first_nov = dt.date(t.year, 11, 1); sunday = first_nov + dt.timedelta(days=(6 - first_nov.weekday()) % 7)
    off = 4 if t.date() < sunday else 5
    return (t + dt.timedelta(hours=off)).replace(tzinfo=dt.timezone.utc)


def _pick(runs, ko):
    ok = [r for r in runs if r[0] <= ko]
    return ok[-1] if ok else None


def grade(season, weeks):
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == season) & (g.week.isin(weeks)) & g.home_score.notna() & (g.game_type == "REG")]
    rows = []
    for r in g.itertuples():
        ko = _kickoff_utc(r); line_m, line_t = float(r.spread_line), float(r.total_line)
        res = dict(week=r.week, game=f"{r.away_team}@{r.home_team}", actual_margin=r.home_score - r.away_score, actual_total=r.home_score + r.away_score, line_margin=line_m, line_total=line_t, home_score=r.home_score, away_score=r.away_score)
        for track in ("model", "market"):
            pick = _pick(_runs(season, r.week, track), ko)
            if not pick:
                continue
            e = pd.read_csv(os.path.join(pick[1], "w4_game_environment.csv")); e = e[(e.away == r.away_team) & (e.home == r.home_team)]
            if not len(e):
                continue
            e = e.iloc[0]; h, a = float(e[f"{r.home_team}_pts_mean"]), float(e[f"{r.away_team}_pts_mean"])
            res.update({f"{track}_home": h, f"{track}_away": a, f"{track}_margin": h - a, f"{track}_total": h + a, f"{track}_pwin": float(e.home_win_prob), f"{track}_run": os.path.basename(pick[1])})
        rows.append(res)
    return pd.DataFrame(rows)


def _md(df):
    cols = list(df.columns)
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])


def summarize(d):
    out = []
    home_won = (d.actual_margin > 0).astype(float).where(d.actual_margin != 0, 0.5)
    line_p = 1 / (1 + np.exp(-d.line_margin / 6.0))      # normal-ish map of a spread to a win probability: NFL margin sd about 13.5 -> logistic scale about 6
    for name, m, t, p, hs, as_ in (("model-only", "model_margin", "model_total", "model_pwin", "model_home", "model_away"), ("market-anchored", "market_margin", "market_total", "market_pwin", "market_home", "market_away"), ("line", "line_margin", "line_total", None, None, None)):
        if m not in d:
            continue
        x = d.dropna(subset=[m])
        hw = (x.actual_margin > 0).astype(float).where(x.actual_margin != 0, 0.5)
        pw = x[p] if p else 1 / (1 + np.exp(-x.line_margin / 6.0))
        acc = float(((pw > 0.5) == (hw > 0.5)).mean())
        brier = float(((pw - hw) ** 2).mean())
        mae_m = float((x[m] - x.actual_margin).abs().mean()); mae_t = float((x[t] - x.actual_total).abs().mean())
        if hs:
            rm = float(np.sqrt((((x[hs] - x.home_score) ** 2).mean() + ((x[as_] - x.away_score) ** 2).mean()) / 2))
        else:
            hl = (x.line_total + x.line_margin) / 2; al = (x.line_total - x.line_margin) / 2
            rm = float(np.sqrt((((hl - x.home_score) ** 2).mean() + ((al - x.away_score) ** 2).mean()) / 2))
        out.append(dict(predictor=name, games=len(x), winner_acc=acc, brier=brier, margin_MAE=mae_m, total_MAE=mae_t, team_pts_RMSE=rm))
    return pd.DataFrame(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("season", type=int); ap.add_argument("weeks", type=int, nargs="+"); ap.add_argument("--out")
    a = ap.parse_args()
    d = grade(a.season, a.weeks)
    if not len(d):
        raise SystemExit("no completed games with frozen runs")
    S = summarize(d)
    lines = [f"# Game-level grade, {a.season} weeks {','.join(map(str, a.weeks))}\n", "Predictors of the final score: model-only (no lines), market-anchored (spread/total prior), and the line itself. The target for the model-only track is the LINE row.\n"]
    for wk, x in [("all", d)] + [(f"week {w}", d[d.week == w]) for w in a.weeks]:
        if len(x.dropna(subset=["model_margin"] if "model_margin" in x else ["line_margin"])):
            lines.append(f"\n## {wk}\n"); lines.append(_md(summarize(x).round(3)))
    pg = d.dropna(subset=["model_margin"]).assign(model_err=lambda x: x.model_margin - x.actual_margin, market_err=lambda x: x.market_margin - x.actual_margin, line_err=lambda x: x.line_margin - x.actual_margin)
    lines.append("\n## By game\n")
    lines.append(_md(pg[["week", "game", "home_score", "away_score", "model_margin", "market_margin", "line_margin", "model_total", "market_total", "line_total", "model_pwin", "market_pwin"]].round(2)))
    txt = "\n".join(lines); print(txt)
    if a.out:
        open(a.out, "w").write(txt + "\n")
