#!/bin/bash
# E11 at 4000 to completion: on 32 threads, under nice 19, capped at 4 hours, from scratch.  It waits for E11 at 5061
# (pid 728855) and E8 at 5060 with B = 31 (pid 759644) to end, so that with the E8 stream still running it stays
# within 40 threads.  Its line goes to hubs-full.jsonl, its progress (every 5 s) to logs/hubsfull-4000-23.log.
cd /home/brian/taxman_work/lab/work/oddcore/e1 || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-e1/release/examples/e1_smooth
tail --pid=728855 -f /dev/null
tail --pid=759644 -f /dev/null
echo "starting 4000 at $(date +%H:%M)"
nice -n 19 "$BIN" 4000 --smooth 23 --hubs --threads 32 --every 5 --seconds 14400 \
  2>logs/hubsfull-4000-23.log >>hubs-full.jsonl
echo "done hubs-full.jsonl 4000 B=23: $(tail -1 hubs-full.jsonl | python3 -I -c 'import json,sys; d=json.loads(sys.stdin.read()); print({k: d[k] for k in ["finished", "PB_s", "PB_s_upper", "share_low", "processed", "seconds", "threads"]})')"
