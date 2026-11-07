#!/usr/bin/env python3
"""Where two chains of the same games differ: the score of each game's line (its last) in each file.

    python3 -I differ.py WITHOUT WITH

Prints each game whose score differs, the two scores and the difference (with less without), and whether the line with
the repair was repaired, then the count of games higher and lower with the repair and the sum of the differences.
"""

import gzip
import json
import sys


def games(path):
    """The last line of each game of the file of unsound lines at `path`, by n."""
    out = {}
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        for text in f:
            d = json.loads(text)
            out[d["n"]] = d
    return out


def main():
    without, with_ = games(sys.argv[1]), games(sys.argv[2])
    higher = lower = total = 0
    for n in sorted(set(without) & set(with_)):
        a, b = without[n]["score"], with_[n]["score"]
        if a != b:
            repaired = with_[n].get("repaired")
            how = f"repaired from {repaired['from']}" if repaired else f"played, {with_[n]['method']}"
            print(f"{n}: {a} -> {b} ({b - a:+d}), {how}")
            higher += b > a
            lower += b < a
            total += b - a
    print(f"games in both: {len(set(without) & set(with_))}; higher with the repair {higher}, lower {lower}; "
          f"sum of the differences {total:+d}")


if __name__ == "__main__":
    main()
