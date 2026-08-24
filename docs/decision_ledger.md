# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 3.5 — 2026-08-23

**Change:** Closed the Issue #23 Runtime Draft-State Consumer v1.2 evidence and regression-protection gate. PR #36 (`test(issue-23): close runtime consumer evidence and snapshot-contract gaps`) merged to `main` at merge commit `f4300623a02185535936ff8378b2224845fea2f5`. The merged change was strictly limited to `.github/workflows/issue23-live-state-consumer.yml` and `tests/acceptance/test_live_state_consumer.py`; no production runtime behavior, contract, schema, League Rules content, or provider integration changed.

The closure added: (1) retained focused-suite CI evidence under artifact name `issue23-live-state-consumer-evidence`; (2) immutable tested-commit, runtime-consumer, League Rules v0.5, and workflow blob provenance; (3) valid-LIVE v1.2 §4.2 snapshot-shape and nested freshness assertions; and (4) parameterized non-DSA-08 structured validation mappings while retaining the DSA-08-specific degraded-mode mapping.

Independent artifact inspection completed against Actions run `32673035038`. The artifact bundle identified CI tested merge commit `c9ee725533d857ff15ca430866f447072c719ddd`, Python `3.12.14`, runtime-consumer blob `40d03dedfcdf97f5a8fda6f4a1d5aa3ae40e3386`, League Rules v0.5 blob `80262aba946697bcd048f318bb2bea24a2f609f9`, and workflow blob `27a2897cbe1a4d6acfefcb1ae228ac49a0ae09cc`. Its raw pytest transcript confirmed `25 collected / 25 passed / 0 failed` for `python -m pytest tests/acceptance/test_live_state_consumer.py -v`. Final PASS was recorded on PR #36.

Also merged PR #35 (`docs: establish execution authority and escalation protocol v1.0`), making `docs/apexos-execution-authority-and-escalation-protocol-v1.0.md` the canonical routing protocol: Architect owns contracts and gates; Codex owns local byte-level implementation, verification, commits, pushes, and PR creation; Reviewer owns independent evidence audit; GitHub is canonical evidence and review transport.

**Type:** Calibration — closes evidence, test-contract, and execution-routing gaps without altering runtime recommendation behavior or approved product scope.

**Impact on build sequence:**
- Issue #23 is PASS and no longer blocks dependent live-draft workflow work.
- All future source/test/workflow/configuration/migration/commit/PR tasks requiring local files or command execution must route through Codex in the clean local checkout.
- The next implementation ticket must be selected from canonical backlog dependencies and opened explicitly; no open GitHub issue currently represents the next approved build target.

**Highest-leverage next artifact:** Architect dependency audit and one complete Codex handoff for the next unblocked MVP backlog ticket.

***

### Version 3.4 — 2026-08-21
**Change:** Added Section 5 (Candidate Connector Assumptions Register) to
`docs/data_source_connector_register.md` (v1.4 → v1.5), recording two post-MVP candidate
connectors identified via third-party external repo review:

1. **AR-C01 — ESPN public endpoints** (documented by `pseudo-r/Public-ESPN-API`): scoped to
   read-only roster, matchup, standings, and public league-state for a future ESPN-hosted league
   only. Status CANDIDATE. Risk HIGH — endpoints are undocumented/unofficial, rate limits and
   permitted-use posture are unknown, private-league support is unverified. The reference repo
   documents observed behavior; it does not constitute ESPN authorization or stability guarantee.
   SPAMML manual entry is unaffected and remains permanent.

2. **AR-C02 — Yahoo Fantasy Sports API** (optionally accessed via `uberfastman/yfpy`): scoped
   to read-only league rules, roster state, and player availability for a future Yahoo-hosted
   league only. Status CANDIDATE. Risk MEDIUM-HIGH — OAuth flow, token storage/rotation, API
   quota, and resource coverage require independent verification. Explicitly does not integrate
   Fantrax or SPAMML; `yfpy` wrapper must not become a core-schema dependency. No SPAMML or
   Fantrax sync capability is implied or enabled.

Both entries impose full promotion gates: purpose, fields, auth, rate limits, terms, freshness,
canonical identity, fallback, degraded mode, and safety verified before any connector contract
is drafted.

**Type:** Calibration — candidate-register expansion only. No approved connector, schema,
source authority, build-ticket dependency, or production implementation changed.

**Impact on build sequence:**
- No MVP ticket unblocked, re-scoped, or authorized to implement either adapter.
- SPAMML manual entry remains the permanent, authoritative draft-state input path.
- Any future ESPN or Yahoo adapter requires a separate versioned connector contract, Architect
  approval, and Reviewer gate before Builder implements anything.
- The five other repos reviewed (nflverse/nflverse-data, nfl_data_py, nflfastR,
  pydfs-lineup-optimizer, draftfast) are already handled: nflverse-data is the approved
  canonical source (v1.4); nfl_data_py is PROHIBITED (v1.4); nflfastR, pydfs-lineup-optimizer,
  and draftfast are reference-only — borrow constraint-modeling patterns for the optimizer
  service when B-05 and the recommendation engine tickets reach implementation.

**Highest-leverage next artifact:** Issue #25 (`round_order_map.py` parsing fix, blocked on
PR #24 merge) per v3.3 build sequence. This ledger entry is non-blocking on that path.

---

### Version 3.3 — 2026-08-21
**Change:** Recorded the full BLOCK -> fix -> re-verification cycle for PR #28...

### Version 3.2 — 2026-08-21
**Change:** Reviewed and merged-gate-hardened PR #28 (Issue #23, engine/draft/live_state_consumer.py, Contract v1.2). Confirmed DSA-first ordering, exact DSA-08 exception, read-only B-05 access, and 900-second B-05-only staleness threshold all match contract. Logged three non-blocking findings: (1) DSA-07 non-live reason codes collapsed to one generic string rather than distinguishing non_live/manual/degraded; (2) DSA_VALIDATOR_VERSION/ROUND_ORDER_MAP_VERSION are hardcoded literals with no source-of-truth binding — accepted as a known limitation, same pattern as U-DSA-IDENTITY-01; (3) live-draft-failure tests cover 2 of 8 DSA fixtures, not all 8 — recommended, not required, before merge. Added scoped CI workflow issue23-live-state-consumer.yml so this consumer is never un-gated again. PR #28 not yet merged; routed to Evidence & Release Reviewer per Issue #23's branch/review gate.

Highest-leverage next artifact: Evidence & Release Reviewer's independent pass on PR #28, then Devin's merge decision.

### Version 3.1 — 2026-08-20
**Change:** Resolved three contract-boundary conflicts (C-01, C-02, C-03) that Builder (via
Codex) surfaced during interface inspection for Issue #23
(`engine/draft/live_state_consumer.py` against Runtime Draft-State Consumer Contract v1.1,
merged PR #22) and correctly halted on before writing code, rather than guessing past them.

1. **C-01 (DSA-08 failure-mode contradiction):** Contract v1.1 §4.3 mapped every
   `ContractValidationError` to `UNKNOWN`/`DSA_VALIDATION_FAILED_<criterion>`, but Issue #23's
   ordered work already assumed DSA-08 specifically degrades to `DEGRADED`/`DSA08_CLOCK_MISMATCH`.
   Both could not be true as written. Resolved by publishing Runtime Draft-State Consumer
   Contract v1.2 (PR #24): a narrow exception where `.criterion == "DSA-08"` maps to
   `DEGRADED`/`DSA08_CLOCK_MISMATCH`; every other criterion's handling is unchanged from v1.1.
2. **C-02 (unparseable provenance rule):** The approved snapshot-provenance rule requires a
   parsed League Rules `contract_version` field, but direct source inspection confirmed
   `engine/draft/round_order_map.py:_league_rules_version()` derives version by regex-matching
   the league-rules YAML **filename** (`re.search(r"v(\d+(?:\.\d+)*)$", path.stem)`), and a
   repo-wide search confirmed zero `contracts/league_rules/*.yaml` files have ever carried a
   `contract_version` field. Resolved by publishing `contracts/league_rules/spamml-2026-v0.5.yaml`
   (PR #24) — additive, immutable, byte-identical to v0.4 except a new top-level
   `contract_version: "0.5"` field and one changelog line. **The corresponding code change to
   `_league_rules_version()` (read the parsed field only; fail to `PROVENANCE_UNAVAILABLE` on a
   missing/invalid field, never infer one) is tracked as Issue #25, blocked on PR #24 merging,
   and is explicitly NOT included in PR #24 itself** — Architect does not write production code.
3. **C-03 (missing scope-lock record):** Issue #23 asserted SPAMML-2026-only binding for the DSA
   validator/consumer as accepted scope, but no ledger entry recorded this decision. Recorded
   below.

**Assumptions Register addition:**
- **ID:** U-DSA-IDENTITY-01
- **Item:** DSA validator/consumer identity scope (`EXPECTED_MANAGER_NAME`,
  `EXPECTED_MANAGER_SEAT` hard-coded module-level constants in
  `engine/contracts/draft_seat_assignment.py`)
- **Decision:** Explicitly scope-locked to SPAMML 2026 only (`"Professor FleX"`, seat 4). A
  general-purpose, multi-league successor validator is deferred to a future ticket and is
  explicitly NOT blocking Issue #23's implementation.
- **Affected module:** `engine/contracts/draft_seat_assignment.py`,
  `engine/draft/live_state_consumer.py`
- **Risk:** Medium — this validator will hard-fail DSA-03 for any second league or season without
  a successor.
- **Owner:** Architect
- **Decision deadline:** Before onboarding any second league.

**Type:** Calibration (a narrow contract exception, one additive league-rules artifact, and one
Assumptions Register/scope-lock record; no scoring, roster, or optimizer weight changed).

**Controlling gate:** Issue #23 (`engine/draft/live_state_consumer.py`) remains PAUSED until
PR #24 merges to `main` **and** Issue #25's `round_order_map.py` parsing-fix PR also merges.
Builder/Codex may resume implementation only after both are independently confirmed merged on
`main` — a Reviewer PASS or green CI on either is not itself "merged" (v2.7 ledger lesson:
merge verification is a separate fact from Reviewer PASS/CI verdict).

**Impact on build sequence:**
- Runtime Draft-State Consumer Contract v1.2 supersedes v1.1 for §4.3 only; all other sections
  unchanged; Issue #23 must implement against v1.2, not v1.1.
- `spamml-2026-v0.5.yaml` is additive; v0.4 remains on record unmodified and is not superseded
  for any field other than the new `contract_version` key's existence.
- `round_order_map.py`'s filename-regex version inference remains ACTIVE and UNCORRECTED until
  Issue #25's PR merges — `league_rules_version` in the runtime-consumer output snapshot remains
  filename-derived until then; do not assume `contract_version` is being read yet.
- **Process note:** the Architect Space's GitHub connector could not return raw file content via
  `get_file_contents` for any file regardless of size (confirmed on files from 1.8KB to 12KB)
  in the 2026-08-20 remediation session. This ledger's own Versions 2.0 through 0.1 (below this
  point) were NOT re-verified that session — content below Version 2.1 reflects the last
  independently confirmed state and was intentionally left untouched rather than risking a
  blind full-file overwrite via the connector.

**Highest-leverage next artifact:** Issue #25 (`round_order_map.py` parsing fix), owned by
Builder, blocked on PR #24. Once PR #24 and Issue #25's PR are both independently confirmed
merged, lift Issue #23's pause and hand it back to Builder/Codex referencing Contract v1.2.

---

### Version 3.0 — 2026-08-19
**Change:** Reconciled four merged pull requests against `main` that were never recorded in this
ledger, closing a gap where confirmed repository state had drifted ahead of the ledger's own
version history (last entry: v2.9, 2026-08-11). Direct repo inspection (PR reads, commit history,
schema inspection) confirmed the following, in merge order:
1. **B-05 Draft State Manager — contract and implementation** (PR #9, merged 2026-08-11T02:16:33Z;
   PR #12, merged 2026-08-11T03:00:10Z). `contracts/draft/draft-state-manager-contract-v0.2-
   correction.md` is APPROVED canonical, resolving U-B05-01 through U-B05-04. Implementation
   (`engine/draft_state/`: `schema.py`, `repository.py`, `manager.py`) is a 3-table isolated
   SQLite store (`draft_pick_entries`, `draft_session_state`, `draft_pick_overrides`). Reviewer
   PASS confirmed on all 13 acceptance criteria (T01-T13). This closes out the B-05 line that
   v2.8 had left blocked pending B-02.
2. **SPAMML 2026 Draft Seat Assignment v1.0** (PR #18, merged 2026-08-18T21:51:29Z). Added
   `contracts/draft/spamml-2026-draft-seat-assignment-v1.0.yaml` — manager identity/seat
   resolution, draft schedule, `selection_state`. Reviewer P2/P3 fix aligned `draft_state.format`
   to canonical league-rules vocabulary (`non_standard_snake`).
3. **Seat Assignment v1.1 / U02 clock resolution / DSA-08** (PR #19, merged 2026-08-18T22:24:31Z).
   Resolved U02 (SPAMML 2026 draft date/time: Mon Aug 31 2026 6pm Pacific / 2026-09-01T01:00:00Z).
   Reviewer P1/P2 fix resolved U-DRAFT-02 (`draft_clock_status: confirmed_untimed`, matching
   League Rules v0.4 `timer_enabled: false`) and normalized timezone provenance (IANA zone kept
   separate from UTC offset/abbreviation). Added DSA-08 as the cross-contract clock-consistency
   acceptance criterion.
4. **DSA Contract Validation Harness, DSA-01 through DSA-08** (PR #20, merged commit
   `26a6913c86d719dfd89ae46aafe895a939d2717e`, base `f6464cf17670ed71e4425ed4926d8033c1ef3485`,
   merged 2026-08-19T06:56:04Z). Added CI/test-only validation infrastructure only:
   `engine/contracts/draft_seat_assignment.py` (`validate_draft_seat_assignment(...)`,
   `classify_draft_activity(...)`), fixture-backed pytest acceptance coverage (29 passed
   locally), safe DSA-07 degraded-mode classification when transition/feed evidence is absent,
   DSA-08 cross-contract clock-consistency enforcement, and a dedicated path-scoped GitHub
   Actions workflow. Confirmed: no canonical contract mutation, no runtime consumer wiring, no
   B-06/data/integration/recommendation/UI/storage/external-platform changes.

**Cross-check performed before closing this reconciliation:** verified B-05's actual schema
(`draft_pick_entries`, `draft_session_state`) contains no `manager_id`, `seat`, or team-identity
column of any kind — confirmed via direct schema inspection, not inference. B-05 is a pick-
sequence/session-resume ledger only; it was scoped and built (2026-08-11) before seat assignment
or the DSA validator existed (2026-08-18/19) and does not model who owns a given `pick_number`.
This means B-05 and the seat-assignment/DSA-01-08 line do not overlap or conflict at the schema
level — no B-05 revision is required to consume DSA-07 activity classification.

**Type:** Structural (records four previously-unlogged canonical merges; establishes ledger
currency with actual `main` state before further design work; no weights, thresholds, or
calibration values changed)

**Impact on build sequence:**
- Ledger now reflects true `main` state as of commit `26a6913c86d719dfd89ae46aafe895a939d2717e`
- B-05 is CLOSED and canonical; no further B-05 work is queued
- Confirmed open gap: `engine/contracts/draft_seat_assignment.py`'s validator and DSA-07
  classifier remain unwired into any runtime consumer — this is the next build target
- Confirmed non-conflict: the runtime draft-state consumer (next artifact) is a new read-only
  join/derivation layer over B-05 + seat assignment v1.1 + the round-order-map contract set +
  League Rules v0.4 — it does not read from or write to B-05's tables directly as a peer
  schema, and it does not require modifying B-05

**Highest-leverage next artifact:** Runtime Draft-State Consumer Contract v1.0 — the read-only
join adapter that wires the validated seat-assignment artifact and DSA-07 activity
classification into a live-usable draft-state snapshot for the draft-day UI and recommendation
adapter, without deriving pick order locally and without silently trusting degraded evidence.
U01 (2026 draft position) remains open and HIGH risk; still TBD per Devin.

---

### Version 2.9 — 2026-08-11
**Change:** Resolved the B-06 v0.2 proposal's structural blocker: the repository's Data Source
Register, B-01/B-06 backlog lines, and Projection Artifact Contract v1.0 all named `nfl_data_py`
as the approved nflverse access method, while the B-06 v0.2 proposal correctly identified this
package as archived/read-only and prohibited it in favor of direct nflverse-data GitHub release-
asset access. Before approving, independently verified the proposal's technical premises against
the live `nflverse/nflverse-data` `pbp` release (release ID 58152862) rather than trusting its
citations: confirmed `play_by_play_{season}.parquet` assets exist and are `state: "uploaded"` for
2016 through 2025 inclusive; confirmed no `play_by_play_2026.*` asset exists; confirmed the 2025
asset (asset ID 354718810, 20,343,981 bytes) carries digest
`sha256:3730c4db2ab99d2dfc4017de975b7610c46c35301b9280b65c03de1b1c74265a`, an exact match to the
proposal's manifest example; confirmed pre-2019 season assets (e.g., 2016, asset ID 250647177)
report no provider digest, validating the nullable-digest design requirement. A repository-wide
`nfl_data_py` audit via code search also surfaced a fifth reference not listed in the original
proposal's "Contracts affected" section: `docs/architect-continuation-prompt.md`. Approved the
five B-06 resolutions (U-B06-01 through U-B06-05) as design and authorized the following
document amendments: `docs/data_source_connector_register.md` (v1.3 -> v1.4, `nfl_data_py`
PROHIBITED, direct release-asset access APPROVED under 2.1), `docs/builder-operator-
implementation-backlog-v1.0.md` (B-01, B-06 lines updated), `docs/architect-continuation-
prompt.md` (nfl_data_py reference corrected), and a new `projection-artifact-contract-v1.2-
addendum.md` (source_citations format migrated off `nfl_data_py`; also corrected a pre-existing
internal inconsistency where v1.0 Section 10 cited a 2023-2025 window against Section 5's
2016-2025 window). Published the new `contracts/ingestion/nflverse-play-by-play-ingestion-
contract-v0.2.md` as the approved (not merely proposed) B-06 source-access contract.

**Type:** Structural (changes the approved data-access method and canonical source-of-truth
documents; not a weight, threshold, or calibration adjustment)

**Impact on build sequence:**
- B-06 remains without an open branch -- this version approves the *design and documentation*
  only; implementation (adapter code, tests, ingestion run) is a separate, still-gated Builder
  ticket against the new ingestion contract
- B-01's dependency line now specifies `httpx`+`pyarrow` instead of `nfl_data_py`; any future
  `pip install -e .` must resolve without `nfl_data_py` present
- Projection Artifact Contract v1.0's body is left byte-identical; the v1.2 addendum pattern
  (matching the existing v1.1 addendum) preserves the original document rather than editing a
  contract in place
- `docs/decision-ledger.md` (hyphenated, template-only file) is unaffected -- `docs/
  decision_ledger.md` (underscore) remains the single source of truth per the architect-
  continuation-prompt's own instruction

**Highest-leverage next artifact:** Builder opens a `builder/b-06-nflverse-ingestion` branch
against the approved v0.2 ingestion contract. U01 (2026 draft position) remains open and HIGH
risk; still TBD per Devin.

---

### Version 2.8 — 2026-08-10
**Change:** Corrected a premature readiness claim in v2.7 ("Ready for B-05 kickoff under fully-verified main"). On attempting B-05 kickoff, direct repo inspection (`engine/` directory listing, Decision Ledger search for "B-02") showed B-02 (canonical data model: `dim_player`, `dim_team`, `dim_game`, `player_alias_map`) had never been implemented -- only B-04 artifacts existed on `main`. B-05's own dependency line (Backlog Section 3: "Depends On: B-02, League Rules Contract") was not satisfied, so B-05 branch creation was withheld. Separately resolved a scope discrepancy surfaced while pulling B-02's contract dependencies: the TouchdownOS reference blueprint lists two additional canonical tables (`player_team_history`, `coaching_history`) not present in the approved Backlog's B-02 line. Per doctrine Rule 6 (reference documents are hypothesis inputs, not approved contracts), ruled these two tables out of scope for B-02 -- no defined draft-day access pattern, acceptance test, or baseline comparison exists for either. Opened branch `builder/b-02-canonical-data-model` from `main` and tracking Issue #5 with the confirmed 4-table scope, done-when criteria, and Reviewer checks.

**Type:** Calibration

**Impact on build sequence:**
- B-05 remains blocked; do not open a B-05 branch until B-02 is merged to `main` and its acceptance test (insert succeeds for all 5 SPAMML position types) passes
- B-02 branch (`builder/b-02-canonical-data-model`) and Issue #5 are open and ready for Builder
- `player_team_history` and `coaching_history` logged as a deferred capability gap for the post-MVP season-features phase, not a blocker

**Highest-leverage next artifact:** Superseded by v2.9+.

---

### Version 2.7 — 2026-08-10
**Change:** Closed a self-caught process gap: B-04 had been logged CLOSED in v2.5 based on Reviewer PASS verdict and a green CI check run, but the actual implementation PR (#2) was never merged to `main`.

**Type:** Calibration

---

### Version 2.6 — 2026-08-10
**Change:** Repository migrated from personal account (`devintyler83`) to GitHub Team organization `devintyler-systems`.
**Type:** Structural

---

### Version 2.5 — 2026-08-10
**Change:** B-04 Reviewer issued final PASS verdict.
**Type:** Structural

---

### Version 2.4 — 2026-08-10
**Change:** Ruled on Reviewer's BLOCKED: INSUFFICIENT EVIDENCE verdict on B-04.
**Type:** Calibration

---

### Version 2.3 — 2026-08-10
**Change:** Replaced truncated TD dataset; registered TeamRankings as approved source in Data Source Register v1.3.
**Type:** Calibration

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
(END)
