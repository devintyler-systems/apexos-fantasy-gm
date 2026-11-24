# Week 12 preliminary run (Tuesday 2026-11-24, 19:05Z), not frozen

**Defaults in effect:** R-23 availability starter flag (adopted today, DECISIONS #76), R-24 provisional R48 rule (#73), R-27 rush form factor 0.40 (#75), plus #66, #69, #70 and #71.

**Inputs:** nflverse fetched 18:59Z; roster week 12 (full snapshot); depth chart 2026-11-24T18:50Z; schedule lines from nflverse (market track anchors to them). No odds, no salaries. `APEX_MANUAL_OUT=var/ro/manual_out_w12_tue.csv`: 193 rows, all practice-squad players with no depth-chart slot. A second roster pass added nothing.

**Why it is preliminary:** the Week 12 injury report is not out, so availability here is roster and depth chart only; last week's designations are not reliable for this week. GB @ LA kicks off Wednesday 2026-11-25 at 8:00 PM ET, so the freeze has to happen before then.

**QA:**
- data-auditor: slate, team codes, QB1 vs depth chart, reserve and released players, no one on the wrong team: all pass. Its one blocker (stale W11 Questionable designations carried into W12: TB Mayfield 0.34, ARI Beck 0.23, SF Mac Jones, W. Evans, Bowers, McConkey and others) is the missing injury report; treat those probabilities as unknown until Wednesday.
- model-qa: conditional pass. Its "lines miss" finding used a stale file (`/tmp/.../sched.csv`, Nov 18). Against the schedule lines fetched today every game matches within 0.24 points on totals and 0.15 on margins. Probability ranges and TD totals reconcile. R-27 shows: rushing P25–P75 width is 26% wider than in the W11 frozen run (median IQR 45.6 yd vs 36.6), receiving and passing widths unchanged.
- Stale W11 odds files were deleted from both output folders; no W12 odds were loaded.

**Slate (market track):** `slate_w12_tue_prelim.csv`.

**Flags for Wednesday:** NE @ LAC is the lowest total on the board (35.5; model-only 43.4); ARI and TB passing depend on their QB reports; Harrison Wallace (ARI) moved from 6 to 42 projected receiving yards with the ARI QB split; carry concentration holds on PHI, KC and DEN backfields.
