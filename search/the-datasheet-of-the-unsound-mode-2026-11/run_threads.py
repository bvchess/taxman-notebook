#!/usr/bin/env python3
"""Study E2 of the unsound mode, Part 2: one game on more threads, one run at a time.

    nice -n 19 python3 -I run_threads.py --bin TAXMAN --dir DIR [--games 4752 4864 5016] [--threads 4 8 16 32 64]

Each game at each thread count is one command, alone on the machine, at effort 5 with the options of Part 1:

    taxman solve N --unsound --effort 5 --back 8 --tilt 25 --widen 4 --seed 1 --from-known --threads T --out FILE

`--from-known` starts the game from the built-in table's moves for n - 1, as the race R1 did; there is no
`--stop-at-known`, so the whole budget of rounds runs (none of the three games has a ceiling in reach).  The file is
DIR/threadsN-T.jsonl and the log DIR/threadsN-T.log, and `DIR/threads.log` records each command's start and end with the
machine's load average.  The lines of one game must agree on every thread count but for their seconds, which
analyze.py checks.  A run whose file already has its line is skipped.
"""

import argparse
import os
import signal
import subprocess
import sys
import time

EFFORT = 5
OPTIONS = ["--back", "8", "--tilt", "25", "--widen", "4", "--seed", "1"]

stopping = False
child = None


def on_term(signum, _frame):
    """Pass the stop signal to the run in play, and stop after it."""
    global stopping
    stopping = True
    if child is not None and child.poll() is None:
        child.send_signal(signal.SIGTERM)


def load():
    """The machine's load averages and running tasks, from /proc/loadavg."""
    with open("/proc/loadavg") as f:
        return f.read().strip()


def main():
    global child
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--dir", required=True, help="the folder of the files and logs")
    parser.add_argument("--games", type=int, nargs="+", default=[4752, 4864, 5016])
    parser.add_argument("--threads", type=int, nargs="+", default=[4, 8, 16, 32, 64])
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    failures = []
    with open(os.path.join(args.dir, "threads.log"), "a") as record:
        for n in args.games:
            for threads in args.threads:
                if stopping:
                    break
                name = f"threads{n}-{threads}"
                path = os.path.join(args.dir, name + ".jsonl")
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    continue
                cmd = [
                    args.bin, "solve", str(n), "--unsound", "--effort", str(EFFORT), *OPTIONS, "--from-known",
                    "--threads", str(threads), "--out", path,
                ]
                began = time.time()
                record.write(f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} start {name}, load {load()}: {' '.join(cmd)}\n")
                record.flush()
                with open(os.path.join(args.dir, name + ".log"), "a") as log:
                    child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
                    code = child.wait()
                record.write(f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} end {name} exit {code} after "
                             f"{time.time() - began:.1f} s, load {load()}\n")
                record.flush()
                if code != 0 and not stopping:
                    failures.append((name, code))
    if failures:
        print(f"failures: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
