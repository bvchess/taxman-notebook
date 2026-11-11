#!/usr/bin/env python3
"""Experiment E: the Lagrangian split bound B_mu at the root, with mu started at the fibers' marginal hub values and
Polyak-style steps toward a target.  Usage: python3 -I exp_e.py N iterations budget_per_E target_gap_guess"""

import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402
from split import Split  # noqa: E402


def main():
    n, iters, budget, target_gap = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    b = Board(n)
    opt = b.opt_line()["score"]
    sp = Split(b)
    # initial prices: the fibers' marginal value of each hub
    f_all, _, _ = sp.fiber_bound(usable=sp.hubs)
    mu = {}
    for h in sp.hubs:
        f_without, _, _ = sp.fiber_bound(usable=[x for x in sp.hubs if x != h])
        mu[h] = float(f_all - f_without)
    print(json.dumps({"n": n, "opt": opt, "hubs": len(sp.hubs), "mu0": {h: mu[h] for h in sp.hubs if mu[h]}}), flush=True)
    best = None
    target = opt + target_gap
    for it in range(iters):
        t0 = time.time()
        r = sp.lagrangian(mu, budget=budget)
        if r is None:
            print(json.dumps({"iter": it, "unfinished": True}), flush=True)
            break
        if best is None or r["bound"] < best:
            best = r["bound"]
        sold, given = set(r["sold"]), set(r["given_up"])
        g = {h: (1 if h in sold else 0) + (1 if h in given else 0) - 1 for h in sp.hubs}
        norm2 = sum(v * v for v in g.values())
        print(json.dumps({"iter": it, "bound": round(r["bound"], 1), "gap": round(r["bound"] - opt, 1),
                          "best_gap": round(best - opt, 1), "sold": sorted(sold), "given_up": sorted(given),
                          "E_nodes": r["E_nodes"], "seconds": round(time.time() - t0, 1)}), flush=True)
        if norm2 == 0:
            break
        step = max(0.0, r["bound"] - target) / norm2  # Polyak step toward the target value
        step = max(step, 5.0 / norm2 ** 0.5)
        for h in sp.hubs:
            mu[h] = mu[h] - step * g[h]


if __name__ == "__main__":
    main()
