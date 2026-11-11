#!/bin/bash
# The five short games, each in its own process (the moves search is single-threaded), at nice 19, each capped at
# 30 minutes by a node budget sized from the measured rate (about 2,000 nodes/s at 5136, 635 at 9456) and by timeout.
cd /home/brian/taxman_work/lab/work/moves/check || exit 1
BIN=/home/brian/taxman_work/lab/work/cargo-target-moves/release/moves
run() {
    local n=$1 budget=$2
    /usr/bin/time -f "n=$n wall=%e s cpu=%U s maxrss=%M KB" timeout 1800 nice -n 19 "$BIN" --list "$n" \
        --results best7.jsonl --budget "$budget" --out "search$n.jsonl" > "search$n.log" 2>&1
    echo "n=$n exit=$?" >> "search$n.log"
}
run 5136 3000000 &
run 5232 2900000 &
run 7824 1400000 &
run 8688 1150000 &
run 9456 1000000 &
wait
