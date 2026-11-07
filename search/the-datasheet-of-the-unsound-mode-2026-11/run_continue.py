#!/usr/bin/env python3
"""Study E2 of the unsound mode, Part 1b: the chain of 4861-4960 played on into 4961-5060.

    nice -n 19 python3 -I run_continue.py --bin TAXMAN --runs DIR --dir DIR2 [--efforts 1 2 3 4 5 6]

A streak of games below the proven score that reaches the end of a segment is cut there: the next segment starts from
the built-in table's game.  The streak of game 4950 reaches the end of the segment 4861-4960 at efforts 1 to 6.  For
each effort this script copies the lines of that segment's run (DIR/eE-4861.jsonl) to a file of its own
(DIR2/cont-eE.jsonl), so that the original is not touched, and plays 4961-5060 on that file:

    taxman solve 4961-5060 --unsound --effort E --back 8 --tilt 25 --widen 4 --seed 1 --threads T --out FILE

Game 4961 then takes the moves for 4960 from the file's line, as a user's run on from game 4960 would (its `prev.source`
is `results`, the file's), and the run goes on from there.  The runs go at once, one process each, with T = 4 (8 at
efforts 5 and 6, whose lines do not depend on the threads).  A rerun resumes.
"""

import argparse
import os
import shutil
import subprocess
import sys

OPTIONS = ["--back", "8", "--tilt", "25", "--widen", "4", "--seed", "1"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True, help="the taxman binary")
    parser.add_argument("--runs", required=True, help="the folder of Part 1's lines")
    parser.add_argument("--dir", required=True, help="the folder of the continuation's files and logs")
    parser.add_argument("--efforts", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6])
    args = parser.parse_args()

    children = []
    for effort in args.efforts:
        out = os.path.join(args.dir, f"cont-e{effort}.jsonl")
        if not os.path.exists(out):
            shutil.copyfile(os.path.join(args.runs, f"e{effort}-4861.jsonl"), out)
        threads = 8 if effort >= 5 else 4
        cmd = [args.bin, "solve", "4961-5060", "--unsound", "--effort", str(effort), *OPTIONS,
               "--threads", str(threads), "--out", out]
        with open(os.path.join(args.dir, f"cont-e{effort}.log"), "a") as log:
            log.write(f"# {' '.join(cmd)}\n")
            log.flush()
            children.append((effort, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)))
    failures = [(effort, code) for effort, child in children if (code := child.wait()) != 0]
    if failures:
        print(f"failures: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
