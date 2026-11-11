#!/usr/bin/env bash
# E2: prove game N standalone with the flags of ../../proofs/run.sh's arm "standalone" (no seed, no ceiling, no
# near-repeat cut, --force-search, 16 threads, --window 1, the default gate and finder), at idle priority, with a store
# of nogoods.
#
#   ./prove.sh TAG N STORE_DIR|none [LIMIT_SECONDS]
#
# STORE_DIR holds nogoods-M.txt for some M <= N (the search reads it, checks every set at its root and keeps the
# conflicts; it also writes its own harvest there as nogoods-N.txt).  "none": no store, as the baseline.
set -euo pipefail

here=/home/brian/taxman_work/lab/work/oddcore/e2
bin=$here/taxman-fac59be  # cores23-4848 ran taxman-5953b6e, the same search with READ_CAP 200,000
tag=$1 n=$2 store=$3 limit=${4:-14400}
carried=()
[[ $store == none ]] || carried=(--carried-dir "$store")
mkdir -p "$here/out" "$here/logs" "$here/ckpt"

stamp() { TZ=America/Los_Angeles date '+%F %H:%M %Z'; }

echo "$(stamp) start $tag (game $n, store $store, limit ${limit}s)" >> "$here/jobs.log"
status=0
nice -n 19 chrt -i 0 "$bin" solve "$n" --out "$here/out/$tag.jsonl" --checkpoint-dir "$here/ckpt/$tag" \
    --time-limit "$limit" --threads 16 --window 1 --progress 60 --force-search --tactic prev_cap=off \
    --tactic near_repeat=off "${carried[@]}" >> "$here/logs/$tag.log" 2>&1 < /dev/null || status=$?
echo "$(stamp) end $tag (exit $status): $(grep -E "^n=[0-9]+ +score=" "$here/logs/$tag.log" | tail -n 1 | cut -c1-200)" \
    >> "$here/jobs.log"
