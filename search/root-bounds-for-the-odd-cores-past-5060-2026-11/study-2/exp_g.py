#!/usr/bin/env python3
"""Experiment G: is max_X [E(X) + F(X)] much above its value at X*?  One-hub moves from X*.
Usage: python3 -I exp_g.py N budget_per_E"""

import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402
from split import Split, SMOOTH  # noqa: E402
from exp_d import hubs_paid_in_peel  # noqa: E402


def main():
    n, budget = int(sys.argv[1]), float(sys.argv[2])
    b = Board(n)
    line = b.opt_line()
    opt = line["score"]
    sp = Split(b)
    fixed = sum(sp.smooth_sources) + sum(sp.fiber_sources)
    xstar = {h for h in hubs_paid_in_peel(b, set(line["moves"])) if b.lp[h] <= SMOOTH and h <= sp.half}
    e = sp.smooth_exact(deleted=xstar, budget=budget)
    f, _, _ = sp.fiber_bound(usable=xstar)
    base = fixed + e["value"] + f
    print(json.dumps({"n": n, "opt": opt, "X*": sorted(xstar), "E": e["value"], "F": f, "B": base, "gap": base - opt}),
          flush=True)
    best = base
    for h in sp.hubs:
        t0 = time.time()
        x = xstar ^ {h}
        f2, _, _ = sp.fiber_bound(usable=x)
        if h in xstar and fixed + e["value"] + f2 <= best:  # removing a hub from X can only lower F; E rises
            pass
        e2 = sp.smooth_exact(deleted=x, budget=budget)
        if not e2["finished"]:
            print(json.dumps({"hub": h, "move": "remove" if h in xstar else "add", "unfinished": True}), flush=True)
            continue
        val = fixed + e2["value"] + f2
        best = max(best, val)
        print(json.dumps({"hub": h, "move": "remove" if h in xstar else "add", "E": e2["value"], "F": f2, "B": val,
                          "gap": val - opt, "best_gap": best - opt, "E_nodes": e2["evaluated"],
                          "seconds": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    main()
