"""49ers trade-deadline target model (2026 season, as of Week 6).

Pulls live team records, 49ers injuries and candidate production from nflverse
(nflreadpy), then scores each candidate 0-100 for trade fit.

Auto-pulled: team records, candidate sacks/TFL/QB hits/receiving lines, ages.
Analyst inputs (CANDIDATES below): impact grade, availability, projected cost,
contract fit. Sources for those are in the report; they are judgments, not facts.

    fit = .25*need + .35*impact + .15*availability + .15*cost_eff + .10*contract_fit
    (impact < 55 caps fit at 60: a cheap player who doesn't move the needle is not a fit)

Writes timestamped outputs (never overwrites) to docs/trade_deadline/.
"""
from __future__ import annotations

import datetime as dt
import pathlib

import nflreadpy as nfl
import pandas as pd

MODEL_VERSION = "v0.1"
OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "trade_deadline"

# 49ers need by position group, 0-100 (Bosa out/ACL returnee, Height 1 sack; Deebo out,
# Evans ribs; OL starters all healthy; Sigle out / Neal questionable at S).
NEED = {"EDGE": 100, "WR": 85, "S": 55, "DT": 70, "OT": 50, "IOL": 40}

# Projected 2027-pick cost -> value in "points" (Jimmy Johnson-style, R1 ~ 100) and cost_eff score.
PICK_VALUE = {"R1": 100, "R2": 60, "R3": 35, "R4": 20, "R5": 12, "R6": 7, "R7": 4}


def cost_eff(cost: str) -> float:
    pts = sum(PICK_VALUE[p.strip()[:2]] for p in cost.replace("cond.", "").split("+"))
    return max(0.0, 100 - pts * 1.2)


# name, nfl name match, pos group, team, impact, availability, projected cost, contract_fit, note
CANDIDATES = [
    # EDGE
    ("Khalil Mack", "Khalil Mack", "EDGE", 78, 92, "R5", 95, "Age 35, $18M 1-yr; 3 sk/10 pressures; execs value ~R5, LAC asks R4"),
    ("Tuli Tuipulotu", "Tuli Tuipulotu", "EDGE", 82, 75, "R2", 45, "24, PFF 80.9 (12th edge), expiring; best edge on market; extension would cost ~$25M+ vs. tight 2027 cap"),
    ("Jacob Martin", "Jacob Martin", "EDGE", 66, 85, "R6", 90, "TEN, 3.5 sk/8 QB hits, $9M 1-yr rental"),
    ("Za'Darius Smith", "Za'Darius Smith", "EDGE", 62, 70, "R6", 92, "ATL 2-4, age 34, 3.5 sk in 4 g, $6M 1-yr"),
    ("Jermaine Johnson II", "Jermaine Johnson", "EDGE", 64, 80, "R5", 70, "TEN, 3 sk/4 TFL, pending FA"),
    ("Josh Sweat", "Josh Sweat", "EDGE", 60, 45, "R4", 35, "ARI, $19.1M thru 2028, 2 sk; GM said no trade; big 2027 hit"),
    ("Chase Young", "Chase Young", "EDGE", 76, 30, "R3", 50, "NO, 5.5 sk/9 QB hits, $17M thru 2027; Loomis resists selling"),
    ("Danielle Hunter", "Danielle Hunter", "EDGE", 72, 25, "R3", 30, "HOU 2-4, $40M 1-yr, age 32; cap-heavy"),
    ("Yaya Diaby", "Yaya Diaby", "EDGE", 48, 70, "R5", 80, "TB, PFF pass-rush 50.6, 0 sk; run-first, pending FA"),
    ("Josh Uche", "Joshua Uche", "EDGE", 50, 90, "R5", 92, "MIA 0-5, PFF 33rd edge, 4 pressures, expiring"),
    ("Will McDonald IV", "Will McDonald", "EDGE", 55, 70, "R5", 80, "NYJ, 2 sk, 1-yr; buried behind newer edges"),
    ("Zaven Collins", "Zaven Collins", "EDGE", 55, 55, "R5", 60, "ARI, PFF run-D 90.6, little rush"),
    ("Baron Browning", "Baron Browning", "EDGE", 45, 70, "R6", 85, "ARI, expiring $7.5M, 0 sk"),
    ("Cameron Jordan", "Cameron Jordan", "EDGE", 40, 60, "R7", 90, "NO, age 37, minimal role"),
    # DT
    ("DeForest Buckner", "DeForest Buckner", "DT", 84, 55, "R4", 75, "IND 2-4, 4 sk/4 TFL/8 QB hits; age 32.6; $23M APY (you flag contract year; nflverse data not updated)"),
    ("A'Shawn Robinson", "Robinson", "DT", 83, 78, "R5", 92, "TB 1-5, PFF 89.5 overall/88.8 run D, $10M 1-yr"),
    ("Daron Payne", "Payne", "DT", 62, 80, "R5", 70, "WAS, $22.5M expiring, 4 straight sub-63 PFF years"),
    ("Jeffery Simmons", "Simmons", "DT", 85, 25, "R2", 25, "TEN, $35.3M thru 2028; team reluctant"),
    ("Dalvin Tomlinson", "Tomlinson", "DT", 52, 88, "R6", 90, "LAC, $6.5M 1-yr, age 32.7"),
    ("Zach Sieler", "Sieler", "DT", 45, 75, "R6", 60, "MIA, $21M thru 2027, PFF run D 30.0"),
    # WR
    ("Jerry Jeudy", "Jerry Jeudy", "WR", 66, 88, "R4", 85, "CLE, reported available, ask R3-R4; 8 rec, 2025 Pro Bowl level in 2024; 1-yr"),
    ("Brian Thomas Jr.", "Brian Thomas", "WR", 80, 20, "R2+R6", 98, "JAX 4-2, 24, $3.7M thru 2027; JAX 'no interest'"),
    ("Stefon Diggs", "Stefon Diggs", "WR", 62, 70, "R6", 92, "WAS, 18 rec/170 yds/3 TD in 4 g, $8M 1-yr"),
    ("Keenan Allen", "Keenan Allen", "WR", 58, 65, "R7", 95, "IND, age 34.5, $3.3M, 227 yds"),
    ("Terry McLaurin", "McLaurin", "WR", 68, 40, "R3", 35, "WAS, $29M thru 2027, age 31"),
    ("Quentin Johnston", "Quentin Johnston", "WR", 52, 70, "R5", 65, "LAC, 22% drop rate, 0.93 YPRR"),
    ("Chris Godwin", "Godwin", "WR", 50, 55, "R5", 35, "TB, 216 yds, $22M thru 2027"),
    ("Calvin Ridley", "Calvin Ridley", "WR", 48, 80, "R6", 40, "TEN, age 31.8, 0.74 YPRR, $17.6M thru 2027"),
    ("Michael Wilson", "Michael Wilson", "WR", 66, 45, "R4", 70, "ARI, 33 rec/320 yds on 58 tgt; contract unverified"),
    ("Davante Adams", "Davante Adams", "WR", 78, 10, "R3", 40, "LAM 2-4 division rival; 480 yds/4 TD"),
    # OL
    ("Dylan Cook", "Dylan Cook", "OT", 68, 55, "R6", 95, "PIT, PFF 76.4, lost RT job to rookie, ~$1M; swing-tackle insurance for Trent Williams"),
    ("Cesar Ruiz", "Cesar Ruiz", "IOL", 55, 45, "R6", 82, "NO RG, $11M expiring, rookie behind him"),
    ("Austin Jackson", "Austin Jackson", "OT", 45, 80, "R7", 88, "MIA RT, $7M expiring, struggling"),
    ("Landon Dickerson", "Landon Dickerson", "IOL", 85, 40, "R2", 40, "PHI LG, IR (knee), $21M thru 2027; not usable now"),
    # S (bonus)
    ("Budda Baker", "Budda Baker", "S", 76, 60, "R4", 75, "ARI, age 30.8, 3.5 sk/4 TFL, $18M thru 2026"),
    ("Derwin James", "Derwin James", "S", 82, 30, "R2", 25, "LAC, $25.2M thru 2028"),
]


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    sched = nfl.load_schedules([2026]).to_pandas().dropna(subset=["home_score"])
    rec: dict[str, list[float]] = {}
    for _, r in sched.iterrows():
        for t, p, o in ((r.home_team, r.home_score, r.away_score), (r.away_team, r.away_score, r.home_score)):
            d = rec.setdefault(t, [0, 0, 0])
            d[0 if p > o else 1 if p < o else 2] += 1
    ps = nfl.load_player_stats([2026]).to_pandas()
    ps = ps[ps.week <= 6]
    ros = nfl.load_rosters([2026]).to_pandas().drop_duplicates("full_name")
    ros["age"] = (pd.Timestamp("2026-10-19") - pd.to_datetime(ros.birth_date)).dt.days / 365.25

    rows = []
    for name, key, pos, impact, avail, cost, cfit, note in CANDIDATES:
        m = ros[ros.full_name.str.contains(key, case=False, regex=False)]
        m = m[m.full_name.str.contains(name.split()[0][:4], case=False)] if len(m) > 1 else m
        team = m.team.iloc[0] if len(m) else ""
        age = round(m.age.iloc[0], 1) if len(m) else None
        w, l, t = rec.get(team, [0, 0, 0])
        s = ps[ps.player_display_name.str.contains(key, case=False, regex=False) & (ps.team == team)]
        line = (f"{int(s.receptions.sum())} rec/{int(s.receiving_yards.sum())} yds/{int(s.receiving_tds.sum())} TD"
                if pos == "WR" else f"{s.def_sacks.sum():g} sk/{int(s.def_tackles_for_loss.sum())} TFL/{int(s.def_qb_hits.sum())} QBH")
        ce = cost_eff(cost)
        fit = 0.25 * NEED[pos] + 0.35 * impact + 0.15 * avail + 0.15 * ce + 0.10 * cfit
        if impact < 55:
            fit = min(fit, 60)
        rows.append(dict(player=name, team=team, pos=pos, age=age, team_record=f"{w}-{l}" + (f"-{t}" if t else ""),
                         stats_wk1_6=line, need=NEED[pos], impact=impact, availability=avail, cost_eff=round(ce),
                         contract_fit=cfit, projected_cost_2027=cost, fit_score=round(fit), note=note))
    df = pd.DataFrame(rows).sort_values("fit_score", ascending=False)
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%MZ")
    path = OUT / f"niners_deadline_targets_{MODEL_VERSION}_{stamp}.csv"
    df.to_csv(path, index=False)
    pd.set_option("display.width", 250, "display.max_colwidth", 60, "display.max_rows", 200)
    print(df.drop(columns=["note"]).to_string(index=False))
    print(f"\nas_of={now.isoformat()} model={MODEL_VERSION} -> {path}")


if __name__ == "__main__":
    main()
