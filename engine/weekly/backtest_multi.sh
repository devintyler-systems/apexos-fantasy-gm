#!/bin/bash
cd "$(dirname "$0")"
run(){ S=$1; W=$2; APEX_SEASON=$S APEX_THROUGH_WEEK=$((W-1)) APEX_BACKTEST=1 APEX_TARGET_WEEK=$W APEX_INJ_WEEK=$W APEX_ROSTER=v4 APEX_ENV=model APEX_NS=5000 python3 backtest_run.py ${S}_w${W}_v4 >/dev/null 2>&1; }
export -f run
for S in 2023 2024 2025; do for W in 4 5 6 7 8 9 10 11 12; do echo "$S $W"; done; done | xargs -P 6 -L1 bash -c 'run $0 $1'
ls "${APEX_OUT:-../../var/out}"/bt_20*_w*_v4.pkl | wc -l
