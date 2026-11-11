#!/bin/bash
# E11 and E8 side by side, under nice 19 (40 threads in all from 2026-11-10 14:20):
#   runs7.sh A   E11 on 16 threads: waits for the 4000 run of runs6.sh (pid 618417) to end, then 5000 (1 h), 3000 (1 h);
#   runs7.sh B   E11 on 16 threads: 5060 (1.5 h), 5061 (1.5 h);
#   runs7.sh E8  E8 on 8 threads, an hour each: B = 31, 37, 41 at 4000 and 5000, then B = 31 and 37 at 5060 (B = 41
#                there only if B = 37 does not show the trend; no 5061).
# A line a run appended to hubs.jsonl (E11) or e8.jsonl (E8), progress every 2 s in logs/{hubs,e8}-N-B.log; a run
# already in its file is skipped.  The streams share no board.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
declare -A KNOWN=([5061]=8057936)
run() {  # file n B threads seconds [extra...]
  local file=$1 n=$2 b=$3 threads=$4 secs=$5
  shift 5
  if grep -q "\"n\":$n,\"B\":$b," "$file" 2>/dev/null; then
    return
  fi
  local known=()
  if [[ -n "${KNOWN[$n]}" ]]; then
    known=(--known "${KNOWN[$n]}")
  fi
  nice -n 19 "$BIN" "$n" --smooth "$b" --threads "$threads" --every 2 --seconds "$secs" "${known[@]}" "$@" \
    2>"logs/$(basename "$file" .jsonl)-$n-$b.log" >>"$file"
  echo "done $file $n B=$b: $(grep "\"n\":$n,\"B\":$b," "$file" | tail -1 | python3 -I -c 'import json,sys; d=json.loads(sys.stdin.read()); print({k: d[k] for k in ["finished", "PB_s", "PB_s_upper", "share_low", "processed", "seconds", "threads"]})')"
}
case "$1" in
  A)
    tail --pid=618417 -f /dev/null
    echo "done hubs.jsonl 4000 B=23: $(grep '"n":4000,"B":23,' hubs.jsonl | tail -1 | cut -c1-400)"
    run hubs.jsonl 5000 23 16 3600 --hubs
    run hubs.jsonl 3000 23 16 3600 --hubs
    ;;
  B)
    run hubs.jsonl 5060 23 16 5400 --hubs
    run hubs.jsonl 5061 23 16 5400 --hubs
    ;;
  E8)
    for n in 4000 5000; do
      for b in 31 37 41; do run e8.jsonl "$n" "$b" 8 3600; done
    done
    for b in 31 37; do run e8.jsonl 5060 "$b" 8 3600; done
    ;;
esac
