#!/usr/bin/env python3
"""Experiment B: the root value of the bound "parity-independent and C2" (fiber hub demands met by the smooth part).

Best-first branch and bound: nodes are (picks, bars); the parity bound with them is the node's value; the node is cut
at the known optimum; if its heaviest set satisfies C2 in every layer >= 4 it is the answer; else branch on a C2
conflict (bar one member, pick the earlier ones).

Usage: python3 -I exp_b.py N [budget_seconds]
"""

import heapq
import itertools
import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board, residual, minimal_core  # noqa: E402

SMOOTH = 23
MAX_COMBOS = 20000


def disjoint_internal_cores(int_lists):
    """Greedy packing of disjoint minimal cores of an internal instance (dict row -> set of internal columns)."""
    rows = set(int_lists)
    cores = []
    while rows:
        res = residual(int_lists, rows)
        if not res:
            break
        core = minimal_core(int_lists, res, sorted(res))
        cores.append(core)
        rows -= core
    return cores


def c2_conflict(board, members, k, stats=None):
    """None if layer k of `members` satisfies C2, else a conflict (a set of numbers of `members`)."""
    mem = set(members)
    lists = board.layer_instance(members, k)
    smooth_rows = {x: set(lists[x]) for x in lists if board.lp[x] <= SMOOTH}
    fibers = {}
    for x in lists:
        p = board.lp[x]
        if p > SMOOTH:
            fibers.setdefault(p, {})[x] = {f for f in lists[x] if f % p == 0}
    # privacy of internal columns
    owner = {}
    for p, rows in fibers.items():
        for x, cols in rows.items():
            for c in cols:
                assert owner.setdefault(c, p) == p, f"column {c} shared by fibers {owner[c]} and {p}"
    cores, hubsets = [], []
    for p, rows in fibers.items():
        for core in disjoint_internal_cores(rows):
            hubs = {x // p for x in core if x // p not in mem}
            cores.append(core)
            hubsets.append(hubs)
            if not hubs:  # a fiber core with no hub at all: unplayable outright
                return set(core) | {f for x in core for f in board.mf[x] if f in mem}
    if stats is not None:
        stats["cores"] = len(cores)
    if not cores:
        res = residual(smooth_rows)
        if not res:
            return None
        return set(res) | {f for x in res for f in board.mf[x] if f in mem}
    allhubs = set().union(*hubsets)
    if not residual({x: cols - allhubs for x, cols in smooth_rows.items()}):
        return None
    # DFS over systems of distinct hubs, one per core, pruned by monotonicity: if the smooth part already stalls with
    # the hubs chosen so far removed, every completion stalls too.
    union_res = set()
    order = sorted(range(len(hubsets)), key=lambda i: len(hubsets[i]))
    found = [False]

    def dfs(j, rm):
        res = residual({x: cols - rm for x, cols in smooth_rows.items()})
        if res:
            union_res.update(res)
            return
        if j == len(order):
            found[0] = True
            return
        for h in sorted(hubsets[order[j]]):
            if h in rm:
                continue
            dfs(j + 1, rm | {h})
            if found[0]:
                return

    dfs(0, frozenset())
    if found[0]:
        return None
    conflict = set(union_res)
    for core in cores:
        conflict |= core
    conflict |= {f for x in conflict for f in board.mf[x] if f in mem}
    return conflict


def main():
    n = int(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
    b = Board(n)
    opt = b.opt_line()["score"]
    t0 = time.time()
    counter = itertools.count()
    heap = [(0, next(counter), frozenset(), frozenset())]
    evaluated = 0
    root_pb = None
    best_open = None
    stats = {}
    answer = None
    while heap and time.time() - t0 < budget:
        prio, _, picks, bars = heapq.heappop(heap)
        try:
            low, pb = b.heaviest(picks, bars)
        except ValueError:
            continue
        evaluated += 1
        if root_pb is None:
            root_pb = pb
        if pb <= opt:
            continue
        if -prio and pb > -prio + 1e-9:
            raise AssertionError("child bound above parent")
        h = set(b.g) | set(low)
        conflict = None
        for k in sorted({b.om[x] for x in low}):
            if k < 4:
                continue
            conflict = c2_conflict(b, h, k, stats)
            if conflict:
                break
        if conflict is None:
            answer = pb
            break
        literals = sorted(x for x in conflict if x not in picks and x <= n // 2)
        for i, x in enumerate(literals):
            heapq.heappush(heap, (-pb, next(counter), picks | frozenset(literals[:i]), bars | {x}))
    if answer is None:
        if heap:
            best_open = -min(heap)[0]
        else:
            answer = opt  # every node cut at the optimum: the bound is exact
    out = {"n": n, "opt": opt, "PB": root_pb, "gap": root_pb - opt, "c2_bound": answer, "best_open": best_open,
           "evaluated": evaluated, "seconds": round(time.time() - t0, 1), "stats": stats}
    if answer is not None:
        out["share"] = round((root_pb - answer) / (root_pb - opt), 4)
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
