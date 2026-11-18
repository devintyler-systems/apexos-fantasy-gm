# W9/W10 post mortem + W11 package: checkpoint

Run opened 2026-11-18 21:19 UTC (13:19 PST). Operator: Devin. Phase: **1+2 complete (retro + change register, no model change); phase 3 (W11) next**.

## Verified at bootstrap
- Repos (branch `claude/zealous-hopper-0cibcy`, clean): `devintyler-systems/apexos-fantasy-gm` @ 9f00a6d (= origin/main), `devintyler-systems/APEX-OS` @ dffa1ea. Note: the prompt's `devintyler83/...` owner is wrong; the org is `devintyler-systems`.
- Weekly engine authority: `engine/weekly/` (DECISIONS.md latest #65; promotion rules in `contracts/weekly/grading.v0.1.yaml`). APEX-OS in-season layer: `apexos_in_season/` (source contract v1 + v1.3.0 addendum).
- **No archived Week 9 or Week 10 predictions exist** on any branch (latest frozen runs: `runs/weekly/2026_w08_*`, last commit 2026-11-03). W9/W10 retrospective model evaluation of original forecasts = unavailable; only a labelled time-correct replay is possible, and nflverse historical feeds are revised (data-vintage limit).
- Schedule (ESPN scoreboard API, retrieved 2026-11-18 ~21:20Z): `schedule_w09_w11.csv`. W9 15 games (bye PIT, TEN) all final; W10 14 games (bye CHI, DEN, PHI, TB) all final; W11 13 games (bye ATL, CLE, GB, LAR, NE, SEA), none started. International: W9 CIN@ATL Madrid, W10 NE@DET Munich, W11 MIN@SF Mexico City.
- **Deadline:** W11 TNF IND@HOU kicks off 2026-11-20 01:15 UTC (Thu 8:15 PM ET), ~28 h after run open.
- Network: ESPN, open-meteo, weather.gov, sleeper reachable via proxy. RESOLVED 2026-11-18 ~21:45Z: the block was on `nflverse/nfldata` raw files (not used by the engine); `nflverse/nflverse-data` release assets download (schedules, stats_player_week_2026 through W10, pbp, snap_counts, injuries, depth_charts all HTTP 200). W11 schedule has 2 games with roof NaN (fill from D038).
- Tooling: pymupdf + pdfplumber + tesseract 5.3.4 installed (container-local, not persistent). Intake tool `tools/intake/pdf_intake.py` smoke-tested (text, OCR, sha256 dedupe).

## Intake (closed)
- Batch B01 = `apex_pdfs_1.zip` (operator: "All files added"), 46 files, 46 unique sha256, 0 duplicates, 46/46 text-layer extraction, 0 OCR needed, 0 failed. Count matches expected 46.
- 46 files = 18 evidence families, ~4 publishers (Sharp Football Analysis ~38, FFToday 1, Football Zebras 1, unverified 4). Multiple views of one tool are NOT independent (e.g. D022-D024, D039-D041).
- Info cutoffs: season stats through W10 (updated 2026-11-17); W11 odds/props/ITT 2026-11-18 14:27 ET; weather 11-18 00:39 + per-game Tue updates; referees 11-18.
- Limitations: (1) column-major text: names and numbers are in separate blocks in props, RZ, first-TD, personnel docs, so they need a coordinate-based row parse (verified feasible on D043); text order must not be used to join. (2) D044 rec-yds props have no NYJ, LAC, WSH rows. (3) No document predates W11, so none can be used as pregame evidence for W9/W10 (leakage); they serve W11 and forward only. (4) D003/D005/D006/D009 publisher unverified; betting-history content, context only.

## Decisions
- nflverse: operator approved read-only (2026-11-18); access verified. No ESPN substitution needed; ESPN fallback cancelled.

## Phase 1/2 (done 2026-11-18 ~22:50Z)
- `RETRO_2026_W09_W10.md`: hindsight diagnostic replay (no archived forecasts), scorecard, largest misses, signals, change register R-01..R-09. No model/calibration change.
- Tools: `tools/replay/{build_vintage,availability_proxy,score_replay}.py`. Engine needs Python 3.12 (`uv venv -p 3.12 /home/user/.venv-apex`; container 3.13 is rejected by pyproject).
- Replay data/outputs: `var/replay_2026_w{09,10}/` (gitignored).

## Next exact action
W11: parse D039-D045 (odds/props) by coordinates -> var/w11_odds.xlsx in the price_odds.py format; fetch; run both tracks for week 11 (TNF IND@HOU first); data-auditor + model-qa; freeze before 2026-11-20 01:15Z.
