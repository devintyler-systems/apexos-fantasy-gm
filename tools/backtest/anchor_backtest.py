"""DECISIONS #91: market-anchored engine output (APEX_ANCHOR_XLSX) vs the engine baseline, split by whether the player had his own line.

  python tools/backtest/anchor_backtest.py BASE CAND [BASE CAND ...]      e.g. rise6A anchA rise6B anchB prn3A anchA
DK points (no bonuses, no INT/fumbles: identical on both sides) = rec + 0.1 (rec_yds + rush_yds) + 6 TDs + 0.04 pass_yds + 4 pass_td.
Scope as evaluate.py: projected players with an offensive snap. 'lined' = an own anchored market (rec_yds, rush_yds, pass_yds or anytime_td);
'lineless' = no own line (team-rescaled or untouched); 'no_yds_line' = no own yardage line (TD-only or none), the group the team rescale acts on. TD log loss on skill players with P(TD) >= 0.03, as evaluate.metrics.
"""
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import evaluate as ev  # noqa: E402

OWN = {"rec_yds", "rush_yds", "pass_yds", "anytime_td"}
YDS = {"rec_yds", "rush_yds", "pass_yds"}


def dk_proj(d): return d.rec + .1 * (d.rec_yds + d.rush_yds) + 6 * d.exp_td + .04 * d.pass_yds + 4 * d.pass_td
def dk_act(d): return d.receptions + .1 * (d.receiving_yards + d.rushing_yards) + 6 * (d.rushing_tds + d.receiving_tds) + .04 * d.passing_yards + 4 * d.passing_tds


def tdll(d):
    t = d[(d.pos != "QB") & (d.any_td >= .03)]; p = np.clip(t.any_td, .01, .99); y = ((t.rushing_tds + t.receiving_tds) >= 1).astype(float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), len(t)


def main(args):
    for base, cand in zip(args[::2], args[1::2]):
        B, C = ev.load(base)[0], ev.load(cand)[0]
        k = ["season", "week", "team", "nkey"]
        M = B.merge(C[k + ["rec", "rec_yds", "rush_yds", "exp_td", "pass_yds", "pass_td", "any_td", "anchored"]], on=k, suffixes=("_b", ""))
        M["own"] = [bool(OWN & set(str(a).split(","))) for a in M.anchored]
        M["own_yds"] = [bool(YDS & set(str(a).split(","))) for a in M.anchored]
        Bm = M.copy(); [Bm.__setitem__(c, Bm[c + "_b"]) for c in ("rec", "rec_yds", "rush_yds", "exp_td", "pass_yds", "pass_td", "any_td")]
        y = dk_act(M); M["e_c"] = (dk_proj(M) - y).abs(); M["e_b"] = (dk_proj(Bm) - y).abs()
        rows = []
        for nm, q in (("all", M.index == M.index), ("lined", M.own), ("lineless", ~M.own), ("yds_line", M.own_yds), ("no_yds_line", ~M.own_yds)):
            for S in list(ev.SEASONS) + ["all"]:
                s = q & ((M.season == S) if S != "all" else True)
                llb, n = tdll(Bm[s]); llc, _ = tdll(M[s])
                rows.append(dict(group=nm, season=S, n=int(s.sum()), dk_mae_base=round(M.e_b[s].mean(), 4), dk_mae_cand=round(M.e_c[s].mean(), 4),
                                 dk_delta=round(M.e_c[s].mean() - M.e_b[s].mean(), 4), td_n=n, td_ll_base=round(llb, 5), td_ll_cand=round(llc, 5), td_delta=round(llc - llb, 5)))
        print(f"\n=== {cand} vs {base}: DK-point MAE and anytime-TD log loss by line status (negative delta = better)\n" + pd.DataFrame(rows).to_string(index=False))
        print("no-own-yardage-line share of players:", round(float((~M.own_yds).mean()), 3), " of projected DK pts:", round(float(dk_proj(M)[~M.own_yds].sum() / dk_proj(M).sum()), 3))
        print("lineless share of players:", round(float((~M.own).mean()), 3), " of projected DK pts:", round(float(dk_proj(M)[~M.own].sum() / dk_proj(M).sum()), 3))


if __name__ == "__main__":
    main(sys.argv[1:])
