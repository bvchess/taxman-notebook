#!/usr/bin/env bash
# The proofs of README.md: one job, or a list of them, one at a time.
#
#   ./run.sh standalone N   prove N with no moves for N-1: no seed, no ceiling
#   ./run.sh seeded N       prove N with the committed lines of 1..N-1 as the --out file, so that the moves for N-1
#                           seed the search
#   ./run.sh follow N M     go on from the proven game N (out/standalone-N.jsonl) to the games N+1..M, as the chain
#                           does, every tactic at its default
#   ./run.sh batch FILE     each line of FILE is one of the above; a job that is done (out/ARM-N.done) is skipped
#
# A job's budget (score.py budget) is 3 times the chain's CPU-hours for a game the chain proved, else 3 times the
# fit's prediction at the game's gap; a search gets that budget's wall time on 16 threads (for follow, each game of the
# range), and a job whose budget passes 100 CPU-hours is not started.  standalone and seeded: --force-search, and
# prev_cap and near_repeat off, so that nothing rests on the moves for N-1.  All: 16 threads at nice 19, --window 1, the
# default gate and finder, no carried nogoods.  A job that a signal stopped resumes from its checkpoint with what is
# left of its budget; the checkpoint of a search that its budget stopped is kept in kept/ARM-N.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
bin=$here/taxman-aeffc29
score=$here/score.py
common=(--threads 16 --window 1 --progress 60)
proof=(--force-search --tactic prev_cap=off --tactic near_repeat=off)

stamp() { TZ=America/Los_Angeles date '+%F %H:%M %Z'; }

note() { echo "$(stamp) $*" | tee -a "$here/jobs.log"; }

one() {
    local arm=$1 n=$2 top=${3:-$2}
    local tag=$arm-$n
    local out=$here/out/$tag.jsonl log=$here/log/$tag.log ckpt=$here/ckpt/$tag done=$here/out/$tag.done
    if [[ -e $done ]]; then
        echo "skip $tag: done"
        return
    fi
    mkdir -p "$here/out" "$here/log" "$here/ckpt" "$here/tmp"
    local file range=$n lo=$n flags=("${proof[@]}") holder
    case $arm in
        standalone)
            file=$out
            if [[ ! -e $file ]] && holder=$(python3 "$score" proven "$n"); then
                note "not started $tag: $(basename "$holder") proves it"
                return
            fi
            ;;
        seeded)
            file=$here/tmp/$tag.jsonl
            [[ -e $file ]] || python3 "$score" prefix "$n" "$file"
            ;;
        follow)
            file=$here/tmp/$tag.jsonl
            if ! python3 "$score" proven "$n" > /dev/null; then
                note "not started $tag: game $n is not proven"
                return
            fi
            lo=$((n + 1)) range=$((n + 1))-$top flags=()
            if [[ ! -e $file ]]; then
                python3 "$score" extract "$here/out/standalone-$n.jsonl" "$n" > "$file"
            fi
            ;;
        *) echo "unknown arm $arm" >&2; exit 2 ;;
    esac
    # Past the table, the best-known scores when the job begins.
    if (( lo > 5060 )) && [[ ! -e $here/out/$tag.known ]]; then
        python3 "$score" known "$lo" "$top" > "$here/out/$tag.known"
    fi
    local hours wall verdict
    read -r hours wall verdict < <(python3 "$score" budget "$arm" "$n")
    if [[ $verdict != ok ]]; then
        note "not started $tag: its budget, $hours CPU-hours, passes 100"
        return
    fi
    local left=$(( wall - $(python3 "$score" spent "$file" "$lo" "$top") ))
    (( left > 0 )) || left=1
    note "start $tag ($range), budget $hours CPU-hours, limit ${left}s of ${wall}s"
    nice -n 19 "$bin" solve "$range" --out "$file" --checkpoint-dir "$ckpt" --time-limit "$left" "${common[@]}" \
        "${flags[@]}" >> "$log" 2>&1 < /dev/null
    if [[ $file != "$out" ]]; then
        python3 "$score" extract "$file" "$lo" "$top" > "$out"
        rm -f "$file"
    fi
    # The checkpoint of a search that its budget stopped is kept in kept/, so that a longer run can resume it; a
    # finished job's is gone already.
    if [[ -e $ckpt ]] && ls "$ckpt"/*.ckpt > /dev/null 2>&1; then
        mkdir -p "$here/kept"
        rm -f "$ckpt/taxman.lock"
        mv "$ckpt" "$here/kept/$tag"
        note "kept the checkpoint of $tag in kept/$tag"
    fi
    rm -rf "$ckpt"
    touch "$done"
    note "end $tag: $(grep -E "^n=[0-9]+ +score=" "$log" | tail -n "$((top - lo + 1))" | cut -c1-150 | paste -sd ';' || true)"
}

case ${1:-} in
    batch)
        while read -r arm n top; do
            [[ -z ${arm:-} || $arm == \#* ]] && continue
            one "$arm" "$n" "${top:-}"
        done < "$2"
        python3 "$score" table > "$here/results.md"
        ;;
    standalone | seeded) one "$1" "$2" ;;
    follow) one "$1" "$2" "$3" ;;
    *) echo "usage: $0 standalone|seeded N | $0 follow N M | $0 batch FILE" >&2; exit 2 ;;
esac
