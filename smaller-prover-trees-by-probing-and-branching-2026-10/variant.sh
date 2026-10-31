#!/bin/bash
# usage: variant.sh BINARY LABEL PB-SETTINGS GAME...   (PB-SETTINGS may be "-" for none)
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
bin=$1; label=$2; pb=$3; shift 3
[ "$pb" = "-" ] && pb=""
mkdir -p $S/out $S/ckpt
for n in "$@"; do
  PB="$pb" nice -n 19 $bin --from $n --to $n --threads 1 --out $S/out/$label-$n.jsonl --checkpoints $S/ckpt/$label-$n > $S/out/$label-$n.log 2>&1
done
echo done
