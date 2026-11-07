#!/usr/bin/env python3
"""Replay the short games of a run of E2 with trajectories from the run's own lines above them.

    nice -n 19 python3 -I run_inrun.py --bin TAXMAN --lines E2FILE --effort E --above J --games N,N,... --dir DIR

For each game k, a file DIR/inrun-k.jsonl gets the lines of E2FILE for k - 8 .. k - 1 and k + 1 .. k + 8 (not k), and
game k is played into it from them, with no table:

    taxman solve k --unsound --effort E --back 8 --tilt 25 --widen 4 --above J --seed 1 --threads 3 --out FILE

so it starts from the run's line of k - 1, as the run did, and begins trajectories from what survives of the run's
lines above it.  Its line is appended to DIR/inrun.jsonl.
"""

import argparse
import gzip
import json
import os
import subprocess

THREADS = 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True)
    parser.add_argument("--lines", required=True, help="a file of E2's lines")
    parser.add_argument("--effort", required=True, type=int)
    parser.add_argument("--above", required=True, type=int)
    parser.add_argument("--games", required=True, help="comma separated")
    parser.add_argument("--dir", required=True)
    parser.add_argument("--tactics-off", action="store_true", help="search primes and repeats too")
    args = parser.parse_args()

    lines = {}
    with (gzip.open(args.lines, "rt") if args.lines.endswith(".gz") else open(args.lines)) as f:
        for text in f:
            lines[json.loads(text)["n"]] = text
    os.makedirs(args.dir, exist_ok=True)
    with open(os.path.join(args.dir, "inrun.log"), "a") as log, open(os.path.join(args.dir, "inrun.jsonl"), "a") as out:
        for k in [int(g) for g in args.games.split(",")]:
            path = os.path.join(args.dir, f"inrun-{k}.jsonl")
            with open(path, "w") as f:
                for m in list(range(k - 8, k)) + list(range(k + 1, k + 9)):
                    if m in lines:
                        f.write(lines[m])
            cmd = [
                args.bin, "solve", str(k), "--unsound", "--effort", str(args.effort), "--back", "8", "--tilt", "25",
                "--widen", "4", "--above", str(args.above), "--seed", "1", "--threads", str(THREADS), "--out", path,
            ]
            if args.tactics_off:
                cmd += ["--tactic", "same_search=off", "--tactic", "prime_shortcut=off"]
            log.write("# " + " ".join(cmd) + "\n")
            log.flush()
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
            with open(path) as f:
                played = [text for text in f if json.loads(text)["n"] == k]
            out.write(played[-1])
            out.flush()


if __name__ == "__main__":
    main()
