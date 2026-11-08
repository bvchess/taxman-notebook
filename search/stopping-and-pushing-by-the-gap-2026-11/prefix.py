#!/usr/bin/env python3
"""Copy a file of unsound lines as its run left it before it played game M, for a run to go on from.

    python3 -I prefix.py IN M OUT

IN may be gzipped.  Its lines are copied in order up to the first line of a game of M or above, so that the repairs
the run made after it played M are left out, and a run that opens OUT takes up the file as the run that wrote IN had it
when it began game M.  OUT must not exist.
"""

import gzip
import json
import sys


def main():
    source, m, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    opener = gzip.open if source.endswith(".gz") else open
    with opener(source, "rt") as f, open(out, "x") as g:
        for text in f:
            if not text.strip():
                continue
            if json.loads(text)["n"] >= m:
                break
            g.write(text if text.endswith("\n") else text + "\n")


if __name__ == "__main__":
    main()
