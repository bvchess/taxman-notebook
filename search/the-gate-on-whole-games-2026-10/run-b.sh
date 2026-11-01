#!/usr/bin/env bash
# Phase B again (the first try gave --out only the line of n - 1, which the solver refuses): game 4875 whole at a fixed
# gate of 300, set up as the re-run set it up (its lines 1..4874 in --out, the carried nogoods of 4872), on 88 threads.
# Compare its own seconds with the re-run's 1.30 h.  Pauses the re-run first; resumes it whatever happens (trap EXIT).
#
# The places, each an environment variable that defaults to something beside this script: STUDY_DIR holds the runs and
# logs/; TAXMAN is the re-run's build of the solver (tag rerun-2026-10); CHAIN_DATA is the re-run's data folder
# (chain.lock, chain.pid, carried/, logs/chain.err, results/strict.jsonl); RERUN_SH starts the re-run again.
set -u
D=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
T=${TAXMAN:-$D/taxman}
DATA=${CHAIN_DATA:-$D/chain-data}
RERUN=${RERUN_SH:-$D/run.sh}
log() { echo "$(date '+%m-%d %H:%M:%S') $*" | tee -a "$D/logs/study.log"; }
resume() {
    log "resuming the re-run"
    for _ in $(seq 1 120); do flock -n "$DATA/chain.lock" true && break; sleep 5; done
    tmux kill-session -t tx 2>/dev/null
    env -u TMUX "$RERUN"
    sleep 90
    log "re-run: $(tail -c 300 "$DATA/logs/chain.err" | tail -1 | cut -c1-100)"
}
pid=""
stop_all() { log "stopped by a signal"; [ -n "$pid" ] && kill -TERM "$pid" 2>/dev/null; wait; exit 143; }

log "phase B2: pausing the re-run"
P=$(cat "$DATA/chain.pid")
kill -TERM "$P"
for _ in $(seq 1 60); do kill -0 "$P" 2>/dev/null || break; sleep 2; done
trap resume EXIT
trap stop_all TERM INT HUP
tmux kill-session -t tx 2>/dev/null
for _ in $(seq 1 60); do flock -n "$DATA/chain.lock" true && break; sleep 2; done

dir="$D/b/4875-g300"
rm -rf "$dir"; mkdir -p "$dir/ckpt" "$dir/carried"
cp "$DATA/carried/nogoods-4872.txt" "$dir/carried/"
python3 -c "import json,sys
for l in open(sys.argv[1]):
    if l.strip() and (d := json.loads(l))['n'] <= 4874 and d.get('completed'): print(l, end='')" \
    "$DATA/results/strict.jsonl" > "$dir/out.jsonl"
log "B2 4875-g300 start (seed lines: $(wc -l < "$dir/out.jsonl"))"
"$T" solve 4875-4875 --threads 88 --background --tactic price_reuse=on --tactic warm_start=on --finder-seconds 900 \
    --gate 300 --checkpoint-dir "$dir/ckpt" --carried-dir "$dir/carried" --out "$dir/out.jsonl" \
    > "$D/logs/b2-4875-g300.out" 2> "$D/logs/b2-4875-g300.err" &
pid=$!
wait "$pid"
log "B2 4875-g300 exit $? own: $(python3 -c "import json,sys; d=[json.loads(l) for l in open(sys.argv[1])][-1]; print(d['n'], d.get('completed'), round(d['seconds']['own']/3600,3), 'h', d.get('nodes'))" "$dir/out.jsonl")"
