#!/bin/bash
# The walks of the tree of the smooth part (`smooth-tree --exact`) on 16 threads at idle priority, each line appended
# to walk.jsonl.  Each argument is N:B:ABOVE:LIMIT[:`FRONTIER`:SAMPLE] (ABOVE "-" for opt(N); the walk stops at LIMIT
# seconds; with `FRONTIER` and SAMPLE, a random sample of SAMPLE nodes of a depth cut of at least `FRONTIER`).  The
# per-subtree lines go to walk-N-B-ABOVE.err.
set -u
cd "$(dirname "$0")"
R=./restricted
for spec in "$@"; do
    IFS=: read -r n b above limit frontier sample <<< "$spec"
    args=(smooth-tree "$n" --smooth "$b" --exact --threads 16 --time-limit "$limit" --tactic symmetry=off)
    [ "$above" != "-" ] && args+=(--above "$above")
    [ -n "${frontier:-}" ] && args+=(--frontier "$frontier" --walk-sample "$sample" --seed 1)
    chrt -i 0 nice -n 19 $R "${args[@]}" >> walk.jsonl 2> "walk-$n-$b-$above.err" \
        || echo "failed: $spec" >> walk.failed
done
echo "done: $*" >> walk.done
