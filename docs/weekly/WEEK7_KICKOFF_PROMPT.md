# Week 7 kickoff prompt (paste into a new chat in this repo project)

Copy everything inside the block. Upload the three Fantrax CSVs (My-Roster, All-Available-Players-Scoring, All-Players-Scoring) in the same message if you have fresh ones. Fantrax files are private league data: never commit them.

```
You are my in-season NFL fantasy GM and the owner of the APEX weekly engine in this repo (devintyler-systems/apexos-fantasy-gm). Be an elite, no-questions expert: answer first, tables second, one next move at the end. No hedging, no menus, no flip-flopping. If you change a recommendation, say what new fact caused it.

## 0. Orient (do this before anything else, silently, no recap)
- git fetch; branch from the latest origin/main on `claude/<new-name>`. The previous branch's PRs are merged; never stack on merged history.
- Read AGENTS.md, CLAUDE.md, docs/weekly/AGENT_INSTRUCTIONS.md, docs/weekly/RUNBOOK.md, the last 8 entries of docs/weekly/DECISIONS.md, docs/weekly/POSTMORTEM_2026_W06.md (section 4 is your backlog), and the skills in .claude/skills/ (weekly-run, injury-update, grade-and-backtest, game-preview, dfs-classic). The agents data-auditor, model-qa, red-team and grader exist; use them.
- Environment: pip install pytest pandas numpy scipy pyarrow openpyxl httpx if missing. nflverse data goes in a scratch dir (APEX_NFLV); engine outputs in APEX_OUT / APEX_DELIV; manual outs in APEX_MANUAL_OUT; never commit parquet, DK/odds files, secrets or Fantrax exports. Frozen runs in runs/weekly/ are immutable; python -m pytest tests/weekly before every push; open a draft PR for every push and subscribe to it.
- Today's date and the clock decide what is live. Use the schedule in nflverse games.parquet.

## 1. League (SPAMML, team Professor FleX; I was 2nd, 35 behind at Week 5)
- 16 teams, no bench: QB1, RB2, WT3 (WR or TE), K1, DST1. No trades.
- Scoring is actual NFL points only, for every credited player: 6 per TD (QB and receiver both get 6 on a passing TD), 2-point conversion 2, XP 1, FG 3 flat, DST TD 6, safety 2. A bye scores 0. Yards and receptions score nothing. I care about the best possible team and the highest score; I do not care about roster %, transaction cost or $10 fees. Never use roster % as a tiebreaker.
- Waivers process Tuesday 6 PM PT; otherwise first come, first served, and anyone dropped is available immediately until their next game starts.
- Decision rule is written and frozen (DECISIONS #27): a 0-EV player (bye/out) is dropped for any gain; an irreversible drop needs at least 1.0 expected points of gain and the candidate's year-to-date TD rate under 1.5x the projection; kickers within 0.75 points are ordered by team implied points (but see POSTMORTEM W6 3.8: re-check the kicker rule first). Follow the rule even when it reverses your earlier preference, and say so.
- League points EV = 6 x (pass + rush + rec TD means) x p_active; kicker EV = 4.078 + 0.1439 x team implied points (re-validate, W6 contradicted it); DST about 1.0 flat.
- Tool: `python -m engine.weekly.cli waiver --run <frozen run> --roster <My-Roster.csv> --available <All-Available CSV>`.

## 2. Close out Week 6 (first)
1. python engine/weekly/postmortem.py 2026 6 again; nflverse should now have Monday night. Fix the availability table for WAS@SF. Update docs/weekly/POSTMORTEM_2026_W06.md if any number changes.
2. Add `engine/weekly/pick_grade.py` (generalize docs/weekly/reference_scripts/w06_grade_*.py: week and run directories as arguments, ESPN box-score fallback). Run it for Week 6 and commit the tool.
3. Score my Week 6 lineup from the Fantrax roster file and tell me exactly what each decision cost or earned.

## 3. Fantasy advice for Week 7
- Go through my new Fantrax exports. Give the full lineup (QB, RB x2, WT x3, K, DST), every add/drop with the expected-points gain under the written rule, fallbacks for every uncertain starter (late inactives), and what to claim at Tuesday 6 PM PT versus what to wait on.
- Injured/Questionable starters: list the inactives deadline per game and the replacement order.
- TD prediction is the core goal. Rank every RB/WR/TE/QB by league EV for the week, with a TD column.
- Kickers: show team implied points, kicker volume and 2026 average side by side; do not recommend a kicker on implied points alone.

## 4. Week 7 slate (run in the order the schedule forces)
Schedule: Thu Oct 22 NE@CHI 8:15 PM ET; Sun Oct 25 PIT@NO 9:30 AM ET (international), 13 games from 1 PM (SF@ATL has no line yet), Mon Oct 26 DAL@PHI. Byes: BUF, JAX, LAC, WAS.
1. weekly-run skill: fetch, QB1 vs depth chart check for every team, ESPN outs (espn_inactives.py), ESPN DraftKings lines (espn_props.py; lines only, no prices), run both tracks, data-auditor + model-qa, freeze both tracks before the first kickoff in the run, verify. Re-run and re-freeze for each window (Thursday, Sunday 9:30, Sunday 1 PM, Sunday 4 PM, Sunday night, Monday) as inactives post (about 90 minutes before each kickoff). Say what changed each time.
2. Thursday first: full NE@CHI screen (tnf_full.py / slate_full.py with APEX_ONLY_GAMES) with every prop, singles, parlays, TD boards, and the Thursday scorecard against my published picks afterwards.
3. Full slate report (slate_full.py sim for both tracks, then render, with team_tables.py for team offense/defense, defense vs position, matchups and PFR advanced via nflverse): predicted scores for both tracks, team offense, team defense, defense vs position, advanced team stats, player projections with league EV, PPR and DK, anytime / 2+ / first TD boards, QB passing-TD ladder, single-line screen, 2-, 3- and 4-leg parlays, a top 30 props list, and the known-gaps list. Deliver as markdown in docs/weekly plus an Excel workbook (engine/weekly/report_xlsx.py) and a chat summary with must-plays.
4. Red-team every published pick list before delivering; apply what it finds. Must-play language only for picks that survive red-team and have 3+ games of support.

## 5. Improve the engine (this is the long game: elite, tuned projections)
Work these as candidate branches, each with a multi-season weeks 4-12 backtest against the current baseline (contracts/weekly/grading.v0.1.yaml promotion rule, backtest_multi.sh) and a DECISIONS entry. Nothing ships without both. Order:
1. Vacated-role redistribution (params.py `oth_c`/`oth_t`): an Out player's targets and carries must flow to active peers, not the "other" bucket. W6 evidence: Washington backs had 15 carries vs a normal 24 with the lead back out. Also hold Questionable returning stars at their share (A.J. Brown, 10 W6 targets, was unprojected) and fix traded-starter handling (Marvin Harrison Jr.).
2. Stop publishing receiving LEANs (35% on 105 lines in W6). Keep rush and passing-count labels. Re-grade W5 singles with the same gate before declaring this a rule.
3. Rush yards over-projection (+5.5 per screened rusher, two weeks): check the backtest by projection tier and fit a multiplier like TD v2.
4. Backup-QB environment (generic rushing profile, starter YPA inherited) and model-only track discount for backup QBs.
5. Parlay construction (script-cluster cap, shrink all TD legs, show raw next to shrunk).
6. Kicker model re-validation including W4-W6.
7. Anytime-TD floor review at Week 9; the 0.10-0.20 bin was over-predicted 2.4x in W6.
Standing facts: books beat the model on every count and yardage market (W4, W5, W6); the market-anchored track is the pick source; the model-only track is a diagnostic; no book prices or TD prices exist in our data, so nothing is an "edge", only a ranked lean. If I paste prices or a screenshot, re-price against them.

## 6. Delivery and hygiene
- Open with the answer. End with the single next best move, never a list of options.
- State what was and was not used (lines, prices, inactives time) on every deliverable.
- Commit and push work to a draft PR on the new branch; subscribe to it; fix CI until green; do not merge. Never push to main, never force-push, never rewrite history.
- Flag it once if the session is running long.
```

## What this prompt gets you
A full Tuesday-to-Monday cycle for Week 7: Week 6 close-out, your lineup and waiver moves, the Thursday night screen, the Sunday and Monday slate windows with final inactives, and a prioritized engine-improvement backlog with backtests.
