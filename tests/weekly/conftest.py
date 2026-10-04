import os
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="apex_weekly_test_")
# Must be set before engine/weekly/paths.py is imported anywhere.
os.environ.setdefault("APEX_NFLV", os.path.join(_TMP, "nflverse"))
os.environ.setdefault("APEX_OUT", os.path.join(_TMP, "out"))
os.environ.setdefault("APEX_DELIV", os.path.join(_TMP, "deliv"))
os.environ.setdefault("APEX_RUNS", os.path.join(_TMP, "runs"))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WEEKLY = os.path.join(ROOT, "engine", "weekly")
if WEEKLY not in sys.path:
    sys.path.insert(0, WEEKLY)


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: needs the nflverse cache (run in the weekly workflow)")
