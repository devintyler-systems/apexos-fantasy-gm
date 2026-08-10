# League Rules Contract Changelog

## spamml-2026-v0.3 — 2026-08-10
**Resolved:**
- U03 (pick timer): SPAMML 2026 is a live, UNTIMED draft — no real pick clock exists
- Added reusable `draft_clock_config` schema (timer_enabled, timer_seconds,
  available_timer_options_seconds: [30, 60, 90, 120]) for future ApexOS leagues
  that DO use a pick clock — built once, applicable to any league, not SPAMML-specific
- Downgraded Live-Draft Degraded Mode Runbook risk item RB03 from MEDIUM to LOW
  for SPAMML 2026 specifically (pre-computation remains implemented regardless,
  since it costs nothing and benefits any future timed league)

**Still unknown:** U01 (2026 draft position), U02 (draft date), U04 (trading
during draft), U05 (missed FG penalty), U06 (waivers), U07 (playoffs),
U08 (keeper status), U09 (prize tie rules)

## spamml-2026-v0.2 — 2026-08-09
Confirmed REC eligibility (WR+TE), D/O slot rules, non-standard snake draft
format, manual-only platform, no flex/hybrid slots, add/drop cost.

## spamml-2026-v0.1 — 2026-08-09
Initial draft from launch session.
