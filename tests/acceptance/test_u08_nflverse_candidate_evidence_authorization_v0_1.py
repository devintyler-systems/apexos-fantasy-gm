"""Documentation-contract acceptance coverage for U08 and the nflverse candidate record."""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


V06 = Path("contracts/league_rules/spamml-2026-v0.6.yaml")
V07 = Path("contracts/league_rules/spamml-2026-v0.7.yaml")
CANDIDATE = Path(
    "contracts/projections/source-authorizations/"
    "nflverse-direct-github-release-assets-2026-player-facts-candidate-v0.1.md"
)
REGISTER = Path("docs/data_source_connector_register.md")
LEDGER = Path("docs/decision_ledger.md")


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_v07_resolves_u08_exactly_and_leaves_v06_outside_this_pr():
    rules = yaml.safe_load(V07.read_text(encoding="utf-8"))
    prior_rules = yaml.safe_load(V06.read_text(encoding="utf-8"))
    assert rules["league_id"] == "spamml-2026"
    assert rules["contract_version"] == "0.7"
    assert rules["amends"] == str(V06).replace("\\", "/")
    assert rules["keeper_dynasty"] == {"keeper": "none", "dynasty": False}
    resolution = rules["resolved_by_this_version"]
    assert len(resolution) == 1
    assert resolution[0]["id"] == "U08"
    assert resolution[0]["field"] == "keeper_dynasty"
    assert resolution[0]["resolution"] == "SPAMML 2026 is a redraft league with no keepers and no dynasty behavior."
    assert str(resolution[0]["resolved_date"]) == "2026-08-27"
    assert "U08" not in {item["id"] for item in rules["unknown_or_unconfirmed"]}
    assert rules["unknown_or_unconfirmed"] == [
        item for item in prior_rules["unknown_or_unconfirmed"] if item["id"] != "U08"
    ]
    assert subprocess.run(
        ["git", "diff", "--quiet", "origin/main", "--", str(V06)], check=False
    ).returncode == 0


def test_v07_retains_v12_as_sole_planned_schedule_timestamp_authority():
    rules = yaml.safe_load(V07.read_text(encoding="utf-8"))
    authority = "contracts/draft/spamml-2026-draft-seat-assignment-v1.2.yaml"
    assert rules["schedule_authority"]["sole_canonical_planned_timestamp_artifact"] == authority
    assert rules["draft"]["schedule_timestamp_authority"] == authority
    assert "sole canonical SPAMML 2026 planned schedule timestamp authority" in rules["schedule_authority"]["rule"]


def test_candidate_is_explicitly_candidate_only_and_read_only():
    text = _text(CANDIDATE)
    assert "CANDIDATE ONLY — NOT APPROVED FOR USE" in text
    assert "historical player/team factual evidence and canonical-reference support" in text
    assert "read-only only" in text
    assert "no implementation authorization" in text


def test_candidate_prohibits_live_and_decision_behavior():
    text = _text(CANDIDATE)
    for prohibited in (
        "provider retrieval", "network calls", "2026 live roster claims", "injuries",
        "availability", "rankings", "ADP", "analyst projections", "scoring", "PRV",
        "roster fit", "recommendations", "live artifact creation",
    ):
        assert prohibited in text


def test_candidate_requires_complete_later_approval_and_fail_closed_boundaries():
    text = _text(CANDIDATE)
    for required in (
        "purpose and bounded factual use case", "exact field inventory",
        "source provider", "provider terms and license verification",
        "authentication posture and rate-limit status", "exact GitHub release and asset identity",
        "local SHA-256", "parser version", "UTC retrieval, effective, and artifact as-of timestamps",
        "canonical player/team identity coverage", "source-specific freshness policy",
        "fallback and degraded-mode behavior", "read/write posture",
    ):
        assert required in text
    for boundary in (
        "Missing or ambiguous canonical identity", "hash mismatch", "missing provenance",
        "post-as-of evidence", "unapproved source status", "benchmark-only role fails closed",
    ):
        assert boundary in text


def test_candidate_does_not_invent_provider_facts_or_generalize_u08():
    text = _text(CANDIDATE)
    assert "no value is asserted by this candidate record" in text
    assert "must not infer provider terms, license, field coverage, rate limit, freshness SLA" in text
    assert "satisfies the U08 prerequisite only for SPAMML 2026" in text
    assert "must not be generalized to another league, season, or format" in text


def test_register_and_ledger_record_candidate_only_status():
    register = _text(REGISTER)
    ledger = _text(LEDGER)
    assert str(CANDIDATE).replace("\\", "/") in register
    assert "CANDIDATE ONLY — NOT APPROVED FOR USE" in register
    assert "This candidate entry authorizes no provider/API/network retrieval" in register
    assert "Version 3.17" in ledger
    assert "Structural governance decision" in ledger
    assert "nflverse direct GitHub release assets" in ledger
    assert "No live evidence, provider/API/network retrieval" in ledger
