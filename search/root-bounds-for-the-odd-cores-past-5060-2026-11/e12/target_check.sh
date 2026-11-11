#!/bin/bash
# E12b's check of the search to a target: at boards where PB_sh is known (e1/hubval2.jsonl), a target of PB_sh - 1
# must fail (a set of the family above it is found) and a target of PB_sh must hold (the search ends without one),
# for each branching rule.  Lines go to targets.jsonl with the variant check-RULE-below / check-RULE-at.
cd /home/brian/taxman_work/lab/work/oddcore/e12 || exit 1
declare -A PBSH=([1000]=315482 [1500]=709424 [2000]=1260029 [2176]=1494375)
for n in 1000 1500 2000 2176; do
  v=${PBSH[$n]}
  for rule in e11 probe; do
    args=""
    [ "$rule" = probe ] && args="--own --probe --probe-live 2"
    ./target.sh "$n" $((v - 1)) "check-$rule-below" 600 $args
    ./target.sh "$n" "$v" "check-$rule-at" 600 $args
  done
done
