#!/bin/bash
# Run the 27-slate weeks 4-12 x 2023-25 backtest for one tag, 4 slates in parallel.
# usage: tools/backtest/run_tag.sh TAG [KEY=VAL ...]
#   KEY=VAL pairs are candidate knobs exported for this tag only (e.g. APEX_SEED=777 APEX_RUSH_FORM=0).
#   Output: $APEX_OUT/bt_{S}_w{W}_{TAG}.pkl and btteam_*.pkl. APEX_OUT defaults to <repo>/var/bt.
#   Set BT_SEASONS / BT_WEEKS to narrow (default "2023 2024 2025" / "4 5 6 7 8 9 10 11 12"), BT_PAR for parallelism.
#   Existing pickles for the tag are skipped (resumable); BT_FORCE=1 reruns them.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=$1; shift
PY=${APEX_PY:-$(command -v python3)}
export APEX_OUT=${APEX_OUT:-$REPO/var/bt}
mkdir -p "$APEX_OUT/logs"
# clear every candidate knob that could leak in from the caller's shell, then apply this tag's knobs
for v in $(env | grep -o '^APEX_[A-Z0-9_]*' | grep -v -E '^APEX_(OUT|NFLV|PY|RUNS|DELIV)$'); do unset "$v"; done
for kv in "$@"; do export "$kv"; done
export TAG PY REPO
SEASONS=${BT_SEASONS:-"2023 2024 2025"}; WEEKS=${BT_WEEKS:-"4 5 6 7 8 9 10 11 12"}
run_one(){ S=$1; W=$2; f="$APEX_OUT/bt_${S}_w${W}_${TAG}.pkl"
  if [ -s "$f" ] && [ "${BT_FORCE:-0}" != 1 ]; then return 0; fi
  cd "$REPO/engine/weekly" && APEX_SEASON=$S APEX_THROUGH_WEEK=$((W-1)) APEX_BACKTEST=1 APEX_TARGET_WEEK=$W APEX_INJ_WEEK=$W \
    APEX_ROSTER=v4 APEX_ENV=model APEX_NS=${APEX_NS:-5000} "$PY" backtest_run.py "${S}_w${W}_${TAG}" > "$APEX_OUT/logs/${S}_w${W}_${TAG}.log" 2>&1 \
    || { echo "FAIL $S w$W $TAG (see $APEX_OUT/logs/${S}_w${W}_${TAG}.log)"; return 1; }; }
export -f run_one
t0=$(date +%s)
for S in $SEASONS; do for W in $WEEKS; do echo "$S $W"; done; done | xargs -P "${BT_PAR:-4}" -L1 bash -c 'run_one $0 $1'
n=$(ls "$APEX_OUT"/bt_*_"${TAG}".pkl 2>/dev/null | wc -l)
echo "tag=$TAG slates=$n knobs=[$*] secs=$(( $(date +%s)-t0 ))" | tee -a "$APEX_OUT/logs/tags.log"
