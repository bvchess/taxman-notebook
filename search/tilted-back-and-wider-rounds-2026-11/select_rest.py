#!/usr/bin/env python3
"""Lists the games of Part 2 of race E3b: the hard games of 3441-5060 that pilot P1 left out.

    python3 -I select_rest.py E0_GAMES_JSON [OUT_DIR [EVERY]]

E0_GAMES_JSON is games.json of the entry `where-the-best-scores-came-from-2026-11`.  P1's rule picks the games of method
`search`, 3441 <= n <= 5060, whose best score the start did not hold (`source` other than `start`), sorted by n, every
4th from the first; the 188 others are these games.  Writes `games-part2.txt` (the n, one a line) to OUT_DIR (default:
the folder of this script): all 188, or every EVERY-th of them from the first (default 1) when the run would take too
long.
"""

import json
import os
import sys

LOW, HIGH, P1_EVERY = 3441, 5060, 4


def main():
    source = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    every = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    with open(source) as f:
        games = json.load(f)
    hard = sorted(
        (g["n"] for g in games if g["method"] == "search" and LOW <= g["n"] <= HIGH and g["source"] != "start"),
    )
    rest = [n for i, n in enumerate(hard) if i % P1_EVERY]
    chosen = rest[::every]
    with open(os.path.join(out_dir, "games-part2.txt"), "w") as f:
        f.write("".join(f"{n}\n" for n in chosen))
    print(f"{len(hard)} hard games, {len(rest)} left out by P1, {len(chosen)} chosen (every {every})")


if __name__ == "__main__":
    main()
