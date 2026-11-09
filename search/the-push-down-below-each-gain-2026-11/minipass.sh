#!/bin/bash
# The mini-pass below pass 2's breakthroughs (2026-11-08): level 3 with no stop, a new seed (3) and --above 8, over the
# 8 games below each of pass 2's breakthroughs (arm t) and over as many games in random windows (arm c, the control),
# from and into the production best-known file.  windows.py chooses the windows; 20 threads an arm, the arms at once.
set -e
cd /home/brian/taxman_work/lab/work/unsound-run/mini
OPTS="--unsound --effort 3 --stop-growth off --seed 3 --above 8 --threads 20"
BEST_KNOWN=/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl
arm() {  # name, windows
    mkdir -p $1
    for w in $2; do
        nice -n 19 ../taxman-f7b134c solve $w $OPTS --best-known $BEST_KNOWN --out $1/w$w.jsonl > $1/w$w.log 2>&1
    done
    echo "$1 done $(date +%T)"
}
nice -n 19 python3 -I windows.py > windows.txt
echo "windows chosen $(date +%T)"
arm t "$(sed -n 's/^t //p' windows.txt)" &
arm c "$(sed -n 's/^c //p' windows.txt)" &
wait
