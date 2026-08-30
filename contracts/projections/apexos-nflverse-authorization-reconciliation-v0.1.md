# ApexOS nflverse Authorization Reconciliation v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-NFLVERSE-AUTHORIZATION-RECONCILIATION` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — reconciliation review required before ingestion implementation |
| Change type | Structural |
| Dependencies | `contracts/projections/apexos-projection-feature-and-score-lineage-contract-v0.1.md`; `contracts/projections/apexos-projection-source-authorization-register-v0.1.md`; `contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`; `docs/data_source_connector_register.md`; `docs/decision_ledger.md` |
| Superseded artifact | `contracts/projections/source-authorizations/nflverse-direct-github-release-assets-2026-player-facts-candidate-v0.1.md` |
| Successor regression test path | `tests/acceptance/test_u08_nflverse_candidate_evidence_authorization_v0_1.py` |
| Current authority | `contracts/projections/apexos-projection-source-authorization-register-v0.1.md` |
| Implementation authorization | None. This artifact reconciles documentation authority only. It does not authorize retrieval, ingestion, parsing, storage, feature use, model development, scoring, projection artifacts, recommendations, or external writes. |

## Decision Statement

**Design decision:** The legacy candidate-only nflverse player-facts
authorization artifact is superseded as an active source-authority record.
The canonical authority for future nflverse evidence evaluation is
`contracts/projections/apexos-projection-source-authorization-register-v0.1.md`.

**Design decision:** The paired legacy acceptance test remains at its existing
path and is replaced with successor regression coverage. The successor
coverage preserves the active U08 and schedule-authority boundaries while
validating the canonical source-governance boundary instead of the superseded
candidate document.

**Confirmed evidence:** The superseded artifact is explicitly labeled
`CANDIDATE ONLY — NOT APPROVED FOR USE`. The canonical v0.1 register
records `nflverse_direct_github_release_assets` as `approved_bounded` for
historical football-event evidence only, under separate source, feature,
identity, time-integrity, scoring, and acceptance gates.

## Authority Resolution

```yaml
authority_resolution:
  prior_candidate_record:
    path: "contracts/projections/source-authorizations/nflverse-direct-github-release-assets-2026-player-facts-candidate-v0.1.md"
    previous_status: "candidate_only_not_approved_for_use"
    disposition: "superseded_and_removed"
    reason:
      - "Candidate-only documentation is not the canonical current source-authorization authority."
      - "Its 2026 player-facts framing could be mistaken for a field-level or projection-use authorization."
      - "The merged source register provides the current bounded authority, prohibited uses, provenance requirements, source gates, and degraded behavior."

  paired_legacy_test:
    path: "tests/acceptance/test_u08_nflverse_candidate_evidence_authorization_v0_1.py"
    superseded_prior_disposition: "obsolete_and_removed"
    superseded_prior_disposition_note: "Historical label retained for audit only; the test path remains active with successor regression coverage."
    disposition: "retained_and_replaced_with_successor_regression_coverage"
    reason:
      - "The prior test content validated the removed candidate document rather than the canonical source register."
      - "Successor coverage preserves the active U08 and schedule-authority assertions while shifting source-authority checks to the canonical source register."
      - "This replacement does not waive future implementation acceptance tests."

  canonical_current_authority:
    path: "contracts/projections/apexos-projection-source-authorization-register-v0.1.md"
    source_id: "nflverse_direct_github_release_assets"
    status: "approved_bounded"
    bounded_purpose:
      - "Historical football-event evidence for separately approved future feature evaluation and football-event projection development."
      - "Reproducible immutable raw-evidence snapshot capture under the approved ingestion contract."
      - "Historical baseline and time-integrity evaluation where separately contracted."
    remains_prohibited:
      - "nfl_data_py"
      - "Automatic projection artifact creation"
      - "Feature, model, event-target, training-label, calibration-target, scoring, or recommendation use before separate gates pass"
      - "Provider-projection substitution, blending, calibration, or fallback"
      - "Current live platform availability or draft-state authority"
      - "External writes"
```

## Compatibility Ruling

**Ruling:** `SUPERSESSION`, not compatibility.

The legacy candidate record does not remain a compatible co-authority path.
The paired test path remains active with successor regression coverage, while
the canonical source register supplies the sole repository-level source
authorization boundary for future nflverse evaluation.

This supersession does not broaden the current source authorization. It
preserves all boundaries of the canonical register:

- nflverse direct GitHub release assets are `approved_bounded` only.
- `nfl_data_py` remains prohibited.
- No raw evidence may become a feature, target, model input, scoring input,
  or recommendation input without separately approved gates.
- Provider-generated fantasy point totals, ranks, ADP, consensus,
  recommendations, status, opponent/schedule context, percentages, and UI
  signals remain prohibited in `apexos_projection` mode.
- Missing lineage, source validation, canonical identity, temporal
  integrity, scoring reconciliation, uncertainty, or known limitations
  cannot silently transition to Provider Snapshot Mode.

## Required Future Acceptance Coverage

The replacement of the legacy candidate-document assertions with successor
regression coverage creates no waiver.

Before any nflverse retrieval or ingestion implementation can be approved,
the implementation handoff must require new acceptance coverage against the
canonical source register and ingestion contract for:

- Direct GitHub release-asset access only; `nfl_data_py` rejected.
- Immutable raw-evidence snapshot manifest and source asset identity.
- Retrieval timestamp, effective timestamp when available, and source
  contract reference.
- Parser version, schema validation, malformed-record handling, and
  retention behavior.
- Canonical identity mapping, ambiguity quarantine, and no destructive
  merge behavior.
- Time-integrity checks and rejection of post-decision information.
- Visible degraded behavior for source authorization, snapshot, schema,
  identity, freshness, and temporal failures.
- No provider-projection input, provider fallback, or provider-derived
  decision influence in ApexOS Projection Mode.
- Read-only behavior and no external fantasy-platform action.

## Scope and Non-Goals

### Scope

- Resolve the authoritative relationship between the legacy candidate
  artifact and the canonical Projection Source Authorization Register v0.1.
- Remove the superseded candidate artifact and replace the paired test content
  with successor regression coverage under its existing path.
- Preserve an explicit, versioned decision record explaining the
  supersession and the required future implementation coverage.

### Non-Goals

- No new source authorization is created.
- No change is made to the canonical Projection Source Authorization
  Register v0.1.
- No modification is made to the nflverse ingestion contract.
- No source is retrieved, downloaded, parsed, ingested, transformed, or
  stored.
- No player fact, feature, event target, model, scoring behavior,
  projection artifact, decision adapter, recommendation, board, or provider
  integration is changed or authorized.
- No source-rights, rate-limit, freshness, or field-semantics claim is
  added.
- No external write is authorized.

## Assumptions Register

| ID | Assumption | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-RECON-001 | The canonical v0.1 Projection Source Authorization Register is the sole current repository-level source authority for nflverse evidence evaluation. | Future source and ingestion work | P0 if legacy candidate material is treated as co-authority. | ApexOS Architect | Immediate and ongoing. |
| A-RECON-002 | Replacing the candidate-document assertions with successor regression coverage does not remove required future ingestion acceptance coverage. | Future ingestion test suite | P0 if candidate supersession is misread as a test waiver. | ApexOS Architect / Builder | Before ingestion implementation. |
| A-RECON-003 | No extraction, ingestion, feature, projection, scoring, or recommendation behavior is authorized by this reconciliation. | Projection program | P0 if documentation reconciliation becomes implicit implementation approval. | ApexOS Architect | Immediate and ongoing. |
| A-RECON-004 | The exact field scope, source rights, asset availability, schema semantics, freshness policy, and retention design remain separately gated. | Source ingestion and feature promotion | P1 if source access is mistaken for complete operational approval. | ApexOS Architect | Before implementation. |

## Acceptance Criteria

- Exactly one new reconciliation record is added.
- The legacy candidate artifact is deleted.
- The exact paired test path is retained and replaced with successor
  regression coverage.
- The final diff contains one added reconciliation record, one deleted
  candidate artifact, and one modified successor regression test.
- No other paths change.
- The reconciliation ruling is explicitly `SUPERSESSION`, not
  compatibility.
- The canonical current authority is named exactly as
  `contracts/projections/apexos-projection-source-authorization-register-v0.1.md`.
- `nfl_data_py` remains prohibited.
- Provider-generated fantasy points, ranks, ADP, consensus,
  recommendations, statuses, schedule context, percentages, and UI signals
  remain prohibited in ApexOS Projection Mode.
- The record explicitly states that no retrieval, ingestion, feature,
  model, projection artifact, scoring, recommendation, or external write
  behavior is authorized.
- Required future ingestion acceptance coverage is preserved explicitly.
- The PR is open, non-draft, documentation/test-reconciliation only, and
  unmerged.

## Builder Handoff Boundary

No ingestion implementation may begin from this reconciliation alone.

A subsequent implementation handoff must start from the canonical
Projection Source Authorization Register v0.1 and the existing nflverse
ingestion contract. It must specify exact release assets, bounded field
scope, immutable manifests, terms references, parsing and schema rules,
canonical identity quarantine, time-integrity checks, retention, fixture
coverage, degraded behavior, and provider-contamination prevention.

## Change Log

- `v0.1` — Structural reconciliation. Supersedes and removes the legacy
  candidate-only nflverse player-facts authorization artifact while retaining
  the paired test path and migrating regression coverage to the canonical
  authority. Establishes the merged Projection Source Authorization Register
  v0.1 as the sole repository-level authority for bounded nflverse evidence
  evaluation.
