# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 1.0 — 2026-08-09
**Change:** Produced Draft Recommendation Engine Contract v1.0 — the last decision-logic artifact needed for a complete draft-day tool. Combines PRV Calculator output with roster-fit filtering, availability pressure (via Draft Round Order Map's get_picks_between), and positional run detection into a ranked recommendation with a closed-set reason-code vocabulary. Defines a hard, tested boundary preventing the LLM explanation layer from ever re-ranking or inventing content.

**Type:** Structural (completes the core decision-engine contract chain)

**Impact on build sequence:**
- All 6 core contracts now exist: League Rules v0.2, Draft Round Order Map v1.0, Projection Artifact v1.0+addendum, Scoring Engine v1.0, PRV Calculator v1.0, Draft Recommendation Engine v1.0
- DR_R03 flags an open gap: user_strategy_controls (positional_priority, d_o_strategy, te_premium) remain entirely unconfirmed -- the engine runs correctly without them but cannot yet reflect any of Devin's personal draft-strategy preferences
- Remaining pre-implementation artifacts are process/documentation only: Live-Draft Degraded Mode Runbook, MVP Acceptance Gates test suite
- my_draft_position (U01) remains the single open HIGH-risk item blocking a live test with real numbers, though the contract itself requires no changes once it's assigned

**Highest-leverage next artifact:** Live-Draft Degraded Mode Runbook -- the last artifact before Builder can begin implementation work end-to-end. Documents manual pick entry procedure, stale-data banner behavior, and draft-clock degraded mode using the now-complete contract chain.

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
