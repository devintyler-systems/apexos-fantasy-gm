---
name: dfs-classic
description: Build DraftKings Classic cash lineup and a 20-lineup GPP set from the frozen simulation (needs the operator's DKSalaries_classic.csv).
---
# DFS Classic

Input: `APEX_DK_SALARIES=<path>` (never commit). Run `apex-weekly run --dfs` (collects sims, builds pool, ILP optimizer via PuLP/CBC).
Scoring and roster rules: `contracts/weekly/dk_salaries.v1.yaml`. GPP: 40% exposure cap, stack required, bring-back; report mean and P95 per lineup.
Exclude any player the NFL report lists Out even if DK status is blank. Showdown is not implemented; say so rather than approximating.
