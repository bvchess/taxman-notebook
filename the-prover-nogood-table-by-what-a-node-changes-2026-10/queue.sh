#!/bin/bash
# The measurement queue, one thread, nice 19, one run at a time.
# NOGOODS_DIR holds bin/ (the builds), out/ and ckpt/ (default: the script's folder).
S=${NOGOODS_DIR:-$(cd "$(dirname "$0")" && pwd)}
cd $S
GAMES="798 864 988 1309 1508 1771 1920 2033 2044 1548 1587 1612"
nice -n 19 bin/nogoodcheck-master 0 $GAMES > out/fp-master.txt 2>&1
nice -n 19 bin/nogoodcheck-final 0 $GAMES > out/fp-final.txt 2>&1
./panel.sh $S/bin/exact-final panel-final 988 1309 1508 1771 1920 2044 1548 1587 1612
for label in master final; do
  nice -n 19 bin/nogoodcheck-$label 200000 1475 > out/long-$label.txt 2>&1
done
for label in before v2b; do
  rm -rf ckpt/long-prof-$label; mkdir -p ckpt/long-prof-$label
  START=$(date +%s.%N)
  nice -n 19 bin/exact-prof-$label --from 1475 --to 1475 --threads 1 --budget 200000 --out out/long-prof-$label.jsonl --checkpoints ckpt/long-prof-$label > out/long-prof-$label.txt 2>&1
  echo "wall $(echo "$(date +%s.%N) - $START" | bc) s" >> out/long-prof-$label.txt
done
echo done > out/queue.done
