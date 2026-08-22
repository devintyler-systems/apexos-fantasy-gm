# Data Source and Connector Register

**Artifact:** `data_source_connector_register`
**Version:** 1.5
**Owner:** Devin Tyler (Architect)
**Status:** APPROVED sources marked; all others BLOCKED pending review
**Depends On:** League Rules Contract v0.3
**Unlocks:** Projection Artifact Contract, PRV Calculator, backtest work (B-17)
**Created:** 2026-08-09
**Last Updated:** 2026-08-21 (v1.5 -- calibration: added Section 5, Candidate Connector
Assumptions Register, with entries AR-C01 (ESPN public endpoints) and AR-C02 (Yahoo
Fantasy Sports API). Neither connector is approved, implemented, or authorized for use
in recommendations. No approved source, schema, or build-ticket dependency changed.
See Decision Ledger v3.0.)

---

## 1. Decision Statement

No data source or connector is used in any ApexOS module until it is recorded here with
purpose, fields, auth, rate limits, terms, freshness, fallback, and read/write permissions.

---

## 2. Source Register (condensed -- see prior versions in git history for full detail on 2.1-2.6)

### 2.1 nflverse / nflverse-data (direct GitHub release assets) -- APPROVED (v1.4, supersedes nfl_data_py wrapper)

| Field | Value |
|---|---|
| Purpose | Historical play-by-play data (2016-2025 window minimum) for xTD derivation per Projection Artifact Contract Section 5 | `confirmed evidence` |
| Access method | Direct HTTP GET against GitHub Releases API (`api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp`); select exactly one asset named `play_by_play_{season}.parquet` with `state == "uploaded"`; download only the returned `browser_download_url`, never a constructed URL | `design decision` |
| Auth | None required -- public repository, public release assets | `confirmed evidence` |
| Rate limits | GitHub REST API: 60 req/hr unauthenticated per IP, 5,000 req/hr if authenticated -- sufficient for a one-time-per-season discovery + download pattern | `confirmed evidence` |
| Terms | nflverse-data is a public open-data project; no license restriction identified against analytical/personal use | `assumption` |
| Freshness | Release `pbp` (release ID 58152862) is updated in place per season as data is finalized -- release timestamp is NOT a freshness signal. B-06 treats the downloaded-bytes SHA-256 as the authoritative freshness/identity signal, with provider-reported digest stored as a nullable secondary field (older season assets may lack it) | `confirmed evidence` |
| Fallback | On discovery failure (zero or multiple exact asset matches, non-2xx response, redirect outside `github.com`/`api.github.com`), B-06 returns `cached_valid` if an independently valid prior revision exists, otherwise `failed` -- never a false current-status claim | `design decision` |
| Read/write | Read-only. ApexOS never writes to this source | `design decision` |
| Supersedes | `nfl_data_py` Python wrapper package. PROHIBITED as of v1.4 -- the package is archived/read-only upstream. No `nfl_data_py` import, dependency declaration, or documentation reference may appear anywhere in this repository as of this version | `confirmed evidence` |

### 2.1a nflfastR / nflreadr (R) -- NOT ADDED, redundant with 2.1
### 2.2 Vegas Team Implied Totals (generic manual) -- APPROVED, superseded in practice by 2.7/2.8
### 2.3 SPAMML 2025 Draft Guide CSV -- APPROVED, calibration only
### 2.4 Pro Football Focus (PFF) -- DEFERRED, not approved
### 2.5 SPAMML Custom League Platform -- no API exists, manual entry permanent
### 2.6 Fantrax -- DEFERRED, Phase 2 candidate
### 2.7 Sharp Football Analysis (2026 projected PPG) -- APPROVED
### 2.8 VegasInsider (2026 win totals) -- APPROVED

### 2.9 TeamRankings.com -- APPROVED (calibration reference only, NOT a 2026 input)

| Field | Value |
|---|---|
| Purpose | 2025 actual team AND player statistics -- team PPG, opponent PPG, FG attempts/game, kicking PPG, red zone attempts/scores/percentage, player total TDs, player games-with-TDs, player pct-of-games-with-TDs |
| Access method | Manual CSV export from teamrankings.com team-stats and player-stats pages; user-supplied | `design decision` |
| Approved page paths | `teamrankings.com/nfl/stats/` (team stats), `teamrankings.com/nfl/player-stats/` (player stats) -- both now explicitly registered as approved source pages, added to search-priority Links across all three ApexOS spaces | `design decision`, 2026-08-10 |
| Terms of use | Publicly published statistics referenced for personal analytical use | `assumption` |
| Freshness | Static -- final 2025 season figures, will not change | `confirmed evidence` |
| Role in ApexOS | Backtest/calibration baseline per TouchdownOS Section 5.4 doctrine. `teamrankings_2025_kicking_ppg.csv` reports actual 2025 kicker points at SPAMML's exact 3pt-FG/1pt-PAT scoring -- near-direct validation set. NEW: `playerrankings_2025_games_with_TDs.csv` and `playerrankings_2025_pct_games_with_TDs.csv` add a consistency/reliability dimension beyond raw TD total -- a player with fewer total TDs but a higher pct-of-games-with-TD may represent a more draftable floor for a no-bench league where every start matters. | `evidence-backed inference` |

### 2.10 PlayerRankings 2025 Total TDs -- APPROVED (calibration reference / backtest ground truth)

| Field | Value |
|---|---|
| Update | File replaced 2026-08-10: original repo copy was truncated to ~10 rows for readability; full ~90-row dataset now committed at `data/raw/2025_actuals/playerrankings_2025_total_TDs.csv` | `design decision` |
| Companion files (NEW) | `playerrankings_2025_games_with_TDs.csv` (count of games with at least one TD), `playerrankings_2025_pct_games_with_TDs.csv` (consistency rate) -- both same source/terms/freshness as the total-TDs file | `design decision` |
| Role in ApexOS | Backtest ground truth per TouchdownOS Gate 2 doctrine. The games-with-TDs and pct-of-games files specifically support a future PRV/projection refinement: distinguishing boom/bust total-TD accumulation from weekly-reliable scoring, which matters more in a no-bench league where a single blank week cannot be covered by a bench substitution. Flagged as a candidate feature for Individual Efficiency layer (Projection Artifact Contract Section 4) once B-17 backtesting begins -- not yet incorporated into any live formula. | `evidence-backed inference` |

---

## 3. Explicitly Blocked Patterns (unchanged)

- No source is ever given write access to make picks, waiver claims, lineup changes, or trades.
- No source's data may be used past its declared `as_of_timestamp` in any frozen recommendation.
- No source is treated as live/current without a passing freshness check.
- 2025 actuals must NEVER be blended into a 2026 projection as if current-season data -- backtest inputs only.
- `nfl_data_py` (Python wrapper package) is explicitly PROHIBITED as of v1.4 -- see 2.1 above. Any code, dependency file, or documentation referencing it is non-compliant and must be corrected.

---

## 4. Decision Ledger Entry

Data completeness improved for backtest/calibration work (unlocks B-17 more fully). No change
to any live 2026 projection formula -- these are reference/validation files only. New idea
surfaced (games-with-TDs as a consistency signal) is flagged as a candidate, not adopted,
pending the same definition/source/validation/baseline/acceptance-test process required
for any promoted idea per shared doctrine.

**v1.4 addition (2026-08-11):** Source authority for nflverse play-by-play migrated from the
`nfl_data_py` Python wrapper to direct nflverse-data GitHub release assets, per the B-06 v0.2
ingestion contract (`contracts/ingestion/nflverse-play-by-play-ingestion-contract-v0.2.md`).
This is a structural change, not calibration -- it changes the approved access method, not a
weight or threshold. Verified against the live `pbp` release (release ID 58152862) before
approval: `play_by_play_{season}.parquet` assets confirmed present for 2016-2025, no 2026 asset
exists, and provider-reported digests are absent on pre-2019 season assets (confirming the
nullable-digest design requirement). Full verification trail and dependent-document list in
`docs/decision_ledger.md` Version 2.9.

**v1.5 addition (2026-08-21):** Added Section 5 (Candidate Connector Assumptions Register)
with entries for ESPN public endpoints (AR-C01) and Yahoo Fantasy Sports API (AR-C02).
Calibration-only change. Neither connector is approved, implemented, or authorized for use
in any recommendation path. See Decision Ledger v3.0.

---

## 5. Candidate Connector Assumptions Register

These entries are discovery records only. `CANDIDATE` status does not authorize adapter
implementation, production retrieval, use in recommendations, or a claim that ApexOS supports
the associated platform. Promotion requires a versioned connector contract and independent
verification of provider capability, terms, authentication, rate limits, freshness, fields,
identity mapping, fallback, and degraded behavior.

| ID | Candidate | Status | Intended decision/workflow | Default / current boundary | Affected module | Risk | Owner | Decision deadline |
|---|---|---|---|---|---|---|---|---|
| AR-C01 | `pseudo-r/Public-ESPN-API` / ESPN public endpoints | CANDIDATE — post-MVP only | Read-only roster, matchup, standings, scoring, and public league-state discovery for an ESPN-hosted league after ESPN platform support is separately approved | Do not retrieve or use ESPN data. SPAMML has no ESPN integration and remains permanent manual entry. No write operations in scope. | Future platform adapter; canonical identity resolution; league rules import; roster-state evidence | HIGH — endpoints are undocumented and unofficial; provider can change behavior without notice; rate limits, private-league support, and permitted-use posture require independent verification | Architect | Before any ESPN league is accepted as a supported platform |
| AR-C02 | `uberfastman/yfpy` / Yahoo Fantasy Sports API | CANDIDATE — post-MVP only | Read-only league rules, roster state, matchup, standings, and player-availability retrieval for a Yahoo-hosted league after OAuth and supported-resource review | Do not retrieve or use Yahoo data. It is not a Fantrax connector and does not sync SPAMML or its Fantrax mirror. No write operations in scope. | Future platform adapter; OAuth credential boundary; canonical identity resolution; league rules import; roster-state evidence | MEDIUM-HIGH — OAuth token storage/rotation, API quota, and resource coverage need independent verification; wrapper must not become a core-schema dependency | Architect | Before any Yahoo league is accepted as a supported platform |

### 5.1 AR-C01 — ESPN Candidate Promotion Gate

**Claim status:** `unknown` pending independent provider review.

| Required evidence | Required result before promotion |
|---|---|
| Purpose and supported workflow | Exact supported ESPN league types, public/private boundary, and read-only user workflow documented |
| Fields and source mapping | Endpoint-to-raw-evidence mapping identifies league settings, roster, schedule, matchup, standings, player, and transaction fields; no provider fields enter the canonical model directly |
| Authentication | Public versus private league behavior and any cookies, tokens, or unsupported mechanisms explicitly documented; unsupported methods prohibited |
| Rate limits and resilience | Measured or documented request ceiling, timeout, retry/backoff, caching policy, and circuit-breaker behavior defined |
| Terms and data rights | Permitted-use assessment recorded; unresolved terms risk blocks approval |
| Freshness | Retrieval timestamp, observed update cadence, effective-time semantics, and stale threshold defined per resource |
| Canonical identity | ESPN player/team IDs map through non-destructive canonical identity resolution; unresolved identities quarantined |
| Fallback | Cached valid artifact plus manual roster/pick entry available; adapter failure never blocks user from operating ApexOS |
| Degraded mode | UI exposes provider unavailable, last successful retrieval, artifact age, affected decision scope, and manual-entry path; no current-state claim shown after failure |
| Safety | Adapter has no write methods, no credential harvesting; fixture-backed contract tests cover endpoint shape drift, malformed payloads, stale data, and identity conflicts |

**Promotion blocker:** The reference documentation repository (`pseudo-r/Public-ESPN-API`)
documents observed endpoint behavior but is not authority that ESPN permits, guarantees,
or will maintain that behavior. Approved connector contract must bind to independently
verified ESPN API capability, not to the reference repository's findings.

### 5.2 AR-C02 — Yahoo Candidate Promotion Gate

**Claim status:** `evidence-backed inference` that Yahoo provides an official developer API;
exact usable resources and operational constraints remain `unknown` until verified.

| Required evidence | Required result before promotion |
|---|---|
| Purpose and supported workflow | Exact Yahoo league types and read-only workflows documented; no inference that Yahoo data represents SPAMML or Fantrax |
| Fields and source mapping | API-resource-to-raw-evidence mapping identifies league settings, scoring, roster, draft, matchup, transaction, and player-status coverage |
| OAuth | Authorization flow, required scopes, secure local credential handling, refresh/expiration behavior, revocation path, and explicit user consent documented |
| Rate limits and resilience | Current Yahoo quota, retry/backoff, caching, timeout, and token-refresh failure behavior defined |
| Terms and data rights | Yahoo developer terms, app-registration requirements, attribution requirements, and permitted-use constraints recorded |
| Freshness | Resource-specific retrieval cadence, effective-time meaning, artifact timestamping, and stale thresholds defined |
| Canonical identity | Yahoo player/team keys route through canonical identity mapping; aliases and unresolved entities remain inspectable |
| Fallback | Cached valid artifact and manual entry available for league rules, rosters, draft state, and player availability |
| Degraded mode | OAuth failure, expired token, quota exhaustion, provider outage, and partial payload states show stale status and preserve manual operation |
| Safety | Adapter remains read-only; no lineup, waiver, trade, roster, or draft-pick write capability exists; fixture-backed tests cover token expiry, quota response, missing fields, stale data, and identity collisions |

**Promotion blocker:** `yfpy` is a convenience wrapper, not an architectural dependency.
The approved connector contract must bind ApexOS to Yahoo's verified API behavior and
raw evidence contract, not to the wrapper's model classes or field names.
