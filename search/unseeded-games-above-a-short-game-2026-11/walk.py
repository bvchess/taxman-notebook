#!/usr/bin/env python3
"""The walk test of study B11: the streak of 4950 in E2's chain at effort 4, and in the same chain after the repair's
walk down from the unseeded line of 4951 and the games after it played on.

    python3 -I walk.py CHAIN WALKED LO HI

CHAIN is E2's chain of 4861-5060 at effort 4 (played on), WALKED the file of the walk and of the games played on from
it.  Prints, for each game LO..HI, opt(n) less the score of the game's last line in each file, the method, and where
the line in WALKED came from: the file as made (E2's line, or the unseeded line of 4951), a repair, or a game played
on.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optlib import last_lines, opt_scores  # noqa: E402


def main():
    chain, walked, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    opt = opt_scores()
    before, after = last_lines(chain), last_lines(walked)
    print(f"{'n':>5} {'opt(n)':>9} | {'E2 short':>8} {'method':>7} | {'after short':>11} {'method':>7}  line")
    short = {"E2": 0, "after": 0}
    for n in range(lo, hi + 1):
        b, a = before[n], after.get(n)
        short["E2"] += opt[n] > b["score"]
        if a is None:
            print(f"{n:>5} {opt[n]:>9} | {opt[n] - b['score']:>8} {b['method']:>7} | {'-':>11}")
            continue
        short["after"] += opt[n] > a["score"]
        if a.get("repaired"):
            how = f"repaired from {a['repaired']['from']}"
        elif a.get("unseeded"):
            how = "unseeded"
        elif a.get("build", {}).get("commit") == b.get("build", {}).get("commit") and a["score"] == b["score"]:
            how = "E2's"
        else:
            how = "played on"
        print(f"{n:>5} {opt[n]:>9} | {opt[n] - b['score']:>8} {b['method']:>7} | {opt[n] - a['score']:>11} "
              f"{a['method']:>7}  {how}")
    print(f"short games of {lo}-{hi}: E2 {short['E2']}, after {short['after']}")


if __name__ == "__main__":
    main()
