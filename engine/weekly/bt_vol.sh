#!/bin/bash
# usage: bt_vol.sh <tag> <volfile>   (27 slates: 2023-25 weeks 4-12, model environment; outputs bt_<season>_w<week>_<tag>.pkl in APEX_OUT)
cd "$(dirname "$0")"; TAG=$1; export APEX_VOLFILE=$2
run(){ S=$1; W=$2; APEX_SEASON=$S APEX_THROUGH_WEEK=$((W-1)) APEX_BACKTEST=1 APEX_TARGET_WEEK=$W APEX_INJ_WEEK=$W APEX_ROSTER=v4 APEX_ENV=model APEX_NS=${APEX_NS:-5000} python3 backtest_run.py ${S}_w${W}_${TAG} >/dev/null 2>&1; }
export -f run; export TAG
for S in 2023 2024 2025; do for W in 4 5 6 7 8 9 10 11 12; do echo "$S $W"; done; done | xargs -P ${PAR:-6} -L1 bash -c 'run $0 $1'
ls "${APEX_OUT:-../../var/out}"/bt_20*_w*_${TAG}.pkl | wc -l
