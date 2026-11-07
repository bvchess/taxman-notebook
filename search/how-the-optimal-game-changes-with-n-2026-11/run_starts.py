#!/usr/bin/env python3
"""Play the start alone (the unsound mode at effort 0) of the games of the unsound pilot whose start fell short.

    nice -n 19 python3 -I run_starts.py --bin TAXMAN --p1 P1_ENTRY --out starts.jsonl --log starts.log

The games are those of the pilot's sample (P1_ENTRY/seed-1.jsonl) whose line did not hold the known score at round 0.
Each is one command, on 2 threads, seeded with the proven game of n - 1 as the pilot's games were:

    taxman solve N --unsound --effort 0 --from-known --threads 2 --out FILE

Its line records the start's promotions, which the pilot's lines do not.  The command skips a game that FILE already
has, so a rerun resumes.  SIGTERM ends the game in play (the command's own handling) and then the script.
"""

import argparse
import json
import signal
import subprocess
import sys
import time

THREADS = 2

stopping = False
child = None


def on_term(signum, _frame):
    """Pass the stop signal to the game in play, and stop after it."""
    global stopping
    stopping = True
    if child is not None and child.poll() is None:
        child.send_signal(signal.SIGTERM)


def short_games(p1_entry):
    """The n of the pilot's games whose start fell short of the known score."""
    out = []
    with open(f"{p1_entry}/seed-1.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            if rec["stop_at_known"]["round"] != 0:
                out.append(rec["n"])
    return out


def main():
    global child
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--p1", required=True, help="the folder of the unsound pilot's entry")
    parser.add_argument("--out", required=True, help="the file of the starts' unsound lines")
    parser.add_argument("--log", required=True, help="the log of the commands' stdout and stderr")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    failures = []
    with open(args.log, "a") as log:
        for n in short_games(args.p1):
            if stopping:
                break
            command = [args.bin, "solve", str(n), "--unsound", "--effort", "0", "--from-known",
                       "--threads", str(THREADS), "--out", args.out]
            began = time.time()
            log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} game {n}: {' '.join(command)}\n")
            log.flush()
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            code = child.wait()
            log.write(f"# game {n} exit {code} after {time.time() - began:.1f} s\n")
            log.flush()
            if code != 0 and not stopping:
                failures.append((n, code))
        log.write(f"# done: stopping={stopping}, failures={failures}\n")
    if failures:
        print(f"failures: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
