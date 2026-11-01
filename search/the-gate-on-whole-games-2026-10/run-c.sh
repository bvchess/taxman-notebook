#!/usr/bin/env bash
# Phase C: whole games under fixed gates against the default policy, the re-run's build, all 88 threads, one run at a
# time.  Phase B2 found 4875 at a fixed gate of 300 took 0.25 h and 125 M nodes against the re-run's 1.30 h and 997 M
# (gate 1200, then the trial's 600), while the trial's small pieces said 300 is worse: the gate matters at the top of
# the tree.  Every run here is set up the same way (--use-prev --force-search: the game of n - 1 from the built-in
# table, no carried nogoods), each stopped after LIMIT seconds.  Pauses the re-run first; resumes it whatever happens (trap EXIT).
#
# The places, each an environment variable that defaults to something beside this script: STUDY_DIR holds the runs and
# logs/; TAXMAN is the re-run's build of the solver (tag rerun-2026-10); CHAIN_DATA is the re-run's data folder
# (chain.lock, chain.pid, carried/, logs/chain.err, results/strict.jsonl); RERUN_SH starts the re-run again.
set -u
D=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
T=${TAXMAN:-$D/taxman}
DATA=${CHAIN_DATA:-$D/chain-data}
RERUN=${RERUN_SH:-$D/run.sh}
LIMIT=10800
TACT="--background --tactic price_reuse=on --tactic warm_start=on --finder-seconds 900"
DEFAULT="--gate 1200 --gate-trial 1000,800,600"
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

# Wait for phase B2's resume to finish, so the pid file names the running chain.
until grep -q "^10-31 19:1[6-9].*re-run: \|^10-31 19:[2-5].*re-run: " "$D/logs/study.log"; do sleep 5; done
log "phase C: pausing the re-run"
P=$(cat "$DATA/chain.pid")
kill -0 "$P" 2>/dev/null || log "the chain's pid $P is not running"
kill -TERM "$P" 2>/dev/null
for _ in $(seq 1 60); do kill -0 "$P" 2>/dev/null || break; sleep 2; done
trap resume EXIT
trap stop_all TERM INT HUP
tmux kill-session -t tx 2>/dev/null
for _ in $(seq 1 60); do flock -n "$DATA/chain.lock" true && break; sleep 2; done

run() {
    local n=$1 tag=$2; shift 2
    local dir="$D/c/$n-$tag"
    rm -rf "$dir"; mkdir -p "$dir/ckpt"
    log "C $n $tag start"
    "$T" solve "$n-$n" --use-prev --force-search --threads 88 $TACT "$@" --checkpoint-dir "$dir/ckpt" \
        --out "$dir/out.jsonl" --time-limit $LIMIT> "$D/logs/c-$n-$tag.out" 2> "$D/logs/c-$n-$tag.err" &
    pid=$!
    wait "$pid"
    local rc=$?
    pid=""
    log "C $n $tag exit $rc: $(python3 -c "import json,sys
ls=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
d=ls[-1] if ls else {}
s=d.get('seconds') or {}
print(d.get('n'), 'completed' if d.get('completed') else 'NOT completed', round(s.get('own',0)/3600,3), 'h', d.get('nodes'), 'nodes', (d.get('engine') or {}).get('gate_trial',{}) and d['engine']['gate_trial'].get('chosen'))" "$dir/out.jsonl" 2>&1 | tail -1)"
}
run 4875 g300 --gate 300
run 4875 g150 --gate 150
run 4875 default $DEFAULT
run 4879 g300 --gate 300
run 4879 default $DEFAULT
run 4893 g300 --gate 300
run 4893 default $DEFAULT
run 5052 g300 --gate 300
run 5052 default $DEFAULT
run 4984 g300 --gate 300
run 4984 default $DEFAULT
run 4968 g300 --gate 300
run 4968 default $DEFAULT
log "phase C done"
