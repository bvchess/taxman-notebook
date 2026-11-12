#!/usr/bin/env python3
"""The rough part's error under other arrangements of the smooth part.  For living leaves of core5060's smooth-part
tree of 5060 at B = 13 (arrangements whose GF(2) bound exceeds opt(5060)), fix the arrangement (its members promoted,
the rest of the smooth part barred), leave the rough part free, and search exactly from a score to beat far below
opt, so that the search finds the best game with that arrangement and proves it.  The rough part's error under the
arrangement is the leaf's bound less that best.  Each run is one line of `restricted solve` with the fields leaf,
leaf_bound and differ (members by which the arrangement differs from the optimal one) added, in arrangements.jsonl;
a leaf already there is skipped.

    python3 -I run-arrangements.py TREE.jsonl FIX.jsonl COUNT [--seed R] [--below D] [--limit S]

FIX.jsonl must hold the line of fix-smooth 5060 --smooth 13 (its smooth_in and barred_in make the smooth part).
"""

import argparse
import json
import os
import random
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tree")
    parser.add_argument("fix")
    parser.add_argument("count", type=int)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--below", type=int, default=3000, help="the score to beat is opt less this")
    parser.add_argument("--limit", type=int, default=300, help="seconds a search")
    args = parser.parse_args()
    reference = None
    with open(args.fix) as f:
        for text in f:
            line = json.loads(text)
            if (line["n"], line["smooth"], line.get("rough"), line.get("random")) == (5060, 13, False, None) \
                    and "barred_in" in line:
                reference = line
    if reference is None:
        raise SystemExit("no line of fix-smooth 5060 --smooth 13 with barred_in")
    optimal = set(reference["smooth_in"])
    part = optimal | set(reference["barred_in"])
    opt = reference["opt"]
    leaves = []
    with open(args.tree) as f:
        for i, text in enumerate(f):
            line = json.loads(text)
            if line.get("leaf"):
                leaves.append((i, line))
    random.Random(args.seed).shuffle(leaves)
    out = os.path.join(HERE, "arrangements.jsonl")
    done = set()
    if os.path.exists(out):
        with open(out) as f:
            done = {json.loads(text)["leaf"] for text in f}
    for i, leaf in leaves[:args.count]:
        name = f"{os.path.basename(args.tree)}:{i}"
        if name in done:
            continue
        fixed = sorted(leaf["smooth_in"])
        if not set(fixed) <= part:
            raise SystemExit(f"leaf {name} holds numbers outside the smooth part")
        barred = sorted(part - set(fixed))
        command = ["chrt", "-i", "0", "nice", "-n", "19", os.path.join(HERE, "restricted"), "solve", "5060",
                   "--fix", ",".join(map(str, fixed)), "--bar", ",".join(map(str, barred)),
                   "--above", str(opt - args.below), "--threads", "16", "--background",
                   "--time-limit", str(args.limit), "--node-limit", "30000000", "--tactic", "symmetry=off"]
        run = subprocess.run(command, capture_output=True, text=True)
        with open(os.path.join(HERE, "arrangements.err"), "a") as f:
            f.write(run.stderr)
        if run.returncode != 0:
            with open(os.path.join(HERE, "arrangements.failed"), "a") as f:
                f.write(f"{name}: exit {run.returncode}\n")
            continue
        result = json.loads(run.stdout.strip().splitlines()[-1])
        result.pop("bar", None)
        result.pop("fix", None)
        result.pop("moves_left", None)
        result.update(leaf=name, leaf_bound=leaf["bound"], differ=len(optimal ^ set(fixed)), opt=opt,
                      below=args.below)
        with open(out, "a") as f:
            f.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
