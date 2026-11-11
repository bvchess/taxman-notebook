#!/usr/bin/env bash
# E9 (study-report-1.md, Sections 8.4 and 9): root forcing with PB_s at 5061.  For each candidate of the list, E1's
# program with it picked (outside the heaviest set) or barred (a member): it is fixed the other way when PB_s with that
# fixing is at most the best-known score, which the run shows by finishing with no smooth-playable set above it.
#
#   ./run.sh LIST PARALLEL THREADS SECONDS
#
# LIST has one candidate a line, "pick X" or "bar X".  Each run writes its JSON line to out/ARM-X.json and its progress
# to logs/ARM-X.log; results.jsonl gathers the lines at the end.
set -euo pipefail

here=/home/brian/taxman_work/lab/work/oddcore/e9
bin=$here/e1_smooth-e9
list=$1 parallel=$2 threads=$3 seconds=$4
export here bin threads seconds

one() {
    local arm=$1 x=$2
    local flag=--picks
    [[ $arm == bar ]] && flag=--bars
    nice -n 19 "$bin" 5061 --smooth 23 --known 8057936 "$flag" "$x" --threads "$threads" --seconds "$seconds" \
        > "$here/out/$arm-$x.json" 2> "$here/logs/$arm-$x.log"
}
export -f one

mkdir -p "$here/out" "$here/logs"
grep -v '^#' "$list" | xargs -P "$parallel" -L 1 bash -c 'one "$0" "$1"'
cat "$here"/out/*.json > "$here/results.jsonl"
