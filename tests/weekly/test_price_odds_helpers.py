"""price_odds.bias_offset: the all-stale case (DECISIONS #67) produced an empty frame whose bias column became text."""
import ast
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parents[2] / "engine/weekly/price_odds.py"


def _load_helper():
    tree = ast.parse(SRC.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "bias_offset")
    ns = {"pd": pd}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(SRC), "exec"), ns)
    return ns["bias_offset"]


def test_bias_offset_empty_frame_is_float_and_subtractable():
    bias_offset = _load_helper()
    E = pd.DataFrame({"market": pd.Series([], dtype="str"), "edge": pd.Series([], dtype=float)})
    b = bias_offset(E.market, pd.Series(dtype=float))
    assert b.dtype == float
    out = np.where(pd.Series([], dtype=bool), E.edge - b, E.edge + b)
    assert len(out) == 0


def test_bias_offset_maps_values():
    bias_offset = _load_helper()
    b = bias_offset(pd.Series(["rec_yds", "anytime_td", "x"]), pd.Series({"rec_yds": -0.07, "anytime_td": -0.03}))
    assert b.dtype == float
    assert b.iloc[0] == -0.07 and b.iloc[1] == -0.03 and np.isnan(b.iloc[2])
