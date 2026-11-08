#!/usr/bin/env python3
"""Part 2.2 of study B13: the push's actions on the flagged streak starts of Part 1.

    python3 -I push.py

The flagged starts are 4914 (levels 1 and 2), 4950 (levels 1 to 6) and 5040 (levels 1 to 5) of E2's chains, and 5061,
which the chains past the table play from the table's 5060.  Each start's lines of n − 1 to n − 8 are the same moves at
every level of E2 (their `prev.moves_digest` agree), and a level runs the rounds of the levels below first, so the
seeded play at the next level is the push by more rounds, to twice the budget, and so on.  The unseeded plays are those
of push/runs/ (`--unseeded` at level 6, with `--stop-at-known` where the table has the game): the work at which each
reached its best score, and its score at each level's budget.  Prints, for each start, its shortfall at each level,
seeded and unseeded.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import E2, NOTEBOOK, games_of, opened, opt_scores  # noqa: E402

# The chain of 5061-5160 at level 6 of the comparison with the other heuristics.
SEVEN = f"{NOTEBOOK}/the-unsound-mode-against-the-other-heuristics-2026-11/runs/unsound/e7-5061.jsonl.gz"
HERE = os.path.dirname(os.path.abspath(__file__))


def unseeded_line(n):
    """The line of the unseeded play of game n at level 6, of push/runs/."""
    with opened(os.path.join(HERE, f"push/runs/u6-{n}.jsonl.gz")) as f:
        return json.loads(f.readline())
STARTS = [(4914, "4861"), (4950, "4861"), (5040, "4961")]


def budget(level):
    return 65_536 << level


def at_budget(line, level):
    """The score of a play by the budget of `level`, its last gain at or below it (else its start), and its first gain
    above it, which the round that reaches the budget may have made: the line does not say the work of each round."""
    below = [gain for gain in line["improvements"] if gain["work"] <= budget(level)]
    above = [gain for gain in line["improvements"] if gain["work"] > budget(level)]
    return (below[-1]["score"] if below else line["start"]), (above[0] if above else None)


def main():
    opt = opt_scores()
    for n, segment in STARTS:
        print(f"## {n}: opt(n) = {opt[n]}")
        for effort in range(2, 8):
            game = games_of(f"{E2}/e{effort}-{segment}.jsonl.gz", opt)[n]
            print(f"  seeded, level {effort - 1}: {opt[n] - game.played['score']} short")
        unseeded = unseeded_line(n)
        reached = unseeded["stop_at_known"]["round"]
        print(f"  unseeded: start {opt[n] - unseeded['start']} short; reaches opt(n) in round {reached} after "
              f"{unseeded['work']:,} work" if reached else "  unseeded: never reaches opt(n) at level 6")
        for level in range(1, 7):
            score, after = at_budget(unseeded, level)
            later = f"; the next gain, to {opt[n] - after['score']} short, at {after['work']:,} work" if after else ""
            print(f"  unseeded, level {level} ({budget(level):,} work): {opt[n] - score} short{later}")
    print("## 5061: from the table's 5060")
    unseeded = unseeded_line(5061)
    seven = games_of(SEVEN, opt)[5061].played
    print(f"  seeded, level 6: {seven['score']}, gains {[(g['work'], g['score']) for g in seven['improvements']]}")
    print(f"  unseeded, level 6: {unseeded['score']}, start {unseeded['start']}, gains "
          f"{[(g['work'], g['score']) for g in unseeded['improvements']]}")


if __name__ == "__main__":
    main()
