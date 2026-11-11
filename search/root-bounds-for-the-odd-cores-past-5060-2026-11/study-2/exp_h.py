#!/usr/bin/env python3
"""Experiment H: the fiber side made exact.  With S*'s hub assignment (each hub of X* to the fiber that pays it in the
peel), solve each fiber's own promotion problem exactly (parity bound on the fiber alone, playability by peel, hubs
assigned to it as private columns, other hubs deleted) and compare the sum with S*'s fiber part and with F(X*).
Usage: python3 -I exp_h.py N [N ...]"""

import heapq
import itertools
import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board, residual, minimal_core  # noqa: E402
from split import Split, SMOOTH  # noqa: E402
from mi import max_weight_common  # noqa: E402


def hub_assignment(board, members):
    """hub -> fiber prime, from a complete peel of each layer of `members` (as in exp_d.hubs_paid_in_peel)."""
    mem = set(members)
    paid = {}
    for k in sorted({board.om[x] for x in members}):
        lists = {x: set(f for f in board.mf[x] if f not in mem) for x in members if board.om[x] == k}
        alive, live = set(lists), set().union(*lists.values()) if lists else set()
        while alive:
            moved = False
            for x in list(alive):
                cols = [f for f in lists[x] if f in live]
                if len(cols) == 1:
                    alive.discard(x); live.discard(cols[0]); moved = True
                    if board.lp[x] > SMOOTH and cols[0] == x // board.lp[x]:
                        paid[cols[0]] = board.lp[x]
                    break
            if moved:
                continue
            for f in list(live):
                listers = [x for x in alive if f in lists[x]]
                if len(listers) == 1:
                    x = listers[0]
                    alive.discard(x); live.discard(f); moved = True
                    if board.lp[x] > SMOOTH and f == x // board.lp[x]:
                        paid[f] = board.lp[x]
                    break
            assert moved
    return paid


def fiber_exact(board, sp, p, hubs_p, budget=300.0):
    """Max weight of fiber-p candidates playable with hubs_p as private columns, other hubs deleted; sources fixed."""
    half = board.n // 2
    sources = [s for s in sp.fiber_sources if board.lp[s] == p]
    cands = [x for x in sp.fiber_cands if board.lp[x] == p]
    elems = {x: sp.fiber_elems[x] for x in cands}
    deleted = [h for h in sp.hubs if h not in hubs_p]
    base = sp.base_vectors(sources, deleted)
    members_fixed = set(sources)

    def playable(promoted):
        members = members_fixed | set(promoted)
        for k in sorted({board.om[x] for x in members}):
            lists = {x: set(f for f in board.mf[x] if f not in members and (board.lp[f] > SMOOTH or f in hubs_p))
                     for x in members if board.om[x] == k}
            if residual(lists):
                return False, lists
        return True, None

    counter = itertools.count()
    heap = [(0, next(counter), frozenset(), frozenset(), None)]
    t0 = time.time()
    evaluated = 0
    while heap and time.time() - t0 < budget:
        prio, _, picks, bars, done = heapq.heappop(heap)
        if done is not None:
            return done, evaluated, True
        sub = {x: e for x, e in elems.items() if x not in bars}
        try:
            chosen, value = max_weight_common(sub, base[0], base[1], picks)
        except ValueError:
            continue
        evaluated += 1
        ok, lists = playable(chosen)
        if ok:
            heapq.heappush(heap, (-value, next(counter), picks, bars, value))
            continue
        core = minimal_core(lists, set(lists), sorted(lists, reverse=True))
        members = members_fixed | set(chosen)
        conflict = set(core) | {f for x in core for f in board.mf[x] if f in members}
        literals = sorted(x for x in conflict if x not in picks and x <= half)
        for i, x in enumerate(literals):
            heapq.heappush(heap, (-value, next(counter), picks | frozenset(literals[:i]), bars | {x}, None))
    return (-min(heap)[0] if heap else 0), evaluated, False


def main():
    for arg in sys.argv[1:]:
        n = int(arg)
        b = Board(n)
        line = b.opt_line()
        s = set(line["moves"])
        sp = Split(b)
        half = n // 2
        assign = hub_assignment(b, s)
        assign = {h: p for h, p in assign.items() if b.lp[h] <= SMOOTH and h <= half}
        xstar = set(assign)
        f_gf2, _, _ = sp.fiber_bound(usable=xstar)
        s_fiber = sum(x for x in s if x <= half and b.lp[x] > SMOOTH)
        primes = sorted({b.lp[x] for x in sp.fiber_sources + sp.fiber_cands})
        total, unfinished, per = 0, 0, {}
        for p in primes:
            hubs_p = {h for h, q in assign.items() if q == p}
            v, ev, fin = fiber_exact(b, sp, p, hubs_p)
            total += v
            if not fin:
                unfinished += 1
            sp_fiber = sum(x for x in s if x <= half and b.lp[x] == p)
            if v != sp_fiber:
                per[p] = {"exact": v, "S*": sp_fiber, "nodes": ev, "finished": fin}
        print(json.dumps({"n": n, "gap": b.heaviest()[1] - line["score"], "F_gf2(X*)": f_gf2, "F_exact(X*)": total,
                          "S*_fiber": s_fiber, "F_exact-S*": total - s_fiber, "F_gf2-S*": f_gf2 - s_fiber,
                          "unfinished_fibers": unfinished, "fibers_differing": per}), flush=True)


if __name__ == "__main__":
    main()
