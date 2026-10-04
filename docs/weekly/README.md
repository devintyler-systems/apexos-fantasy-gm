# Weekly props + DFS engine

Self-contained inside `apexos-fantasy-gm`. Entry point: `apex-weekly` (or `python -m engine.weekly.cli`).

```
pip install -e ".[dev,weekly]"
apex-weekly fetch  --season 2026                 # nflverse cache -> var/nflverse (gitignored)
apex-weekly run    --season 2026 --track both    # model-only + market-anchored, sequential
apex-weekly freeze --season 2026 --week 5 --track market   # immutable, hashed run -> runs/weekly/<run_id>/
apex-weekly verify runs/weekly/<run_id>
apex-weekly grade  runs/weekly/<run_id>          # after the games are final
APEX_DK_SALARIES=/path/DKSalaries_classic.csv apex-weekly run --season 2026 --dfs
```

Environment: `APEX_NFLV`, `APEX_OUT`, `APEX_DELIV`, `APEX_RUNS` (paths), `APEX_INPUTS` and `APEX_ODDS_XLSX` (operator-supplied files), plus the model knobs listed in RUNBOOK.md.

Files: `BLUEPRINT_v4.md` (design and lessons), `RUNBOOK.md` (as built), `AGENT_INSTRUCTIONS.md` (agent system prompt), `DECISIONS.md` (decisions and Gate Bypass Log).
Contracts: `contracts/weekly/`. Tests: `tests/weekly/` (`-m integration` needs the nflverse cache).

Human inputs each week: DK salary CSV, odds workbook or API key, bankroll (optional), lineup submission. Everything else is automated.
Known follow-ups: Showdown optimizer, official-inactives ingest, QB-swap-aware model-only environment, relative-import refactor of the flat pipeline modules.
