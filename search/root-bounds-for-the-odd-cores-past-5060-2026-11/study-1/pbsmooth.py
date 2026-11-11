#!/usr/bin/env python3
"""PB_smooth(n): the heaviest set independent at both parities (parity bound) whose B-smooth sub-instance of every layer
is playable.  Best-first branch and bound: a node is (picks, bars); its bound is the parity bound with them; if the
heaviest set's smooth sub-instances all peel, that set is the answer (every other open node has a lower bound).
Otherwise a minimal smooth core K (deletion filter) and the promoted columns its members list give the children:
child i bars the i-th of those numbers and picks the first i-1 (a partition).

    python3 -I pbsmooth.py N [B] [max_nodes]
"""
import heapq
import json
import math
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P  # noqa: E402
import cores as C  # noqa: E402


def smooth_flags(n, B):
    s = [True] * (n + 1)
    for x in range(2, n + 1):
        y = x
        for p in range(2, B + 1):
            while y % p == 0:
                y //= p
        s[x] = y == 1
    return s


def intersect(n, om, mf, g, picks, bars):
    """parity.py's intersect with picks (forced in, counted) and bars (excluded).  Returns (weight, inset) or None."""
    bases = []
    for i in (0, 1):
        b = P.Echelon()
        for s in g:
            v = P.parity_vector(s, i, n, om, mf)
            if v is not None:
                b.insert(v, 0)
        for x in picks:
            v = P.parity_vector(x, i, n, om, mf)
            if v is not None and not b.insert(v, 0):
                return None
        bases.append(b)
    vecs = {}
    ground = []
    for x in range(2, n // 2 + 1):
        if x in bars or x in picks:
            continue
        vs = [P.parity_vector(x, i, n, om, mf) for i in (0, 1)]
        if all(bases[i].reduce(vs[i])[0] for i in (0, 1)):
            vecs[x] = vs
            ground.append(x)
    inset = []
    while True:
        index = {x: k for k, x in enumerate(inset)}
        echs = []
        for i in (0, 1):
            e = P.Echelon(bases[i])
            for k, x in enumerate(inset):
                e.insert(vecs[x][i], 1 << k)
            echs.append(e)
        outside = [y for y in ground if y not in index]
        circ = {0: {}, 1: {}}
        free = {0: set(), 1: set()}
        for y in outside:
            for i in (0, 1):
                r, combo = echs[i].reduce(vecs[y][i])
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
            dist[y] = (-y, 0)
            pred[y] = None
            frontier.append(y)
        while frontier:
            nxt = set()
            for u in frontier:
                du = dist[u]
                for v in succ.get(u, ()):
                    dv = (du[0] + (v if v in index else -v), du[1] + 1)
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
    return sum(g) + sum(picks) + sum(inset), sorted(inset)


def smooth_conflict(h, n, om, mf, sm):
    """The first layer whose smooth sub-instance of h stalls: (free members of a minimal core, promoted columns it lists), or None."""
    hs = set(h)
    for k in sorted({om[x] for x in h}):
        layer = [x for x in h if om[x] == k and sm[x]]
        if not layer:
            continue
        lists = {x: set(f for f in mf[x] if f not in hs) for x in layer}
        res = C.residual(layer, lists)
        if not res:
            continue
        core = C.minimal_core(res, lists, sorted(res, key=lambda x: (-len(lists[x]), -x)))
        free = sorted(x for x in core if x <= n // 2)
        deleted = sorted({f for x in core for f in mf[x] if f in hs and f <= n // 2})
        return k, sorted(core), free, deleted
    return None


def main():
    n = int(sys.argv[1])
    B = int(sys.argv[2]) if len(sys.argv) > 2 else 23
    max_nodes = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    t0 = time.time()
    om, mf = P.omega_and_mf(n)
    sm = smooth_flags(n, B)
    g = P.greedy_basis(n, om, mf)
    root = intersect(n, om, mf, g, frozenset(), frozenset())
    pb = root[0]
    line = P.results_line(n)
    opt = line["score"] if line else None
    heap = [(-root[0], 0, frozenset(), frozenset(), root[1])]
    nodes = 1
    best_leaf = None
    log = []
    while heap:
        negw, _, picks, bars, inset = heapq.heappop(heap)
        w = -negw
        h = sorted(g) + sorted(picks) + inset
        conf = smooth_conflict(h, n, om, mf, sm)
        if conf is None:
            best_leaf = (w, picks, bars)
            break
        k, core, free, deleted = conf
        log.append({"bound": w, "layer": k, "core": len(core), "free": len(free), "deleted": len(deleted)})
        branch = free + deleted
        if not branch:
            continue  # the core is made of sources with no promoted column: unplayable whatever we do (should not happen)
        prev = []
        for i, x in enumerate(branch):
            nodes += 1
            child = intersect(n, om, mf, g, picks | frozenset(prev), bars | {x})
            if child is not None:
                heapq.heappush(heap, (-child[0], nodes, picks | frozenset(prev), bars | {x}, child[1]))
            prev.append(x)
        if nodes > max_nodes:
            break
    out = {"n": n, "B": B, "PB": pb, "opt": opt, "gap": pb - opt if opt else None, "nodes": nodes, "seconds": round(time.time() - t0, 1)}
    if best_leaf:
        out["PB_smooth"] = best_leaf[0]
        out["closed_share"] = round((pb - best_leaf[0]) / (pb - opt), 3) if opt and pb > opt else None
        out["picks"] = sorted(best_leaf[1])
        out["bars"] = sorted(best_leaf[2])
    else:
        out["PB_smooth"] = "not finished; best open bound %d" % (-heap[0][0] if heap else 0)
    out["conflicts_seen"] = log[:12]
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
