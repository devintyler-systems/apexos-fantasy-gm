"""Quarterback-market candidate vs baseline on the weeks 4-12, 2023-25 backtest (pairs with bt_variant.sh; the promotion rule's rec_yds / TD metrics cannot see a QB change).

Usage: APEX_OUT=<dir with bt_{season}_w{week}_{tag}.pkl> python eval_qb.py BASE_TAG CAND_TAG [CAND_TAG ...]
Per tag and season: passing-yards MAE, bias, P25-P75 coverage and pinball loss (quantiles 10/25/75/90), completions MAE, pass-TD MAE and Brier of P(1+ pass TD) is not available in the pickle, so
pass TD is scored by MAE of the mean. Players: QBs with projected passing yards >= 100, projected active, with a recorded offensive snap (grade.py scope). Negative delta = better.
"""
import sys

import numpy as np
import pandas as pd

from load import norm_name
from paths import OUT, NFLV

NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
SEASONS = (2023, 2024, 2025)


def actuals(S):
    st = pd.read_parquet(NFLV + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy(); st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name)
    sn = pd.read_parquet(NFLV + f"snap_counts_{S}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.offense_snaps > 0)].copy(); sn["team"] = sn.team.replace(NV2T); sn["nkey"] = sn.player.map(norm_name)
    return st, sn


def pin(y, q, tau):
    d = y - q
    return np.maximum(tau * d, (tau - 1) * d)


def load(tag, S, st, sn):
    fr = []
    for w in range(4, 13):
        try:
            b = pd.read_pickle(f"{OUT}bt_{S}_w{w}_{tag}.pkl")
        except FileNotFoundError:
            continue
        b = b[(b.pos == "QB") & (b.pass_yds >= 100) & (b.p_active >= 0.5)].copy(); b["week"] = w
        a = st[st.week == w][["nkey", "team", "passing_yards", "completions", "passing_tds"]].drop_duplicates(["nkey", "team"])
        played = set(zip(sn[sn.week == w].nkey, sn[sn.week == w].team))
        b = b[[(x, y) in played for x, y in zip(b.nkey, b.team)]].merge(a, on=["nkey", "team"], how="inner"); fr.append(b)
    return pd.concat(fr)


def metrics(d):
    y = d.passing_yards
    cov = float(((y >= d.pass_yds_q25) & (y <= d.pass_yds_q75)).mean()); c8 = float(((y >= d.pass_yds_q10) & (y <= d.pass_yds_q90)).mean())
    pl = np.mean([pin(y, d.pass_yds_q10, .1).mean(), pin(y, d.pass_yds_q25, .25).mean(), pin(y, d.pass_yds_q75, .75).mean(), pin(y, d.pass_yds_q90, .9).mean()])
    return dict(n=len(d), mae=float((d.pass_yds - y).abs().mean()), bias=float((d.pass_yds - y).mean()), cov50=cov, cov80=c8, pinball=float(pl),
                cmp_mae=float((d.pass_cmp - d.completions).abs().mean()), ptd_mae=float((d.pass_td - d.passing_tds).abs().mean()), ptd_bias=float((d.pass_td - d.passing_tds).mean()))


if __name__ == "__main__":
    tags = sys.argv[1:]
    A = {S: actuals(S) for S in SEASONS}
    res = {}
    for t in tags:
        for S in SEASONS:
            res[(t, S)] = metrics(load(t, S, *A[S]))
        res[(t, "all")] = metrics(pd.concat([load(t, S, *A[S]) for S in SEASONS]))
    pd.set_option("display.width", 200)
    print(pd.DataFrame(res).T.round(3).to_string())
    for t in tags[1:]:
        print(f"\n{t} minus {tags[0]}")
        print(pd.DataFrame({k[1]: {m: res[(t, k[1])][m] - res[(tags[0], k[1])][m] for m in ("mae", "pinball", "cmp_mae", "ptd_mae")} for k in res if k[0] == t}).T.round(3).to_string())
