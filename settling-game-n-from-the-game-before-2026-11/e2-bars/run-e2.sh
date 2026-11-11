#!/bin/bash
# E2, the 12P law, run (b): for each game n = 12P, P prime, with P1 the prime before P, solve game n as an exact
# standalone search with 6P fixed in (promoted at the root) and 4P barred, on 16 threads at idle priority, and report
# whether 8P, 8P1 and 12P1 are in U*(n).  One JSON line per game in e2.jsonl; a game already there is skipped.
set -u
cd "$(dirname "$0")"
R=../e1-holes/restricted
for spec in 1668:139:137 2004:167:163 2316:193:191 2748:229:227; do
    IFS=: read -r n p p1 <<< "$spec"
    if grep -q "^{\"n\":$n," e2.jsonl 2>/dev/null; then
        continue
    fi
    $R solve "$n" --fix $((6 * p)) --bar $((4 * p)) --in-ustar $((8 * p)),$((8 * p1)),$((12 * p1)) --threads 16 \
        --background --time-limit 1800 --tactic symmetry=off --tactic prev_cap=off --tactic near_repeat=off \
        >> e2.jsonl 2>> "e2-$n.err" || { echo "game $n failed" >> e2.failed; exit 1; }
done
