# ApexOS nflverse Play-by-Play Upstream Documentation Registration v0.1

## Metadata

| Field | Value |
|---|---|
| Artifact name | APEXOS-NFLVERSE-PLAY-BY-PLAY-UPSTREAM-DOCUMENTATION-REGISTRATION |
| Version | v0.1 |
| Owner | Devin Tyler / ApexOS Principal Product and Systems Architect |
| Status | EVIDENCE RETAINED — no individual field semantic approved |
| Change type | Structural evidence registration |
| Decision ID | D-NORM-SEMANTICS-001 |
| Semantic authority contract | contracts/normalization/apexos-nflverse-play-by-play-field-semantics-evidence-contract-v0.1.md v0.1 |
| Collection authorization | APEXOS-NFLVERSE-UPSTREAM-DOCUMENTATION-EVIDENCE-COLLECTION-018 |

## Registration Decision

Version-pinned upstream nflverse play-by-play documentation is the candidate
semantic authority. The locally retained repository snapshot is immutable audit
evidence only; it cannot itself approve a raw-field semantic, fact, identity,
feature, target, forecast, score, artifact, rank, value, availability state,
optimizer output, board output, recommendation, or implementation.

This registration approves no individual raw-field meaning, null convention,
event attribution rule, ownership rule, timing rule, correction rule,
normalized fact, canonical identity, feature, target, model, score, or
recommendation. It does not interpret, summarize, or promote the retained
upstream text.

## Upstream Provenance

| Field | Observed value |
|---|---|
| Upstream repository owner/name | nflverse/nflreadr |
| Canonical upstream URL | https://github.com/nflverse/nflreadr |
| Upstream document repository path | vignettes/dictionary_pbp.Rmd |
| Canonical document URL | https://github.com/nflverse/nflreadr/blob/d072c08492067b578f27e562b6cc9c9e3b8589c3/vignettes/dictionary_pbp.Rmd |
| Read-only retrieval URL | https://raw.githubusercontent.com/nflverse/nflreadr/d072c08492067b578f27e562b6cc9c9e3b8589c3/vignettes/dictionary_pbp.Rmd |
| Immutable upstream version pin | d072c08492067b578f27e562b6cc9c9e3b8589c3 |
| Pin type | Git commit SHA |
| Documentation retrieval timestamp | 2026-08-30T11:35:34.8176950Z |
| Documentation publication/effective timestamp | unknown |
| Retrieval mechanism | Read-only HTTPS GET using curl.exe with HTTPS-only, fail-on-error, and location-following options |
| Response content type | text/plain; charset=utf-8 |
| Source-provider / rights-or-terms reference | https://github.com/nflverse/nflreadr/blob/d072c08492067b578f27e562b6cc9c9e3b8589c3/LICENSE.md — reference retained; interpretation requires separate review |
| Upstream origin status | Confirmed through the nflverse/nflreadr GitHub repository and immutable Git commit pin |

## Immutable Local Audit Evidence

| Field | Value |
|---|---|
| Retained snapshot path | docs/evidence/nflverse-play-by-play-upstream-documentation-snapshot-v0.1.txt |
| Snapshot byte count | 648 |
| Calculated SHA-256 | fed29e04b0035254874cee213649ec0e3159bea916d1b7464f422cdb30708b5f |
| Digest file | docs/evidence/nflverse-play-by-play-upstream-documentation-snapshot-v0.1.sha256 |
| Local immutable evidence snapshot ID | nflverse-nflreadr-d072c08492067b578f27e562b6cc9c9e3b8589c3-dictionary-pbp-rmd-fed29e04b0035254874cee213649ec0e3159bea916d1b7464f422cdb30708b5f |
| Retention form | Exact first retrieved response body; retrieval metadata is retained in this registration, not inserted into the snapshot |
| Repeat retrieval result | Matching digest: fed29e04b0035254874cee213649ec0e3159bea916d1b7464f422cdb30708b5f |

## Retrieval Integrity

The retained snapshot is the exact first HTTPS response body. No normalization,
paraphrase, redaction, reformatting, selective excerpt, or source merge was
performed.

Verification command:

    sha256sum -c docs/evidence/nflverse-play-by-play-upstream-documentation-snapshot-v0.1.sha256

The second read-only HTTPS GET used the same immutable upstream pin and
produced the same SHA-256 digest. RETRIEVAL_REPEAT_DIGEST_MISMATCH was not
observed.

Whitespace validation evidence: the required default `git diff --check`
reports expected external-source formatting at
`docs/evidence/nflverse-play-by-play-upstream-documentation-snapshot-v0.1.txt:21`:
`trailing whitespace`. The snapshot remains byte-preserved because its digest
matches the independent repeat retrieval. No whitespace finding is permitted
in this authored registration or in the checksum file.

## Bounded Applicability Assessment

| Field | Status |
|---|---|
| Intended historical release-asset family | play_by_play_{season}.parquet |
| Source release-asset applicability | DOCUMENTATION_APPLICABILITY_UNCONFIRMED |
| Applicability assessment | The retained artifact is preserved only as candidate documentation evidence. This registration does not assert that it explicitly applies to the intended historical release-asset family. |
| Parser applicability | unknown |
| Source-contract applicability | unknown |
| Individual field applicability | No field is selected or approved. |

Because applicability is unconfirmed, this registration is not semantic
authority for any individual field. It cannot support a semantic mapping,
normalized fact, canonical identity, feature, target, model, scoring input,
artifact, value, availability output, optimizer result, board, or
recommendation.

## Evidence and Semantic Boundary

The retained snapshot may contain upstream raw text. This registration makes no
field-level interpretation of that text and records no individual field names,
event attribution, null behavior, ownership behavior, correction behavior,
timing behavior, or semantic mapping.

Raw parquet column names, types, isolated records, screenshots, inferred
football knowledge, and downstream expected outputs remain structural or
candidate-question evidence only. They cannot establish semantics,
attribution, null rules, correction behavior, or availability behavior.

K and D/O remain separate capability gaps. This registration implies no kicker
or D/O field semantics, mapping, target, or projection support.

## Provider-Contamination Prohibition

In apexos_projection mode, no provider point total, projection, rank, ADP,
status, opponent context, percentage, consensus, analyst output,
recommendation, or UI signal may establish or supplement raw-field meaning,
null behavior, attribution, ownership, identity, timing, correction,
transformation, or fallback behavior. Provider Snapshot Mode remains a
separate, explicitly labeled authority boundary. Display-only comparison is
permitted only after independent ApexOS output is frozen.

## Visible Status and Fail-Closed Outcome

Required reason-code vocabulary:

- UPSTREAM_DOCUMENTATION_UNAVAILABLE
- UPSTREAM_DOCUMENTATION_UNPINNED
- UPSTREAM_DOCUMENTATION_VERSION_UNVERIFIED
- UPSTREAM_ORIGIN_UNCONFIRMED
- LOCAL_EVIDENCE_SNAPSHOT_MISSING
- LOCAL_EVIDENCE_DIGEST_MISSING
- LOCAL_EVIDENCE_DIGEST_MISMATCH
- DOCUMENTATION_APPLICABILITY_UNCONFIRMED
- TERMS_OR_RIGHTS_REFERENCE_MISSING
- RETRIEVAL_REPEAT_DIGEST_MISMATCH
- PROVIDER_CONTAMINATION_DETECTED

Status is visible and fail-closed: missing pin, failed retrieval, unreadable
content, missing digest, digest mismatch, missing rights or terms reference,
upstream-origin uncertainty, or unknown applicability must record the relevant
reason code and cannot claim an approved semantic source. This registration
retains DOCUMENTATION_APPLICABILITY_UNCONFIRMED; no individual semantic approval
is made.

## Assumptions and Limitations

| ID | Assumption / limitation | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|
| A-EVID-001 | Documentation may not apply to the intended historical release asset. | Future semantic mapping | P0 if candidate evidence is treated as field authority. | ApexOS Architect | Before individual semantic approval. |
| A-EVID-002 | Retention does not establish field semantics. | Normalization | P0 if audit evidence becomes an inferred mapping. | ApexOS Architect | Before mapping work. |
| A-EVID-003 | Publication/effective time is unavailable. | Time integrity | P1 if availability is inferred. | ApexOS Architect | Before temporal approval. |
| A-EVID-004 | Upstream documentation may change after the retained pin. | Evidence revision | P1 if revisions overwrite prior evidence. | ApexOS Architect | Before new-version use. |
| A-EVID-005 | Rights or terms may require separate review. | Source governance | P0 if the reference is misread as authorization. | ApexOS Architect | Before use beyond evidence retention. |
| A-EVID-006 | No local implementation authorization follows. | Projection program | P0 if evidence collection becomes implementation approval. | ApexOS Architect / Builder | Immediate and ongoing. |
| A-EVID-007 | K and D/O remain unsupported capability gaps. | Entity and target design | P1 if this evidence implies unsupported implementation. | ApexOS Architect | Before K or D/O work. |

## Acceptance Criteria

This registration is acceptable only when all criteria are true:

- Exactly three evidence-only files are added by this PR.
- The upstream origin and immutable version pin are retained.
- The local snapshot is byte-preserved and its SHA-256 verifies.
- Provenance includes collection method, timestamp, byte count, digest,
  rights/terms reference, and bounded applicability status.
- The registration contains no raw-field, event, attribution, null,
  correction, timing, identity, or semantic mapping interpretation.
- Applicability and unavailable values are recorded as unknown or failed, not
  inferred.
- Provider contamination is absent.
- No product behavior, parser, raw-data processing, normalization, identity,
  feature, target, model, scoring, artifact, board, optimizer,
  recommendation, test, configuration, dependency, or runtime behavior
  changes.
- The PR remains open, non-draft, evidence-only, and unmerged.

## Builder Handoff Boundary

This evidence collection authorizes no parser, raw-evidence, normalization,
canonical identity, field-semantic mapping, feature, target, model,
evaluation, scoring, artifact, board, optimizer, recommendation, test,
configuration, dependency, or external-write behavior beyond this evidence-only
branch, commit, and PR creation.

A separately approved future handoff for evidence collection or mapping work
must identify the exact authorized upstream URL and immutable version pin,
rights or terms reference, retention destination, allowed paths, evidence
commands, acceptance criteria, stop conditions, and reviewer focus.

## Change Log

- v0.1 — Structural evidence registration introduced. Retains one version-pinned
  upstream documentation response as immutable audit evidence after raw
  evidence and before source-field semantic mapping, normalized facts, or
  football-event target derivation.
