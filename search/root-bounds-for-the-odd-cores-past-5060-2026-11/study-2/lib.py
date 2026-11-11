#!/usr/bin/env python3
"""Helpers for the second study: layer instances, peel, cores, and the parity bound with picks and bars.

Builds on ../parity.py (the parity bound from the definitions) and reads results/optimal.jsonl.gz for S*.
"""

import json
import math
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P  # noqa: E402

SMOOTH_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23)


def largest_prime(x):
    p, lp = 2, 1
    while p * p <= x:
        if x % p == 0:
            lp = p
            while x % p == 0:
                x //= p
        p += 1
    if x > 1:
        lp = max(lp, x)
    return lp


class Board:
    def __init__(self, n):
        self.n = n
        self.om, self.mf = P.omega_and_mf(n)
        self.lp = [0] * (n + 1)
        for x in range(2, n + 1):
            self.lp[x] = largest_prime(x)
        self.g = P.greedy_basis(n, self.om, self.mf)
        self.gset = set(self.g)
        self._opt = None

    def opt_line(self):
        if self._opt is None:
            self._opt = P.results_line(self.n)
        return self._opt

    def smooth(self, x, bound=23):
        return self.lp[x] <= bound

    def layer_instance(self, members, k):
        """Rows: members of layer k; lists: maximal factors not in `members`.  Returns dict row -> set of columns."""
        mem = set(members)
        return {x: set(f for f in self.mf[x] if f not in mem) for x in members if self.om[x] == k}

    def heaviest(self, picks=(), bars=()):
        """The parity bound's heaviest set with picks forced in and bars out (numbers up to n/2).  Returns (I, total)."""
        return intersect_pb(self.n, self.om, self.mf, self.g, set(picks), set(bars))


def residual(lists, members=None):
    alive = set(lists if members is None else members)
    while True:
        count = {}
        for x in alive:
            for f in lists[x]:
                count[f] = count.get(f, 0) + 1
        drop = [x for x in alive if any(count[f] == 1 for f in lists[x])]
        if not drop:
            return alive
        alive -= set(drop)


def minimal_core(lists, start, order):
    core = set(residual(lists, start))
    if not core:
        return None
    for x in order:
        if x in core:
            trial = residual(lists, core - {x})
            if trial:
                core = set(trial)
    return core


def intersect_pb(n, om, mf, g, picks, bars):
    """Weighted matroid intersection over GF(2) as in parity.intersect, with picks forced in and bars out."""
    bases = []
    for i in (0, 1):
        b = P.Echelon()
        for s in g:
            v = P.parity_vector(s, i, n, om, mf)
            if v is not None:
                b.insert(v, 0)
        for s in sorted(picks):
            v = P.parity_vector(s, i, n, om, mf)
            if v is not None and not b.insert(v, 0):
                raise ValueError(f"pick {s} dependent at parity {i}")
        bases.append(b)
    vecs = {}
    ground = []
    for x in range(2, n // 2 + 1):
        if x in picks or x in bars:
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
    low = sorted(set(inset) | set(picks))
    return low, sum(g) + sum(low)


def classify(board, lists, x, bound=23):
    """'smooth', 'fiber' (a live internal column), or 'plug' (a fiber member listing only its hub or nothing)."""
    if board.smooth(x, bound):
        return "smooth"
    p = board.lp[x]
    internal = [f for f in lists[x] if f % p == 0]
    return "fiber" if internal else "plug"


def load_e1_leaf(n, B=23):
    for fn in ("e1/results.jsonl", "e1/small.jsonl"):
        for line in open("/home/brian/taxman_work/lab/work/oddcore/" + fn):
            d = json.loads(line)
            if d["n"] == n and d["B"] == B and d.get("leaf_promotions"):
                return d
    return None


def isqrt_T(n):
    return math.isqrt(n // 8)
