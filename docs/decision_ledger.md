# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.5 — 2026-08-09
**Change:** Produced Projection Artifact Contract v1.0. Adapted TouchdownOS blueprint's scoring-neutral kicker and D/ST contracts to SPAMML's exact confirmed scoring rules (no points-allowed, no standalone sack/INT/fumble scoring). Defined xTD derivation method sourced from nflverse play-by-play (replacing framework doc's fixed 0.55/0.38 constants). Added Data Source Register v1.1 noting nflreadr/nflfastR as intentionally not added (redundant with nfl_data_py).

**Type:** Structural (unlocks Scoring Engine and PRV Calculator)

**Impact on build sequence:**
- Framework doc's 45/25/20/10 modeling weights adopted as starting hypothesis only, not production truth — flagged for backtest validation (P01)
- D_O weekly prize EV isolated from fantasy scoring per PA08 — two separate value streams preserved
- Kicker treated as first-class position with zero penalty assumption pending U05 resolution
- 9 acceptance tests defined (8 blocking, 1 advisory)

**Highest-leverage next artifact:** Scoring Engine Contract — converts this projection artifact's raw scoring-event expectations into SPAMML fantasy points using the confirmed scoring map from League Rules Contract v0.2. This is the shortest remaining artifact before the PRV Calculator can be built.

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
