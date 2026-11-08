#!/usr/bin/env python3
"""The lines that Part 1's stop rule would change, in detail.

    python3 -I part1_losses.py T

For each game of E2's runs at levels 1 to 6 and B11's Part 2 chains whose line the stop rule at T, with no floor,
changes: the chain, n, the work and the growth of the gap where it stops, the work of its last gain and its final
growth, the growth of the proven game of n (where opt(n) is known), the work of its play, and each gain's work and
growth.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import games_of, opt_scores, parity_bounds, growth_of  # noqa: E402
from part1 import chains, stop_point  # noqa: E402


def main():
    t = int(sys.argv[1])
    opt, bounds = opt_scores(), parity_bounds()
    for level, name, path in chains():
        for n, g in sorted(games_of(path, opt).items()):
            stop = stop_point(g, t, bounds)
            if stop is None:
                continue
            score, work, improvements = g.seeded()
            if stop[1] == score:
                continue
            last = max(i["work"] for i in improvements)
            proven = None
            if n in opt and n - 1 in opt:
                proven = (bounds[n] - opt[n]) - (bounds[n - 1] - opt[n - 1])
            print(f"level {level} {name} n={n}: stops at work {stop[0]} with growth {growth_of(g, stop[1], bounds)}, "
                  f"last gain at work {last}, final growth {growth_of(g, score, bounds)}, lost {score - stop[1]}; "
                  f"proven growth {proven}; play's work {work}; gains at "
                  f"{[(i['work'], growth_of(g, i['score'], bounds)) for i in improvements]}")


if __name__ == "__main__":
    main()
