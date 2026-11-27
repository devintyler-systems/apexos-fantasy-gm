"""DECISIONS #91 live-equivalence: the same sample games anchored to the closing snapshot vs a T-2h snapshot (both built by build_anchor_lines_raw.py).

  python tools/backtest/anchor_live_check.py var/anchor/lines_t2h_s.csv rise6A anchA ancC ancT
Scores evaluate.metrics on the sample games only (season / week / teams of the lines file), plus DK-point MAE as anchor_backtest.py.
"""
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import evaluate as ev  # noqa: E402
from anchor_backtest import dk_act, dk_proj  # noqa: E402

lines, tags = sys.argv[1], sys.argv[2:]
L = pd.read_csv(lines); G = L[["season", "week", "away", "home"]].drop_duplicates()
teams = {(r.season, r.week, t) for r in G.itertuples() for t in (r.away, r.home)}
rows = []
for tag in tags:
    ds, ts = [], []
    for (S, W), _ in G.groupby(["season", "week"]):
        st, sn, g = ev._actuals(S)
        P = pd.read_pickle(ev.OUT + f"bt_{S}_w{W}_{tag}.pkl"); pl = set(zip(sn[sn.week == W].nkey, sn[sn.week == W].team))
        P = P[[(a, b) in pl and (S, W, b) in teams for a, b in zip(P.nkey, P.team)]]
        P = P.merge(st[st.week == W][["nkey", "team"] + ev.A], on=["nkey", "team"], how="left").fillna({c: 0 for c in ev.A}); ds.append(P)
    D = pd.concat(ds, ignore_index=True); r = ev.metrics(D, None)
    rows.append(dict(tag=tag, n=len(D), dk_mae=float((dk_proj(D) - dk_act(D)).abs().mean()), **{c: r.get(c) for c in ev.CORE if c in r}))
R = pd.DataFrame(rows).set_index("tag")
print(f"sample: {len(G)} games {sorted(set(zip(G.season, G.week)))}\n" + R.round(4).to_string())
base = tags[0]
print("\ndelta vs " + base + " (negative = better):\n" + (R.drop(columns="n") - R.loc[base].drop("n")).round(4).to_string())
