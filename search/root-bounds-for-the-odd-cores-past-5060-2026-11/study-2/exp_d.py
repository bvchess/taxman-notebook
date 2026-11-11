#!/usr/bin/env python3
"""Experiment D: the smooth/fiber split bound at the root.

1. E(X*) + F(X*) at X* = the hubs paid by fiber rows in a peel of S* (one term of the max over X).
2. The Lagrangian B_mu by subgradient from mu = 0.
Usage: python3 -I exp_d.py N iterations budget_per_E
"""

import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402
from split import Split, SMOOTH  # noqa: E402


def hubs_paid_in_peel(board, members):
    """Fiber rows paired with their hub in a complete peel of each layer of `members` (one scheme among many)."""
    mem = set(members)
    paid = set()
    for k in sorted({board.om[x] for x in members}):
        lists = {x: set(f for f in board.mf[x] if f not in mem) for x in members if board.om[x] == k}
        alive = set(lists)
        live = set().union(*lists.values()) if lists else set()
        changed = True
        while changed:
            changed = False
            count = {}
            for x in alive:
                for f in lists[x]:
                    if f in live:
                        count[f] = count.get(f, 0) + 1
            for x in list(alive):
                cols = [f for f in lists[x] if f in live]
                if len(cols) == 1:
                    f = cols[0]
                    alive.discard(x)
                    live.discard(f)
                    if board.lp[x] > SMOOTH and f == x // board.lp[x]:
                        paid.add(f)
                    changed = True
                    break
            if changed:
                continue
            for f in list(live):
                listers = [x for x in alive if f in lists[x]]
                if len(listers) == 1:
                    x = listers[0]
                    alive.discard(x)
                    live.discard(f)
                    if board.lp[x] > SMOOTH and f == x // board.lp[x]:
                        paid.add(f)
                    changed = True
                    break
        assert not alive, f"layer {k} did not peel"
    return paid


def main():
    n = int(sys.argv[1])
    iters = int(sys.argv[2])
    budget = float(sys.argv[3])
    b = Board(n)
    line = b.opt_line()
    opt = line["score"]
    sp = Split(b)
    _, pb = b.heaviest()
    print(json.dumps({"n": n, "opt": opt, "PB": pb, "gap": pb - opt, "hubs": len(sp.hubs),
                      "smooth_cands": len(sp.smooth_cands), "fiber_cands": len(sp.fiber_cands)}), flush=True)
    s = set(line["moves"])
    xstar = hubs_paid_in_peel(b, s)
    t0 = time.time()
    e = sp.smooth_exact(deleted=xstar, budget=budget)
    f, _, _ = sp.fiber_bound(usable=xstar)
    bx = sum(sp.smooth_sources) + sum(sp.fiber_sources) + (e["value"] or 0) + f
    print(json.dumps({"X*": sorted(xstar), "E": e["value"], "E_nodes": e["evaluated"], "E_finished": e["finished"],
                      "F": f, "B_X*": bx, "B_X*_gap": bx - opt, "seconds": round(time.time() - t0, 1)}), flush=True)
    # the plain terms with no hub sold (E(empty) + F(all hubs usable)): the split's own root value at mu = 0
    mu = {h: 0.0 for h in sp.hubs}
    best = None
    step = 50.0
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
        norm = sum(v * v for v in g.values()) ** 0.5
        print(json.dumps({"iter": it, "bound": r["bound"], "gap": r["bound"] - opt, "best_gap": best - opt,
                          "sold": len(sold), "given_up": len(given), "E_nodes": r["E_nodes"], "gnorm": round(norm, 2),
                          "step": step, "seconds": round(time.time() - t0, 1)}), flush=True)
        if norm == 0:
            break
        for h in sp.hubs:
            mu[h] = mu[h] - step * g[h] / norm
        step *= 0.9


if __name__ == "__main__":
    main()
