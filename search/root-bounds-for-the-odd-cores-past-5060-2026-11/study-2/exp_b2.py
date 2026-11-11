#!/usr/bin/env python3
"""Experiment B2: the root value of the bound "parity-independent and C2", by best-first branch and bound on
minimal full cores (c2b.py).  Usage: python3 -I exp_b2.py N [budget_seconds]"""

import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402
from c2b import c2_bound  # noqa: E402


def main():
    n = int(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
    b = Board(n)
    opt = b.opt_line()["score"]
    r = c2_bound(b, (), (), opt, budget=budget)
    out = {"n": n, "opt": opt, "PB": r["root_pb"], "gap": r["root_pb"] - opt, "c2_bound": r["bound"],
           "best_open": r["best_open"], "evaluated": r["evaluated"], "seconds": r["seconds"],
           "final_low": r["feasible"]}
    if r["bound"] is not None:
        out["c2_gap"] = r["bound"] - opt
        out["share"] = round((r["root_pb"] - r["bound"]) / (r["root_pb"] - opt), 4)
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
