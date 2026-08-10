# Data Source and Connector Register

**Artifact:** `data_source_connector_register`
**Version:** 1.0
**Owner:** Devin Tyler (Architect)
**Status:** APPROVED sources marked; all others BLOCKED pending review
**Depends On:** League Rules Contract v0.2
**Unlocks:** Projection Artifact Contract (source fields), Kicker Model, D/O Model
**Created:** 2026-08-09

---

## 1. Decision Statement

No data source or connector is used in any ApexOS module until it is recorded here with purpose, fields, auth, rate limits, terms, freshness, fallback, and read/write permissions. This register is the single approval gate. The Projection Artifact Contract may only reference sources marked APPROVED below.

---

## 2. Source Register

### 2.1 nflverse / nfl_data_py — **APPROVED (read-only, historical + reference)**

| Field | Value |
|---|---|
| Purpose | Historical play-by-play, weekly player stats, rosters, snap counts, NGS stats, schedules, scoring lines, draft picks — primary source for xTD constant derivation and role/opportunity features |
| Access method | Python package `nfl_data_py` (pip install), pulls from `nflverse/nflverse-data`, `nflverse/nfldata`, `dynastyprocess/data` GitHub repos | `confirmed evidence` [web:19][web:20]
| Auth | None required — public GitHub-hosted data, no API key | `confirmed evidence` [web:20]
| Rate limits | None documented — data is static files (Parquet/CSV) hosted on GitHub, not a live API | `confirmed evidence` [web:20]
| Terms of use | R/Python code is MIT licensed (open source). Underlying NFL data "belong to their respective owners, and are governed by their terms of use" — redistribution of raw NFL data for commercial use not explicitly cleared; personal/analytical use is the established norm in the community | `confirmed evidence` [web:20] / `assumption` on commercial-use boundary — revisit if ApexOS is ever monetized externally |
| Freshness | Automated via GitHub Actions; play-by-play and weekly stats updated within ~24-48h of games during season; historical data back to 1999 (pbp) | `confirmed evidence` [web:20][web:24] |
| Historical depth | Play-by-play: 1999–present. Weekly/seasonal stats, rosters, combine, draft picks, scoring lines also available | `confirmed evidence` [web:19][web:24] |
| Fallback if unavailable | Cached local Parquet snapshot from last successful pull; system flags `data_freshness_status: stale` and continues with last-known-good data. No live dependency during draft. | `design decision` |
| Read/write | Read-only. No write path exists or is needed. | `confirmed evidence` |
| Role in ApexOS | Primary source for: field-position xTD rate derivation (Step 2 of TD framework), role/opportunity features (red zone carries, target share, routes per dropback), 3-year historical decay baseline | `design decision` |

**Approval condition met:** Free, no auth, no rate limit, MIT-licensed code, established use for exactly this purpose (fantasy/analytics projection modeling) throughout the public nflverse community.

---

### 2.2 Vegas Team Implied Totals / Odds Consensus — **APPROVED (manual ingest only)**

| Field | Value |
|---|---|
| Purpose | Team implied point totals, win/loss over-unders — the Offensive Scheme Quality layer (25% weight) in the TD projection framework |
| Access method | Manual CSV export from a consensus odds aggregator (e.g., the 2025 SPAMML draft guide already contains a "Vegas Total TDs CON" column as precedent). No live odds API contracted. | `design decision` |
| Auth | N/A — manual entry, no API key held | — |
| Rate limits | N/A — no live calls | — |
| Terms of use | Not established for any specific paid odds API. Manual reference of publicly displayed consensus lines for personal, non-commercial analytical use is the interim posture. **Any live odds API integration is BLOCKED until its specific ToS is reviewed here.** | `assumption` — flagged for review before Phase 3 (market adapter, per TouchdownOS blueprint) |
| Freshness | As of manual entry timestamp only — no live refresh | `design decision` |
| Fallback | If no fresh line available at ingest time, field is marked `null` and flows through as `data_freshness_status: incomplete` — never silently defaulted | `design decision` |
| Read/write | Read-only, manual | — |
| Role in ApexOS | Feeds `team_expected_offensive_tds` and `projected_team_td_environment` driver in the canonical player projection contract | `design decision` |

**Approval condition met for MVP:** No commercial odds API is contracted or required for draft-day projections; manual entry of public consensus numbers is sufficient and lowest-risk.

---

### 2.3 SPAMML 2025 Draft Guide CSV (in-repo) — **APPROVED (calibration reference only — NOT a 2026 projection source)**

| Field | Value |
|---|---|
| Purpose | Historical calibration check only — compare ApexOS-derived 2025 projections against ESPN/LineupExperts/DraftSharks consensus retroactively | `design decision` |
| Access method | Already committed to repo at `data/raw/spamml_2025_draft_guide_overall.csv` | `confirmed evidence` |
| Terms of use | User-compiled aggregate of public consensus rankings for personal league use — no redistribution rights claimed or needed since it stays in a private repo | `assumption` |
| Freshness | Static, 2025 season — explicitly NOT used as a 2026 input | `design decision` |
| Role in ApexOS | Backtest / calibration baseline only, per TouchdownOS doctrine ("full model must outperform relevant baselines out of sample before treated as useful") | `design decision` |

---

### 2.4 Pro Football Focus (PFF) — **DEFERRED, NOT APPROVED**

| Field | Value |
|---|---|
| Purpose (if approved) | Route participation, TPRR, red-zone target share, scheme/coaching grades — would strengthen Individual Efficiency (20%) and Offensive Scheme Quality (25%) layers |
| Access method | Subscription-gated web platform; no public documented API for third-party programmatic ingestion at standard subscription tiers | `confirmed evidence` [web:18][web:23] |
| Auth | Account login required; subscription fee billed at signup and recurring intervals (monthly/annual) | `confirmed evidence` [web:18][web:26] |
| Rate limits | Unknown — no public API rate-limit documentation found; likely web-scraping-only access at standard tiers, which raises ToS risk | `unknown` |
| Terms of use | PFF Terms of Use govern the Service Subscription Fee and account terms; **does not confirm any right to programmatic scraping or redistribution of graded data** for building a derivative fantasy tool | `confirmed evidence` [web:18] / `unknown` on scraping/redistribution permissions |
| Freshness | Weekly updated per public info | `confirmed evidence` |
| Fallback | N/A — not integrated | — |
| Read/write | Would be read-only if approved | — |

**Decision: DEFERRED.** Cost ($ subscription) and unresolved scraping/ToS risk are not justified for a draft MVP that has zero live users beyond Devin. Revisit only if Phase 2 in-season module needs TPRR/scheme-grade features beyond what nflverse computes, AND a documented API or licensed data-export path is confirmed. `design decision`

---

### 2.5 SPAMML Custom League Platform — **NOT APPROVED, NO CONNECTOR EXISTS**

| Field | Value |
|---|---|
| Purpose | Would provide live draft pick sync, roster state, transaction history if an API existed |
| Access method | None — confirmed custom manual site with no API, per league rules contract v0.2 | `confirmed evidence` |
| Terms of use | N/A — no integration possible |
| Fallback / degraded behavior | **This IS the default mode, not a fallback.** All draft state entry is manual for the life of this league engagement. No sync attempt is ever made. UI must never imply live sync capability exists. | `design decision` |

---

### 2.6 Fantrax (Devin's personal mirror league) — **DEFERRED, PHASE 2 CANDIDATE**

| Field | Value |
|---|---|
| Purpose | Devin manually mirrors SPAMML rosters/transactions here for personal tracking convenience |
| Access method | Fantrax has a documented read-only API for league/roster data in some tiers — NOT yet validated for this specific account/league | `unknown` — requires dedicated review before any integration attempt |
| Terms of use | Unknown — not reviewed | `unknown` |
| Role in ApexOS | Potential Phase 2 read-only sync target for season-long roster tracking, SINCE Devin already re-enters data there manually. Would reduce double-entry, not add new capability. | `design decision` |
| Decision | **Do not build any Fantrax connector until this register entry is completed with auth, rate limits, terms, and confirmed read-only scope.** Flagged as the single most promising Phase 2 integration since it's already part of Devin's workflow. | `design decision` |

---

## 3. Explicitly Blocked Patterns

Per shared doctrine, the following are blocked regardless of source approval status:

- No source is ever given write access to make picks, waiver claims, lineup changes, or trades.
- No source's data may be used past its declared `as_of_timestamp` in any frozen recommendation (no leakage).
- No source is treated as live/current without a passing freshness check; stale data always displays a visible banner.
- No commercial odds API is integrated without a dedicated ToS and cost review entry added to this register first.

---

## 4. Approved Source Summary (for Projection Artifact Contract)

| Source | Status | MVP Role |
|---|---|---|
| nflverse / nfl_data_py | **APPROVED** | Historical xTD derivation, role/opportunity features, 3-year decay baseline |
| Vegas implied totals (manual) | **APPROVED** | Team environment layer |
| SPAMML 2025 draft guide CSV | **APPROVED (calibration only)** | Backtest baseline, not projection input |
| PFF | DEFERRED | Not used in MVP |
| SPAMML custom platform | NOT AVAILABLE | Manual entry is permanent mode, not a gap |
| Fantrax | DEFERRED (Phase 2) | Pending its own register entry |

---

## 5. Risks and Assumptions

| ID | Item | Label | Risk |
|---|---|---|---|
| D01 | nflverse commercial-use boundary for NFL data is not explicitly cleared, only community-normed | `assumption` | LOW for personal single-league use; MEDIUM if ApexOS is ever distributed externally |
| D02 | No live odds API is contracted; manual Vegas entry introduces latency and human-error risk | `design decision` | LOW for draft MVP (one-time freeze); MEDIUM for weekly Phase 2 refresh cadence |
| D03 | PFF deferral means TPRR and scheme-grade features are unavailable at MVP | `design decision` | LOW — nflverse route/target-share data is a reasonable substitute per TouchdownOS feature taxonomy |
| D04 | Fantrax API scope/terms unreviewed | `unknown` | Blocks any Phase 2 Fantrax connector until resolved |

---

## 6. Builder Handoff

**Done definition:** This register exists, at least one historical data source (nflverse) and one team-environment source (Vegas manual) are APPROVED with all required fields populated, and the Projection Artifact Contract cites only sources listed here.

**What this unlocks:** Projection Artifact Contract can now specify real `source` field values (`nflverse:nfl_data_py:v{version}`, `vegas_manual:{ingest_date}`) instead of placeholders, satisfying the doctrinal requirement that every projection preserve source provenance.
