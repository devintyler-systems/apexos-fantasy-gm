# Draft Recommendation Engine Contract — v1.2 Addendum

**Resolves:** Open sub-question in v1.1 addendum (KCK/D_O guardrail flavor)
**Adds:** New capability — "Snooze" user override
**Supersedes:** Section 4 sub-question in `draft-recommendation-engine-contract-v1.1-addendum.md`
**Status:** APPROVED
**Created:** 2026-08-10

---

## 1. Decision Statement

Devin's answer: option (b), soft guardrail. Kicker before round 4 is a real deviation from how he plays; D_O outside the last 2 rounds is also atypical. But he does not want a hard block — if the model surfaces a genuinely compelling case, he wants to see it and decide. This requires two additions to the Draft Recommendation Engine: (1) a convention-deviation flag, informational only, never affecting ranking math, and (2) a new "snooze" control letting Devin defer a specific recommended player by one round without losing the system's tracking of that player. `confirmed evidence` (direct user statement)

---

## 2. Soft Guardrail: Convention Deviation Flag

### 2a. Trigger Definition

```text
Given SPAMML's 8-round draft (confirmed round boundaries from Draft Round Order
Map Contract v1.0):

IF primary_recommendation.position_slot == KCK AND current_round < 4:
  ADD reason_code: "unconventional_early_kicker"

IF primary_recommendation.position_slot == D_O AND current_round < 7:
  ADD reason_code: "unconventional_early_do"

Where current_round is derived from pick_number using the Draft Round Order
Map's round boundaries (Round 1: picks 1-16, Round 2: 17-32, etc.)
```

**This is purely additive to `reason_codes` (Section 5 of the base contract).** It does NOT alter `dynamic_prv_score`, `final_score`, or the ranking that determines `primary_recommendation` vs. `alternatives`. If PRV math says the kicker is the best value at pick 3, it remains the primary recommendation — it just now carries an explicit flag that this is atypical for how Devin normally drafts, so he can weigh it consciously rather than by default. `design decision`

### 2b. Closed-Set Reason Code Addition

Add to the Section 5 closed vocabulary in the base contract:

| Code | Trigger Condition |
|---|---|
| `unconventional_early_kicker` | Primary recommendation is KCK before round 4 |
| `unconventional_early_do` | Primary recommendation is D_O before round 7 |

---

## 3. New Capability: Snooze-for-1-Round

### 3a. Decision Statement

When the engine's `primary_recommendation` doesn't feel right to Devin at that moment — not wrong, just early — he needs a way to say "skip this player for my current pick only, but keep tracking them" without that action permanently removing the player from consideration or corrupting the PRV/availability model. This is a **user-initiated, pick-scoped filter**, not a data mutation. `design decision`

### 3b. Snooze Action Contract

```yaml
snooze_action:
  snooze_id: uuid
  player_id_or_team_id: canonical_identifier
  snoozed_at_pick_number: integer   # Devin's current pick when snooze was invoked
  rounds_requested: integer          # default 1, per Devin's stated use case
  reason: null_or_string             # optional free-text note, not required
  timestamp_utc: ISO-8601 timestamp
  outcome: pending | player_survived | player_drafted_by_other_team
    # populated retroactively once Devin's next pick occurs
```

### 3c. Engine Behavior

```text
Step 1: When Devin invokes snooze(player_X) at his current pick:
  - player_X is EXCLUDED from primary_recommendation and alternatives
    for THIS pick's recommendation payload only
  - player_X's dynamic_prv_score, scarcity_ratio, and all PRV Calculator
    outputs remain COMPLETELY UNCHANGED -- snooze is a display/candidacy
    filter applied AFTER PRV ranking, never a data mutation
  - The engine re-runs Step 5 (final score + rank) over the remaining
    eligible candidates to produce a new primary_recommendation

Step 2: At Devin's NEXT pick (rounds_requested picks later):
  - IF player_X is still undrafted: player_X re-enters the candidate pool
    normally, ranked purely on current dynamic_prv_score -- no penalty,
    no boost, exactly as if never snoozed
  - IF player_X was drafted by another team in the interim: outcome logs
    as player_drafted_by_other_team -- this is the accepted risk of
    snoozing, surfaced for post-draft review, not an error state

Step 3: Snooze log entry is appended to the draft session record for
  post-draft review ("did snoozing cost me value?") -- this is informational
  history, not a live input to any future recommendation's math.
```

### 3d. UI/Interaction Requirement (for Streamlit Draft UI, downstream)

The recommendation display must expose a "Snooze 1 round" action directly on `primary_recommendation` and each item in `alternatives`. Invoking it must trigger the Step 1 re-ranking synchronously and show the new primary recommendation without requiring a page reload or re-entering draft state.

---

## 4. Output Contract Update

Add to the base contract's Section 6 output:

```yaml
active_snoozes: [array of snooze_action records still pending outcome]
snooze_available_for: [player_id_or_team_id array -- which current candidates
                        can be snoozed, i.e., all of them except D_O/KCK
                        which have no meaningful "wait" value once your last
                        pick approaches -- see 4a caveat]
```

### 4a. Caveat: Snooze Near Draft End

If `rounds_requested` would push past Devin's final pick (Round 8), the snooze action must be rejected with a clear error — there is no "next pick" to defer to. This is a hard validation rule, not a judgment call.

---

## 5. Acceptance Tests

### DR09 — Convention Flag Does Not Alter Ranking (BLOCK)
```
Given a KCK candidate with the highest final_score at round 2, the engine
must still set it as primary_recommendation AND attach unconventional_early_kicker.
Both conditions must be true simultaneously -- the flag never suppresses the pick.
```

### DR10 — Snooze Excludes Only Current-Pick Candidacy (BLOCK)
```
After snoozing player_X at pick N, player_X must not appear in
primary_recommendation or alternatives for pick N's payload, but
player_X's dynamic_prv_score in the PRV Calculator's independent output
must be verifiably unchanged (byte-identical) before and after the snooze action.
```

### DR11 — Snoozed Player Returns Cleanly (BLOCK)
```
If player_X survives to Devin's next pick after being snoozed for 1 round,
player_X must be re-evaluated using current (not stale) dynamic_prv_score
and may become primary_recommendation again with zero penalty or flag
carried over from the snooze action.
```

### DR12 — Snooze Rejected Past Final Pick (BLOCK)
```
Attempting to snooze a player at Devin's 8th (final) pick, or with
rounds_requested that would exceed the 8th pick, must return a validation
error, not a silent no-op or a crash.
```

### DR13 — Snooze Log Never Feeds Future Math (BLOCK)
```
Two otherwise-identical draft simulations, one where player_X was snoozed
and later drafted elsewhere, one where no snooze occurred at all, must
produce IDENTICAL dynamic_prv_score and final_score for every OTHER
remaining player at every subsequent pick. Snoozing player_X must have
zero side effect on anyone else's valuation.
```

---

## 6. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| DR_R05 | Round boundaries for the KCK/D_O flag (round 4, round 7) are Devin's stated preference, not derived from any objective threshold | `design decision` | LOW — purely cosmetic/informational; easy to adjust the round cutoff without touching ranking logic |
| DR_R06 | Snooze is scoped to "1 round" per Devin's example; the contract supports arbitrary `rounds_requested` but only 1 has been validated against his actual use case | `assumption` | LOW — UI can default to 1 and expose more only if requested later |
| DR_R07 | No limit is defined on how many snoozes Devin can use per draft | `unknown` | LOW — default to unlimited; revisit only if it becomes a usability problem in practice |

---

## 7. Decision Ledger Entry

Both open items from the v1.1 addendum are now resolved. The Draft Recommendation Engine Contract has zero remaining blocking unknowns. Snooze is a genuinely new capability, not a strategy-tuning parameter — it requires Builder to implement a stateful, pick-scoped filter that is fully isolated from the PRV Calculator's independent math (per DR10/DR13), which is the primary integration risk to test carefully.
