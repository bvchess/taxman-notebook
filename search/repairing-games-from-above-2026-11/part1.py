#!/usr/bin/env python3
"""Part 1 of study B10: what survives of the proven games above n, and the search with trajectories from them.

    python3 -I part1.py DIR

DIR holds the lines of run_part1.py, gzipped, eE-aJ.jsonl.gz for the efforts E of 4 and 7 and the J of 0, 1, 2 and 4
games above.
Every game started from the proven game of n - 1, with `--back 8 --tilt 25 --widen 4 --seed 1 --stop-at-known`, so
a line says whether the game reached opt(n) (`stop_at_known.round`), after how much work, and which trajectory made the
improvement that reached it.  Prints, for each game, how far what survives of the proven games n + 1 .. n + 4 falls
short of opt(n), then for each effort and J the work at which the game reached opt(n) and the trajectory ("s" the
start, "-j" the game n - j, "+j" the game n + j), or "-" if it did not; then the counts.
"""

import gzip
import json
import os
import sys

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
R1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "a-share-of-tilted-neighborhoods-2026-11")
EFFORTS = (4, 7)
ABOVE = (0, 1, 2, 4)


def read(path):
    lines = {}
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        for text in f:
            d = json.loads(text)
            lines[d["n"]] = d
    return lines


def reached(d):
    """The work at which the line reached the known score, and the trajectory that made it; None if it did not."""
    known = d["stop_at_known"]
    if known["round"] is None:
        return None
    if d["start"] is not None and d["start"] >= known["known"]:
        return 0, "s"
    raised = next(r for r in d["improvements"] if r["score"] >= known["known"])
    origin = d["trajectories"][raised["trajectory"]]
    where = "s" if origin == "start" else f"{origin - d['n']:+d}"
    return raised["work"], where


def main():
    folder = sys.argv[1]
    opt = {}
    with gzip.open(RESULTS, "rt") as f:
        for text in f:
            d = json.loads(text)
            if d["n"] >= 3400:
                opt[d["n"]] = d["score"]
    runs = {(e, j): read(os.path.join(folder, f"e{e}-a{j}.jsonl.gz")) for e in EFFORTS for j in ABOVE}
    # The arm of effort 7 with no game above is race R1's arm K25W4 (the same command but for --above 0 and the
    # threads), which this build played again line for line on the games it ran before it was stopped.
    r1 = {}
    for part in range(6):
        r1.update(read(os.path.join(R1, f"k25w4-{part}.jsonl")))
    for n, d in r1.items():
        if n in runs[(7, 4)] and n not in runs[(7, 0)]:
            runs[(7, 0)][n] = d
    games = sorted(runs[(7, 4)])
    header = "n     above: +1    +2    +3    +4 |" + "".join(
        f" E{e} J{j}         " for e in EFFORTS for j in ABOVE)
    print(header)
    counts = {key: 0 for key in runs}
    from_above = {key: 0 for key in runs}
    at_zero = {key: 0 for key in runs}
    survivors_at_opt = [0, 0, 0, 0]
    for n in games:
        line = runs[(7, 4)][n]
        survivors = {m: s for m, s in line.get("survivors") or [] if m > n}
        short = [opt[n] - survivors[n + j] if n + j in survivors else None for j in range(1, 5)]
        for j, s in enumerate(short):
            survivors_at_opt[j] += s == 0
        cells = " ".join(f"{'-' if s is None else s:>5}" for s in short)
        row = f"{n} {cells} |"
        for key in runs:
            d = runs[key].get(n)
            got = d and reached(d)
            if got:
                counts[key] += 1
                from_above[key] += got[1].startswith("+")
                at_zero[key] += got[0] == 0
            row += f" {('-' if not got else f'{got[0]}:{got[1]}'):>16}"
        print(row)
    print()
    print(f"games: {len(games)}; what survives of n + j is opt(n) in", ", ".join(
        f"+{j + 1}: {c}" for j, c in enumerate(survivors_at_opt)))
    for key in runs:
        print(f"E{key[0]} J{key[1]}: opt(n) in {counts[key]} of {len(runs[key])}, {at_zero[key]} at work 0, "
              f"{from_above[key]} by a trajectory from above")


if __name__ == "__main__":
    main()
