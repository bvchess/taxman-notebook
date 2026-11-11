#!/bin/bash
# E12's check against E11 (e1/hubval2.jsonl, e1/hubs.jsonl): PB_sh at the boards where E11 finished, in three modes:
# E11's literal branching (the refactored program), hub ownership with the decisions on the smooth and hub tests only
# (--no-project: must give PB_sh exactly), and hub ownership with the decisions on the frames too (E12).  16 threads,
# nice 19.  Lines go to check.jsonl, each with its mode in the fields own and project.
cd /home/brian/taxman_work/lab/work/oddcore/e12 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e12/release/examples/e1_smooth
mkdir -p logs
for n in "$@"; do
  for mode in "" "--own --no-project" "--own"; do
    tag=$(echo "e11 $mode" | tr -d ' -')
    nice -n 19 "$BIN" "$n" --smooth 23 --hubs $mode --threads 16 --every 5 --seconds 3600 \
      2>"logs/check-$n-$tag.log" >>check.jsonl
  done
done
