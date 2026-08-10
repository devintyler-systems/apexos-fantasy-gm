# Live-Draft Degraded Mode Runbook

**Artifact:** `live_draft_degraded_mode_runbook`
**Version:** 1.0
**Status:** READY FOR BUILDER + OPERATOR USE
**Owner:** Devin Tyler (Architect)
**Depends On:** League Rules Contract v0.2, Draft Round Order Map Contract v1.0, Draft Recommendation Engine Contract v1.0-v1.2
**Unlocks:** MVP Acceptance Gates, Streamlit Draft UI implementation
**Created:** 2026-08-10

---

## 1. Decision Statement

SPAMML has no draft API — manual entry is the **permanent operating mode**, not a fallback (confirmed in Data Source and Connector Register 2.5). This runbook is therefore not a rare-failure playbook; it is the primary operating procedure for every single draft-day pick. "Degraded mode" language is retained for consistency with ApexOS doctrine, but in this league's context, degraded mode IS normal mode. `confirmed evidence`

This document defines exactly what happens at the keyboard, in what order, for every pick — both Devin's picks and the other 15 teams' picks — plus what happens when something goes wrong (typo, unknown player, ambiguous name, stale projection, clock pressure).

---

## 2. Scope and Non-Goals

**In scope:**
- Step-by-step manual pick entry procedure for all 128 picks
- Player/team identity conflict resolution procedure
- Stale projection data handling and visible banner behavior
- Draft-clock time-pressure procedure (pre-computed top candidates)
- Recovery procedure if Devin's own pick entry is wrong (fat-finger correction)
- Session interruption/resume procedure (if Devin closes the laptop mid-draft)

**Not in scope:**
- Any live platform sync recovery (does not apply — no sync exists to fail)
- Automated pick submission of any kind (explicitly prohibited by shared doctrine — read-only, no autonomous picks)

---

## 3. Standard Operating Procedure: Every Pick, League-Wide

```text
FOR EACH of the 128 picks in the draft, in order:

  1. Devin watches/hears the pick announced on the SPAMML custom site (external
     to ApexOS -- there is no automated feed).

  2. Devin enters into the Draft State Manager (Streamlit UI):
     - pick_number (auto-incremented, but manually confirmable)
     - team making the pick (auto-derived from Draft Round Order Map's
       get_draft_position(pick_number) -- Devin verifies this matches what
       he just heard/saw, does not re-type it)
     - player_id_or_team_id selected (via search/autocomplete against the
       canonical player table)

  3. System validates:
     - Position eligibility check (does this player fit ANY open slot for
       the picking team? -- informational only for other teams, since
       ApexOS doesn't track other teams' full roster construction by default
       at MVP; STRICT for Devin's own picks)
     - Player not already drafted (duplicate-pick guard)

  4. On successful entry: draft_state updates, available_pool removes the
     player, PRV Calculator recalculates (per PRV Calculator Contract PRV03),
     Draft Recommendation Engine recalculates IF it is currently Devin's
     upcoming pick.

  5. If this pick was Devin's: Draft Recommendation Engine payload is
     generated fresh for his NEXT pick and displayed proactively, not on-demand,
     using availability pressure and picks-until-next-turn from the Draft
     Round Order Map.
```

**Note:** ApexOS does not need to track full roster construction for all 15 opposing teams at MVP — only which players are no longer available. Opposing-team roster-fit logic is a Phase 2 refinement if Devin wants to model opponent behavior; MVP only needs the available_pool to shrink correctly.

---

## 4. Procedure: Player/Team Identity Conflict

```text
TRIGGER: Search/autocomplete returns 2+ plausible matches, OR the announced
         player name doesn't cleanly match any canonical_player_id in the pool.

STEPS:
  1. System HALTS auto-progression for this pick entry -- does not guess.
  2. UI presents all candidate matches with disambiguating context
     (team, position, any available identifying data).
  3. Devin manually selects the correct match, OR
  4. If genuinely no match exists (e.g., a practice-squad call-up not in the
     canonical player table), Devin manually creates a new canonical_player_id
     entry with position, team, and a flagged null projection
     (data_freshness_status: incomplete) rather than blocking the draft.
  5. This event is logged: timestamp, ambiguous input, resolution chosen,
     resolved_by: Devin -- for post-draft audit, per shared doctrine's
     "never destructively merge ambiguous identities" rule.

NEVER: Auto-merge on name similarity alone. This is a hard rule inherited
from shared doctrine Section 4 (canonical identity, never destructive merge).
```

---

## 5. Procedure: Stale Projection Data

```text
TRIGGER: Projection Artifact's as_of_timestamp is older than a Builder-
         documented threshold relative to draft_start_timestamp (e.g., >48h,
         tune during implementation), OR any upstream source
         (Sharp Football, VegasInsider, nflverse) was last refreshed before
         a materially relevant roster/injury event.

BEHAVIOR:
  1. UI displays a persistent, impossible-to-miss stale-data banner:
     "Projections last updated: {as_of_timestamp}. Refresh before draft
     if roster/injury news has changed since this snapshot."
  2. Recommendations CONTINUE to be generated -- staleness does not halt
     the tool, since a stale-but-present recommendation beats no
     recommendation during a live draft.
  3. Every recommendation payload's data_freshness_status field reflects
     the true state (fresh | stale | incomplete) -- this is NEVER silently
     hidden or defaulted to "fresh."
  4. If Devin has time before the draft starts, he re-runs the Projection
     Artifact ingest pipeline manually (per Projection Artifact Contract
     Section 5) to refresh the frozen snapshot BEFORE setting
     draft_start_timestamp. Once the draft starts, the artifact is frozen
     per PA04 (Projection Artifact Contract) -- no mid-draft refresh is
     permitted, to preserve reproducibility.

HARD RULE: The system must never claim "live" or "current" data status when
it is not. This is non-negotiable per shared doctrine Section 9.
```

---

## 6. Procedure: Draft-Clock Time Pressure

```text
TRIGGER: SPAMML's actual pick timer (U03, still unconfirmed) creates time
         pressure at Devin's pick.

MITIGATION (pre-computed, not reactive):
  1. As soon as Devin's PREVIOUS pick is entered, the Draft Recommendation
     Engine immediately computes and caches his NEXT recommendation --
     it does not wait for his turn to arrive.
  2. Between his previous pick and his upcoming turn, EVERY intervening
     league pick (per get_picks_between()) triggers a full recalculation
     of PRV and the recommendation payload -- so by the time his turn
     arrives, the top-3 candidates are already computed and displayed,
     zero calculation lag at decision time.
  3. UI displays primary_recommendation + 2 alternatives + snooze buttons
     at all times during the waiting period, updating live as other
     teams pick -- Devin is never staring at a blank screen when his
     turn arrives.

If pick_timer (U03) is confirmed to be aggressive (e.g., under 60 seconds),
this pre-computation requirement becomes a hard performance gate for
Builder, not just a UX nicety -- flag for MVP Acceptance Gates.
```

---

## 7. Procedure: Correcting a Wrong Manual Entry

```text
TRIGGER: Devin realizes a just-entered pick was wrong (wrong player, wrong
         team, mis-heard the announcement).

STEPS:
  1. UI provides an explicit "Undo last entry" action -- reverses the most
     recent draft_state update only (not a general edit-any-pick feature
     at MVP, to avoid data integrity risk mid-draft).
  2. Undo restores: available_pool (player returns), removes the picks_made
     entry, reverts PRV Calculator to its prior state for that pick number.
  3. Devin re-enters the correct pick using the standard procedure (Section 3).
  4. If the error is discovered LATER (not the immediately preceding entry),
     this requires a manual data correction outside the live-draft flow --
     out of scope for in-draft recovery; log the discrepancy and correct
     in the frozen historical record post-draft for future backtest accuracy.
```

---

## 8. Procedure: Session Interruption

```text
TRIGGER: Devin closes the laptop, loses power, or the browser session ends
         mid-draft.

BEHAVIOR:
  1. draft_state is persisted to local SQLite after EVERY pick entry, not
     just at session end -- resuming mid-draft requires zero re-entry of
     already-confirmed picks.
  2. On relaunch, UI reads the last-known draft_state, re-displays the
     current recommendation for whatever pick is now active, and confirms
     with Devin: "Resuming at pick #N -- last confirmed pick was #N-1
     ({player}). Correct?" before allowing new entries.
  3. If picks occurred in the league during the interruption gap that Devin
     hasn't yet entered, he must manually back-fill them in order before
     the system will generate a new recommendation -- the system will not
     guess what happened while it was offline.
```

---

## 9. Acceptance Criteria (feeds directly into MVP Acceptance Gates)

| Procedure | Pass Criterion |
|---|---|
| Standard pick entry | All 128 picks can be entered manually with correct position/eligibility validation |
| Identity conflict | Ambiguous player names halt and prompt disambiguation; never auto-merge |
| Stale data | Banner is visible and accurate at all times; recommendations never silently claim "fresh" when stale |
| Draft clock | Recommendation payload is pre-computed and displayed with zero calculation lag at Devin's turn |
| Wrong entry correction | "Undo last entry" fully reverses draft_state, available_pool, and PRV Calculator state for the immediately preceding pick |
| Session interruption | draft_state persists after every pick; resume flow requires explicit confirmation before continuing |

---

## 10. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| RB01 | Opposing-team roster-fit is not tracked at MVP (Section 3 note) | `design decision` | LOW — MVP only needs available_pool accuracy, not full 15-team roster modeling |
| RB02 | "Undo" is limited to the immediately preceding entry, not arbitrary history | `design decision` | LOW — reduces implementation complexity; edge case (late-discovered error) has a defined manual fallback |
| RB03 | Draft-clock pre-computation performance requirement depends on U03 (pick timer) being confirmed | `unknown` | MEDIUM if pick timer turns out to be very aggressive — flag for Builder to load-test recalculation speed regardless, since the confirmed value is still unknown |

---

## 11. Builder Handoff

**Ordered work:**
1. Implement Section 3 standard pick entry flow in Streamlit UI, wired to Draft State Manager
2. Implement Section 4 identity conflict halt-and-disambiguate flow
3. Implement Section 5 stale-data banner, wired to Projection Artifact's `data_freshness_status`
4. Implement Section 6 pre-computation trigger (fires after every league-wide pick entry, not just Devin's)
5. Implement Section 7 "Undo last entry" action
6. Implement Section 8 session persistence and resume-confirmation flow
7. Validate against Section 9 acceptance criteria as part of MVP Acceptance Gates test suite

**Done definition:** All 6 procedures in this runbook are implemented and demonstrable in a full simulated 128-pick draft session, including at least one deliberately triggered identity conflict, one deliberately stale projection scenario, and one deliberate wrong-entry-then-undo sequence.

**What this unlocks:** MVP Acceptance Gates (the formal pass/fail test suite) and the Streamlit Draft UI implementation itself — this runbook is the last specification document; everything after this is either the test suite or the actual build.
