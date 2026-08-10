# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 2.1 — 2026-08-10
**Change:** Resolved a Builder-surfaced version-binding ambiguity in the Draft Round Order Map Contract. The contract's example JSON cited `league_rules_version: spamml-2026-v0.2` (current at contract-authoring time); League Rules Contract has since advanced to v0.3. Established a general rule applying to ALL contracts in this repo: any version-reference field in an example block is illustrative, not pinned, unless a contract explicitly states otherwise (none currently do). Generated artifacts always cite the CURRENT league rules version at generation time, read dynamically from config — never hardcoded as a literal string in implementation code. Added acceptance test T11 enforcing this.

**Type:** Calibration (clarifies an ambiguity; no change to B-04's actual scope, algorithm, or output schema)

**Impact on build sequence:**
- B-04 unblocked: Builder proceeds using `spamml-2026-v0.3`, sourced dynamically
- This same class of question will recur on B-08 (Projection Artifact) and B-10 (Scoring Engine), both of which also reference `league_rules_version` in their example schemas — Section 3's general rule preempts needing a separate clarification for each
- Positive signal: Builder correctly identified a real ambiguity and escalated rather than guessing silently, exactly as instructed in the kickoff prompt ("if you hit a genuine ambiguity the contracts don't resolve, stop and ask Devin directly rather than guessing")

**Highest-leverage next artifact:** None at the architecture layer. Builder proceeds with B-04 implementation.

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
