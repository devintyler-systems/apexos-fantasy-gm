# Data source review, 2026 Week 7

Reviewed 2026-10-22 from the cloud container: every page below was fetched, its tabs, filters and the data endpoints behind them were read, and the useful series were tested against the 27-slate backtest (weeks 4-12, 2023-25) before any recommendation. Nothing here is wired into the model yet.

## Verdicts

| Source | Gets us route or personnel data for 2026? | Worth wiring? | Why |
|---|---|---|---|
| Sharp Football Analysis personnel page | Team personnel by play, yes; player routes, no | Yes, as a tendency feature and a research set; not for volume | Free, play-level, weekly, 2021-2026 |
| NFLsavant | Weekly snaps by player, yes; routes, no (its own flag says participation coverage is false for 2026) | Yes: expected fantasy points, coach PROE, referee crews, OL grades, snap trends | Open JSON API behind the site |
| SumerSports personnel tendency | Season-to-date team personnel only | Low priority | Season aggregates, important fields paywalled |
| Pro Football Reference advanced | Blocked (Cloudflare 403) | Already covered | The same advanced tables are in the nflverse `pfr_advstats` release we use |

## Sharp Football Analysis (sharpfootballanalysis.com/stats-nfl/nfl-offensive-personnel/)

- **Page:** a table of all 32 teams by 11, 12, 13, 21, 22 personnel, plus 2+ TE, 2+ RB, 3+ WR and plays. A Usage/Efficiency toggle, filters for season, week, quarter, down, field zone, distance, score margin, neutral script (quarters 1-3, margin within 14), play type (run or dropback) and RB/TE/WR counts.
- **Data behind it:** one static JSON per season at `https://rmsummerlin.github.io/SFAStatsPages/data/personnel_grouping_{season}.json` (index lists 2021-2026). One row per run or dropback with team, week, quarter, down, distance, zone, margin, yards, EPA, success, dropback flag, RB/TE/WR counts. 2026 holds 11,425 plays through week 6 (generated 2026-10-20). Decoded and checked against the page (CHI: 11 personnel 46.5% vs 47% on the page, 432 plays).
- **Does not have:** player names, routes, formation or alignment. It tells us how many backs, tight ends and receivers were on the field, never which ones.
- **Tests (stack and regression, held-out seasons):** trailing neutral dropback rate improves team pass-attempt RMSE only 7.619 to 7.574 (0.6%); personnel mix adds nothing for carries (7.157 to 7.181); as an add-on to the player projection, team 2+ TE share, 3+ WR share and 2+ RB share all make TE, WR and RB MAE slightly worse (-1.3% to -2.2%). The model already learns the scheme through each player's observed share.
- **Use:** a clean prior for rookies and new-role players (a team that runs 12 personnel 30% of the time has a TE2 role to give), and the only free source of personnel by situation (goal line, third down) for the TD model. Tool: `engine/weekly/sfa_personnel.py` (fetch and decode).

## NFLsavant (nflsavant.com/league)

- **Page:** a React app (the HTML is a shell). Sections seen in the code: League, Teams, Players, Games, Explore (every play since 2013 as a query builder with CSV export from `pub-...r2.dev`), Matchup, Slate, Coaches, Referees, OL grades, Combine/RAS, Madden, Fantasy opportunity, Insights.
- **Open JSON endpoints that answer without a key** (`https://www.nflsavant.com/api/...`): `meta` (latest completed week 5 of its own data), `seasons`, `slate` (week 7, with the referee for each game: Alan Eck for NE@CHI), `league`, `teams`, `fantasy/opportunity` (213 players: targets, target share, air yards share, WOPR, carries, carry share, red-zone opportunities, TD vs expected TD, fantasy points vs expected, weekly splits), `coaches` (PROE, go-for-it rate over expected, no-huddle %, 2-point rate, challenge win % per coach and season: Ben Johnson CHI PROE -2.83, go rate +3.0 over expected), `referees` (per crew flags, yards, DPI, holding, home edge, over %: Eck 10.9 flags a game vs 12.7 league, over 45%), `ol-grades?season=` (pass-block and run-block grades, pressure and sack rates, run lanes, per team), `usage/team/{TEAM}` (weekly snaps and snap percent for every player, role label, trend), `team-situational/{TEAM}` (pass rate by down and distance with top personnel), `pass-chart`, `qb-concepts` and others.
- **Snap trends are the role-change signal we were missing in a usable form:** Roschon Johnson 0, 1, 0, 10, 27, 31 snaps by week (0% to 40%, trend +14.8) while Swift sits at 57.5% and Monangai Out. nflverse `snap_counts` carries the same series; the stack test shows last-3-game snap share helps rush attempts 2.5% and nothing for receiving.
- **Limits:** its own flag says route participation is not available for 2026 (`coverage.participation: false`, FTN true); `usage/player/{gsis}` returned 404 for players that do appear in the team view, so use the team endpoint; its data runs one week behind nflverse (latest week 5 in `meta` while week 6 is final).
- **Use:** pull `fantasy/opportunity` (expected fantasy points and expected TDs) as the TD v3 candidate input and a benchmark; archive `coaches`, `referees`, `slate` and `ol-grades` each window; test coach PROE and OL grades as volume and efficiency features (OL injuries are already in the engine as `inj_ol`).

## SumerSports personnel tendency (sumersports.com/teams/offensive/personnel-tendency/)

- **Page:** a server-rendered table of every team by personnel group (11, 12, 13, 21, 22 and rarer), with plays, usage rate, EPA, EPA per pass and rush, pass rate, league average usage and EPA. Filters: season (URL `?season=2022` to `2026` work, older years fall back to 2026), side, refinement (only 'Standard' exists in the payload). Tabs: Overview, Personnel Tendency, Formation Tendency; defensive side too.
- **Data:** the table data is embedded in the page. Season-to-date only, no weekly cut, so any backtest on it leaks the future. 35 fields are locked behind SumerPass, including snap counts and percent, dropbacks over expected, sack rate and defensive snap rates.
- **Verdict:** nothing here that the Sharp Football play-level set does not give us with weekly granularity. Skip unless the locked fields become available.

## Pro Football Reference advanced (pro-football-reference.com/years/2026/advanced.htm)

- Cloudflare returns HTTP 403 ("Just a moment...") to scripted requests; no workaround attempted (DECISIONS #32). The tables it shows (passing, receiving, rushing and defense advanced) are the nflverse `pfr_advstats` release, which the engine already downloads every run. Nothing to add.

## What is still missing

- **Player-level routes and personnel for 2026.** Not in nflverse (participation stops at 2025, and the 2025/2026 play-by-play files no longer carry personnel columns), not in any of these four sources. FTN charting (already downloaded, unused) has play-action, motion, screen, RPO, box count, blitzers, and drops by play but no player routes. Candidates: a paid feed (PFF, FTN, Next Gen Stats routes), or building routes-run from snap counts plus targets (a proxy).
- **Prices for touchdown markets and passing completions** (the prop sheet has neither).
- **A historical archive of pre-game prop lines** to test the model against the books over more than one week.
