#!/usr/bin/env python3
"""The parity bound of game n, its heaviest set, and the odd cores that set runs into (for the brief in brief.md).

    python3 -I parity.py N [N ...]          # one JSON line a board on stdout

For each board n it computes, from the definitions of docs/theory/parity-bound.md only:

* G, the greedy basis of the sources' vectors v(s) over GF(2), taken by decreasing value (W3: every heaviest set
  independent at both parities holds exactly G among the sources);
* a heaviest set I of numbers up to n/2 independent at both parities together with G, by weighted matroid intersection
  (shortest augmenting paths, Schrijver, Theorem 41.7), so that the parity bound is sum(G) + sum(I);
* the residual of the own instance of H = G + I, layer by layer (the layer theorem F3), whose cores are all odd, and,
  if results/optimal.jsonl.gz has the game, its optimal set S* against H, layer by layer.

Pure Python, one thread.  It is slow past n of about 2500.
"""

import gzip
import json
import sys

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"


def omega_and_mf(n):
    """Omega(x) and the maximal factors of x, for x in 1..n."""
    spf = list(range(n + 1))
    p = 2
    while p * p <= n:
        if spf[p] == p:
            for q in range(p * p, n + 1, p):
                if spf[q] == q:
                    spf[q] = p
        p += 1
    om = [0] * (n + 1)
    mf = [[] for _ in range(n + 1)]
    for x in range(2, n + 1):
        om[x] = om[x // spf[x]] + 1
        primes, y = set(), x
        while y > 1:
            primes.add(spf[y])
            y //= spf[y]
        mf[x] = sorted(x // p for p in primes)
    return om, mf


def vec(factors):
    v = 0
    for f in factors:
        v |= 1 << f
    return v


class Echelon:
    """Vectors over GF(2) as ints, in echelon form by leading bit, each with the set of members it combines."""

    def __init__(self, base=None):
        self.piv = dict(base.piv) if base else {}

    def reduce(self, v):
        combo = 0
        while v:
            p = v.bit_length() - 1
            e = self.piv.get(p)
            if e is None:
                return v, combo
            v ^= e[0]
            combo ^= e[1]
        return 0, combo

    def insert(self, v, tag):
        r, combo = self.reduce(v)
        if r == 0:
            return False
        self.piv[r.bit_length() - 1] = (r, combo ^ tag)
        return True


def greedy_basis(n, om, mf):
    ech = Echelon()
    kept = []
    for s in range(n, n // 2, -1):
        if ech.insert(vec(mf[s]), 0):
            kept.append(s)
    return kept


def parity_vector(x, i, n, om, mf):
    """The parity-i vector of x on the coordinates 1..n/2, or None for an extra coordinate."""
    if om[x] % 2 != i:
        return vec(mf[x])
    if x <= n // 2:
        return 1 << x
    return None


def intersect(n, om, mf, g):
    """A heaviest set of numbers 2..n/2 independent at both parities together with G (weighted matroid intersection)."""
    bases = []
    for i in (0, 1):
        b = Echelon()
        for s in g:
            v = parity_vector(s, i, n, om, mf)
            if v is not None:
                b.insert(v, 0)
        bases.append(b)
    vecs = {}
    ground = []
    for x in range(2, n // 2 + 1):
        vs = [parity_vector(x, i, n, om, mf) for i in (0, 1)]
        if all(bases[i].reduce(vs[i])[0] for i in (0, 1)):  # not a loop of either contracted matroid
            vecs[x] = vs
            ground.append(x)
    inset = []
    total = 0
    while True:
        index = {x: k for k, x in enumerate(inset)}
        echs = []
        for i in (0, 1):
            e = Echelon(bases[i])
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
        # Arcs: y outside -> x inside when I - x + y is independent in M1 (x in y's circuit of M1);
        #       x inside -> y outside when I - x + y is independent in M0 (x in y's circuit of M0).
        # Paths run from free[0] to free[1]; length: +w inside, -w outside, then fewest arcs.
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
        total -= dist[best][0]
    return sorted(inset), ground


def layer_residual(members, n, om, mf):
    """Dismantle the own instance of `members`, layer by layer: the residual's members and pool, by layer."""
    mem = set(members)
    out = {}
    for k in sorted({om[x] for x in members}):
        layer = [x for x in members if om[x] == k]
        lists = {x: set(f for f in mf[x] if f not in mem) for x in layer}
        alive = set(layer)
        changed = True
        while changed:
            changed = False
            count = {}
            for x in alive:
                for f in lists[x]:
                    count[f] = count.get(f, 0) + 1
            for x in list(alive):
                if any(count[f] == 1 for f in lists[x]):
                    alive.discard(x)
                    changed = True
        if alive:
            pool = set().union(*(lists[x] for x in alive))
            wide = sum(len(lists[x]) >= 3 for x in alive)
            out[k] = {"members": sorted(alive), "pool": sorted(pool), "wide": wide}
    return out


def results_line(n):
    with gzip.open(RESULTS, "rt") as f:
        for i, text in enumerate(f, start=1):
            if i == n:
                x = json.loads(text)
                assert x["n"] == n
                return x
    return None


def board(n):
    om, mf = omega_and_mf(n)
    g = greedy_basis(n, om, mf)
    inset, ground = intersect(n, om, mf, g)
    h = sorted(g + inset)
    out = {"n": n, "bound": sum(h), "sum_g": sum(g), "sum_i": sum(inset), "size_i": len(inset),
           "ground": len(ground), "heaviest_low": inset, "greedy_basis": g}
    out["residual"] = {str(k): v for k, v in layer_residual(h, n, om, mf).items()}
    line = results_line(n)
    if line:
        s = set(line["moves"])
        out["opt"] = line["score"]
        out["gap"] = out["bound"] - line["score"]
        hs = set(h)
        by_layer = {}
        for k in sorted({om[x] for x in hs | s}):
            hk = {x for x in hs if om[x] == k}
            sk = {x for x in s if om[x] == k}
            if hk != sk:
                by_layer[str(k)] = {"only_bound": sorted(hk - sk), "only_opt": sorted(sk - hk),
                                    "excess": sum(hk) - sum(sk)}
        out["against_opt"] = by_layer
        out["opt_residual_empty"] = not layer_residual(sorted(s), n, om, mf)
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(json.dumps(board(int(arg))), flush=True)
