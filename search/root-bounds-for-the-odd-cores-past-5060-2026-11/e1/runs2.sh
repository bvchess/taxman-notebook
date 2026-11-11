#!/bin/bash
# E1's second round, after the boards of runs.sh, each on 4 threads under nice 19, a line a run appended to its file;
# a run already there is skipped, so the script resumes after an interruption.
#   timing.jsonl: 5000 to the end, 5060 and 5061 for 300 s, with the timers of the later build;
#   dive.jsonl:   5140, a dive alone (the child of the largest key each step), for a smooth-playable set;
#   sweep.jsonl:  B = 23 at 1500-4750, every 250 (and 2176's neighbors), for the trend, 300 s each at most;
#   bsweep.jsonl: B = 17-47 at 3000 and 5000, 300 s each at most.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
run() {  # file n B seconds [extra...]
  local file=$1 n=$2 b=$3 secs=$4
  shift 4
  if grep -q "\"n\":$n,\"B\":$b," "$file" 2>/dev/null; then
    return
  fi
  nice -n 19 "$BIN" "$n" --smooth "$b" --threads 4 --seconds "$secs" "$@" 2>"logs/$(basename "$file" .jsonl)-$n-$b.log" >>"$file"
  echo "done $file $n B=$b: $(tail -1 "$file" | cut -c1-200)"
}
run timing.jsonl 5000 23 1800
run timing.jsonl 5060 23 300
run timing.jsonl 5061 23 300
run dive.jsonl 5140 23 0 --known 8317376 --dive 400
for n in 1500 1750 2000 2250 2500 2750 3250 3500 3750 4250 4500 4750; do
  run sweep.jsonl "$n" 23 300
done
for n in 3000 5000; do
  for b in 17 19 29 31 37 47; do
    run bsweep.jsonl "$n" "$b" 300
  done
done
