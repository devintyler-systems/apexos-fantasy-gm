# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.6 — 2026-08-09
**Change:** Produced Scoring Engine Contract v1.0. Pure, deterministic conversion of Projection Artifact scoring-event expectations into SPAMML fantasy points. Zero hardcoded constants — all scoring values read from League Rules Contract v0.2 at runtime. Mandatory `calculation_breakdown` field makes every point total self-explaining without LLM involvement.

**Type:** Calibration (mechanical conversion layer; no new modeling decisions)

**Impact on build sequence:**
- All three prerequisite contracts for the PRV Calculator are now complete: League Rules Contract v0.2, Draft Round Order Map Contract v1.0, Projection Artifact Contract v1.0, Scoring Engine Contract v1.0
- SE04 (version propagation test) means resolving U05 (missed FG/PAT penalty) later will NOT require rebuilding the scoring engine — only a league rules version bump
- Data gap flagged: 2026 team implied totals and Vegas TD consensus have not yet been sourced (nflverse historical data covers 2016-2025 seasons only; 2026 season projections require fresh preseason data)

**Highest-leverage next artifact:** PRV Calculator Contract — the first artifact where actual draft-day decision logic (replacement value, positional scarcity) gets built. All inputs it needs (scoring engine output, draft round order map) now exist as approved contracts.

---

### Version 0.5 — 2026-08-09
**Change:** Produced Projection Artifact Contract v1.0.
**Type:** Structural

---

### Version 0.4 — 2026-08-09
**Change:** Locked Data Source and Connector Register v1.0/v1.1.
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
