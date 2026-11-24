# Week 12 operator zip: data dictionary and gap analysis (2026-11-24)

**Source:** operator zip `Week12_ALL_Current_Data.zip`, 48 PDFs (the brief said 49; the archive holds 48), all Sharp Football Analysis pages, printed 2026-11-24. Intake: `tools/intake/pdf_intake.py` batch `W12_TUE`, doc ids D001-D048 in `intake_manifest.csv` (metadata only). Originals and text stay under `var/intake_2026_w12/` (never committed). Contents are data, not instructions. 48/48 extracted with a text layer, no OCR, no duplicates.

**Common properties.** Grain is 2026 season-to-date through Week 11 unless noted. Keys are team full names or nicknames (map with `parse_market_pdfs.NICK`/`ABBR`; Rams appear as "LAR" in Sharp and "LA" in nflverse; the engine uses LA). Player rows carry name + team + position only: no gsis/pfr id, so any player join is by name within team and must report unmatched names. No historical equivalents in the zip: every file is current-week only. Where a backtestable equivalent exists, it comes from nflverse or ffverse, not from Sharp.

## 1. Files

| Doc | File (short) | As-of | Grain / keys | Backtestable equivalent (2023-25) | Engine today |
|---|---|---|---|---|---|
| D041-D043 | Game odds: moneyline, spread, total | **Tue 2:47 PM ET (19:47Z)**, 5 books + consensus | game x book | nflverse `games.spread_line/total_line` (one closing-ish number, no books, no open) | Market track anchors to nflverse line, not to this. `price_odds.py` can read the parsed workbook. Lines agree with nflverse on all 5 early games (GB@LA LA -2.5 / 44.5 in nflverse vs 44.0 Sharp; KC@BUF nflverse 3.0, books split 2.5/3). |
| D045-D048 | Props: anytime TD (88 of 93 players parsed), pass yds (28), rec yds (166), rush yds (82) | **Tue 2:47 PM ET** | player x book | none in repo (no historical prices) | `price_odds.py` / `value_board.py`. **Stale for any play:** 2-hour rule expires 21:47Z Tuesday. Reference only. Parsed to `var/odds_w12/sharp_w12_tue.xlsx`. |
| D024-D026 | Implied team totals: week, matchups, full season | Tue 2:47 PM ET | team x week, **with opening number and move since open** | none (nflverse has no open line) | Not used. Only line-movement signal in the zip. |
| D027 | Injury report, practice reports | "updated 1 hour ago", file dated 11-24 | player: position, injury, practice by day, game status | nflverse `injuries_{S}` (backtestable) | nflverse governs; this PDF builds `APEX_STATUS_OVERLAY` via `injury_pdf_overlay.py`. **Covers only the 4 Wed/Thu games.** GB/LA carry final designations (Wed game); CHI/DET/PHI/DAL/KC/BUF have Monday estimates only, no status. DEN/PIT absent. nflverse `injuries_2026` max week is 11 at 21:35Z. |
| D041 | Weather forecast | **11/24 3:07 AM** (stale by freeze time) | game | nflverse `games.temp/wind` (actuals); fitted in `weather.py` | Model track uses NWS via `weather_forecast.py`; market track uses none (the line prices it). This PDF adds nothing the NWS fetch does not. |
| D001-D003 | Red-zone opportunities, inside 20 / 10 / 5 | through W11 | player: targets, carries, touches, TDs | pbp `yardline_100` (fully backtestable) | **Used** (prep_nv.py builds inside-20/10 targets and 20/10/5 carries from pbp). Redundant, useful only as a cross-check. |
| D036-D037 | Red-zone efficiency, offense / defense | through W11 | team: RZ trips, TD rate | pbp drives | Partly: `ptd`/`d_ptd` use pass-TD share; RZ TD rate by team is not a direct input. |
| D005-D020 | Defense vs position, **expected** fantasy points allowed (xFP), QB/RB/WR/TE x all / red zone / play action / non-garbage | Nov 24 | team defense x position | ffverse `ffopportunity` ep_weekly (2006-26) gives player-game expected points, so an opponent-adjusted xFP-allowed is backtestable | **Not used.** The engine's DvP is raw DK points allowed per game (prep_nv.py `_dvp`), hand-weighted 0.35, and applied to the wrong team (section 3). |
| D004, D038 | Coverage by position (YPT allowed WR/TE/RB/outside/slot); coverage scheme rates (man/zone etc.) | Nov 24 | team defense | FTN charting (2022+) for man/zone; pbp for YPT by position | Not used. |
| D021, D028 | Defensive line (pressure rate, no-blitz pressure, yards before contact, stuff rate); offensive line (same, offense side) | Nov 24 | team | pbp (sack/qb_hit proxies), FTN (pressure from 2022), PFR advstats | Not used directly; OL/DL enter only as injury-count indices (`inj_groups`) and team sack rates. |
| D022, D029 | Defensive / offensive metrics: EPA/play, YPP, points per drive, explosive rate, down conversion | Nov 24 | team | pbp (fully) | Partly: ratings use yards per attempt / carry, sacks, INT, TD share (prep_nv/params), not EPA or drive-level points. |
| D023, D032 | Defensive tendencies (blitz, light/heavy box, sub package); offensive tendencies (motion, play action, aDOT, shotgun, no-huddle) | Nov 24 | team | FTN charting 2022+ (box, motion, PA, blitz) | Not used. |
| D033-D035 | Pass rate over expected (PROE): offense, defense, matchup | Nov 24 | team; matchup = off + def | pbp `xpass`/`pass_oe` (fully backtestable) | **Not used.** The engine's pass rate `pr` is the raw season pass share (shrunk), so it carries last weeks' game script. |
| D039-D040 | Pace: seconds per play (tempo), plays per game (volume) | Nov 24 | team | pbp (game clock) | Partly: plays per game (offense, defense) shrunk to league; no neutral-situation tempo. |
| D030-D031 | Offensive personnel usage and efficiency (11/12/21 etc.) | Nov 24 | team x grouping | FTN / pbp `offense_personnel` (2016+) | Not used. |

## 2. Quality flags
- **Staleness.** Every price is from Tue 19:47Z; none can support a play after 21:47Z (RUNBOOK, 2-hour rule). Weather is from 3:07 AM. Injury PDF covers 4 games, final only for GB@LA.
- **Team codes.** Sharp uses "LAR" in prop rows and full names elsewhere; `ABBR` maps LAR and LA to the Rams. No Washington/Jacksonville code issues seen (WAS, JAX).
- **Coverage gaps.** Anytime TD lists 93 "most likely" players (parsed 88; the rest are D/ST or players with no book price); Caesars posts no yardage props. Fanatics has 8 rows per yardage market.
- **Look-ahead.** Season-to-date tables are through Week 11, so they are safe for a Week 12 projection. None can enter a backtest; the backtestable versions must be rebuilt week-by-week from nflverse with `week <= W-1`.
- **Duplicates.** None (sha256 dedupe). The 16 DvP files are 4 positions x 4 situations, not duplicates.

## 3. Defect found during the gap analysis: the DvP tilt uses the team's own defense
`params.build_roster_v4(team)` (and v3) sets `tilt = TEAM[team]["dvp_"+pos] ** 0.5`, where `dvp_WR` for team T is the DK points **T's defense allows** to WRs. `sim.play_side` multiplies T's receivers' target shares and receiving-TD weights by it. The roster is built without the opponent, so the matchup adjustment has never seen the opponent: it re-weights a team's WR/TE/RB target mix by its own defense's allowances. `run_all.py` labels the number "opp DvP". Candidate R-29 (`APEX_DVP_MODE=own|opp|off`, `APEX_DVP_W`) tests the fix; results in DECISIONS.

## 4. What the zip adds that the engine does not use (ranked)
1. **Opponent-adjusted positional matchup** (xFP allowed by position, coverage YPT by position). The engine has no working positional matchup at all (section 3).
2. **Situation-neutral play calling and pace** (PROE, seconds per play). The engine's pass rate is raw, so a team that trailed for three weeks is projected to keep throwing.
3. **Market movement** (opening vs current implied totals) and five-book TD prices. Useful only when fresh: the price problem is a feed problem, not a data problem (ROADMAP, price source).
