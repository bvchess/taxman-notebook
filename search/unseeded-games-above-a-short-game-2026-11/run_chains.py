#!/usr/bin/env python3
"""Play Part 2's chains of study B11 side by side: each a range at effort 4, with and without games played twice.

    nice -n 19 python3 -I run_chains.py --bin TAXMAN --dir DIR [--threads T] [--only NAME...]

Each chain is one command, with the defaults but for `--unseeded-every`:

    taxman solve LO-HI --unsound --effort 4 --unseeded-every K --seed 1 --threads T --out DIR/NAME.jsonl

for the chains of CHAINS (or those named), all at once, its stdout and stderr in DIR/NAME.log.  T is 5 by default:
four chains of 5 threads and the thread of each that makes the next game's setup are 24 threads.  A command goes on
from its file, and its lines do not depend on the threads, so a rerun resumes, on as many threads as it is given.
SIGTERM stops every chain between rounds (the command's own handling), and then the script.
"""

import argparse
import os
import signal
import subprocess
import sys
import time

# name, range, K.
CHAINS = [
    ("with-e4-4861", "4861-5060", 8),
    ("without-e4-4861", "4861-5060", 0),
    ("with-e4-5061", "5061-5260", 8),
    ("without-e4-5061", "5061-5260", 0),
]

children = []


def on_term(signum, _frame):
    """Pass the stop signal to every chain."""
    for child in children:
        if child.poll() is None:
            child.send_signal(signal.SIGTERM)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--dir", required=True, help="the folder of the chains' files")
    parser.add_argument("--threads", type=int, default=5)
    parser.add_argument("--only", nargs="*", help="the names of the chains to play (default: all)")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    os.makedirs(args.dir, exist_ok=True)
    logs = []
    for name, games, every in CHAINS:
        if args.only and name not in args.only:
            continue
        cmd = [
            args.bin, "solve", games, "--unsound", "--effort", "4", "--unseeded-every", str(every), "--seed", "1",
            "--threads", str(args.threads), "--out", os.path.join(args.dir, f"{name}.jsonl"),
        ]
        log = open(os.path.join(args.dir, f"{name}.log"), "a")
        log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} {' '.join(cmd)}\n")
        log.flush()
        children.append(subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT))
        logs.append((name, log, time.time()))
    codes = []
    for child, (name, log, began) in zip(children, logs):
        code = child.wait()
        log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S %Z')} exit {code} after {time.time() - began:.1f} s\n")
        log.close()
        codes.append((name, code))
    print(f"done: {codes}")
    if any(code != 0 for _, code in codes):
        sys.exit(1)


if __name__ == "__main__":
    main()
