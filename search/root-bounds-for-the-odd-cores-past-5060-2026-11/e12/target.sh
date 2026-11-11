#!/bin/bash
# E12b: PB_sh (B = 23) searched depth first to a target T, with no queue: usage target.sh N T TAG SECONDS [ARGS...].
# The search stops at the first set of the family above T (the target fails); if it ends within SECONDS without one
# (target_holds true), no set of the family weighs more than T, so opt(N) <= T.  16 threads, nice 19.  The line goes to
# targets.jsonl with the tag in the field "variant", progress to logs/target-N-T-TAG.log.
cd /home/brian/taxman_work/lab/work/oddcore/e12 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e12/release/examples/e1_smooth
mkdir -p logs
n=$1
t=$2
tag=$3
seconds=$4
shift 4
out=$(nice -n 19 "$BIN" "$n" --smooth 23 --hubs --dfs --target --known "$t" --threads 16 --every 20 \
  --seconds "$seconds" "$@" 2>"logs/target-$n-$t-$tag.log")
echo "{\"variant\":\"$tag\",${out:1}" >>targets.jsonl
echo "$n T=$t $tag: $(echo "{${out:1}" | python3 -I -c 'import json,sys; d=json.loads(sys.stdin.read()); print({k: d[k] for k in ["target_holds", "exhausted", "PB_s_lower", "processed", "seconds", "hub_budget_hits", "hub_fibers_skipped"]})')"
