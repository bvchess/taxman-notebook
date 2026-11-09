#!/bin/bash
# The rehearsal (2026-11-08; the plan doc's "The rehearsal"): the procedure past 5060, run on 3001-5060 from the proven
# 3000 (--known-to 3000) into a best-known file of its own (best-known.jsonl here), one pass at a time on 44 threads,
# scored against opt(n) after each (score.py, into score.txt).  Pass 1: level 3, seed 1, the default stop; passes 2,
# 3, ...: level 3, no stop, seed k, each descending below its own gains, until a pass raises no new streak (8 at most).
# A pass cut short resumes from pK.jsonl when this is run again; its hours then count from the restart.
cd /home/brian/taxman_work/lab/work/rehearsal
TAXMAN=../unsound-run/taxman-bd6381b
THREADS=44
for k in 1 2 3 4 5 6 7 8; do
    opts="--unsound --effort 3 --known-to 3000 --threads $THREADS --seed $k"
    [ $k -gt 1 ] && opts="$opts --stop-growth off"
    echo "pass $k began $(date +%T): solve 3001-5060 $opts --out p$k.jsonl"
    began=$(date +%s)
    nice -n 19 $TAXMAN solve 3001-5060 $opts --out p$k.jsonl > p$k.log 2>&1
    status=$?
    if [ $status -ne 0 ]; then
        echo "pass $k failed $(date +%T): exit $status"
        exit 1
    fi
    nice -n 19 python3 -I score.py $k $(( $(date +%s) - began )) $THREADS >> score.txt
    tail -n 6 score.txt
    if [ $k -gt 1 ] && [ "$(tail -n 1 score.txt)" = "new streaks: 0" ]; then
        break
    fi
done
echo "done $(date +%T)"
