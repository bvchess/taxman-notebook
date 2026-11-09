#!/usr/bin/env python3
"""The windows of the mini-pass below pass 2's breakthroughs (2026-11-08).

    python3 -I windows.py > windows.txt

A breakthrough of pass 2 is the first game of a streak of games whose best-known line came from pass 2's file.  The
games just below it were played before it was found, so they never searched from it.  Prints two lines:

    t LO-HI LO-HI ...   the target windows: the 8 games below each breakthrough, merged where they touch
    c LO-HI LO-HI ...   the control windows: as many games, in 8-game windows drawn at random from pass 2's range, at
                        least 16 games from any game pass 2 raised and from every other window

Only breakthroughs at least 20 games below pass 2's last game count, so each streak is complete.
"""

import json
import random

BEST_KNOWN = "../best-known.jsonl"
PASS2 = "p2-l3s2.jsonl"
FIRST = 5061  # pass 2's first game
BELOW, MARGIN, SETTLED = 8, 16, 20


def last_game(path):
    with open(path) as f:
        return max(json.loads(text)["n"] for text in f if text.strip())


def best_known_lines(path):
    best = {}
    with open(path) as f:
        for text in f:
            line = json.loads(text)
            n = line["n"]
            if n not in best or line["score"] > best[n]["score"]:
                best[n] = line
    return best


def merged(windows):
    out = []
    for lo, hi in sorted(windows):
        if out and lo <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def main():
    top = last_game("../" + PASS2)
    best = best_known_lines(BEST_KNOWN)
    raised = {n for n, line in best.items() if (line.get("best_known") or {}).get("file") == PASS2}
    starts = [n for n in sorted(raised) if n - 1 not in raised and n <= top - SETTLED]
    targets = merged((max(FIRST, m - BELOW), m - 1) for m in starts)
    games = sum(hi - lo + 1 for lo, hi in targets)

    taken = set(raised)
    for lo, hi in targets:
        taken.update(range(lo, hi + 1))
    rng = random.Random(3)
    controls = []
    while sum(hi - lo + 1 for lo, hi in controls) < games:
        lo = rng.randrange(FIRST + MARGIN, top - SETTLED - BELOW)
        hi = lo + BELOW - 1
        if any(abs(n - k) < MARGIN for n in (lo, hi) for k in taken):
            continue
        controls.append((lo, hi))
        taken.update(range(lo, hi + 1))

    print("t " + " ".join(f"{lo}-{hi}" for lo, hi in targets))
    print("c " + " ".join(f"{lo}-{hi}" for lo, hi in sorted(controls)))


if __name__ == "__main__":
    main()
