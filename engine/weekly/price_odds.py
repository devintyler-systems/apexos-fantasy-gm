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
MK = {"player_receptions": "rec", "player_pass_completions": "pass_cmp", "player_pass_attempts": "pass_att", "player_rush_attempts": "rush_att", "player_1st_td": "first_td"}
SD = {"Over": "over", "Under": "under", "Yes": "yes"}
STALE_H = 6
imp = lambda a: np.where(np.asarray(a, float) < 0, -np.asarray(a, float) / (-np.asarray(a, float) + 100), 100 / (np.asarray(a, float) + 100))
payout = lambda a: np.where(np.asarray(a, float) < 0, 100 / (-np.asarray(a, float)), np.asarray(a, float) / 100)

raw = pd.read_excel(os.environ["APEX_ODDS_XLSX"])
raw["as_of_utc"] = raw.last_update + pd.Timedelta(hours=TZ_OFFSET_H)
raw["commence_utc"] = raw.commence_time + pd.Timedelta(hours=TZ_OFFSET_H)
raw["home"] = raw.home_team.map(FULL2ABBR); raw["away"] = raw.away_team.map(FULL2ABBR)
sched = {(r.away, r.home): r for r in SCHED.itertuples()}
raw["in_week"] = [(a, h) in sched for a, h in zip(raw.away, raw.home)]
rej_wk = raw[~raw.in_week]
p = raw[raw.in_week].copy()
p["game"] = p.away + "@" + p.home
NOW = pd.Timestamp(dt.datetime.now(dt.timezone.utc)).tz_localize(None)
p["played_or_started"] = p.commence_utc <= NOW
# game lines (h2h/spreads/totals) for the model-vs-book table
gl = p[p.market.isin(["h2h", "spreads", "totals"])]
gl.to_csv(O + "odds_game_lines.csv", index=False)
pp = p[p.market.isin(MK)].copy()
pp["market_v2"] = pp.market.map(MK); pp["side"] = pp.label.map(SD); pp["nkey"] = pp.description.map(norm_name)
pp = pp[~pp.played_or_started]

R_ = {}
rows, rejected = [], []
for g in SCHED.itertuples():
    a, h = g.away, g.home
    R.run_game(a, h, neutral=is_neutral(a, h))
    d = R.STORE.pop((a, h)); R_[(a, h)] = d
unmatched = []
out = []
for (a, h), d in R_.items():
    Ttot = np.maximum(d["A"]["td"] + d["H"]["td"] + d["A"]["dtd"] + d["H"]["dtd"], 1)
    pls = {}
    for t in (a, h):
        for pl in d["players"][t]: pls[norm_name(pl["player"])] = (t, pl)
    sub = pp[(pp.away == a) & (pp.home == h)]
    for (nk, mk), grp in sub.groupby(["nkey", "market_v2"]):
        hit = pls.get(nk)
        if hit is None:
            unmatched.append(dict(game=f"{a}@{h}", player=grp.description.iloc[0], market=mk, rows=len(grp), reason="no projected player with this name in either team")); continue
        team, pl = hit
        m = pl["mask"]
        if pl["p_active"] < 0.03 or m.sum() < 200:
            unmatched.append(dict(game=f"{a}@{h}", player=grp.description.iloc[0], market=mk, rows=len(grp), reason=f"p_active {pl['p_active']:.2f} (projected out/inactive)")); continue
        opp = h if team == a else a
        if mk == "first_td":
            tdc = pl["rush_td"] + pl["rec_td"]; pm = float((tdc[m] / Ttot[m]).mean())
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
E = pd.DataFrame(out)
E["edge"] = E.model_p - E.novig_p
E["ev"] = E.ev.where(E.ev.notna(), E.model_p * payout(E.odds) - (1 - E.model_p))
E["age_h"] = (NOW - E.as_of).dt.total_seconds() / 3600; E["stale"] = E.age_h > STALE_H
E["model_gap_flag"] = E.edge.abs() > 0.15
bias = E[E.side.isin(["over", "yes"])].groupby("market").edge.median()
E["bias_offset"] = E.market.map(bias)
E["edge_bias_centered"] = np.where(E.side.isin(["over", "yes"]), E.edge - E.bias_offset, E.edge + E.bias_offset)
E.to_csv(O + "edges_all_rows.csv", index=False)
pd.DataFrame(unmatched).to_csv(O + "odds_unmatched_names.csv", index=False)
cols = ["bookmaker", "game", "description", "market_v2", "side", "point", "price", "as_of_utc"]
pp[cols].rename(columns={"bookmaker": "book", "description": "player", "market_v2": "market", "point": "line", "price": "odds_american"}).to_csv(O + "props_lines.csv", index=False)
rej_wk.assign(reject="not a Week %d game on the schedule" % TARGET_WEEK)[["game_id", "bookmaker", "away_team", "home_team", "market", "commence_utc", "reject"]].to_csv(O + "props_lines_rejected.csv", index=False)
print(f"odds rows {len(raw)}, in week {len(p)}, not week {len(rej_wk)}, player-market rows priced {len(E)}, unmatched player-markets {len(unmatched)}")
print("snapshot as_of range", E.as_of.min(), E.as_of.max(), "| max age h", round(E.age_h.max(), 2), "| stale rows", int(E.stale.sum()))
print("market bias offsets", bias.round(3).to_dict())
