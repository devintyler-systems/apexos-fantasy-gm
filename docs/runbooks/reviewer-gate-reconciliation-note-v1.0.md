# Reviewer Gate Reconciliation Note v1.0

## Purpose

Codify a standing pre-PR check after the B-04 BLOCKED: INSUFFICIENT EVIDENCE
finding (2026-08-10). The block was justified: Builder's branch
`builder/b-04-draft-round-order-map` was cut before contract v1.2 landed on
`main` and was never resynced, so the PR was missing the v1.2-correction
contract, the required `data/processed/` artifacts, and repo-native test
evidence. The 18-pass test result cited in the PR came from an isolated
sandbox reconstruction, not the actual branch checkout -- useful as
implementation feedback, not valid as release evidence.

## Standing rule

No PR may be submitted for Reviewer audit until all of the following are true
on the PR's source branch, verified by Builder before opening or re-opening
the PR:

1. **Branch is synced with `main`.** Rebase or merge `main` into the working
   branch immediately before final commit. If any contract file changed on
   `main` after the branch was created, the branch must show that file.
2. **All required artifacts for the ticket are present in the diff** --
   source code, data artifacts (CSV/JSON), and test scaffold together, not
   code alone. A ticket is not "implementation complete" if its artifacts
   exist only in a sandbox or local environment.
3. **Test evidence is repo-native.** Test output pasted into the PR must come
   from running tests against the actual branch checkout (local clone or CI),
   never a sandbox reconstruction of file contents. If Builder's sandbox has
   no internet/DB access needed for a test, that test must be run on Devin's
   local machine (`C:\Projects\apexos-fantasy-gm`) and the real output
   captured, not approximated.
4. **Contract-version alignment is explicit.** The PR description states
   which contract version(s) the implementation targets, and Builder has
   confirmed that version is the one physically present on the PR branch --
   not assumed present because it exists on `main`.

## Enforcement

- Builder self-certifies items 1-4 in the PR description before requesting
  Reviewer audit.
- Reviewer's audit scope explicitly includes verifying branch-vs-main sync
  and artifact presence as a first-pass gate, before any deeper correctness
  review -- a sync/artifact failure is grounds for immediate BLOCKED without
  further review time spent.
- This does not replace or weaken the existing Architect-Builder-Reviewer
  escalate-don't-guess pattern (working as intended per Decision Ledger
  v2.2). It closes the specific gap where "code intent is correct" was
  conflated with "release evidence exists."

## Scope

Applies to all remaining backlog tickets B-05 through B-17 and any future
ticket. Retroactively applies to B-04: remediation required before
resubmission per Architect ruling on the B-04 BLOCKED verdict (2026-08-10).

## Status

Active. Owner: Architect. Depends on: Builder/Operator Implementation
Backlog v1.0, Live-Draft Degraded Mode Runbook v1.0 (peer runbook, no
dependency conflict).

---

## Addendum v1.1 — Connector Body-Fetch Fallback (2026-08-10)

**Trigger:** Confirmed during B-04 remediation. GitHub connector's file-content tools
(`get_file_contents`, raw-URL fetch) intermittently return only SHA/status metadata
with no body for larger files -- affecting all three ApexOS spaces (Architect,
Builder/Operator, Reviewer) equally. This is a known tool limitation, not a repo
or content problem, and it can recur on any ticket touching test scaffolds, data
artifacts, or larger contract files.

**Standing rule:**

1. On a body-fetch failure, retry once.
2. On a second failure, do not attempt to reconstruct, retype, or approximate the
   file's content from memory, prior context, or pattern-matching -- regardless of
   how confident the model is. This is the same discipline as the T09 fabricated-
   value failure mode: plausible-looking content that was never actually verified
   against the source is not evidence.
3. Fall back to Devin's local git checkout as the source of truth:
   ```
   git show <branch>:<path>
   ```
   or for a conflict resolution specifically:
   ```
   git checkout --theirs <path>   # or --ours, depending on merge direction
   ```
4. If a byte-exact diff is needed (e.g., confirming a conflict resolution changed
   only an import line), request the diff output directly rather than the full
   file body:
   ```
   git diff main -- <path>
   ```
5. Exploring lower-level connector routes (GitHub Blobs API for base64 payloads,
   authenticated raw-URL fetch) is a legitimate future fix, but is Builder/Operator
   tooling work, not an Architect task, and is not required to unblock any current
   ticket -- local git already provides exact bytes with no size ceiling.

**Scope:** Applies whenever any of the three spaces hits a truncated or bodiless
connector read on this repository. Does not change any contract, schema, or
acceptance criteria. Owner: Architect. Status: Active.
