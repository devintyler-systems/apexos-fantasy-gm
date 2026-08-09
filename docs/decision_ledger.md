# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 0.2 — 2026-08-09
**Change:** Locked League Rules Contract v0.2 with confirmed REC eligibility (WR+TE),
D/O slot rules (team-only, ST TDs score, weekly prizes are separate from scoring),
non-standard snake draft format, and manual-only platform.

**Type:** Structural (confirmed eligibility rules change optimizer and scarcity model)

**Impact on optimizer:**
- REC replacement pool = WR + TE combined; replacement level at REC3 ≈ pick 48 across WR+TE
- D/O prize EV must be modeled as a second value stream separate from projected_fantasy_pts
- All draft state: manual entry only; no sync fallback needed
- Draft pick sequence must use confirmed non-standard snake, not generic snake assumption

**Highest-leverage next artifact:** Draft Round Order Map
(encode the confirmed non-standard pick sequence so optimizer knows Professor FleX's
exact pick numbers for all 8 rounds regardless of assigned draft position)

---

### Version 0.1 — 2026-08-09
**Change:** Established first-league MVP architecture from supplied league configuration.
**Type:** Structural
