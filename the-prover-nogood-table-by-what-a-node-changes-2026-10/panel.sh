#!/bin/bash
# panel.sh BINARY LABEL GAME...: `exact --all 1` on each game, one thread, a fresh checkpoint directory each.
# NOGOODS_DIR holds out/ and ckpt/ (default: the script's folder).
S=${NOGOODS_DIR:-$(cd "$(dirname "$0")" && pwd)}
BIN=$1; LABEL=$2; shift 2
mkdir -p $S/out/$LABEL
for n in "$@"; do
  rm -rf $S/ckpt/$LABEL-$n; mkdir -p $S/ckpt/$LABEL-$n
  nice -n 19 $BIN --from $n --to $n --threads 1 --all 1 --out $S/out/$LABEL/$n.jsonl --checkpoints $S/ckpt/$LABEL-$n 2> $S/out/$LABEL/$n.err
done
echo done > $S/out/$LABEL/done
