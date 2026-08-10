# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 2.3 — 2026-08-10
**Change:** Replaced the truncated `playerrankings_2025_total_TDs.csv` (previously ~10 of ~90 rows) with the full dataset. Added two new calibration files: `playerrankings_2025_games_with_TDs.csv` and `playerrankings_2025_pct_games_with_TDs.csv`. Formally registered TeamRankings' team-stats and player-stats page paths as approved source domains in Data Source Register v1.3, and confirmed they should be added as search-priority Links across all three ApexOS spaces (Architect, Builder/Operator, Reviewer).

**Type:** Calibration (data completeness improvement; no change to any live projection formula)

**Impact on build sequence:**
- B-17 (backtest xTD/kicker model against 2025 data) now has a complete, non-truncated ground-truth dataset to validate against
- New idea surfaced, NOT yet adopted: games-with-TDs / pct-of-games-with-TDs as a weekly-consistency signal, potentially valuable for a no-bench league where a single blank week can't be covered by a bench swap. Flagged as a candidate for the Individual Efficiency layer (Projection Artifact Contract Section 4) -- requires the full promotion process (definition, source, validation, baseline comparison, acceptance test) before any formula adopts it. Correctly NOT hardcoded into anything yet.
- Devin confirmed adding TeamRankings' two page URLs as prioritized Links in all three Spaces (Architect, Builder/Operator, Reviewer) -- reinforces search grounding toward already-approved sources per Data Source Register doctrine

**Highest-leverage next artifact:** None at the architecture layer. Builder proceeds with B-04 close-out (PR open, pending Reviewer). This calibration data becomes relevant once B-17 backtesting starts.

---

### Version 2.2 — 2026-08-10
**Change:** Corrected fabricated T09 edge-position values.
**Type:** Calibration

---

### Version 2.1 — 2026-08-10
**Change:** Resolved a Builder-surfaced version-binding ambiguity.
**Type:** Calibration

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
**Change:** Resolved D07.
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
**Change:** Locked Data Source and Connector Register.
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
