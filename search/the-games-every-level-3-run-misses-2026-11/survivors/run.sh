#!/bin/bash
# The survivor test (2026-11-09; the briefing's review, recommendation 3): the games that start a streak of short
# games in rehearsal passes at level 3 whatever the seed, played alone from their proven n - 1 line (--known-to n - 1,
# no best-known file) at levels 4, 5 and 6, three seeds each, no stop on growth, 12 threads.  Does more effort reach
# their optimum?  score.py compares each play with opt(n).
cd "$(dirname "$0")"
TAXMAN=../unsound-run/taxman-aeffc29
for g in 3311 3549 3844 4134 4225 5060; do
    for level in 4 5 6; do
        for seed in 31 32 33; do
            out=g$g-l$level-s$seed
            nice -n 19 $TAXMAN solve $g-$g --unsound --effort $level --stop-growth off --seed $seed \
                --known-to $((g - 1)) --best-known off --threads 12 --out $out.jsonl > $out.log 2>&1
            echo "$out $(date +%T): $(grep -h '^n=' $out.log | cut -c1-40)"
        done
    done
done
nice -n 19 python3 -I score.py
echo "done $(date +%T)"
