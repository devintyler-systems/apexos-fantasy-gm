# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 1.4 — 2026-08-10
**Change:** Resolved U03 (pick timer) via League Rules Contract v0.3. SPAMML 2026 is confirmed as an untimed live draft. Added a reusable `draft_clock_config` schema (none/30s/60s/90s/120s) to the League Rules Contract structure so future ApexOS leagues with real pick clocks can configure timing without a contract redesign. Live-Draft Degraded Mode Runbook's RB03 risk item downgraded from MEDIUM to LOW for this specific league, though pre-computation behavior remains implemented as built (zero cost, future-proofs the platform).

**Type:** Calibration (resolves an open unknown; adds reusable config schema for future leagues, no change to SPAMML 2026 build requirements)

**Impact on build sequence:**
- League Rules Contract now has 7 remaining unknowns (down from 8): U01, U02, U04, U05, U06, U07, U08, U09 remain; U03 is closed
- Draft Recommendation Engine and Live-Draft Runbook require no changes — pre-computation behavior was already spec'd as always-on regardless of timer status
- This is the first artifact explicitly designed for multi-league reuse (draft_clock_config), signaling the platform is starting to generalize beyond SPAMML-only assumptions where doing so costs nothing extra

**Highest-leverage next artifact:** MVP Acceptance Gates — the consolidated pass/fail test suite pulling together acceptance criteria from all 7 prior artifacts. Last specification document before Builder/Operator begins implementation.

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
