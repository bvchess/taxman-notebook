#!/bin/bash
# E11 (PB_sh, --hubs, B = 23) on 16 threads under nice 19, progress every 2 s: 4000 and 5000 for an hour each, 5060
# and 5061 for 1.5 hours, then 3000 again for an hour (runs4.sh's run of it on 4 threads was stopped at 1,863 s).
# A line a run appended to hubs.jsonl, progress in logs/hubs-N-23.log; a run already there is skipped.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
declare -A KNOWN=([5061]=8057936)
run() {  # n seconds
  local n=$1 secs=$2
  if grep -q "\"n\":$n,\"B\":23," hubs.jsonl 2>/dev/null; then
    return
  fi
  local known=()
  if [[ -n "${KNOWN[$n]}" ]]; then
    known=(--known "${KNOWN[$n]}")
  fi
  nice -n 19 "$BIN" "$n" --smooth 23 --hubs --threads 16 --every 2 --seconds "$secs" "${known[@]}" \
    2>"logs/hubs-$n-23.log" >>hubs.jsonl
  echo "done $n: $(tail -1 hubs.jsonl | python3 -I -c 'import json,sys; d=json.loads(sys.stdin.read()); print({k: d[k] for k in ["n", "finished", "PB_s", "PB_s_upper", "share_low", "processed", "seconds"]})')"
}
run 4000 3600
run 5000 3600
run 5060 5400
run 5061 5400
run 3000 3600
