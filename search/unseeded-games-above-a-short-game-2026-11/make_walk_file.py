#!/usr/bin/env python3
"""Make the file of the walk test of study B11: a chain's lines below game M, then one more line of M.

    python3 -I make_walk_file.py CHAIN M LINE OUT

CHAIN is a file of unsound lines (E2's chain of 4861-5060 at effort 4, played on); its last line of each game below M
is copied to OUT, with `"repaired":null` added where the line lacks it (E2's build wrote no such key, and this build's
reader needs it).  LINE is a file whose last line of game M is appended to OUT: the unseeded line.  A run of the
unsound mode that opens OUT takes up the repair's walk from that last line, down the chain's lines below it.
"""

import json
import sys


def last_lines(path):
    """The last line of each game of a file of unsound lines, by n."""
    games = {}
    with open(path) as f:
        for text in f:
            if text.strip():
                line = json.loads(text)
                games[line["n"]] = line
    return games


def main():
    chain, m, line, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    below = last_lines(chain)
    top = last_lines(line)[m]
    with open(out, "x") as f:
        for n in sorted(k for k in below if k < m):
            game = below[n]
            game.setdefault("repaired", None)
            f.write(json.dumps(game, separators=(",", ":")) + "\n")
        f.write(json.dumps(top, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
