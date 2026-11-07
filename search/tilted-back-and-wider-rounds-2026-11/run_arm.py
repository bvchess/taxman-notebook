#!/usr/bin/env python3
"""Run one arm of race E3b of the unsound mode on a list of games, one game at a time, appending to one file.

    nice -n 19 python3 -I run_arm.py --arm TKW --bin TAXMAN --games games.txt --out arm-tkw.jsonl --log arm-tkw.log

An arm is the options that shape the rounds (ARMS); every arm runs at effort 7, a budget of 2^6 * 65,536 = 4,194,304
work.  Each game is one command, seeded with the proven game of n - 1 and ended at the known score, on 4 threads:

    taxman solve N --unsound --effort 7 [OPTIONS] --from-known --stop-at-known --seed 1 --threads 4 --out FILE

The command skips a game that FILE already has, so a rerun of this script resumes.  SIGTERM ends the game in play
between its rounds (the command's own handling) and then the script, which leaves FILE whole.
"""

import argparse
import signal
import subprocess
import sys
import time

EFFORT = 7
SEED = 1
THREADS = 4

# arm: the options of the rounds.  A is the default.
ARMS = {
    "A": [],
    "T": ["--tilt"],
    "K": ["--back", "8"],
    "W": ["--widen", "4"],
    "TKW": ["--tilt", "--back", "8", "--widen", "4"],
    "TK": ["--tilt", "--back", "8"],
    "TKW16": ["--tilt", "--back", "8", "--widen", "16"],
}

stopping = False
child = None


def on_term(signum, _frame):
    """Pass the stop signal to the game in play, and stop after it."""
    global stopping
    stopping = True
    if child is not None and child.poll() is None:
        child.send_signal(signal.SIGTERM)


def command(binary, arm, n, out):
    """The command of one game of an arm."""
    return [
        binary, "solve", str(n), "--unsound", "--effort", str(EFFORT), *ARMS[arm], "--from-known", "--stop-at-known",
        "--seed", str(SEED), "--threads", str(THREADS), "--out", out,
    ]


def main():
    global child
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True, choices=sorted(ARMS))
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--games", required=True, help="a file with one n a line")
    parser.add_argument("--out", required=True, help="the unsound lines file of this arm")
    parser.add_argument("--log", required=True, help="the log of the commands' stdout and stderr")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    with open(args.games) as f:
        games = [int(line) for line in f if line.strip()]

    failures = []
    with open(args.log, "a") as log:
        for n in games:
            if stopping:
                break
            cmd = command(args.bin, args.arm, n, args.out)
            began = time.time()
            log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} arm {args.arm} game {n}: {' '.join(cmd)}\n")
            log.flush()
            child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
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
