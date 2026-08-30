# ApexOS nflverse Dictionary Release Schema Applicability Equivalence Policy v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | `APEXOS-NFLVERSE-DICTIONARY-RELEASE-SCHEMA-APPLICABILITY-EQUIVALENCE-POLICY` |
| Version | `v0.1` |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | PROPOSED — policy-only review required before any applicability evaluation |
| Change type | Structural |
| Dependencies | Normalized Fact and Canonical Identity Promotion Contract v0.1; nflverse Play-by-Play Field Semantics Evidence Contract v0.1; C-01 retained dictionary evidence; nflverse raw-evidence contracts |
| Current applicability status | `DOCUMENTATION_APPLICABILITY_UNCONFIRMED` |
| Implementation authorization | None. This policy authorizes no collection, inspection, comparison, mapping, or downstream implementation. |

## Decision Boundary

**Design decision:** When no direct upstream applicability statement exists,
ApexOS may consider only a separately evidenced and independently reviewed
schema-applicability equivalence result. This policy creates no equivalence
result and does not make C-01 applicable.

`DOCUMENTATION_APPLICABILITY_UNCONFIRMED` remains active until a future evidence
package satisfies every policy gate and receives an explicit, separately
versioned Architect applicability decision. Direct upstream applicability
evidence remains preferred and supersedes any indirect equivalence result if it
is later found. The absence of a direct statement is not permission to infer
semantic equivalence.

## Two-Sided Immutable Evidence Requirement

Every future evaluation requires exactly one immutable dictionary side and one
immutable release-asset side. Neither side may be substituted with a moving
branch, mutable reference, provider source, inferred relationship, or prior
evaluation for a different boundary.

```yaml
evidence_sides:
  dictionary_side:
    required:
      - "Pinned, byte-preserved dictionary artifact."
      - "Registration reference, snapshot ID, and SHA-256."
      - "Upstream repository, path, and immutable commit reference."
      - "Dictionary schema and declared grain evidence."

  release_asset_side:
    required:
      - "Approved immutable raw-evidence manifest for exactly one selected play_by_play_{season}.parquet release asset."
      - "Direct release-asset URL and release or version identity."
      - "SHA-256, or a documented nullable digest state."
      - "Byte count; source, retrieval, effective when available, and as-of timestamps."
      - "Parser version and structural schema evidence."
```

## Future Schema-Applicability Evidence Package

The following is a placeholder-only schema. It defines required evidence; it
does not define a comparison method, identifier normalization rule, type rule,
exception, threshold, or result.

```yaml
schema_applicability_evidence_package:
  evidence_package_id: "<stable-versioned-id>"
  version: "<semantic-version>"
  status: "<not_evaluated|candidate|reviewed|rejected>"

  dictionary_side:
    registration_reference: "<immutable-reference>"
    snapshot_id: "<immutable-snapshot-id>"
    sha256: "<sha256>"
    upstream_repository: "<owner/repository>"
    upstream_path: "<path>"
    upstream_commit: "<immutable-commit>"
    schema_grain_evidence: "<versioned-evidence-reference>"

  release_asset_side:
    manifest_reference: "<immutable-manifest-reference>"
    direct_release_asset_url: "<url>"
    release_version_identity: "<immutable-identity>"
    raw_sha256: "<sha256-or-documented-nullable-state>"
    raw_byte_count: "<byte-count>"
    source_timestamp: "<RFC3339-UTC-or-null>"
    retrieval_timestamp: "<RFC3339-UTC>"
    effective_timestamp: "<RFC3339-UTC-or-null>"
    as_of_timestamp: "<RFC3339-UTC>"
    parser_version: "<semantic-version>"
    structural_schema_evidence: "<versioned-evidence-reference>"

  exact_source_version_boundary: "<one-dictionary-pin-and-one-release-boundary>"
  structural_comparison_method_version: "<semantic-version>"
  identifier_comparison_policy_version: "<separately-versioned-policy>"
  type_representation_policy_version: "<separately-versioned-policy>"
  allowable_transport_serialization_differences: "<separately-versioned-policy>"
  dictionary_only_identifiers: "<observed-structural-output>"
  release_only_identifiers: "<observed-structural-output>"
  shared_identifiers: "<observed-structural-output>"
  duplicate_identifier_results: "<observed-structural-output>"
  nullability_availability_observation_status: "<observed-status>"
  source_field_semantic_status: "<unapproved|separately-approved-reference>"
  identity_status: "<not_applicable|unresolved|separately-approved-reference>"
  time_integrity_status: "<pass|fail|not_evaluated>"
  limitations: ["<limitation>"]
  integrity_digests: ["<digest-reference>"]
  independent_acceptance_evidence: "<reference>"
  architect_decision: "<missing|approved|rejected>"
  effective_timestamp: "<RFC3339-UTC-or-null>"
  supersession_reference: "<prior-or-successor-reference-or-null>"
```

## Structural-Only Comparison Boundary

A future comparison may inspect and compare schema-level metadata only after a
separate implementation or evidence-collection authorization. It may compare
identifier presence, uniqueness, declared broad type representation, and
source-version applicability only.

It must not inspect play rows, derive values, parse football outcomes, infer
event ownership, inspect player or team values, create records, calculate
aggregates, or claim field-level semantics. Shared identifiers do not prove
identical meaning, null behavior, attribution, correction behavior,
availability, or fitness for target construction.

No header-normalization rule, type-equivalence table, exception list,
compatibility threshold, or acceptance threshold is defined here. Each must be
separately versioned before future use.

## Source and Version Binding

- One dictionary immutable pin and one release-asset immutable manifest are
  required per evaluation.
- No cross-season, cross-release, cross-parser, cross-dictionary, or
  moving-branch generalization is permitted.
- A different release-asset variant, source contract, dictionary revision,
  parser version, release range, or field-availability boundary requires a
  separate evaluation.
- Later upstream revisions or asset corrections create new immutable evidence
  and new evaluation IDs; they never rewrite a prior result.

## Classifications

```yaml
schema_applicability_classification:
  - NOT_EVALUATED
  - STRUCTURAL_COMPARISON_INCOMPLETE
  - STRUCTURAL_IDENTIFIER_MISMATCH
  - STRUCTURAL_DUPLICATE_IDENTIFIER_DETECTED
  - STRUCTURAL_TYPE_REPRESENTATION_CONFLICT
  - STRUCTURAL_AVAILABILITY_UNKNOWN
  - STRUCTURAL_COMPARABILITY_LIMITED
  - SCHEMA_APPLICABILITY_SUPPORTED_FOR_DECLARED_BOUNDARY
  - SCHEMA_APPLICABILITY_REJECTED
```

`SCHEMA_APPLICABILITY_SUPPORTED_FOR_DECLARED_BOUNDARY`, if ever issued, is
structural applicability support only. It is not individual field-semantic,
null, attribution, ownership, identity, target, model, scoring, or downstream
use approval.

## Fail-Closed Gates and Reason Codes

A future result must reject or retain unconfirmed status when immutable source
pins, byte or digest proof, release manifest, schema evidence, identifier
policy, type policy, duplicate check, availability observation, version
applicability, independent evidence, or an explicit Architect decision is
absent, contradictory, stale, or unreviewable.

```text
DICTIONARY_EVIDENCE_MISSING
DICTIONARY_PIN_UNVERIFIED
DICTIONARY_DIGEST_MISMATCH
RELEASE_ASSET_MANIFEST_MISSING
RELEASE_ASSET_PIN_UNVERIFIED
RELEASE_ASSET_DIGEST_UNVERIFIED
RELEASE_SCHEMA_EVIDENCE_MISSING
STRUCTURAL_COMPARISON_METHOD_UNVERSIONED
STRUCTURAL_IDENTIFIER_POLICY_UNDECLARED
STRUCTURAL_TYPE_POLICY_UNDECLARED
STRUCTURAL_DUPLICATE_IDENTIFIER_DETECTED
STRUCTURAL_IDENTIFIER_MISMATCH
STRUCTURAL_TYPE_REPRESENTATION_CONFLICT
STRUCTURAL_AVAILABILITY_UNKNOWN
SOURCE_VERSION_APPLICABILITY_UNCONFIRMED
POST_DECISION_INFORMATION_DETECTED
INDEPENDENT_APPLICABILITY_EVIDENCE_MISSING
ARCHITECT_APPLICABILITY_DECISION_MISSING
PROVIDER_CONTAMINATION_DETECTED
```

## Time Integrity, Degraded Behavior, and Provider Boundary

Source-documentation retrieval time, release-asset retrieval time, release
effective time when available, as-of timestamp, evaluation time, and
decision-time cutoff remain separately represented. A schema evaluation cannot
use a later correction to claim earlier availability without a versioned
retrospective policy.

Degraded behavior retains evidence packages, manifests, structural comparison
outputs, limitations, reason codes, and prior candidate evidence separately;
visibly labels status; and does not overwrite prior results or create a false
statement of documentation applicability. It does not silently use a provider,
Provider Snapshot Mode, inferred field meaning, or downstream output as a
fallback.

Fantrax and all provider fantasy outputs, ranks, ADP, statuses, opponent
context, percentages, consensus, analyst forecasts, recommendations, UI
signals, provider identity evidence, and provider-derived schema or field
assumptions cannot influence a structural comparison, version applicability,
reconciliation, exception, or fallback.

## Capability Boundaries

K and D/O remain capability gaps. This policy does not imply kicker or D/O
identity, event, field-semantic, target, scoring, or projection support.

## Assumptions Register

| ID | Assumption / default | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-APP-001 | C-01 remains candidate evidence only. | Future semantic governance | P0 if retention is mistaken for applicability. | ApexOS Architect | Immediate and ongoing. |
| A-APP-002 | Direct documentation applicability remains absent. | Source applicability | P0 if linkage is mistaken for direct evidence. | ApexOS Architect | Before any evaluation. |
| A-APP-003 | Release-asset schema evidence is not yet collected. | Future structural evaluation | P0 if a schema result is inferred. | ApexOS Architect | Before collection. |
| A-APP-004 | Structural comparability cannot establish semantic equivalence. | Normalization policy | P0 if identifiers become semantic approval. | ApexOS Architect | Before any decision. |
| A-APP-005 | Schema support cannot approve individual fields or downstream use. | Projection program | P0 if structural support leaks into implementation. | ApexOS Architect | Immediate and ongoing. |
| A-APP-006 | Source corrections and revisions require new evaluation. | Evidence revision control | P1 if prior lineage is rewritten. | ApexOS Architect | Before revision use. |
| A-APP-007 | Provider data cannot fill evidence gaps. | Provider-contamination boundary | P0 if independent authority is breached. | ApexOS Architect | Immediate and ongoing. |
| A-APP-008 | K and D/O remain unsupported capability gaps. | Entity capability design | P1 if unsupported entities are implied. | ApexOS Architect | Before any K or D/O work. |

## Acceptance Criteria

- Exactly one documentation-only policy file is added.
- `DOCUMENTATION_APPLICABILITY_UNCONFIRMED` remains active pending a later,
  independently evidenced Architect decision.
- Each future evaluation requires immutable dictionary and release-asset sides.
- Future comparison is structural-only and prohibits raw-row inspection, field
  selection, semantics, target derivation, and downstream behavior.
- Version binding, classifications, fail-closed gates, reason codes,
  time-integrity rules, independent evidence, and degraded behavior are
  explicit.
- Provider contamination is prohibited; no provider fallback exists.
- K and D/O remain capability gaps.
- No parser, ingestion, normalization, canonical identity, target, model,
  scoring, artifact, board, optimizer, recommendation, test, configuration,
  dependency, runtime, or external-write behavior is authorized.
- The PR is open, non-draft, documentation-only, and unmerged.

## Builder Handoff Boundary

This policy authorizes no raw release-asset retrieval, schema inspection,
schema comparison, raw-record access, parser change, normalization, canonical
identity, field-semantic mapping, feature, target extraction, model,
evaluation, scoring, artifact, board, optimizer, recommendation, test,
configuration, dependency, or external write.

A later handoff must name the exact dictionary evidence reference and exact
selected immutable release-asset manifest before any structural evaluation may
begin.

## Change Log

- `v0.1` — Establishes a fail-closed, structural-only dictionary-to-release
  schema applicability policy after the absence of a direct upstream
  applicability statement and before any individual field-semantic decision.
