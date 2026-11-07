#!/usr/bin/env python3
"""Run the unsound mode's commands of a batch one after another, each at nice 19, logging the machine's load before each.

    python3 -I run_b9.py BATCH DIR

BATCH has one run a line, `LABEL [NAME=VALUE ...] BIN ARG ...` (shell words; `#` starts a comment): the command
`env NAME=VALUE ... nice -n 19 BIN ARG ... --out DIR/LABEL.jsonl`, whose stdout goes to DIR/LABEL.log and stderr to
DIR/LABEL.err.
Before each run the script appends to DIR/runs.log the time (Pacific), `uptime` and the count of the processes named
taxman (`pgrep -x taxman`), and after it the exit status, the seconds and the CPU time of the command.  A run whose DIR/LABEL.done exists is skipped,
so a rerun of the script goes on from the first run not done; a run cut short starts again from the games its file
lacks (the command skips the ones it has).  SIGTERM ends the run in play between its rounds (the command's own handling)
and then the script.
"""

import itertools
import os
import resource
import shlex
import signal
import subprocess
import sys
import time

stopping = False
child = None


def on_term(signum, _frame):
    global stopping
    stopping = True
    if child is not None and child.poll() is None:
        child.send_signal(signum)


def pacific():
    return subprocess.run(["date", "+%Y-%m-%d %H:%M:%S %Z"], env={**os.environ, "TZ": "America/Los_Angeles"},
                          capture_output=True, text=True).stdout.strip()


def load_line():
    uptime = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()
    pids = subprocess.run(["pgrep", "-x", "taxman"], capture_output=True, text=True).stdout.split()
    return f"uptime: {uptime}; taxman processes: {len(pids)}"


def main():
    global child
    batch, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    runs = []
    with open(batch) as f:
        for line in f:
            words = shlex.split(line, comments=True)
            if words:
                runs.append(words)
    log = open(os.path.join(out_dir, "runs.log"), "a")
    for label, *words in runs:
        if stopping:
            break
        done = os.path.join(out_dir, label + ".done")
        if os.path.exists(done):
            continue
        # NAME=VALUE words before the binary set the environment of the command.
        env = list(itertools.takewhile(lambda word: "=" in word.split("/")[0], words))
        binary, *args = words[len(env):]
        command = ["env", *env, "nice", "-n", "19", binary, *args, "--out", os.path.join(out_dir, label + ".jsonl")]
        log.write(f"{pacific()} start {label}: {shlex.join(command)}\n  before: {load_line()}\n")
        log.flush()
        began, used = time.monotonic(), resource.getrusage(resource.RUSAGE_CHILDREN)
        with open(os.path.join(out_dir, label + ".log"), "a") as stdout, \
                open(os.path.join(out_dir, label + ".err"), "a") as stderr:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            status = child.wait()
            child = None
        seconds, now = time.monotonic() - began, resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = f"cpu user {now.ru_utime - used.ru_utime:.1f} s, system {now.ru_stime - used.ru_stime:.1f} s"
        log.write(f"{pacific()} end {label}: exit {status} after {seconds:.1f} s, {cpu}\n  after: {load_line()}\n")
        log.flush()
        if status == 0 and not stopping:
            open(done, "w").close()
    log.close()


if __name__ == "__main__":
    main()
