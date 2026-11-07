#!/usr/bin/env python3
"""What survives of a run's lines in each game replayed by run_inrun.py, against the run's line and opt(n).

    python3 -I show_inrun.py E2FILE INRUN.jsonl

For each game: opt(n), how far the run's line falls short of it, the replayed line's start and score, and for each game
whose moves a trajectory could begin from, how far what survives of them falls short of opt(n) (negative: a set the
run's line falls short of).
"""

import gzip
import json
import sys

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"


def main():
    opt = {}
    with gzip.open(RESULTS, "rt") as f:
        for text in f:
            d = json.loads(text)
            opt[d["n"]] = d["score"]
    run = {}
    with (gzip.open(sys.argv[1], "rt") if sys.argv[1].endswith(".gz") else open(sys.argv[1])) as f:
        for text in f:
            d = json.loads(text)
            run[d["n"]] = d["score"]
    with open(sys.argv[2]) as f:
        for text in f:
            d = json.loads(text)
            n = d["n"]
            best = opt[n]
            survivors = " ".join(f"{m - n:+d}:{best - s}" for m, s in d.get("survivors") or [])
            start = d["start"] and best - d["start"]
            print(f"{n} {d['method']:<6} run short {best - run[n]:>4}  start {start}  line {best - d['score']:>4}  "
                  f"work {d['work']:>8}  {survivors}")


if __name__ == "__main__":
    main()
