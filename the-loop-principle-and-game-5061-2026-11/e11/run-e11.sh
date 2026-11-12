#!/bin/bash
# E11, the region solve: game n with the candidates of the columns of the primes given free and every other candidate
# fixed or barred as the committed optimal set of n - 1 has it, an exact standalone search on 16 threads at idle
# priority, stopped at 30 minutes, and the script with it.  Each argument is N:Q,Q,... (a game and its region's
# primes).  One JSON line per game and region in e11.jsonl, with the moves; one already there is skipped.
set -u
cd "$(dirname "$0")"
R=./restricted
for spec in "$@"; do
    n=${spec%%:*}
    primes=${spec#*:}
    if grep -q "^{\"n\":$n,.*\"columns\":\[$primes\]," e11.jsonl 2>/dev/null; then
        continue
    fi
    $R window "$n" --primes "$primes" --threads 16 --background --time-limit 1800 --tactic symmetry=off --show \
        >> e11.jsonl 2>> "e11-$n.err" || { echo "game $n region $primes failed" >> e11.failed; exit 1; }
    if tail -n 1 e11.jsonl | grep -q '"completed":false'; then
        echo "game $n region $primes passed 30 minutes" >> e11.failed
        exit 1
    fi
done
echo "done: $*" >> e11.done
