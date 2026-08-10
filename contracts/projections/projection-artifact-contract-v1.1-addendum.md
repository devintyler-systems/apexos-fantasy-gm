# Projection Artifact Contract — v1.1 Addendum

**Supersedes:** Section 6a `team_expected_offensive_tds` derivation in `projection-artifact-contract-v1.0.md`
**Resolves:** Data Source Register D07 (Sharp Football PPG vs. VegasInsider win-total reconciliation)
**Status:** APPROVED
**Created:** 2026-08-09

---

## 1. Decision Statement

Sharp Football Analysis (projected PPG) and VegasInsider (projected win totals) are both APPROVED 2026 sources but can disagree on a team's offensive quality. Analysis of the actual 2026 data shows strong overall correlation (Pearson r = 0.91 across all 32 teams) but real divergence on specific teams — e.g., Cowboys rank 6th in projected PPG but only 13th in win total; Commanders rank 16th in PPG but 22nd in win total. This pattern indicates strong-offense/weak-defense teams, which is directly relevant signal, not noise to be averaged away. `evidence-backed inference`

**Rule: Sharp Football projected PPG is the PRIMARY team-environment driver. VegasInsider win total is a SECONDARY divergence flag, not a blended input.**

---

## 2. Rationale

PPG projects what the question actually asks: how many points will this team's offense produce, which is the direct driver of TD opportunity. Win total is a function of both offense AND defense/game-script and is one step removed from the signal ApexOS needs. Blending the two into a single averaged number would wash out exactly the useful information the divergence reveals — a high-PPG/low-win-total team is likely to face more negative game scripts (trailing, forced to pass more or abandon the run), which changes TD-type mix (rushing vs. passing) even though total scoring stays similar. `design decision`

---

## 3. Implementation Rule

```text
Step 1: team_expected_offensive_tds baseline = f(sharpfootball_projected_ppg)
        Use PPG as the primary regression input for team TD-count environment,
        per Projection Artifact Contract Section 5 Step 1.

Step 2: Compute divergence_score = ppg_rank - win_total_rank
         (positive = offense outperforms win expectation; negative = underperforms)

Step 3: If abs(divergence_score) >= 5 (threshold, tune during backtest):
         Set game_script_flag: "pass_funnel_risk" (if divergence_score > 0,
           team likely trails more -> pass-funnel skews receiving TD share up,
           rushing TD share down for that team's players)
         OR "positive_script_likely" (if divergence_score < 0,
           team wins more than scoring suggests -> more rushing TD volume
           via clock-control game script)

Step 4: game_script_flag feeds into TD-type-mix allocation (framework doc
         Section 3's "macro trend" concept) as a qualitative adjustment factor,
         NOT into the raw team_expected_offensive_tds count itself.
```

**2026 teams flagged at |divergence| >= 5 based on current snapshot (2026-08-09):**

| Team | PPG Rank | Win Rank | Divergence | Flag |
|---|---|---|---|---|
| Cowboys | 6 | 13 | -7 | pass_funnel_risk |
| Commanders | 16 | 22 | -6 | pass_funnel_risk |

These two teams' players should be evaluated with reduced confidence on rushing-TD projections and elevated confidence on receiving-TD/passing-TD projections until updated data (post-camp, closer to draft) is pulled. `evidence-backed inference`

---

## 4. Output Contract Update

Add to Section 6a (Offensive Player Projection):

```yaml
team_environment_sources:
  primary_ppg_source: "sharpfootball:2026-08-09"
  primary_ppg_value: nonnegative_float
  secondary_win_total_source: "vegasinsider:2026-08-09"
  secondary_win_total_value: nonnegative_float
  divergence_score: integer   # ppg_rank - win_total_rank
  game_script_flag: null | "pass_funnel_risk" | "positive_script_likely"
```

---

## 5. Acceptance Test Addition

### PA10 — Team Environment Precedence (BLOCK)
```
team_expected_offensive_tds must be derived from primary_ppg_value only.
secondary_win_total_value must never appear in the arithmetic that produces
team_expected_offensive_tds -- it may only populate divergence_score and
game_script_flag.
```

---

## 6. Risks and Assumptions

| ID | Item | Label | Impact if Wrong |
|---|---|---|---|
| P05 | Divergence threshold of 5 ranks is an initial guess, not backtested | `assumption` | LOW — tune against 2025 actuals (TeamRankings PPG vs. opponent PPG as a proxy) once backtest harness exists |
| P06 | game_script_flag is currently qualitative-only; no quantitative TD-type-mix adjustment formula defined yet | `unknown` | Flagged for a future Projection Artifact refinement once nflverse pass/rush split data is incorporated |

---

## 7. Decision Ledger Entry

This addendum resolves D07 without blocking the PRV Calculator Contract. Both source citations (`sharpfootball:2026-08-09`, `vegasinsider:2026-08-09`) are now fully specified with a precedence rule, satisfying Projection Artifact Contract PA01 (source citation completeness).
