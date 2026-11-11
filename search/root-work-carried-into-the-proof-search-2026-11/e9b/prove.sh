#!/usr/bin/env bash
# E9b: prove game N standalone with the flags of ../../proofs/run.sh's arm "standalone" (no seed, no ceiling, no
# near-repeat cut, --force-search, 16 threads, --window 1, the default gate and finder), at idle priority, with a
# directory of stores: here the bars of carried/bars-N.txt, read as nogoods of one member.
#
#   ./prove.sh TAG N STORE_DIR [LIMIT_SECONDS]
set -euo pipefail

here=/home/brian/taxman_work/lab/work/oddcore/e9b
bin=$here/taxman-c235b4a
tag=$1 n=$2 store=$3 limit=${4:-14400}
mkdir -p "$here/proof" "$here/logs" "$here/ckpt"

stamp() { TZ=America/Los_Angeles date '+%F %H:%M %Z'; }

echo "$(stamp) start $tag (game $n, store $store, limit ${limit}s)" >> "$here/jobs.log"
status=0
nice -n 19 chrt -i 0 "$bin" solve "$n" --out "$here/proof/$tag.jsonl" --checkpoint-dir "$here/ckpt/$tag" \
    --time-limit "$limit" --threads 16 --window 1 --progress 60 --force-search --tactic prev_cap=off \
    --tactic near_repeat=off --carried-dir "$store" >> "$here/logs/$tag.log" 2>&1 < /dev/null || status=$?
echo "$(stamp) end $tag (exit $status): $(grep -E "^n=[0-9]+ +score=" "$here/logs/$tag.log" | tail -n 1 | cut -c1-200)" \
    >> "$here/jobs.log"
