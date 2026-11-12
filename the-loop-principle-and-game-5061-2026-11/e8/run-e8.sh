#!/bin/bash
# E8, locality: for each game n given and each depth d of DEPTHS (default "3"), game n with the candidates of columns
# 0 to d free and every other candidate fixed or barred as the committed optimal set of n - 1 has it, an exact
# standalone search on 4 threads at idle priority, stopped at 30 minutes, and the script with it.  One JSON line per
# game and depth in e8.jsonl; one already there is skipped, so the script resumes after an interruption.
set -u
cd "$(dirname "$0")"
R=./restricted
DEPTHS=${DEPTHS:-3}
for n in "$@"; do
    for d in $DEPTHS; do
        if grep -q "^{\"n\":$n,.*\"depth\":$d," e8.jsonl 2>/dev/null; then
            continue
        fi
        $R window "$n" --depth "$d" --threads 4 --background --time-limit 1800 --tactic symmetry=off \
            >> e8.jsonl 2>> "e8-$n.err" || { echo "game $n depth $d failed" >> e8.failed; exit 1; }
        if tail -n 1 e8.jsonl | grep -q '"completed":false'; then
            echo "game $n depth $d passed 30 minutes" >> e8.failed
            exit 1
        fi
    done
done
echo "done: $* (depths $DEPTHS)" >> e8.done
