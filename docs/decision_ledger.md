# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.4 — 2026-08-09
**Change:** Locked Data Source and Connector Register v1.0. Approved nflverse/nfl_data_py (historical play-by-play, free, no auth, MIT-licensed) and manual Vegas implied-totals ingest for MVP. Deferred PFF (cost + unresolved ToS/scraping risk). Confirmed SPAMML custom platform has no API — manual entry is permanent mode, not a gap to close. Flagged Fantrax as the most promising Phase 2 read-only sync candidate pending its own register entry.

**Type:** Structural (unlocks Projection Artifact Contract source fields)

**Impact on next artifact:**
- Projection Artifact Contract may now cite `nflverse:nfl_data_py` and `vegas_manual` as real, approved sources instead of placeholders
- xTD constants (e.g., "0.55 xTD for a 1-yard carry" from the framework doc) must be recomputed from nflverse play-by-play, not imported as fixed values
- No live platform sync work is authorized — SPAMML has no API; this is permanent, not temporary

**Highest-leverage next artifact:** Projection Artifact Contract — now unblocked. Defines the TD-only scoring ingest schema, xTD derivation method (using nflverse as source), kicker and D/O model contracts (adapted from TouchdownOS blueprint), and the frozen artifact format consumed by the scoring engine and optimizer.

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
