"""DECISIONS #88 addendum: re-score a candidate tag against its baseline on the priced anytime-TD player-games (#84 close set, #85 early set).

  python tools/backtest/gl5_price_compare.py BASE_A CAND_A BASE_B CAND_B
Needs var/bt/odds_td_{TAG}.pkl and var/bt/odds_early_{TAG}.pkl for every tag (odds_price_eval.py td, odds_early_eval.py).
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import odds_price_eval as ope  # noqa: E402
from odds_price_eval import ll, br, REPO  # noqa: E402
from odds_early_eval import cboot  # noqa: E402

BT = os.path.join(REPO, "var", "bt")
D = None


def close(tag):
    T = pd.read_pickle(os.path.join(BT, f"odds_td_{tag}.pkl"))[["di", "season", "y", "cons", "eng", "game_id"]].rename(columns={"cons": "book"})
    T["pos"] = D.loc[T.di, "pos"].values; T["rush_att"] = D.loc[T.di, "rush_att"].values
    return T


def scores(T):
    rows = []
    for S in (2023, 2024, 2025, "all"):
        t = T if S == "all" else T[T.season == S]; bl = t.book + .2 * (t.eng - t.book)
        rows.append(dict(season=S, n=len(t), eng_ll=ll(t.eng, t.y), w02_ll=ll(bl, t.y), book_ll=ll(t.book, t.y), eng_br=br(t.eng, t.y), w02_br=br(bl, t.y), book_br=br(t.book, t.y)))
    return pd.DataFrame(rows).set_index("season")


def topdec(T, edges):
    t = T.assign(gap=T.eng - T.book); t["dec"] = np.digitize(t.gap, edges)      # fixed baseline decile edges
    top = t[t.dec == 9]; rb = top[top.pos == "RB"]; com = rb[(rb.rush_att >= 6) & (rb.rush_att < 14)]
    f = lambda g: dict(n=len(g), hit=round(g.y.mean(), 3), book=round(g.book.mean(), 3), eng=round(g.eng.mean(), 3), over_hit_pts=round(100 * (g.eng.mean() - g.y.mean()), 1)) if len(g) else {}
    return dict(top_all=f(top), top_RB=f(rb), top_committee_RB_6to14=f(com), RB_share=round(len(rb) / max(len(top), 1), 3),
                all_committee_RB=f(t[(t.pos == "RB") & (t.rush_att >= 6) & (t.rush_att < 14)]))


def early(tag):
    E = pd.read_pickle(os.path.join(BT, f"odds_early_{tag}.pkl")); E = E[E.healthy & E.xmove.notna()]
    g = E[(E.gap >= .05) & (E.gap < .10)]; lo = cboot(g, "xmove")
    pl = np.where(g.y == 1, ope.pay(g.best_e), -1.0)
    return dict(n=len(g), rel_move_pts=round(100 * g.xmove.mean(), 2), rel_90=tuple(np.round(100 * np.array(lo), 2)), roi_pct=round(100 * pl.mean(), 1),
                early_ll_eng=round(ll(E.eng, E.y), 5), early_ll_5050=round(ll(.5 * (E.eng + E.b_e), E.y), 5), early_ll_book=round(ll(E.b_e, E.y), 5))


if __name__ == "__main__":
    D = ope.engine(sys.argv[1])
    a = sys.argv[1:]
    for base, cand in zip(a[0::2], a[1::2]):
        B, C = close(base), close(cand)
        assert len(B) == len(C) and (B.di.values == C.di.values).all(), "priced sets differ"
        sb, sc = scores(B), scores(C)
        d = (sc - sb)[["eng_ll", "w02_ll", "eng_br", "w02_br"]].round(5); d.columns = ["d_" + c for c in d.columns]
        print(f"\n=== {cand} vs {base} on {len(B)} priced player-games (negative = candidate better)\n" + pd.concat([sb[["eng_ll", "w02_ll", "book_ll"]].round(5).add_prefix("base_"),
              sc[["eng_ll", "w02_ll"]].round(5).add_prefix("cand_"), d], axis=1).to_string())
        edges = np.quantile(B.eng - B.book, np.linspace(.1, .9, 9))
        print("top decile (baseline edges):\n base", topdec(B, edges), "\n cand", topdec(C, edges))
        print("2025 early, healthy, gap 5-10 rule:\n base", early(base), "\n cand", early(cand))
