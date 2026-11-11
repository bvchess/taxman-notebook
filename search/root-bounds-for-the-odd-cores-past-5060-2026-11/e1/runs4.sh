#!/bin/bash
# E11 (PB_sh, --hubs, B = 23) and E8 (PB_s with B = 31, 37, 41), the cheap boards first, each on 4 threads under
# nice 19 and stopped after 3600 s; a line a run appended to hubs.jsonl (E11) or e8.jsonl (E8), progress in
# logs/{hubs,e8}-N-B.log.  A run already in its file is skipped, so the script resumes after an interruption.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
declare -A KNOWN=([5061]=8057936 [5096]=8170466 [5140]=8317376)
run() {  # file n B [extra...]
  local file=$1 n=$2 b=$3
  shift 3
  if grep -q "\"n\":$n,\"B\":$b," "$file" 2>/dev/null; then
    return
  fi
  local known=()
  if [[ -n "${KNOWN[$n]}" ]]; then
    known=(--known "${KNOWN[$n]}")
  fi
  nice -n 19 "$BIN" "$n" --smooth "$b" --threads 4 --seconds 3600 "${known[@]}" "$@" \
    2>"logs/$(basename "$file" .jsonl)-$n-$b.log" >>"$file"
  echo "done $file $n B=$b: $(tail -1 "$file" | cut -c1-200)"
}
for n in 2176 3000 4000 5000; do
  run hubs.jsonl "$n" 23 --hubs
done
for n in 4000 5000; do
  for b in 31 37 41; do
    run e8.jsonl "$n" "$b"
  done
done
for n in 5060 5061; do
  run hubs.jsonl "$n" 23 --hubs
done
for n in 5060 5061; do
  for b in 31 37 41; do
    run e8.jsonl "$n" "$b"
  done
done
