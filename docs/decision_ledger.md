# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 2.5 — 2026-08-10
**Change:** B-04 (Draft Round Order Map) CLOSED. Reviewer issued final PASS verdict: the GitHub Actions check run (`.github/workflows/b04-draft-round-order-map.yml`, head SHA b2c5c15, conclusion: success, 21:04:28 UTC) provided machine-executed evidence running the exact reviewer-specified command (`python -m pytest tests/acceptance/test_draft_round_order_map.py -q`), closing the P1 gap from the prior BLOCKED verdict (unverifiable pasted transcript). Reviewer additionally independently recomputed the full 128-pick map and confirmed it matches the committed `data/processed/` JSON/CSV exactly. All four remediation items from v2.4 are now satisfied: branch synced with main, artifacts committed, test evidence repo-native (CI, not sandbox), contract-version alignment explicit (v1.2-correction).

**Type:** Structural (first ticket to complete the full Architect-Builder-Reviewer-CI cycle; establishes the CI-check-as-evidence pattern for all remaining tickets)

**Impact on build sequence:**
- `data/processed/draft_round_order_map_spamml_2026.csv` and `draft_position_pick_map_spamml_2026.json` are now frozen, approved artifacts and the formal dependency input for B-05
- `.github/workflows/b04-draft-round-order-map.yml` becomes the template pattern for B-05 through B-17: scoped paths, `contents: read`, pytest against the ticket's acceptance file
- Builder proceeding to B-05 with these artifacts as approved input
- Devin enabling branch protection on `main` (PR-required, status-checks-required, up-to-date-required, no force-push/delete) -- directly closes the branch-desync failure mode that caused the original BLOCKED verdict

**Highest-leverage next artifact:** None at the architecture layer pending B-05 kickoff. U01 (2026 draft position) remains open and HIGH risk; still TBD per Devin.

---

### Version 2.4 — 2026-08-10
**Change:** Ruled on Reviewer's BLOCKED: INSUFFICIENT EVIDENCE verdict on B-04. Verdict confirmed justified via direct repo inspection: (1) contract-version gap real -- `draft-round-order-map-contract-v1.2-correction.md` exists on `main` but was absent from `builder/b-04-draft-round-order-map`, branch was cut before v1.2 landed and never resynced; (2) required artifacts absent real -- `data/processed/` does not exist at all on the B-04 branch; only `engine/draft/round_order_map.py` and `__init__.py` were committed, no data artifacts or test scaffold; (3) no repo-native test evidence real -- the cited 18-pass result came from a sandbox reconstruction, not the actual branch checkout. Ruled v1.2-correction.md remains the canonical current contract (no new contract needed, not in dispute). Published Reviewer Gate Reconciliation Note v1.0 (docs/runbooks/) codifying a standing pre-PR check -- branch synced with main, all artifacts present in diff, test evidence repo-native only, contract-version alignment explicit in PR description -- applying to B-05 through B-17 and retroactively to B-04. This supersedes the "PR open, pending Reviewer" status noted in v2.3 -- B-04 is BLOCKED, not pending.

**Type:** Calibration (process/discipline correction; no contract, schema, or algorithm changed)

**Impact on build sequence:**
- B-04 remains BLOCKED until Builder: syncs branch with main, commits the two `data/processed/` artifacts using T12-corrected values, commits the test scaffold, runs tests against the actual branch checkout, and resubmits PR with repo-native evidence
- Reviewer's audit scope now formally includes branch-vs-main sync and artifact-presence as a first-pass gate, ahead of deeper correctness review
- Does not weaken the escalate-don't-guess pattern; closes the distinct gap where implementation intent was conflated with release evidence

**Highest-leverage next artifact:** None at the architecture layer until Builder resubmits B-04 with repo-native evidence. U01 (2026 draft position) remains open and HIGH risk pending live draft; Devin has not yet selected positions.

---

### Version 2.3 — 2026-08-10
**Change:** Replaced the truncated `playerrankings_2025_total_TDs.csv` (previously ~10 of ~90 rows) with the full dataset. Added two new calibration files: `playerrankings_2025_games_with_TDs.csv` and `playerrankings_2025_pct_games_with_TDs.csv`. Formally registered TeamRankings' team-stats and player-stats page paths as approved source domains in Data Source Register v1.3, and confirmed they should be added as search-priority Links across all three ApexOS spaces (Architect, Builder/Operator, Reviewer).

**Type:** Calibration (data completeness improvement; no change to any live projection formula)

**Impact on build sequence:**
- B-17 (backtest xTD/kicker model against 2025 data) now has a complete, non-truncated ground-truth dataset to validate against
- New idea surfaced, NOT yet adopted: games-with-TDs / pct-of-games-with-TDs as a weekly-consistency signal, potentially valuable for a no-bench league where a single blank week can't be covered by a bench swap. Flagged as a candidate for the Individual Efficiency layer (Projection Artifact Contract Section 4) -- requires the full promotion process (definition, source, validation, baseline comparison, acceptance test) before any formula adopts it. Correctly NOT hardcoded into anything yet.
- Devin confirmed adding TeamRankings' two page URLs as prioritized Links in all three Spaces (Architect, Builder/Operator, Reviewer) -- reinforces search grounding toward already-approved sources per Data Source Register doctrine

**Highest-leverage next artifact:** None at the architecture layer. This calibration data becomes relevant once B-17 backtesting starts. (Superseded by v2.5: B-04 closed.)

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
