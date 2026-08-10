# Draft Recommendation Engine Contract — v1.1 Addendum

**Resolves:** DR_R03 (user_strategy_controls unconfirmed)
**Supersedes:** Section 3 `user_strategy_controls` placeholder in `draft-recommendation-engine-contract-v1.0.md`
**Status:** APPROVED (pending one open sub-question, see Section 4)
**Created:** 2026-08-10

---

## 1. Decision Statement

Devin's stated strategy: draft the best player available for the open roster need, OR take the scarcity play when overall value justifies it over raw BPA. Confidence is explicitly placed in ApexOS's rankings once calibrated — the stated intent is to follow the system's output, not override it with personal heuristics.

**This maps directly onto the existing `dynamic_prv_score` definition and requires no new weighting logic.** PRV (projected_fantasy_pts minus scarcity-adjusted replacement value) already IS "BPA adjusted for scarcity when the value gap justifies it" — it is not a separate concept that needs to be layered on top. Devin is not asking for a strategy preference; he is confirming the PRV methodology itself is the correct decision rule with no artificial overrides. `confirmed evidence` (direct user statement)

---

## 2. Resolved Strategy Control Values

```yaml
user_strategy_controls:
  positional_priority: none
    # Resolution: no position is boosted or suppressed independent of dynamic_prv_score.
    # "Best player available" = highest final_score among roster-fit-eligible candidates,
    # full stop. Scarcity is already priced into final_score via PRV -- no separate
    # scarcity multiplier or position-specific floor is applied on top.

  d_o_strategy: value_based_no_floor_no_ceiling
    # Resolution: D_O is evaluated on the same final_score basis as every other position.
    # No artificial "never take D_O before round N" rule -- OPEN SUB-QUESTION below on
    # whether this extends fully to KCK as well, or whether an early-round guardrail
    # is wanted for the two shallow, high-scarcity-but-low-ceiling positions.

  te_premium: none
    # Resolution: TE receives zero boost or penalty relative to WR in the REC combined
    # pool. This was already PRV Calculator's default behavior (Contract v1.0, Section 4) --
    # this addendum confirms it as the correct, intentional default rather than an
    # unconfirmed placeholder.

  override_philosophy: "trust_the_model"
    # Resolution: once rankings/projections are calibrated and backtested, Devin's stated
    # intent is to follow system output rather than apply manual judgment overrides at
    # the pick-decision level. This does NOT eliminate manual_environment_override
    # (Projection Artifact Contract Section 6a) -- that remains available for qualitative
    # reads (camp battles, scheme changes) that feed INTO the projection before PRV runs.
    # It specifically means: once a projection is set, don't second-guess the resulting
    # PRV rank at pick time.
```

---

## 3. Practical Effect on Draft Recommendation Engine Contract v1.0

**No changes to Section 4 (Core Calculation Sequence) or Section 5 (Reason Codes) are required.** The engine as originally specified already implements "BPA adjusted for scarcity" via `dynamic_prv_score`. This addendum's only functional effect is:

1. `user_strategy_controls` in Section 3 (Inputs) is no longer `unknown` — it resolves to the neutral/trust-the-model values above
2. DR_R03 is closed as a risk item
3. Reason code `positional_scarcity` (Section 5) now has explicit doctrinal backing: it is not a hedge or a tiebreaker, it is the primary mechanism by which "scarcity value over BPA" gets surfaced to Devin at pick time

---

## 4. Open Sub-Question (not yet resolved — single remaining item)

**Should KCK and/or D_O ever carry an early-round guardrail independent of raw PRV math**, given both are shallow-ceiling positions where even the "best available" option provides limited swing between the 1st and 8th ranked player at the position (compressed value distribution), versus QB/RB/REC where the gap between the 1st and 8th ranked player is typically much larger?

This matters because PRV alone doesn't distinguish between "this position has high scarcity AND high value spread" (worth reacting to early) versus "this position has high scarcity but low value spread" (the math may show scarcity pressure, but skipping the top kicker for a QB with more absolute ceiling ends about the same). Without an answer, the engine will recommend positions purely on `final_score` with no distribution-spread awareness — which may occasionally recommend an early kicker/D_O pick that is mathematically correct by PRV but stylistically unusual for how most SPAMML managers draft.

**Answer options:**
- (a) No guardrail — pure math, if PRV says take the kicker at pick 3, recommend it and explain why
- (b) Soft guardrail — recommend it but flag `unconventional_early_pick` as an additional reason code so Devin can weigh optics/psychology, still his call
- (c) Hard guardrail — suppress KCK/D_O recommendations before a specific round regardless of PRV

---

## 5. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| DR_R03a | "Trust the model" assumes calibration/backtest work (flagged throughout Projection Artifact and PRV contracts) is completed before draft day — trusting an uncalibrated model is a different risk profile than trusting a validated one | `assumption` | MEDIUM — if backtest work doesn't complete before late August draft date, "trust the model" should implicitly mean "trust the model's relative rankings, not its absolute point estimates" |
| DR_R03b | KCK/D_O guardrail question (Section 4) remains open | `unknown` | LOW — engine is fully functional without an answer; defaults to option (a) no guardrail unless Devin specifies otherwise |

---

## 6. Decision Ledger Entry

DR_R03 is resolved. The Draft Recommendation Engine Contract now has zero unconfirmed strategy inputs blocking implementation. One optional refinement (KCK/D_O guardrail flavor) remains open but does not block Builder — default behavior (option a) applies until Devin specifies otherwise.
