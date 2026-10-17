"""QB candidate list for a team: drop released/retired/exempt QBs and add depth-chart QBs with no 2026 attempts (DECISIONS #31).

Found in the Week 6 audit: PHI with Hurts Out projected Andy Dalton (released after Week 5, 1 attempt in 2026) as the fill-in because `pas` only holds QBs with attempts;
Tanner McKee (depth chart QB2, no attempts) was never a candidate. Live runs only: the caller passes `gone` and `add_depth` only when the roster snapshot is a full current roster,
so historical backtests are unchanged.
"""
import numpy as np
import pandas as pd


def adjust_qbs(q, dc, gone, add_depth):
    """q: pas rows for the team (needs player, nkey, team, Att). dc: depth-chart QB rows for the team (player_name, nkey, pos_rank). gone: set of nkeys that cannot play.
    Returns q without `gone` QBs plus one blank row (Att 0) for every depth-chart QB that is not in q (when add_depth)."""
    q = q[~q.nkey.isin(gone)].copy()
    if add_depth and len(dc):
        have = set(q.nkey)
        rows = []
        for r in dc.itertuples():
            if r.nkey in have or r.nkey in gone:
                continue
            blank = {c: np.nan for c in q.columns}
            blank.update(player=r.player_name, nkey=r.nkey, Att=0.0)
            if "team" in q.columns and len(q):
                blank["team"] = q.team.iloc[0]
            rows.append(blank)
            have.add(r.nkey)
        if rows:
            q = pd.concat([q, pd.DataFrame(rows)], ignore_index=True)
    return q
