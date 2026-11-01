#!/usr/bin/env bash
# The gate study of 2026-10-31: which gate policy minimizes the full chain's time, measured with the re-run's own
# build (tag rerun-2026-10, 3ca11bf).  Runs unattended in tmux; whatever happens, it resumes the re-run at the end
# (trap EXIT), so the machine never sits idle.
#   Phase A: 22 of the costliest games, each searched for a while on 4 threads with the gate trial over 8 gates
#            (2000,1200,1000,800,600,400,300,150), trial after 15 M steps; the trial's CPU per gate is in a-N.err.
#   Phase B: whole games 4875 and 4879 as the re-run set them up (the line of n-1 in --out, its carried nogoods), on
#            88 threads, with the trial over 1000,800,600,400,300,150; and 4875 at a fixed gate of 300 with no trial.
#            Compare their own seconds with the re-run's (4875: 1.30 h; 4879: 1.19 h).
#
# The places, each an environment variable that defaults to something beside this script: STUDY_DIR holds the runs
# (a/, b/, c/, d/, logs/, pids/); TAXMAN is the build of the solver (the re-run's, tag rerun-2026-10); CHAIN_DATA is the
# re-run's data folder (chain.lock, chain.pid, carried/, logs/chain.err, results/strict.jsonl); RERUN_SH starts the
# re-run again.
set -u
D=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
T=${TAXMAN:-$D/taxman}
DATA=${CHAIN_DATA:-$D/chain-data}
RERUN=${RERUN_SH:-$D/run.sh}
COMMON="--background --tactic price_reuse=on --tactic warm_start=on --finder-seconds 900"
mkdir -p "$D/logs"
log() { echo "$(date '+%m-%d %H:%M:%S') $*" | tee -a "$D/logs/study.log"; }

resume() {
    log "resuming the re-run"
    for _ in $(seq 1 120); do flock -n "$DATA/chain.lock" true && break; sleep 5; done
    tmux kill-session -t tx 2>/dev/null
    env -u TMUX "$RERUN"
    sleep 90
    log "re-run: $(tail -c 300 "$DATA/logs/chain.err" | tail -1 | cut -c1-100)"
}
trap resume EXIT
# A stop of this script stops its own searches first (each keeps its checkpoint), then the EXIT trap resumes the re-run.
stop_all() {
    log "stopped by a signal"
    for f in "$D"/pids/*; do [ -e "$f" ] && kill -TERM "$(cat "$f")" 2>/dev/null; done
    wait
    exit 143
}
trap stop_all TERM INT HUP
mkdir -p "$D/pids"
# Runs a search in the background, its pid in $D/pids/TAG (so a stop can reach it), and waits for it.
search() {
    local tag=$1; shift
    "$@" &
    local pid=$!
    echo "$pid" > "$D/pids/$tag"
    wait "$pid"
    local rc=$?
    rm -f "$D/pids/$tag"
    return $rc
}

log "phase A start"
A_GAMES="4983 4984 5054 5056 5049 5052 4968 4970 4893 4980 4975 4976 5060 4992 4991 4960 4890 4956 4950 4953 4961 4952"
run_a() {
    local n=$1
    mkdir -p "$D/a/$n/ckpt" "$D/a/$n/carried"
    search "a-$n" "$T" solve "$n-$n" --use-prev --force-search --threads 4 $COMMON --gate 1200 \
        --gate-trial 2000,1000,800,600,400,300,150 --gate-trial-plan after=15000000 \
        --checkpoint-dir "$D/a/$n/ckpt" --carried-dir "$D/a/$n/carried" --out "$D/a/$n/out.jsonl" \
        --time-limit 5400 > "$D/logs/a-$n.out" 2> "$D/logs/a-$n.err"
    log "A $n exit $? trial: $(grep -m1 'gate trial' "$D/logs/a-$n.err" | cut -c1-60)"
}
set -- $A_GAMES
while [ $# -gt 0 ]; do
    wave=""
    for _ in $(seq 1 11); do [ $# -gt 0 ] || break; wave="$wave $1"; shift; done
    log "wave:$wave"
    for n in $wave; do run_a "$n" & done
    wait
done
log "phase A done"

run_b() {
    local tag=$1 n=$2 carry=$3; shift 3
    local dir="$D/b/$tag"
    mkdir -p "$dir/ckpt" "$dir/carried"
    cp "$DATA/carried/nogoods-$carry.txt" "$dir/carried/"
    python3 -c "import json,sys
for l in open(sys.argv[1]):
    if l.strip() and (d := json.loads(l))['n'] == int(sys.argv[2]) and d.get('completed'): print(l, end='')" \
        "$DATA/results/strict.jsonl" "$((n - 1))" > "$dir/out.jsonl"
    log "B $tag start (seed lines: $(wc -l < "$dir/out.jsonl"))"
    search "b-$tag" "$T" solve "$n-$n" --threads 88 $COMMON "$@" \
        --checkpoint-dir "$dir/ckpt" --carried-dir "$dir/carried" --out "$dir/out.jsonl" \
        > "$D/logs/b-$tag.out" 2> "$D/logs/b-$tag.err"
    log "B $tag exit $? own: $(python3 -c "import json,sys; d=[json.loads(l) for l in open(sys.argv[1])][-1]; print(d['n'], d.get('completed'), round(d['seconds']['own']/3600,3), 'h', d.get('nodes'))" "$dir/out.jsonl")"
}
run_b 4875-trial 4875 4872 --gate 1200 --gate-trial 1000,800,600,400,300,150 &
wait $!
run_b 4879-trial 4879 4875 --gate 1200 --gate-trial 1000,800,600,400,300,150 &
wait $!
run_b 4875-g300 4875 4872 --gate 300 &
wait $!
log "phase B done"
