# Draft Recommendation Engine Contract

**Artifact:** `draft_recommendation_engine`
**Version:** 1.0
**Status:** READY FOR BUILDER
**Owner:** Devin Tyler (Architect)
**Builder:** TBD
**Reviewer:** TBD
**Depends On:** League Rules Contract v0.2, Draft Round Order Map Contract v1.0, Projection Artifact Contract v1.0+addendum, Scoring Engine Contract v1.0, PRV Calculator Contract v1.0
**Unlocks:** Live-Draft Degraded Mode Runbook, MVP Acceptance Gates, Streamlit Draft UI
**Created:** 2026-08-09

---

## 1. Decision Statement

This is the last deterministic artifact before draft-day usability exists. It takes PRV Calculator output, filters it against Devin's actual remaining roster needs, weights it by how likely each candidate is to survive until his next pick, and emits a ranked recommendation with alternatives and machine-readable reason codes. The LLM explanation layer (out of scope here) consumes this contract's output verbatim — it narrates, it never re-ranks. `design decision`

The engine is triggered once per Devin's pick (8 times total across the draft), not once per every league pick (128 times) — though its internal PRV dependency does update on all 128, per PRV Calculator Contract PRV03.

---

## 2. Scope and Non-Goals

**In scope:**
- Roster-fit filtering: exclude any player whose only eligible slot(s) are already filled on Devin's roster
- Availability pressure model: probability each top candidate survives to Devin's next pick, using `get_picks_between()` from the Draft Round Order Map
- Positional run detection: flag when 3+ consecutive league-wide picks hit the same position
- Final ranked recommendation with primary pick + 2 alternatives
- Machine-readable `reason_codes` array — the sole interface to the LLM explanation layer
- Full reproducibility from a frozen snapshot (same inputs → same output, always)

**Not in scope:**
- The LLM explanation layer itself (separate, downstream, consumes this contract's output)
- Weekly waiver/trade recommendations (Phase 2 — this contract is draft-day only)
- Any UI rendering (Streamlit Draft UI is a separate build item)
- Auto-pick or auto-draft functionality — this engine recommends only; a human enters every pick manually per League Rules Contract v0.2 (no platform API exists)

---

## 3. Inputs (all frozen or live per their own contracts)

```yaml
inputs:
  league_rules: spamml-2026-v0.2.yaml           # roster slots, eligibility
  draft_round_order_map: v1.0                    # get_pick_numbers(), get_draft_position(), get_picks_between()
  projection_artifact: v1.0 + v1.1 addendum      # frozen at draft_start_timestamp
  scoring_engine_output: v1.0                     # projected_fantasy_pts per player
  prv_calculator_output: v1.0                     # dynamic_prv_score, scarcity_ratio, updated per pick
  draft_state:
    picks_made: list[{pick_number, player_id_or_team_id, position_slot}]
    my_roster: list[{position_slot, player_id_or_team_id, pick_number_used}]
    my_draft_position: integer (1-16)             # unknown per U01 until assigned
    current_pick_number: integer
  user_strategy_controls:
    positional_priority: unknown (U-flagged, not yet provided)
    d_o_strategy: unknown (U-flagged)
    te_premium: unknown (U-flagged)
```

**Note:** `my_draft_position` (U01) remains unresolved. This contract is fully specified and buildable without it — the engine reads `my_draft_position` from `draft_state` at runtime, so it works correctly whenever Devin's 2026 slot is assigned, with zero contract changes needed. `design decision`

---

## 4. Core Calculation Sequence

```text
Step 1: ROSTER-FIT FILTER
  open_slots = all League Rules Contract roster slots NOT YET present in my_roster
  eligible_candidates = all undrafted players/teams whose position_slot_eligibility
                        intersects open_slots
  # A player eligible ONLY for a filled slot (e.g., a 2nd QB when QB is filled)
  # is excluded entirely from this pick's candidate list.

Step 2: PRV RANKING
  ranked_candidates = eligible_candidates sorted by dynamic_prv_score descending
  # Pulled directly from PRV Calculator Contract output, current as of this pick

Step 3: AVAILABILITY PRESSURE
  next_pick_number = the next pick_number in get_pick_numbers(my_draft_position)
                      after current_pick_number
  picks_before_next_turn = get_picks_between(current_pick_number, my_draft_position)
  picks_remaining_count = len(picks_before_next_turn)

  For each candidate C in top 15 of ranked_candidates:
    survival_pressure(C) = f(picks_remaining_count, C's position scarcity_ratio,
                              C's rank_within_position)
    # Higher picks_remaining_count + higher scarcity_ratio + poor rank_within_position
    # => LOWER survival probability => HIGHER urgency to draft now
    availability_pressure(C) = categorize as low | medium | high
    # low = likely available next turn; high = likely gone before next turn

Step 4: POSITIONAL RUN DETECTION
  last_5_league_picks = picks_made[-5:] (or fewer if early in draft)
  If 3+ of the last 5 picks share the same position_slot category:
    positional_run_flag = true, run_position = that position
  Else:
    positional_run_flag = false

Step 5: FINAL SCORE AND RANK
  final_score(C) = dynamic_prv_score(C) × availability_pressure_weight(C)
  # availability_pressure_weight: high=1.15, medium=1.0, low=0.9
  # (weights are an initial hypothesis -- tune during backtest, not fixed forever)

  primary_recommendation = candidate with highest final_score
  alternatives = next 2 candidates by final_score (may span different positions)

Step 6: REASON CODE ASSIGNMENT
  Attach applicable reason_codes (see Section 5) to primary_recommendation
  based on which factors most influenced its ranking
```

---

## 5. Reason Code Vocabulary (closed set — Builder must not invent new codes without an Architect contract update)

| Code | Trigger Condition |
|---|---|
| `positional_scarcity` | Candidate's position has `scarcity_ratio > 1.0` |
| `rec_combined_pool_value` | Candidate is a TE ranked above several available WRs in the merged REC pool |
| `high_availability_pressure` | `availability_pressure: high` — unlikely to survive to next pick |
| `positional_run_detected` | `positional_run_flag: true` and candidate's position matches `run_position` |
| `kicker_scarcity_reminder` | KCK position `scarcity_ratio` crosses a Builder-documented threshold, since kicker scarcity is easy to underrate |
| `d_o_prize_ev_signal` | D_O candidate has notably high `weekly_prize_ev` values per Projection Artifact Contract Section 6c (informational — never affects `dynamic_prv_score` itself) |
| `pass_funnel_risk` | Candidate's team carries the `game_script_flag: pass_funnel_risk` from Projection Artifact Contract v1.1 addendum |
| `last_slot_urgency` | This is one of Devin's final 1-2 remaining open slots with few picks left in the draft |
| `roster_fit_only_option` | Fewer than 3 eligible candidates remain for an open slot — flags real scarcity risk, not just preference |

---

## 6. Output Contract

```yaml
recommendation_id: uuid
as_of_timestamp_utc: ISO-8601 timestamp
snapshot_id: immutable_identifier   # ties this recommendation to a specific frozen state
draft_id: identifier
pick_number: integer
my_draft_position: integer

league_rules_version: "spamml-2026-v0.2"
projection_artifact_version: "1.0"
scoring_engine_version: string
prv_calculator_version: "1.0"
engine_version: semver_or_git_sha

primary_recommendation:
  player_id_or_team_id: canonical_identifier
  position_slot: QB | RB1 | RB2 | REC1 | REC2 | REC3 | KCK | D_O
  projected_fantasy_pts: nonnegative_float
  dynamic_prv_score: float
  final_score: float
  availability_pressure: low | medium | high
  reason_codes: [array from Section 5 closed set]

alternatives:
  - player_id_or_team_id: canonical_identifier
    position_slot: string
    dynamic_prv_score: float
    final_score: float
    reason_codes: [array]
  - player_id_or_team_id: canonical_identifier
    position_slot: string
    dynamic_prv_score: float
    final_score: float
    reason_codes: [array]

open_slots_remaining: [array of unfilled position_slot values]
positional_run_flag: boolean
run_position: null_or_string
data_freshness_status: fresh | stale | incomplete
known_limitations: [array of strings, e.g. "my_draft_position not yet confirmed (U01)"]
```

---

## 7. Explanation Layer Boundary (binding constraint)

The LLM explanation layer receives this contract's output and ONLY this contract's output. It may:
- Convert `reason_codes` into a 2-3 sentence natural-language rationale
- Reference `projected_fantasy_pts`, `dynamic_prv_score`, and `availability_pressure` values verbatim
- Flag `known_limitations` in plain language

It may NOT:
- Re-rank `primary_recommendation` vs. `alternatives`
- Introduce any player, team, or reason not present in this output
- Adjust `final_score`, `dynamic_prv_score`, or any numeric field
- Speculate about player performance beyond what `reason_codes` support

This boundary is the direct implementation of the shared doctrine: "LLMs plan, extract bounded facts, orchestrate, and explain. Deterministic services... make recommendations." `design decision`

---

## 8. Acceptance Tests

### DR01 — Roster-Fit Exclusion Correctness (BLOCK)
```
Given my_roster already has a QB filled, no QB may appear anywhere in
primary_recommendation or alternatives for the remainder of the draft.
```

### DR02 — Availability Pressure Uses Correct Pick Gap (BLOCK)
```
Given my_draft_position=11 and current_pick_number=11, availability_pressure
calculations must use get_picks_between(11, 11) = 10 picks (per Draft Round
Order Map ground truth), not a generic "half the league size" approximation.
```

### DR03 — Reason Code Closed-Set Compliance (BLOCK)
```
Every reason_code emitted must be a member of the Section 5 closed set.
Any code not in that list must fail validation, not pass through silently.
```

### DR04 — REC Combined Pool Reflected in Recommendation (BLOCK)
```
Given a TE with a higher dynamic_prv_score than several available WRs,
the engine must recommend that TE for an open REC slot and attach
rec_combined_pool_value if applicable -- confirming PRV Calculator's
merged-pool logic flows through correctly to this layer.
```

### DR05 — D_O Prize EV Never Affects Ranking (BLOCK)
```
Two D_O candidates with identical dynamic_prv_score but different
weekly_prize_ev values must receive IDENTICAL final_score. Prize EV may
only appear in reason_codes as d_o_prize_ev_signal, never in the scoring math.
```

### DR06 — Reproducibility From Frozen Snapshot (BLOCK)
```
Given an identical snapshot_id, draft_state, and all versioned inputs,
running the engine twice must produce a byte-identical recommendation_id
payload (excluding the recommendation_id itself and as_of_timestamp_utc).
```

### DR07 — Last-Slot Urgency Trigger (BLOCK)
```
With exactly 1 open slot remaining and fewer than 3 eligible candidates left
in the pool, primary_recommendation must carry last_slot_urgency and/or
roster_fit_only_option in reason_codes.
```

### DR08 — Explanation Layer Cannot Re-Rank (ADVISORY — enforced at integration, not unit test)
```
Integration test: feed identical recommendation output to the LLM explanation
layer twice. Verify the narrated text differs (natural language variation is
fine) but primary_recommendation identity never changes across LLM calls.
```

---

## 9. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| DR_R01 | availability_pressure_weight values (1.15/1.0/0.9) are an initial hypothesis, not backtested | `assumption` | MEDIUM — flag for tuning once a backtest harness exists against 2025 draft outcomes |
| DR_R02 | Positional run detection threshold (3 of last 5 picks) is a starting heuristic | `assumption` | LOW — easy to adjust without contract restructuring |
| DR_R03 | User strategy controls (positional_priority, d_o_strategy, te_premium) are all unconfirmed (U-flagged) — engine currently treats them as unset/neutral | `unknown` | MEDIUM — if Devin has strong priors (e.g., "always take D_O last"), this contract needs an addendum before draft day to incorporate them as a filter or weight |
| DR_R04 | This contract assumes my_draft_position will be known before draft_start_timestamp is set; if unknown mid-draft somehow, engine has no defined fallback | `design decision` | LOW — practically impossible scenario since draft position is always known before the draft begins |

---

## 10. Builder Handoff

**Ordered work:**
1. Implement roster-fit filter (Step 1)
2. Implement PRV ranking pass-through (Step 2) — consumes PRV Calculator output directly, no re-derivation
3. Implement availability pressure model (Step 3) using Draft Round Order Map's `get_picks_between()`
4. Implement positional run detection (Step 4)
5. Implement final score + ranking (Step 5)
6. Implement reason code assignment (Step 6) against the closed set in Section 5
7. Run DR01–DR07 as automated tests; DR08 as an integration test once the LLM explanation layer exists
8. Submit for Reviewer sign-off

**Done definition:** All DR01–DR07 pass. A full simulated draft (reusing the PRV Calculator's 128-pick test harness) produces 8 valid recommendation payloads at Devin's exact pick numbers with correctly populated reason codes.

**What this unlocks:** This is the last decision-logic contract needed for a complete draft-day tool. Remaining work per the original build sequence is the Live-Draft Degraded Mode Runbook (manual entry procedures, stale-data handling) and the MVP Acceptance Gates test suite — both process/documentation artifacts, not new modeling logic. After those, the Streamlit Draft UI is the final implementation item.
