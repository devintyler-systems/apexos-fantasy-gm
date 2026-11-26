"""Backtest evaluation for the weekly engine (weeks 4-12, 2023-25). Reads the pickles written by tools/backtest/run_tag.sh.

  python tools/backtest/evaluate.py floor   TAG_A TAG_B TAG_C              noise floor = max |pairwise pooled delta| over three baseline seeds
  python tools/backtest/evaluate.py compare BASE_A CAND_A [BASE_B CAND_B]   pooled + per-season deltas and the noise-aware verdict
  python tools/backtest/evaluate.py quant   TAG [TAG ...]                  pinball loss and P10/P25/P75/P90 coverage per stat
  python tools/backtest/evaluate.py team    TAG                             team points: bias and RMSE by season and week, totals bias
  python tools/backtest/evaluate.py tdcal   TAG                             anytime-TD calibration by probability bucket and position

Scope is the same as engine/weekly/eval_candidate.py: projected players with an offensive snap that week, actuals from nflverse.
Floors are written to var/bt/floor_<A>.json by `floor` and read by `compare --floor A`. Negative delta = better.
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "engine", "weekly"))
os.environ.setdefault("APEX_OUT", os.path.join(REPO, "var", "bt"))
from load import norm_name  # noqa: E402
from paths import NFLV, OUT  # noqa: E402

warnings.filterwarnings("ignore")
NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
SEASONS = (2023, 2024, 2025)
WEEKS = range(4, 13)
A = ["completions", "passing_yards", "passing_tds", "carries", "rushing_yards", "receptions", "receiving_yards", "rushing_tds", "receiving_tds"]
CORE = ["rec_yds_mae", "rec_mae", "rush_yds_mae", "rush_att_mae", "td_ll", "team_rmse", "pass_yds_mae", "rec_yds_pin", "rush_yds_pin", "pass_yds_pin"]
_ACT = {}


def _actuals(S):
    if S not in _ACT:
        st = pd.read_parquet(NFLV + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy()
        st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name)
        sn = pd.read_parquet(NFLV + f"snap_counts_{S}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.offense_snaps > 0)].copy()
        sn["team"] = sn.team.replace(NV2T); sn["nkey"] = sn.player.map(norm_name)
        g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == S) & (g.game_type == "REG")].copy()
        g["home_team"] = g.home_team.replace(NV2T); g["away_team"] = g.away_team.replace(NV2T)
        _ACT[S] = (st, sn, g)
    return _ACT[S]


def load(tag):
    rows, trows = [], []
    for S in SEASONS:
        st, sn, g = _actuals(S)
        for W in WEEKS:
            P = pd.read_pickle(OUT + f"bt_{S}_w{W}_{tag}.pkl")
            pl = set(zip(sn[sn.week == W].nkey, sn[sn.week == W].team))
            P = P[[(a, b) in pl for a, b in zip(P.nkey, P.team)]]
            P = P.merge(st[st.week == W][["nkey", "team"] + A], on=["nkey", "team"], how="left").fillna({c: 0 for c in A})
            P["season"], P["week"] = S, W
            rows.append(P)
            T = pd.read_pickle(OUT + f"btteam_{S}_w{W}_{tag}.pkl"); T = T[T.away.notna()]
            T = T.merge(g[g.week == W][["away_team", "home_team", "away_score", "home_score", "spread_line", "total_line"]], left_on=["away", "home"], right_on=["away_team", "home_team"])
            T["season"], T["week"] = S, W; trows.append(T)
    return pd.concat(rows, ignore_index=True), pd.concat(trows, ignore_index=True)


def pinball(y, qs):
    """mean pinball loss over the quantile columns given as {q: array}."""
    out = [np.mean(np.maximum(q * (y - v), (q - 1) * (y - v))) for q, v in qs.items()]
    return float(np.mean(out))


def metrics(D, T):
    sk = D[D.pos != "QB"]; r = {}
    for nm, mask, pc, ac in (("rec_yds", sk.rec >= 1.0, "rec_yds", "receiving_yards"), ("rec", sk.rec >= 1.0, "rec", "receptions"),
                             ("rush_yds", sk.rush_att >= 4, "rush_yds", "rushing_yards"), ("rush_att", sk.rush_att >= 4, "rush_att", "carries")):
        d = sk[mask]; r[nm + "_mae"] = float((d[pc] - d[ac]).abs().mean()); r[nm + "_ratio"] = float(d[ac].sum() / d[pc].sum())
    t = sk[sk.any_td >= 0.03]; p = np.clip(t.any_td, .01, .99); y = ((t.rushing_tds + t.receiving_tds) >= 1).astype(float)
    r["td_ll"] = float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    r["td_brier"] = float(np.mean((p - y) ** 2))
    qb = D[(D.pos == "QB") & (D.pass_yds >= 100)]
    r["pass_yds_mae"] = float((qb.pass_yds - qb.passing_yards).abs().mean()) if len(qb) else np.nan
    for stat, d, ac in (("rec_yds", sk[sk.rec >= 1.0], "receiving_yards"), ("rush_yds", sk[sk.rush_att >= 4], "rushing_yards"), ("pass_yds", qb, "passing_yards")):
        if not len(d) or f"{stat}_q10" not in d:
            continue
        qs = {q / 100: d[f"{stat}_q{q}"].values for q in (10, 25, 75, 90)}
        r[f"{stat}_pin"] = pinball(d[ac].values, qs)
        r[f"{stat}_iqr_cov"] = float(((d[ac] >= d[f"{stat}_q25"]) & (d[ac] <= d[f"{stat}_q75"])).mean())
    if T is not None and len(T):
        r["team_rmse"] = float(np.sqrt(np.mean(np.r_[(T.away_pts - T.away_score) ** 2, (T.home_pts - T.home_score) ** 2])))
        r["team_bias"] = float(np.mean(np.r_[T.away_pts - T.away_score, T.home_pts - T.home_score]))
    return r


def table(tag):
    D, T = load(tag)
    res = {"all": metrics(D, T)}
    for S in SEASONS:
        res[str(S)] = metrics(D[D.season == S], T[T.season == S])
    return pd.DataFrame(res).T, D, T


def cmd_floor(tags):
    R = {t: table(t)[0].loc["all"] for t in tags}
    fl, pairs = {}, [(0, 1), (0, 2), (1, 2)]
    for c in CORE:
        d = [abs(R[tags[i]][c] - R[tags[j]][c]) for i, j in pairs if c in R[tags[i]] and c in R[tags[j]]]
        fl[c] = float(max(d)) if d else np.nan
        print(f"{c:14s} pairwise {' / '.join(f'{x:.4f}' for x in d)}  floor {fl[c]:.4f}")
    json.dump(dict(tags=tags, floor=fl), open(OUT + f"floor_{tags[0]}.json", "w"), indent=1)
    print("written", OUT + f"floor_{tags[0]}.json")


def cmd_compare(args):
    fl = None
    if "--floor" in args:
        i = args.index("--floor"); fl = json.load(open(OUT + f"floor_{args[i + 1]}.json"))["floor"]; args = args[:i] + args[i + 2:]
    pairs = [(args[i], args[i + 1]) for i in range(0, len(args), 2)]
    deltas = []
    for base, cand in pairs:
        Rb, Rc = table(base)[0], table(cand)[0]
        cols = [c for c in CORE if c in Rb and c in Rc]
        d = (Rc[cols] - Rb[cols])
        print(f"\nDELTA {cand} - {base} (negative = better)\n" + d.round(4).to_string())
        print("levels (base):\n" + Rb.loc[["all"], cols + [c for c in ("rec_yds_ratio", "rush_yds_ratio", "team_bias", "rec_yds_iqr_cov", "rush_yds_iqr_cov", "pass_yds_iqr_cov") if c in Rb]].round(4).to_string())
        deltas.append(d.loc["all"])
    if fl is not None:
        M = pd.concat(deltas, axis=1)
        print("\nNOISE-AWARE CHECK (contracts/weekly/grading.v0.1.yaml promotion_rule_noise_aware): floor, per-seed delta, mean, verdict")
        for c in M.index:
            f = fl.get(c, np.nan); m = M.loc[c].mean()
            tag = "BETTER" if (M.loc[c] < -2 * f).all() else ("WORSE" if m > 2 * f else "noise")
            print(f"  {c:14s} floor {f:.4f}  deltas {' / '.join(f'{x:+.4f}' for x in M.loc[c])}  mean {m:+.4f}  -> {tag}")


def cmd_quant(tags):
    for tag in tags:
        D, _ = load(tag); sk = D[D.pos != "QB"]
        print(f"\n{tag}")
        for stat, d, ac in (("rec_yds", sk[sk.rec >= 1.0], "receiving_yards"), ("rec", sk[sk.rec >= 1.0], "receptions"),
                            ("rush_yds", sk[sk.rush_att >= 4], "rushing_yards"), ("pass_yds", D[(D.pos == "QB") & (D.pass_yds >= 100)], "passing_yards")):
            if f"{stat}_q10" not in d:
                continue
            y = d[ac]
            cov = {f"<=P10": (y <= d[f"{stat}_q10"]).mean(), "P25-P75": ((y >= d[f"{stat}_q25"]) & (y <= d[f"{stat}_q75"])).mean(), ">P90": (y > d[f"{stat}_q90"]).mean()}
            qs = {q / 100: d[f"{stat}_q{q}"].values for q in (10, 25, 75, 90)}
            print(f"  {stat:9s} n={len(d):5d} pinball {pinball(y.values, qs):.4f}  " + "  ".join(f"{k} {v:.3f}" for k, v in cov.items()))


def cmd_team(tag):
    _, T = load(tag)
    L = pd.concat([pd.DataFrame(dict(season=T.season, week=T.week, proj=T.away_pts, act=T.away_score, side="away")),
                   pd.DataFrame(dict(season=T.season, week=T.week, proj=T.home_pts, act=T.home_score, side="home"))])
    L["err"] = L.proj - L.act
    g = L.groupby(["season", "week"]).agg(n=("err", "size"), bias=("err", "mean"), rmse=("err", lambda e: float(np.sqrt(np.mean(e ** 2)))), proj=("proj", "mean"), act=("act", "mean"))
    print(g.round(2).to_string())
    print("\nby season\n" + L.groupby("season").agg(bias=("err", "mean"), rmse=("err", lambda e: float(np.sqrt(np.mean(e ** 2))))).round(3).to_string())
    T = T.assign(ptot=T.away_pts + T.home_pts, atot=T.away_score + T.home_score)
    T["tot_err"] = T.ptot - T.atot; T["line_err"] = T.total_line - T.atot
    print("\ngame totals: engine bias {:.2f} MAE {:.2f} | line bias {:.2f} MAE {:.2f} (n={})".format(T.tot_err.mean(), T.tot_err.abs().mean(), T.line_err.mean(), T.line_err.abs().mean(), len(T)))


def cmd_tdcal(tag):
    D, _ = load(tag); sk = D[(D.pos != "QB") & (D.any_td >= 0.03)].copy()
    sk["y"] = ((sk.rushing_tds + sk.receiving_tds) >= 1).astype(float)
    sk["b"] = pd.cut(sk.any_td, [0, .1, .2, .3, .4, .5, .6, 1])
    print(sk.groupby("b", observed=True).agg(n=("y", "size"), proj=("any_td", "mean"), hit=("y", "mean")).round(3).to_string())
    print(sk.groupby("pos").agg(n=("y", "size"), proj=("any_td", "mean"), hit=("y", "mean")).round(3).to_string())


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    {"floor": cmd_floor, "compare": cmd_compare, "quant": cmd_quant, "team": lambda r: cmd_team(r[0]), "tdcal": lambda r: cmd_tdcal(r[0])}[cmd](rest)
