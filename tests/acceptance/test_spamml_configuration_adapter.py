from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path

import pytest

from engine.draft import spamml_configuration as config


def _fixture_hashes(*paths: Path) -> dict[str, str]:
    return {
        key: sha256(path.read_bytes()).hexdigest().upper()
        for key, path in zip(("league_rules", "seat_assignment", "round_order_map"), paths, strict=True)
    }


def _fixture_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    paths = (
        config.DEFAULT_LEAGUE_RULES_PATH,
        config.DEFAULT_SEAT_ASSIGNMENT_PATH,
        config.DEFAULT_ROUND_ORDER_MAP_PATH,
    )
    copied = tuple(tmp_path / path.name for path in paths)
    for source, destination in zip(paths, copied, strict=True):
        destination.write_bytes(source.read_bytes())
    return copied


def _load_fixture(paths: tuple[Path, Path, Path]):
    return config.load_spamml_configuration(
        league_rules_path=paths[0],
        seat_assignment_path=paths[1],
        round_order_map_path=paths[2],
        expected_hashes=_fixture_hashes(*paths),
    )


def test_at_01_through_at_13_canonical_configuration_is_static_and_exact() -> None:
    result = config.load_spamml_configuration()
    assert result.status == "valid"
    assert result.reason_codes == ()
    assert result.configuration is not None
    value = result.configuration
    assert value["league_id"] == "spamml-2026"
    assert value["season"] == 2026
    assert value["league_rules_version"] == "0.7"
    assert value["team_count"] == 16
    assert value["draft_format"] == "non_standard_snake"
    assert value["total_roster_slots"] == 8
    assert value["bench_slots"] == 0
    assert dict(value["starter_counts"]) == {"QB": 1, "RB": 2, "REC": 3, "KCK": 1, "D_O": 1}
    assert value["slot_eligibility"]["REC"] == ("WR", "TE")
    assert value["slot_eligibility"]["QB"] == ("QB",)
    assert value["flex_eligibility"] is None
    assert value["declared_scoring"]["passing"]["td_pass"] == 6
    assert value["declared_scoring"]["rushing"]["td_rush"] == 6
    assert value["declared_scoring"]["receiving"]["td_reception"] == 6
    assert value["declared_scoring"]["passing"]["two_point_conversion_pass"] == 2
    assert value["declared_scoring"]["rushing"]["two_point_conversion_rush"] == 2
    assert value["declared_scoring"]["receiving"]["two_point_conversion_catch"] == 2
    assert set(value["declared_zero_fields"].values()) == {0}
    assert all(item is None for item in value["undefined_capability_gaps"].values())
    assert value["manager_team_name"] == "Professor FleX"
    assert value["manager_draft_seat"] == 4
    assert value["planned_pick_sequence"] == (4, 29, 45, 52, 68, 93, 109, 116)
    assert value["planned_schedule_only"] is True
    assert "freshness" not in result.to_dict()["configuration"]


def test_at_12_uses_existing_finalized_map_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def finalized_map() -> dict[str, dict[str, tuple[int, ...]]]:
        nonlocal called
        called = True
        return {"position_pick_map": {"4": (4, 29, 45, 52, 68, 93, 109, 116)}}

    monkeypatch.setattr(config, "build_full_map", finalized_map)
    assert config.load_spamml_configuration().status == "valid"
    assert called is True


def test_at_14_digest_mismatch_rejects(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    paths[0].write_text("league_id: changed\n", encoding="utf-8")
    result = config.load_spamml_configuration(
        league_rules_path=paths[0], seat_assignment_path=paths[1], round_order_map_path=paths[2]
    )
    assert result.status == "rejected"
    assert result.reason_codes == ("AUTHORITY_DIGEST_MISMATCH_LEAGUE_RULES",)


@pytest.mark.parametrize(
    ("target", "contents", "reason"),
    [
        ("league", "[not: valid", "AUTHORITY_YAML_MALFORMED"),
        ("league", "league_id: spamml-2026\nseason: 2026\ncontract_version: '9.9'\n", "LEAGUE_RULES_IDENTITY_OR_VERSION_MISMATCH"),
        ("seat", "artifact:\n  version: '9.9'\nidentity:\n  season: 2026\n", "SEAT_ASSIGNMENT_IDENTITY_OR_VERSION_MISMATCH"),
        ("map", "artifact:\n  version: '1.0'\n  status: DRAFT\n", "ROUND_ORDER_MAP_NOT_FINALIZED"),
    ],
)
def test_at_15_and_at_16_fixture_authority_failures_reject(
    tmp_path: Path, target: str, contents: str, reason: str
) -> None:
    paths = _fixture_paths(tmp_path)
    index = {"league": 0, "seat": 1, "map": 2}[target]
    paths[index].write_text(contents, encoding="utf-8")
    result = _load_fixture(paths)
    assert result.status == "rejected"
    assert result.reason_codes == (reason,)


def test_at_15_missing_authority_rejects(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    paths[0].unlink()
    result = config.load_spamml_configuration(
        league_rules_path=paths[0], seat_assignment_path=paths[1], round_order_map_path=paths[2],
        expected_hashes=config.CANONICAL_AUTHORITY_SHA256,
    )
    assert result.status == "rejected"
    assert result.reason_codes == ("AUTHORITY_FILE_MISSING",)


def test_at_17_manager_seat_failure_rejects(tmp_path: Path) -> None:
    paths = _fixture_paths(tmp_path)
    text = paths[1].read_text(encoding="utf-8").replace("manager_draft_seat: 4", "manager_draft_seat: 5")
    paths[1].write_text(text, encoding="utf-8")
    result = _load_fixture(paths)
    assert result.status == "rejected"
    assert result.reason_codes == ("MANAGER_SEAT_UNRESOLVED",)


def test_at_18_and_at_19_adapter_source_has_no_network_live_state_or_player_imports() -> None:
    source = Path(config.__file__).read_text(encoding="utf-8")
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imports.isdisjoint({"requests", "httpx", "socket", "engine.ingestion", "engine.projections"})
    assert "RuntimeDraftStateConsumer" not in source
    assert "live_state_consumer" not in source


def test_result_is_immutable_and_serializable() -> None:
    result = config.load_spamml_configuration()
    assert result.configuration is not None
    with pytest.raises(TypeError):
        result.configuration["league_id"] = "other"  # type: ignore[index]
    serialized = result.to_dict()
    assert serialized["configuration"]["planned_pick_sequence"] == [4, 29, 45, 52, 68, 93, 109, 116]
