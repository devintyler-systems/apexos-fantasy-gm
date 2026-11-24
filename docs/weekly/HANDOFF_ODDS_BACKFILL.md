# Handoff: one-time historical odds backfill (ROADMAP P-1b)

Owner bought The Odds API 20K plan (one month) on 2026-11-24 to backtest the anytime-TD edge rule on real 2023-25 prices.

**Key handling.** The Odds API accepts the key only as the `apiKey` query parameter (tested 2026-11-24: an Authorization header gives 401 MISSING_KEY), so a proxy network secret cannot carry it. The key lives in the environment variable `ODDS_API_KEY` (set by the owner in the environment settings; never in chat, never committed). Check with `echo ${ODDS_API_KEY:+set}`.

**Steps** (from the repo root, `APEX_PY=/home/user/.venv-apex/bin/python`; nflverse cache must exist, see BACKTEST_HOWTO):
1. `$APEX_PY tools/backtest/odds_backfill.py --check` : two sample games; confirm `player_anytime_td` and the books; note credits used.
2. `$APEX_PY tools/backtest/odds_backfill.py --seasons 2023 2024 2025 --weeks 4-12 --markets player_anytime_td --max-credits 6000` : about 4,000 credits.
3. If credits allow: a second pass into a separate folder with `player_reception_yds,player_rush_yds,player_pass_yds` (about 12,000 more). Keep the total under 18,000.
4. Price each backtest player-game (b12/prn3 pickles) against the de-vigged book price; report engine vs book vs 50/50 blend (Brier, log loss) by season, and the simulated P&L of the 5-point blended-edge rule. Record in DECISIONS.
5. Tell the owner to cancel the plan.

Output stays in `var/odds_hist/` (never committed). Never run this inside a freeze window.
