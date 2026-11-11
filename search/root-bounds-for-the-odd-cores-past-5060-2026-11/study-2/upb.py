#!/usr/bin/env python3
"""The union-block parity bound (UPB): the parity bound with every block's GF(2) matroid replaced by the union matroid
L' v L_int, where L' is the GF(2) matroid on the smooth coordinates of the block (smooth rows' vectors, fiber rows'
hub units, smooth columns' units) and L_int the one on the fiber coordinates (fiber rows' internal vectors, fiber
columns' units).  A set is independent in the union iff it splits into a hub-paying part (distinct hubs, jointly
independent with the smooth rows) and an internally independent part.  The union is represented over a large prime
field by stacking L' over L_int with a random scalar per (element, role) (generic stacking represents the union).

    python3 -I upb.py N [N ...]
"""

import json
import random
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board  # noqa: E402

Q = (1 << 61) - 1
SMOOTH = 23


class EchelonQ:
    """Sparse vectors over GF(Q) as dicts coord -> value, pivot on the largest coordinate; each pivot row carries the
    combination (dict tag -> coeff) of inserted vectors it is made of."""

    def __init__(self, base=None):
        self.piv = dict(base.piv) if base else {}

    def reduce(self, v):
        v = dict(v)
        combo = {}
        while v:
            p = max(v)
            row = self.piv.get(p)
            if row is None:
                return v, combo
            c = v[p]  # row's pivot value is 1
            for k, val in row[0].items():
                nv = (v.get(k, 0) - c * val) % Q
                if nv:
                    v[k] = nv
                else:
                    v.pop(k, None)
            for t, val in row[1].items():
                nc = (combo.get(t, 0) + c * val) % Q
                if nc:
                    combo[t] = nc
                else:
                    combo.pop(t, None)
        return v, combo

    def insert(self, v, tag):
        r, combo = self.reduce(v)
        if not r:
            return False
        p = max(r)
        inv = pow(r[p], Q - 2, Q)
        row = {k: val * inv % Q for k, val in r.items()}
        if tag is not None:
            combo = dict(combo)
            combo[tag] = (combo.get(tag, 0) - 1) % Q  # v = sum(combo) + r  =>  r = v - sum(combo)
        rc = {t: (-val * inv) % Q for t, val in combo.items()}
        self.piv[p] = (row, rc)
        return True


class UPB:
    def __init__(self, board, seed=1):
        self.b = board
        self.rng = random.Random(seed)
        n = board.n
        self.half = n // 2
        self.vec = {}  # (x, parity) -> dict or None

    def coord(self, f):
        """A coordinate: smooth numbers in the L' part, fiber numbers in the L_int part; ordered so that pivots are
        well defined (any total order works)."""
        return (0, f) if self.b.lp[f] <= SMOOTH else (1, f)

    def vector(self, x, i):
        key = (x, i)
        if key in self.vec:
            return self.vec[key]
        om, mf = self.b.om, self.b.mf
        if om[x] % 2 != i:  # the row vector in block Omega(x) - 1
            lam = self.rng.randrange(1, Q)
            v = {}
            for f in mf[x]:
                c = self.coord(f)
                v[c] = 1 if c[0] == 0 else lam
        elif x <= self.half:  # the unit vector in block Omega(x)
            c = self.coord(x)
            v = {c: 1 if c[0] == 0 else self.rng.randrange(1, Q)}
        else:
            v = None
        self.vec[key] = v
        return v

    def independent(self, members):
        """Is `members` independent at both parities in the union blocks?  Returns (ok, parity, element)."""
        for i in (0, 1):
            e = EchelonQ()
            for x in sorted(members, reverse=True):
                v = self.vector(x, i)
                if v is not None and not e.insert(v, None):
                    return False, i, x
        return True, None, None

    def bound(self, picks=(), bars=()):
        """Max weight common independent set of the two union-block matroids, sources fixed.  Returns (low, total)."""
        b = self.b
        n = b.n
        bases = [EchelonQ(), EchelonQ()]
        for s in b.g:
            for i in (0, 1):
                v = self.vector(s, i)
                if v is not None:
                    bases[i].insert(v, None)
        for s in sorted(picks):
            for i in (0, 1):
                v = self.vector(s, i)
                if v is not None and not bases[i].insert(v, None):
                    raise ValueError(f"pick {s} dependent at parity {i}")
        vecs, ground = {}, []
        for x in range(2, self.half + 1):
            if x in picks or x in bars:
                continue
            vs = [self.vector(x, i) for i in (0, 1)]
            if all(v is None or bases[i].reduce(v)[0] for i, v in enumerate(vs)):
                vecs[x] = vs
                ground.append(x)
        inset = []
        while True:
            index = {x: k for k, x in enumerate(inset)}
            echs = []
            for i in (0, 1):
                e = EchelonQ(bases[i])
                for x in inset:
                    if vecs[x][i] is not None:
                        e.insert(vecs[x][i], x)
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
                        circ[i][y] = [t for t in combo if t in index]
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
        return low, sum(b.g) + sum(low)


def main():
    for arg in sys.argv[1:]:
        n = int(arg)
        t0 = time.time()
        b = Board(n)
        opt = b.opt_line()["score"]
        low, pb = b.heaviest()
        h = set(b.g) | set(low)
        u = UPB(b)
        ok, par, x = u.independent(h)
        s = set(b.opt_line()["moves"])
        oks, _, xs = u.independent(s)
        print(json.dumps({"n": n, "opt": opt, "PB": pb, "gap": pb - opt, "H_union_independent": ok,
                          "H_fails_at": x, "S*_union_independent": oks, "S*_fails_at": xs,
                          "seconds": round(time.time() - t0, 1)}), flush=True)
        t0 = time.time()
        low2, ub = u.bound()
        print(json.dumps({"n": n, "UPB": ub, "UPB_gap": ub - opt, "share": round((pb - ub) / (pb - opt), 4),
                          "seconds": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    main()
