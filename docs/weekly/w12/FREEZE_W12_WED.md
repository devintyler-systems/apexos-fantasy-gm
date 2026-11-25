# Week 12 Wednesday freeze (2026-11-25)

| Run | Track | Anchoring | Frozen (UTC) | Branch |
|---|---|---|---|---|
| `2026_w12_market_20261125T211249Z` | market | raw | 21:12 | claude/awesome-goldberg-yak905 |
| `2026_w12_model_20261125T211252Z` | model-only | raw | 21:12 | claude/awesome-goldberg-yak905 |
| `2026_w12_market_20261125T190858Z` | market | anchored to 18:54Z lines (early-line, #91) | 19:08 | claude/odds-backfill-2023-25 (#111) |

All verify intact. Engine defaults: #66, #69, #70, #71, #73, #75, #76, R-31 (#82), R-40 (#89). No odds in the raw runs (stale 11-24 files removed from the bundle), no salaries.

**Inputs:** nflverse 21:01Z (schedule via the nfldata games.csv fallback, #fetch fix db075ef). W12 injury report: GB/LA final; the eight Thursday/Friday teams practice-only (designations pending); Sunday/Monday teams have no W12 report, so those 11 games are provisional. Depth chart 17:56Z; QB1 matches for all 32 (TB Mayfield, ARI Beck at p 1.0 pending their reports).

**QA:** model-qa PASS, data-auditor PASS. Warnings: PHI 23% of carries in 'other' (Barkley under-projected, #35/#43); QB pass yds 5-12% below receiver sum by design (#59/#65); Walker KC p 0.998 on Limited practice although every book pulled his lines (#61 ordering); Pittman PIT held out by R-24 until PIT designates.

**Market-track game projections (raw):** GB 20.6 @ LA 23.1; CHI 28.5 @ DET 26.9; PHI 19.6 @ DAL 27.9; KC 21.8 @ BUF 24.6; DEN 20.0 @ PIT 16.5.

**Next:** re-freeze the Thursday games after their Wednesday-afternoon designations (by 00:30Z); anchored T-2h re-freezes per game in the backfill session; DEN@PIT re-freeze after PIT's Thursday report.
