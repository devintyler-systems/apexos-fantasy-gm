# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.7 — 2026-08-09
**Change:** Ingested 2026 team-environment projections (Sharp Football Analysis projected PPG, VegasInsider projected win totals) and 2025 team/player statistics (TeamRankings PPG/opponent-PPG/FG-attempts/kicking-PPG/red-zone data, PlayerRankings total TDs). Registered two new approved 2026 sources (2.7, 2.8) and two new approved calibration-only sources (2.9, 2.10) in Data Source Register v1.2.

**Type:** Calibration (data ingestion; no architecture change)

**Impact on next artifact:**
- The Projection Artifact Contract's team-environment layer no longer references a generic placeholder — it can cite dated, approved 2026 sources
- D07 flagged: Sharp Football PPG and VegasInsider win totals may disagree on a given team's quality; the Projection Artifact Contract needs a defined reconciliation rule (e.g., weighted average, or PPG as primary with win total as a game-script modifier) before Builder implements the team-environment feature
- `teamrankings_2025_kicking_ppg.csv` is a near-perfect backtest set since it already reports actual 2025 kicker points at SPAMML's exact 3pt-FG/1pt-PAT scoring rule — highest-value single calibration file received today
- 2025 actuals are explicitly barred from entering the 2026 projection artifact as live inputs; calibration-only status enforced in the register

**Highest-leverage next artifact:** Resolve D07 (team-environment source reconciliation rule) as a short addendum to the Projection Artifact Contract, THEN proceed to the PRV Calculator Contract — all four of its prerequisite contracts (League Rules, Draft Round Order Map, Projection Artifact, Scoring Engine) are otherwise complete.

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
