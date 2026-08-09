# Draft Round Order Map Contract

**Artifact:** `draft_round_order_map`  
**Version:** 1.0  
**Status:** READY FOR BUILDER  
**Owner:** Devin Tyler (Architect)  
**Builder:** TBD  
**Reviewer:** TBD  
**Depends On:** `spamml-2026-v0.2.yaml` (League Rules Contract)  
**Unlocks:** PRV Calculator, Availability Model, Draft State Manager, Draft UI pick-slot display  
**Created:** 2026-08-09  

---

## 1. Decision Statement

The SPAMML draft uses a non-standard snake that pivots mid-draft. A generic snake encoder
will produce wrong pick numbers for rounds 3–4 and 7–8. The optimizer cannot compute
"what is available at my next pick" without a deterministic, version-locked pick sequence
for every possible draft position (1–16). This contract defines the algorithm, output
schema, acceptance tests, and file location for that map.

---

## 2. Scope and Non-Goals

**In scope:**
- Encode the confirmed non-standard snake algorithm for a 16-team, 8-round draft
- Produce a complete 128-pick lookup table: `pick_number → draft_position`
- Produce the inverse map: `draft_position → [pick_1, pick_2, ..., pick_8]`
- Validate the map against confirmed 2025 ground truth (Professor FleX at position 11
  picked: 11, 22, 35, 62, 75, 86, 99, 126)
- Emit the map as both a CSV artifact and a Python dict for engine consumption
- Handle all 16 possible draft positions, not just position 11

**Not in scope:**
- Draft pick trading (unknown — see U04 in Assumptions Register)
- Conditional pick reordering mid-draft (not confirmed in league rules)
- Any platform sync or live draft-order detection
- Playoff seeding or waiver priority derived from draft order

---

## 3. Confirmed Draft Format

Source: `spamml-2026-v0.2.yaml` + 2025 PF.pdf draft order sheet. `confirmed evidence`

```
League size:  16 teams
Total rounds: 8  (no bench — each pick is a starter)
Total picks:  128

Teams are numbered 1–16 by their assigned draft position for that season.
The draft pivot is keyed to the team holding position 9 in the current year's order.

Round 1  (picks   1– 16): Forward  — positions  1 → 16
Round 2  (picks  17– 32): Reverse  — positions 16 →  1
Round 3  (picks  33– 48): PIVOT    — positions  9 → 16, then 1 → 8
Round 4  (picks  49– 64): Reverse of Round 3 — positions 8 → 1, then 16 → 9
Round 5  (picks  65– 80): Forward  — positions  1 → 16  (standard snake resumes)
Round 6  (picks  81– 96): Reverse  — positions 16 →  1
Round 7  (picks  97–112): PIVOT    — positions  9 → 16, then 1 → 8  (same as Rd 3)
Round 8  (picks 113–128): Reverse of Round 7 — positions 8 → 1, then 16 → 9

Ground truth validation (draft position 11, 2025 season):
  Rd1 pick  11  ✓  (position 11, forward)
  Rd2 pick  22  ✓  (position 11 → slot 6 in reverse = pick 16+6=22)
  Rd3 pick  35  ✓  (position 11 → slot 3 in pivot sequence = pick 32+3=35)
  Rd4 pick  62  ✓  (position 11 → slot 14 in reverse pivot = pick 48+14=62)
  Rd5 pick  75  ✓  (position 11 → slot 11 forward = pick 64+11=75)
  Rd6 pick  86  ✓  (position 11 → slot 6 reverse = pick 80+6=86)
  Rd7 pick  99  ✓  (position 11 → slot 3 pivot = pick 96+3=99)
  Rd8 pick 126  ✓  (position 11 → slot 14 reverse pivot = pick 112+14=126)
```

**Pivot sequence definition (rounds 3 and 7):**
```
Slot within round:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
Draft position:     9  10  11  12  13  14  15  16   1   2   3   4   5   6   7   8
```

**Reverse pivot sequence definition (rounds 4 and 8):**
```
Slot within round:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
Draft position:     8   7   6   5   4   3   2   1  16  15  14  13  12  11  10   9
```

---

## 4. Output Contracts

### 4a. Full Pick Table (CSV)

**File:** `data/processed/draft_round_order_map_spamml_2026.csv`

```
Columns:
  pick_number       integer  1–128
  round_number      integer  1–8
  slot_in_round     integer  1–16
  draft_position    integer  1–16  (which team picks here)
  round_type        string   forward | reverse | pivot | reverse_pivot
```

Example rows (position 11 picks highlighted):
```csv
pick_number,round_number,slot_in_round,draft_position,round_type
1,1,1,1,forward
...
11,1,11,11,forward
...
22,2,6,11,reverse
...
35,3,3,11,pivot
...
```

### 4b. Position Pick Map (JSON — primary engine artifact)

**File:** `data/processed/draft_position_pick_map_spamml_2026.json`

```json
{
  "artifact_id": "draft_round_order_map_spamml_2026",
  "version": "1.0",
  "league_rules_version": "spamml-2026-v0.2",
  "league_size": 16,
  "total_rounds": 8,
  "total_picks": 128,
  "as_of_timestamp": "<ISO8601 timestamp of generation>",
  "position_pick_map": {
    "1":  [1, 32, 40, 57, 65, 96, 104, 121],
    "2":  [2, 31, 41, 56, 66, 95, 105, 120],
    ...
    "11": [11, 22, 35, 62, 75, 86, 99, 126],
    ...
    "16": [16, 17, 44, 49, 80, 81, 108, 113]
  },
  "pick_to_position_map": {
    "1": 1,
    "2": 2,
    ...
    "128": 9
  }
}
```

### 4c. Python Module (engine import)

**File:** `engine/draft/round_order_map.py`

```python
# Public interface — Builder implements internals

def get_pick_numbers(draft_position: int) -> list[int]:
    """
    Returns the 8 pick numbers for a given draft position (1-16).
    Example: get_pick_numbers(11) == [11, 22, 35, 62, 75, 86, 99, 126]
    Raises ValueError if draft_position not in 1–16.
    """
    ...

def get_draft_position(pick_number: int) -> int:
    """
    Returns the draft position that owns a given pick number (1-128).
    Example: get_draft_position(35) == 11
    Raises ValueError if pick_number not in 1–128.
    """
    ...

def get_picks_between(current_pick: int, my_draft_position: int) -> list[int]:
    """
    Returns all pick numbers between current_pick (exclusive) and my next pick.
    Used by availability pressure model to count how many picks fire before my next turn.
    Example: get_picks_between(11, 11) == [12, 13, ..., 21]  → 10 picks until my next turn
    """
    ...

def build_full_map() -> dict:
    """
    Returns the full position_pick_map and pick_to_position_map as a single dict.
    Used at startup to hydrate in-memory lookup for the optimizer.
    """
    ...
```

---

## 5. Algorithm Specification

Builder must implement the following deterministic sequence generator. No randomness.
No external input at generation time beyond `league_size=16`.

```
ROUND_PATTERNS = [
  round 1: forward          positions [1..16]
  round 2: reverse          positions [16..1]
  round 3: pivot            positions [9..16, 1..8]
  round 4: reverse_pivot    positions [8..1, 16..9]
  round 5: forward          positions [1..16]
  round 6: reverse          positions [16..1]
  round 7: pivot            positions [9..16, 1..8]
  round 8: reverse_pivot    positions [8..1, 16..9]
]

For each round r (1–8):
  base_pick = (r - 1) * 16
  For each slot s (1–16):
    pick_number = base_pick + s
    draft_position = ROUND_PATTERNS[r][s]
    emit: (pick_number, r, s, draft_position, round_type)
```

This fully specifies the map. No heuristics, no conditionals beyond the above.

---

## 6. Acceptance Tests

All tests must pass before this artifact is considered DONE.
Failing any test blocks the PRV Calculator and Availability Model.

### T01 — Ground Truth Validation (BLOCK)
```
Assert: get_pick_numbers(11) == [11, 22, 35, 62, 75, 86, 99, 126]
Source: Confirmed 2025 Professor FleX actual picks from PF.pdf
```

### T02 — Total Pick Count (BLOCK)
```
Assert: len(all pick_numbers in map) == 128
Assert: all pick_numbers are unique integers 1–128
```

### T03 — Total Position Coverage (BLOCK)
```
Assert: every draft_position 1–16 appears exactly 8 times across all 128 picks
```

### T04 — Round Coverage (BLOCK)
```
Assert: every round 1–8 contains exactly 16 picks
Assert: each round contains each draft_position exactly once
```

### T05 — Pivot Round Correctness (BLOCK)
```
Assert: picks 33–48 map to positions [9,10,11,12,13,14,15,16,1,2,3,4,5,6,7,8] in order
Assert: picks 97–112 map to positions [9,10,11,12,13,14,15,16,1,2,3,4,5,6,7,8] in order
```

### T06 — Reverse Pivot Round Correctness (BLOCK)
```
Assert: picks 49–64 map to positions [8,7,6,5,4,3,2,1,16,15,14,13,12,11,10,9] in order
Assert: picks 113–128 map to positions [8,7,6,5,4,3,2,1,16,15,14,13,12,11,10,9] in order
```

### T07 — Inverse Map Consistency (BLOCK)
```
For every (pick_number, draft_position) in full map:
  Assert: get_draft_position(pick_number) == draft_position
  Assert: pick_number in get_pick_numbers(draft_position)
```

### T08 — get_picks_between Correctness (BLOCK)
```
Assert: get_picks_between(11, 11) == [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
# 10 picks fire between pick 11 and pick 22 (Professor FleX's next turn)

Assert: get_picks_between(22, 11) == [23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
         33, 34]  # 12 picks fire between pick 22 and pick 35
```

### T09 — Edge Position Validation (BLOCK)
```
Assert: get_pick_numbers(1)  == [1, 32, 40, 57, 65, 96, 104, 121]
Assert: get_pick_numbers(16) == [16, 17, 44, 49, 80, 81, 108, 113]
# These are the most extreme positions — longest and shortest waits
```

### T10 — ValueError on Out-of-Range Input (ADVISORY)
```
Assert: get_pick_numbers(0)   raises ValueError
Assert: get_pick_numbers(17)  raises ValueError
Assert: get_draft_position(0)   raises ValueError
Assert: get_draft_position(129) raises ValueError
```

---

## 7. Reviewer Checklist

Reviewer confirms before marking artifact DONE:

- [ ] T01–T09 all pass (automated)
- [ ] `get_picks_between` returns an empty list (not error) if called on the last pick of the draft
- [ ] JSON artifact includes `as_of_timestamp` and `league_rules_version` fields
- [ ] CSV artifact is deterministic: same output on repeated runs with no external input
- [ ] Python module has no side effects on import
- [ ] No hardcoded pick numbers — all values derived from the algorithm above
- [ ] Position 9 is confirmed as the pivot start position (not hardcoded as team name)

---

## 8. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| R01 | Pivot always starts at position 9 regardless of which team holds that slot | `confirmed evidence` | Low — derived from 2025 actual picks with full 16-team order visible |
| R02 | 2026 draft uses same round pattern as 2025 | `assumption` | HIGH — if league changes format, map must be rebuilt from new ground truth |
| R03 | Draft position numbering is 1-indexed and stable during the draft | `assumption` | Medium — if positions renumber mid-draft (e.g., trade), map is invalid for that pick |
| R04 | Position 9 pivot applies to all future SPAMML seasons until confirmed otherwise | `assumption` | Medium — architect must re-validate before each season |

---

## 9. Builder Handoff

**Ordered work:**
1. Implement `build_full_map()` using the algorithm in Section 5
2. Validate T01 first — if ground truth fails, stop and report to Architect before proceeding
3. Run T02–T09 as an automated test suite (`tests/acceptance/test_draft_round_order_map.py`)
4. Emit CSV to `data/processed/draft_round_order_map_spamml_2026.csv`
5. Emit JSON to `data/processed/draft_position_pick_map_spamml_2026.json`
6. Implement public Python interface in `engine/draft/round_order_map.py`
7. Submit for Reviewer sign-off using the checklist in Section 7

**Done definition:**  
All T01–T09 pass. JSON and CSV artifacts exist in `data/processed/`. Python module
imports cleanly with no side effects. Reviewer checklist complete. Pick map for all
16 positions filed in repo.

**What this unlocks:**  
- PRV Calculator can compute replacement depth per position accounting for actual pick gaps  
- Availability Model can calculate picks-until-my-next-turn for any draft state  
- Draft UI can display "your next pick: #XX (N picks away)" accurately  
- Draft State Manager can validate pick sequence integrity during live draft entry
