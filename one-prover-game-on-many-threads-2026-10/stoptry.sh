#!/usr/bin/env bash
# Mimics the stop test: run exact on LIST with THREADS, SIGTERM at the first line (plus DELAY seconds), rerun; print
# the CPU of the exact runs only (bash's `times`, children line).
# usage: stoptry.sh LIST THREADS [DELAY [RERUN_THREADS]]   (LIST: games separated by commas, as in `exact --list`)
# STOP_DIR is the folder that gets try/ (default: the script's folder); EXACT_BIN is the exact binary (default:
# exact in STOP_DIR).
S=${STOP_DIR:-$(cd "$(dirname "$0")" && pwd)}
B=${EXACT_BIN:-$S/exact}
rm -rf "$S/try"
mkdir -p "$S/try"
nice -n 19 "$B" --list "$1" --threads "$2" --checkpoints "$S/try/ck" --out "$S/try/out.jsonl" 2>"$S/try/err1" &
pid=$!
until [ -f "$S/try/out.jsonl" ] && [ "$(wc -l <"$S/try/out.jsonl")" -ge 1 ]; do sleep 0.01; done
sleep "${3:-0}"
kill -TERM "$pid"
wait "$pid"
echo "status $?"
times >"$S/try/times1"
echo "after run 1 (shell, children): $(tail -n 1 "$S/try/times1")"
ls "$S/try/ck"
grep -E "not finished|nodes" "$S/try/err1"
nice -n 19 "$B" --list "$1" --threads "${4:-$2}" --checkpoints "$S/try/ck" --out "$S/try/out.jsonl" 2>&1 | grep -E "not finished|nodes"
times >"$S/try/times2"
echo "after run 2 (children): $(tail -n 1 "$S/try/times2")"
wc -l <"$S/try/out.jsonl"
