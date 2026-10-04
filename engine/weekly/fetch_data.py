"""Download nflverse parquet files into the local cache (APEX_NFLV). Idempotent; never committed.

Closed seasons are fetched once. The current season and the mutable single files are refreshed each call.
"""
import os
import sys
import httpx

from paths import NFLV

BASE = "https://github.com/nflverse/nflverse-data/releases/download"
# (release tag, local/remote file stem). Local name == remote name.
PER_SEASON = [
    ("stats_player", "stats_player_week_{s}"),
    ("stats_team", "stats_team_week_{s}"),
    ("snap_counts", "snap_counts_{s}"),
    ("injuries", "injuries_{s}"),
    ("depth_charts", "depth_charts_{s}"),
    ("rosters", "roster_{s}"),
    ("pbp", "play_by_play_{s}"),
    ("ftn_charting", "ftn_charting_{s}"),
    ("pfr_advstats", "advstats_week_rec_{s}"),
    ("pfr_advstats", "advstats_week_rush_{s}"),
    ("pfr_advstats", "advstats_week_pass_{s}"),
    ("pfr_advstats", "advstats_week_def_{s}"),
]
SINGLE = [("schedules", "games"), ("players", "players")]
# not available in nflverse-data; lives in the ffverse release (used by fit_opportunity only)
FFO = "https://github.com/ffverse/ffopportunity/releases/download/latest-data/ep_weekly_{s}.parquet"


def _get(url, dest):
    tmp = dest + ".part"
    with httpx.stream("GET", url, follow_redirects=True, timeout=120) as r:
        if r.status_code != 200:
            return r.status_code
        with open(tmp, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    os.replace(tmp, dest)
    return 200


def fetch(season, history=(2023, 2024, 2025), with_pbp=True, with_ffo=False, force_current=True):
    """Fetch the nflverse tables the engine reads. Returns {file: status}."""
    seasons = sorted(set(history) | {season})
    status = {}
    jobs = [(t, f"{s}.parquet") for t, s in SINGLE]
    for s in seasons:
        for tag, stem in PER_SEASON:
            if tag == "pbp" and not with_pbp:
                continue
            jobs.append((tag, stem.format(s=s) + ".parquet"))
    for tag, fn in jobs:
        dest = NFLV + fn
        current = fn.split("_")[-1].startswith(str(season)) or fn in ("games.parquet", "players.parquet")
        if os.path.exists(dest) and not (current and force_current):
            status[fn] = "cached"
            continue
        code = _get(f"{BASE}/{tag}/{fn}", dest)
        status[fn] = "ok" if code == 200 else f"HTTP {code}"
    if with_ffo:
        for s in seasons:
            fn = f"ffo_weekly_{s}.parquet"
            if not os.path.exists(NFLV + fn):
                code = _get(FFO.format(s=s), NFLV + fn)
                status[fn] = "ok" if code == 200 else f"HTTP {code}"
    return status


if __name__ == "__main__":
    st = fetch(int(os.environ.get("APEX_SEASON", 2026)))
    bad = {k: v for k, v in st.items() if v.startswith("HTTP")}
    print(f"{len(st)} files, {len(bad)} failed")
    for k, v in bad.items():
        print("  ", k, v)
    sys.exit(1 if bad else 0)
