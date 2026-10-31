#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
mkdir -p $S/ckpt/hard2
for n in 1548 1587 1612; do
  nice -n 19 $S/exact-v6 --from $n --to $n --threads 1 --seconds 1500 --out $S/out/h2v6-$n.jsonl --checkpoints $S/ckpt/hard2 > $S/out/h2v6-$n.log 2>&1
  nice -n 19 $S/exact-master3 --from $n --to $n --threads 1 --seconds 1500 --out $S/out/h2m3-$n.jsonl --checkpoints $S/ckpt/hard2 > $S/out/h2m3-$n.log 2>&1
done
echo hard2 done
