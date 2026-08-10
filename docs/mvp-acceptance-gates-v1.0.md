# MVP Acceptance Gates

**Artifact:** `mvp_acceptance_gates`
**Version:** 1.0
**Status:** READY FOR BUILDER/REVIEWER
**Owner:** Devin Tyler (Architect)
**Depends On:** All prior contracts (League Rules v0.3, Draft Round Order Map v1.0, Projection Artifact v1.0+addenda, Scoring Engine v1.0, PRV Calculator v1.0, Draft Recommendation Engine v1.0-v1.2, Live-Draft Degraded Mode Runbook v1.0)
**Unlocks:** Builder/Operator implementation backlog
**Created:** 2026-08-10

---

## 1. Decision Statement

This is the single consolidated go/no-go checklist. The system is NOT ready for the live SPAMML draft until every BLOCK-level item below passes. This document does not introduce new logic — it aggregates and cross-references acceptance tests already defined across all 7 prior contracts, organized by what an Operator needs to verify before trusting the tool on draft day.

**Rule:** No item below is waived informally. If a BLOCK gate fails, the tool is not used live — fall back to fully manual drafting using the frozen Projection Artifact's raw numbers read directly from the data file, without the optimizer.

---

## 2. Gate Categories

### Category A: Scoring Correctness

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| A1 | Scoring Engine SE01-SE03 | All point calculations match manual arithmetic for 10 hand-picked test cases across every position type | PENDING |
| A2 | Scoring Engine SE02 | Forbidden dimensions (points allowed, sacks, INTs, fumbles, blocked kicks) produce zero code-path effect | PENDING |
| A3 | League Rules v0.3 | 2pt conversions score identically (2 pts) regardless of pass/rush/catch origin | PENDING |
| A4 | Scoring Engine SE01 | Zero hardcoded point values in engine source — all read from League Rules Contract YAML at runtime | PENDING |

### Category B: Roster and Positional Eligibility

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| B1 | League Rules v0.3, PRV01 | REC1/2/3 correctly accept both WR and TE from a single merged replacement pool | PENDING |
| B2 | Draft Recommendation DR01 | Once a slot is filled on Devin's roster, no candidate for that position ever reappears in recommendations | PENDING |
| B3 | PRV05 | D_O replacement pool never exceeds 16 entries (one per NFL team); any overflow fails loudly | PENDING |
| B4 | League Rules v0.3 | RB1/RB2 only accept HB/FB; QB/KCK are single-eligibility, no cross-position leakage | PENDING |

### Category C: Projection and Recommendation Integrity

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| C1 | Projection Artifact PA01 | Every projection row cites only APPROVED sources from Data Source Register v1.2 | PENDING |
| C2 | Projection Artifact PA04 | Frozen artifact is immutable once `draft_start_timestamp` is set; corrections require a new version, never an overwrite | PENDING |
| C3 | Projection Artifact PA02 | xTD lookup buckets below the minimum sample-size threshold propagate `projected_role_confidence: low` | PENDING |
| C4 | Projection Artifact addendum (D07) | `team_expected_offensive_tds` derives from Sharp Football PPG only; VegasInsider win total never enters that specific calculation | PENDING |
| C5 | Draft Recommendation DR06 | Identical snapshot + draft_state inputs produce byte-identical recommendation output (excluding timestamp/UUID fields) | PENDING |
| C6 | Draft Recommendation DR05 | Two D_O candidates with identical PRV but different weekly_prize_ev receive identical final_score — prize EV never enters ranking math | PENDING |

### Category D: 16-Team Scarcity and Replacement Value

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| D1 | PRV01 | REC replacement value computed from merged WR+TE pool at rank 48, not WR-only or TE-only | PENDING |
| D2 | PRV02, PRV03 | Dynamic replacement value recalculates after every single pick (128 times/draft), not batched by round | PENDING |
| D3 | PRV04 | `scarcity_ratio` exceeds 1.0 when league-wide remaining demand exceeds remaining pool for a position | PENDING |
| D4 | PRV07 | PRV output is byte-identical on repeated runs against an identical frozen snapshot | PENDING |

### Category E: Draft-Day Operational Readiness

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| E1 | Live-Draft Runbook §3 | All 128 picks (Devin's 8 + 120 others) can be entered manually with correct validation | PENDING |
| E2 | Live-Draft Runbook §4 | Ambiguous player names halt entry and force manual disambiguation; zero auto-merge events occur in a simulated draft | PENDING |
| E3 | Live-Draft Runbook §5 | Stale-data banner displays accurately; `data_freshness_status` is never silently defaulted to "fresh" | PENDING |
| E4 | Live-Draft Runbook §6 | Recommendation payload for Devin's next pick is fully pre-computed before his turn arrives, with zero calculation lag — verified even though SPAMML 2026 is untimed (per League Rules v0.3), since this remains free insurance | PENDING |
| E5 | Live-Draft Runbook §7 | "Undo last entry" fully reverses draft_state, available_pool, and PRV state for the immediately preceding pick only | PENDING |
| E6 | Live-Draft Runbook §8 | Session interruption and resume requires explicit confirmation before allowing new entries; zero data loss across a simulated interruption | PENDING |

### Category F: Draft Round Order and Availability

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| F1 | Draft Round Order Map T01 | Ground truth validation: `get_pick_numbers(11) == [11, 22, 35, 62, 75, 86, 99, 126]` matches confirmed 2025 actuals | PENDING |
| F2 | Draft Round Order Map T05-T06 | Pivot rounds (3,4,7,8) correctly reorder starting from position 9 | PENDING |
| F3 | Draft Round Order Map T08 | `get_picks_between()` correctly computes picks remaining until Devin's next turn for all 16 possible draft positions | PENDING |
| F4 | Draft Recommendation DR02 | Availability pressure calculations use the ACTUAL pick gap from the round order map, never a generic "half the league" approximation | PENDING |

### Category G: New Capabilities (Snooze, Convention Flags)

| Gate | Source Test(s) | Pass Criterion | Status |
|---|---|---|---|
| G1 | Draft Recommendation DR10, DR13 | Snoozing a player excludes them from the CURRENT pick only; zero effect on that player's or any other player's PRV/scarcity math | PENDING |
| G2 | Draft Recommendation DR11 | A snoozed player who survives to Devin's next pick is re-evaluated with zero penalty or carryover flag | PENDING |
| G3 | Draft Recommendation DR12 | Snoozing past Devin's final (8th) pick returns a validation error, not a silent no-op | PENDING |
| G4 | Draft Recommendation DR09 | KCK-before-round-4 and D_O-before-round-7 recommendations still surface as primary_recommendation when PRV justifies it — the convention flag never suppresses a mathematically correct pick | PENDING |

---

## 3. Gate Severity Legend

- **BLOCK** (default, unless marked otherwise): Failure means the tool is not used live for the draft. All gates above are BLOCK unless noted.
- **ADVISORY**: Nice-to-have; failure is logged but does not prevent live use. (None of the gates above are advisory — all trace back to BLOCK-level tests in their source contracts.)

---

## 4. Go/No-Go Procedure

```text
1. Builder completes implementation of all 7 core contracts + runbook.
2. Builder runs the full automated test suite corresponding to every
   Source Test cited above (SE, PA, PRV, DR, T-series, plus manual
   verification of E-series operational procedures).
3. Builder marks each gate's Status column: PASS | FAIL | BLOCKED (dependency
   not yet resolved, e.g., U01 draft position affects some F-series tests
   but F1/F2/F3 are position-independent and can pass regardless).
4. Reviewer independently re-runs a sample of gates (at minimum: A1, B1,
   C2, D1, E2, F1, G1) without relying solely on Builder's self-report.
5. Devin (Architect/Operator) reviews the full gate table. ANY BLOCK-level
   FAIL means the system is not used live -- fall back to the frozen
   Projection Artifact's raw numbers, read manually, no optimizer.
6. Once all gates show PASS, the system is authorized for the live SPAMML
   2026 draft.
```

---

## 5. Known Dependencies Not Yet Resolved (do not block gate testing, but affect live accuracy)

| ID | Item | Affects Which Gates | Status |
|---|---|---|---|
| U01 | 2026 draft position | F3, F4 can be tested generically for all 16 positions but the LIVE draft needs this confirmed before draft day | Open |
| U02 | Draft date/time | C1-C4 (projection freshness) depend on knowing when to freeze the artifact | Open |
| U04-U09 | Various (trading, missed FG, waivers, playoffs, keeper, prize ties) | Do not block MVP draft gates; flagged in League Rules Contract v0.3 | Open, non-blocking |

---

## 6. Builder/Operator Handoff

**Ordered work:**
1. Implement all 7 core contracts per their individual Builder Handoff sections (already specified)
2. Run every Source Test cited in Sections 2A-2G as an automated suite where possible
3. Manually verify the E-series (operational) gates via a full simulated 128-pick draft session
4. Populate the Status column in this document (PASS/FAIL/BLOCKED) for every gate
5. Submit to Reviewer for independent spot-check per Section 4, Step 4
6. Present completed gate table to Devin for final go/no-go

**Done definition:** Every gate in Categories A-G shows PASS. Reviewer has independently verified the minimum spot-check set. No BLOCK-level gate is outstanding.

**What this unlocks:** This is the last specification artifact in the ApexOS Fantasy GM draft-MVP chain. What follows is pure implementation — Builder writes the actual Python/SQLite/Streamlit code against these now-complete contracts, with this document as the final acceptance checklist before Devin trusts the tool in a live draft.
