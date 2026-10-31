#!/bin/bash
# resume.sh BINARY LABEL EXTRA_NODES: resume the 1475 checkpoint (564,224 nodes, 17,830 nogoods) for EXTRA_NODES more
# nodes.  The checkpoint, ckpt/hard-orig/exact_1475_low.ckpt, is what the search of game 1475 left after 2,400 s on one
# thread; it is not kept.  NOGOODS_DIR holds ckpt/ and out/ (default: the script's folder).
S=${NOGOODS_DIR:-$(cd "$(dirname "$0")" && pwd)}
BIN=$1; LABEL=$2; EXTRA=$3
rm -rf $S/ckpt/$LABEL; mkdir -p $S/ckpt/$LABEL $S/out
cp $S/ckpt/hard-orig/exact_1475_low.ckpt $S/ckpt/$LABEL/
START=$(date +%s.%N)
nice -n 19 $BIN --from 1475 --to 1475 --threads 1 --budget $((564224 + EXTRA)) --out $S/out/$LABEL.jsonl --checkpoints $S/ckpt/$LABEL
echo "wall $(echo "$(date +%s.%N) - $START" | bc) s"
