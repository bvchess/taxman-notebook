#!/usr/bin/env python3
"""The rehearsal's score after pass K (2026-11-08; the plan doc's "The rehearsal").

    python3 -I score.py K SECONDS THREADS

Reads the rehearsal's best-known.jsonl and the proven table, and prints, for the games 3001-5060: the games at opt(n),
the misses and the streaks they make; what pass K raised over the best-known scores after pass K - 1
(scores-(K-1).json), in games, streaks and points; its thread-hours (SECONDS of wall-clock on THREADS threads); and
from pass 3 on, the estimate of the streaks still short (if each pass finds a steady share c of them, after pass k
about found_k (1 - c) / c are left), beside the misses' streaks, which here are known.  Saves scores-K.json.  The last
line is "new streaks: S", the streaks pass K raised, which run.sh reads to decide whether to go on.
"""

import gzip
import json
import os
import sys

LO, HI = 3001, 5060
TABLE = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
BEST_KNOWN = "best-known.jsonl"


def streaks(games):
    out = []
    for n in sorted(games):
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return out


def table():
    opt = {}
    with gzip.open(TABLE, "rt") as f:
        for text in f:
            line = json.loads(text)
            if LO <= line["n"] <= HI:
                opt[line["n"]] = line["score"]
    return opt


def best_known():
    best = {}
    with open(BEST_KNOWN) as f:
        for text in f:
            if text.strip():
                line = json.loads(text)
                best[line["n"]] = max(best.get(line["n"], 0), line["score"])
    return best


def main():
    k, seconds, threads = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    opt, best = table(), best_known()
    before, found = {}, []
    if os.path.exists(f"scores-{k - 1}.json"):
        with open(f"scores-{k - 1}.json") as f:
            saved = json.load(f)
        before, found = {int(n): score for n, score in saved["scores"].items()}, saved["found"]
    scores = {n: best[n] for n in range(LO, HI + 1) if n in best}

    over = [n for n, score in scores.items() if score > opt[n]]
    missing = [n for n in range(LO, HI + 1) if n not in scores]
    misses = [n for n in range(LO, HI + 1) if scores.get(n, 0) < opt[n]]
    raised = [n for n, score in scores.items() if score > before.get(n, 0)]
    points = sum(score - before.get(n, 0) for n, score in scores.items() if n in before and score > before[n])
    new = len(streaks(raised))
    found = found + [new]

    print(f"pass {k}: {HI - LO + 1 - len(misses)} of {HI - LO + 1} games at opt(n); {len(misses)} misses in "
          f"{len(streaks(misses))} streaks, {sum(opt[n] - scores.get(n, 0) for n in misses)} points short")
    if over:
        print(f"ERROR: above opt(n): {over}")
    if missing:
        print(f"no line: {len(missing)} games, {streaks(missing)[:10]}")
    print(f"  the misses' streaks: {' '.join(f'{lo}-{hi}' if lo < hi else str(lo) for lo, hi in streaks(misses))}")
    print(f"  raised {len(raised)} games in {new} streaks, {points} points over pass {k - 1}; "
          f"{seconds / 3600:.2f} h on {threads} threads, {seconds * threads / 3600:.1f} thread-hours")
    if k >= 3 and found[-2] > 0 and found[-1] < found[-2]:
        c = 1 - found[-1] / found[-2]
        left = found[-1] * (1 - c) / c
        print(f"  estimate: c = 1 - {found[-1]}/{found[-2]} = {c:.2f}, streaks left about {left:.1f}; "
              f"in fact {len(streaks(misses))}")
    with open(f"scores-{k}.json", "w") as f:
        json.dump({"scores": scores, "found": found}, f)
    print(f"new streaks: {new}")


if __name__ == "__main__":
    main()
