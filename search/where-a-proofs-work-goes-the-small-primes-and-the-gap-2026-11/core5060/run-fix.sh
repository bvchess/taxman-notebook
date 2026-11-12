#!/bin/bash
# The fixed runs: game n with its B-smooth candidates (the smooth part) fixed or barred as a reference set has them
# and every other candidate free, an exact search on 16 threads at idle priority that proves no game of the
# arrangement scores more than the score to beat, or finds one.  Each argument is N:B[:FROM[:FLIPS[:ABOVE]]] (FLIPS
# comma-separated, or "-" for none; ABOVE "-" for the default, opt(N) - 1).  One JSON line per run in $OUT (default
# fix.jsonl); a run already there is skipped.  NODES (default 30000000) limits each search's steps and LIMIT
# (default 1800) its seconds.
set -u
cd "$(dirname "$0")"
R=./restricted
OUT=${OUT:-fix.jsonl}
NODES=${NODES:-30000000}
LIMIT=${LIMIT:-1800}
for spec in "$@"; do
    IFS=: read -r n b from flips above <<< "$spec"
    from=${from:-$n}
    flips=${flips:--}
    above=${above:--}
    args=(fix-smooth "$n" --smooth "$b" --from "$from" --threads 16 --background --node-limit "$NODES")
    args+=(--time-limit "$LIMIT" --tactic symmetry=off)
    [ "$flips" != "-" ] && args+=(--flip "$flips")
    [ "$above" != "-" ] && args+=(--above "$above")
    key="{\"n\":$n,\"smooth\":$b,\"from\":$from,\"flips\":[${flips/-/}],"
    if [ "$above" = "-" ]; then
        grep -qF "$key" "$OUT" 2>/dev/null && continue
    else
        grep -F "$key" "$OUT" 2>/dev/null | grep -qF "\"above\":$above," && continue
    fi
    chrt -i 0 nice -n 19 $R "${args[@]}" >> "$OUT" 2>> "fix-$n.err" || echo "failed: $spec" >> fix.failed
done
echo "done: $*" >> fix.done
