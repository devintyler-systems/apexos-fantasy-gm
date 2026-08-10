# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 1.1 — 2026-08-10
**Change:** Resolved DR_R03 via Draft Recommendation Engine Contract v1.1 addendum. Devin's stated strategy (BPA, or scarcity value when it justifies deviation) maps directly onto the existing dynamic_prv_score definition -- no new weighting logic required. Confirmed as design decision: te_premium=none, positional_priority=none, d_o_strategy=value_based_no_floor, override_philosophy=trust_the_model (post-calibration). One open sub-question remains (KCK/D_O early-round guardrail flavor) but does not block Builder -- defaults to no-guardrail behavior.

**Type:** Calibration (confirms existing engine behavior is correct; no structural change)

**Impact on build sequence:**
- Draft Recommendation Engine Contract v1.0 now has zero unconfirmed strategy inputs
- DR_R03a flags a real dependency: "trust the model" is only as good as the calibration/backtest work still pending across the Projection Artifact and PRV Calculator contracts -- this should be revisited if backtest work isn't complete before the late-August draft date
- All 6 core decision contracts (League Rules, Draft Round Order Map, Projection Artifact, Scoring Engine, PRV Calculator, Draft Recommendation Engine) are now fully resolved with no blocking unknowns

**Highest-leverage next artifact:** Live-Draft Degraded Mode Runbook -- last artifact before Builder can begin end-to-end implementation.

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
