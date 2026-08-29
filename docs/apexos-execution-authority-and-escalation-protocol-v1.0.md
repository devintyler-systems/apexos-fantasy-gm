# ApexOS Execution Authority and Escalation Protocol

**Artifact:** Execution Authority and Escalation Protocol
**Version:** 1.0
**Owner:** Architect
**Status:** Proposed — ready for repository promotion
**Dependencies:** ApexOS Agent Operating System; GitHub repository; Codex local checkout
**Change type:** Structural governance clarification

## 1. Decision statement

ApexOS uses a **three-authority execution model**:

1. **Architect** owns product/system decisions, contracts, acceptance criteria, scope control, and release-gate design.
2. **Codex** owns byte-level repository implementation: local checkout, source edits, command execution, tests, commits, pushes, and pull-request creation.
3. **Evidence & Release Reviewer** owns independent verification of PR diff, CI, retained evidence artifacts, provenance, and release verdict.

GitHub is the canonical durable record for approved contracts, code, tests, issues, PRs, commits, CI, release evidence, and the Decision Ledger. A GitHub API connector is **not assumed to be a local development environment** and is never the sole required path for source-file editing or test execution.

This protocol eliminates implementation stalls caused by connector limitations, role ambiguity, or repeated requests for the operator to broker file contents between agents.

## 2. Scope and non-goals

### In scope

- Decision rights and tool-routing rules for Architect, Codex, Reviewer, GitHub, and operator.
- Mandatory escalation and handoff format when code, tests, CI, or repository writes are required.
- Evidence requirements for implementation completion and release review.
- Rules preventing unsafe source reconstruction from truncated connector responses.
- A single execution owner for every implementation task.

### Explicit non-goals

- Replacing versioned ApexOS contracts, backlog tickets, or test requirements.
- Granting automated authority to merge production changes, make external platform writes, or change league rules.
- Treating Codex as a product or architecture authority.
- Requiring Perplexity agents to possess a local shell, Computer tool, or full-file GitHub retrieval capability.

## 3. Authority matrix

| Actor | Owns | Must do | Must not do | Completion output |
|---|---|---|---|---|
| Architect | Decision statement; contract binding; scope; assumptions; acceptance criteria; dependency order; release gates | Produce one executable, bounded Codex handoff when implementation is needed; identify allowed paths, commands, evidence, and done definition | Edit/reconstruct source from partial connector excerpts; ask operator to relay source bodies; claim tests passed without evidence | Versioned decision/handoff and reviewer focus |
| Codex | Local checkout; source and test edits; workflow edits; local verification; commit; push; PR creation | Read current source locally; preserve existing code; execute commands; make exact bounded patch; return PR and evidence | Change contract/scope/league semantics without Architect escalation; claim pass without terminal output; modify paths outside scope | Commit SHA, changed paths, commands/results, PR URL, deviations |
| Evidence & Release Reviewer | Independent audit of diff, CI, artifact evidence, provenance, and acceptance criteria | Verify commit/PR identities; inspect changed paths; reconcile logs/counts/artifacts; issue PASS/CONDITIONAL PASS/BLOCK | Implement production code; accept green CI as proof of unseen details; require tools not available to implementation owner | Verdict, findings, required closure |
| GitHub | Canonical durable system of record | Store approved artifacts, PRs, commits, CI, reviews, decision ledger, retained evidence | Serve as a presumed shell/editor when connector capabilities do not expose bytes or execution | Immutable URLs, SHAs, check runs, artifacts |
| Operator | Approves irreversible actions and resolves genuine product/business unknowns | Approve bound writes; provide inaccessible credentials or policy decisions only when necessary | Broker routine file contents or mediate normal agent-to-agent role handoffs | Approval or decision |

## 4. Mandatory routing rules

### Rule EAP-01 — Code change means Codex

If requested work requires any of the following, Architect must issue a Codex handoff rather than attempt implementation through a connector-only session:

- Editing source, tests, CI workflows, configuration, migrations, or contracts.
- Running local tests, linters, type checks, builds, or git commands.
- Reviewing full local file context when a connector does not return the raw body.
- Creating a commit or opening a PR whose correctness depends on local verification.

**Safe behavior:** Architect may inspect GitHub metadata and immutable identities, but must stop before a speculative overwrite.

### Rule EAP-02 — GitHub connector is canonical review transport

Use GitHub connector/API access for:

- Reading issues, PR metadata, commits, check runs, review comments, file blob identities, and durable repository documents.
- Creating/maintaining GitHub administrative artifacts only when exact contents and targets are known.
- Independent post-implementation review.

Do not use a metadata-only file response as permission to reconstruct or replace a source file.

### Rule EAP-03 — No operator file-brokerage

When a local checkout is required, the implementation request goes directly to Codex. Agents must not ask the operator to paste source files, attach files repeatedly, or manually move routine code between systems merely to compensate for a connector limitation.

The only valid operator escalation is a genuine missing business decision, credential/policy approval, unavailable local access, or required external-write confirmation.

### Rule EAP-04 — One implementation owner

Every implementation ticket must name exactly one implementation owner: `Codex` unless Architect explicitly records a different local execution mechanism.

A task may have many reviewers, but only one actor owns producing the patch and PR.

### Rule EAP-05 — Do not split a single closure without a reason

If a release gate requires related test and CI evidence changes, deliver them in one bounded PR unless Architect records a dependency or risk reason for separation. Do not create a workflow-only PR simply because a test file was unavailable through an API connector.

### Rule EAP-06 — No unverified completion claims

No agent may state that tests passed, a PR was opened, a commit exists, or CI retained evidence unless the claim is supported by terminal output, GitHub evidence, or an immutable artifact.

### Rule EAP-07 — Mandatory Canonical-Baseline Gate

Before Codex begins repository-dependent work, it must establish and report a
canonical baseline in the task-approved local inspection worktree:

1. Fetch `origin main --prune`.
2. Confirm the inspection-worktree path is the task-approved path and the
   worktree is clean.
3. Confirm `origin` resolves to the approved canonical repository.
4. Confirm `HEAD` equals `origin/main`.
5. Confirm `git rev-list --left-right --count HEAD...origin/main` returns `0 0`.
6. Record the verified canonical SHA and commit subject in the handoff evidence.

Only after this gate passes may Codex create an explicitly authorized
task-specific worktree and branch from that verified SHA.

Before every later repository write in the task-specific worktree, Codex must
fetch `origin main --prune`, report the task worktree path, branch, `HEAD`,
fresh `origin/main`, ahead/behind count, modified tracked paths, staged paths,
and untracked paths, and confirm that:

1. `origin/main` still equals the task-approved canonical base SHA; or
2. the Architect has explicitly approved the reported newer `origin/main` SHA
   as the new task baseline.

Codex must stop with `BLOCKED` before staging, editing, running tests,
committing, pushing, opening a pull request, or accessing external data sources
when an inspection baseline is stale, diverged, dirty, non-canonical, or
path-mismatched; when a task worktree is dirty outside authorized paths; when
the active branch/worktree is not the approved task context; or when canonical
`origin/main` has drifted without explicit Architect approval.

This gate governs local repository state only. It does not authorize production
behavior, provider access, player-data access, configuration changes, external
writes, or GitHub actions.

## 5. Required Architect-to-Codex handoff

Before Codex begins, Architect produces one complete handoff with all fields below. Missing fields are an Architect defect, not an invitation for Codex to guess.

```yaml
handoff_version: "1.0"
ticket_or_artifact: "<Issue/PR/contract identifier>"
owner: "Codex"
base_branch: "main"
working_branch: "<branch>"
commit_message: "<exact message>"
pr:
  title: "<exact title>"
  base: "main"
  draft: false
scope:
  allowed_paths:
    - "<path>"
  prohibited_paths:
    - "<path/category>"
  production_behavior_change: false
binding_inputs:
  contracts:
    - "<path and version>"
  dependent_interfaces:
    - "<path>"
required_changes:
  - "<testable behavior/change>"
verification:
  commands:
    - "<exact command>"
  required_evidence:
    - "<terminal output/artifact/check>"
acceptance_criteria:
  - "<independently testable criterion>"
stop_conditions:
  - "<when Codex must return a blocker rather than guess>"
reviewer_focus:
  - "<highest-risk review item>"
```

### Codex return contract

Codex must return only evidence-bearing completion data:

```yaml
status: "completed | blocked"
branch: "<branch>"
commit_sha: "<sha or null>"
changed_paths:
  - "<path>"
commands_run:
  - command: "<command>"
    exit_code: 0
    result_summary: "<observed output>"
pr_url: "<url or null>"
deviations:
  - "<none or explicit deviation>"
blocker:
  reason: "<only if blocked>"
  attempted: "<what was tried>"
  exact_decision_needed: "<Architect or operator decision>"
```

## 6. Escalation protocol

### A. Architect identifies implementation work

1. Bind the task to the approved contract and current dependency interfaces.
2. Decide whether the change is structural or calibration.
3. Produce the complete Codex handoff.
4. Do not request code attachments or file-copy operations from the operator.

### B. Codex encounters a real blocker

Codex may block only for one of these reasons:

- Required contract, acceptance criterion, or source authority is genuinely absent or contradictory.
- Required local dependency, credential, or environment capability is unavailable.
- Working tree has out-of-scope user changes that cannot safely be preserved.
- The requested implementation would violate the allowed-path or non-goal boundary.
- Required test evidence contradicts the approved contract.

Codex must report: exact blocker, commands attempted, observed evidence, affected paths, and the single decision needed. It must not respond merely that another agent lacks a connector.

### C. Reviewer receives PR

1. Verify PR base/head, commit SHA, changed paths, and contract version.
2. Inspect exact diff and reject scope creep.
3. Check CI runs and retained artifacts.
4. Reconcile reported test counts with raw artifact output.
5. Trace each acceptance criterion to a test, workflow output, or implementation evidence.
6. Issue verdict without reassigning implementation work to Architect or operator.

## 7. Required release evidence

Every material implementation PR must contain or reference:

- Exact tested commit SHA.
- Relevant source/config/contract blob SHA(s) where provenance matters.
- Runtime/language version.
- Dependency-install command.
- Exact test command(s).
- Unabridged focused-test output when the result is a release gate.
- Collection, pass, fail, and skipped counts if available, with raw output authoritative.
- Explicit changed-path scope.
- Statement of production behavior and migration impact.
- Known limitations and degraded-mode behavior when applicable.

For CI failures, evidence must still upload when safe, and the workflow must preserve the original test exit status.

## 8. Capability-degraded behavior

### GitHub connector cannot return raw file body

- Architect/Reviewer record the file path and immutable blob SHA.
- Codex reads and edits the complete local file.
- No agent reconstructs the file from a bounded excerpt.
- Work continues through Codex; this is not a ticket blocker.

### Perplexity session lacks a local shell

- Architect produces the Codex handoff.
- Codex executes local commands.
- Reviewer audits GitHub evidence after PR creation.
- Do not ask the operator to act as the local shell unless Codex itself is unavailable.

### Codex cannot access repository

- Return an access blocker with exact failed command and authentication state.
- Operator resolves only the missing repository authorization/local checkout issue.
- Architect does not attempt a speculative connector-only implementation substitute.

### CI has no retained terminal output

- Reviewer issues `CONDITIONAL PASS` or `BLOCKED: INSUFFICIENT EVIDENCE` as appropriate.
- Codex creates a test/evidence-only closure PR.
- Do not remediate production code unless evidence identifies a behavior defect.

## 9. Acceptance criteria for this protocol

1. Every implementation task names one execution owner and one reviewer.
2. Every code/test/workflow modification request includes a complete Architect-to-Codex handoff.
3. Connector inability to return source bytes never causes an operator file-copy loop.
4. No source file is overwritten from a bounded or truncated response.
5. Every release claim can be traced to a commit, check run, retained artifact, or terminal output.
6. Architect, Codex, and Reviewer handoffs state the single next owner and action.
7. The Decision Ledger records structural changes to this protocol and any exceptions.

## 10. Immediate application: Issue #23

**Decision:** Codex is the implementation owner for the existing branch `test/issue-23-evidence-closure`. Architect has already defined the allowed two-file scope and acceptance gates. Reviewer will inspect the resulting PR and CI evidence.

**Next action:** Codex executes the approved Issue #23 evidence-closure handoff in a local checkout, commits only the workflow and acceptance-test files, pushes the branch, and opens the PR against `main`.

## Change log

- **v1.0:** Establishes Codex as the mandatory local implementation owner; establishes GitHub as canonical evidence and review surface; prohibits connector-driven source reconstruction and operator file-brokerage.

**Version 1.0 – change made:** Established a durable execution-authority protocol that routes all byte-level repository work to Codex and all post-implementation proof to GitHub-backed review.

**Highest-leverage next artifact:** Promote this protocol to `docs/apexos-execution-authority-and-escalation-protocol-v1.0.md` through the next approved governance/documentation PR.
