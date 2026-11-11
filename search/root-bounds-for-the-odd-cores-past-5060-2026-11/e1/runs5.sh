#!/bin/bash
# E11 (PB_sh, --hubs, B = 23) and E8 (PB_s with B = 31, 37, 41) after runs4.sh was stopped (its 3000 run of E11 at
# 1,863 s: logs/hubs-3000-23.log).  Each run on 4 threads under nice 19, a line a run appended to hubs.jsonl (E11) or
# e8.jsonl (E8), progress in logs/{hubs,e8}-N-B.log; a run already in its file is skipped.  The time limits follow the tests:
# 30 minutes at 4000 and for E11 at 5000 (E11's test there is 2 × E1's 67 s); an hour for E8 at 5000-5061 (its rule)
# and for E11 at 5060-5061 (2 × E1's 1,294 and 1,514 s).  5061 last: its smooth sub-board is 5060's.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
declare -A KNOWN=([5061]=8057936 [5096]=8170466 [5140]=8317376)
run() {  # file n B seconds [extra...]
  local file=$1 n=$2 b=$3 secs=$4
  shift 4
  if grep -q "\"n\":$n,\"B\":$b," "$file" 2>/dev/null; then
    return
  fi
  local known=()
  if [[ -n "${KNOWN[$n]}" ]]; then
    known=(--known "${KNOWN[$n]}")
  fi
  nice -n 19 "$BIN" "$n" --smooth "$b" --threads 4 --seconds "$secs" "${known[@]}" "$@" \
    2>"logs/$(basename "$file" .jsonl)-$n-$b.log" >>"$file"
  echo "done $file $n B=$b: $(tail -1 "$file" | cut -c1-200)"
}
run hubs.jsonl 4000 23 1800 --hubs
run hubs.jsonl 5000 23 1800 --hubs
for b in 31 37 41; do run e8.jsonl 4000 "$b" 1800; done
for b in 31 37 41; do run e8.jsonl 5000 "$b" 3600; done
run hubs.jsonl 5060 23 3600 --hubs
run hubs.jsonl 5061 23 3600 --hubs
for b in 31 37 41; do run e8.jsonl 5060 "$b" 3600; done
for b in 31 37 41; do run e8.jsonl 5061 "$b" 3600; done
