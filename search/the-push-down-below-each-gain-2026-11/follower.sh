#!/bin/bash
# The push-down of pass 2 (2026-11-08): while pass 2's two lanes run, search the 8 games below each root of their gains,
# and below each root the push-down itself makes, on 8 threads, with the mini-pass's options (pushdown.py says what to
# search).  Each round's windows go to pd/; the follower waits 5 minutes when there is nothing to search, and ends when
# both lanes are done (../p2.done and ../u.done) and nothing is left.
cd /home/brian/taxman_work/lab/work/unsound-run/mini
OPTS="--unsound --effort 3 --stop-growth off --seed 3 --above 8 --threads 8"
BEST_KNOWN=/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl
mkdir -p pd
round=0
while true; do
    windows=$(nice -n 19 python3 -I pushdown.py)
    if [ -n "$windows" ]; then
        round=$((round + 1))
        echo "round $round $(date +%T): $windows"
        for w in $windows; do
            nice -n 19 ../taxman-f7b134c solve $w $OPTS --best-known $BEST_KNOWN --out pd/r$round-w$w.jsonl \
                > pd/r$round-w$w.log 2>&1
        done
    elif [ -e ../p2.done ] && [ -e ../u.done ]; then
        echo "done $(date +%T)"
        break
    else
        sleep 300
    fi
done
