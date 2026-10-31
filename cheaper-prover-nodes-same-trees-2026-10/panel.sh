#!/bin/bash
# Runs the panel, one game at a time on one thread at nice 19: panel.sh BINARY LABEL [GAMES...]
# Writes LABEL/out.jsonl (exact's lines) and LABEL/N.err (stderr: the profile, when built with it).
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
    nice -n 19 "$bin" --from "$n" --to "$n" --threads 1 --out "$dir/out.jsonl" --checkpoints "$ck" >"$dir/$n.out" 2>"$dir/$n.err"
    rm -rf "$ck"
    grep "\"n\":$n," "$dir/out.jsonl" | tail -1
done
