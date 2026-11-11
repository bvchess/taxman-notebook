#!/usr/bin/env python3
"""Experiment F: how many playable smooth configurations lie within a margin of the smooth optimum E(empty)?
Usage: python3 -I exp_f.py N margin budget"""

import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402
from split import Split, smooth_enumerate  # noqa: E402


def main():
    n, margin, budget = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    b = Board(n)
    sp = Split(b)
    best, found, evaluated, truncated = smooth_enumerate(sp, margin, budget=budget)
    bands = {}
    for v, s in found:
        band = (best - v) // 25 * 25
        bands[band] = bands.get(band, 0) + 1
    print(json.dumps({"n": n, "E_empty": best, "margin": margin, "configs": len(found), "by_band_of_25": bands,
                      "evaluated": evaluated, "truncated": truncated}), flush=True)


if __name__ == "__main__":
    main()
