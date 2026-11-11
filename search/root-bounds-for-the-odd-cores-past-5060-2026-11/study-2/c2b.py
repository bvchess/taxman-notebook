#!/usr/bin/env python3
"""The C2 bound of a node by best-first branch and bound (library form of exp_b2.py)."""

import heapq
import itertools
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import minimal_core  # noqa: E402
from exp_b import c2_conflict  # noqa: E402


def c2_bound(board, picks, bars, cutoff, budget=600.0, max_nodes=None):
    """max{sum : parity-independent with picks/bars, C2 in every layer >= 4}, or cutoff if everything is cut at it.

    Returns dict with bound (None if unfinished), best_open, evaluated, root_pb, feasible (the C2-feasible set)."""
    n = board.n
    t0 = time.time()
    counter = itertools.count()
    heap = [(0, next(counter), frozenset(picks), frozenset(bars), None)]
    evaluated = 0
    root_pb = None
    answer = None
    feasible = None
    while heap and time.time() - t0 < budget and (max_nodes is None or evaluated < max_nodes):
        prio, _, pk, br, done = heapq.heappop(heap)
        if done is not None:  # a feasible node popped at the top of the heap: it is the maximum
            answer, feasible = -prio, done
            break
        try:
            low, pb = board.heaviest(pk, br)
        except ValueError:
            continue
        evaluated += 1
        if root_pb is None:
            root_pb = pb
        if pb <= cutoff:
            continue
        h = set(board.g) | set(low)
        conflict = None
        for k in sorted({board.om[x] for x in low}):
            if k < 4:
                continue
            if c2_conflict(board, h, k):
                lists = board.layer_instance(h, k)
                core = minimal_core(lists, set(lists), sorted(lists, reverse=True))
                conflict = set(core) | {f for x in core for f in board.mf[x] if f in h}
                break
        if conflict is None:
            heapq.heappush(heap, (-pb, next(counter), pk, br, low))
            continue
        literals = sorted(x for x in conflict if x not in pk and x <= n // 2)
        for i, x in enumerate(literals):
            heapq.heappush(heap, (-pb, next(counter), pk | frozenset(literals[:i]), br | {x}, None))
    best_open = -min(heap)[0] if heap else None
    if answer is None and not heap:
        answer = cutoff
    return {"bound": answer, "best_open": best_open, "evaluated": evaluated, "root_pb": root_pb,
            "feasible": feasible, "seconds": round(time.time() - t0, 1)}
