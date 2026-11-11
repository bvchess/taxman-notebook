#!/usr/bin/env python3
"""Experiment C: does C2 carry its share at search nodes?

Runs the parity-only tree (core branching, best-first, cut at opt) and samples nodes at given depths (number of bars)
with parity bound above opt; at each, computes the C2 bound by sub-branch-and-bound and reports whether the node would
be cut (C2 bound <= opt), with the node's gap PB(N) - opt and the C2 gap.

Usage: python3 -I exp_c.py N depths samples budget_per_node
"""

import heapq
import itertools
import json
import random
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board, residual, minimal_core  # noqa: E402
from c2b import c2_bound  # noqa: E402


def parity_tree_nodes(board, opt, want_depths, limit_nodes=4000):
    """Nodes (picks, bars, pb) of the parity tree at the wanted depths, best-first, up to limit_nodes evaluations."""
    n = board.n
    counter = itertools.count()
    heap = [(0, next(counter), frozenset(), frozenset())]
    found = {d: [] for d in want_depths}
    evaluated = 0
    while heap and evaluated < limit_nodes:
        prio, _, pk, br = heapq.heappop(heap)
        try:
            low, pb = board.heaviest(pk, br)
        except ValueError:
            continue
        evaluated += 1
        if pb <= opt:
            continue
        if len(br) in found:
            found[len(br)].append((pk, br, pb))
        h = set(board.g) | set(low)
        conflict = None
        for k in sorted({board.om[x] for x in low}):
            if k < 4:
                continue
            lists = board.layer_instance(h, k)
            if residual(lists):
                core = minimal_core(lists, set(lists), sorted(lists, reverse=True))
                conflict = set(core) | {f for x in core for f in board.mf[x] if f in h}
                break
        if conflict is None:
            continue  # a playable heaviest set above opt cannot happen
        literals = sorted(x for x in conflict if x not in pk and x <= n // 2)
        for i, x in enumerate(literals):
            heapq.heappush(heap, (-pb, next(counter), pk | frozenset(literals[:i]), br | {x}))
    return found, evaluated


def main():
    n = int(sys.argv[1])
    depths = [int(d) for d in sys.argv[2].split(",")]
    samples = int(sys.argv[3])
    budget = float(sys.argv[4])
    random.seed(1)
    b = Board(n)
    opt = b.opt_line()["score"]
    t0 = time.time()
    found, evaluated = parity_tree_nodes(b, opt, depths)
    print(json.dumps({"n": n, "opt": opt, "tree_evaluated": evaluated,
                      "nodes_at_depth": {d: len(v) for d, v in found.items()},
                      "seconds": round(time.time() - t0, 1)}), flush=True)
    for d in depths:
        nodes = found[d]
        random.shuffle(nodes)
        for pk, br, pb in nodes[:samples]:
            r = c2_bound(b, pk, br, opt, budget=budget)
            out = {"n": n, "depth": d, "node_gap": pb - opt, "c2_bound": r["bound"],
                   "c2_gap": None if r["bound"] is None else r["bound"] - opt,
                   "cut": None if r["bound"] is None else r["bound"] <= opt,
                   "best_open_gap": None if r["best_open"] is None else r["best_open"] - opt,
                   "sub_nodes": r["evaluated"], "seconds": r["seconds"], "bars": sorted(br), "picks": len(pk)}
            print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
