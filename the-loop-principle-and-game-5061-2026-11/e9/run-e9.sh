#!/bin/bash
# E9, the parity hole law (T): for each exchange step n given and each mode of MODES (default "ghost plain"), the
# ghost search on board n - 1 on one thread at idle priority (chrt --idle), stopped at 30 minutes; 15 runs at a time.
# The search is the prover's (examples/ghost.rs); v1/ holds the runs of a first, slower search of its own, stopped and
# superseded.
# One JSON line per run in e9-N-MODE.json (a run with its file is skipped, so the script resumes); then e9.jsonl
# gathers them.
set -u
cd "$(dirname "$0")"
MODES=${MODES:-"ghost plain"}
for n in "$@"; do
    for mode in $MODES; do
        [ -s "e9-$n-$mode.json" ] || echo "$n $mode"
    done
done | xargs -P 15 -n 2 sh -c 'chrt --idle 0 ./ghost "$0" --mode "$1" --time-limit 1800 > "e9-$0-$1.json.part" 2> "e9-$0-$1.err" && mv "e9-$0-$1.json.part" "e9-$0-$1.json"'
cat e9-*.json > e9.jsonl
