from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from engine.ingestion.nflverse_pbp import (
    FALSE_PLAY_TYPES,
    NO_PLAY_NORMALIZATION_VERSION,
    PARSER_VERSION,
    normalize_no_play,
)


def test_direct_no_play_is_true() -> None:
    assert normalize_no_play(
        {"play_type": "no_play", "pass_attempt": 1, "rush_attempt": 0}
    ) == "true"


@pytest.mark.parametrize("play_type", sorted(FALSE_PLAY_TYPES))
def test_recognized_non_no_play_values_are_false(play_type: str) -> None:
    assert normalize_no_play(
        {"play_type": play_type, "pass_attempt": 0, "rush_attempt": 0}
    ) == "false"


@pytest.mark.parametrize(
    ("pass_attempt", "rush_attempt"),
    [(None, None), (0, 0), (False, False)],
)
def test_null_play_type_without_opportunity_is_conservatively_true(
    pass_attempt: object, rush_attempt: object
) -> None:
    assert normalize_no_play(
        {
            "play_type": None,
            "pass_attempt": pass_attempt,
            "rush_attempt": rush_attempt,
        }
    ) == "true"


@pytest.mark.parametrize(
    ("pass_attempt", "rush_attempt"),
    [(1, 0), (0, 1), (True, False), (False, True)],
)
def test_null_play_type_with_opportunity_is_unknown(
    pass_attempt: object, rush_attempt: object
) -> None:
    assert normalize_no_play(
        {
            "play_type": None,
            "pass_attempt": pass_attempt,
            "rush_attempt": rush_attempt,
        }
    ) == "unknown"


@pytest.mark.parametrize("missing", ["play_type", "pass_attempt", "rush_attempt"])
def test_required_source_field_absence_is_unknown(missing: str) -> None:
    row: dict[str, object] = {
        "play_type": "pass",
        "pass_attempt": 1,
        "rush_attempt": 0,
    }
    del row[missing]
    assert normalize_no_play(row) == "unknown"


def test_unexpected_play_type_is_unknown() -> None:
    assert normalize_no_play(
        {"play_type": "provider_new_value", "pass_attempt": 0, "rush_attempt": 0}
    ) == "unknown"


def test_accepted_penalty_stays_separate_from_no_play() -> None:
    row = {
        "play_type": "pass",
        "pass_attempt": 1,
        "rush_attempt": 0,
        "penalty": 1,
    }
    assert normalize_no_play(row) == "false"
    assert row["penalty"] == 1


def test_declined_penalty_non_play_is_conservatively_true() -> None:
    row = {
        "play_type": None,
        "pass_attempt": None,
        "rush_attempt": None,
        "penalty": None,
    }
    assert normalize_no_play(row) == "true"


@pytest.mark.parametrize(
    "row",
    [
        {"play_type": "pass", "pass_attempt": 1, "rush_attempt": 0, "sack": 1},
        {"play_type": "qb_spike", "pass_attempt": 0, "rush_attempt": 0, "qb_spike": 1},
        {
            "play_type": "no_play",
            "pass_attempt": 1,
            "rush_attempt": 0,
            "two_point_conv_result": "success",
        },
    ],
)
def test_independent_exclusion_fields_do_not_redefine_mapping(
    row: dict[str, object]
) -> None:
    expected = "true" if row["play_type"] == "no_play" else "false"
    assert normalize_no_play(row) == expected


def test_normalization_does_not_mutate_raw_record() -> None:
    row = {
        "play_type": "no_play",
        "pass_attempt": 0,
        "rush_attempt": 0,
        "desc": "provider bytes remain raw",
    }
    before = deepcopy(row)
    assert normalize_no_play(row) == "true"
    assert row == before


def test_contract_addenda_bind_mapping_and_preserve_b07_rules() -> None:
    root = Path(__file__).resolve().parents[2]
    b06 = (
        root
        / "contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2-no-play-addendum-v0.1.md"
    ).read_text(encoding="utf-8")
    b07 = (
        root
        / "contracts/projections/xtd-lookup-table-contract-resolution-addendum-v0.1-no-play-addendum.md"
    ).read_text(encoding="utf-8")
    assert 'play_type = "no_play"' in b06
    assert "logical_no_play = unknown" in b06
    assert "logical_no_play_unknown" in b06
    assert "raw provider Parquet bytes and columns remain unchanged" in b06
    assert "0.17, 0.33, and 0.50" in b07
    assert "100.0 weighted-sample confidence threshold" in b07
    assert "rolling-origin Brier-score promotion gate" in b07
    assert "B-07 remains blocked" in b07


def test_parser_identity_binds_controlling_interface_and_normalization() -> None:
    assert PARSER_VERSION.startswith("b06-v0.2-")
    assert NO_PLAY_NORMALIZATION_VERSION in PARSER_VERSION
    assert "b06-v0.3" not in PARSER_VERSION
