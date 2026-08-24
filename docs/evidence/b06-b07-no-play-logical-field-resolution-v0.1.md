# B-06/B-07 `no_play` Logical Source-Field Resolution Evidence v0.1

## Run identity

- Branch: `docs/b06-b07-no-play-logical-field-resolution-v0.1`
- Tested canonical main: `0b28fc6f5aaf308805616b9421c3c7113ba4f9ae`
- Evidence source: official retained 2023 nflverse PBP Parquet candidate
- Python: 3.12.10
- PyArrow: 22.0.0
- Provider request during this resolution: none
- Raw-data mutation: none

## Source identity

| Field | Value |
|---|---|
| Release tag | `pbp` |
| Release ID | `58152862` |
| Asset ID | `354728689` |
| Asset name | `play_by_play_2023.parquet` |
| Size | `20,534,088` bytes |
| Provider SHA-256 | `bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776` |
| Computed SHA-256 | `bd3484731408def6b0ec93225bba2bd7b2c65769ca707a2b9444d891abdc6776` |
| Rows | `49,665` |
| Columns | `372` |

## Investigation method

PyArrow `ParquetFile` metadata and selected-column reads were run directly against the retained
official candidate. The investigation printed the complete Arrow schema, low-cardinality value
distributions, null counts, cross-tabs, and bounded descriptions for mismatches and exceptional
rows. It made no provider request and wrote no raw or derived data.

## Full observed Arrow schema

<!-- FULL_SCHEMA_BEGIN -->

| Column | Arrow dtype | Nullable |
|---|---|---:|
| `play_id` | `double` | true |
| `game_id` | `string` | true |
| `old_game_id` | `string` | true |
| `home_team` | `string` | true |
| `away_team` | `string` | true |
| `season_type` | `string` | true |
| `week` | `int32` | true |
| `posteam` | `string` | true |
| `posteam_type` | `string` | true |
| `defteam` | `string` | true |
| `side_of_field` | `string` | true |
| `yardline_100` | `double` | true |
| `game_date` | `string` | true |
| `quarter_seconds_remaining` | `double` | true |
| `half_seconds_remaining` | `double` | true |
| `game_seconds_remaining` | `double` | true |
| `game_half` | `string` | true |
| `quarter_end` | `double` | true |
| `drive` | `double` | true |
| `sp` | `double` | true |
| `qtr` | `double` | true |
| `down` | `double` | true |
| `goal_to_go` | `int32` | true |
| `time` | `string` | true |
| `yrdln` | `string` | true |
| `ydstogo` | `double` | true |
| `ydsnet` | `double` | true |
| `desc` | `string` | true |
| `play_type` | `string` | true |
| `yards_gained` | `double` | true |
| `shotgun` | `double` | true |
| `no_huddle` | `double` | true |
| `qb_dropback` | `double` | true |
| `qb_kneel` | `double` | true |
| `qb_spike` | `double` | true |
| `qb_scramble` | `double` | true |
| `pass_length` | `string` | true |
| `pass_location` | `string` | true |
| `air_yards` | `double` | true |
| `yards_after_catch` | `double` | true |
| `run_location` | `string` | true |
| `run_gap` | `string` | true |
| `field_goal_result` | `string` | true |
| `kick_distance` | `double` | true |
| `extra_point_result` | `string` | true |
| `two_point_conv_result` | `string` | true |
| `home_timeouts_remaining` | `double` | true |
| `away_timeouts_remaining` | `double` | true |
| `timeout` | `double` | true |
| `timeout_team` | `string` | true |
| `td_team` | `string` | true |
| `td_player_name` | `string` | true |
| `td_player_id` | `string` | true |
| `posteam_timeouts_remaining` | `double` | true |
| `defteam_timeouts_remaining` | `double` | true |
| `total_home_score` | `double` | true |
| `total_away_score` | `double` | true |
| `posteam_score` | `double` | true |
| `defteam_score` | `double` | true |
| `score_differential` | `double` | true |
| `posteam_score_post` | `double` | true |
| `defteam_score_post` | `double` | true |
| `score_differential_post` | `double` | true |
| `no_score_prob` | `double` | true |
| `opp_fg_prob` | `double` | true |
| `opp_safety_prob` | `double` | true |
| `opp_td_prob` | `double` | true |
| `fg_prob` | `double` | true |
| `safety_prob` | `double` | true |
| `td_prob` | `double` | true |
| `extra_point_prob` | `double` | true |
| `two_point_conversion_prob` | `double` | true |
| `ep` | `double` | true |
| `epa` | `double` | true |
| `total_home_epa` | `double` | true |
| `total_away_epa` | `double` | true |
| `total_home_rush_epa` | `double` | true |
| `total_away_rush_epa` | `double` | true |
| `total_home_pass_epa` | `double` | true |
| `total_away_pass_epa` | `double` | true |
| `air_epa` | `double` | true |
| `yac_epa` | `double` | true |
| `comp_air_epa` | `double` | true |
| `comp_yac_epa` | `double` | true |
| `total_home_comp_air_epa` | `double` | true |
| `total_away_comp_air_epa` | `double` | true |
| `total_home_comp_yac_epa` | `double` | true |
| `total_away_comp_yac_epa` | `double` | true |
| `total_home_raw_air_epa` | `double` | true |
| `total_away_raw_air_epa` | `double` | true |
| `total_home_raw_yac_epa` | `double` | true |
| `total_away_raw_yac_epa` | `double` | true |
| `wp` | `double` | true |
| `def_wp` | `double` | true |
| `home_wp` | `double` | true |
| `away_wp` | `double` | true |
| `wpa` | `double` | true |
| `vegas_wpa` | `double` | true |
| `vegas_home_wpa` | `double` | true |
| `home_wp_post` | `double` | true |
| `away_wp_post` | `double` | true |
| `vegas_wp` | `double` | true |
| `vegas_home_wp` | `double` | true |
| `total_home_rush_wpa` | `double` | true |
| `total_away_rush_wpa` | `double` | true |
| `total_home_pass_wpa` | `double` | true |
| `total_away_pass_wpa` | `double` | true |
| `air_wpa` | `double` | true |
| `yac_wpa` | `double` | true |
| `comp_air_wpa` | `double` | true |
| `comp_yac_wpa` | `double` | true |
| `total_home_comp_air_wpa` | `double` | true |
| `total_away_comp_air_wpa` | `double` | true |
| `total_home_comp_yac_wpa` | `double` | true |
| `total_away_comp_yac_wpa` | `double` | true |
| `total_home_raw_air_wpa` | `double` | true |
| `total_away_raw_air_wpa` | `double` | true |
| `total_home_raw_yac_wpa` | `double` | true |
| `total_away_raw_yac_wpa` | `double` | true |
| `punt_blocked` | `double` | true |
| `first_down_rush` | `double` | true |
| `first_down_pass` | `double` | true |
| `first_down_penalty` | `double` | true |
| `third_down_converted` | `double` | true |
| `third_down_failed` | `double` | true |
| `fourth_down_converted` | `double` | true |
| `fourth_down_failed` | `double` | true |
| `incomplete_pass` | `double` | true |
| `touchback` | `double` | true |
| `interception` | `double` | true |
| `punt_inside_twenty` | `double` | true |
| `punt_in_endzone` | `double` | true |
| `punt_out_of_bounds` | `double` | true |
| `punt_downed` | `double` | true |
| `punt_fair_catch` | `double` | true |
| `kickoff_inside_twenty` | `double` | true |
| `kickoff_in_endzone` | `double` | true |
| `kickoff_out_of_bounds` | `double` | true |
| `kickoff_downed` | `double` | true |
| `kickoff_fair_catch` | `double` | true |
| `fumble_forced` | `double` | true |
| `fumble_not_forced` | `double` | true |
| `fumble_out_of_bounds` | `double` | true |
| `solo_tackle` | `double` | true |
| `safety` | `double` | true |
| `penalty` | `double` | true |
| `tackled_for_loss` | `double` | true |
| `fumble_lost` | `double` | true |
| `own_kickoff_recovery` | `double` | true |
| `own_kickoff_recovery_td` | `double` | true |
| `qb_hit` | `double` | true |
| `rush_attempt` | `double` | true |
| `pass_attempt` | `double` | true |
| `sack` | `double` | true |
| `touchdown` | `double` | true |
| `pass_touchdown` | `double` | true |
| `rush_touchdown` | `double` | true |
| `return_touchdown` | `double` | true |
| `extra_point_attempt` | `double` | true |
| `two_point_attempt` | `double` | true |
| `field_goal_attempt` | `double` | true |
| `kickoff_attempt` | `double` | true |
| `punt_attempt` | `double` | true |
| `fumble` | `double` | true |
| `complete_pass` | `double` | true |
| `assist_tackle` | `double` | true |
| `lateral_reception` | `double` | true |
| `lateral_rush` | `double` | true |
| `lateral_return` | `double` | true |
| `lateral_recovery` | `double` | true |
| `passer_player_id` | `string` | true |
| `passer_player_name` | `string` | true |
| `passing_yards` | `double` | true |
| `receiver_player_id` | `string` | true |
| `receiver_player_name` | `string` | true |
| `receiving_yards` | `double` | true |
| `rusher_player_id` | `string` | true |
| `rusher_player_name` | `string` | true |
| `rushing_yards` | `double` | true |
| `lateral_receiver_player_id` | `string` | true |
| `lateral_receiver_player_name` | `string` | true |
| `lateral_receiving_yards` | `double` | true |
| `lateral_rusher_player_id` | `string` | true |
| `lateral_rusher_player_name` | `string` | true |
| `lateral_rushing_yards` | `double` | true |
| `lateral_sack_player_id` | `string` | true |
| `lateral_sack_player_name` | `string` | true |
| `interception_player_id` | `string` | true |
| `interception_player_name` | `string` | true |
| `lateral_interception_player_id` | `string` | true |
| `lateral_interception_player_name` | `string` | true |
| `punt_returner_player_id` | `string` | true |
| `punt_returner_player_name` | `string` | true |
| `lateral_punt_returner_player_id` | `string` | true |
| `lateral_punt_returner_player_name` | `string` | true |
| `kickoff_returner_player_name` | `string` | true |
| `kickoff_returner_player_id` | `string` | true |
| `lateral_kickoff_returner_player_id` | `string` | true |
| `lateral_kickoff_returner_player_name` | `string` | true |
| `punter_player_id` | `string` | true |
| `punter_player_name` | `string` | true |
| `kicker_player_name` | `string` | true |
| `kicker_player_id` | `string` | true |
| `own_kickoff_recovery_player_id` | `string` | true |
| `own_kickoff_recovery_player_name` | `string` | true |
| `blocked_player_id` | `string` | true |
| `blocked_player_name` | `string` | true |
| `tackle_for_loss_1_player_id` | `string` | true |
| `tackle_for_loss_1_player_name` | `string` | true |
| `tackle_for_loss_2_player_id` | `string` | true |
| `tackle_for_loss_2_player_name` | `string` | true |
| `qb_hit_1_player_id` | `string` | true |
| `qb_hit_1_player_name` | `string` | true |
| `qb_hit_2_player_id` | `string` | true |
| `qb_hit_2_player_name` | `string` | true |
| `forced_fumble_player_1_team` | `string` | true |
| `forced_fumble_player_1_player_id` | `string` | true |
| `forced_fumble_player_1_player_name` | `string` | true |
| `forced_fumble_player_2_team` | `string` | true |
| `forced_fumble_player_2_player_id` | `string` | true |
| `forced_fumble_player_2_player_name` | `string` | true |
| `solo_tackle_1_team` | `string` | true |
| `solo_tackle_2_team` | `string` | true |
| `solo_tackle_1_player_id` | `string` | true |
| `solo_tackle_2_player_id` | `string` | true |
| `solo_tackle_1_player_name` | `string` | true |
| `solo_tackle_2_player_name` | `string` | true |
| `assist_tackle_1_player_id` | `string` | true |
| `assist_tackle_1_player_name` | `string` | true |
| `assist_tackle_1_team` | `string` | true |
| `assist_tackle_2_player_id` | `string` | true |
| `assist_tackle_2_player_name` | `string` | true |
| `assist_tackle_2_team` | `string` | true |
| `assist_tackle_3_player_id` | `string` | true |
| `assist_tackle_3_player_name` | `string` | true |
| `assist_tackle_3_team` | `string` | true |
| `assist_tackle_4_player_id` | `string` | true |
| `assist_tackle_4_player_name` | `string` | true |
| `assist_tackle_4_team` | `string` | true |
| `tackle_with_assist` | `double` | true |
| `tackle_with_assist_1_player_id` | `string` | true |
| `tackle_with_assist_1_player_name` | `string` | true |
| `tackle_with_assist_1_team` | `string` | true |
| `tackle_with_assist_2_player_id` | `string` | true |
| `tackle_with_assist_2_player_name` | `string` | true |
| `tackle_with_assist_2_team` | `string` | true |
| `pass_defense_1_player_id` | `string` | true |
| `pass_defense_1_player_name` | `string` | true |
| `pass_defense_2_player_id` | `string` | true |
| `pass_defense_2_player_name` | `string` | true |
| `fumbled_1_team` | `string` | true |
| `fumbled_1_player_id` | `string` | true |
| `fumbled_1_player_name` | `string` | true |
| `fumbled_2_player_id` | `string` | true |
| `fumbled_2_player_name` | `string` | true |
| `fumbled_2_team` | `string` | true |
| `fumble_recovery_1_team` | `string` | true |
| `fumble_recovery_1_yards` | `double` | true |
| `fumble_recovery_1_player_id` | `string` | true |
| `fumble_recovery_1_player_name` | `string` | true |
| `fumble_recovery_2_team` | `string` | true |
| `fumble_recovery_2_yards` | `double` | true |
| `fumble_recovery_2_player_id` | `string` | true |
| `fumble_recovery_2_player_name` | `string` | true |
| `sack_player_id` | `string` | true |
| `sack_player_name` | `string` | true |
| `half_sack_1_player_id` | `string` | true |
| `half_sack_1_player_name` | `string` | true |
| `half_sack_2_player_id` | `string` | true |
| `half_sack_2_player_name` | `string` | true |
| `return_team` | `string` | true |
| `return_yards` | `double` | true |
| `penalty_team` | `string` | true |
| `penalty_player_id` | `string` | true |
| `penalty_player_name` | `string` | true |
| `penalty_yards` | `double` | true |
| `replay_or_challenge` | `double` | true |
| `replay_or_challenge_result` | `string` | true |
| `penalty_type` | `string` | true |
| `defensive_two_point_attempt` | `double` | true |
| `defensive_two_point_conv` | `double` | true |
| `defensive_extra_point_attempt` | `double` | true |
| `defensive_extra_point_conv` | `double` | true |
| `safety_player_name` | `string` | true |
| `safety_player_id` | `string` | true |
| `season` | `int32` | true |
| `cp` | `double` | true |
| `cpoe` | `double` | true |
| `series` | `double` | true |
| `series_success` | `double` | true |
| `series_result` | `string` | true |
| `order_sequence` | `double` | true |
| `start_time` | `string` | true |
| `time_of_day` | `string` | true |
| `stadium` | `string` | true |
| `weather` | `string` | true |
| `nfl_api_id` | `string` | true |
| `play_clock` | `string` | true |
| `play_deleted` | `double` | true |
| `play_type_nfl` | `string` | true |
| `special_teams_play` | `double` | true |
| `st_play_type` | `string` | true |
| `end_clock_time` | `string` | true |
| `end_yard_line` | `string` | true |
| `fixed_drive` | `double` | true |
| `fixed_drive_result` | `string` | true |
| `drive_real_start_time` | `string` | true |
| `drive_play_count` | `double` | true |
| `drive_time_of_possession` | `string` | true |
| `drive_first_downs` | `double` | true |
| `drive_inside20` | `double` | true |
| `drive_ended_with_score` | `double` | true |
| `drive_quarter_start` | `double` | true |
| `drive_quarter_end` | `double` | true |
| `drive_yards_penalized` | `double` | true |
| `drive_start_transition` | `string` | true |
| `drive_end_transition` | `string` | true |
| `drive_game_clock_start` | `string` | true |
| `drive_game_clock_end` | `string` | true |
| `drive_start_yard_line` | `string` | true |
| `drive_end_yard_line` | `string` | true |
| `drive_play_id_started` | `double` | true |
| `drive_play_id_ended` | `double` | true |
| `away_score` | `int32` | true |
| `home_score` | `int32` | true |
| `location` | `string` | true |
| `result` | `int32` | true |
| `total` | `int32` | true |
| `spread_line` | `double` | true |
| `total_line` | `double` | true |
| `div_game` | `int32` | true |
| `roof` | `string` | true |
| `surface` | `string` | true |
| `temp` | `int32` | true |
| `wind` | `int32` | true |
| `home_coach` | `string` | true |
| `away_coach` | `string` | true |
| `stadium_id` | `string` | true |
| `game_stadium` | `string` | true |
| `aborted_play` | `double` | true |
| `success` | `double` | true |
| `passer` | `string` | true |
| `passer_jersey_number` | `int32` | true |
| `rusher` | `string` | true |
| `rusher_jersey_number` | `int32` | true |
| `receiver` | `string` | true |
| `receiver_jersey_number` | `int32` | true |
| `pass` | `double` | true |
| `rush` | `double` | true |
| `first_down` | `double` | true |
| `special` | `double` | true |
| `play` | `double` | true |
| `passer_id` | `string` | true |
| `rusher_id` | `string` | true |
| `receiver_id` | `string` | true |
| `name` | `string` | true |
| `jersey_number` | `int32` | true |
| `id` | `string` | true |
| `fantasy_player_name` | `string` | true |
| `fantasy_player_id` | `string` | true |
| `fantasy` | `string` | true |
| `fantasy_id` | `string` | true |
| `out_of_bounds` | `double` | true |
| `home_opening_kickoff` | `double` | true |
| `qb_epa` | `double` | true |
| `xyac_epa` | `double` | true |
| `xyac_mean_yardage` | `double` | true |
| `xyac_median_yardage` | `int32` | true |
| `xyac_success` | `double` | true |
| `xyac_fd` | `double` | true |
| `xpass` | `double` | true |
| `pass_oe` | `double` | true |

<!-- FULL_SCHEMA_END -->

## Candidate-field distributions

| Field | Dtype | Nulls | Observed distribution / result |
|---|---|---:|---|
| `play_type` | string | 1,452 | `pass` 20,723; `run` 14,877; `no_play` 4,555; `kickoff` 2,838; `punt` 2,352; `extra_point` 1,238; `field_goal` 1,107; `qb_kneel` 454; `qb_spike` 69 |
| `play_type_nfl` | string | 0 | COMMENT 4; END_GAME 285; END_QUARTER 869; FIELD_GOAL 1,107; FUMBLE_RECOVERED_BY_OPPONENT 15; GAME_START 285; INTERCEPTION 454; KICK_OFF 2,838; PASS 18,778; PAT2 126; PENALTY 2,372; PUNT 2,351; RUSH 15,266; SACK 1,459; TIMEOUT 2,054; UNSPECIFIED 159; XP_KICK 1,243 |
| `play_deleted` | double | 0 | `0.0` for all 49,665 rows; cannot represent no-play status |
| `penalty` | double | 1,488 | `1.0` 3,229; `0.0` 44,948; not equivalent because 764 penalty rows had `play_type != "no_play"` |
| `desc` | string | 0 | 45,006 distinct descriptions; 2,496 contained “No Play”; two replay-reversal rows ended with `play_type` `pass` or `punt` |
| `aborted_play` | double | 0 | `1.0` 98; `0.0` 49,567; represents aborted mechanics, not nullification |
| `st_play_type` | string | 49,665 | No non-null values; cannot represent no-play status |
| `first_down_penalty` | double | 1,488 | `1.0` 983; `0.0` 47,194; describes first-down effect, not nullification |
| `penalty_team` | string | 46,436 | 32 non-null team values; penalty identity, not play disposition |
| `penalty_player_id` | string | 46,700 | 1,146 non-null identifiers; penalty identity, not play disposition |
| `penalty_player_name` | string | 46,700 | 1,075 non-null names; penalty identity, not play disposition |
| `penalty_yards` | double | 46,436 | 47 non-null values; penalty enforcement distance, not nullification |
| `penalty_type` | string | 46,436 | 52 non-null categories; penalty classification, not final play disposition |
| `drive_yards_penalized` | double | 567 | 79 non-null values; drive-level penalty yardage, not row nullification |

`play_type = "no_play"` cross-tabbed to `play_type_nfl` as: PENALTY 2,372; TIMEOUT
2,053; UNSPECIFIED 125; XP_KICK 5. Seven no-play rows retained a rush/pass/spike flag, including
six two-point rows; the proposed true branch excludes them before any B-07 opportunity use.

All 1,452 null `play_type` rows had zero rush/pass opportunity shape. They consisted of game
start/end, end-quarter, comment, timeout, and eight UNSPECIFIED administrative/declined-penalty
records. Consequently null does not silently become false; it conservatively becomes true unless
a true rush/pass opportunity flag creates an unknown state.

## Rejected candidate mappings

- `play_deleted = 1`: rejected because the field was always zero.
- `penalty = 1`: rejected because accepted penalties can remain attached to valid pass/run plays
  and B-07 owns a separate penalty exclusion.
- description contains “No Play”: rejected because two replay-reversal descriptions retained the
  phrase although the final provider `play_type` was `pass` or `punt`.
- `play_type_nfl = "PENALTY"`: rejected because provider `play_type = "no_play"` also covered
  timeouts, unspecified records, and XP rows.

## Proven mapping

```text
if play_type column is absent:
  unknown
elif play_type == "no_play":
  true
elif play_type is null and (pass_attempt is true or rush_attempt is true):
  unknown
elif play_type is null:
  true
elif play_type in {
  "extra_point", "field_goal", "kickoff", "pass", "punt",
  "qb_kneel", "qb_spike", "run"
}:
  false
else:
  unknown
```

`pass_attempt` and `rush_attempt` must also be present. True means boolean true or numeric `1`.
Any unknown result fails B-06 promotion; it is never passed to B-07 or treated as false.

Applied to all 49,665 retained rows, the mapping produced 6,007 true values (4,555 explicit
`no_play` plus 1,452 null administrative/non-opportunity rows), 43,658 false values, and zero
unknown values.

## Mapping truth table

| Raw condition | Logical result | Required behavior |
|---|---|---|
| `play_type = "no_play"` | true | Exclude |
| Recognized non-no-play value | false | Continue to independent B-07 predicates |
| Null `play_type`, no true rush/pass flag | true | Conservative exclusion |
| Null `play_type`, true rush or pass flag | unknown | Fail B-06 promotion |
| Required source field absent | unknown | Fail B-06 promotion |
| Unexpected non-null `play_type` | unknown | Fail B-06 promotion |

## Risks and limitations

- Evidence is from the authenticated-by-digest official 2023 asset only. Every later selected
  season must independently validate the required fields, domain, and zero unknown rows.
- Conservative true handling for null non-opportunity records can create false negatives if a
  provider later nulls `play_type` on a real opportunity without setting its opportunity flag.
  The explicit flag guard converts that observed conflict to unknown and blocks promotion.
- The mapping does not infer penalty acceptance, sacks, spikes, or two-point semantics. Their
  existing B-07 filters remain independent.

## Boundary declarations

- The retained raw candidate remained byte-identical and unmodified.
- No B-06 revision, manifest, or pointer was promoted.
- No B-07 lookup table, artifact, test of lookup computation, or projection output was generated.
- B-07 remains blocked on controlled B-06 revisions for 2023, 2024, and 2025 and all other gates.

## Verification trace

```text
python -m pytest tests/ -k 'b06 or no_play' -v
collected 199 items / 171 deselected / 28 selected
tests\acceptance\test_b06_no_play_logical_field.py: 27 passed
tests\review\test_b06_release_schema_evidence.py: 1 passed
28 passed, 171 deselected in 0.63s
exit code: 0
```

Final diff, scope, and repository-state commands are recorded in the Codex completion evidence.
