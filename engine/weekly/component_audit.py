"""Market-by-market component audit of frozen runs against nflverse actuals (read-only).

Usage: python component_audit.py SEASON WEEK [WEEK ...] [--runs DIR] [--track market|model|both] [--min-active 0.5]

Per week it takes, per game and track, the latest frozen run whose as_of_utc is before kickoff (postmortem.pick_runs), grades it into a SCRATCH
copy of the run folders (pass --runs to a copy: grade() writes grade_players.csv beside the manifest, frozen runs are never to be written) and pools weeks.
Per market: n, mean projected / actual, bias, MAE, RMSE, P25-P75 coverage and the implied dispersion scale, rank skill (Spearman) against the naive
'prior weeks per-game average', calibration slope of actual on projection, and MAE of the naive average and of a 50/50 blend. Rows are players with a logged snap (grade.py drops the rest).
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

from load import norm_name
from paths import NFLV
from postmortem import load_games, pick_runs, player_frame

# market, projection mean col, actual col, naive volume col, P25 col, P75 col, row filter
MARKETS = [
    ("pass_yds", "pass_yds_mean", "passing_yards", "attempts", "pass_yds_p25", "pass_yds_p75", lambda d: (d.pos == "QB") & (d.pass_yds_mean >= 100)),
    ("pass_cmp", "pass_cmp_mean", "completions", "attempts", "pass_cmp_p25", "pass_cmp_p75", lambda d: (d.pos == "QB") & (d.pass_yds_mean >= 100)),
    ("pass_td", "pass_td_mean", "passing_tds", "attempts", "pass_td_p25", "pass_td_p75", lambda d: (d.pos == "QB") & (d.pass_yds_mean >= 100)),
    ("qb_rush_yds", "rush_yds_mean", "rushing_yards", "carries", None, None, lambda d: (d.pos == "QB") & (d.pass_yds_mean >= 100)),
    ("rb_rush_yds", "rush_yds_mean", "rushing_yards", "carries", "rush_yds_p25", "rush_yds_p75", lambda d: (d.pos == "RB") & (d.rush_att_mean >= 4)),
    ("rb_carries", "rush_att_mean", "carries", "carries", None, None, lambda d: (d.pos == "RB") & (d.rush_att_mean >= 4)),
    ("rec_wr", "rec_mean", "receptions", "targets", "rec_p25", "rec_p75", lambda d: (d.pos == "WR") & (d.rec_mean >= 1)),
    ("rec_te", "rec_mean", "receptions", "targets", "rec_p25", "rec_p75", lambda d: (d.pos == "TE") & (d.rec_mean >= 1)),
    ("rec_rb", "rec_mean", "receptions", "targets", "rec_p25", "rec_p75", lambda d: (d.pos == "RB") & (d.rec_mean >= 1)),
    ("rec_yds_wr", "rec_yds_mean", "receiving_yards", "targets", "rec_yds_p25", "rec_yds_p75", lambda d: (d.pos == "WR") & (d.rec_mean >= 1)),
    ("rec_yds_te", "rec_yds_mean", "receiving_yards", "targets", "rec_yds_p25", "rec_yds_p75", lambda d: (d.pos == "TE") & (d.rec_mean >= 1)),
    ("rec_yds_rb", "rec_yds_mean", "receiving_yards", "targets", "rec_yds_p25", "rec_yds_p75", lambda d: (d.pos == "RB") & (d.rec_mean >= 1)),
]


def naive_table(season, week):
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet")
    st = st[(st.season_type == "REG") & (st.week < week)].copy()
    st["nkey"] = st.player_display_name.map(norm_name)
    return st


def spearman(a, b):
    return float(pd.Series(a).rank().corr(pd.Series(b).rank())) if len(a) > 4 else float("nan")


def audit(frames, min_active):
    rows = []
    for name, pc, ac, vol, lo, hi, mask in MARKETS:
        parts = []
        for P, st in frames:
            d = P[mask(P) & (P.p_active >= min_active)].copy()
            h = st[st[vol] > 0].groupby("nkey")[ac].agg(["mean", "size"])
            d["naive"] = d.nkey.map(h["mean"]); d["ng"] = d.nkey.map(h["size"])
            parts.append(d)
        d = pd.concat(parts)
        d = d[d[pc].notna() & d[ac].notna()]
        if len(d) < 8:
            continue
        e = d[pc] - d[ac]
        dn = d[d.naive.notna() & (d.ng >= 2)]
        r = dict(market=name, n=len(d), proj=d[pc].mean(), actual=d[ac].mean(), bias=e.mean(), bias_pct=100 * e.mean() / max(d[ac].mean(), 1e-9), mae=e.abs().mean(), rmse=float(np.sqrt((e ** 2).mean())),
                 spearman=spearman(d[pc], d[ac]))
        if lo is not None and d[lo].notna().any():
            dd = d[d[lo].notna()]
            r["cov_p25_p75"] = float(((dd[ac] >= dd[lo]) & (dd[ac] <= dd[hi])).mean())
            half = ((dd[hi] - dd[lo]) / 2).clip(lower=1e-6)
            z = (dd[ac] - dd[pc]) / half
            r["abs_z_med"] = float(z.abs().median())      # 1.0 would be exact when the interval were symmetric; the nominal median |z| for a normal is 1.0 on the IQR half-width
            r["disp_scale"] = float(z.abs().median() / 1.0)  # >1: intervals too narrow; <1: too wide
        slope = np.polyfit(d[pc], d[ac], 1)[0] if d[pc].std() > 0 else float("nan")
        r["calib_slope"] = float(slope)
        if len(dn) >= 8:
            r.update(n_naive=len(dn), mae_model_sub=(dn[pc] - dn[ac]).abs().mean(), mae_naive=(dn.naive - dn[ac]).abs().mean(), mae_blend=((dn[pc] + dn.naive) / 2 - dn[ac]).abs().mean(),
                     spearman_model_sub=spearman(dn[pc], dn[ac]), spearman_naive=spearman(dn.naive, dn[ac]))
        rows.append(r)
    return pd.DataFrame(rows)


def td_audit(frames, min_active):
    d = pd.concat([P[(P.p_active >= min_active) & (P.pos != "QB")] for P, _ in frames])
    d = d[d.any_td_pct.notna()]
    d["scored"] = (d.rushing_tds + d.receiving_tds > 0).astype(int)
    rows = []
    for lo, hi in [(0, .05), (.05, .1), (.1, .2), (.2, .3), (.3, .45), (.45, 1)]:
        x = d[(d.any_td_pct >= lo) & (d.any_td_pct < hi)]
        if len(x):
            rows.append(dict(bin=f"{lo:.2f}-{hi:.2f}", n=len(x), predicted=x.any_td_pct.mean(), scored=x.scored.mean()))
    p, y = d.any_td_pct.clip(1e-4, 1 - 1e-4), d.scored
    ll = float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()); base = y.mean()
    llb = float(-(y * np.log(base) + (1 - y) * np.log(1 - base)).mean())
    return pd.DataFrame(rows), dict(n=len(d), log_loss=ll, log_loss_flat=llb, brier=float(((p - y) ** 2).mean()), brier_flat=float(((base - y) ** 2).mean()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("season", type=int)
    ap.add_argument("weeks", type=int, nargs="+")
    ap.add_argument("--runs", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runs", "weekly"))
    ap.add_argument("--track", default="both")
    ap.add_argument("--min-active", type=float, default=0.5)
    a = ap.parse_args(argv)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    for track in (["market", "model"] if a.track == "both" else [a.track]):
        frames = []
        for w in a.weeks:
            g = load_games(a.season, w); pick = pick_runs(a.runs, a.season, w, g)
            P = player_frame(pick, a.season, w, track)
            if P.empty:
                continue
            P["nkey"] = P.player.map(norm_name)
            frames.append((P, naive_table(a.season, w)))
        print(f"\n## component audit, track={track}, season {a.season} weeks {a.weeks}, p_active >= {a.min_active}, rows graded (logged an offensive snap)\n")
        print(audit(frames, a.min_active).round(3).to_string(index=False))
        t, s = td_audit(frames, a.min_active)
        print(f"\nanytime TD (non-QB, played): {s}\n{t.round(3).to_string(index=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
