# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 1.2 — 2026-08-10
**Change:** Produced Draft Recommendation Engine Contract v1.2 addendum. Resolved the KCK/D_O guardrail sub-question as a soft, informational flag (unconventional_early_kicker before round 4, unconventional_early_do before round 7) that never alters ranking math. Added a new "Snooze-for-1-round" capability: a user-initiated, pick-scoped candidate filter that excludes a player from the CURRENT pick's recommendation only, with zero effect on that player's or any other player's PRV/scarcity math. 5 new acceptance tests (DR09-DR13), all blocking, with DR13 specifically testing for zero cross-player side effects from a snooze action.

**Type:** Structural (adds a new user-facing capability, not just a parameter resolution)

**Impact on build sequence:**
- Draft Recommendation Engine Contract now has zero remaining blocking unknowns
- Snooze is flagged as the primary integration risk for Builder -- it must be implemented as a pure display/candidacy filter, never a data mutation, verified by DR10 and DR13's isolation tests
- Streamlit Draft UI build item now has a concrete interaction requirement (Section 3d): a "Snooze 1 round" button on every recommended candidate

**Highest-leverage next artifact:** Live-Draft Degraded Mode Runbook -- last artifact before Builder can begin end-to-end implementation. All 6 core decision contracts (League Rules, Draft Round Order Map, Projection Artifact, Scoring Engine, PRV Calculator, Draft Recommendation Engine) are now fully resolved with no blocking unknowns.

---

### Version 1.1 — 2026-08-10
**Change:** Resolved DR_R03 via Draft Recommendation Engine Contract v1.1 addendum.
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
