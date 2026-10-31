#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
bin=$1; label=$2
for g in 1000 1040 1196 1771 2030 2044 1309 1508 1920 1575 1584 1600; do
  nice -n 19 $bin $g $g >> $S/out/$label-panel.jsonl 2>> $S/out/$label-panel.err
done
nice -n 19 $bin 187 1000 3 > $S/out/$label-sweep1.jsonl 2> $S/out/$label-sweep1.err
echo "exit=$?"
nice -n 19 $bin 1001 1400 7 > $S/out/$label-sweep2.jsonl 2> $S/out/$label-sweep2.err
echo "exit=$?"
echo pcheck2 done
