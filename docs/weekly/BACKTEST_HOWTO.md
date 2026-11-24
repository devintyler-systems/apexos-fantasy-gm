# Backtest how-to (weeks 4-12, 2023-25)

Tooling lives in `tools/backtest/`. Nothing here writes to `config/`, `runs/` or any frozen artifact.

## 0. Environment
```
uv venv -p 3.12 /home/user/.venv-apex && VIRTUAL_ENV=/home/user/.venv-apex uv pip install -e ".[weekly,dev]" pymupdf
export APEX_PY=/home/user/.venv-apex/bin/python
```
nflverse cache: `python -c "import sys; sys.path.insert(0,'engine/weekly'); from fetch_data import fetch; fetch(2026, history=(2022,2023,2024,2025))"` (2022 is needed for the 2023 prior season).

## 1. One tag = 27 slates
```
tools/backtest/run_tag.sh TAG [KNOB=VALUE ...]
```
- 4 slates in parallel (`BT_PAR`), about 11 s a slate on 4 cores, so about 85 s a tag.
- Every `APEX_*` variable in the caller's shell is cleared first; only the knobs on the command line apply. Seeds: default 20261004, `APEX_SEED=777`, `APEX_SEED=999`.
- Output `var/bt/bt_{S}_w{W}_{TAG}.pkl` (players, with q10/q25/q75/q90 for rec_yds, rec, rush_yds, pass_yds) and `btteam_*` (team means and spreads); logs in `var/bt/logs/`, one line per tag in `var/bt/logs/tags.log`.
- Resumable: existing pickles are skipped; `BT_FORCE=1` reruns. Narrow with `BT_SEASONS="2025" BT_WEEKS="6"`.
- **Never edit `engine/weekly/` while a tag is running.** Each slate imports the code when it starts; an edit mid-run mixes two versions in one tag (it happened on 2026-11-24: the first b12a run crashed on three slates and was rerun with `BT_FORCE=1`).

## 2. Baseline, determinism and noise floor
```
tools/backtest/run_tag.sh b12a && tools/backtest/run_tag.sh b12b APEX_SEED=777 && tools/backtest/run_tag.sh b12c APEX_SEED=999
$APEX_PY tools/backtest/evaluate.py floor b12a b12b b12c       # writes var/bt/floor_b12a.json
```
Floor per metric = largest absolute pairwise pooled delta over the three seeds. Re-measure after every promotion.
Determinism check before trusting a candidate: run any slate twice under two tags and `cmp` the pickles (byte-identical on 2026-11-24, `2025_w6`). A knob at its "off" value must reproduce the baseline pickle byte for byte.

## 3. Candidate vs baseline
```
tools/backtest/run_tag.sh candA KNOB=V && tools/backtest/run_tag.sh candB KNOB=V APEX_SEED=777
$APEX_PY tools/backtest/evaluate.py compare b12a candA b12b candB --floor b12a
```
Prints per-season deltas for both seeds and a per-metric verdict: BETTER (both seeds beyond 2x floor), WORSE (mean beyond 2x floor), noise. The promotion rules themselves (`noise_aware`, `qb_only`, `dispersion_only`) are in `contracts/weekly/grading.v0.1.yaml`; the verdict line is a helper, the contract decides. The older `engine/weekly/eval_candidate.py BASE CAND` (run from `engine/weekly` with `APEX_OUT=var/bt`) still works and adds the Out-player subset and rush tier tables.

## 4. Other evaluators
```
$APEX_PY tools/backtest/evaluate.py quant TAG     # pinball loss (P10/P25/P75/P90) and coverage: rec_yds, rec, rush_yds, pass_yds
$APEX_PY tools/backtest/evaluate.py team  TAG     # team points bias and RMSE by season x week; game-total bias vs the line
$APEX_PY tools/backtest/evaluate.py tdcal TAG     # anytime-TD calibration by bucket and position
```
Note: receptions are integers, so "inside P25-P75" counts ties and reads high (65%); judge receptions on pinball, not coverage.

## 5. Availability (leave-one-season-out)
`engine/weekly/fit_availability_role.py` is the pattern: fit on the other seasons plus 2026, score the held-out season (Brier, log loss by group). Caution: it also rewrites `config/weekly/availability_by_status_pos_role.csv`, the table now in production (#76). Run it only on the refit day, or on a copy of the repo.

## 6. Look-ahead rules for new features
Only information available before that week's kickoff: stats with `week <= W-1` (`APEX_THROUGH_WEEK`), the injury report of week W (`APEX_INJ_WEEK`), schedule lines as nflverse stores them (closing-ish; never use them in the model-only track). Season-to-date tables from the operator (Sharp) are current-week only and can never enter a backtest; rebuild the equivalent from pbp week by week.
