# ApexOS Fantasy GM — Decision Ledger

## Version History

### Version 3.6 — 2026-08-23
**Change:** Approved B-07 xTD Lookup Table Contract Resolution Addendum v0.1 as the structural resolution of B-07’s contract blockers. B-07 uses regular-season-only 2023–2025 PBP data, applies count-weighted 0.17 / 0.33 / 0.50 seasonal decay, defines deterministic rush-attempt and pass-target eligibility, requires immutable B-06 v0.2 revision provenance, and establishes low-confidence propagation, immutable artifact behavior, a live/controlled-data generation gate, and a Brier-score feature-promotion gate. B-06 v0.2 remains controlling; B-06 v0.3 is not adopted without independent Evidence & Release Reviewer PASS and a subsequent Decision Ledger entry.

**Type:** Structural

**Impact on build sequence:**
- B-07 implementation is not authorized until this addendum is merged and independently reviewed PASS.
- Real B-07 artifact generation remains blocked on valid non-synthetic B-06 revisions for 2023, 2024, and 2025 that satisfy the live/controlled-data gate.
- B-07 output cannot affect a production projection artifact unless it passes the defined rolling-origin Brier-score promotion gate.
- B-08 remains blocked by B-07 completion.

**Highest-leverage next artifact:** Evidence & Release Reviewer audit of the B-07 contract-promotion PR.

***

### Version 3.9 — 2026-08-23
**Change:** Recorded the merged structural B-06/B-07 logical `no_play`
source-field resolution. PR #39 was independently evidence-reviewed PASS
at head `288c9571eef9154592d2856adf5ae25f045174f4` and squash-merged to
canonical `main` as `a1856e5d47016cd8ea1e45c100f1940542da9702`
(`docs(b-06): resolve logical no_play source field v0.1 (#39)`). The
resolution responds to controlled live-run evidence from official
`nflverse/nflverse-data` release `58152862`, asset `354728689`,
20,534,088 bytes, SHA-256
`bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776`,
which established that the raw physical `no_play` column is absent. The
merged B-06 v0.2 addendum defines `b06-no-play-normalization-v0.1` at the
normalized decision-adapter boundary: raw provider bytes and columns remain
unchanged; the logical field is deterministic and source-traceable; missing
required fields, unexpected domains, and ambiguous opportunity-shaped null
rows resolve fail-closed as `logical_no_play_unknown`. The B-07 addendum
consumes this normalized logical field while preserving all existing B-07
rules: regular-season-only 2023–2025 inputs; count weighting
0.17/0.33/0.50; exact seven buckets and 14-row output; receiver identity
requirement for pass targets; low-confidence behavior; immutable append-only
output; and rolling-origin Brier-score promotion gate. Focused verification
recorded 199 collected, 171 deselected, and 28 passed; all seven GitHub
checks succeeded.

**Solo-Operator Exception:** GitHub identity `devintyler83` is the sole
human operator and PR #39 author, so GitHub self-approval was unavailable.
The merge used Solo-Operator Evidence & Release Review Exception v0.2:
separate evidence-review role, Reviewer PASS with no findings, immutable
reviewed head/base SHA verification, exact four-path diff verification,
seven successful checks, Architect merge authorization, and Codex
post-merge canonical-state verification. This is a disclosed governance
exception; it does not claim an independent human GitHub approval or a
GitHub-recorded PASS comment.

**Type:** Structural (changes the approved B-06 normalized source-field
interface used by B-07; does not alter raw source evidence or B-07
weighting, scoring, lookup outputs, or production projection behavior).

**Impact on build sequence:**
- B-06 v0.2 remains the sole controlling ingestion interface; B-06 v0.3
  remains non-controlling.
- B-06 controlled live-data promotion remains required and must be rerun
  against canonical `main` at
  `a1856e5d47016cd8ea1e45c100f1940542da9702` for 2023, 2024, and 2025.
- A B-06 season may promote only after authentic provider lineage, reported
  and computed digest equality, required raw schema, logical `no_play`
  normalization, regular-season game-count validation, immutable manifest,
  and atomic `current.json` pointer requirements all pass.
- B-07 remains BLOCKED. No B-07 lookup table, xTD artifact, or production
  projection behavior is authorized until all three B-06 controlled
  revisions pass the live/controlled-data gate and the separate B-07
  execution handoff is issued.

**Highest-leverage next artifact:** B-06 Controlled Live-Data Retrieval and
Promotion Rerun Handoff v0.2, bound to canonical `main`
`a1856e5d47016cd8ea1e45c100f1940542da9702`.

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

---

### Version 3.10 — 2026-08-24

**Change:** Recorded the successful, reviewed B-06 controlled live-data rerun for the 2023 regular season after an earlier failed/degraded attempt exposed a controlled-runner import-provenance defect. PR #41 head `aaeaed6ca50ac5ca99c496adfd2eb8684c07bf4d` was squash-merged to canonical `main` as `7fd7d207d1b3cc2ca62c0f9aaa974d4e2b14af52` (`fix(b06): attest adapter and rerun 2023 promotion (#41)`). The merged calibration fixes pin controlled-runner child-process imports to the reviewed worktree adapter and add a pre-retrieval adapter path/SHA attestation. A mismatch now exits before provider retrieval, ingestion calls, provider events, partial-manifest output, or `current.json` promotion.

**2023 controlled promotion evidence:** The fresh retry run root is `C:\ApexOS\b06-rerun-aaeaed6-v021`. Its immutable review package is `C:\ApexOS\b06-rerun-aaeaed6-v021\runs\20260824T192734954Z-season=2023-sha=aaeaed6ca50a-7899d551\review-package.json`, SHA-256 `5da47a686b2caf0737715091c27d936671c398adfd6cc56d9906ff93f878d6e1`. The promoted manifest is located under the content-addressed 2023 revision directory for SHA-256 `bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776`. The official nflverse-data source was release `58152862`, asset `354728689`, 20,534,088 bytes. Reported/revision asset digest equality, pointer/manifest/payload digest identities, and atomic `current.json` update all passed. The 49,665-row artifact contains 272 regular-season games and 13 postseason games; B-06 regular-season validation passed. Runtime adapter attestation passed at reviewed path `C:\Projects\apexos-fantasy-gm\.worktrees\b06-rerun-7ca2b24\engine\ingestion\nflverse_pbp.py`, with adapter SHA-256 `7f21b953fd9252c9c1ea6d84ca07a836fd908cd240598b4500c969233da9a46a`. Parser version was `b06-v0.2-evidence-1+b06-no-play-normalization-v0.1`; logical `no_play` counts were false `43,658`, true `6,007`, unknown `0`.

**Quarantined prior evidence:** The first 2023 attempt at implementation SHA `4761023cbab6d846ec98d514df984b8aaf06e568` remains `failed_or_stale` / degraded. It correctly verified the official 2023 asset digest and 272 regular-season games, but imported `b06-v0.3-evidence-1` from a different editable checkout; logical `no_play` normalization was consequently not applied. Its immutable evidence is preserved but cannot be consumed. Any pointer generated before rejection is non-current and must never be used as current evidence.

**Type:** Calibration (not structural). This changes controlled-runner provenance validation and promotion safety; it does not alter the B-06 v0.2 controlling normalized source-field interface, raw provider bytes, canonical identity, B-07 rules or weighting, draft/live runtime, or projection behavior.

**Verification:** PR #41 completed eight successful GitHub checks: B-01, B-02, B-04, B-05 acceptance checks; B-06 nflverse ingestion evidence; CodeQL; and CodeQL actions/Python analysis. Local evidence recorded 89 production and no-play focused tests passed, the Ledger-referenced normalization subset 28 passed, controlled-run harness 14 passed / 0 failed, synthetic adapter mismatch behavior with zero ingestion calls, zero provider events, and absent data root, plus clean `git diff --check` against `7ca2b244bfa8648d5458cd9c163e763ce8744be8`.

**Impact on build sequence:**
- B-06 v0.2 remains controlling, now with the v0.2.1 adapter-attestation safety calibration enforced by merged code.
- 2023 is the only completed controlled live-data promotion.
- 2024 remains unstarted and is the next authorized season, must execute from a fresh root using canonical `main` at `7fd7d207d1b3cc2ca62c0f9aaa974d4e2b14af52` or later, and must halt for Architect review before 2025 begins.
- 2025 remains unstarted and requires the same independent gate.
- B-07 remains BLOCKED: no lookup table, xTD artifact, or production projection behavior is authorized until 2024 and 2025 independently pass their controlled B-06 promotion gates and a separate B-07 execution handoff is issued.
- The next authorized action is the 2024 fresh-root controlled run, only after this Decision Ledger v3.10 PR is merged.

**Highest-leverage next artifact:** B-06 2024 Controlled Live-Data Retrieval and Promotion Rerun Handoff, bound to canonical `main` `7fd7d207d1b3cc2ca62c0f9aaa974d4e2b14af52`, with fresh-root execution and post-run independent evidence review.

---

### Version 3.11 — 2026-08-24

**Decision:** Accepted and promoted the B-06 2024 raw play-by-play evidence after independent Architect review. The accepted controlled run completed with final run state `FRESH_SUCCESS_PENDING_REVIEW` from canonical checkout SHA `2694c1070b253e2f5f43ec54bf555579f8c735a8`, worktree `C:\tmp\apexos-b06-fresh-2694c107`, branch `main`, and worktree cleanliness `true`. The run ID is `20260824T212737205Z-season=2024-sha=2694c1070b25-35e1ab5f`; its evidence root is `C:\ApexOS\b06-rerun-2694c107-v021`.

**Evidence identities:** The immutable review package SHA-256 is `c52e64eeb70a67fd7aaa4adce481036ef134f9dda589424eb9898687228541a5`. The immutable manifest SHA-256 is `bcf3186b3722d4de733b8dfe1aaac857acdb26e942917b15ac1f262a7e04b30c`. The source asset / Parquet SHA-256 is `3fd2896bc0b911b615142d2f1fabae54a4bbba5ab7b73b28187b118ef8af6a3b`. The `current.json` SHA-256 is `5587e31b8a2c67950f1dbbe7c10c61431925dc836443caa40136166de0e17b37`. The retrieval event SHA-256 is `389ee2793ec2bb2996830f9c634238672ab5cbb9ba09372f365a07f2c900db98`.

**Adapter attestation:** The runtime adapter path was `C:\tmp\apexos-b06-fresh-2694c107\engine\ingestion\nflverse_pbp.py`. Its runtime and reviewed-worktree SHA-256 were both `a922817a0512d6b7edf258bb936f8575c730deb30d1d0aeb4dbd498aff0ef34f`. Path equality was `true`; SHA equality was `true`; `adapter_attestation_pass: true`; and `adapter_module_matches_repository: true`.

**Provider lineage:** Provider/source `nflverse/nflverse-data`, release tag `pbp`, release ID `58152862`, asset ID `512957858`, and asset name `play_by_play_2024.parquet` identified the accepted source. The source URL was `https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2024.parquet`. Retrieval timestamp was `2026-08-24T21:27:40.284375Z`; effective timestamp was `2026-08-13T12:26:27Z`; byte count was `20,597,560`; and the reported and computed SHA-256 digest match was `true`.

**Promotion-gate result:** Required raw schema `pass`; raw row count `49,492`; regular-season game count `272 observed / 272 expected`; postseason game count `13`; logical `no_play` normalization version `b06-no-play-normalization-v0.1`; logical `no_play` counts false `43,110`, true `6,382`, unknown `0`; pointer/manifest/payload digest identities all `true`; atomic `current.json` update `pass`; preexisting `current.json` `false`; preexisting revisions directory `false`; new derived artifacts `none`; promotion result `pass`.

**Verification:** The what-if controlled harness passed. The live controlled harness finished `FRESH_SUCCESS_PENDING_REVIEW`. The focused acceptance command was `python -B -m pytest tests/acceptance/test_nflverse_pbp_ingestion.py tests/acceptance/test_b06_no_play_logical_field.py -p no:cacheprovider -o addopts=` and recorded 89 passed in the live run. `git diff --check` was clean.

**Type:** Documentation/evidence-record update only; it is not a B-06 interface, provider, schema, normalization, or algorithm change. No runtime, B-07 behavior, projection, recommendation, league-rules, or other implementation change is authorized or made by this record.

**Release control:** 2025 remains NOT STARTED and requires a separate, fresh-root B-06 execution handoff only after this ledger update is reviewed and merged.

B-07 remains BLOCKED. No B-07 lookup, xTD artifact, or production projection behavior is authorized.

**Highest-leverage next artifact:** Independent review and merge of this Decision Ledger v3.11 documentation-only record. No 2025 execution may begin before that merge and a separate fresh-root handoff.

---

### Version 3.12 — 2026-08-24

**Decision:** Accepted and promoted the B-06 2025 raw play-by-play evidence after independent Architect review. The accepted controlled run completed with final run state `FRESH_SUCCESS_PENDING_REVIEW`, promotion result `pass`, result `success_new_revision`, freshness `fresh`, and stale banner required `false`. B-07 is `BLOCKED`, pending this ledger PR's review/merge and a separately issued B-07 execution handoff. 2026 is `NOT STARTED`.

**Canonical checkout and worktree:** Canonical checkout SHA and `origin/main` were both `574a716c93991183d091631a98d0f5a497ef7746`. The execution used detached `HEAD`, remote `origin` at `https://github.com/devintyler-systems/apexos-fantasy-gm.git`, and worktree `C:\Projects\apexos-fantasy-gm\.worktrees\b06-2025-live-574a716-20260824-01`. Worktree cleanliness before and after was `true`; repository changed paths were none.

**Fresh roots and runs:** The data root was `C:\ApexOS\b06-2025-574a716-c7f4a91d2e83-data\raw\nflverse\pbp`; the run root was `C:\ApexOS\b06-2025-574a716-c7f4a91d2e83-runs`. Both roots were absent before WhatIf, and the data root remained absent after WhatIf. Preexisting 2025 `current.json` was `false`; preexisting 2025 revisions directory was `false`. The WhatIf run ID was `20260824T235444131Z-season=2025-sha=574a716c9399-e81de0ce`; the live run ID was `20260824T235621519Z-season=2025-sha=574a716c9399-7520ef89`.

**Evidence identities:** The WhatIf review package SHA-256 was `b676335dbc66f434bc9c93b4309fd0203d6a315eb83005b88cbe71d8afe82d40`; the WhatIf console transcript SHA-256 was `a11c7e97e5ad254d53a749740c8c21746a2a0ae1f389ac477c4a34fe30d7e3bc`. The live review package SHA-256 was `41be06cbb5d66963531631b84f3b363a1d73f77a20c88f8c2b1df66e05994a62`; the live console transcript SHA-256 was `f0bb14e995ac1a6b85fca0e1f4fc7b5461a830328c40579cfb49487ff84dffd8`. The retrieval event SHA-256 was `4bd5ea0cac25a61d4e1526c21d9249e0d49a8a884f4ee5d77b244593364f27f0`; the immutable manifest SHA-256 was `e1aac2af15332bd019f2afbc0cd6d823de93922965069c94ced57197db59e7bb`; the raw payload SHA-256 was `c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29`; and the atomic `current.json` pointer SHA-256 was `c3c3bc593ce2a3c1db3404a00e965ec885fc9b9218aa34c406d3d8959d4dfe99`.

**Adapter attestation:** The runtime-loaded and reviewed-worktree adapter paths were both `C:\Projects\apexos-fantasy-gm\.worktrees\b06-2025-live-574a716-20260824-01\engine\ingestion\nflverse_pbp.py`. The runtime and independently computed repository adapter SHA-256 were both `a922817a0512d6b7edf258bb936f8575c730deb30d1d0aeb4dbd498aff0ef34f`. Path equality was `true`; SHA equality was `true`; `adapter_attestation_pass: true`; and `adapter_module_matches_repository: true`. Attestation occurred before the sole ingestion call. Adapter invocation count was `1`.

**Provider lineage and integrity:** Provider `nflverse/nflverse-data` and canonical source ID `nflverse/nflverse-data:release:pbp`, release tag `pbp`, release ID `58152862`, asset `play_by_play_2025.parquet`, and asset ID `512957613` identified the accepted source. The source URL was `https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.parquet`; the discovery URL was `https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp`. Byte count was `20,337,029`; retrieval timestamp was `2026-08-24T23:56:24.482747Z`; effective timestamp was `2026-08-13T12:26:09Z`; and parser version was `b06-v0.2-evidence-1+b06-no-play-normalization-v0.1`. The reported and computed SHA-256 were both `c6ecedd6d678cc37ed316b23ef84ee1ec6abb69c514bb11868a7ebd5a367df29`; digest equality was `true`.

**Schema, games, and normalization:** Required raw schema `pass`; missing required columns none; provider source bytes and columns unchanged `true`; additional provider columns retained and enumerated in the immutable manifest `true`; raw rows `48,771`; regular-season games `272 observed / 272 expected`; postseason games `13`. Logical normalization version was `b06-no-play-normalization-v0.1`; decision-adapter boundary application was confirmed `true`; logical `no_play` counts were false `42,603`, true `6,168`, unknown `0`. Missing, unexpected, and ambiguous-row fail-closed handling passed.

**Pointer and promotion integrity:** Pointer revision equals manifest revision `true`; manifest revision equals payload SHA `true`; pointer revision equals payload SHA `true`; revision-directory name matches payload identity `true`; immutable timestamped manifest `true`; atomic `current.json` update `true`; residual temporary pointer file none.

**Verification:** The focused acceptance command was `python -B -m pytest tests/acceptance/test_nflverse_pbp_ingestion.py tests/acceptance/test_b06_no_play_logical_field.py -p no:cacheprovider -o addopts=`. Its initial restricted-sandbox attempt collected 89 tests, passed 28, and produced 61 setup errors with 0 assertion failures because the sandbox denied pytest's Windows temporary directory. The required unrestricted rerun collected 89 tests: 89 passed, 0 failed, 0 errors, 0 skipped, and 0 deselected. The controlled-run harness command `pwsh -NoProfile -File tests\acceptance\test_b06_controlled_run_harness.ps1` passed 14 and failed 0. The 2025 WhatIf command `pwsh -NoProfile -File .\tools\run_b06_controlled.ps1 -Season 2025 -DataRoot C:\ApexOS\b06-2025-574a716-c7f4a91d2e83-data\raw\nflverse\pbp -RunRoot C:\ApexOS\b06-2025-574a716-c7f4a91d2e83-runs -ExpectedCommitSha 574a716c93991183d091631a98d0f5a497ef7746 -WhatIf` recorded 89 collected / 89 passed, status `WHAT_IF_PASS`, and 0 adapter/provider calls. The 2025 live command `pwsh -NoProfile -File .\tools\run_b06_controlled.ps1 -Season 2025 -DataRoot C:\ApexOS\b06-2025-574a716-c7f4a91d2e83-data\raw\nflverse\pbp -RunRoot C:\ApexOS\b06-2025-574a716-c7f4a91d2e83-runs -ExpectedCommitSha 574a716c93991183d091631a98d0f5a497ef7746 -ExecuteLive` executed exactly once, recorded 89 collected / 89 passed, and finished `FRESH_SUCCESS_PENDING_REVIEW`. `git status --short` produced no output; `git diff --check` was clean with exit 0 and no output.

**Type:** Documentation/evidence-record update only; it is not a B-06 interface, provider, schema, normalization, algorithm, runtime, or B-07 change. No runtime, draft/live behavior, projection, recommendation, league-rules, optimizer, provider-integration, parser, decision-adapter, test, CI, configuration, migration, schema, data-contract, or other implementation change is authorized or made by this record.

**Release control:** B-07 remains BLOCKED pending review and merge of this Decision Ledger v3.12 record and a separately issued B-07 execution handoff. No B-07 lookup, xTD artifact, or production projection behavior is authorized by this record.

2026 remains NOT STARTED. No later-season retrieval is authorized.

**Highest-leverage next artifact:** Independent review and merge of this Decision Ledger v3.12 documentation-only record. B-07 may proceed only under a separately issued execution handoff after this ledger record is reviewed and merged.

---

### Version 3.13 — 2026-08-25

**Change:** Canonicalized B-07 v0.1 contract digest attestation across checkout line endings. The frozen contract and SHA-256 remain unchanged; CRLF checkout bytes normalize to LF before hashing, while BOM and lone-CR input fail closed.

**Type:** Structural

**Impact on build sequence:**
- B-07 contract attestation is reproducible on LF and CRLF checkouts.
- Any true canonical-byte change continues to fail closed.
- No candidate, production, artifact, endpoint, pointer, or recommendation behavior is authorized.

**Highest-leverage next artifact:** Independent review of the B-07 contract-digest canonicalization evidence.

---

(END)
