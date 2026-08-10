# Projection Artifact Contract

**Artifact:** `projection_artifact`
**Version:** 1.0
**Status:** READY FOR BUILDER
**Owner:** Devin Tyler (Architect)
**Builder:** TBD
**Reviewer:** TBD
**Depends On:** League Rules Contract v0.2, Data Source and Connector Register v1.1
**Unlocks:** Scoring Engine, PRV Calculator, Draft Recommendation Engine
**Created:** 2026-08-09

---

## 1. Decision Statement

SPAMML scores **actual game points only** — TDs (6), 2pt conversions (2), FGs (3), PATs (1), defensive/ST TDs (6), safeties (2). Zero yardage, zero receptions, zero bonuses. This means every projection must resolve to a touchdown/scoring-event probability or expected count, not a generic "fantasy points" number imported from a standard-scoring source. This contract defines a scoring-neutral projection layer (per TouchdownOS doctrine) that outputs raw scoring-event expectations, which the separate Scoring Engine (not this contract) converts into SPAMML fantasy points.

The framework document's trait-weight system and its cited xTD constants (0.55 for 1-yard carries, 0.38 for end-zone targets) are **not adopted as-is**. This contract requires xTD values to be derived from nflverse play-by-play data, not imported as fixed constants. `design decision`

---

## 2. Scope and Non-Goals

**In scope:**
- Team offensive TD-count environment model (baseline layer)
- Player-level rushing/receiving/passing TD expectation model (QB, RB, WR, TE)
- Kicker FG/PAT expectation model (first-class position, per TouchdownOS correction)
- D/O (team defense+offense+special teams) scoring-event model, scoped exactly to SPAMML's confirmed scoring rules
- xTD derivation method sourced from nflverse historical play-by-play
- Frozen artifact schema, versioning, and `as_of_timestamp` discipline
- Manual environment override field for Devin's qualitative read (scheme changes, camp battles, depth chart shifts)

**Not in scope (deferred):**
- Monte Carlo simulation engine (Phase 2 per TouchdownOS Gate 5 — MVP uses point estimate + confidence band, not full distribution simulation)
- Player capability registry with expert observations (Phase 2 — MVP uses measurable role/production features only, per TouchdownOS Section 5.5 doctrine: traits are explanatory, not primary)
- Market/odds-edge adapter (Phase 3 per TouchdownOS Gate 6)
- Weekly in-season refresh cadence (this contract covers the draft-day frozen artifact only; Phase 2 extends to weekly runs)
- Backtesting harness execution (contract defines the requirement; execution is a build-sequence item, not this artifact)

---

## 3. Core Doctrine (inherited from TouchdownOS blueprint, binding on this contract)

1. Team environment is modeled before player outcomes — a player cannot score a TD his team doesn't create.
2. Volume/opportunity, scheme quality, individual efficiency, and talent/trait are kept as **separate, auditable fields** — never pre-blended into one opaque score before the optimizer sees them.
3. No time leakage — every feature must be dated before the declared `as_of_timestamp`.
4. Frozen artifacts — once `draft_start_timestamp` is set, this artifact does not change.
5. Manual overrides are stored as data (value, reason, owner, timestamp), never silently blended into the raw model output.
6. Kicker is a first-class scoring position (SPAMML confirms FG=3, PAT=1) — not deferred, not treated as noise.
7. D/O event definition is scoped EXACTLY to what SPAMML pays: defensive TD, safety, special-teams TD. Points allowed, sacks, INTs, and fumble recoveries (as standalone events, not TDs) are explicitly excluded from scoring — confirmed in League Rules Contract v0.2.

---

## 4. Modeling Weight Framework (adapted, not adopted verbatim)

From the framework document, retained as **starting hypothesis weights**, not fixed constants — subject to backtest validation before being trusted:

| Dimension | Starting Weight | Status |
|---|---|---|
| Volume & Opportunity | 45% | `evidence-backed inference` — red zone carries/targets, goal-to-go touches, routes per dropback; directly computable from nflverse |
| Offensive Scheme Quality | 25% | `evidence-backed inference` — Vegas implied totals (manual, approved), EPA/play (nflverse), pace/RZ ratio (nflverse) |
| Individual Efficiency | 20% | `evidence-backed inference` — xTD over/under performance (self-derived, see Section 5), TPRR (nflverse routes+targets) |
| Talent & Trait Profile | 10% | `assumption` — lowest-confidence layer; MVP uses only objectively sourced measurables (NFL Combine/NGS speed/burst), not subjective 0-100 grades |

**These weights are NOT hardcoded into the scoring formula at v1.0.** They inform initial feature engineering priority. The actual blend must be validated against the backtest protocol in Section 8 before being trusted for live recommendations. Flagging any weight as production-ready before backtest validation is a doctrine violation. `design decision`

---

## 5. xTD Derivation Method (replaces framework doc's fixed constants)

```text
Source: nflverse play-by-play data via nfl_data_py (2016–2025 window minimum)

Step 1: Bucket every rushing/receiving play by field position at snap
         (e.g., yard-line bands: 1, 2-3, 4-5, 6-10, 11-20, 21+)
Step 2: For each bucket, compute:
         xTD_rate(bucket) = (TDs scored from bucket) / (total plays from bucket)
         Segment separately for rush attempts vs. pass targets
Step 3: Apply 3-year weighted decay per framework doc's cited method:
         50% weight to most recent complete season, 33% to season-2, 17% to season-3
         (NOTE: decay weights themselves are a starting assumption —
          validate against backtest before treating as final)
Step 4: Store resulting xTD lookup table as a versioned artifact:
         data/processed/xtd_lookup_table_v{N}.parquet
         Fields: field_position_bucket, play_type, xtd_rate, sample_size, season_window, as_of_timestamp
Step 5: Apply xTD lookup to each player's projected touch/target distribution
         (from role/opportunity layer) to produce expected_rushing_tds,
         expected_receiving_tds, expected_passing_tds
```

**Acceptance requirement:** xTD lookup table must report `sample_size` per bucket. Any bucket with sample_size below a Builder-documented minimum threshold must be flagged `low_confidence` rather than silently used. `design decision`

---

## 6. Output Contracts

### 6a. Offensive Player Projection (QB, RB, WR, TE) — adapted from TouchdownOS canonical contract

```yaml
projection_id: uuid
artifact_version: "1.0"
season: 2026
player_id: canonical_player_identifier
team_id: team_identifier
position: QB | RB | WR | TE
as_of_timestamp_utc: ISO-8601 timestamp
source_citations:
  - nflverse:nfl_data_py:v{package_version}
  - vegas_manual:{ingest_date}
model_version: semver_or_git_sha
feature_snapshot_id: immutable_identifier

expected_rushing_tds: nonnegative_float
expected_receiving_tds: nonnegative_float
expected_passing_tds: nonnegative_float_or_null   # QB only
expected_two_point_conversions: nonnegative_float  # rush+rec+pass combined per SPAMML rules
expected_total_scoring_events: nonnegative_float   # sum of the above, pre-scoring-engine

team_expected_offensive_tds: nonnegative_float
projected_role_confidence: low | medium | high
data_freshness_status: fresh | stale | incomplete

primary_drivers:
  - name: red_zone_touch_share
    dimension: volume_opportunity
    contribution: 0.00
  - name: team_implied_total
    dimension: offensive_scheme_quality
    contribution: 0.00
  - name: xtd_over_under_performance
    dimension: individual_efficiency
    contribution: 0.00

raw_model_expected_total_scoring_events: nonnegative_float
manual_environment_override:
  value: null_or_float
  reason: null_or_string
  owner: null_or_string
  timestamp: null_or_ISO8601
final_expected_total_scoring_events: nonnegative_float
```

### 6b. Kicker Projection — adopted directly from TouchdownOS blueprint (SPAMML-scoped)

```yaml
projection_id: uuid
artifact_version: "1.0"
player_id: canonical_player_identifier
team_id: team_identifier
position: K
as_of_timestamp_utc: ISO-8601 timestamp
source_citations: [nflverse:nfl_data_py:v{version}, vegas_manual:{date}]

expected_field_goal_attempts: nonnegative_float
expected_field_goals_made: nonnegative_float
expected_pat_attempts: nonnegative_float
expected_pats_made: nonnegative_float
expected_kicker_scoring_events: nonnegative_float   # (3 x FG made) + (1 x PAT made), pre-scoring-engine
data_freshness_status: fresh | stale | incomplete

primary_drivers:
  - name: team_drive_environment
    contribution: 0.00
  - name: field_goal_distance_distribution
    contribution: 0.00

note: "SPAMML has no missed_fg/missed_pat penalty confirmed (U05, unconfirmed) — model must NOT assume a penalty exists"
```

### 6c. D/O (Team Defense/Offense/Special Teams) Projection — adapted from TouchdownOS D/ST contract, rescoped

```yaml
projection_id: uuid
artifact_version: "1.0"
team_id: team_identifier   # a full NFL team, per League Rules Contract v0.2
position: D_O
as_of_timestamp_utc: ISO-8601 timestamp
source_citations: [nflverse:nfl_data_py:v{version}]

expected_defensive_touchdowns: nonnegative_float       # INT/fumble return TDs
expected_special_teams_touchdowns: nonnegative_float   # kick/punt return TDs
expected_safeties: nonnegative_float
expected_do_scoring_events: nonnegative_float          # 6x(def_td + st_td) + 2x(safety), pre-scoring-engine
data_freshness_status: fresh | stale | incomplete

# Explicitly EXCLUDED per SPAMML scoring rules (confirmed League Rules Contract v0.2):
# points_allowed, sacks, interceptions (as standalone), fumble_recoveries (as standalone),
# blocked_kicks (as standalone) -- these do NOT convert to fantasy points in this league

# Weekly prize EV -- separate value stream, NOT part of expected_do_scoring_events:
weekly_prize_ev:
  top_offense_prize_probability: 0.0000-1.0000   # probability this team leads league in real points scored, that week
  top_defense_prize_probability: 0.0000-1.0000   # probability this team allows fewest real points, that week
  note: "Prize EV is informational for draft-day D_O value assessment; excluded from projected_fantasy_pts entirely"

primary_drivers:
  - name: opponent_turnover_vulnerability
    contribution: 0.00
  - name: return_opportunity_index
    contribution: 0.00
```

---

## 7. Frozen Artifact File Contract

```text
File: data/processed/projection_artifact_spamml_2026_v{N}.parquet
Frozen at: draft_start_timestamp (set once, immutable thereafter for this draft)

Required top-level metadata (stored alongside the Parquet file as a companion JSON):
{
  "artifact_id": "projection_artifact_spamml_2026",
  "version": "1.0",
  "league_rules_version": "spamml-2026-v0.2",
  "data_source_register_version": "1.1",
  "as_of_timestamp_utc": "<ISO8601>",
  "frozen": true,
  "row_count": <int>,
  "positions_covered": ["QB", "RB", "WR", "TE", "K", "D_O"],
  "xtd_lookup_table_version": "v{N}",
  "known_limitations": [
    "Missed FG/PAT penalty unconfirmed (U05) -- not modeled",
    "Monte Carlo simulation deferred to Phase 2 -- point estimates only",
    "Player capability registry deferred to Phase 2 -- role/production features only"
  ]
}
```

Once `frozen: true` is written, no process may modify rows in this file. A new version number is required for any correction — corrections do not overwrite frozen artifacts, per doctrine.

---

## 8. Acceptance Tests

### PA01 — Source Citation Completeness (BLOCK)
```
Every projection row must have a non-empty source_citations list referencing only
sources marked APPROVED in Data Source and Connector Register v1.1.
```

### PA02 — xTD Table Sample Size Transparency (BLOCK)
```
Every xTD lookup bucket used in a projection must carry a sample_size field.
Any bucket below the Builder-documented minimum threshold must propagate
projected_role_confidence: low for affected players.
```

### PA03 — No Time Leakage (BLOCK)
```
No feature timestamp in feature_snapshot_id may postdate as_of_timestamp_utc.
```

### PA04 — Frozen Artifact Immutability (BLOCK)
```
Once draft_start_timestamp is set and artifact is written with frozen: true,
any attempt to modify existing rows must raise an error, not silently succeed.
Corrections require a new version number.
```

### PA05 — D_O Scoring Scope Correctness (BLOCK)
```
expected_do_scoring_events must derive ONLY from defensive_td, special_teams_td,
and safety fields. Points allowed, sacks, interceptions, and fumble recoveries
must NOT appear anywhere in the scoring calculation.
```

### PA06 — Kicker No-Penalty Assumption (BLOCK)
```
Kicker projection must NOT apply any missed_fg or missed_pat point deduction
unless U05 in the Assumptions Register is resolved to confirm a penalty exists.
```

### PA07 — Manual Override Non-Destructive (BLOCK)
```
When manual_environment_override.value is set, raw_model_expected_total_scoring_events
must remain unchanged in the same record; only final_expected_total_scoring_events
reflects the override. Both fields must be present and distinct.
```

### PA08 — Weekly Prize EV Isolation (BLOCK)
```
weekly_prize_ev fields must never be summed into expected_do_scoring_events
or any field consumed by the Scoring Engine.
```

### PA09 — Baseline Comparison Present (ADVISORY — required before Phase 2, not blocking MVP)
```
Projection artifact generation process must log a comparison against at least
one baseline (e.g., prior-season position-average TD rate) per TouchdownOS
Section 5.4 doctrine, even if informal at MVP.
```

---

## 9. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| P01 | Framework doc's 45/25/20/10 weight split is untested for this specific league's scoring rules (TD-only, no yardage) | `assumption` | MEDIUM — SPAMML's zero-yardage scoring may shift optimal weighting toward pure TD/opportunity signal vs. standard leagues; validate via backtest before trusting |
| P02 | 3-year decay (50/33/17) is inherited from framework doc, not independently validated | `assumption` | LOW-MEDIUM — reasonable default, but Builder should A/B against a simpler 1-year or unweighted 3-year average during backtest |
| P03 | xTD bucket granularity (yard-line bands) may be too coarse for goal-to-go precision needed at MVP scale | `evidence-backed inference` | LOW — refine bucket width if backtest shows systematic bias near goal line |
| P04 | D_O weekly_prize_ev model has no defined calculation method yet in this contract | `unknown` | Flagged for a follow-up mini-contract before draft if Devin wants prize EV surfaced as a reason code |

---

## 10. Builder Handoff

**Ordered work:**
1. Implement nflverse ingestion (`nfl_data_py` pull for 2023-2025 seasons minimum)
2. Build xTD lookup table per Section 5; validate sample sizes
3. Implement offensive player projection (6a) for QB/RB/WR/TE
4. Implement kicker projection (6b)
5. Implement D_O projection (6c), enforcing PA05 scope exclusions
6. Wire manual Vegas ingest and `manual_environment_override` input path
7. Implement frozen artifact writer with immutability enforcement (PA04)
8. Run PA01–PA08 as automated test suite; PA09 as a logged manual step
9. Submit for Reviewer sign-off

**Done definition:** All PA01–PA08 pass. Frozen Parquet + companion JSON exist in `data/processed/`. Reviewer confirms D_O scope exclusions (PA05) and kicker no-penalty assumption (PA06) by manual inspection, not just automated test.

**What this unlocks:** Scoring Engine (applies SPAMML point values to these scoring-event expectations), PRV Calculator (ranks players using `final_expected_total_scoring_events` converted to fantasy points), Draft Recommendation Engine.
