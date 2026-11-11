#!/bin/bash
# E12's boards: PB_sh (B = 23) with hub-ownership branching, best first, 16 threads, nice 19, an hour each.  Lines go to
# boards.jsonl, progress (every 20 s) to logs/board-N.log.  Extra arguments after the boards are passed on.
cd /home/brian/taxman_work/lab/work/oddcore/e12 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e12/release/examples/e1_smooth
mkdir -p logs
boards=()
while [ $# -gt 0 ] && [[ "$1" != -* ]]; do boards+=("$1"); shift; done
for n in "${boards[@]}"; do
  echo "starting $n at $(date +%H:%M)"
  nice -n 19 "$BIN" "$n" --smooth 23 --hubs --own --threads 16 --every 20 --seconds 3600 "$@" \
    2>"logs/board-$n.log" >>boards.jsonl
  echo "done $n at $(date +%H:%M)"
done
