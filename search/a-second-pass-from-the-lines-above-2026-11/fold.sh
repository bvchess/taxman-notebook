#!/bin/bash
# Folds every known-range chain of B14 and B17 into start.jsonl, a best-known file of 3001-5060 with the table cut at 3000.
set -e
NB=/home/brian/taxman_work/research/solver/notebook/search
B14=$NB/tuning-the-unsound-mode-on-a-long-chain-2026-11
B17=$NB/the-stop-that-waits-for-quiet-rounds-2026-11/runs
fold() {  # name, source.gz, lo, hi
    gunzip -c "$2" > fold/$1.jsonl
    nice -n 19 ./taxman-928ad6a solve $3-$4 --unsound --effort 3 --threads 4 --known-to 3000 --out fold/$1.jsonl \
        --best-known start.jsonl > fold/$1.log 2>&1
    echo "$1: $(tail -1 fold/$1.log)"
}
for a in l3 l4 l2-push25 l2-control l2-stopoff l2-push100 l2 l2-stop50 l2-unseeded1 l1; do fold b14-$a $B14/part1/$a.jsonl.gz 4001 5060; done
fold b17-q3 $B17/q3.jsonl.gz 4001 5060
fold b17-q2 $B17/q2.jsonl.gz 4001 5060
for a in h-choice-l3 h-control-l2 h-choice-l2 h-default-l2; do fold b14-$a $B14/part2/$a.jsonl.gz 3001 4000; done
fold b17-off3-h $B17/off3-h.jsonl.gz 3001 4000
fold b17-q3-h $B17/q3-h.jsonl.gz 3001 4000
fold b17-q2-h $B17/q2-h.jsonl.gz 3001 4000
wc -l start.jsonl
