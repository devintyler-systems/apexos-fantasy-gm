# Claude Code instructions

1. Read `AGENTS.md` first. Its non-negotiables apply everywhere.
2. Weekly props + DFS engine work: follow `docs/weekly/AGENT_INSTRUCTIONS.md`, the runbook in `docs/weekly/RUNBOOK.md`, and the skills in `.claude/skills/`.
3. The weekly engine lives only in `engine/weekly/`, `contracts/weekly/`, `config/weekly/`, `tests/weekly/`, `runs/weekly/`, `docs/weekly/`. Never import the draft engine from it.
4. Never overwrite a frozen run in `runs/weekly/`. Never commit parquet, DK salary files, odds files or secrets.
5. A model or calibration change ships only with a multi-season week 4-12 backtest against the current baseline (`contracts/weekly/grading.v0.1.yaml`, promotion_rule) and an entry in `docs/weekly/DECISIONS.md`.
6. Run `python -m pytest tests/weekly` before every push; the weekly workflow also runs the integration test.
