#!/usr/bin/env python3
"""Study H1 of the unsound mode: the Franklin-Moniot upper bound on opt(n), for every n up to a limit.

    python3 -I fm_bound.py --limit 5160 --out fm_bound.json [--committed fm_bound_2000.json]

The bound of game n is the weight of a maximum-weight matching of the graph on 1..n with an edge (d, c), of weight c,
for every c in 2..n and every maximal factor d of c (c / d is prime), as heuristics/evaluation/bound.py defines it.
That program calls networkx, which is not installed here, and a blossom matching of 5,000 vertices for each of 600
games takes too long.  This script computes the same numbers another way.  The graph is bipartite (the two ends of an
edge differ by one prime factor, so their numbers of prime factors differ in parity), and game n adds to game n - 1 the
one vertex n, so the script keeps a maximum-weight matching and its dual and mends both with one search for each n.

The dual gives each vertex v a number y[v] >= 0 with y[d] + y[c] >= c on every edge, and y[v] = 0 on every vertex the
matching leaves out.  The matching's weight equals the sum of the y, which proves that the matching is a maximum and
the bound is exact.  The script checks all of this for every n, and compares the bounds with a file of
heuristics/results/ (`--committed`, which has them for 2..2000) where it has them.

The search for n starts at the new vertex v, which gets the smallest y that makes its edges feasible, and looks for
the cheapest way to repair the matching: a shortest path over the alternating paths from v (an unmatched edge costs its
slack y[d] + y[c] - c, a matched edge nothing), to an unmatched vertex of the other side, or to a vertex of v's side
whose y would reach 0.  The y of the vertices the search reached move by their distance, and the matching flips along
the path.
"""

import argparse
import heapq
import json
import sys

INF = float("inf")


def prime_factor_counts(limit):
    """Omega(n), the prime factors of n with multiplicity, and the distinct primes of n, for n up to limit."""
    omega = [0] * (limit + 1)
    primes = [[] for _ in range(limit + 1)]
    for p in range(2, limit + 1):
        if primes[p]:
            continue
        power = p
        while power <= limit:
            for m in range(power, limit + 1, power):
                omega[m] += 1
            power *= p
        for m in range(p, limit + 1, p):
            primes[m].append(p)
    return omega, primes


def bounds(limit):
    """The bound of every game 2..limit, {n: bound}, with the checks of the matching and its dual at every n."""
    omega, primes = prime_factor_counts(limit)
    side = [o % 2 for o in omega]
    y = [0] * (limit + 1)
    mate = [0] * (limit + 1)
    adjacent = [[] for _ in range(limit + 1)]
    edges = []  # (d, c) of every edge so far
    result = {}
    for v in range(2, limit + 1):
        factors = [v // p for p in primes[v]]
        for d in factors:
            adjacent[v].append(d)
            adjacent[d].append(v)
            edges.append((d, v))
        y[v] = max(0, max(v - y[d] for d in factors))
        repair(v, y, mate, adjacent, side)
        result[v] = check(v, y, mate, edges)
    return result


def repair(v, y, mate, adjacent, side):
    """Mends the matching and its dual after the vertex v, the largest, joined the graph with y[v] set."""
    dist = {v: 0}
    pred = {}
    settled = {}
    heap = [(0, v)]
    best = (INF, None, None)
    while heap and heap[0][0] < best[0]:
        d, u = heapq.heappop(heap)
        if u in settled:
            continue
        settled[u] = d
        if side[u] == side[v]:  # on the side of v: its y may fall until it is 0
            if y[u] + d < best[0]:
                best = (y[u] + d, "zero", u)
            for x in adjacent[u]:
                if x not in settled:
                    nd = d + y[u] + y[x] - max(u, x)
                    if nd < dist.get(x, INF):
                        dist[x] = nd
                        pred[x] = u
                        heapq.heappush(heap, (nd, x))
        elif mate[u] == 0:  # on the other side and free: an augmenting path ends here
            if d < best[0]:
                best = (d, "augment", u)
        else:  # matched: the walk goes on through its mate at no cost
            partner = mate[u]
            if partner not in settled and d < dist.get(partner, INF):
                dist[partner] = d
                pred[partner] = u
                heapq.heappush(heap, (d, partner))
    total, kind, end = best
    for u, d in settled.items():
        if d < total:
            y[u] += (total - d) * (-1 if side[u] == side[v] else 1)
    cur = end if kind == "augment" else (pred[end] if end != v else None)
    if kind == "zero" and end != v:
        mate[end] = 0
    while cur is not None:
        u = pred[cur]
        before = mate[u]
        mate[cur], mate[u] = u, cur
        if u == v:
            break
        cur = before


def check(n, y, mate, edges):
    """The bound of game n, after checking the matching and its dual: the y are not negative and feasible on every
    edge, a vertex the matching leaves out has y = 0, and the matching's weight is the sum of the y."""
    for d, c in edges:
        if y[d] + y[c] < c:
            raise AssertionError(f"n={n}: the edge ({d}, {c}) is infeasible")
    weight = 0
    for u in range(1, n + 1):
        if y[u] < 0:
            raise AssertionError(f"n={n}: y[{u}] is negative")
        if mate[u] == 0 and y[u] != 0:
            raise AssertionError(f"n={n}: the free vertex {u} has y {y[u]}")
        if mate[u] and mate[mate[u]] != u:
            raise AssertionError(f"n={n}: the matching is not symmetric at {u}")
        if mate[u] > u:
            weight += mate[u]
    if weight != sum(y[1:n + 1]):
        raise AssertionError(f"n={n}: the matching weighs {weight} and the dual {sum(y[1:n + 1])}")
    return weight


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--committed", help="a JSON object {n: bound} to compare with")
    args = parser.parse_args()
    result = bounds(args.limit)
    with open(args.out, "w") as f:
        json.dump(result, f, separators=(",", ":"))
    print(f"wrote the bounds of 2..{args.limit} to {args.out}")
    if args.committed:
        with open(args.committed) as f:
            known = {int(n): b for n, b in json.load(f).items()}
        differ = [n for n in known if n in result and known[n] != result[n]]
        shown = ": " + str(differ[:10]) if differ else ""
        print(f"compared with {len(known)} bounds of {args.committed}: {len(differ)} differ{shown}")
        if differ:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
