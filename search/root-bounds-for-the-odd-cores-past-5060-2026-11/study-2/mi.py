#!/usr/bin/env python3
"""Weighted matroid intersection of two GF(2) linear matroids on arbitrary elements (a generalization of
parity.intersect).  An element is (v0, v1, w): its vectors at parity 0 and 1 (ints as bit sets; None = a private
coordinate, i.e. free at that parity) and its weight."""

import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
from parity import Echelon  # noqa: E402


def max_weight_common(elems, base0=(), base1=(), picks=()):
    """elems: dict key -> (v0, v1, w).  base_i: vectors fixed in the parity-i span.  picks: keys forced in.
    Returns (chosen keys sorted, total weight of chosen keys)."""
    bases = [Echelon(), Echelon()]
    for i, base in enumerate((base0, base1)):
        for v in base:
            bases[i].insert(v, 0)
    for s in picks:
        v0, v1, w = elems[s]
        for i, v in enumerate((v0, v1)):
            if v is not None and not bases[i].insert(v, 0):
                raise ValueError(f"pick {s} dependent at parity {i}")
    ground, vecs, weight = [], {}, {}
    for x, (v0, v1, w) in elems.items():
        if x in picks:
            continue
        vs = (v0, v1)
        if all(v is None or bases[i].reduce(v)[0] for i, v in enumerate(vs)):
            vecs[x] = vs
            weight[x] = w
            ground.append(x)
    inset = []
    while True:
        index = {x: k for k, x in enumerate(inset)}
        echs = []
        for i in (0, 1):
            e = Echelon(bases[i])
            for k, x in enumerate(inset):
                if vecs[x][i] is not None:
                    e.insert(vecs[x][i], 1 << k)
            echs.append(e)
        outside = [y for y in ground if y not in index]
        circ = {0: {}, 1: {}}
        free = {0: set(), 1: set()}
        for y in outside:
            for i in (0, 1):
                v = vecs[y][i]
                if v is None:
                    free[i].add(y)
                    continue
                r, combo = echs[i].reduce(v)
                if r:
                    free[i].add(y)
                else:
                    circ[i][y] = [inset[k] for k in range(len(inset)) if combo >> k & 1]
        succ = {}
        for y, c in circ[1].items():
            succ.setdefault(y, []).extend(c)
        for y, c in circ[0].items():
            for x in c:
                succ.setdefault(x, []).append(y)
        INF = (float("inf"), 0)
        dist, pred = {}, {}
        frontier = []
        for y in free[0]:
            dist[y] = (-weight[y], 0)
            pred[y] = None
            frontier.append(y)
        while frontier:
            nxt = set()
            for u in frontier:
                du = dist[u]
                for v in succ.get(u, ()):
                    dv = (du[0] + (weight[v] if v in index else -weight[v]), du[1] + 1)
                    if dv < dist.get(v, INF):
                        dist[v] = dv
                        pred[v] = u
                        nxt.add(v)
            frontier = list(nxt)
        ends = [y for y in free[1] if y in dist]
        if not ends:
            break
        best = min(ends, key=lambda y: dist[y])
        if dist[best][0] >= 0:
            break
        path, u = [], best
        while u is not None:
            path.append(u)
            u = pred[u]
        for u in path:
            if u in index:
                inset.remove(u)
            else:
                inset.append(u)
    chosen = sorted(set(inset) | set(picks), key=str)
    return chosen, sum(elems[x][2] for x in chosen)
