#!/usr/bin/env python3
"""The split's X-term at a given hub set X, by the Python study's own code (study-2/split.py): E(X) by its best-first
branch and bound, F(X) by its matroid intersection.  An independent check of the Rust values of out/N_RUN.json.

Usage: python3 -I check_term.py N BUDGET_SECONDS H,H,...
"""

import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402
from split import Split  # noqa: E402


def main():
    n, budget = int(sys.argv[1]), float(sys.argv[2])
    xs = {int(h) for h in sys.argv[3].split(",") if h}
    b = Board(n)
    opt = b.opt_line()["score"]
    sp = Split(b)
    t0 = time.time()
    f, _, _ = sp.fiber_bound(usable=xs)
    e = sp.smooth_exact(deleted=xs, budget=budget)
    fixed = sum(sp.smooth_sources) + sum(sp.fiber_sources)
    term = None if e["value"] is None else fixed + e["value"] + f
    print(json.dumps({"n": n, "X": sorted(xs), "E": e["value"], "E_finished": e["finished"], "E_nodes": e["evaluated"],
                      "F": f, "term_gap": None if term is None else term - opt,
                      "seconds": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    main()
