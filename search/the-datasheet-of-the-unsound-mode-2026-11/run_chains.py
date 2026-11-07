#!/usr/bin/env python3
"""Study E2 of the unsound mode, Part 1: the chains of the datasheet, run from a queue.

    nice -n 19 python3 -I run_chains.py --bin TAXMAN --dir DIR [--max-threads 80]

The jobs are 45 runs of `taxman solve LO-HI --unsound ...`: each of the five segments of 100 games (4561-4660, ...,
4961-5060) at each effort level 0 to 7, and the segments again at effort 4 with `--past-ceiling`.  Every run is one
command, with the options the race R1 chose, and writes the file DIR/eE-LO.jsonl (DIR/e4pc-LO.jsonl past the ceiling)
and the log DIR/eE-LO.log, none shared with another run:

    taxman solve LO-HI --unsound --effort E --back 8 --tilt 25 --widen 4 --seed 1 --threads T [--past-ceiling]
        --out FILE

with T = 4, and 8 at effort 7.  There is no `--from-known` and no `--stop-at-known`, so a run's first game starts from
the built-in table's game LO - 1 and every later one from the run's own line.  The queue is longest first (effort 7,
then 6, ..., 0, the segments from the top down within a level), and a job starts when the threads it needs fit under
`--max-threads` beside the running ones.  A run that has all its lines is skipped, and a run that has some resumes, so
a rerun of this script after a stop finishes the work.  SIGTERM or SIGINT passes the signal to the runs, which end
between rounds and leave their files whole, and then ends the script.  `DIR/jobs.log` records every start and end with
the machine's load average.
"""

import argparse
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time

SEGMENTS = [(4561, 4660), (4661, 4760), (4761, 4860), (4861, 4960), (4961, 5060)]
LEVELS = range(8)
OPTIONS = ["--back", "8", "--tilt", "25", "--widen", "4", "--seed", "1"]
PAST_CEILING_EFFORT = 4


class Job:
    """One run: a segment at a level, with or without the stop at the run's ceiling."""

    def __init__(self, directory, binary, lo, hi, effort, past_ceiling):
        self.lo, self.hi, self.effort, self.past_ceiling = lo, hi, effort, past_ceiling
        self.threads = 8 if effort == 7 else 4
        self.name = f"e{effort}{'pc' if past_ceiling else ''}-{lo}"
        self.file = os.path.join(directory, self.name + ".jsonl")
        self.log = os.path.join(directory, self.name + ".log")
        self.command = [
            binary, "solve", f"{lo}-{hi}", "--unsound", "--effort", str(effort), *OPTIONS,
            "--threads", str(self.threads), *(["--past-ceiling"] if past_ceiling else []), "--out", self.file,
        ]

    def lines_done(self):
        """How many of the run's games its file has."""
        if not os.path.exists(self.file):
            return 0
        with open(self.file) as f:
            return len({json.loads(line)["n"] for line in f if line.strip()})

    def order(self):
        """Longest first: the effort, with the past-ceiling run before the run at its effort, then the top segment."""
        return (-self.effort, not self.past_ceiling, -self.lo)


def jobs(directory, binary):
    """All the jobs, longest first."""
    every = [Job(directory, binary, lo, hi, e, False) for lo, hi in SEGMENTS for e in LEVELS]
    every += [Job(directory, binary, lo, hi, PAST_CEILING_EFFORT, True) for lo, hi in SEGMENTS]
    return sorted(every, key=Job.order)


def load():
    """The machine's load averages and running tasks, from /proc/loadavg."""
    with open("/proc/loadavg") as f:
        return f.read().strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--dir", required=True, help="the folder of the runs' files and logs")
    parser.add_argument("--max-threads", type=int, default=80, help="the most threads of all the running jobs")
    args = parser.parse_args()

    stopping = False
    running = {}  # name -> (job, Popen)
    ended = queue.Queue()

    def on_term(signum, _frame):
        """Pass the signal to the runs, which stop between rounds, and start no more."""
        nonlocal stopping
        stopping = True
        for _, child in list(running.values()):
            if child.poll() is None:
                child.send_signal(signal.SIGTERM)

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)

    def watch(job, child):
        """Wait for a run in a thread of its own and report its end."""
        ended.put((job, child.wait(), time.time()))

    queued = [job for job in jobs(args.dir, args.bin) if job.lines_done() < job.hi - job.lo + 1]
    used = 0
    failures = []
    with open(os.path.join(args.dir, "jobs.log"), "a") as record:

        def note(text):
            record.write(f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} {text}\n")
            record.flush()

        note(f"queue of {len(queued)} runs, at most {args.max_threads} threads: {' '.join(j.name for j in queued)}")
        began = {}
        while queued or running:
            while queued and not stopping and used + queued[0].threads <= args.max_threads:
                job = queued.pop(0)
                with open(job.log, "a") as log:
                    log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} {' '.join(job.command)}\n")
                    log.flush()
                    child = subprocess.Popen(job.command, stdout=log, stderr=subprocess.STDOUT)
                running[job.name] = (job, child)
                used += job.threads
                began[job.name] = time.time()
                threading.Thread(target=watch, args=(job, child), daemon=True).start()
                note(f"start {job.name} ({job.lines_done()} games done, {job.threads} threads, {used} in use), "
                     f"load {load()}")
            if not running:
                break
            job, code, finished = ended.get()
            del running[job.name]
            used -= job.threads
            note(f"end {job.name} exit {code} after {finished - began[job.name]:.0f} s, {job.lines_done()} games, "
                 f"load {load()}")
            if code != 0 and not stopping:
                failures.append((job.name, code))
        note(f"done: stopping={stopping}, not started {[j.name for j in queued]}, failures={failures}")
    if failures:
        print(f"failures: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
