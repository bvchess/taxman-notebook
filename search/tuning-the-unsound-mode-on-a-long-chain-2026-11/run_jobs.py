#!/usr/bin/env python3
"""Run commands of the unsound mode side by side, for study B14 (adapted from B13's driver).

    nice -n 19 python3 -I run_jobs.py --bin TAXMAN --jobs JOBS --dir DIR [--parallel P] [--only NAME...]
                                      [--progress SECONDS]

JOBS has one job a line, `NAME ARG...`: the command `TAXMAN ARG... --out DIR/NAME.jsonl`, its stdout and stderr in
DIR/NAME.log, which records the command, the pid, the time it began and its exit.  Lines that begin with `#` are
comments.  P jobs run at once (default: all), in the order of JOBS.  A command goes on from its file, so a rerun
resumes.  The driver's own events (a job starting, a job ending, a progress line every SECONDS) go to stdout and to
DIR/driver.log, and the pid of every job to DIR/pids.txt, one `NAME PID` a line, so that one job can be stopped by
SIGTERM to its own pid: it ends between rounds, and its file keeps its games.  SIGTERM to the driver passes the signal
to every job in play and starts no other.
"""

import argparse
import os
import signal
import subprocess
import sys
import time

stopping = False
children = []
running = {}
log_path = None


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def say(text):
    """One event line, to stdout and to the driver's log."""
    line = f"{stamp()} {text}"
    print(line, flush=True)
    with open(log_path, "a") as f:
        f.write(line + "\n")


def on_term(signum, _frame):
    """Pass the stop signal to the jobs in play, and start no other."""
    global stopping
    stopping = True
    for child in children:
        if child.poll() is None:
            child.send_signal(signal.SIGTERM)


def progress(_signum, _frame):
    """A line a job in play: the games its log has and its last line (the repair's lines count as games)."""
    for _child, name, log, began, log_file in running.values():
        with open(log_file) as f:
            lines = [text for text in f if text.startswith("n=")]
        last = lines[-1].split()[:2] if lines else "none yet"
        say(f"progress {name}: {len(lines)} summary lines, last {last}, {time.time() - began:,.0f} s")


def main():
    global log_path
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--jobs", required=True, help="a file with one job a line, NAME ARG...")
    parser.add_argument("--dir", required=True, help="the folder of the jobs' files and logs")
    parser.add_argument("--parallel", type=int, default=0, help="the jobs at once (0: all)")
    parser.add_argument("--only", nargs="*", help="the names of the jobs to run (default: all)")
    parser.add_argument("--progress", type=float, default=0, help="seconds between progress lines (0: none)")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    os.makedirs(args.dir, exist_ok=True)
    log_path = os.path.join(args.dir, "driver.log")
    with open(args.jobs) as f:
        jobs = [line.split() for line in f if line.strip() and not line.startswith("#")]
    queue = [job for job in jobs if not args.only or job[0] in args.only]
    parallel = args.parallel or len(queue)
    failures = []
    say(f"driver pid {os.getpid()}, {len(queue)} jobs, {parallel} at once")
    if args.progress:
        signal.signal(signal.SIGALRM, progress)
        signal.setitimer(signal.ITIMER_REAL, args.progress, args.progress)
    while queue or running:
        while queue and len(running) < parallel and not stopping:
            name, *rest = queue.pop(0)
            log_file = os.path.join(args.dir, f"{name}.log")
            cmd = [args.bin, *rest, "--out", os.path.join(args.dir, f"{name}.jsonl")]
            log = open(log_file, "a")
            child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
            log.write(f"# {stamp()} pid {child.pid} {' '.join(cmd)}\n")
            log.flush()
            with open(os.path.join(args.dir, "pids.txt"), "a") as f:
                f.write(f"{name} {child.pid}\n")
            children.append(child)
            running[child.pid] = (child, name, log, time.time(), log_file)
            say(f"started {name}: pid {child.pid}")
        if stopping:
            queue = []
        if not running:
            break
        pid, status = os.wait()
        if pid not in running:
            continue
        child, name, log, began, _log_file = running.pop(pid)
        child.returncode = os.waitstatus_to_exitcode(status)
        children.remove(child)
        log.write(f"# {stamp()} exit {child.returncode} after {time.time() - began:.1f} s\n")
        log.close()
        say(f"{name}: exit {child.returncode} after {time.time() - began:.1f} s")
        if child.returncode != 0 and not stopping:
            failures.append((name, child.returncode))
    signal.setitimer(signal.ITIMER_REAL, 0)
    say(f"done: stopping={stopping}, failures={failures}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
