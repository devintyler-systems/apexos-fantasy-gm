# Issue #25 acceptance coverage: parsed league-rules provenance.

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import engine.draft.round_order_map as round_order_map


class _ModulePath:
    def __init__(self, repository_root: Path) -> None:
        self._repository_root = repository_root

    def resolve(self) -> "_ModulePath":
        return self

    @property
    def parents(self) -> list[Path]:
        return [self._repository_root, self._repository_root, self._repository_root]


def _configure_rules_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    rules_directory = tmp_path / "contracts" / "league_rules"
    rules_directory.mkdir(parents=True)
    monkeypatch.setattr(round_order_map, "Path", lambda _: _ModulePath(tmp_path))
    return rules_directory


def test_current_canonical_rules_return_parsed_contract_version() -> None:
    assert round_order_map._league_rules_version() == "0.6"


def test_v06_delegates_planned_schedule_to_finalized_seat_assignment_only() -> None:
    rules_path = Path("contracts/league_rules/spamml-2026-v0.6.yaml")
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))

    assert rules["contract_version"] == "0.6"
    assert "date_time" not in rules["draft"]
    assert rules["schedule_authority"]["sole_canonical_planned_timestamp_artifact"] == (
        "contracts/draft/spamml-2026-draft-seat-assignment-v1.2.yaml"
    )
    assert "Manual live events and validated B-05 session state outrank" in rules["schedule_authority"]["precedence"]


@pytest.mark.parametrize(
    ("contents", "filename"),
    [
        ("league: spamml\n", "spamml-2026-v9.9.yaml"),
        ("contract_version: \"\"\n", "spamml-2026-v9.9.yaml"),
        ("contract_version: \"0.5-beta\"\n", "spamml-2026-v9.9.yaml"),
        ("contract_version: 0.5\n", "spamml-2026-v9.9.yaml"),
    ],
)
def test_invalid_contract_version_returns_provenance_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    contents: str,
    filename: str,
) -> None:
    rules_directory = _configure_rules_directory(monkeypatch, tmp_path)
    (rules_directory / filename).write_text(contents, encoding="utf-8")

    assert round_order_map._league_rules_version() == round_order_map.PROVENANCE_UNAVAILABLE


def test_filename_never_becomes_a_provenance_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    rules_directory = _configure_rules_directory(monkeypatch, tmp_path)
    (rules_directory / "spamml-2026-v9.9.yaml").write_text("league: spamml\n", encoding="utf-8")

    assert round_order_map._league_rules_version() != "spamml-2026-v9.9"
    assert round_order_map._league_rules_version() == round_order_map.PROVENANCE_UNAVAILABLE


def test_v04_fixture_remains_unmodified_and_does_not_require_contract_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    rules_directory = _configure_rules_directory(monkeypatch, tmp_path)
    v04 = rules_directory / "spamml-2026-v0.4.yaml"
    v04_contents = "league: spamml\n"
    v04.write_text(v04_contents, encoding="utf-8")
    (rules_directory / "spamml-2026-v0.5.yaml").write_text(
        "contract_version: \"0.5\"\n",
        encoding="utf-8",
    )

    assert round_order_map._league_rules_version() == "0.5"
    assert v04.read_text(encoding="utf-8") == v04_contents
