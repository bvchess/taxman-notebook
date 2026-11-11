#!/usr/bin/env bash
# E9b: root forcing with PB_s (B = 23), as ../e9/run.sh at 5061, for any game: for each candidate of the list, E1's
# program with it picked; it is barred when PB_s with it picked is at most KNOWN, which the run shows by finishing with
# no smooth-playable set above KNOWN.
#
#   ./run.sh N KNOWN LIST PARALLEL THREADS SECONDS
#
# LIST has one candidate a line, "pick X".  Each run writes its JSON line to out/pick-X.json and its progress to
# logs/pick-X.log; results.jsonl gathers the lines at the end.
set -euo pipefail

here=/home/brian/taxman_work/lab/work/oddcore/e9b
bin=$here/e1_smooth-fac59be
n=$1 known=$2 list=$3 parallel=$4 threads=$5 seconds=$6
export here bin n known threads seconds

one() {
    local arm=$1 x=$2
    nice -n 19 "$bin" "$n" --smooth 23 --known "$known" --picks "$x" --threads "$threads" --seconds "$seconds" \
        > "$here/out/$arm-$x.json" 2> "$here/logs/$arm-$x.log"
}
export -f one

mkdir -p "$here/out" "$here/logs"
grep -v '^#' "$list" | xargs -P "$parallel" -L 1 bash -c 'one "$0" "$1"'
cat "$here"/out/*.json > "$here/results.jsonl"
