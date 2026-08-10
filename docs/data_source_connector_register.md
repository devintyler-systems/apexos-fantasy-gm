# Data Source and Connector Register

**Artifact:** `data_source_connector_register`
**Version:** 1.2
**Owner:** Devin Tyler (Architect)
**Status:** APPROVED sources marked; all others BLOCKED pending review
**Depends On:** League Rules Contract v0.2
**Unlocks:** Projection Artifact Contract v1.0 (source fields), PRV Calculator
**Created:** 2026-08-09
**Last Updated:** 2026-08-09 (v1.2 — added Sharp Football Analysis and VegasInsider as approved 2026 team-environment sources; added 2025 TeamRankings/PlayerRankings data as approved calibration sources)

---

## 1. Decision Statement

No data source or connector is used in any ApexOS module until it is recorded here with purpose, fields, auth, rate limits, terms, freshness, fallback, and read/write permissions. This register is the single approval gate. The Projection Artifact Contract may only reference sources marked APPROVED below.

---

## 2. Source Register

### 2.1 nflverse / nfl_data_py — **APPROVED (read-only, historical + reference)**

Historical play-by-play, weekly stats, rosters, snap counts, NGS, schedules — primary source for xTD constant derivation. Free, no auth, no rate limit, MIT-licensed, 1999-present. `confirmed evidence`

### 2.1a nflfastR / nflreadr (R packages) — **NOT ADDED — REDUNDANT WITH 2.1**

Same underlying data as nfl_data_py; adding would require a second language runtime with zero data-completeness benefit. See prior register version for full rationale and scoped-exception steps.

### 2.2 Vegas Team Implied Totals / Odds Consensus (generic manual ingest) — **APPROVED (manual ingest only)**

Manual CSV export of consensus lines. No live odds API contracted. Superseded in practice by the specific approved sources in 2.7 and 2.8 below, which now provide this data concretely for 2026.

### 2.3 SPAMML 2025 Draft Guide CSV — **APPROVED (calibration reference only)**

Backtest / calibration baseline only — not a 2026 input.

### 2.4 Pro Football Focus (PFF) — **DEFERRED, NOT APPROVED**

Cost + unresolved scraping/ToS risk not justified for single-user MVP.

### 2.5 SPAMML Custom League Platform — **NOT APPROVED, NO CONNECTOR EXISTS**

No API exists. Manual entry is the permanent mode.

### 2.6 Fantrax — **DEFERRED, PHASE 2 CANDIDATE**

Requires its own register entry before any build work.

### 2.7 Sharp Football Analysis (team projected PPG) — **APPROVED (manual ingest, 2026 season)**

| Field | Value |
|---|---|
| Purpose | 2026 preseason team projected points-per-game — direct input to Offensive Scheme Quality layer (25% weight) in Projection Artifact Contract |
| Access method | Manual CSV export/entry from publicly published Sharp Football Analysis projections; user-supplied, uploaded 2026-08-09 | `design decision` |
| Auth | None — manual entry of publicly available projection figures | — |
| Rate limits | N/A — no live API | — |
| Terms of use | Publicly published analyst projections referenced for personal, non-commercial league use. No redistribution beyond private repo. | `assumption` |
| Freshness | Point-in-time snapshot as of 2026-08-09; preseason projections may shift with roster/injury news through camp — must be re-pulled closer to draft date if materially stale | `design decision` |
| Fallback | If stale (>2 weeks before draft), flag `data_freshness_status: stale` and prompt Devin for a refreshed pull before freezing the Projection Artifact | `design decision` |
| Read/write | Read-only, manual | — |
| Role in ApexOS | Primary 2026 team offensive environment signal — replaces the generic "Vegas implied totals" placeholder in 2.2 with a concrete, dated data point | `design decision` |

**Approval condition met:** Free, publicly available, directly fills the confirmed data gap (2026 team environment) flagged in Decision Ledger v0.6.

### 2.8 VegasInsider (team projected win totals) — **APPROVED (manual ingest, 2026 season)**

| Field | Value |
|---|---|
| Purpose | 2026 preseason team win-total over/unders — secondary Offensive Scheme Quality signal (correlates with expected competitiveness/game script, which affects pass/run ratio and garbage-time TD risk) |
| Access method | Manual CSV export/entry from publicly published VegasInsider win-total odds; user-supplied, uploaded 2026-08-09 | `design decision` |
| Auth | None — manual entry of publicly displayed odds | — |
| Rate limits | N/A | — |
| Terms of use | Publicly displayed sportsbook-consensus win totals referenced for personal, non-commercial use. No redistribution beyond private repo. Any LIVE odds API integration remains BLOCKED per 2.2 until separately reviewed. | `assumption` |
| Freshness | Point-in-time snapshot as of 2026-08-09; win totals can move with news through the offseason — re-pull if >2-3 weeks stale before draft freeze | `design decision` |
| Fallback | If stale, flag `data_freshness_status: stale`; win total is a slower-moving number than weekly odds so staleness risk is lower than in-season market data | `design decision` |
| Read/write | Read-only, manual | — |
| Role in ApexOS | Secondary team-environment driver; used alongside 2.7 to form `team_expected_offensive_tds` baseline before player-level role allocation | `design decision` |

**Approval condition met:** Free, publicly available, no live API needed for a single preseason freeze value.

### 2.9 TeamRankings.com (2025 team stats) — **APPROVED (calibration reference only, NOT a 2026 input)**

| Field | Value |
|---|---|
| Purpose | 2025 actual team PPG, opponent PPG, FG attempts/game, kicking PPG, red zone attempts/scores/percentage — backtest and calibration reference for validating the xTD model and kicker/D_O models against known 2025 outcomes |
| Access method | Manual CSV export; user-supplied, uploaded 2026-08-09 | `design decision` |
| Terms of use | Publicly published team statistics referenced for personal analytical use | `assumption` |
| Freshness | Static — final 2025 season figures, will not change | `confirmed evidence` |
| Role in ApexOS | Backtest baseline per TouchdownOS Section 5.4 doctrine ("full model must outperform relevant baselines out of sample"). The `teamrankings_2025_kicking_ppg.csv` file is especially valuable — it reports actual 2025 kicker fantasy points at 3pt-FG/1pt-PAT scoring, which is IDENTICAL to SPAMML's kicker scoring rule, making it a near-direct validation set. | `design decision` |

### 2.10 PlayerRankings 2025 Total TDs — **APPROVED (calibration reference / backtest ground truth)**

| Field | Value |
|---|---|
| Purpose | 2025 actual player-level total TD counts — the ground-truth outcome set for backtesting whether ApexOS's role/opportunity/xTD model would have correctly ranked players | `design decision` |
| Access method | Manual CSV export; user-supplied, uploaded 2026-08-09 (truncated in repo to ~10 rows for readability; full ~90+ row file retained in thread attachment) | `design decision` |
| Terms of use | Publicly published player statistics for personal analytical use | `assumption` |
| Freshness | Static — final 2025 season | `confirmed evidence` |
| Role in ApexOS | Backtest ground truth per TouchdownOS Gate 2 ("Evaluation and calibration" — prove whether the model is useful before trusting it) | `design decision` |
| Note | Full dataset should be re-exported at ingestion time since only a truncated sample is committed to the repo | `design decision` |

---

## 3. Explicitly Blocked Patterns

- No source is ever given write access to make picks, waiver claims, lineup changes, or trades.
- No source's data may be used past its declared `as_of_timestamp` in any frozen recommendation.
- No source is treated as live/current without a passing freshness check.
- No commercial odds API integrated without a dedicated ToS/cost review entry here.
- No dual-runtime (R + Python) data path unless a specific field gap is documented per Section 2.1a.
- 2025 actuals (2.9, 2.10) must NEVER be blended into a 2026 projection as if they were current-season data — they are backtest inputs only.

---

## 4. Approved Source Summary (for Projection Artifact Contract)

| Source | Status | MVP Role |
|---|---|---|
| nflverse / nfl_data_py | **APPROVED** | Historical xTD derivation, role/opportunity features |
| Sharp Football Analysis (2026 projected PPG) | **APPROVED** | 2026 team offensive environment — primary |
| VegasInsider (2026 win totals) | **APPROVED** | 2026 team environment — secondary |
| SPAMML 2025 draft guide CSV | **APPROVED (calibration only)** | Backtest baseline |
| TeamRankings 2025 team stats | **APPROVED (calibration only)** | Backtest baseline, esp. kicker validation |
| PlayerRankings 2025 total TDs | **APPROVED (calibration only)** | Backtest ground truth |
| nflreadr / nflfastR (R) | **NOT ADDED (redundant)** | N/A |
| PFF | DEFERRED | Not used in MVP |
| SPAMML custom platform | NOT AVAILABLE | Manual entry is permanent mode |
| Fantrax | DEFERRED (Phase 2) | Pending its own register entry |

---

## 5. Risks and Assumptions

| ID | Item | Label | Risk |
|---|---|---|---|
| D01 | nflverse commercial-use boundary not explicitly cleared | `assumption` | LOW for personal use |
| D02 | No live odds API; manual entry introduces latency/human-error risk | `design decision` | LOW for draft MVP |
| D03 | PFF deferral means TPRR/scheme-grade features unavailable at MVP | `design decision` | LOW |
| D04 | Fantrax API scope/terms unreviewed | `unknown` | Blocks Phase 2 Fantrax connector |
| D05 | nflreadr/nflfastR intentionally not added | `design decision` | None |
| D06 | Sharp Football Analysis and VegasInsider projections are single-point-in-time snapshots (Aug 9, 2026) with no defined re-pull cadence yet | `assumption` | MEDIUM — must re-pull closer to draft date since camp battles/injuries can shift both by late August |
| D07 | Two 2026 team-environment sources (2.7 PPG-based, 2.8 win-total-based) may disagree on a given team's environment quality; no reconciliation method defined yet | `unknown` | Flagged for Projection Artifact Contract update — needs a defined blend or precedence rule |

---

## 6. Builder Handoff

**Done definition:** Register exists with nflverse, Sharp Football Analysis, and VegasInsider approved for 2026 team environment. TeamRankings and PlayerRankings 2025 data approved for calibration. Projection Artifact Contract cites only sources listed here.

**What this unlocks:** The Projection Artifact Contract's `team_expected_offensive_tds` and `source_citations` fields can now reference real, dated 2026 data (`sharpfootball:2026-08-09`, `vegasinsider:2026-08-09`) instead of a generic "vegas_manual" placeholder. Backtesting against 2025 TeamRankings/PlayerRankings data can begin once the xTD lookup table (Projection Artifact Contract Section 5) is built.
