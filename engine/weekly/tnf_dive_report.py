"""Build the single-game dossier markdown from tnf_dive pickles + the priced book lines (edges_all_rows.csv, local only) + the frozen run's TD driver text.
Usage: python tnf_dive_report.py AWAY HOME MKT_RUN_DIR MODEL_RUN_DIR OUT_MD   (reads ../../var/out_market|out_model/{dive_*.pkl,edges_all_rows.csv})"""
import sys, numpy as np, pandas as pd, os
from load import norm_name
AWAY, HOME, MR, OR, OUTMD = sys.argv[1:6]
V = "../../var/"; GAME = f"{AWAY}@{HOME}"
Dm, Gm = pd.read_pickle(V + f"out_market/dive_{AWAY}_{HOME}_market.pkl"); Do, Go = pd.read_pickle(V + f"out_model/dive_{AWAY}_{HOME}_model.pkl")
Em = pd.read_csv(V + "out_market/edges_all_rows.csv"); Eo = pd.read_csv(V + "out_model/edges_all_rows.csv")
Em = Em[Em.game == GAME].copy(); Eo = Eo[Eo.game == GAME].copy(); Em["key"] = Em.player.map(norm_name); Eo["key"] = Eo.player.map(norm_name)
TDM = pd.read_csv(MR + "/w4_td_markets.csv"); TDM["key"] = TDM.player.map(norm_name)
Do = Do.set_index("key"); NOBOOK = set(pd.read_csv(V + "out_market/odds_no_book_lines.csv").player.map(norm_name))
am = lambda x: f"{int(x):+d}"; pc = lambda x: "" if pd.isna(x) else f"{100 * x:.0f}%"; pc1 = lambda x: "" if pd.isna(x) else f"{100 * x:.1f}%"
SUSPECT = {"jalon daniels": "role mismatch with books (books: 182.5 pass yds / 28.5 att / 44.5 rush yds; model 250 / 33 / 15)"}
BOOKMKT = {"pass_att": "pass_att", "pass_cmp": "pass_cmp", "pass_yds": "pass_yds", "rush_att": "rush_att", "rush_yds": "rush_yds", "rec": "rec", "rec_yds": "rec_yds"}

def book(E, key, mk):
    x = E[(E.key == key) & (E.market == mk) & E.is_main_line] if "is_main_line" in E else E.iloc[0:0]
    if not len(x): return None
    ov = x[x.side == "over"]; un = x[x.side == "under"]
    if not len(ov): return None
    bo = ov.sort_values("odds", ascending=False).iloc[0]; bu = un.sort_values("odds", ascending=False).iloc[0] if len(un) else None
    return dict(line=float(bo.line), o=int(bo.odds), ob=bo.book, u=None if bu is None else int(bu.odds), ub=None if bu is None else bu.book, nv=float(ov.novig_p.mean()), model=float(ov.model_p.iloc[0]), feeds=int(ov.book.nunique()))
def tdbook(E, key, mk):
    x = E[(E.key == key) & (E.market == mk)]
    if not len(x): return None
    b = x.sort_values("odds", ascending=False).iloc[0]
    return dict(best=int(b.odds), book=b.book, vigin=float(b.imp_vig_in), nv=float(x.novig_p.median()), feeds=int(x.book.nunique()), vig_med=float(x.imp_vig_in.median()))
def f(v, n): return "" if pd.isna(v) else (f"{v:.{n}f}")
def statrow(label, r, ro, s, n, mk, key, E, Eo_, note=""):
    lo, mean, hi = r[f"{s}_lo"], r[f"{s}_mean"], r[f"{s}_hi"]
    mo = ro[f"{s}_mean"] if ro is not None else np.nan
    b = book(E, key, mk) if mk else None
    if b:
        bm = book(Eo_, key, mk); mod = b["model"]; capd = mod > 0.85 or mod < 0.15
        line = f"{b['line']:g}"; px = f"O {am(b['o'])} {b['ob']} / U {am(b['u']) if b['u'] is not None else 'n/a'} {b['ub'] or ''}"
        cmp_ = "n/a (cap)" if capd else f"{pc(mod)} vs {pc(b['nv'])}"; gap = "" if capd else f"{100 * (mod - b['nv']):+.0f}"
        feeds = b["feeds"]
    else: line = px = cmp_ = gap = ""; feeds = ""
    return f"| {label} | {f(lo, n)} | **{f(mean, n)}** | {f(hi, n)} | {f(mo, n)} | {line} | {px} | {cmp_} | {gap} | {feeds} |"
HDR = "| Stat | Floor (P10) | **MAIN** | Ceiling (P90) | Model-only main | Book line | Best Over / Under | Model P(over) vs book no-vig | Gap (pts) | Feeds |\n|---|---|---|---|---|---|---|---|---|---|"
def tdrows(r, key):
    out = []
    for mk, lab, p in (("anytime_td", "Anytime TD (rush/rec)", r["any_td"]), ("first_td", "First TD scorer", r["first_td"])):
        b = tdbook(Em, key, mk)
        if b: out.append(f"| {lab} | model {pc1(p)} (x availability {pc1(p * r['p_active'])}) | | | | | best {am(b['best'])} {b['book']} | vig-in {pc1(b['vigin'])}; Estimated no-vig {pc1(b['nv'])} | {100 * (p - b['nv']):+.1f} | {b['feeds']} |")
        else: out.append(f"| {lab} | model {pc1(p)} (x availability {pc1(p * r['p_active'])}) | | | | | no book price | | | |")
    return out
def block(key, r, ro, kind):
    head = f"#### {r['player']} ({r['team']} {r['pos']}), availability {pc(r['p_active'])}" + (" [NO BOOK LINES]" if key in NOBOOK else "")
    L = [head]
    if key in SUSPECT: L.append(f"> Caution: {SUSPECT[key]}.")
    if r["p_active"] < 0.97: L.append(f"> Availability {pc(r['p_active'])}: the NFL report has this player listed; every number below is conditional on playing.")
    L += [HDR]
    S = lambda lab, s, n, mk: statrow(lab, r, ro, s, n, mk, key, Em, Eo)
    if kind == "QB":
        L += [S("Pass attempts", "pass_att", 1, "pass_att"), S("Completions", "pass_cmp", 1, "pass_cmp"), S("Passing yards", "pass_yds", 0, "pass_yds"), S("Passing TD", "pass_td", 2, None), S("Interceptions", "pass_int", 2, None),
              S("Rush attempts", "rush_att", 1, "rush_att"), S("Rush yards", "rush_yds", 0, "rush_yds"), S("Rush TD", "rush_td", 2, None)]
    elif kind == "RB":
        L += [S("Rush attempts", "rush_att", 1, "rush_att"), S("Rush yards", "rush_yds", 0, "rush_yds"), S("Rush TD", "rush_td", 2, None), S("Targets", "tgt", 1, None), S("Receptions", "rec", 1, "rec"), S("Receiving yards", "rec_yds", 0, "rec_yds"),
              S("Receiving TD", "rec_td", 2, None),
              f"| **Overall: scrimmage yards** | {r['scr_lo']:.0f} | **{r['scr_mean']:.0f}** | {r['scr_hi']:.0f} | {ro['scr_mean']:.0f} | | | | | |", f"| **Overall: total TD** | {r['tot_td_lo']:.0f} | **{r['tot_td_mean']:.2f}** | {r['tot_td_hi']:.0f} | {ro['tot_td_mean']:.2f} | | | | | |"]
    else:
        L += [S("Targets", "tgt", 1, None), S("Receptions", "rec", 1, "rec"), S("Receiving yards", "rec_yds", 0, "rec_yds"), S("Receiving TD", "rec_td", 2, None)]
        if r["rush_att_mean"] >= 0.3: L += [S("Rush attempts", "rush_att", 1, "rush_att"), S("Rush yards", "rush_yds", 0, "rush_yds"), S("Rush TD", "rush_td", 2, None)]
    L += [f"| DraftKings points | {r['dk_lo']:.1f} | **{r['dk_mean']:.1f}** | {r['dk_hi']:.1f} | {ro['dk_mean']:.1f} | | | | | |"] + tdrows(r, key) + [""]
    return L

out = [f"# Thursday night deep dive: {AWAY} @ {HOME}, Week 5 2026 (kickoff 2026-10-08 20:15 ET)\n"]
w = out.append
w(f"- **MAIN** = mean of the simulated outcome among games the player plays, MARKET-ANCHORED track (nflverse spread/total as the team-points prior), run `{os.path.basename(MR)}`. Model-only main (ratings + weather, no lines), run `{os.path.basename(OR)}`, sits beside it.")
w("- **FLOOR / CEILING** = 10th / 90th percentile of the same 20,000 correlated simulations: a game that goes worse or better than expected for that player. Both are conditional on the player being active; availability is shown separately. A floor of 0 on touchdowns means at least 10% of simulated games end with none.")
w("- **Book columns** come from NFL_Week5_Odds.xlsx (snapshot 22:10 to 22:15Z) and the Add-On workbook (22:37 to 22:42Z), US Pacific converted +7h to UTC; lines may have moved. Best price = the best Over (or Under) among 12 books at the main line (the line with the most feeds, ties to the price closest to even). Gap = model P(over) minus book no-vig P(over), in points, and it is diagnostic, not an edge. Probabilities above 85% or below 15% are shown as n/a (cap).")
w("- **The model runs low on counts and yardage versus the books** (receptions, attempts, completions, yards), so Over gaps are biased negative. TB passing is overprojected (see the cautions).")
w("- Anytime and first-TD no-vig numbers are a flat 10% haircut on a one-sided market, labeled Estimated, and one-signed by construction. No pick here is labeled edge or confident.\n")
w("## Game\n")
for nm, G in (("Market-anchored", Gm), ("Model-only", Go)):
    pass
w("| Track | Winner (win prob) | " + f"{AWAY} pts: mean / P10-P90 | {HOME} pts: mean / P10-P90 | Total: mean / P10-P90 |\n|---|---|---|---|---|")
for nm, G in (("Market-anchored", Gm), ("Model-only", Go)):
    hw = G["home_win"]; win, wp = (HOME, hw) if hw >= .5 else (AWAY, 1 - hw)
    w(f"| {nm} | {win} {wp * 100:.0f}% | {G['away_mean']:.1f} / {G['away_p10']:.0f}-{G['away_p90']:.0f} | {G['home_mean']:.1f} / {G['home_p10']:.0f}-{G['home_p90']:.0f} | {G['total_mean']:.1f} / {G['total_p10']:.0f}-{G['total_p90']:.0f} |")
GL = pd.read_csv(V + "out_market/odds_game_lines.csv"); GL = GL[GL.game == GAME]
sp = GL[(GL.market == "spreads") & (GL.label == GL.home_team)]; tt = GL[(GL.market == "totals") & (GL.label == "Over")]
w(f"\nBooks: {HOME} {sp.point.mode().iloc[0]:+.1f} (range {sp.point.min():+.1f} to {sp.point.max():+.1f}), total {tt.point.mode().iloc[0]:.1f} (range {tt.point.min():.1f} to {tt.point.max():.1f}).\n")
keep = Dm[(Dm.dk_mean >= 1.5) & (Dm.p_active >= 0.4) & ~Dm.key.isin(["emari demercado"])].copy()
w("## Availability and data conflicts\n")
w("- Baker Mayfield (TB QB1) is Out on the NFL report (thumb) and Out on DK. Jalon Daniels starts.")
w("- DK lists Emari Demercado (DAL RB) and Camden Brown (DAL WR) OUT while nflverse has no row for either; the model had Demercado active, so he is excluded here. Jonathan Mingo (DAL WR) is Questionable on the NFL report (DNP, illness) with DK blank: the model has him at 50%.")
w("- CeeDee Lamb: Full participation, thigh designation (model 95% active); DK blank. nflverse has no Thursday report and no inactives list yet.\n")
QB = keep[keep.pos == "QB"].sort_values("dk_mean", ascending=False); RB = keep[keep.pos == "RB"].sort_values("dk_mean", ascending=False); PC = keep[keep.pos.isin(["WR", "TE"])].sort_values("dk_mean", ascending=False)
w("## Summary tables (MAIN projection; floor-ceiling in brackets)\n")
w("**Quarterbacks**\n\n| Player | Att | Cmp | Pass yds | Pass TD | INT | Rush att | Rush yds | Anytime TD | First TD | DK pts |\n|---|---|---|---|---|---|---|---|---|---|---|")
for r in QB.itertuples(): w(f"| {r.player} ({r.team}) | {r.pass_att_mean:.1f} | {r.pass_cmp_mean:.1f} | {r.pass_yds_mean:.0f} [{r.pass_yds_lo:.0f}-{r.pass_yds_hi:.0f}] | {r.pass_td_mean:.2f} [{r.pass_td_lo:.0f}-{r.pass_td_hi:.0f}] | {r.pass_int_mean:.2f} | {r.rush_att_mean:.1f} | {r.rush_yds_mean:.0f} [{r.rush_yds_lo:.0f}-{r.rush_yds_hi:.0f}] | {pc1(r.any_td)} | {pc1(r.first_td)} | {r.dk_mean:.1f} [{r.dk_lo:.0f}-{r.dk_hi:.0f}] |")
w("\n**Running backs**\n\n| Player | Rush att | Rush yds | Rush TD | Tgt | Rec | Rec yds | Rec TD | Scrimmage yds | Total TD | Anytime TD | First TD | DK pts |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in RB.itertuples(): w(f"| {r.player} ({r.team}) | {r.rush_att_mean:.1f} | {r.rush_yds_mean:.0f} [{r.rush_yds_lo:.0f}-{r.rush_yds_hi:.0f}] | {r.rush_td_mean:.2f} | {r.tgt_mean:.1f} | {r.rec_mean:.1f} | {r.rec_yds_mean:.0f} [{r.rec_yds_lo:.0f}-{r.rec_yds_hi:.0f}] | {r.rec_td_mean:.2f} | {r.scr_mean:.0f} [{r.scr_lo:.0f}-{r.scr_hi:.0f}] | {r.tot_td_mean:.2f} | {pc1(r.any_td)} | {pc1(r.first_td)} | {r.dk_mean:.1f} [{r.dk_lo:.0f}-{r.dk_hi:.0f}] |")
w("\n**Receivers (WR/TE)** (rushing shown where the model projects any)\n\n| Player | Tgt | Rec | Rec yds | Rec TD | Rush att / yds | Anytime TD | First TD | DK pts |\n|---|---|---|---|---|---|---|---|---|")
for r in PC.itertuples(): w(f"| {r.player} ({r.team} {r.pos}) | {r.tgt_mean:.1f} | {r.rec_mean:.1f} [{r.rec_lo:.0f}-{r.rec_hi:.0f}] | {r.rec_yds_mean:.0f} [{r.rec_yds_lo:.0f}-{r.rec_yds_hi:.0f}] | {r.rec_td_mean:.2f} | {('%.1f / %.0f' % (r.rush_att_mean, r.rush_yds_mean)) if r.rush_att_mean >= 0.3 else ''} | {pc1(r.any_td)} | {pc1(r.first_td)} | {r.dk_mean:.1f} [{r.dk_lo:.0f}-{r.dk_hi:.0f}] |")
w("\n## Quarterbacks: full lines\n")
for r in QB.itertuples(): out += block(r.key, Dm[Dm.key == r.key].iloc[0], Do.loc[r.key], "QB")
w("## Running backs: rushing, receiving and overall\n")
for r in RB.itertuples(): out += block(r.key, Dm[Dm.key == r.key].iloc[0], Do.loc[r.key], "RB")
w("## Wide receivers and tight ends: receiving (and rushing where projected)\n")
for r in PC.itertuples(): out += block(r.key, Dm[Dm.key == r.key].iloc[0], Do.loc[r.key], "PC")
# rankings
A = Dm.copy(); A["adj"] = A.any_td * A.p_active; A = A[~A.key.isin(["emari demercado"])].sort_values("adj", ascending=False).head(15)
w("## Top 15 Anytime TD (rush or receiving TD; ranked by model probability x availability)\n")
w("| # | Player | Model (if active / x avail.) | Targets / carries | Why (usage, red zone) | Best price | Book vig-in | Book est. no-vig | Gap (diag.) |\n|---|---|---|---|---|---|---|---|---|")
drv = {(k, m): s for k, m, s in zip(TDM.key, TDM.market, TDM.key_drivers)}
for i, r in enumerate(A.itertuples(), 1):
    b = tdbook(Em, r.key, "anytime_td")
    w(f"| {i} | {r.player} ({r.team} {r.pos}) | {pc1(r.any_td)} / {pc1(r.adj)} | {r.tgt_mean:.1f} / {r.rush_att_mean:.1f} | {drv.get((r.key, 'anytime_td'), '')} | {am(b['best']) + ' ' + b['book'] if b else ''} | {pc1(b['vigin']) if b else ''} | {pc1(b['nv']) if b else ''} | {('%+.1f' % (100 * (r.any_td - b['nv']))) if b else ''} |")
F = Dm.copy(); F["adj"] = F.first_td * F.p_active; F = F[~F.key.isin(["emari demercado"])].sort_values("adj", ascending=False).head(5)
w("\n## Top 5 First TD scorer\n")
w("| # | Player | Model (if active / x avail.) | Best price | Book vig-in | Book est. no-vig | Gap (diag.) |\n|---|---|---|---|---|---|---|")
for i, r in enumerate(F.itertuples(), 1):
    b = tdbook(Em, r.key, "first_td")
    w(f"| {i} | {r.player} ({r.team} {r.pos}) | {pc1(r.first_td)} / {pc1(r.adj)} | {am(b['best']) + ' ' + b['book'] if b else ''} | {pc1(b['vigin']) if b else ''} | {pc1(b['nv']) if b else ''} | {('%+.1f' % (100 * (r.first_td - b['nv']))) if b else ''} |")
open(OUTMD, "w").write("\n".join(out) + "\n"); print("written", len(out))
