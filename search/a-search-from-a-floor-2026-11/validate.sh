#!/bin/bash
# ./validate.sh: the checks before a real run, one after another (./run.sh each): for games 300, 700, 1200, 1600 and
# 2000, the floor at opt(n), which must hold, and at opt(n) - 1, which a game of opt(n) must beat; then 4848 at
# opt - 300 (a limit of 1,200 s) and at opt (a limit of 2,400 s, about 3 times its standalone proof).  opt.txt holds
# opt(n) of each game, from results/optimal.jsonl.gz.
set -u
here=/home/brian/taxman_work/lab/work/floor
opt() { awk -v n="$1" '$1 == n { print $2 }' "$here/opt.txt"; }
for n in 300 700 1200 1600 2000; do
    o=$(opt $n)
    "$here/run.sh" "v$n-at" "$n" "$o" --progress 0
    "$here/run.sh" "v$n-below" "$n" $((o - 1)) --progress 0
done
o=$(opt 4848)
"$here/run.sh" v4848-below300 4848 $((o - 300)) --progress 30 --time-limit 1200
"$here/run.sh" v4848-at 4848 "$o" --progress 60 --time-limit 2400
