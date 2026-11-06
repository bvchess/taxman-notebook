#!/usr/bin/env python3
"""Picks the sample of pilot P1: the hard games of 3441-5060, every 4th.

    python3 -I select_games.py E0_GAMES_JSON [OUT_DIR]

E0_GAMES_JSON is games.json of the entry `where-the-best-scores-came-from-2026-11`.  The games are those of method
`search`, 3441 <= n <= 5060, whose best score the start did not hold (`source` other than `start`), sorted by n, every
4th from the first.  Writes sample.json (the numbers of that run for each game) and games.txt (the n, one a line) to
OUT_DIR (default: the folder of this script).
"""

import json
import os
import sys

LOW, HIGH, EVERY = 3441, 5060, 4


def main():
    source = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    with open(source) as f:
        games = json.load(f)
    hard = sorted(
        (g for g in games if g["method"] == "search" and LOW <= g["n"] <= HIGH and g["source"] != "start"),
        key=lambda g: g["n"],
    )
    sample = []
    for g in hard[::EVERY]:
        finder = g["finder"]
        sample.append({
            "n": g["n"], "opt": g["opt"], "start": g["start"], "source": g["source"], "greedy": g["greedy"],
            "active": round(g["active"], 1),
            "finder": None if finder is None else {
                "best": finder["best"], "from": finder["from"], "seconds": round(finder["seconds"], 1),
                "found_seconds": round(finder["found_seconds"], 1)},
        })
    with open(os.path.join(out_dir, "sample.json"), "w") as f:
        json.dump(sample, f, separators=(",", ":"))
        f.write("\n")
    with open(os.path.join(out_dir, "games.txt"), "w") as f:
        f.write("".join(f"{g['n']}\n" for g in sample))
    print(f"{len(hard)} hard games, {len(sample)} in the sample")


if __name__ == "__main__":
    main()
