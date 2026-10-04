"""APEX weekly props + DFS projection engine (self-contained; no dependency on the draft engine).

The pipeline modules in this directory are flat scripts that import each other by bare name
(`from params import ...`). `cli.py` runs them with this directory as cwd and on sys.path.
"""
from .version import ENGINE_VERSION  # noqa: F401
