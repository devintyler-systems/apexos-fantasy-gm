# Draft Round Order Map Contract — v1.2 Correction

**Resolves:** Builder-surfaced contradiction between T05/T06 (pivot algorithm) and T09 (edge position validation)
**Supersedes:** T09 assertions and the Section 4b JSON example values for positions 1, 2, and 16 in `draft-round-order-map-contract-v1.0.md`
**Status:** APPROVED — root cause confirmed, corrected values verified
**Created:** 2026-08-10

---

## 1. Decision Statement

**Option 1: Correct T09 to match the Section 5 algorithm.** The algorithm and the T05/T06 pivot-sequence tests are correct — they are independently validated against the confirmed 2025 ground truth (position 11's actual picks: 11, 22, 35, 62, 75, 86, 99, 126). T09's stated values for positions 1, 2, and 16 were never actually derived from the algorithm; they were fabricated placeholder numbers written directly into the Section 4b JSON illustration and then mistakenly copied into T09 as if they were verified outputs. This is an Architect authoring error, not a Builder error, and not a flaw in the algorithm itself. `confirmed evidence` (verified by independent computation, see Section 3)

---

## 2. Root Cause

When the original contract was authored, Section 4b's JSON example needed illustrative `position_pick_map` values to show the schema shape. Position 11 was correctly sourced from real 2025 draft data. Positions 1, 2, and 16 were typed in by hand as "looks plausible" placeholder numbers to fill out the example — never actually run through the Section 5 algorithm to verify correctness. T09 ("Edge Position Validation") was then written by copying those same unverified placeholder numbers, creating a test that validated against itself rather than against the algorithm. Builder correctly implemented Section 5 exactly as specified, got a different (correct) answer, and flagged the contradiction instead of silently picking a side. This is precisely the escalation behavior required by the kickoff prompt. `confirmed evidence`

---

## 3. Corrected Values (independently verified: ground truth match + internal invariant checks + full 128-pick uniqueness)

```text
get_pick_numbers(1)  == [1, 32, 41, 56, 65, 96, 105, 120]   (was incorrectly stated as [1, 32, 40, 57, 65, 96, 104, 121])
get_pick_numbers(2)  == [2, 31, 42, 55, 66, 95, 106, 119]   (was incorrectly stated as [2, 31, 41, 56, 66, 95, 105, 120])
get_pick_numbers(11) == [11, 22, 35, 62, 75, 86, 99, 126]   (UNCHANGED -- this was always correct, ground-truth sourced)
get_pick_numbers(16) == [16, 17, 40, 57, 80, 81, 104, 121]  (was incorrectly stated as [16, 17, 44, 49, 80, 81, 108, 113])
```

**Verification method applied before approving these corrected values:**
1. Computed directly from the Section 5 algorithm (pivot sequence `[9,10,11,12,13,14,15,16,1,2,3,4,5,6,7,8]`, reverse-pivot sequence `[8,7,6,5,4,3,2,1,16,15,14,13,12,11,10,9]`) — no shortcuts, no hardcoding
2. Cross-checked against confirmed 2025 ground truth for position 11 — exact match, unchanged
3. Internal invariant check: for every position, R1+R2 picks sum to 33, R3+R4 sum to 97, R5+R6 sum to 161, R7+R8 sum to 225 (these sums are a structural property of any symmetric snake/pivot pattern across a 16-team round) — all four positions (1, 2, 11, 16) satisfy this
4. Full-map uniqueness check: computing all 128 picks across all 16 positions produces every integer 1–128 exactly once, with zero duplicates or gaps

---

## 4. Corrected T09 (replaces the version in `draft-round-order-map-contract-v1.0.md` Section 6)

```python
class TestEdgePositions:
    """T09 -- Validate most extreme draft positions."""

    def test_position_1_picks(self):
        assert get_pick_numbers(1) == [1, 32, 41, 56, 65, 96, 105, 120]

    def test_position_2_picks(self):
        assert get_pick_numbers(2) == [2, 31, 42, 55, 66, 95, 106, 119]

    def test_position_16_picks(self):
        assert get_pick_numbers(16) == [16, 17, 40, 57, 80, 81, 104, 121]
```

---

## 5. Corrected Section 4b JSON Example (replaces the illustrative map in the base contract)

```json
"position_pick_map": {
    "1":  [1, 32, 41, 56, 65, 96, 105, 120],
    "2":  [2, 31, 42, 55, 66, 95, 106, 119],
    "11": [11, 22, 35, 62, 75, 86, 99, 126],
    "16": [16, 17, 40, 57, 80, 81, 104, 121]
}
```

---

## 6. Acceptance Test Addition

### T12 — Invariant Sum Check (BLOCK, new)
```
For every draft_position 1-16, the sum of its Round1+Round2 picks must equal 33,
Round3+Round4 picks must equal 97, Round5+Round6 picks must equal 161, and
Round7+Round8 picks must equal 225. This is a structural property of the
confirmed round pattern and provides a fast, position-independent sanity
check that catches exactly this class of error (a plausible-looking but
unverified pick number) before it reaches T01 ground-truth-style validation.
```

---

## 7. Process Correction (prevents recurrence)

Going forward, any numeric example embedded in a contract (JSON schema illustrations, sample outputs, etc.) MUST be independently computed and verified before being written — not typed in as "looks about right." This applies retroactively as a review requirement for any future contract corrections and prospectively for all new contracts. Reviewer's audit scope should explicitly include re-deriving embedded numeric examples, not just checking that acceptance tests exist. `design decision`

---

## 8. Builder Unblock Confirmation

Builder is cleared to proceed with the B-04 branch exactly as previously scoped. Section 5's algorithm is confirmed correct and requires no code changes from what Builder already implemented (T01 passing for position 11 confirms this). Only the T09 test file and the Section 4b JSON documentation example needed correction — both are now fixed in this document. Add T12 as an additional test. Commit and proceed to opening the PR.

---

## 9. Decision Ledger Entry

This is a calibration fix to a documentation/test authoring error, not a structural algorithm change. Builder's refusal to "encode exceptions, hardcode position-specific picks, or weaken T05/T09 to force a pass" was exactly correct and is the reason this bug was caught before it reached committed code or a live draft.
