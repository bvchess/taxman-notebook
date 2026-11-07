#!/usr/bin/env python3
"""Play games alone in the unsound mode, a game a command, several commands at once, for study B11.

    nice -n 19 python3 -I run_games.py --bin TAXMAN --jobs JOBS --dir DIR [--parallel P]

JOBS has one job a line, `ARM N`.  An arm is one of

* `uE`: game N unseeded at effort E, `--unseeded`, which takes nothing from the games below it;
* `sE`: game N played normally from the proven game of N - 1 at effort E, `--from-known`;

both with the defaults `--back 8 --tilt 25 --widen 4 --seed 1` and `--stop-at-known`, on THREADS threads:

    taxman solve N --unsound --effort E [--unseeded | --from-known] --stop-at-known --threads THREADS
        --out DIR/ARM/N.jsonl

Each game has a file of its own, so that commands run side by side; the command skips a game its file already has, so
a rerun of this script resumes.  Its stdout and stderr go to DIR/ARM/N.log.  P commands run at once (default 6, which
is 24 threads).  SIGTERM ends each game in play between its rounds (the command's own handling) and then the script.
"""

import argparse
import os
import signal
import subprocess
import sys
import time

THREADS = 4

stopping = False
children = []


def on_term(signum, _frame):
    """Pass the stop signal to the games in play, and start no other."""
    global stopping
    stopping = True
    for child in children:
        if child.poll() is None:
            child.send_signal(signal.SIGTERM)


def command(binary, arm, n, out):
    """The command of one job."""
    kind, effort = arm[0], arm[1:]
    how = {"u": ["--unseeded"], "s": ["--from-known"]}[kind]
    return [
        binary, "solve", str(n), "--unsound", "--effort", effort, *how, "--stop-at-known", "--threads", str(THREADS),
        "--out", out,
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--jobs", required=True, help="a file with one job a line, ARM N")
    parser.add_argument("--dir", required=True, help="the folder of the arms' files")
    parser.add_argument("--parallel", type=int, default=6)
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    with open(args.jobs) as f:
        jobs = [(arm, int(n)) for arm, n in (line.split() for line in f if line.strip())]

    running = {}
    failures = []
    queue = list(jobs)
    while queue or running:
        while queue and len(running) < args.parallel and not stopping:
            arm, n = queue.pop(0)
            folder = os.path.join(args.dir, arm)
            os.makedirs(folder, exist_ok=True)
            cmd = command(args.bin, arm, n, os.path.join(folder, f"{n}.jsonl"))
            log = open(os.path.join(folder, f"{n}.log"), "a")
            log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} {' '.join(cmd)}\n")
            log.flush()
            child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
            children.append(child)
            running[child.pid] = (child, arm, n, log, time.time())
        if stopping:
            queue = []
        if not running:
            break
        pid, status = os.wait()
        if pid not in running:
            continue
        child, arm, n, log, began = running.pop(pid)
        child.returncode = os.waitstatus_to_exitcode(status)
        children.remove(child)
        log.write(f"# exit {child.returncode} after {time.time() - began:.1f} s\n")
        log.close()
        if child.returncode != 0 and not stopping:
            failures.append((arm, n, child.returncode))
    print(f"done: stopping={stopping}, failures={failures}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
