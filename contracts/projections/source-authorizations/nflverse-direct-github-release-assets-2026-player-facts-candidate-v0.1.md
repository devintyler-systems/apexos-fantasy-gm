# nflverse Direct GitHub Release Assets — 2026 Player Facts Candidate v0.1

**Artifact:** `nflverse_direct_github_release_assets_2026_player_facts_candidate`
**Version:** `0.1`
**Status:** CANDIDATE ONLY — NOT APPROVED FOR USE
**Owner:** ApexOS Architect
**Scope:** Documentation-only candidate record; no implementation authorization

## 1. Candidate purpose and boundary

Direct GitHub release assets published by nflverse are a candidate only for
historical player/team factual evidence and canonical-reference support. This
record neither asserts field coverage nor authorizes use of any data. It is not
an approval for 2026 player-level evidence.

The proposed future access method is direct GitHub release assets, read-only
only. No provider retrieval, network call, API client, parser, credential,
cache, or implementation is authorized by this record.

## 2. Explicit exclusions

This candidate is not authorized for provider retrieval, network calls, 2026
live roster claims, injuries, availability, rankings, ADP, analyst projections,
scoring, PRV, roster fit, recommendations, or live artifact creation. It does
not authorize an endpoint, external write, player projection, optimizer, or
production behavior.

Rankings, ADP, and analyst projections remain benchmark-only roles and are not
eligible evidence inputs. A historical/B-06 approval or use of nflverse does
not automatically authorize 2026 player-level evidence under this record.

## 3. Required later approval package

Before any use, a later source-specific approval package must independently
verify and record all of the following; no value is asserted by this candidate
record:

- purpose and bounded factual use case;
- exact field inventory and source-to-canonical mapping;
- source provider and exactly one locator (`source_url` or
  `provider_record_id`);
- provider terms and license verification;
- authentication posture and rate-limit status;
- exact GitHub release and asset identity;
- local SHA-256 of the supplied bytes and parser version;
- UTC retrieval, effective, and artifact as-of timestamps;
- canonical player/team identity coverage and ambiguity handling;
- a separately approved source-specific freshness policy;
- fallback and degraded-mode behavior; and
- read/write posture confirming read-only operation and no external writes.

The package must be approved before implementation authorization. It must not
infer provider terms, license, field coverage, rate limit, freshness SLA, or
current status from this candidate record.

## 4. Fail-closed conditions

Missing or ambiguous canonical identity, hash mismatch, missing provenance,
post-as-of evidence, unapproved source status, or a benchmark-only role fails
closed. A stale or incomplete condition must surface its status and known
limitations without a false current claim. This candidate record is not itself
the approval package and cannot satisfy any fail-closed gate by declaration.

## 5. U08 and league scope

League Rules v0.7 resolves U08 for SPAMML 2026 only: “SPAMML 2026 is a redraft
league with no keepers and no dynasty behavior.” That resolution satisfies the
U08 prerequisite only for SPAMML 2026 and must not be generalized to another
league, season, or format. It does not approve this candidate source.

## 6. Non-authorization statement

No live evidence, provider/API/network retrieval, live projection artifact,
scoring, PRV, availability, roster-fit, recommendation, or external-write
behavior is authorized by this candidate-only record.
