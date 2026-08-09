# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.3 — 2026-08-09
**Change:** Produced Draft Round Order Map Contract v1.0 — formal Architect contract for Builder.
Encodes confirmed non-standard snake algorithm, full output schema, Python module interface,
10 acceptance tests (9 blocking, 1 advisory), and Reviewer checklist.

**Type:** Structural (first implementation-ready contract; unlocks PRV calculator)

**Impact on build sequence:**
- Builder can now implement `engine/draft/round_order_map.py` without further architecture input
- Test scaffold filed at `tests/acceptance/test_draft_round_order_map.py`
- T01 ground truth must pass before Builder proceeds to any other test
- PRV Calculator and Availability Model remain blocked until Reviewer signs off

**Highest-leverage next artifact:** Projection Artifact Contract  
(defines the TD-only scoring model and ingest schema; required before the scoring engine
and optimizer can be built)

---

### Version 0.2 — 2026-08-09
**Change:** Locked League Rules Contract v0.2 with confirmed REC eligibility (WR+TE),
D/O slot rules (team-only, ST TDs score, weekly prizes are separate from scoring),
non-standard snake draft format, and manual-only platform.

**Type:** Structural

---

### Version 0.1 — 2026-08-09
**Change:** Established first-league MVP architecture from supplied league configuration.
**Type:** Structural
