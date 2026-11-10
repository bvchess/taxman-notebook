#!/bin/bash
# B24 (2026-11-09): can a change to the unsound search's rounds reach the optimum of the games that every level-3 run
# misses?  Each game is played alone from its proven n - 1 line (--known-to n - 1, no best-known file) at level 3, no
# stop on growth, 8 threads, one play at a time, by the build taxman-VARIANT here.
#
#     ./run.sh VARIANT "GAMES" "SEEDS"
#
# GAMES is "rec", "ctl", "all" or a list of games; SEEDS a list of seeds.  Each play writes
# plays/VARIANT/gN-sS.jsonl and .log; a play whose .jsonl is not empty is done and skipped, so the script resumes after
# an interruption (a play cut short writes no line).  score.py reads the plays.
cd "$(dirname "$0")"
REC="3192 3311 3332 3384 3549 3565 3723 3844 3968 4107 4134 4225 5060"
CTL="3213 3321 3328 3392 3553 3542 3735 3828 3944 4100 4130 4224 5054"
variant=$1
case $2 in
    rec) games=$REC ;;
    ctl) games=$CTL ;;
    all) games="$REC $CTL" ;;
    *) games=$2 ;;
esac
seeds=$3
taxman=./taxman-$variant
[ -x "$taxman" ] || { echo "no build $taxman"; exit 1; }
mkdir -p plays/$variant
for seed in $seeds; do
    for g in $games; do
        out=plays/$variant/g$g-s$seed
        [ -s $out.jsonl ] && continue
        nice -n 19 $taxman solve $g-$g --unsound --effort 3 --stop-growth off --seed $seed \
            --known-to $((g - 1)) --best-known off --threads 8 --out $out.jsonl > $out.log 2>&1
        echo "$variant $out $(date +%T): $(grep -h '^n=' $out.log | head -n 1 | cut -c1-60)"
    done
done
echo "done $variant $(date +%T)"
