"""Append-only calibration ledger: aggregated graded counts per week, kept in the repo WITHOUT any line or price.

Usage (from Python): ledger_rows(df, week, source) -> DataFrame; append(path, rows).  df needs: market, model_p (probability of the chosen side), hit (0/1), optional anchor_p (book de-vigged probability of that side).
Rows: week, source (screen_50 | book_anchor), market, bucket_type (raw | gap), bucket, n, hits, sum_model_p, sum_anchor_p. Re-running a week replaces that week's rows for the source.
This is what lets the gap-aware shrink be fit on several weeks without committing odds files."""
import os

import numpy as np
import pandas as pd

RAW_BINS = [.5, .55, .6, .65, .7, .75, .8, .85, 1.0001]
GAP_BINS = [-1.0, -.2, -.1, -.05, .05, .1, .2, 1.0]


def ledger_rows(df, week, source):
    out = []
    d = df.copy(); d["anchor_p"] = d["anchor_p"] if "anchor_p" in d else np.nan
    for bt, col, bins in (("raw", "model_p", RAW_BINS), ("gap", "gap", GAP_BINS)):
        if col not in d:
            continue
        d["b"] = pd.cut(d[col], bins)
        for (m, b), g in d.dropna(subset=["b"]).groupby(["market", "b"], observed=True):
            out.append(dict(week=week, source=source, market=m, bucket_type=bt, bucket=str(b), n=len(g), hits=int(g.hit.sum()), sum_model_p=float(g.model_p.sum()), sum_anchor_p=float(g.anchor_p.sum()) if g.anchor_p.notna().any() else np.nan))
    return pd.DataFrame(out)


def append(path, rows):
    old = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    if len(old) and len(rows):
        old = old[~((old.week == rows.week.iloc[0]) & (old.source == rows.source.iloc[0]))]
    pd.concat([old, rows], ignore_index=True).to_csv(path, index=False)
