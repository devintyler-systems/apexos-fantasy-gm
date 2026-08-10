# Scoring Engine Contract

**Artifact:** `scoring_engine`
**Version:** 1.0
**Status:** READY FOR BUILDER
**Owner:** Devin Tyler (Architect)
**Builder:** TBD
**Reviewer:** TBD
**Depends On:** League Rules Contract v0.2, Projection Artifact Contract v1.0
**Unlocks:** PRV Calculator, Draft Recommendation Engine
**Created:** 2026-08-09

---

## 1. Decision Statement

The Scoring Engine is a pure, deterministic function: it takes a frozen Projection Artifact record (scoring-event expectations) and the League Rules Contract's scoring map, and returns SPAMML fantasy points. It contains zero modeling logic, zero opinions, and zero probability estimation — those all live upstream in the Projection Artifact. This is intentionally the smallest, most mechanical contract in the system. If this engine ever needs a judgment call, that call belongs in the Projection Artifact or League Rules Contract instead. `design decision`

---

## 2. Scope and Non-Goals

**In scope:**
- Convert `expected_total_scoring_events` fields (offense, kicker, D_O) into `projected_fantasy_pts` using only the confirmed scoring map values from `spamml-2026-v0.2.yaml`
- Apply the conversion independently per position type (offense / kicker / D_O)
- Preserve full traceability: every output must cite which scoring map version and which projection artifact version produced it
- Validate that no scoring dimension outside the confirmed map (yardage, receptions, points allowed, sacks, INTs, fumbles) ever enters the calculation

**Not in scope:**
- Any projection, probability, or expected-value modeling (that's the Projection Artifact's job)
- Replacement value, availability, or optimizer logic (that's the PRV Calculator's job)
- Weekly prize EV conversion to dollars (informational only, tracked separately per Projection Artifact Contract PA08 — never enters `projected_fantasy_pts`)

---

## 3. Conversion Formulas (all constants sourced directly from League Rules Contract v0.2 — zero hardcoding)

### 3a. Offensive Player (QB, RB, WR, TE)

```text
projected_fantasy_pts =
    (expected_rushing_tds       × scoring.rushing.td_rush)
  + (expected_receiving_tds     × scoring.receiving.td_reception)
  + (expected_passing_tds       × scoring.passing.td_pass)
  + (expected_two_point_conversions × scoring.rushing.two_point_conversion_rush)
    # NOTE: 2pt conversions score identically (2 pts) whether pass/rush/catch per
    # League Rules Contract v0.2 — single constant applies regardless of type
```

### 3b. Kicker

```text
projected_fantasy_pts =
    (expected_field_goals_made × scoring.kicking.field_goal)
  + (expected_pats_made        × scoring.kicking.pat)

# PA06 enforcement: if scoring.kicking.missed_fg or missed_pat is non-zero
# (only possible once U05 is resolved), a penalty term is added here.
# Until U05 resolves, these constants remain 0 and NO penalty is applied.
```

### 3c. D_O (Team Defense/Offense/Special Teams)

```text
projected_fantasy_pts =
    (expected_defensive_touchdowns     × scoring.defense_special_teams.defensive_td)
  + (expected_special_teams_touchdowns × scoring.defense_special_teams.special_teams_td)
  + (expected_safeties                 × scoring.defense_special_teams.safety)

# Explicitly forbidden inputs (must not exist in the calculation under any code path):
# points_allowed, sacks, interceptions (standalone), fumble_recoveries (standalone),
# blocked_kicks (standalone) -- confirmed zero-value / not-scored in League Rules Contract v0.2
```

---

## 4. Output Contract

```yaml
scoring_result_id: uuid
projection_id: <references source projection_artifact record>
player_id_or_team_id: canonical_identifier
position: QB | RB | WR | TE | K | D_O
league_rules_version: "spamml-2026-v0.2"
projection_artifact_version: "1.0"
as_of_timestamp_utc: ISO-8601 timestamp   # inherited from source projection, not regenerated

projected_fantasy_pts: nonnegative_float
calculation_breakdown:
  - component: rushing_tds
    raw_value: 0.00
    scoring_constant: 6
    points_contributed: 0.00
  - component: receiving_tds
    raw_value: 0.00
    scoring_constant: 6
    points_contributed: 0.00
  # ... one entry per scoring dimension actually applied for this position type

data_freshness_status: fresh | stale | incomplete   # inherited unchanged from source projection
engine_version: semver_or_git_sha
```

The `calculation_breakdown` array is mandatory, not optional — it is the mechanism by which Devin (or anyone) can answer "why does this player show 42.3 points?" without opening code. This satisfies the explainability requirement without involving the LLM layer at all, since the math itself is the explanation. `design decision`

---

## 5. Acceptance Tests

### SE01 — Zero Hardcoded Constants (BLOCK)
```
Code review / static check: no scoring point value (6, 2, 3, 1, etc.) may appear
as a literal in the scoring engine source code. All constants must be read from
the League Rules Contract YAML at runtime.
```

### SE02 — Forbidden Dimension Absence (BLOCK)
```
Given a projection artifact record with non-null values in points_allowed,
sacks, interceptions, fumble_recoveries, or blocked_kicks fields (if such fields
exist upstream), the scoring engine output must be IDENTICAL to a record
where those fields are null. These dimensions must have zero code path
into the calculation.
```

### SE03 — Manual Calculation Cross-Check (BLOCK)
```
For 10 hand-picked test cases (2 QB, 2 RB, 2 WR, 1 TE, 1 K, 1 D_O, 1 edge case
with a 2pt conversion), engine output must exactly match manual arithmetic
using the confirmed scoring map. Zero tolerance for rounding drift beyond
2 decimal places.
```

### SE04 — Scoring Map Version Change Propagation (BLOCK)
```
If League Rules Contract version changes (e.g., v0.2 -> v0.3 with a resolved
missed_fg penalty), re-running the scoring engine against the same frozen
projection artifact must produce a DIFFERENT projected_fantasy_pts for kickers,
and the output record must cite the new league_rules_version.
```

### SE05 — Calculation Breakdown Completeness (BLOCK)
```
Sum of all points_contributed values in calculation_breakdown must exactly
equal projected_fantasy_pts for every output record.
```

### SE06 — Weekly Prize EV Isolation (BLOCK)
```
weekly_prize_ev fields from the projection artifact must never appear anywhere
in the scoring engine's output or calculation. This is a hard boundary carried
forward from Projection Artifact Contract PA08.
```

### SE07 — Frozen Input Immutability (ADVISORY)
```
Scoring engine must treat its input projection artifact as read-only.
It must not write back to or modify the projection artifact file.
```

---

## 6. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| S01 | 2pt conversion scores identically regardless of pass/rush/catch type per League Rules Contract v0.2 | `confirmed evidence` | None — directly confirmed in league data |
| S02 | Kicker missed_fg/missed_pat constants remain 0 until U05 resolves | `assumption` | LOW — engine is version-aware (SE04) and will auto-correct once U05 resolves and league rules version bumps |
| S03 | D_O scoring is team-level only; no individual defensive player scoring path exists anywhere in this engine | `confirmed evidence` | None — confirmed in League Rules Contract v0.2 (D_O eligibility: TEAM only) |

---

## 7. Builder Handoff

**Ordered work:**
1. Implement scoring map loader that reads directly from `contracts/league_rules/spamml-2026-v0.2.yaml` (no copy/paste of constants into engine code)
2. Implement the three conversion functions (3a, 3b, 3c) as pure functions with no side effects
3. Implement `calculation_breakdown` generation alongside each conversion
4. Run SE01–SE06 as automated test suite; SE07 as a code-review checklist item
5. Submit for Reviewer sign-off

**Done definition:** All SE01–SE06 pass. Engine reads scoring constants exclusively from the League Rules Contract YAML at runtime — verified by static analysis, not just test-passing. `calculation_breakdown` present and summing correctly on every output record.

**What this unlocks:** PRV Calculator can now rank every available player by `projected_fantasy_pts` (a real, traceable, SPAMML-correct value) instead of an imported standard-scoring number. Draft Recommendation Engine can build on top of PRV once this and the Draft Round Order Map are both complete.
