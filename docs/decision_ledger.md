# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 2.6 — 2026-08-10
**Change:** Repository migrated from personal account (`devintyler83`) to GitHub Team organization `devintyler-systems` ($4/mo flat, 1 license) to unlock enforceable branch protection rulesets on a private repo. Org-level OAuth access-restriction policy initially blocked the GitHub connector post-migration (403 on API access); resolved by removing the org's third-party application access restriction (justified: solo-operator org, no additional members to govern). Confirmed the `main-protection` ruleset (Active) survived the repo transfer intact: target = Default branch (resolves to `main`, robust to future default-branch renames), require pull request before merging (0 required approvals -- solo operator, Reviewer audits happen via PR comments not GitHub approvals), require conversation resolution before merging, require status checks to pass (B-04 CI check selected), require linear history, block force pushes, restrict deletions, squash-only merge method. Ruleset immediately proved itself: a direct-push ledger update attempt was correctly rejected (409, "Changes must be made through a pull request") -- confirming enforcement is live, not cosmetic. This entry itself was committed via branch + PR, not direct push.

**Type:** Structural (closes the branch-desync failure class at the platform level, not just the process level; v2.4's Reviewer Gate Reconciliation Note codified the discipline, this ruleset makes violation technically impossible)

**Impact on build sequence:**
- No direct pushes to `main` are possible going forward, including from Architect -- every change (docs, code, contract corrections) must go through a branch + PR
- Future ticket branches (B-05 onward) cannot merge to `main` with a stale/unsynced branch or a failing status check -- the exact failure mode that caused the original B-04 BLOCKED verdict is now structurally prevented, not just procedurally discouraged
- Docs-only PRs (like this one) will need the required status check resolved or the check scoped to only fire on paths it covers -- worth revisiting if pure-docs PRs get blocked waiting on an irrelevant CI check
- Org umbrella (`devintyler-systems`) is available for future migration of DerbyEdge, PGA VenueDNA, FFS-CAR, and DraftOS if Devin chooses; no action required now

**Highest-leverage next artifact:** None at the architecture layer. Ready for B-05 kickoff under the protected `main`. U01 (2026 draft position) remains open and HIGH risk; still TBD per Devin.

---

### Version 2.5 — 2026-08-10
**Change:** B-04 (Draft Round Order Map) CLOSED. Reviewer issued final PASS verdict: the GitHub Actions check run (`.github/workflows/b04-draft-round-order-map.yml`, head SHA b2c5c15, conclusion: success, 21:04:28 UTC) provided machine-executed evidence running the exact reviewer-specified command (`python -m pytest tests/acceptance/test_draft_round_order_map.py -q`), closing the P1 gap from the prior BLOCKED verdict (unverifiable pasted transcript). Reviewer additionally independently recomputed the full 128-pick map and confirmed it matches the committed `data/processed/` JSON/CSV exactly. All four remediation items from v2.4 are now satisfied.

**Type:** Structural

**Impact on build sequence:**
- `data/processed/draft_round_order_map_spamml_2026.csv` and `draft_position_pick_map_spamml_2026.json` are now frozen, approved artifacts and the formal dependency input for B-05
- `.github/workflows/b04-draft-round-order-map.yml` becomes the template pattern for B-05 through B-17
- Devin enabling branch protection on `main` (superseded by v2.6: org migration and ruleset now confirmed active)

**Highest-leverage next artifact:** Superseded by v2.6.

---

### Version 2.4 — 2026-08-10
**Change:** Ruled on Reviewer's BLOCKED: INSUFFICIENT EVIDENCE verdict on B-04. Verdict confirmed justified via direct repo inspection: contract-version gap, missing artifacts, sandbox-only test evidence all real. Ruled v1.2-correction.md remains canonical. Published Reviewer Gate Reconciliation Note v1.0 codifying a standing pre-PR check, applying to B-05 through B-17 and retroactively to B-04.

**Type:** Calibration

**Impact on build sequence:** B-04 remained BLOCKED until remediated (resolved in v2.5).

**Highest-leverage next artifact:** Superseded by v2.5 and v2.6.

---

### Version 2.3 — 2026-08-10
**Change:** Replaced the truncated `playerrankings_2025_total_TDs.csv` with the full dataset. Added two new calibration files. Registered TeamRankings as approved source domains in Data Source Register v1.3.

**Type:** Calibration

**Impact on build sequence:** B-17 now has a complete ground-truth dataset. New idea surfaced (games-with-TDs consistency signal), NOT yet adopted, requires full promotion process.

**Highest-leverage next artifact:** Superseded by v2.5.

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
