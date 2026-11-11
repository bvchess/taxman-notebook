#!/bin/bash
# E12's variants against E11 on boards where all finish: usage variants.sh "BOARDS" "TAG=ARGS" ...  Each line goes to
# variants.jsonl with its tag in the field "variant" (and its board, mode and value as e1_smooth prints them).  16
# threads, nice 19, PB_sh with B = 23.
cd /home/brian/taxman_work/lab/work/oddcore/e12 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e12/release/examples/e1_smooth
mkdir -p logs
boards=$1
shift
for n in $boards; do
  for spec in "$@"; do
    tag=${spec%%=*}
    extra=${spec#*=}
    out=$(nice -n 19 "$BIN" "$n" --smooth 23 --hubs $extra --threads 16 --every 5 --seconds ${SECONDS_CAP:-3600} \
      2>"logs/variant-$n-$tag.log")
    echo "{\"variant\":\"$tag\",${out:1}" >>variants.jsonl
  done
done
