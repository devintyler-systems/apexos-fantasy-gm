# W9/W10 post mortem + W11 package: checkpoint

Run opened 2026-11-18 21:19 UTC (13:19 PST). Operator: Devin. Phase: **0 complete, intake gate OPEN (2026-11-18 ~22:00Z)**.

## Verified at bootstrap
- Repos (branch `claude/zealous-hopper-0cibcy`, clean): `devintyler-systems/apexos-fantasy-gm` @ 9f00a6d (= origin/main), `devintyler-systems/APEX-OS` @ dffa1ea. Note: the prompt's `devintyler83/...` owner is wrong; the org is `devintyler-systems`.
- Weekly engine authority: `engine/weekly/` (DECISIONS.md latest #65; promotion rules in `contracts/weekly/grading.v0.1.yaml`). APEX-OS in-season layer: `apexos_in_season/` (source contract v1 + v1.3.0 addendum).
- **No archived Week 9 or Week 10 predictions exist** on any branch (latest frozen runs: `runs/weekly/2026_w08_*`, last commit 2026-11-03). W9/W10 retrospective model evaluation of original forecasts = unavailable; only a labelled time-correct replay is possible, and nflverse historical feeds are revised (data-vintage limit).
- Schedule (ESPN scoreboard API, retrieved 2026-11-18 ~21:20Z): `schedule_w09_w11.csv`. W9 15 games (bye PIT, TEN) all final; W10 14 games (bye CHI, DEN, PHI, TB) all final; W11 13 games (bye ATL, CLE, GB, LAR, NE, SEA), none started. International: W9 CIN@ATL Madrid, W10 NE@DET Munich, W11 MIN@SF Mexico City.
- **Deadline:** W11 TNF IND@HOU kicks off 2026-11-20 01:15 UTC (Thu 8:15 PM ET), ~28 h after run open.
- Network: ESPN, open-meteo, weather.gov, sleeper reachable via proxy; `github.com/nflverse/*` downloads are blocked (repo not in session scope) — this blocks the engine's nflverse fetch until resolved.
- Tooling: pymupdf + pdfplumber + tesseract 5.3.4 installed (container-local, not persistent). Intake tool `tools/intake/pdf_intake.py` smoke-tested (text, OCR, sha256 dedupe).

## Intake (closed)
- Batch B01 = `apex_pdfs_1.zip` (operator: "All files added"), 46 files, 46 unique sha256, 0 duplicates, 46/46 text-layer extraction, 0 OCR needed, 0 failed. Count matches expected 46.
- 46 files = 18 evidence families, ~4 publishers (Sharp Football Analysis ~38, FFToday 1, Football Zebras 1, unverified 4). Multiple views of one tool are NOT independent (e.g. D022-D024, D039-D041).
- Info cutoffs: season stats through W10 (updated 2026-11-17); W11 odds/props/ITT 2026-11-18 14:27 ET; weather 11-18 00:39 + per-game Tue updates; referees 11-18.
- Limitations: (1) column-major text: names and numbers are in separate blocks in props, RZ, first-TD, personnel docs, so they need a coordinate-based row parse (verified feasible on D043); text order must not be used to join. (2) D044 rec-yds props have no NYJ, LAC, WSH rows. (3) No document predates W11, so none can be used as pregame evidence for W9/W10 (leakage); they serve W11 and forward only. (4) D003/D005/D006/D009 publisher unverified; betting-history content, context only.

## Decisions
- nflverse: required (engine fetch, grading, replay all read it). Operator asked to approve attaching `nflverse/nflverse-data` read-only. Fallback if not unblocked by 2026-11-19 12:00 ET: TNF IND@HOU on ESPN summaries + PDFs, marked provisional, every substitution logged.

## Next exact action
Build coordinate parsers for F16/F17 (odds, props) and F01 (red zone) into `var/.../parsed/*.csv`, validate 5 sampled values per doc against the page image; in parallel start the W9/W10 actuals reconciliation from ESPN summaries.
