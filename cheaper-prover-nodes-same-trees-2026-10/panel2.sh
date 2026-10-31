#!/bin/bash
# The panel with --all 1, for builds on 2896cdd and later, which skip an odd semiprime game the semiprime formula
# proves (1347 and 2033 are odd semiprimes): panel2.sh BINARY LABEL [GAMES...]
set -eu
here=${NODECOST_DIR:-$(cd "$(dirname "$0")" && pwd)}
bin=$1
label=$2
shift 2
games=${*:-"988 1347 1584 1771 2033 2044 1309 1508 1920"}
dir=$here/runs/$label
mkdir -p "$dir"
for n in $games; do
    ck=$dir/ckpt_$n
    rm -rf "$ck"
    mkdir -p "$ck"
    nice -n 19 "$bin" --from "$n" --to "$n" --threads 1 --all 1 --out "$dir/out.jsonl" --checkpoints "$ck" >"$dir/$n.out" 2>"$dir/$n.err"
    rm -rf "$ck"
    grep "\"n\":$n," "$dir/out.jsonl" | tail -1
done
