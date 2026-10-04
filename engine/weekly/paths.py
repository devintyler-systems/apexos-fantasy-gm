"""Single source of truth for weekly-engine filesystem roots. All overridable by env."""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))


def _dir(env, default):
    p = os.environ.get(env, default)
    p = p if p.endswith("/") else p + "/"
    os.makedirs(p, exist_ok=True)
    return p


# nflverse parquet cache (never committed; see .gitignore)
NFLV = _dir("APEX_NFLV", os.path.join(_REPO, "var", "nflverse"))
# intermediate working files for a run
OUT = _dir("APEX_OUT", os.path.join(_REPO, "var", "out"))
# deliverables for a run
DELIV = _dir("APEX_DELIV", os.path.join(_REPO, "var", "deliverables"))
# fitted parameters (committed, small)
CONF = os.path.join(_REPO, "config", "weekly") + "/"
# frozen, immutable run artifacts (small: manifest + projection CSVs; committed)
RUNS = _dir("APEX_RUNS", os.path.join(_REPO, "runs", "weekly"))
