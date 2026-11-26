"""Market-anchored player projections (DECISIONS #90 design, #91 test). Off unless APEX_ANCHOR_XLSX is set; when off nothing here runs (byte-identical).

APEX_ANCHOR_XLSX = one of
  * a prepared anchor-lines CSV: season, week, away, home, nkey, market, line, p   (market in rec_yds, rush_yds, pass_yds, anytime_td; p = de-vigged
    P(over the line) for yardage, P(at least one TD) for anytime_td; rows filtered to the current SEASON / TARGET_WEEK and game)
  * an operator / Odds API workbook in the price_odds.py schema (bookmaker, home_team, away_team, market, label, description, price, point):
    main line = most books, ties to the line priced nearest even; two-way de-vig per book, mean over books; anytime TD de-vigged with
    config/weekly/td_book_devig.json.
APEX_ANCHOR_W (default 0): engine weight; the shift applied is (1 - w) of the full shift to the market (held-out optimum 0-0.1, #90).

Applied after the joint simulation of one game, on the active draws (mask) of each player:
  1. yardage (rec_yds, rush_yds, pass_yds): draws above 0 are shifted by s, floored at 0, s solved so P(X > line | active) = p (0-yard draws stay 0,
     so a game without a catch stays without yards); the shape and the within-game correlation stay the engine's.
  2. anytime TD: TD draws are thinned (P_engine > p) or a TD is added to 0-TD draws (P_engine < p) until P(TD >= 1 | active) = p; the added TD goes to
     receiving or rushing in proportion to the player's simulated TD split. A separate seeded RNG is used, so other games are untouched.
  3. lineless teammates: receiving yards of unanchored receivers are rescaled so the team's receiving yards match the anchored QB's passing yards
     (when the QB is anchored); rushing yards of unanchored rushers are rescaled to keep the team's simulated rushing total. Factor clipped to [0.5, 1.5].
  4. fantasy points (fp) are recomputed from the deltas; raw arrays are kept in pl["raw"], anchored markets in pl["anchored"].
Team-level arrays (scores, team totals) are not changed.
"""
import json
import os
import re
import zlib

import numpy as np
import pandas as pd

MARKETS = ("rec_yds", "rush_yds", "pass_yds")
_OA = {"player_reception_yds": "rec_yds", "player_rush_yds": "rush_yds", "player_pass_yds": "pass_yds", "player_anytime_td": "anytime_td"}
NICK = {"Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL", "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
        "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL", "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
        "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX", "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC",
        "Los Angeles Rams": "LA", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN", "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
        "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT", "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
        "Tennessee Titans": "TEN", "Washington Commanders": "WAS"}
_CACHE = {}


def norm_name(s):
    s = str(s).replace("*", "").replace("+", "").strip()
    s = re.sub(r"\s*\([A-Z]{2,3}\)\s*$", "", s)
    s = re.sub(r"[.’']", "", s).lower()
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _imp(a):
    a = np.asarray(a, float)
    with np.errstate(divide="ignore", invalid="ignore"): return np.where(a < 0, -a / (100 - a), 100 / (100 + a))


def _from_workbook(path):
    return lines_from_rows(pd.concat([sh for f in path.split(os.pathsep) for sh in pd.read_excel(f, sheet_name=None).values()], ignore_index=True))


def lines_from_rows(raw):
    """price_odds-schema rows (bookmaker, home_team, away_team, market, label, description, price, point) -> anchor lines (away, home, nkey, market, line, p)."""
    raw = raw[raw.market.isin(_OA)].copy(); raw["mk"] = raw.market.map(_OA); raw["nkey"] = raw.description.map(norm_name)
    raw["away"] = raw.away_team.map(lambda x: NICK.get(x, x)); raw["home"] = raw.home_team.map(lambda x: NICK.get(x, x)); raw["imp"] = _imp(raw.price)
    raw["side"] = raw.label.astype(str).str.lower()
    dv = {}
    cf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config", "weekly", "td_book_devig.json")
    if os.path.exists(cf): dv = json.load(open(cf))
    def k_of(b):
        b = str(b).lower().replace(" ", "").replace("caesars", "williamhill_us")
        for kk, v in dv.get("books", {}).items():
            if kk.replace("_", "") == b.replace("_", "").replace(".ag", "ag"): return float(v)
        return float(dv.get("pooled", 0.9))
    out = []
    td = raw[(raw.mk == "anytime_td") & (raw.side == "yes")]
    for (a, h, n), g in td.groupby(["away", "home", "nkey"]):
        out.append(dict(away=a, home=h, nkey=n, market="anytime_td", line=np.nan, p=float(np.mean([min(k_of(b) * i, .99) for b, i in zip(g.bookmaker, g.imp)]))))
    yd = raw[raw.mk.isin(MARKETS) & raw.point.notna()]
    for (a, h, n, mk), g in yd.groupby(["away", "home", "nkey", "mk"]):
        best = None
        for pt, gl in g.groupby("point"):
            ps = []
            for b, gb in gl.groupby("bookmaker"):
                o, u = gb[gb.side == "over"], gb[gb.side == "under"]
                if len(o) and len(u): io, iu = float(_imp(o.price.iloc[0])), float(_imp(u.price.iloc[0])); ps.append(io / (io + iu))
            if ps:
                cand = (len(ps), -abs(np.mean(ps) - .5), pt, float(np.mean(ps)))
                if best is None or cand[:2] > best[:2]: best = cand
        if best: out.append(dict(away=a, home=h, nkey=n, market=mk, line=best[2], p=best[3]))
    return pd.DataFrame(out)


def lines_for(away, home):
    path = os.environ.get("APEX_ANCHOR_XLSX", "")
    if not path: return None
    if path not in _CACHE:
        if path.endswith(".csv"):
            L = pd.read_csv(path)
            S, W = os.environ.get("APEX_SEASON"), os.environ.get("APEX_TARGET_WEEK")
            if "season" in L and S: L = L[L.season == int(S)]
            if "week" in L and W: L = L[L.week == int(W)]
        else:
            L = _from_workbook(path)
        _CACHE[path] = {k: g for k, g in L.groupby(["away", "home"])}
    return _CACHE[path].get((away, home))


def _solve_shift(x, line, p):
    """s such that P(x' > line) = p over the given draws, x' = x + s on draws x > 0 (floored at 0), 0 draws stay 0."""
    pos = x > 0
    if pos.mean() < 1e-9: return 0.0
    if p >= pos.mean() - 1e-9:      # the market wants more over-probability than the share of draws with yards: push every positive draw over
        return float(line - x[pos].min() + 1e-6)
    lo, hi = -float(x.max()) - abs(line) - 1, float(abs(line)) + float(x.max()) + 1
    for _ in range(60):
        mid = .5 * (lo + hi); xp = np.where(pos, np.maximum(x + mid, 0), 0)
        if (xp > line).mean() < p: lo = mid
        else: hi = mid
    return .5 * (lo + hi)


def apply(players, away, home):
    """mutates the player dicts of one simulated game; returns the number of anchored player-markets."""
    L = lines_for(away, home)
    if L is None or not len(L): return 0
    w = float(os.environ.get("APEX_ANCHOR_W", 0) or 0)
    rng = np.random.default_rng(zlib.crc32(f"{os.environ.get('APEX_SEASON')}{os.environ.get('APEX_TARGET_WEEK')}{away}{home}".encode()))
    by = {(r.nkey, r.market): r for r in L.itertuples()}
    n_anch = 0
    for t, pls in players.items():
        team_rec0 = sum(float(pl["rec_yds"][pl["mask"]].mean()) * pl["p_active"] for pl in pls if pl["mask"].sum() > 0)
        team_rush0 = sum(float(pl["rush_yds"][pl["mask"]].mean()) * pl["p_active"] for pl in pls if pl["mask"].sum() > 0)
        for pl in pls:
            m = pl["mask"]
            if m.sum() < 50: continue
            nk = norm_name(pl["player"]); pl.setdefault("anchored", set()); pl.setdefault("raw", {})
            d_yds, d_rec_td, d_rush_td, d_pass = 0, 0, 0, 0
            for mk in MARKETS:
                r = by.get((nk, mk))
                if r is None or not np.isfinite(r.p): continue
                x = pl[mk][m].astype(float)
                if x.max() <= 0: continue
                s = (1 - w) * _solve_shift(x, float(r.line), float(r.p))
                new = pl[mk].astype(float).copy(); sel = m & (pl[mk] > 0); new[sel] = np.maximum(pl[mk][sel] + s, 0)
                pl["raw"][mk] = pl[mk]; delta = new - pl[mk]; pl[mk] = new; pl["anchored"].add(mk); n_anch += 1
                if mk == "pass_yds": d_pass = delta
                else: d_yds = d_yds + delta
            r = by.get((nk, "anytime_td"))
            if r is not None and np.isfinite(r.p):
                tdc = pl["rush_td"] + pl["rec_td"]; pe = float((tdc[m] >= 1).mean()); pt = pe + (1 - w) * (float(r.p) - pe)
                rt, ct = pl["rec_td"].astype(float).copy(), pl["rush_td"].astype(float).copy()
                if pe > pt and pe > 0:
                    drop = m & (tdc >= 1) & (rng.random(len(tdc)) < (pe - pt) / pe); rt[drop] = 0; ct[drop] = 0
                elif pt > pe and pe < 1:
                    add = m & (tdc == 0) & (rng.random(len(tdc)) < (pt - pe) / (1 - pe))
                    sr, sc = float(pl["rec_td"][m].sum()), float(pl["rush_td"][m].sum())
                    to_rec = rng.random(len(tdc)) < (sr / (sr + sc) if sr + sc > 0 else (1.0 if pl["rec_yds"][m].mean() >= pl["rush_yds"][m].mean() else 0.0))
                    rt[add & to_rec] += 1; ct[add & ~to_rec] += 1
                pl["raw"]["rec_td"], pl["raw"]["rush_td"] = pl["rec_td"], pl["rush_td"]
                d_rec_td, d_rush_td = rt - pl["rec_td"], ct - pl["rush_td"]; pl["rec_td"], pl["rush_td"] = rt, ct; pl["anchored"].add("anytime_td"); n_anch += 1
            if pl["anchored"]:
                pl["raw"].setdefault("fp", pl["fp"])
                pl["fp"] = pl["fp"] + 0.1 * d_yds + 0.04 * d_pass + 6 * (d_rec_td + d_rush_td)
        # 3. lineless teammates
        qb = [pl for pl in pls if pl["pos"] == "QB" and "pass_yds" in pl.get("anchored", ()) and pl["mask"].sum() >= 50]
        for mk, target in (("rec_yds", (float(qb[0]["pass_yds"][qb[0]["mask"]].mean()) * qb[0]["p_active"] / max(float(qb[0]["raw"]["pass_yds"][qb[0]["mask"]].mean()) * qb[0]["p_active"], 1e-9)) * team_rec0 if qb else team_rec0),
                           ("rush_yds", team_rush0)):
            free = [pl for pl in pls if mk not in pl.get("anchored", ()) and pl["mask"].sum() > 0 and pl["pos"] != "QB" and float(pl[mk][pl["mask"]].mean()) > 0]
            fixed = sum(float(pl[mk][pl["mask"]].mean()) * pl["p_active"] for pl in pls if pl["mask"].sum() > 0 and not any(pl is q for q in free))   # anchored + unanchored QB
            fsum = sum(float(pl[mk][pl["mask"]].mean()) * pl["p_active"] for pl in free)
            if fsum <= 0: continue
            f = float(np.clip((target - fixed) / fsum, .5, 1.5))
            if abs(f - 1) < 1e-9: continue
            for pl in free:
                pl.setdefault("raw", {}); pl.setdefault("anchored", set()); pl["raw"].setdefault(mk, pl[mk]); pl["raw"].setdefault("fp", pl["fp"])
                new = pl[mk].astype(float) * f; pl["fp"] = pl["fp"] + 0.1 * (new - pl[mk]); pl[mk] = new; pl["anchored"].add(mk + "_team")
    return n_anch
