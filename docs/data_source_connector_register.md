# Data Source and Connector Register

**Artifact:** `data_source_connector_register`
**Version:** 1.1
**Owner:** Devin Tyler (Architect)
**Status:** APPROVED sources marked; all others BLOCKED pending review
**Depends On:** League Rules Contract v0.2
**Unlocks:** Projection Artifact Contract v1.0 (source fields)
**Created:** 2026-08-09
**Last Updated:** 2026-08-09 (v1.1 — added nflreadr/nflfastR redundancy note)

---

## 1. Decision Statement

No data source or connector is used in any ApexOS module until it is recorded here with purpose, fields, auth, rate limits, terms, freshness, fallback, and read/write permissions. This register is the single approval gate. The Projection Artifact Contract may only reference sources marked APPROVED below.

---

## 2. Source Register

### 2.1 nflverse / nfl_data_py — **APPROVED (read-only, historical + reference)**

| Field | Value |
|---|---|
| Purpose | Historical play-by-play, weekly player stats, rosters, snap counts, NGS stats, schedules, scoring lines, draft picks — primary source for xTD constant derivation and role/opportunity features |
| Access method | Python package `nfl_data_py` (pip install), pulls from `nflverse/nflverse-data`, `nflverse/nfldata`, `dynastyprocess/data` GitHub repos | `confirmed evidence` |
| Auth | None required — public GitHub-hosted data, no API key | `confirmed evidence` |
| Rate limits | None documented — data is static files (Parquet/CSV) hosted on GitHub, not a live API | `confirmed evidence` |
| Terms of use | R/Python code is MIT licensed (open source). Underlying NFL data belongs to respective owners; personal/analytical use is the established community norm. | `confirmed evidence` / `assumption` on commercial-use boundary |
| Freshness | Automated via GitHub Actions; play-by-play and weekly stats updated within ~24-48h of games during season; historical data back to 1999 (pbp) | `confirmed evidence` |
| Historical depth | Play-by-play: 1999–present. Weekly/seasonal stats, rosters, combine, draft picks, scoring lines also available | `confirmed evidence` |
| Fallback if unavailable | Cached local Parquet snapshot from last successful pull; system flags `data_freshness_status: stale` and continues | `design decision` |
| Read/write | Read-only | `confirmed evidence` |
| Role in ApexOS | Primary source for: field-position xTD rate derivation, role/opportunity features, 3-year historical decay baseline | `design decision` |

**Approval condition met:** Free, no auth, no rate limit, MIT-licensed code, established use for exactly this purpose.

---

### 2.1a nflfastR / nflreadr (R packages) — **NOT ADDED — REDUNDANT WITH 2.1**

**Decision: Do not add as a separate connector.** `design decision`

`nflfastR` and `nflreadr` are the R-native clients for the exact same underlying data repositories (`nflverse/nflverse-data`, `nflverse/nfldata`) that `nfl_data_py` already exposes in Python. All three tools read from identical source-of-truth files — there is no additional data, freshness, or coverage gained by adding the R packages alongside the already-approved Python client.

**Adding them would require:** a second language runtime (R) in an otherwise Python-primary stack, with zero data-completeness benefit under current MVP scope.

**When to revisit:** Only if Builder encounters a specific field or dataset during ingestion that exists in nflreadr's data dictionary but is not yet exposed by `nfl_data_py`'s function set (this has historically been rare — `nfl_data_py` maintains close parity). If that happens, treat it as a scoped one-time R script to export the missing table to CSV/Parquet for Python ingestion — not a standing dual-runtime connector.

**If you want to proceed anyway despite the above** (e.g., for direct access to a nflreadr-only convenience function), steps would be:
1. Install R (if not already present) and the `nflreadr` package: `install.packages("nflreadr")`
2. Identify the specific missing dataset/field via the [nflreadr data dictionary](https://nflreadr.nflverse.com/)
3. Pull only that dataset, export to Parquet/CSV
4. Ingest the exported file through the same Python ingestion pipeline used for nfl_data_py — do not build a parallel R-based ingest path
5. Log the addition here as a scoped exception, not a standing register entry

---

### 2.2 Vegas Team Implied Totals / Odds Consensus — **APPROVED (manual ingest only)**

| Field | Value |
|---|---|
| Purpose | Team implied point totals, win/loss over-unders — Offensive Scheme Quality layer |
| Access method | Manual CSV export from a consensus odds aggregator | `design decision` |
| Terms of use | Manual reference of publicly displayed consensus lines for personal, non-commercial use. Any live odds API is BLOCKED until reviewed here. | `assumption` |
| Freshness | As of manual entry timestamp only | `design decision` |
| Fallback | Null if unavailable, never silently defaulted | `design decision` |
| Role in ApexOS | Feeds `team_expected_offensive_tds` driver | `design decision` |

---

### 2.3 SPAMML 2025 Draft Guide CSV — **APPROVED (calibration reference only)**

Backtest / calibration baseline only — not a 2026 input. `design decision`

---

### 2.4 Pro Football Focus (PFF) — **DEFERRED, NOT APPROVED**

Cost + unresolved scraping/ToS risk not justified for single-user MVP. `design decision`

---

### 2.5 SPAMML Custom League Platform — **NOT APPROVED, NO CONNECTOR EXISTS**

No API exists. Manual entry is the permanent mode. `confirmed evidence`

---

### 2.6 Fantrax — **DEFERRED, PHASE 2 CANDIDATE**

Requires its own register entry before any build work. `design decision`

---

## 3. Explicitly Blocked Patterns

- No source is ever given write access to make picks, waiver claims, lineup changes, or trades.
- No source's data may be used past its declared `as_of_timestamp` in any frozen recommendation.
- No source is treated as live/current without a passing freshness check.
- No commercial odds API integrated without a dedicated ToS/cost review entry here.
- No dual-runtime (R + Python) data path unless a specific field gap is documented per Section 2.1a.

---

## 4. Approved Source Summary (for Projection Artifact Contract)

| Source | Status | MVP Role |
|---|---|---|
| nflverse / nfl_data_py | **APPROVED** | Historical xTD derivation, role/opportunity features, decay baseline |
| Vegas implied totals (manual) | **APPROVED** | Team environment layer |
| SPAMML 2025 draft guide CSV | **APPROVED (calibration only)** | Backtest baseline |
| nflreadr / nflfastR (R) | **NOT ADDED (redundant)** | N/A — see 2.1a for scoped exception path |
| PFF | DEFERRED | Not used in MVP |
| SPAMML custom platform | NOT AVAILABLE | Manual entry is permanent mode |
| Fantrax | DEFERRED (Phase 2) | Pending its own register entry |

---

## 5. Risks and Assumptions

| ID | Item | Label | Risk |
|---|---|---|---|
| D01 | nflverse commercial-use boundary not explicitly cleared, only community-normed | `assumption` | LOW for personal use |
| D02 | No live odds API; manual entry introduces latency/human-error risk | `design decision` | LOW for draft MVP; MEDIUM for Phase 2 weekly cadence |
| D03 | PFF deferral means TPRR/scheme-grade features unavailable at MVP | `design decision` | LOW — nflverse route/target-share is a reasonable substitute |
| D04 | Fantrax API scope/terms unreviewed | `unknown` | Blocks Phase 2 Fantrax connector |
| D05 | nflreadr/nflfastR intentionally not added as a separate connector | `design decision` | None — fully redundant with 2.1 under current scope |

---

## 6. Builder Handoff

**Done definition:** Register exists with nflverse and Vegas manual approved. Projection Artifact Contract cites only sources listed here.

**What this unlocks:** Projection Artifact Contract v1.0 (built same day) cites `nflverse:nfl_data_py:v{version}` and `vegas_manual:{ingest_date}` as real source values.
