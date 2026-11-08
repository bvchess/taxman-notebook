#!/bin/bash
# Test 1: a second pass over windows around the 33 games every known-range chain missed, from start.jsonl,
# level 3 with no stop and seed 2, without (arm a) and with (arm b) --above 8.  Each arm has its own best-known file.
set -e
WINDOWS="3172-3199 3309-3313 3563-3568 3721-3725 3886-3896 3966-3970 4132-4141 4223-4233"
arm() {  # name, extra options
    mkdir -p $1 && cp start.jsonl $1/best-known.jsonl
    for w in $WINDOWS; do
        nice -n 19 ./taxman-928ad6a solve $w --unsound --effort 3 --stop-growth off --seed 2 --threads 22 --known-to 3000 \
            $2 --out $1/w$w.jsonl > $1/w$w.log 2>&1
    done
    echo "$1 done $(date +%T)"
}
arm a "" &
arm b "--above 8" &
wait
