"""Acceptance coverage for the documentation-only 2026 evidence authorization gate."""
from __future__ import annotations

from pathlib import Path


CONTRACT = Path(
    "contracts/projections/2026-player-level-evidence-source-freshness-authorization-v0.1.md"
)
REGISTER = Path("docs/data_source_connector_register.md")
LEDGER = Path("docs/decision_ledger.md")


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_contract_is_a_documentation_only_read_only_gate():
    text = _text(CONTRACT)
    assert "**Version:** `0.1`" in text
    assert "NO SOURCE OR LIVE EVIDENCE AUTHORIZED" in text
    assert "Every source remains read-only." in text
    assert "does not approve a source, authorize a provider retrieval, authorize live evidence" in text
    assert "Provider/API/network retrieval remains out of scope" in text


def test_contract_keeps_benchmark_roles_out_of_evidence_inputs():
    text = _text(CONTRACT)
    assert "`ranking`, `ADP`, and `analyst_projection` roles are benchmark-only." in text
    assert "not permitted evidence inputs" in text


def test_contract_requires_source_specific_provenance_before_use():
    text = _text(CONTRACT)
    assert "source-specific authorization approved under this contract is required before a source can be used." in text
    for field in (
        "`source_sha256`",
        "`parser_version`",
        "`source_provider`",
        "`source_url`",
        "`provider_record_id`",
        "`retrieved_at_utc`",
        "`effective_time_utc`",
        "`as_of_timestamp_utc`",
    ):
        assert field in text
    assert "exactly one source locator" in text
    assert "fail closed" in text


def test_contract_makes_u08_a_hard_ingest_prerequisite():
    text = _text(CONTRACT)
    assert "U08 (keeper/dynasty status) is a hard ingest prerequisite" in text
    assert "An unresolved, conflicting, or expired U08 decision blocks ingest" in text


def test_contract_requires_honest_degraded_mode_and_separate_freshness_policy():
    text = _text(CONTRACT)
    assert "validates temporal non-futurity only" in text
    assert "does not certify source freshness" in text
    assert "does not invent a numeric freshness threshold or source SLA" in text
    assert "source-specific freshness policy" in text
    assert "`data_freshness_status` as `stale` or `incomplete`" in text
    assert "avoid any current, fresh, or complete claim" in text
    assert "no live evidence authorization exists under this contract" in text


def test_register_and_ledger_record_gate_without_authorizing_live_evidence():
    register = _text(REGISTER)
    ledger = _text(LEDGER)
    assert "2026 Player-Level Evidence Source & Freshness Authorization Gate" in register
    assert str(CONTRACT).replace("\\", "/") in register
    assert "No source is authorized by this section for 2026 player-level evidence ingest." in register
    assert "Version 3.16" in ledger
    assert "This record authorizes no source, provider retrieval, network call, live evidence" in ledger
