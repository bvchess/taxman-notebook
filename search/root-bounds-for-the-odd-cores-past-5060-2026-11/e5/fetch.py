#!/usr/bin/env python3
"""Compute and cache the parity bound's heaviest set H and the recorded optimal set S* of boards (for E5).

    nice -n 19 python3 -I -B fetch.py N [N ...]       # writes cache/boardN.json, skipping boards already cached

The cache holds what parity.board returns plus the optimal moves of the game; e5.py reads it.
"""

import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def cache_path(n):
    return f"{HERE}/cache/board{n}.json"


def load_board(n):
    """The board's record from the cache, computing it (about 10 s at n = 5000) if absent."""
    path = cache_path(n)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    d = P.board(n)
    d["moves"] = P.results_line(n)["moves"]
    with open(path, "w") as f:
        json.dump(d, f)
    return d


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        d = load_board(int(arg))
        print(arg, d["bound"], d["opt"], d["gap"], flush=True)
