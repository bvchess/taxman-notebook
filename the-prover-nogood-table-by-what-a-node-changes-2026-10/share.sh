#!/bin/bash
# share.sh: 1540 on 4 threads, with and without --share 10, master (c0d0d3e) and the rebased build.
# NOGOODS_DIR holds bin/ (the builds), out/ and ckpt/ (default: the script's folder).
S=${NOGOODS_DIR:-$(cd "$(dirname "$0")" && pwd)}
cd $S
for run in "master2 " "rebased " "master2 --share=10" "rebased --share=10"; do
  set -- $run
  bin=$1; share=$2
  label=$bin${share:+-share}
  rm -rf ckpt/t1540-$label; mkdir -p ckpt/t1540-$label
  extra=""; [ -n "$share" ] && extra="--share 10"
  /usr/bin/time -f "%e s wall, %U s user" nice -n 19 bin/exact-$bin --from 1540 --to 1540 --threads 4 --all 1 $extra --out out/t1540/$label-4.jsonl --checkpoints ckpt/t1540-$label > out/t1540/$label-4.txt 2>&1
done
echo done > out/t1540/done
