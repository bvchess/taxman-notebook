#!/usr/bin/env bash
# Phase D: after 4984 at gate 300 ends, stop phase C (skipping 4984's default run and 4968), then game 3942, 4192 and
# 3441 whole at a fixed gate of 300, set up as the re-run set them up (its lines 1..n-1 in --out, the carried nogoods
# of the last searched game before n), on 88 threads.  Compare nodes and own time with the re-run's.  Resumes the
# re-run at the end whatever happens (trap EXIT).
#
# The places, each an environment variable that defaults to something beside this script: STUDY_DIR holds the runs and
# logs/; TAXMAN is the re-run's build of the solver (tag rerun-2026-10); CHAIN_DATA is the re-run's data folder
# (chain.lock, chain.pid, carried/, logs/chain.err, results/strict.jsonl); RERUN_SH starts the re-run again.
set -u
D=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
T=${TAXMAN:-$D/taxman}
DATA=${CHAIN_DATA:-$D/chain-data}
RERUN=${RERUN_SH:-$D/run.sh}
L=$D/logs/study.log
log() { echo "$(date '+%m-%d %H:%M:%S') $*" | tee -a "$L"; }
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

until grep -q "C 4984 g300 exit" "$L"; do sleep 20; done
C=$(ps -eo pid,args | grep "run-c.sh" | grep -v grep | grep -v "exec bash" | awk '{print $1}' | head -1)
before=$(grep -c "re-run: " "$L")
log "phase D: stopping phase C (pid $C)"
[ -n "$C" ] && kill -TERM "$C"
until [ "$(grep -c "re-run: " "$L")" -gt "$before" ]; do sleep 10; done
log "phase D: pausing the re-run"
P=$(cat "$DATA/chain.pid")
kill -TERM "$P"
for _ in $(seq 1 60); do kill -0 "$P" 2>/dev/null || break; sleep 2; done
trap resume EXIT
trap stop_all TERM INT HUP
tmux kill-session -t tx 2>/dev/null
for _ in $(seq 1 60); do flock -n "$DATA/chain.lock" true && break; sleep 2; done

for n in 3942 4192 3441; do
    dir="$D/d/$n-g300"
    rm -rf "$dir"; mkdir -p "$dir/ckpt" "$dir/carried"
    carry=$(ls "$DATA/carried" | sed -n 's/^nogoods-\([0-9]*\)\.txt$/\1/p' | awk -v n="$n" '$1 < n' | sort -n | tail -1)
    [ -n "$carry" ] && cp "$DATA/carried/nogoods-$carry.txt" "$dir/carried/"
    python3 -c "import json,sys
for l in open(sys.argv[1]):
    if l.strip() and (d := json.loads(l))['n'] < int(sys.argv[2]) and d.get('completed'): print(l, end='')" \
        "$DATA/results/strict.jsonl" "$n" > "$dir/out.jsonl"
    log "D $n g300 start (carried from $carry)"
    "$T" solve "$n-$n" --threads 88 --background --tactic price_reuse=on --tactic warm_start=on --finder-seconds 900 \
        --gate 300 --checkpoint-dir "$dir/ckpt" --carried-dir "$dir/carried" --out "$dir/out.jsonl" --time-limit 7200 \
        > "$D/logs/d-$n-g300.out" 2> "$D/logs/d-$n-g300.err" &
    pid=$!
    wait "$pid"
    rc=$?
    pid=""
    log "D $n g300 exit $rc: $(python3 -c "import json,sys; d=[json.loads(l) for l in open(sys.argv[1])][-1]; print(d['n'], d.get('completed'), round(d['seconds']['own']/3600,3), 'h', d.get('nodes'))" "$dir/out.jsonl")"
done
log "phase D done"
