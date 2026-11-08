#!/usr/bin/env python3
"""Whether a file of unsound lines of this study's build holds master's lines: the same lines, in order, but for the
times, the threads, the build, and the keys this build adds (the bound, the growth of the gap, the stop and the push on
growth, and the level of the unseeded play), with the rules off.

    python3 -I same.py A B [--all]

A is this build's file, B master's.  B's lines of the games A has are compared; prints the games whose lines differ.
With `--all`, B is a file of this study's build too, and the keys it adds are compared as well.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import opened  # noqa: E402

VARY = {"seconds", "start_seconds", "threads", "build"}
ADDED = {"bound", "growth", "growth_stop", "pushed", "stop_growth", "push_growth", "unseeded_effort"}


def lines(path):
    """The lines of the file, in order."""
    with opened(path) as f:
        return [json.loads(text) for text in f if text.strip()]


def strip(value, added, top=True):
    """`value` without the keys that vary, at every depth, and at the top without the keys this build adds unless
    `added`."""
    if isinstance(value, dict):
        return {key: strip(item, added, False) for key, item in value.items()
                if key not in VARY and not (top and not added and key in ADDED)}
    if isinstance(value, list):
        return [strip(item, added, False) for item in value]
    return value


def main():
    added = "--all" in sys.argv[3:]
    a = lines(sys.argv[1])
    games = {line["n"] for line in a}
    b = [line for line in lines(sys.argv[2]) if line["n"] in games]
    differ = [x["n"] for x, y in zip(a, b) if strip(x, added) != strip(y, added)]
    off = all(x.get("stop_growth") is None and x.get("push_growth") is None for x in a)
    print(f"{len(a)} and {len(b)} lines, the games in the same order: {[x['n'] for x in a] == [y['n'] for y in b]}; "
          f"the rules off in A: {off}")
    keys = "" if added else " and the keys added"
    print(f"lines that differ but for the times, the threads, the build{keys}: {differ}")


if __name__ == "__main__":
    main()
