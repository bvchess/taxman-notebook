#!/usr/bin/env python3
"""Writes the best-known line of each game asked (the highest score in unsound-run/best-known.jsonl, the last if
tied, as in ../short.py) to a file the prover's `moves --results` reads.

Run:  nice -n 19 python3 -I extract.py OUT.jsonl N [N ...]    (reads best-known.jsonl only)
"""

import json
import sys
from pathlib import Path

BEST_KNOWN = Path("/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl")


def main():
    out, wanted = Path(sys.argv[1]), {int(a) for a in sys.argv[2:]}
    best = {}
    with BEST_KNOWN.open() as f:
        for line in f:
            game = json.loads(line)
            n = game["n"]
            if n in wanted and (n not in best or game["score"] >= best[n][0]):
                best[n] = (game["score"], line.rstrip("\n"))
    with out.open("w") as f:
        for n in sorted(best):
            f.write(best[n][1] + "\n")
    for n in sorted(best):
        game = json.loads(best[n][1])
        print(n, game["score"], len(game["moves"]))
    missing = sorted(wanted - set(best))
    if missing:
        sys.exit(f"no line for {missing}")


if __name__ == "__main__":
    main()
