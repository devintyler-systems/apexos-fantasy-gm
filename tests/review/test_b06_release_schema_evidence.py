"""Narrow tests for the review-only B-06 schema evidence utility."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


pyarrow = pytest.importorskip("pyarrow")
parquet = pytest.importorskip("pyarrow.parquet")
UTILITY_PATH = Path(__file__).parents[2] / "tools" / "review" / "b06_release_schema_evidence.py"


def load_utility():
    spec = importlib.util.spec_from_file_location("b06_review_only_utility", UTILITY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_missing_required_column_returns_nonzero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A synthetic metadata fixture proves the utility's required-column failure path."""
    fixture = tmp_path / "missing-pass-attempt.parquet"
    parquet.write_table(
        pyarrow.table(
            {
                "season": [2025],
                "season_type": ["REG"],
                "game_id": ["fixture"],
                "yardline_100": [50.0],
                "touchdown": [0.0],
                "rush_attempt": [0.0],
            }
        ),
        fixture,
    )
    utility = load_utility()
    monkeypatch.setattr(sys, "argv", [str(UTILITY_PATH), "--parquet", str(fixture)])

    assert utility.main() == 2
