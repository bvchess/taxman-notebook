#!/bin/bash
# E6, the exchange law's obligation: for each exchange step n given, an exact standalone search of game n - 1 from its
# committed optimal promotion set, with the search's trace on, on 16 threads at idle priority, stopped at 30 minutes,
# and the script with it.  TAG (default "default") names the variant, and EXTRA holds its flags (such as
# "--tactic symmetry=off").  One JSON line per game in e6-TAG.jsonl, the samples in e6-TAG-samples-N.jsonl, the progress
# lines in e6-TAG-N.err; a game already in e6-TAG.jsonl is skipped, so the script resumes after an interruption.
set -u
cd "$(dirname "$0")"
TAG=${TAG:-default}
EXTRA=${EXTRA:-}
O=./obligation
for n in "$@"; do
    if grep -q "^{\"n\":$n," "e6-$TAG.jsonl" 2>/dev/null; then
        continue
    fi
    # shellcheck disable=SC2086
    $O "$n" --threads 16 --background --time-limit 1800 --samples "e6-$TAG-samples-$n.jsonl" $EXTRA \
        >> "e6-$TAG.jsonl" 2>> "e6-$TAG-$n.err" || { echo "game $n failed" >> "e6-$TAG.failed"; exit 1; }
    if tail -n 1 "e6-$TAG.jsonl" | grep -q '"completed":false'; then
        echo "game $n passed 30 minutes" >> "e6-$TAG.failed"
        exit 1
    fi
done
echo "done: $*" >> "e6-$TAG.done"
