# PRV (Positional Replacement Value) Calculator Contract

**Artifact:** `prv_calculator`
**Version:** 1.0
**Status:** READY FOR BUILDER
**Owner:** Devin Tyler (Architect)
**Builder:** TBD
**Reviewer:** TBD
**Depends On:** League Rules Contract v0.2, Draft Round Order Map Contract v1.0, Projection Artifact Contract v1.0+addendum, Scoring Engine Contract v1.0
**Unlocks:** Draft Recommendation Engine (availability model + slot optimizer)
**Created:** 2026-08-09

---

## 1. Decision Statement

PRV answers one question per available player: **"How many more fantasy points does this player provide over the next-best player I could get at the same roster slot?"** This is the primary ranking signal for the draft optimizer — not raw `projected_fantasy_pts`, not ADP, not positional rank in isolation. A player with a high point total at a deep position can be a worse pick than a lower-scoring player at a scarce position, because the deep-position player's replacement is nearly as good.

This calculator is deterministic and pure: given a `projected_fantasy_pts` value (from the Scoring Engine) for every available player, plus the current draft state, it computes a single `prv_score` per player with zero LLM involvement. `design decision`

---

## 2. Scope and Non-Goals

**In scope:**
- Replacement level calculation per position, correctly scoped to SPAMML's 16-team, 8-slot, no-bench, REC=WR+TE structure
- Static PRV (pre-draft baseline) and dynamic PRV (recalculated as players are drafted and the pool shrinks)
- Position-specific replacement depth derived from actual roster slot counts — not generic 12-team assumptions
- Output contract consumed directly by the Draft Recommendation Engine

**Not in scope:**
- Availability pressure / pick-timing probability (separate module, consumes PRV output but is not part of this contract)
- Roster-fit filtering (e.g., "I already have my QB") — that's a Draft Recommendation Engine responsibility, applied after PRV ranking
- Trade value or in-season waiver PRV (Phase 2 — this contract covers draft-day only)

---

## 3. Replacement Level Definition (SPAMML-specific — do not use generic 12-team defaults)

### 3a. Slot Demand Table

Per League Rules Contract v0.2, 16 teams each draft exactly one of each starter slot, zero bench:

| Position Slot | Teams | Total League Demand | Eligible Player Pool |
|---|---|---|---|
| QB | 16 | 16 | QB only |
| RB1 + RB2 | 16 | 32 | HB or FB (HB typical) |
| REC1 + REC2 + REC3 | 16 | 48 | WR or TE (combined pool — confirmed) |
| KCK | 16 | 16 | K only |
| D_O | 16 | 16 | Full NFL team only |

**Critical distinction from standard leagues:** REC replacement is NOT computed as WR-replacement-only or TE-replacement-only. It is computed against the **combined WR+TE ranked pool**, because any player from either position can fill any of the 3 REC slots. `confirmed evidence` (League Rules Contract v0.2)

### 3b. Static Replacement Rank Formula

```text
For QB:  replacement_rank = 16   (the 16th-best QB by projected_fantasy_pts)
For RB:  replacement_rank = 32   (the 32nd-best RB by projected_fantasy_pts)
For REC: replacement_rank = 48   (the 48th-best player in the COMBINED WR+TE pool)
For KCK: replacement_rank = 16   (the 16th-best K)
For D_O: replacement_rank = 16   (the 16th-best team by projected_fantasy_pts)

replacement_value(position) = projected_fantasy_pts of the player/team at
                               exactly replacement_rank within that position's pool
```

This is the **static baseline PRV**, computed once when the Projection Artifact freezes, before any picks are made.

### 3c. Dynamic Replacement Rank (recalculated during live draft)

As players are drafted, both league-wide slot demand AND the remaining pool shrink. The replacement rank must adjust to reflect **remaining unfilled slots**, not the original 16/32/48/16/16 baseline, once the draft is underway.

```text
remaining_slots(position) = total_league_demand(position) - slots_already_filled(position)

dynamic_replacement_rank(position) = remaining_slots(position)
  # e.g., if 5 of 16 QBs have been drafted league-wide, remaining_slots(QB) = 11,
  # and replacement_value(QB) becomes the 11th-best REMAINING QB in the pool

dynamic_replacement_value(position) = projected_fantasy_pts of the player at
                                       dynamic_replacement_rank within the
                                       CURRENTLY AVAILABLE pool for that position
```

This must be recalculated after every single pick in the draft (128 recalculations total), not just once per round. `design decision`

---

## 4. PRV Score Formula

```text
For any available player P at position slot S:

prv_score(P) = projected_fantasy_pts(P) - dynamic_replacement_value(S)

Where dynamic_replacement_value(S) is computed per Section 3c using ONLY
players/teams currently undrafted and eligible for slot S.
```

**Special case — REC:** Since REC is a combined WR+TE pool, `dynamic_replacement_value(REC)` is computed once against the merged available WR+TE pool, and applies identically whether the candidate player P is a WR or a TE. A TE and a WR with the same `projected_fantasy_pts` have the identical `prv_score` — there is no separate TE-specific replacement baseline. `design decision`

**Special case — D_O:** Replacement pool is all undrafted NFL teams (max 16 total, one per team), scored via the D_O scoring engine output. No sub-position split needed.

---

## 5. Output Contract

```yaml
prv_result_id: uuid
as_of_timestamp_utc: ISO-8601 timestamp   # updated after every pick
pick_number_context: integer              # which pick number this PRV snapshot is valid for
league_rules_version: "spamml-2026-v0.2"
projection_artifact_version: "1.0"
scoring_engine_version: string

player_id_or_team_id: canonical_identifier
position_slot_eligibility: [QB] | [RB] | [WR, TE] | [K] | [TEAM]
projected_fantasy_pts: nonnegative_float

static_replacement_value: nonnegative_float    # baseline, computed once at freeze
dynamic_replacement_value: nonnegative_float   # current, recalculated per pick
static_prv_score: float                        # projected_fantasy_pts - static_replacement_value
dynamic_prv_score: float                       # projected_fantasy_pts - dynamic_replacement_value

remaining_slots_league_wide: integer
remaining_pool_size: integer
scarcity_ratio: float   # remaining_slots_league_wide / remaining_pool_size
                        # >1.0 means demand exceeds supply -- true scarcity signal

rank_within_position: integer   # this player's rank in the combined eligible pool
```

`scarcity_ratio` is the key 16-team-specific addition: in a 16-team league, positions can flip from surplus to scarce mid-draft far faster than in a 10-12 team league, because 16 teams are all competing for the same shallow pool simultaneously. `design decision`

---

## 6. 16-Team Scarcity Behavior (explicit, since this is the core value-add over a generic PRV calculator)

| Position | Static Replacement Rank | Behavior Difference vs. 12-Team League |
|---|---|---|
| QB | 16th best QB | 12-team leagues stop needing QB depth at rank 12; SPAMML needs 4 more QBs drafted, pulling from a shallower remaining tier — QB scarcity hits earlier |
| RB | 32nd best RB | Roughly comparable to a 12-team 2-RB league's replacement depth (24) scaled up; RB remains the deepest relative position |
| REC (WR+TE combined) | 48th best in combined pool | This is the position most affected by the WR+TE merge — the combined pool is larger than either alone, so replacement level is DEEPER than a WR-only 12-team league at the same slot count would suggest |
| KCK | 16th best K | Standard leagues barely draft kickers 12 deep; SPAMML forces all 16 kickers into starting lineups — kicker scarcity is real and often ignored by generic tools |
| D_O | 16th best team | Same logic as kicker — all 16 NFL teams get drafted as D_O, meaning even a mediocre defense/offense combo has real replacement-level value once the top tier is gone |

---

## 7. Acceptance Tests

### PRV01 — REC Combined Pool Correctness (BLOCK)
```
Given a mixed pool of WRs and TEs, dynamic_replacement_value(REC) must be
computed from their MERGED ranking by projected_fantasy_pts, not computed
separately per position and then combined. A test case with a TE ranked
higher than several WRs must place that TE correctly in the merged order.
```

### PRV02 — Static vs. Dynamic Divergence (BLOCK)
```
After simulating 20 picks at a single position (e.g., 20 QBs drafted),
dynamic_replacement_value(QB) must differ from static_replacement_value(QB)
and must reflect the new remaining_slots(QB) = 16 - (QBs drafted so far).
```

### PRV03 — Full Recalculation Per Pick (BLOCK)
```
Simulate a full 128-pick draft using the Draft Round Order Map. Verify that
dynamic_prv_score for every remaining player changes appropriately after
EVERY pick that affects their position's remaining pool -- not just at
round boundaries.
```

### PRV04 — Scarcity Ratio Sanity (BLOCK)
```
When remaining_slots_league_wide > remaining_pool_size for a position
(demand exceeds supply -- true scarcity, e.g., late in draft when good
kickers are gone but teams still need one), scarcity_ratio must be > 1.0
and the position must visibly rank higher in relative PRV terms than its
raw point total alone would suggest.
```

### PRV05 — D_O Single-Pool Correctness (BLOCK)
```
D_O replacement value must be computed against a pool no larger than 16
(one entry per NFL team) minus already-drafted teams. A test with 20+
hypothetical D_O candidates must fail loudly -- this is a data integrity
error, not a valid state.
```

### PRV06 — No Position Cross-Contamination (BLOCK)
```
A QB's dynamic_replacement_value must never be affected by RB, REC, KCK,
or D_O picks, and vice versa -- each position's remaining pool and
replacement calculation is fully independent except for the REC WR+TE merge
explicitly defined in Section 4.
```

### PRV07 — Reproducibility from Frozen Snapshot (BLOCK)
```
Given an identical draft_state, projection_artifact_version, and pick_number_context,
running the PRV calculator twice must produce byte-identical output. This is
the same reproducibility discipline required of the Recommendation Artifact.
```

---

## 8. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| PRV_R01 | Static replacement rank (16/32/48/16/16) assumes no player is drafted outside their primary slot (e.g., no team drafts 2 QBs) | `confirmed evidence` — roster structure enforces exactly 1 per slot, no flex | None — structurally guaranteed by League Rules Contract v0.2 |
| PRV_R02 | Dynamic recalculation after every pick (128 times per draft) may be computationally trivial but must not be batched/approximated to "per round" for speed | `design decision` | HIGH if violated — approximating would reintroduce exactly the staleness risk this contract exists to prevent |
| PRV_R03 | REC combined-pool merge assumes TE and WR `projected_fantasy_pts` are computed on a fully comparable basis (same Scoring Engine, same units) | `confirmed evidence` — guaranteed by Scoring Engine Contract v1.0 applying identical constants regardless of position | None |

---

## 9. Builder Handoff

**Ordered work:**
1. Implement static replacement value calculator (Section 3b) — run once at Projection Artifact freeze time
2. Implement dynamic replacement value calculator (Section 3c) — must accept current `draft_state` as input
3. Implement PRV score formula (Section 4), including the REC merged-pool special case
4. Implement `scarcity_ratio` calculation
5. Wire recalculation trigger to fire after every single pick entered into `draft_state` (not batched)
6. Run PRV01–PRV07 as automated test suite, including a full 128-pick simulated draft for PRV03
7. Submit for Reviewer sign-off

**Done definition:** All PRV01–PRV07 pass, including the full-draft simulation test. Output contract fields all populate correctly for a real Scoring Engine output sample across all 5 position types.

**What this unlocks:** Draft Recommendation Engine — the final piece before a working draft-day tool. It layers roster-fit filtering and availability-pressure weighting on top of `dynamic_prv_score` to produce the actual pick-by-pick recommendation payload defined in the original Draft-Day Decision Model.
