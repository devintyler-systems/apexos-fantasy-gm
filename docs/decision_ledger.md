# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 1.5 — 2026-08-10
**Change:** Produced MVP Acceptance Gates v1.0 — the consolidated pass/fail test suite spanning all 7 prior artifacts (League Rules, Draft Round Order Map, Projection Artifact, Scoring Engine, PRV Calculator, Draft Recommendation Engine, Live-Draft Degraded Mode Runbook). 28 gates across 7 categories (Scoring Correctness, Roster/Eligibility, Projection Integrity, Scarcity/Replacement Value, Operational Readiness, Draft Round Order, New Capabilities). Every gate is BLOCK-severity by default — no informal waivers. Defines the explicit go/no-go procedure and fallback (raw frozen projections, no optimizer) if any gate fails.

**Type:** Structural (last specification document; completes the pre-implementation contract chain)

**Impact on build sequence:**
- This is the terminal specification artifact. Every subsequent step is Builder implementation work, not Architect design work
- Section 5 explicitly separates "blocks gate testing" (nothing) from "affects live draft-day accuracy" (U01, U02) -- Builder can proceed with full implementation and testing without waiting on those two unknowns, but Devin still needs U01/U02 resolved before the actual live draft
- Per project doctrine's required build sequence (item 8 of 9: MVP Acceptance Gates), only the Builder/Operator implementation backlog (item 9) remains as a distinct architectural artifact

**Highest-leverage next artifact:** Builder/Operator Implementation Backlog -- an ordered, dependency-mapped task list translating all 8 completed specification artifacts into actual build tickets (Python modules, SQLite schema, Streamlit UI screens) ready for Builder to execute against.

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
