# ApexOS Fantasy GM — Assumptions Register

| ID | Assumption | Default | Affected Module | Risk | Owner | Decision Deadline |
|---|---|---|---|---|---|---|
| U01 | 2026 draft pick position | unknown | optimizer_prv, availability_model | HIGH | Devin | Before optimizer calibration |
| U02 | Draft date/time | Late August 2026 | projection_artifact_freeze | MEDIUM | Devin | 2 weeks before draft |
| U03 | Pick timer | unknown | draft_clock_ui | LOW | Devin | Before draft UI build |
| U04 | Trading during draft | unknown | draft_state_manager | LOW | Devin | Before draft UI build |
| U05 | Missed FG/PAT penalty | 0 (no penalty) | kicker_projection | LOW | Devin | Before scoring engine build |
| U06 | Waiver rules / FAAB | unknown | phase2_waiver_optimizer | MEDIUM | Devin | Before Phase 2 build |
| U07 | Playoff format and team count | unknown | phase2_schedule_model | LOW | Devin | Before Phase 2 build |
| U08 | Keeper status | Redraft assumed | draft_value_model | MEDIUM | Devin | Before projection ingest |
| U09 | Weekly prize tie-split rule | 1 winner (no split) | d_o_prize_ev_model | LOW | Devin | Before Phase 2 build |
