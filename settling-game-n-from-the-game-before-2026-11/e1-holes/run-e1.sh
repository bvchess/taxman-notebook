#!/bin/bash
# E1, the hole law: for each exchange step n of the list, solve the board n - 1 without its shadow x, as an exact
# standalone search on 16 threads at idle priority, each solve stopped at 30 minutes, and the script with it.  One JSON line per game in
# e1.jsonl; a game already there is skipped, so the script resumes after an interruption.
set -u
cd "$(dirname "$0")"
R=./restricted
for pair in 741:374 1083:578 1209:638 1599:814 1677:902 1729:935 1767:986 1833:946 2067:1034 2139:1102 2301:1166; do
    n=${pair%%:*}
    x=${pair##*:}
    m=$((n - 1))
    if grep -q "^{\"n\":$m," e1.jsonl 2>/dev/null; then
        continue
    fi
    $R solve "$m" --holes "$x" --threads 16 --background --time-limit 1800 \
        --tactic prev_cap=off --tactic near_repeat=off >> e1.jsonl 2>> "e1-$m.err" || { echo "game $m failed" >> e1.failed; exit 1; }
    if tail -n 1 e1.jsonl | grep -q '"completed":false'; then
        echo "game $m passed 30 minutes" >> e1.failed
        exit 1
    fi
done
echo "all done" >> e1.done
