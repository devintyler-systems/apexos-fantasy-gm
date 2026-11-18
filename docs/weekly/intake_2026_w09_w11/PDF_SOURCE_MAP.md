# Operator PDF pack (46 files, 18 evidence families): where each family plugs into Apex

Status labels follow the data-source register:
- **benchmark** = labelled outside comparison, never an input.
- **input** = used through an existing engine path with provenance.
- **context** = narrative only.

Nothing here replaces Apex-owned projections.

| Family | Docs | Use now (W11) | Use going forward | Status |
|---|---|---|---|---|
| F16 game odds | D039–D041 | Parsed into an Odds-API-style workbook (`tools/intake/parse_market_pdfs.py`) and priced against both tracks; 26/26 rows per market | Weekly priced window for `calibration_ledger.csv` (DECISIONS #64 needs 4 windows before non-TD props can return) | input (prices, var/ only) |
| F17 player props | D042–D045 | 2,165 book rows, 166 anytime-TD players + 13 D/ST (D/ST not priced), 94 rec, 58 rush, 25 pass; Olave page-break and Burrow values checked against the page | Same; once archived weekly, enables price-aware backtests the repo can't run today | input (prices, var/ only) |
| F10 implied team totals | D022–D024 | Open line and move: closing-line-value tracking and stale-anchor check (#63 KC@DEN) | Line-movement feature for market-track freeze timing | benchmark |
| F15 weather | D038 | Roof notes fill nflverse roof NaN (IND@HOU and TEN@DAL are retractable; NRG open ~15% of games) | Cross-check of the NWS feed in `weather_forecast.py` | benchmark / context |
| F01 red-zone opportunity | D001–D002 | Outside check on TD shares (the only market we still bet) | Candidate red-zone share prior; needs a weeks 4–12 backtest | benchmark |
| F12 PROE, F14 pace | D030–D032, D036–D037 | Compare against engine `pass_rate` and `plays` per team; flag disagreements over 1 SD | Neutral-script pass-rate prior; pace/tempo prior | benchmark |
| F09 unit metrics (OL/DL pressure, EPA, PPD, tendencies) | D019–D021, D025–D026, D029 | Cross-check of sack and pressure inputs (engine `inj_ol`, `inj_pr_opp`) | Most of this is reproducible from nflverse play-by-play; build it there rather than from PDFs | benchmark |
| F11 personnel usage/efficiency | D027–D028 | 12-personnel share: test bed for the TE-over / WR-under split (RETRO R-04) | Personnel-aware target split; `sfa_personnel.py` already pulls this kind of data | benchmark |
| F07 coverage (man/zone, YPT by alignment) | D010, D035 | WR/TE matchup notes | Coverage-aware efficiency (needs data with a history) | context |
| F08 defense vs position xFP | D011–D018 | Fantasy GM matchup benchmark (labelled) | Same | benchmark |
| F05 first TD | D007–D008 | Context for first-TD pricing | – | context |
| F13 red-zone efficiency | D033–D034 | Context | – | context |
| F03 run/pass (FFToday) | D004 | Second source on pass rate | – | benchmark |
| F18 referee assignments | D046 | Logged per game (substitutions possible) | – | context |
| F02 referee trends, F04 coach ATS, F06 team ATS | D003, D005–D006, D009 | Not used: betting-history splits, unverified publisher, high noise | – | rejected as features |

**Independence.** About 38 of the 46 files come from one publisher. Views of one tool count once (D022–D024, D039–D041, D030–D032).

**Biggest strategic gain.** A dated weekly capture of F16/F17 (Wednesday, Friday, Sunday 11:00 ET) plus F10 builds the historical price archive the repo lacks. That archive is the only route to reversing DECISIONS #64 with evidence. A direct export or API from the publisher, if their terms allow it, beats PDFs. With PDFs, `parse_market_pdfs.py` handles the layout, and every new pack must reconcile to the "N OF N PLAYERS" counts on each page.
