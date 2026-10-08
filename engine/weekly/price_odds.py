"""Week-5+ book lines: convert an Odds-API style workbook (Sheet1: game_id, commence_time, bookmaker, last_update, home_team, away_team, market, label,
description, price, point; timestamps US Pacific) to props_lines.csv, then price it against the simulated joint distribution.
Usage: APEX_ODDS_XLSX=<file> APEX_ENV=<track> python price_odds.py   (OUT/APEX_OUT must hold the finished run)
Outputs in OUT: props_lines.csv, props_lines_rejected.csv, edges_all_rows.csv, odds_game_lines.csv, odds_unmatched_names.csv
Lines never enter the projection stages; this reads finished sims only. One-sided prices are de-vigged with a flat 10% haircut and labeled Estimated."""
import os, datetime as dt
import numpy as np, pandas as pd
from paths import OUT as O
import run_all as R
from params import SCHED, norm_name, is_neutral, TARGET_WEEK
from load import FULL2ABBR

TZ_OFFSET_H = 7        # sheet timestamps are US Pacific (PDT): TNF commence 17:15 == 8:15 PM ET kickoff
MK = {"player_receptions": "rec", "player_pass_completions": "pass_cmp", "player_pass_attempts": "pass_att", "player_rush_attempts": "rush_att", "player_1st_td": "first_td",
      "player_anytime_td": "anytime_td", "player_pass_yds": "pass_yds", "player_reception_yds": "rec_yds", "player_rush_yds": "rush_yds"}
ONE_SIDED = ("first_td", "anytime_td")
SD = {"Over": "over", "Under": "under", "Yes": "yes"}
NAME_ALIAS = {"zonovan knight": "bam knight", "drew ogletree": "andrew ogletree"}      # book name -> nflverse name (verified to exist in the Week 5 sim)
STALE_H = 6
imp = lambda a: np.where(np.asarray(a, float) < 0, -np.asarray(a, float) / (-np.asarray(a, float) + 100), 100 / (np.asarray(a, float) + 100))
payout = lambda a: np.where(np.asarray(a, float) < 0, 100 / (-np.asarray(a, float)), np.asarray(a, float) / 100)

raw = pd.concat([pd.read_excel(f).assign(src_file=os.path.basename(f)) for f in os.environ["APEX_ODDS_XLSX"].split(os.pathsep)], ignore_index=True)      # several workbooks: os.pathsep-separated
raw["as_of_utc"] = raw.last_update + pd.Timedelta(hours=TZ_OFFSET_H)
raw["commence_utc"] = raw.commence_time + pd.Timedelta(hours=TZ_OFFSET_H)
raw["home"] = raw.home_team.map(FULL2ABBR); raw["away"] = raw.away_team.map(FULL2ABBR)
sched = {(r.away, r.home): r for r in SCHED.itertuples()}
raw["et_date"] = (raw.commence_utc - pd.Timedelta(hours=4)).dt.strftime("%Y-%m-%d")      # US Eastern date of kickoff (EDT)
raw["in_week"] = [((a, h) in sched) and (sched[(a, h)].date == d) for a, h, d in zip(raw.away, raw.home, raw.et_date)]
rej_wk = raw[~raw.in_week]
p = raw[raw.in_week].copy()
p["game"] = p.away + "@" + p.home
NOW = pd.Timestamp(dt.datetime.now(dt.timezone.utc)).tz_localize(None)
p["played_or_started"] = p.commence_utc <= NOW
# game lines (h2h/spreads/totals) for the model-vs-book table
gl = p[p.market.isin(["h2h", "spreads", "totals"])]
gl.to_csv(O + "odds_game_lines.csv", index=False)
pp = p[p.market.isin(MK)].copy()
pp["market_v2"] = pp.market.map(MK); pp["side"] = pp.label.map(SD); pp["nkey"] = pp.description.map(norm_name).replace(NAME_ALIAS)
pp = pp[~pp.played_or_started]
# books are not independent: collapse books whose price sheet for a market is identical (e.g. Hard Rock state variants; several first-TD feeds)
feed_of = {}
for mk_, g_ in pp.groupby("market_v2"):
    sig = {b: hash(tuple(sorted(zip(x.game, x.nkey, x.label, x.point.fillna(-1), x.price)))) for b, x in g_.groupby("bookmaker")}
    first = {}
    for b in sorted(sig): first.setdefault(sig[b], b)
    for b in sig: feed_of[(mk_, b)] = first[sig[b]]
pp["feed"] = [feed_of[(m_, b)] for m_, b in zip(pp.market_v2, pp.bookmaker)]
n_books = pp.bookmaker.nunique(); n_feeds = pp.groupby("market_v2").feed.nunique().to_dict()
pp = pp[pp.feed == pp.bookmaker].copy()      # one row set per independent feed

R_ = {}
rows, rejected = [], []
for g in SCHED.itertuples():
    a, h = g.away, g.home
    R.run_game(a, h, neutral=is_neutral(a, h))
    d = R.STORE.pop((a, h)); R_[(a, h)] = d
unmatched = []
alias_log = []
out = []
for (a, h), d in R_.items():
    Ttot = np.maximum(d["A"]["td"] + d["H"]["td"] + d["A"]["dtd"] + d["H"]["dtd"], 1)
    pls = {}
    for t in (a, h):
        for pl in d["players"][t]: pls[norm_name(pl["player"])] = (t, pl)
    sub = pp[(pp.away == a) & (pp.home == h)]
    for (nk, mk), grp in sub.groupby(["nkey", "market_v2"]):
        hit = pls.get(nk)
        if hit is None:      # alias fallback: same team, same last name and first initial, exactly one candidate (Josh/Joshua Palmer, Bam/Zonovan Knight, Drew/Andrew Ogletree)
            last = nk.split()[-1] if nk.split() else ""
            cand = [v for k_, v in pls.items() if k_.split() and k_.split()[-1] == last and k_[:1] == nk[:1]]
            if len(cand) == 1: hit = cand[0]; alias_log.append(dict(game=f"{a}@{h}", book_name=grp.description.iloc[0], sim_name=hit[1]["player"]))
        if hit is None:
            unmatched.append(dict(game=f"{a}@{h}", player=grp.description.iloc[0], market=mk, rows=len(grp), reason="no projected player with this name in either team")); continue
        team, pl = hit
        m = pl["mask"]
        if pl["p_active"] < 0.03 or m.sum() < 200:
            unmatched.append(dict(game=f"{a}@{h}", player=grp.description.iloc[0], market=mk, rows=len(grp), reason=f"p_active {pl['p_active']:.2f} (projected out/inactive)")); continue
        opp = h if team == a else a
        if mk in ONE_SIDED:
            tdc = pl["rush_td"] + pl["rec_td"]      # passing TDs do not count for anytime/first TD
            pm = float((tdc[m] / Ttot[m]).mean()) if mk == "first_td" else float((tdc[m] >= 1).mean())
            for r in grp.itertuples():
                nv = float(imp(r.price)) * 0.90
                out.append(dict(game=f"{a}@{h}", player=r.description, team=team, opp=opp, market=mk, side="yes", line=np.nan, book=r.bookmaker, odds=r.price, model_p=pm, novig_p=nv,
                                novig_method="Estimated (10% flat haircut, one-sided)", p_active=pl["p_active"], as_of=r.as_of_utc))
            continue
        x = pl[mk][m]
        for line, lg in grp.groupby("point"):
            po = float((x > line).mean()); pu = float((x < line).mean()); den = max(po + pu, 1e-9)
            both = {}
            for b, bg in lg.groupby("bookmaker"):
                o = bg[bg.side == "over"]; u = bg[bg.side == "under"]
                if len(o) and len(u):
                    io, iu = float(imp(o.price.iloc[0])), float(imp(u.price.iloc[0])); both[b] = io / (io + iu)
            cons = float(np.mean(list(both.values()))) if both else np.nan
            for r in lg.itertuples():
                pm = po / den if r.side == "over" else pu / den
                if r.bookmaker in both: nv = both[r.bookmaker] if r.side == "over" else 1 - both[r.bookmaker]; meth = "two-way no-vig (same book)"
                elif both: nv = cons if r.side == "over" else 1 - cons; meth = "two-way no-vig (other-book consensus)"
                else: nv = float(imp(r.price)) * 0.90; meth = "Estimated (10% flat haircut, one-sided)"
                out.append(dict(game=f"{a}@{h}", player=r.description, team=team, opp=opp, market=mk, side=r.side, line=line, book=r.bookmaker, odds=r.price, model_p=pm, novig_p=nv,
                                novig_method=meth, p_active=pl["p_active"], as_of=r.as_of_utc,
                                ev=(po if r.side == "over" else pu) * float(payout(r.price)) - (pu if r.side == "over" else po)))
E = pd.DataFrame(out, columns=["game", "player", "team", "opp", "market", "side", "line", "book", "odds", "model_p", "novig_p", "novig_method", "p_active", "as_of", "ev"])
E["as_of"] = pd.to_datetime(E.as_of)
E["imp_vig_in"] = imp(E.odds) if len(E) else []
ft = E.market == "first_td"      # only first TD forms a (near) complete field that can be normalized
tot = E[ft].groupby(["game", "book"]).imp_vig_in.transform("sum")
E["novig_p_ceiling"] = np.nan
E.loc[ft, "novig_p_ceiling"] = E.loc[ft, "imp_vig_in"] / tot      # listed field forced to sum to 1: an UPPER bound (unlisted players also take probability)
E["edge"] = E.model_p - E.novig_p
E["ev"] = E.ev.where(E.ev.notna(), E.model_p * payout(E.odds) - (1 - E.model_p))
E["age_h"] = (NOW - E.as_of).dt.total_seconds() / 3600; E["stale"] = E.age_h > STALE_H
n_stale = int(E.stale.sum()); E = E[~E.stale].copy()      # stale lines are excluded, not just flagged
E["is_main_line"] = False
for k_, g_ in (E[~E.market.isin(ONE_SIDED)].groupby(["game", "player", "market"]) if len(E) else []): E.loc[g_.index[g_.line == g_.line.mode().iloc[0]], "is_main_line"] = True
E["model_gt_85_suppress"] = (E.model_p > 0.85) | (E.model_p < 0.15)
E["model_gap_flag"] = E.edge.abs() > 0.15
bias = E[E.side.isin(["over", "yes"])].groupby("market").edge.median() if len(E) else pd.Series(dtype=float)
E["bias_offset"] = E.market.map(bias)
E["edge_bias_centered"] = np.where(E.side.isin(["over", "yes"]), E.edge - E.bias_offset, E.edge + E.bias_offset)
# names say what they are: model minus book, diagnostic only. No row here is an edge or a pick (postmortem P0 #2); never rank by these.
E = E.rename(columns={"edge": "gap_model_minus_novig", "ev": "ev_if_model_right_DIAGNOSTIC", "edge_bias_centered": "gap_bias_centered_DIAGNOSTIC", "bias_offset": "market_median_gap_DIAGNOSTIC"})
E.to_csv(O + "edges_all_rows.csv", index=False)
pd.DataFrame(unmatched).to_csv(O + "odds_unmatched_names.csv", index=False)
pd.DataFrame(alias_log).drop_duplicates().to_csv(O + "odds_name_aliases.csv", index=False)
pd.DataFrame([dict(pricing_now_utc=NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), snapshot_min=str(E.as_of.min()), snapshot_max=str(E.as_of.max()), book_names=n_books, independent_feeds_by_market=str(n_feeds),
                   stale_rows_excluded=n_stale, odds_rows=len(raw), rows_in_week=len(p), rows_not_week=len(rej_wk), tz_offset_h=TZ_OFFSET_H)]).to_csv(O + "odds_meta.csv", index=False)
# players the model projects with a real role but NO book lists any prop for (book-vs-report conflict candidates)
listed = set(p.loc[p.market.isin(MK), "description"].map(norm_name))
nb = []
for (a_, h_), d_ in R_.items():
    for t_ in (a_, h_):
        for pl in d_["players"][t_]:
            m_ = pl["mask"]
            if pl["p_active"] < 0.5 or m_.sum() < 200 or norm_name(pl["player"]) in listed: continue
            role = max(float(pl["rush_att"][m_].mean()) / 8.0, float(pl["rec"][m_].mean()) / 2.5, float(pl["pass_att"][m_].mean()) / 15.0)
            if role >= 1: nb.append(dict(game=f"{a_}@{h_}", player=pl["player"], team=t_, p_active=pl["p_active"], rush_att=float(pl["rush_att"][m_].mean()), rec=float(pl["rec"][m_].mean()), pass_att=float(pl["pass_att"][m_].mean())))
pd.DataFrame(nb).to_csv(O + "odds_no_book_lines.csv", index=False)
cols = ["bookmaker", "game", "description", "market_v2", "side", "point", "price", "as_of_utc"]
pp[cols].rename(columns={"bookmaker": "book", "description": "player", "market_v2": "market", "point": "line", "price": "odds_american"}).to_csv(O + "props_lines.csv", index=False)
rej_wk.assign(reject="not a Week %d game on the schedule" % TARGET_WEEK)[["game_id", "bookmaker", "away_team", "home_team", "market", "commence_utc", "reject"]].to_csv(O + "props_lines_rejected.csv", index=False)
print(f"odds rows {len(raw)}, in week {len(p)}, not week {len(rej_wk)}, player-market rows priced {len(E)}, unmatched player-markets {len(unmatched)}")
print("book names", n_books, "independent feeds by market", n_feeds, "| stale excluded", n_stale, "| aliases", len(alias_log), "| no-book-line players", len(nb))
print("snapshot as_of range", E.as_of.min() if len(E) else None, E.as_of.max() if len(E) else None, "| max age h", round(E.age_h.max(), 2) if len(E) else None, "| stale excluded", n_stale)
print("market bias offsets", bias.round(3).to_dict())
