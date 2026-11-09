#!/usr/bin/env python3
"""The push-down of pass 2: the windows to search now, below the roots of pass 2's gains (2026-11-08).

    python3 -I pushdown.py

A *gain* of pass 2 is a game whose best-known line came from a run of pass 2 or of its push-down: any file but pass
1's and pass 3's (pass 3 descends below its own gains).  A *root* is a gain whose game below is no gain.  The 8 games
below a root were played before the root's line was found, so they never searched from it; the mini-pass found them
short far more often than other games.  Prints the windows to search now, the 8 games below each root not yet handled,
merged where they touch, and records those roots in handled.txt.  A window whose bottom game gains makes a new root
lower down, so the push-down goes on until a window gains nothing.

A root is searched only once every game of its window has been played by pass 2's lane over it: the lower lane plays
up to UPPER - 1, the upper lane from UPPER on.
"""

import json
import os

BEST_KNOWN = "../best-known.jsonl"
LOWER = "../p2-l3s2.jsonl"
PASS1 = {"a-l3.jsonl", "a2-l3.jsonl", "b-l4.jsonl"}
PASS3 = "p3-"  # the files of pass 3 begin so
FIRST, UPPER, BELOW = 5061, 9300, 8
HANDLED = "handled.txt"


def last_game(path):
    with open(path) as f:
        return max(json.loads(text)["n"] for text in f if text.strip())


def of_pass2(name):
    return name not in PASS1 and not (name or "").startswith(PASS3)


def gains(path):
    best = {}
    with open(path) as f:
        for text in f:
            line = json.loads(text)
            n = line["n"]
            if n not in best or line["score"] > best[n]["score"]:
                best[n] = line
    return {n for n, line in best.items() if of_pass2((line.get("best_known") or {}).get("file"))}


def merged(windows):
    out = []
    for lo, hi in sorted(windows):
        if out and lo <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def main():
    lower = last_game(LOWER)
    raised = gains(BEST_KNOWN)
    handled = set()
    if os.path.exists(HANDLED):
        with open(HANDLED) as f:
            handled = {int(word) for word in f.read().split()}
    roots = [r for r in sorted(raised) if r - 1 not in raised and r > FIRST and r not in handled
             and (r - 1 < lower or r - BELOW >= UPPER)]
    if not roots:
        return
    with open(HANDLED, "a") as f:
        f.write(" ".join(map(str, roots)) + "\n")
    print(" ".join(f"{lo}-{hi}" for lo, hi in merged((max(FIRST, r - BELOW), r - 1) for r in roots)))


if __name__ == "__main__":
    main()
