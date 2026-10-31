#!/bin/bash
# usage: panel.sh BINARY LABEL GAME...   one game at a time, one thread, nice 19
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
bin=$1; label=$2; shift 2
mkdir -p $S/out $S/ckpt
for n in "$@"; do
  nice -n 19 $bin --from $n --to $n --threads 1 --out $S/out/$label-$n.jsonl --checkpoints $S/ckpt/$label-$n > $S/out/$label-$n.log 2>&1
done
echo done
