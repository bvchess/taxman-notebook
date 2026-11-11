#!/bin/bash
# E1's boards, one after another, each on 4 threads under nice 19 and stopped after 1800 s.  Appends one JSON line a
# run to results.jsonl and writes its progress to logs/N-B.log; a run already in results.jsonl is skipped, so the
# script resumes after an interruption.  The scores past 5060 are the best known, from gapdash/games.csv.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
declare -A KNOWN=([5061]=8057936 [5096]=8170466 [5140]=8317376)
for B in 23 13; do
  for n in 3000 4000 5000 5060 5061 5096 5140; do
    if grep -q "\"n\":$n,\"B\":$B," results.jsonl 2>/dev/null; then
      continue
    fi
    extra=()
    if [[ -n "${KNOWN[$n]}" ]]; then
      extra=(--known "${KNOWN[$n]}")
    fi
    nice -n 19 "$BIN" "$n" --smooth "$B" --threads 4 --seconds 1800 "${extra[@]}" 2>"logs/$n-$B.log" >>results.jsonl
    echo "done $n B=$B: $(tail -1 results.jsonl | cut -c1-260)"
  done
done
