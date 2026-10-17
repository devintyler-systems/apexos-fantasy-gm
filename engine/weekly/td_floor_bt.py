"""Backtest behind candidate v3 (anytime-TD floor, DECISIONS #29): reads bt_{season}_w{week}_v4.pkl from backtest_multi.sh (model track, weeks 4-12, 2023-25),
joins actuals, and reports calibration by probability bin plus the held-out log-loss change for each floor value. The floor is applied after the simulation, so every
other promotion metric (rec_yds MAE, rec MAE, team RMSE) is unchanged by construction.
Usage: APEX_NFLV=... APEX_OUT=<dir holding the bt pickles> python td_floor_bt.py"""
import numpy as np
import pandas as pd

from paths import NFLV, OUT
from load import norm_name

NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}
GRID = [0.04, 0.05, 0.06, 0.065, 0.07, 0.075, 0.08, 0.09, 0.10]


def sample():
    rows = []
    for S in (2023, 2024, 2025):
        st = pd.read_parquet(NFLV + f"stats_player_week_{S}.parquet"); st = st[st.season_type == "REG"].copy(); st["team"] = st.team.replace(NV2T); st["nkey"] = st.player_display_name.map(norm_name)
        sn = pd.read_parquet(NFLV + f"snap_counts_{S}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.offense_snaps > 0)].copy(); sn["team"] = sn.team.replace(NV2T); sn["nkey"] = sn.player.map(norm_name)
        for W in range(4, 13):
            P = pd.read_pickle(OUT + f"bt_{S}_w{W}_v4.pkl")
            played = set(zip(sn[sn.week == W].nkey, sn[sn.week == W].team)); P = P[[(a, b) in played for a, b in zip(P.nkey, P.team)]]
            a = st[st.week == W][["nkey", "team", "receiving_tds", "rushing_tds"]]
            P = P.merge(a, on=["nkey", "team"], how="left"); P["season"] = S; rows.append(P)
    D = pd.concat(rows, ignore_index=True)
    D = D[(D.pos != "QB") & (D.rec >= 0.5) & (D.p_active >= 0.5)].copy()
    D["y"] = ((D.receiving_tds.fillna(0) + D.rushing_tds.fillna(0)) >= 1).astype(int)
    return D


def ll(y, p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def main():
    D = sample()
    print(f"n={len(D)} predicted {D.any_td.mean():.4f} actual {D.y.mean():.4f}")
    for s, d in D.groupby("season"):
        t = d[d.any_td < 0.05]
        print(s, f"n={len(d)} pred {d.any_td.mean():.3f} act {d.y.mean():.3f} | <5% bin n={len(t)} pred {t.any_td.mean():.3f} act {t.y.mean():.3f}")
    print("floor: held-out log-loss change by season (negative = better), pooled")
    for f in GRID:
        by = [ll(d.y.values, np.maximum(d.any_td.values, f)) - ll(d.y.values, d.any_td.values) for _, d in D.groupby("season")]
        pooled = ll(D.y.values, np.maximum(D.any_td.values, f)) - ll(D.y.values, D.any_td.values)
        print(f"{f:.3f}", " ".join(f"{x:+.4f}" for x in by), f"| pooled {pooled:+.4f}")
    return D


if __name__ == "__main__":
    main()
