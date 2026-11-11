#!/usr/bin/env python3
"""Minimal odd cores inside the residual of the parity bound's heaviest set (for brief.md).

    python3 -I cores.py N [K]      # N a board, K the number of minimal cores to extract per layer (default 6)

For each layer instance whose residual is not empty, it extracts up to K minimal cores by a deletion filter (each run
starts from the residual less one member of each core found before, so the cores differ), and for each core reports its
members, its pool, the live-factor count of each member, the primes involved, the share of members with a prime above
T = floor(sqrt(n/8)) (the fibers of the exact problem of frame 2), the number of payment schemes onto each set of
factors of the core's size when it is small, and the integer determinant when the core is square.
"""

import json
import math
import sys
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P  # noqa: E402


def residual(members, lists):
    alive = set(members)
    while True:
        count = {}
        for x in alive:
            for f in lists[x]:
                count[f] = count.get(f, 0) + 1
        drop = [x for x in alive if any(count[f] == 1 for f in lists[x])]
        if not drop:
            return alive
        alive -= set(drop)


def minimal_core(start, lists, order):
    core = set(residual(start, lists))
    if not core:
        return None
    for x in order:
        if x in core:
            trial = residual(core - {x}, lists)
            if trial:
                core = set(trial)
    return core


def perm_count(rows, cols, lists):
    """Number of payment schemes of rows onto exactly the factors cols (|rows| == |cols|), by DP over columns."""
    idx = {c: i for i, c in enumerate(cols)}
    masks = [sum(1 << idx[f] for f in lists[r] if f in idx) for r in rows]
    dp = {0: 1}
    for m in masks:
        nd = {}
        for used, c in dp.items():
            avail = m & ~used
            while avail:
                b = avail & -avail
                nd[used | b] = nd.get(used | b, 0) + c
                avail ^= b
        dp = nd
    return sum(dp.values())


def det_int(rows, cols, lists):
    m = [[Fraction(1) if c in lists[r] else Fraction(0) for c in cols] for r in rows]
    k = len(m)
    d = Fraction(1)
    for i in range(k):
        p = next((r for r in range(i, k) if m[r][i] != 0), None)
        if p is None:
            return 0
        if p != i:
            m[i], m[p] = m[p], m[i]
            d = -d
        d *= m[i][i]
        for r in range(i + 1, k):
            if m[r][i]:
                f = m[r][i] / m[i][i]
                m[r] = [a - f * b for a, b in zip(m[r], m[i])]
    return int(d)


def primes_of(x):
    out, p = [], 2
    while p * p <= x:
        if x % p == 0:
            out.append(p)
            while x % p == 0:
                x //= p
        p += 1
    if x > 1:
        out.append(x)
    return out


def main():
    n = int(sys.argv[1])
    want = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    d = P.board(n)
    om, mf = P.omega_and_mf(n)
    h = set(d["greedy_basis"] + d["heaviest_low"])
    t = math.isqrt(n // 8)
    out = {"n": n, "gap": d.get("gap"), "T": t, "layers": {}}
    for k, r in d["residual"].items():
        k = int(k)
        layer = [x for x in h if om[x] == k]
        lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
        res = sorted(r["members"])
        fiber = sum(1 for x in res if max(primes_of(x)) > t)
        cores = []
        start = set(res)
        for j in range(want):
            order = sorted(start, key=lambda x: (-len(lists[x]), -x)) if j % 2 else sorted(start)
            c = minimal_core(start, lists, order)
            if not c:
                break
            pool = sorted(set().union(*(lists[x] for x in c)))
            deg = {}
            for x in c:
                deg[len(lists[x])] = deg.get(len(lists[x]), 0) + 1
            info = {"size": len(c), "pool": len(pool), "live_factor_counts": deg,
                    "primes": sorted(set(p for x in c for p in primes_of(x))),
                    "fiber_members": sum(1 for x in c if max(primes_of(x)) > t),
                    "members": sorted(c), "pool_list": pool}
            if len(c) == len(pool) and len(c) <= 40:
                info["det"] = det_int(sorted(c), pool, lists)
                info["schemes"] = perm_count(sorted(c), pool, lists)
            cores.append(info)
            start -= {min(c, key=lambda x: x)}  # remove the smallest member, so the next core differs
        out["layers"][k] = {"residual": len(res), "pool": len(r["pool"]), "fiber_members": fiber, "cores": cores}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
