#!/usr/bin/env python3
"""Whether two files of unsound lines hold the same lines, in order, but for the times, the threads, the build and the
number of the level (a build after master's renumbering calls the old effort E level E - 1).

    python3 -I same.py A B

B's lines of the games A has are compared; prints the games whose lines differ.
"""

import gzip
import json
import sys

VARY = {"seconds", "start_seconds", "threads", "build", "effort"}


def lines(path):
    """The lines of the file, in order."""
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        return [json.loads(text) for text in f if text.strip()]


def strip(value):
    """`value` without the keys that vary, at every depth."""
    if isinstance(value, dict):
        return {key: strip(item) for key, item in value.items() if key not in VARY}
    if isinstance(value, list):
        return [strip(item) for item in value]
    return value


def main():
    a = lines(sys.argv[1])
    games = {line["n"] for line in a}
    b = [line for line in lines(sys.argv[2]) if line["n"] in games]
    differ = [x["n"] for x, y in zip(a, b) if strip(x) != strip(y)]
    print(f"{len(a)} and {len(b)} lines, the games in the same order: {[x['n'] for x in a] == [y['n'] for y in b]}")
    print(f"lines that differ but for the times, the threads, the build and the level's number: {differ}")


if __name__ == "__main__":
    main()
