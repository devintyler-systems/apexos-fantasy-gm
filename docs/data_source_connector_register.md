# Data Source and Connector Register

**Artifact:** `data_source_connector_register`
**Version:** 1.3
**Owner:** Devin Tyler (Architect)
**Status:** APPROVED sources marked; all others BLOCKED pending review
**Depends On:** League Rules Contract v0.3
**Unlocks:** Projection Artifact Contract, PRV Calculator, backtest work (B-17)
**Created:** 2026-08-09
**Last Updated:** 2026-08-10 (v1.3 -- replaced truncated player-TD file with full dataset;
added games-with-TDs and pct-of-games-with-TDs calibration files; formally registered
TeamRankings player-stats pages as an approved source domain, not just the team-stats pages)

---

## 1. Decision Statement

No data source or connector is used in any ApexOS module until it is recorded here with
purpose, fields, auth, rate limits, terms, freshness, fallback, and read/write permissions.

---

## 2. Source Register (condensed -- see prior versions in git history for full detail on 2.1-2.6)

### 2.1 nflverse / nfl_data_py -- APPROVED
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

---

## 4. Decision Ledger Entry

Data completeness improved for backtest/calibration work (unlocks B-17 more fully). No change
to any live 2026 projection formula -- these are reference/validation files only. New idea
surfaced (games-with-TDs as a consistency signal) is flagged as a candidate, not adopted,
pending the same definition/source/validation/baseline/acceptance-test process required
for any promoted idea per shared doctrine.
