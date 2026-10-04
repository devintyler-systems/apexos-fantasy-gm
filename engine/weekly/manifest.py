"""Freeze a run: immutable directory with projections + manifest (as-of, versions, input hashes).

Contract: contracts/weekly/weekly_run_manifest.v0.1.yaml. A frozen run is never overwritten.
"""
import datetime as dt
import glob
import hashlib
import json
import os
import platform
import subprocess
import sys

import pandas as pd

from paths import CONF, NFLV, OUT, RUNS
from version import ENGINE_VERSION

SCHEMA = "weekly_run_manifest/0.1"
# Artifacts copied into a frozen run (small, human-diffable). Raw sim pickles stay out.
FREEZE_PICKLES = {"proj_all.pkl": "projections.csv", "rank_raw.pkl": "rankings_raw.csv"}
FREEZE_CSVS = ["w4_game_environment.csv", "w4_team_environment.csv", "w4_team_totals.csv", "w4_td_markets.csv",
               "w4_injury_adjustments.csv", "qa_reconcile.csv"]


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=os.path.dirname(__file__),
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unknown"


def _versions():
    out = {"python": platform.python_version()}
    for m in ("pandas", "numpy", "scipy", "pulp"):
        try:
            out[m] = __import__(m).__version__
        except Exception:
            pass
    return out


def run_id(season, week, track, as_of):
    return f"{season}_w{int(week):02d}_{track}_{as_of.strftime('%Y%m%dT%H%M%SZ')}"


def freeze(season, week, track, out_dir=None, runs_dir=None, as_of=None, notes="", deliv_dir=None):
    """Copy a finished run's outputs into an immutable run directory and write manifest.json."""
    out_dir = out_dir or OUT
    runs_dir = runs_dir or RUNS
    as_of = as_of or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    rid = run_id(season, week, track, as_of)
    dest = os.path.join(runs_dir, rid)
    if os.path.exists(dest):
        raise FileExistsError(f"frozen run already exists, refusing to overwrite: {dest}")
    os.makedirs(dest)
    artifacts = {}
    for pk, name in FREEZE_PICKLES.items():
        src = os.path.join(out_dir, pk)
        if os.path.exists(src):
            df = pd.read_pickle(src)
            df.to_csv(os.path.join(dest, name), index=False)
            artifacts[name] = {"rows": int(len(df))}
    for name in FREEZE_CSVS:
        src = os.path.join(out_dir, name)
        if os.path.exists(src):
            with open(src, "rb") as a, open(os.path.join(dest, name), "wb") as b:
                b.write(a.read())
            artifacts[name] = {"rows": int(sum(1 for _ in open(src, encoding="utf-8", errors="ignore")) - 1)}
    if deliv_dir:      # DFS lineups (the raw DK salary file and the salary pool are never frozen/committed)
        for name in (f"dfs_classic_gpp_lineups_{track}.csv", f"dfs_classic_cash_and_stacks_{track}.csv"):
            src = os.path.join(deliv_dir, name)
            if os.path.exists(src):
                with open(src, "rb") as a, open(os.path.join(dest, name), "wb") as b:
                    b.write(a.read())
                artifacts[name] = {"rows": int(sum(1 for _ in open(src, encoding="utf-8", errors="ignore")) - 1)}
    mo = os.environ.get("APEX_MANUAL_OUT")
    if mo and os.path.exists(mo):        # confirmed-inactive overrides travel with the run
        with open(mo, "rb") as a, open(os.path.join(dest, "manual_overrides.csv"), "wb") as b:
            b.write(a.read())
        artifacts["manual_overrides.csv"] = {"rows": int(sum(1 for _ in open(mo, encoding="utf-8", errors="ignore")) - 1)}
    if "projections.csv" not in artifacts:
        raise RuntimeError("no projections found in out_dir; run the pipeline before freezing")
    for name, meta in artifacts.items():
        meta["sha256"] = sha256(os.path.join(dest, name))
    inputs = {}
    for p in sorted(glob.glob(NFLV + "*.parquet")):
        inputs[os.path.basename(p)] = sha256(p)
    for p in sorted(glob.glob(CONF + "*")):
        inputs["config/" + os.path.basename(p)] = sha256(p)
    dk = os.environ.get("APEX_DK_SALARIES")
    if dk and os.path.exists(dk):
        inputs["dk_salaries"] = sha256(dk)
    man = {
        "schema": SCHEMA,
        "run_id": rid,
        "season": int(season), "week": int(week), "track": track,
        "as_of_utc": as_of.isoformat().replace("+00:00", "Z"),
        "engine_version": ENGINE_VERSION,
        "git_sha": _git_sha(),
        "versions": _versions(),
        "env": {k: v for k, v in sorted(os.environ.items()) if k.startswith("APEX_") and k not in ("APEX_DK_SALARIES", "APEX_MANUAL_OUT")},
        "inputs_sha256": inputs,
        "artifacts": artifacts,
        "uses_future_information": False,
        "notes": notes,
    }
    with open(os.path.join(dest, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1, sort_keys=True)
    return dest


def verify(run_dir):
    """Re-hash artifacts; return list of mismatches (empty == intact)."""
    man = json.load(open(os.path.join(run_dir, "manifest.json")))
    bad = []
    for name, meta in man["artifacts"].items():
        p = os.path.join(run_dir, name)
        if not os.path.exists(p) or sha256(p) != meta["sha256"]:
            bad.append(name)
    return bad


if __name__ == "__main__":
    print(freeze(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))
