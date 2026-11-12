#!/bin/bash
# The samples of the tree of the smooth part (Knuth's estimator), on 16 threads at idle priority.  Each argument is
# N:B:SAMPLES:SEED[:LEAFNODES] (LEAFNODES: solve each leaf reached, its search stopped at that many steps; none if
# absent).  No sample is begun after LIMIT seconds (default 1800).  Each run writes tree-N-B-sSEED.jsonl; one already
# there is skipped.
set -u
cd "$(dirname "$0")"
R=./restricted
LIMIT=${LIMIT:-1800}
for spec in "$@"; do
    IFS=: read -r n b samples seed leafnodes <<< "$spec"
    out="tree-$n-$b-s$seed.jsonl"
    [ -s "$out" ] && continue
    args=(smooth-tree "$n" --smooth "$b" --samples "$samples" --seed "$seed" --threads 16 --time-limit "$LIMIT")
    args+=(--tactic symmetry=off)
    [ -n "${leafnodes:-}" ] && args+=(--solve-leaves --node-limit "$leafnodes")
    chrt -i 0 nice -n 19 $R "${args[@]}" > "$out.part" 2> "tree-$n-$b-s$seed.err" && mv "$out.part" "$out" \
        || echo "failed: $spec" >> tree.failed
done
echo "done: $*" >> tree.done
