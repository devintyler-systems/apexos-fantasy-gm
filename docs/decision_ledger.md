# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.8 — 2026-08-09
**Change:** Resolved D07 via Projection Artifact Contract v1.1 addendum. Established precedence rule: Sharp Football projected PPG is the primary team-environment driver; VegasInsider win total is a secondary divergence flag only, never blended into the raw TD-count baseline. Analysis of actual 2026 snapshot data confirmed r=0.91 correlation between sources with two real outliers (Cowboys, Commanders) flagged `pass_funnel_risk`.

**Type:** Calibration (resolves an open unknown; no structural change)

**Impact on build sequence:**
- All blocking gaps in the Projection Artifact Contract are now closed
- Four prerequisite contracts for the PRV Calculator are complete: League Rules v0.2, Draft Round Order Map v1.0, Projection Artifact v1.0+addendum, Scoring Engine v1.0
- game_script_flag is qualitative-only at this version (P06) — acceptable for MVP since it informs Devin's manual_environment_override judgment, not an automated formula

**Highest-leverage next artifact:** PRV Calculator Contract — fully unblocked. First artifact where real draft-day replacement-value math and 16-team positional scarcity logic get built.

---

### Version 0.7 — 2026-08-09
**Change:** Ingested 2026 team-environment projections and 2025 calibration statistics; registered Sharp Football Analysis and VegasInsider as approved sources.
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
