# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.9 — 2026-08-09
**Change:** Produced PRV Calculator Contract v1.0. Defines SPAMML-specific replacement levels (16/32/48/16/16 across QB/RB/REC/KCK/D_O), the REC combined WR+TE merged-pool rule, static vs. dynamic replacement value, and scarcity_ratio as the explicit 16-team scarcity signal. 7 acceptance tests, all blocking, including a full 128-pick simulated draft reproducibility test.

**Type:** Structural (first artifact where real draft-day decision math is defined)

**Impact on build sequence:**
- All 5 prerequisite contracts for the Draft Recommendation Engine are now complete: League Rules v0.2, Draft Round Order Map v1.0, Projection Artifact v1.0+addendum, Scoring Engine v1.0, PRV Calculator v1.0
- Kicker and D_O scarcity are explicitly modeled as real signals (Section 6), correcting the common generic-tool mistake of treating them as afterthoughts
- PRV_R02 flags that dynamic recalculation must fire on every pick, not per-round -- a performance shortcut here would silently reintroduce staleness

**Highest-leverage next artifact:** Draft Recommendation Engine Contract -- the final contract before a working draft-day tool exists end-to-end. Combines PRV output with roster-fit filtering and the availability-pressure model (using the Draft Round Order Map's get_picks_between function) to produce the actual recommendation payload.

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
