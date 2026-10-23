"""Archive an independent consensus benchmark each window: Sleeper's weekly player projections (Rotowire feed) and Sleeper/ESPN-style injury status, with as-of timestamps.

Why: the engine is graded against a naive per-game average and the DraftKings lines only; there is no independent projection to measure it against, and no free source of PAST pre-game projections
(Sleeper's archive keeps only a few hundred players for earlier weeks). So the benchmark is built prospectively: every window appends one CSV, `bench_grade.py` compares the frozen run, the benchmark and
the naive average against the box score.
Usage: python bench_fetch.py SEASON WEEK [--out runs/weekly/_benchmarks]
Writes <out>/sleeper_proj_{season}_w{week}_{YYYYMMDDTHHMMZ}.csv and sleeper_inj_{...}.csv. Small CSVs, no odds, safe to commit.
"""
import argparse
import datetime as dt
import os
import sys

import httpx
import pandas as pd

from paths import RUNS

STATS = ["rec", "rec_yd", "rec_td", "rec_tgt", "rush_att", "rush_yd", "rush_td", "pass_att", "pass_cmp", "pass_yd", "pass_td", "pass_int", "pts_ppr"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("season", type=int); ap.add_argument("week", type=int); ap.add_argument("--out", default=os.path.join(RUNS, "_benchmarks"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc); tag = now.strftime("%Y%m%dT%H%MZ")
    pl = httpx.get("https://api.sleeper.app/v1/players/nfl", timeout=120).json()
    pr = httpx.get(f"https://api.sleeper.app/projections/nfl/{a.season}/{a.week}?season_type=regular&position[]=QB&position[]=RB&position[]=WR&position[]=TE", timeout=120).json()
    rows = []
    for x in pr:
        s = x["stats"]
        if s.get("pts_ppr") is None:
            continue
        p = pl.get(x["player_id"], {})
        rows.append(dict(as_of_utc=now.isoformat(timespec="seconds"), sleeper_id=x["player_id"], gsis_id=(p.get("gsis_id") or "").strip(), name=f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                         pos=p.get("position"), team=x.get("team"), opp=x.get("opponent"), last_modified_utc=dt.datetime.fromtimestamp(x["last_modified"] / 1000, dt.timezone.utc).isoformat(timespec="seconds"),
                         **{k: s.get(k, 0) for k in STATS}))
    P = pd.DataFrame(rows); P.to_csv(os.path.join(a.out, f"sleeper_proj_{a.season}_w{a.week:02d}_{tag}.csv"), index=False)
    I = pd.DataFrame([dict(as_of_utc=now.isoformat(timespec="seconds"), sleeper_id=k, gsis_id=(v.get("gsis_id") or "").strip(), name=v.get("full_name") or f"{v.get('first_name', '')} {v.get('last_name', '')}",
                           pos=v.get("position"), team=v.get("team"), injury_status=v.get("injury_status"), injury_body_part=v.get("injury_body_part"), practice=v.get("practice_participation"),
                           news_updated_utc=(dt.datetime.fromtimestamp(v["news_updated"] / 1000, dt.timezone.utc).isoformat(timespec="seconds") if v.get("news_updated") else None))
                      for k, v in pl.items() if v.get("team") and v.get("position") in ("QB", "RB", "WR", "TE") and v.get("active")])
    I.to_csv(os.path.join(a.out, f"sleeper_inj_{a.season}_w{a.week:02d}_{tag}.csv"), index=False)
    print(f"{len(P)} projected players, {len(I)} active skill players with status -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
