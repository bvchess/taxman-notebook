#!/usr/bin/env python3
"""E11: replays the moves of every line of e11.jsonl by the plain rules of Taxman, with the referee of the research
repository's solver/tools/check_results.py (standard library only, no code shared with the solver), and prints for each
line the game, the region, the recorded and replayed scores, whether a legal move is left, and the line's delta and
recovery R = 6P - delta (for the 21P games, where 6P is what column 0 gives up).  Run as
`nice -n 19 python3 -I referee.py` from this folder."""
import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/research/solver/tools")
from check_results import Divisors, referee  # noqa: E402

BEST_KNOWN = {5061: 8057936}


def main():
    lines = [json.loads(line) for line in open("e11.jsonl")]
    divisors = Divisors(max(d["n"] for d in lines))
    print("n | region primes | score | replayed | moves left | opt(n) or best-known | delta | R = 6P - delta | nodes | s")
    for d in lines:
        n, p = d["n"], d["p"]
        replayed, left = referee(n, d["moves"], divisors)
        target = d["opt"] if d["opt"] is not None else BEST_KNOWN.get(n)
        r = 6 * p - d["delta"] if d["cofactor"] == 21 else None
        print(n, "|", d["columns"], "|", d["score"], "|", replayed, replayed == d["score"], "|", len(left), "|", target,
              "|", d["delta"], "|", r, "|", d["nodes"], d["seconds"])


if __name__ == "__main__":
    main()
