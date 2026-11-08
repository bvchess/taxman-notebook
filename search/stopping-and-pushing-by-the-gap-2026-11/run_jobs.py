#!/usr/bin/env python3
"""Run commands of the unsound mode side by side, for study B13.

    nice -n 19 python3 -I run_jobs.py --bin TAXMAN --jobs JOBS --dir DIR [--parallel P] [--only NAME...]
    nice -n 19 python3 -I run_jobs.py --bins KEY=TAXMAN... --jobs JOBS --dir DIR [--parallel P] [--only NAME...]

JOBS has one job a line, `NAME ARG...` (with `--bins`, `NAME KEY ARG...`, KEY naming the binary): the command `TAXMAN
ARG... --out DIR/NAME.jsonl`, its stdout and stderr in DIR/NAME.log, which records the command, the time it began and
its exit.  Lines that begin with `#` are comments.  P jobs run at once (default: all), in the order of JOBS.  A command
goes on from its file, so a rerun resumes.  SIGTERM passes the signal to every job in play, which ends between rounds
(the command's own handling), and starts no other.
"""

import argparse
import os
import signal
import subprocess
import sys
import time

stopping = False
children = []


def on_term(signum, _frame):
    """Pass the stop signal to the jobs in play, and start no other."""
    global stopping
    stopping = True
    for child in children:
        if child.poll() is None:
            child.send_signal(signal.SIGTERM)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", help="the taxman binary")
    parser.add_argument("--bins", nargs="*", help="KEY=TAXMAN: the binaries that the jobs name by KEY")
    parser.add_argument("--jobs", required=True, help="a file with one job a line, NAME ARG...")
    parser.add_argument("--dir", required=True, help="the folder of the jobs' files and logs")
    parser.add_argument("--parallel", type=int, default=0, help="the jobs at once (0: all)")
    parser.add_argument("--only", nargs="*", help="the names of the jobs to run (default: all)")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    os.makedirs(args.dir, exist_ok=True)
    with open(args.jobs) as f:
        jobs = [line.split() for line in f if line.strip() and not line.startswith("#")]
    if (args.bin is None) == (args.bins is None):
        sys.exit("give --bin or --bins")
    bins = dict(item.split("=", 1) for item in args.bins) if args.bins else None
    queue = [job for job in jobs if not args.only or job[0] in args.only]
    parallel = args.parallel or len(queue)
    running, failures = {}, []
    while queue or running:
        while queue and len(running) < parallel and not stopping:
            name, *rest = queue.pop(0)
            binary = args.bin if bins is None else bins[rest.pop(0)]
            cmd = [binary, *rest, "--out", os.path.join(args.dir, f"{name}.jsonl")]
            log = open(os.path.join(args.dir, f"{name}.log"), "a")
            log.write(f"# {stamp()} {' '.join(cmd)}\n")
            log.flush()
            child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
            children.append(child)
            running[child.pid] = (child, name, log, time.time())
        if stopping:
            queue = []
        if not running:
            break
        pid, status = os.wait()
        if pid not in running:
            continue
        child, name, log, began = running.pop(pid)
        child.returncode = os.waitstatus_to_exitcode(status)
        children.remove(child)
        log.write(f"# {stamp()} exit {child.returncode} after {time.time() - began:.1f} s\n")
        log.close()
        print(f"{stamp()} {name}: exit {child.returncode} after {time.time() - began:.1f} s", flush=True)
        if child.returncode != 0 and not stopping:
            failures.append((name, child.returncode))
    print(f"done: stopping={stopping}, failures={failures}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
