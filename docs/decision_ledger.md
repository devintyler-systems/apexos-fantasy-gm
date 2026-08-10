# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 1.3 — 2026-08-10
**Change:** Produced Live-Draft Degraded Mode Runbook v1.0. Documents that manual entry IS the permanent operating mode for SPAMML (no API exists), not a rare-failure fallback. Defines 6 procedures: standard pick entry, identity conflict resolution, stale-data handling, draft-clock pre-computation, wrong-entry correction, and session interruption/resume.

**Type:** Structural (last specification document before implementation)

**Impact on build sequence:**
- Every core decision-logic contract now has a corresponding operational procedure
- RB03 flags that draft-clock pre-computation performance can't be fully validated until U03 (pick timer) is confirmed -- Builder should load-test regardless of the unknown value
- Section 9 acceptance criteria feed directly into the next artifact (MVP Acceptance Gates)

**Highest-leverage next artifact:** MVP Acceptance Gates -- the formal, consolidated pass/fail test suite pulling together acceptance criteria from every contract produced so far (League Rules, Draft Round Order Map, Projection Artifact, Scoring Engine, PRV Calculator, Draft Recommendation Engine, and this Runbook). This is the last specification artifact before Builder/Operator begins actual implementation.

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
