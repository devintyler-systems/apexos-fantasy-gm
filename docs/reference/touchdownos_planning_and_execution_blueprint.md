# TouchdownOS — Planning & Execution Blueprint (Design Reference)

> **Status: design-reference.** This is prior art from an earlier planning session and is more rigorous than `nfl_td_projection_framework.md` on scoring-neutrality, time-integrity, and validation. Treat its doctrine (probability-not-picks, team-before-player, frozen artifacts, no time leakage) as directly applicable to the ApexOS Projection Artifact Contract.

**Version 1.0 / 1.1 addendum** | **Purpose:** Evidence-driven NFL touchdown, fantasy-football, and market-decision engine without an opaque player-rating system.

## Core Model Doctrine (non-negotiable principles)

1. Model team scoring environment before player outcomes.
2. Separate team TD volume, TD type, player opportunity, conversion, player capability, fantasy scoring, and market probability as distinct fields.
3. Produce probabilities and distributions, not binary picks.
4. No time leakage — every input known before declared `as_of_timestamp`.
5. Market is a benchmark, not truth — store model-only, market-implied, and market-informed probability separately.
6. Frozen artifacts — every weekly run preserves inputs, feature snapshot, model version, output, and later outcome.
7. Human overrides are data — never overwrite model output; store override value, reason, owner, timestamp, and resulting final projection separately.
8. Backtest before product expansion.

## Scoring Architecture (Actual-Points League Correction — directly applicable to SPAMML)

```text
Game environment
    -> Team offensive scoring opportunities
        -> Offensive TD events (passing TD: QB + receiver; rushing TD: ball carrier)
        -> Field-goal / PAT opportunities (kicker attempt/make distributions)
        -> Defensive / special-teams scoring events (defensive TD, punt/kickoff return TD,
           blocked-kick return TD, safety)
    -> Position-specific scoring distributions
    -> League scoring adapter
```

The football-event engine remains **scoring-neutral**. A separate league scoring adapter converts event distributions into fantasy points — this maps directly onto ApexOS's Projection Artifact -> Scoring Engine separation.

## Kicker Model Specification (directly applicable — SPAMML has a KCK starter slot)

```yaml
position: K
expected_field_goal_attempts: nonnegative_float
expected_field_goals_made: nonnegative_float
expected_pat_attempts: nonnegative_float
expected_pats_made: nonnegative_float
probability_0_field_goals_made: 0.0000-1.0000
probability_2plus_field_goals_made: 0.0000-1.0000
expected_kicker_points: nonnegative_float
probability_kicker_10plus_points: 0.0000-1.0000
```

Model layers: team drive environment -> scoring-choice model -> attempt model (by distance band) -> conversion model (kicker-specific, with shrinkage) -> fantasy adapter:
`E[K points] = 3 x E[FG made] + 1 x E[PAT made]`

Do not infer kicker value from team implied total alone — a high-scoring offense can produce more PATs but fewer FG attempts.

## D/ST Model Specification (directly applicable — SPAMML's D/O slot)

```yaml
position: DST
probability_any_defensive_or_special_teams_td: 0.0000-1.0000
expected_defensive_touchdowns: nonnegative_float
expected_special_teams_return_touchdowns: nonnegative_float
probability_safety: 0.0000-1.0000
expected_safeties: nonnegative_float
expected_dst_actual_points: nonnegative_float
probability_dst_6plus_points: 0.0000-1.0000
```

Scoring-event definition: interception-return TDs, fumble-return TDs, punt-return TDs, kickoff-return TDs, blocked-kick return TDs (if eligible), safeties. Do NOT add points allowed, sacks, interceptions, fumble recoveries, or blocked kicks unless league scoring separately awards them — **SPAMML does not award these; confirmed in League Rules Contract v0.2.**

Model layers: opponent exposure -> turnover creation/vulnerability -> return opportunity -> safety process -> rare-event calibration (heavy shrinkage, long historical windows).

## Canonical Player Projection Output Contract

```yaml
projection_id: uuid
season: 2026
week: 1
game_id: nfl_game_identifier
player_id: canonical_player_identifier
team_id: team_identifier
opponent_id: opponent_identifier
position: QB | RB | WR | TE
as_of_timestamp_utc: ISO-8601 timestamp
model_version: semver_or_git_sha
feature_snapshot_id: immutable_identifier

probability_anytime_td: 0.0000-1.0000
expected_total_tds: nonnegative_float
probability_2plus_tds: 0.0000-1.0000
expected_rushing_tds: nonnegative_float
expected_receiving_tds: nonnegative_float
expected_passing_tds: nonnegative_float_or_null

team_expected_offensive_tds: nonnegative_float
team_probability_0_offensive_tds: 0.0000-1.0000
projected_role_confidence: low | medium | high
active_status_confidence: low | medium | high
data_freshness_status: fresh | stale | incomplete

primary_drivers:
  - name: goal_line_rush_share
    direction: positive
    contribution: 0.00
  - name: projected_team_td_environment
    direction: positive
    contribution: 0.00

raw_model_probability_anytime_td: 0.0000-1.0000
manual_override_probability_anytime_td: null
final_probability_anytime_td: 0.0000-1.0000
```

## Feature Inclusion Rule

No feature enters the model until it has: (1) definition and unit, (2) source and license/usage note, (3) availability time relative to kickoff, (4) historical coverage period, (5) missing-value behavior, (6) leakage assessment, (7) backtest result or explicit experimental status.

## Player Capability Registry (replaces ungrounded 0-100 trait scores)

```yaml
player_id: canonical_player_identifier
as_of_date: YYYY-MM-DD
physical:
  height_inches: number
  weight_lbs: number
  speed_metric: null_or_number
  burst_metric: null_or_number
role_archetypes:
  goal_line_qb: low | medium | high
  early_down_power_back: low | medium | high
  receiving_back: low | medium | high
  perimeter_x_receiver: low | medium | high
  slot_receiver: low | medium | high
  inline_te: low | medium | high
  receiving_te: low | medium | high
expert_observations:
  - label: contested_catch_finisher
    evidence_source: string
    evidence_date: YYYY-MM-DD
    confidence: low | medium | high
    reviewer: string
```

Use this registry as a prior/explanatory layer only after it demonstrates incremental predictive value beyond measurable role and production features. **This directly resolves the framework doc's ungrounded 0-100 trait scale.**

## Data Contracts and Storage

- Raw and analytical data: Parquet + DuckDB
- Small durable app/config state: SQLite
- Model artifacts: versioned files with metadata and Git commit SHA
- Code and decisions: private GitHub repository

```text
raw/            source_manifest, source_payload_metadata, raw_game_data, raw_play_by_play,
                 raw_rosters, raw_injuries, raw_odds
canonical/       dim_player, dim_team, dim_game, player_team_history, coaching_history,
                 player_alias_map
features/        player_game_pregame_features, team_game_pregame_features,
                 role_projection_features, market_snapshot_features
model/           model_registry, training_runs, prediction_runs, predictions,
                 prediction_driver_values, overrides, outcomes, evaluation_metrics
app/             leagues, league_scoring_rules, league_rosters, user_notes
```

## Validation Requirements

- Brier score, log loss, calibration curve, reliability tables by probability band
- Rank performance within position/slate
- Expected vs. realized TD error by position/role/team/environment/week
- Market comparison only at timestamp-matched probabilities
- Backtest protocol: train only on prior seasons/weeks, generate predictions chronologically, freeze data as if live, evaluate by season and slate, compare against baselines, segment failures

**Acceptance gate:** Do not describe as predictive until it produces complete frozen weekly artifacts, runs without manual source reconstruction, meets data-completeness thresholds, demonstrates reasonable calibration out of sample, beats simple baselines, and has a documented failure review process.

---
*Converted from `TouchdownOS-Planning-and-Execution-Blueprint.md`, uploaded 2026-08-09. Full document (Perplexity Space setup, GitHub repo bootstrap, execution roadmap Gates 0-6, weekly runbook) available in original attachment — condensed here to sections directly applicable to ApexOS Projection Artifact Contract design.*
