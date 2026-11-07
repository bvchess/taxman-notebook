#!/usr/bin/env python3
"""Study H1 of the unsound mode: runs its jobs from a queue.

    nice -n 19 python3 -I run_h1.py --dir DIR --taxman TAXMAN --playtaxman PLAYTAXMAN --heuristics HEURISTICS
        --optimal OPTIMAL [--max-threads 8] [--only PREFIX,...] [--list]

The jobs are the runs of the study, each one command of `taxman` or of h1_heuristics.py, with a file of its own and a
log in DIR:

* `heur/B-NAME.jsonl`: a heuristic strategy on 4561-5060, NAME one of moniot/'s seven (`moniot-onetax`, ...),
  `maxturn`, `onetax`, `cascade`, `solvent` (these cut into parts, `B-NAME-pK.jsonl`, each part the games K, K + PARTS,
  ... of the list the strategy plays) and `solvent_b` (every 100th game); `heur/B-chain-LO.jsonl`, the five chains
  (LO = 4561, ..., 4961), each from the optimal moves for LO - 1, of 20 games;
* `heur/C-NAME.jsonl`: the same on 5061-5160, past the proven games, with `solvent_b` on every 10th game and
  `heur/C-chain.jsonl`, one chain from the optimal moves for 5060 that plays until 4 hours of its games have passed;
* `unsound/eE-5061.jsonl`: the unsound mode on 5061-5160 at efforts 2, 4 and 7, a chain of 100 games from the table's
  game 5060: `taxman solve 5061-5160 --unsound --effort E --seed 1 --threads 4 --out FILE`.

The solvent-b runs of 4561-5060 and 5061-5160 beyond the parts of this queue were started by hand, as pools of
workers that claim the games between them (`h1_heuristics.py python --strategy solvent_b --workers W --order spread
--claims DIR --skip GLOB --deadline EPOCH`, the README has the commands), and so were the last two games of the
unsound mode on 5061-5160, after the queue was stopped.

A job whose file has all its games is skipped, and one that has some goes on from them.  The unsound mode's jobs share
one lane of 4 threads, a job at a time, and every other job is one thread; a job starts when its lane has room and
the threads of all the running jobs stay under `--max-threads`, with the lane's threads kept for the unsound mode
while any of its jobs is left.  The jobs start in the order of PRIORITY.  SIGTERM or SIGINT is passed to the running
jobs, which end between games, and ends the script.  `DIR/jobs.log` records every start and end with the load average.
"""

import argparse
import os
import queue
import signal
import subprocess
import sys
import threading
import time

B_LO, B_HI = 4561, 5060
B_CHAIN_LOS = (4561, 4661, 4761, 4861, 4961)
B_CHAIN_SAMPLE = 20
C_LO, C_HI = 5061, 5160
C_CHAIN_SECONDS = 4 * 3600
UNSOUND_EFFORTS = (2, 4, 7)
UNSOUND_THREADS = 4
MONIOT = ("OneTax", "GreedyOneTax", "PureOneTax", "MaxTurn+", "MaxTurn", "OddsEvens", "MaxPick")
PYTHON_STRATEGIES = ("maxturn", "onetax", "cascade", "solvent", "solvent_b")
# What a Python strategy plays: a list of (first, last, step, parts, number of the first part) of the games, and the
# parts it is cut into (a part plays every PARTSth game of the list, from the Kth).  The default is the whole range in
# one part.  The games of solvent_b on 4561-5060 are every 100th: 4561 (part 4, run by hand before the queue existed,
# with the same command), the others in the parts 0 to 3.
PLAN = {
    "B-solvent_b": [(4661, 4961, 100, 4, 0)], "B-cascade": [(B_LO, B_HI, 1, 4, 0)],
    "B-solvent": [(B_LO, B_HI, 1, 4, 0)],
    "C-solvent_b": [(C_LO, C_HI, 10, 10, 0)],
}
# Lower runs first: the longest jobs, so that the last ones to end are short.
PRIORITY = ("unsound/e7", "heur/C-chain", "heur/C-solvent_b", "unsound/e4", "unsound/e2", "heur/B-solvent_b",
            "heur/B-chain", "heur/B-solvent", "heur/B-cascade", "heur/C-solvent", "heur/C-cascade", "heur/B-moniot",
            "heur/C-moniot", "heur/C-maxturn", "heur/C-onetax", "heur/B-maxturn", "heur/B-onetax")


def moniot_name(strategy):
    """The file name of one of moniot/'s strategies."""
    return "moniot-" + strategy.lower().replace("+", "plus")


class Job:
    """One run: a command, the threads it uses, its file and the number of games the file holds when it is done."""

    def __init__(self, name, threads, command, expected, directory):
        self.name, self.threads, self.expected = name, threads, expected
        self.lane = "unsound" if name.startswith("unsound/") else "heur"
        self.out = os.path.join(directory, name + ".jsonl")
        self.log = os.path.join(directory, name + ".log")
        self.command = command + ["--out", self.out]

    def lines_done(self):
        """How many games the job's file has."""
        if not os.path.exists(self.out):
            return 0
        with open(self.out) as f:
            return sum(1 for line in f if line.strip())

    def priority(self):
        """The place of the job in PRIORITY: the first entry that its name starts with."""
        for place, prefix in enumerate(PRIORITY):
            if self.name.startswith(prefix):
                return place
        return len(PRIORITY)


def jobs(args):
    """Every job of the study."""
    d = args.dir
    heur = ["python3", "-I", os.path.abspath("h1_heuristics.py")]
    common = ["--heuristics", args.heuristics]
    every = []
    for effort in UNSOUND_EFFORTS:
        command = [args.taxman, "solve", f"{C_LO}-{C_HI}", "--unsound", "--effort", str(effort), "--seed", "1",
                   "--threads", str(UNSOUND_THREADS)]
        every.append(Job(f"unsound/e{effort}-{C_LO}", UNSOUND_THREADS, command, C_HI - C_LO + 1, d))
    for stretch, (lo, hi) in (("B", (B_LO, B_HI)), ("C", (C_LO, C_HI))):
        for strategy in MONIOT:
            command = heur + ["moniot", "--bin", args.playtaxman, "--strategy", strategy, "--lo", str(lo), "--hi",
                              str(hi)]
            every.append(Job(f"heur/{stretch}-{moniot_name(strategy)}", 1, command, hi - lo + 1, d))
        for strategy in PYTHON_STRATEGIES:
            for first, last, step, parts, number in PLAN.get(f"{stretch}-{strategy}", [(lo, hi, 1, 1, 0)]):
                for part in range(parts):
                    start, stride = first + part * step, step * parts
                    command = heur + ["python", "--strategy", strategy, "--lo", str(start), "--hi", str(last),
                                      "--every", str(stride), "--workers", "1"] + common
                    name = f"heur/{stretch}-{strategy}" + (f"-p{number + part}" if number or parts > 1 else "")
                    every.append(Job(name, 1, command, len(range(start, last + 1, stride)), d))
    chain = heur + ["chain", "--reanchor-solvent", "--optimal", args.optimal] + common
    for lo in B_CHAIN_LOS:
        every.append(Job(f"heur/B-chain-{lo}", 1, chain + ["--lo", str(lo), "--hi", str(lo + B_CHAIN_SAMPLE - 1)],
                         B_CHAIN_SAMPLE, d))
    # The chain of 5061-5160 stops when the seconds of its games pass four hours: it is done when it has played all
    # 100 games or has stopped there, which `expected` cannot tell, so a rerun goes on and stops at once.
    every.append(Job("heur/C-chain", 1, chain + ["--lo", str(C_LO), "--hi", str(C_HI), "--max-seconds",
                                                 str(C_CHAIN_SECONDS)], C_HI - C_LO + 1, d))
    return sorted(every, key=Job.priority)


def load():
    """The machine's load averages and running tasks, from /proc/loadavg."""
    with open("/proc/loadavg") as f:
        return f.read().strip()


def thread_limit(args):
    """The most threads to use: the number in DIR/max-threads if the file exists, else `--max-threads`."""
    try:
        with open(os.path.join(args.dir, "max-threads")) as f:
            return int(f.read().split()[0])
    except (OSError, ValueError, IndexError):
        return args.max_threads


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", required=True, help="the folder of the runs' files and logs")
    parser.add_argument("--taxman", required=True)
    parser.add_argument("--playtaxman", required=True)
    parser.add_argument("--heuristics", required=True)
    parser.add_argument("--optimal", required=True)
    parser.add_argument("--max-threads", type=int, default=8,
                        help="the most threads of all the running jobs; a number in the file DIR/max-threads, if it "
                             "exists, replaces it, and is read again every minute")
    parser.add_argument("--only", help="run only the jobs whose names start with one of these, comma separated")
    parser.add_argument("--list", action="store_true", help="list the jobs and what they have done, and stop")
    args = parser.parse_args()
    for sub in ("unsound", "heur"):
        os.makedirs(os.path.join(args.dir, sub), exist_ok=True)
    chosen = jobs(args)
    if args.only:
        prefixes = args.only.split(",")
        chosen = [j for j in chosen if any(j.name.startswith(p) for p in prefixes)]
    if args.list:
        for job in chosen:
            print(f"{job.name:32} {job.threads} threads  {job.lines_done()}/{job.expected}")
        return 0

    stopping = False
    running = {}
    ended = queue.Queue()

    def on_term(signum, _frame):
        """Pass the signal to the runs, which stop between games, and start no more."""
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

    queued = [job for job in chosen if job.lines_done() < job.expected]

    def threads_in_use(lane=None):
        return sum(j.threads for j, _ in running.values() if lane is None or j.lane == lane)

    def fits(job):
        """Whether the job may start: its lane has room, and the threads stay under the limit with the unsound
        lane's threads kept back while it has a job left."""
        limit = thread_limit(args)
        if job.lane == "unsound":
            return (threads_in_use("unsound") + job.threads <= UNSOUND_THREADS
                    and threads_in_use() + job.threads <= limit)
        kept = UNSOUND_THREADS if any(j.lane == "unsound" for j in queued) or threads_in_use("unsound") else 0
        return threads_in_use("heur") + job.threads <= limit - kept

    failures = []
    with open(os.path.join(args.dir, "jobs.log"), "a") as record:

        def note(text):
            record.write(f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} {text}\n")
            record.flush()

        note(f"queue of {len(queued)} jobs, at most {thread_limit(args)} threads: {' '.join(j.name for j in queued)}")
        began = {}
        while queued or running:
            # The first job that fits starts, so that a short job does not wait behind a job that needs more threads.
            started = True
            while started and queued and not stopping:
                started = False
                queued[:] = [job for job in queued if job.lines_done() < job.expected]
                for job in queued:
                    if fits(job):
                        queued.remove(job)
                        with open(job.log, "a") as log:
                            log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} {' '.join(job.command)}\n")
                            log.flush()
                            child = subprocess.Popen(["nice", "-n", "19"] + job.command, stdout=log,
                                                     stderr=subprocess.STDOUT)
                        running[job.name] = (job, child)
                        began[job.name] = time.time()
                        threading.Thread(target=watch, args=(job, child), daemon=True).start()
                        note(f"start {job.name} ({job.lines_done()}/{job.expected} games done, {job.threads} threads, "
                             f"{threads_in_use()} in use), load {load()}")
                        started = True
                        break
            if not running:
                break
            try:
                job, code, finished = ended.get(timeout=60)
            except queue.Empty:
                continue
            del running[job.name]
            note(f"end {job.name} exit {code} after {finished - began[job.name]:.0f} s, "
                 f"{job.lines_done()}/{job.expected} games, load {load()}")
            if code != 0 and not stopping:
                failures.append((job.name, code))
        note(f"done: stopping={stopping}, not started {[j.name for j in queued]}, failures={failures}")
    if failures:
        print(f"failures: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
