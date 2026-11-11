#!/bin/bash
# One board of experiment 1 (study-report-2.md, Section 4): the split's X-term at the X* of xstar.jsonl.
# Usage: run_board.sh N [PEEL] [THREADS] [SECONDS]
#   PEEL: xstar (exp_d's peel, the default), xstar_asc or xstar_desc
# The JSON line goes to out/N_PEEL.json, the progress lines to logs/N_PEEL.log.
set -euo pipefail
n=$1
peel=${2:-xstar}
threads=${3:-8}
seconds=${4:-3500}
dir=/home/brian/taxman_work/lab/work/oddcore/f2-1
bin=/home/brian/taxman_work/lab/work/cargo-target-f2/release/examples/e1_smooth
hubs=$(python3 -I -c "
import json
for line in open('$dir/xstar.jsonl'):
    d = json.loads(line)
    if d['n'] == $n:
        print(','.join(map(str, d['$peel'])))
")
if [ -z "$hubs" ]; then
    echo "no $peel for $n in xstar.jsonl" >&2
    exit 1
fi
mkdir -p "$dir/out" "$dir/logs"
nice -n 19 "$bin" "$n" --split --xstar "$hubs" --threads "$threads" --seconds "$seconds" \
    > "$dir/out/${n}_${peel}.json" 2> "$dir/logs/${n}_${peel}.log"
