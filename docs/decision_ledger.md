# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 2.2 — 2026-08-10
**Change:** Corrected a genuine Architect authoring error Builder caught during B-04 implementation. The original Draft Round Order Map Contract's T09 test and Section 4b JSON example contained fabricated placeholder pick numbers for positions 1, 2, and 16 that were never actually run through the Section 5 algorithm -- they contradicted the algorithm even though the algorithm itself was correct (already validated against 2025 ground truth for position 11). Corrected values independently verified via: (1) direct algorithm computation, (2) ground-truth cross-check (position 11 unchanged, still matches real 2025 data), (3) internal invariant sum checks (R1+R2=33, R3+R4=97, R5+R6=161, R7+R8=225 for every position), (4) full 128-pick uniqueness across all 16 positions. Added new test T12 (invariant sum check) specifically to catch this class of error faster in the future. Updated the test scaffold file directly.

**Type:** Calibration (fixes a test/documentation error; the algorithm and all previously-passing tests, including T01 ground truth, required zero changes)

**Impact on build sequence:**
- B-04 unblocked: Builder's implementation of Section 5 was correct all along; only the test file needed correction
- Section 7 process correction applied: all future contract numeric examples must be independently computed before being written, not estimated by pattern-matching
- Positive signal, second time in two exchanges: Builder correctly refused to force a passing test by weakening T05/T09 or hardcoding an exception -- this is exactly the discipline the Architect-Builder-Reviewer gate exists to enforce
- Reviewer's future audit scope should explicitly include re-deriving embedded numeric examples in contracts, not just confirming tests exist

**Highest-leverage next artifact:** None at the architecture layer. Builder proceeds with B-04: commit `engine/draft/round_order_map.py`, the two `data/processed/` artifacts (using `league_rules_version: spamml-2026-v0.3` per the prior v1.1 clarification), and the corrected test scaffold, then open the PR for Reviewer.

---

### Version 2.1 — 2026-08-10
**Change:** Resolved a Builder-surfaced version-binding ambiguity (league_rules_version).
**Type:** Calibration

---

### Version 2.0 — 2026-08-10
**Change:** Produced Builder/Operator Implementation Backlog v1.0 and Builder Kickoff Prompt.
**Type:** Structural

---

### Version 1.5 — 2026-08-10
**Change:** Produced MVP Acceptance Gates v1.0.
**Type:** Structural

---

### Version 1.4 — 2026-08-10
**Change:** Resolved U03 (pick timer) via League Rules Contract v0.3.
**Type:** Calibration

---

### Version 1.3 — 2026-08-10
**Change:** Produced Live-Draft Degraded Mode Runbook v1.0.
**Type:** Structural

---

### Version 1.2 — 2026-08-10
**Change:** Added soft KCK/D_O guardrail and snooze-for-1-round capability.
**Type:** Structural

---

### Version 1.1 — 2026-08-10
**Change:** Resolved DR_R03 (user strategy controls).
**Type:** Calibration

---

### Version 1.0 — 2026-08-09
**Change:** Produced Draft Recommendation Engine Contract v1.0.
**Type:** Structural

---

### Version 0.9 — 2026-08-09
**Change:** Produced PRV Calculator Contract v1.0.
**Type:** Structural

---

### Version 0.8 — 2026-08-09
**Change:** Resolved D07 via Projection Artifact Contract v1.1 addendum.
**Type:** Calibration

---

### Version 0.7 — 2026-08-09
**Change:** Ingested 2026 team-environment projections and 2025 calibration statistics.
**Type:** Calibration

---

### Version 0.6 — 2026-08-09
**Change:** Produced Scoring Engine Contract v1.0.
**Type:** Calibration

---

### Version 0.5 — 2026-08-09
**Change:** Produced Projection Artifact Contract v1.0.
**Type:** Structural

---

### Version 0.4 — 2026-08-09
**Change:** Locked Data Source and Connector Register v1.0/v1.1/v1.2.
**Type:** Structural

---

### Version 0.3 — 2026-08-09
**Change:** Produced Draft Round Order Map Contract v1.0.
**Type:** Structural

---

### Version 0.2 — 2026-08-09
**Change:** Locked League Rules Contract v0.2.
**Type:** Structural

---

### Version 0.1 — 2026-08-09
**Change:** Established first-league MVP architecture.
**Type:** Structural
