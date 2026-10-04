"""apex-weekly: one command per weekly step. Every step is idempotent and resumable.

  apex-weekly fetch  --season 2026
  apex-weekly run    --season 2026 [--week N] --track both|model|market [--dfs]
  apex-weekly freeze --season 2026 --week N --track market      (immutable, hashed)
  apex-weekly grade  runs/weekly/<run_id>
  apex-weekly fit    availability|team|player|calibration|weather
  apex-weekly verify runs/weekly/<run_id>
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PIPELINE = ["run_all.py", "build_outputs.py", "projections_report.py", "build_projection_tables.py"]
DFS = ["dfs_collect.py"]  # dfs_classic.py takes the track as argv
FITS = {"availability": ["fit_availability.py"], "team": ["fit_team_priors.py"], "player": ["fit_player_priors.py"],
        "calibration": ["calibrate_bt.py"], "weather": ["weather.py"], "opportunity": ["fit_opportunity.py"]}


def _sh(script, env, args=()):
    r = subprocess.run([sys.executable, script, *args], cwd=HERE, env=env)
    if r.returncode != 0:
        raise SystemExit(f"step failed: {script} (exit {r.returncode})")


def _env(args, track=None):
    e = dict(os.environ)
    e["APEX_SEASON"] = str(args.season)
    if getattr(args, "week", None):
        e["APEX_TARGET_WEEK"] = str(args.week)
    if track:
        e["APEX_ENV"] = track
    return e


def cmd_fetch(a):
    from fetch_data import fetch
    st = fetch(a.season, with_pbp=not a.no_pbp, with_ffo=a.ffo)
    bad = {k: v for k, v in st.items() if v.startswith("HTTP")}
    print(f"{len(st)} files, {len(bad)} unavailable")
    for k, v in bad.items():
        print("  ", k, v)
    core = [k for k in bad if k.startswith(("stats_player", "snap_counts", "injuries", "depth_charts", "games", "players"))]
    return 1 if core else 0


def cmd_run(a):
    tracks = ["model", "market"] if a.track == "both" else [a.track]
    for t in tracks:  # sequential on purpose: tracks share no state only if OUT differs
        from paths import OUT, DELIV
        e = _env(a, t)
        e["APEX_OUT"] = OUT.rstrip("/") + "_" + t
        e["APEX_DELIV"] = DELIV.rstrip("/") + "_" + t
        os.makedirs(e["APEX_OUT"], exist_ok=True)
        os.makedirs(e["APEX_DELIV"], exist_ok=True)
        for s in PIPELINE:
            _sh(s, e)
        if a.dfs:
            if not e.get("APEX_DK_SALARIES"):
                raise SystemExit("--dfs needs APEX_DK_SALARIES=<path to DKSalaries_classic.csv>")
            for s in DFS:
                _sh(s, e)
            _sh("dfs_classic.py", e, [t])
        print(f"[{t}] done -> {e['APEX_OUT']}")
    return 0


def cmd_freeze(a):
    from manifest import freeze
    from paths import OUT, DELIV
    out = a.out or (OUT.rstrip("/") + "_" + a.track)
    print(freeze(a.season, a.week, a.track, out_dir=out, notes=a.notes, deliv_dir=DELIV.rstrip("/") + "_" + a.track))
    return 0


def cmd_grade(a):
    from grade import grade
    r = grade(a.run_dir)
    print(json.dumps(r, indent=1))
    return 0 if r.get("status") == "graded" else 2


def cmd_verify(a):
    from manifest import verify
    bad = verify(a.run_dir)
    print("intact" if not bad else f"MISMATCH: {bad}")
    return 1 if bad else 0


def cmd_fit(a):
    for s in FITS[a.which]:
        _sh(s, _env(a))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="apex-weekly")
    sp = p.add_subparsers(dest="cmd", required=True)
    f = sp.add_parser("fetch"); f.add_argument("--season", type=int, required=True)
    f.add_argument("--no-pbp", action="store_true"); f.add_argument("--ffo", action="store_true"); f.set_defaults(fn=cmd_fetch)
    r = sp.add_parser("run"); r.add_argument("--season", type=int, required=True); r.add_argument("--week", type=int)
    r.add_argument("--track", choices=["model", "market", "both"], default="both"); r.add_argument("--dfs", action="store_true"); r.set_defaults(fn=cmd_run)
    z = sp.add_parser("freeze"); z.add_argument("--season", type=int, required=True); z.add_argument("--week", type=int, required=True)
    z.add_argument("--track", choices=["model", "market"], required=True); z.add_argument("--out"); z.add_argument("--notes", default=""); z.set_defaults(fn=cmd_freeze)
    g = sp.add_parser("grade"); g.add_argument("run_dir"); g.set_defaults(fn=cmd_grade)
    v = sp.add_parser("verify"); v.add_argument("run_dir"); v.set_defaults(fn=cmd_verify)
    t = sp.add_parser("fit"); t.add_argument("which", choices=sorted(FITS)); t.add_argument("--season", type=int, default=2026); t.set_defaults(fn=cmd_fit)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
