#!/bin/bash
# E1's third round, after runs2.sh, on 4 threads under nice 19 (the dives on one), a line a run appended to its file;
# a run already there is skipped.
#   timing.jsonl: 5061 for 300 s with the timers (runs2.sh ran it without its best-known score);
#   dive.jsonl:   depth-first dives of 3,000 nodes for smooth-playable sets, at 5140, where the best-first search
#                 stopped, and at 5061 and 5096, where it finished, to see how close a dive comes.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
declare -A KNOWN=([5061]=8057936 [5096]=8170466 [5140]=8317376)
run() {  # file n B seconds threads [extra...]
  local file=$1 n=$2 b=$3 secs=$4 threads=$5
  shift 5
  if grep -q "\"n\":$n,\"B\":$b," "$file" 2>/dev/null; then
    return
  fi
  nice -n 19 "$BIN" "$n" --smooth "$b" --threads "$threads" --seconds "$secs" --known "${KNOWN[$n]}" "$@" \
    2>"logs/$(basename "$file" .jsonl)-$n-$b.log" >>"$file"
  echo "done $file $n B=$b: $(tail -1 "$file" | cut -c1-200)"
}
run timing.jsonl 5061 23 300 4
: > dive.jsonl  # the first dive.jsonl came from a dive that did not backtrack
for n in 5140 5061 5096; do
  run dive.jsonl "$n" 23 0 1 --dive 3000
done
