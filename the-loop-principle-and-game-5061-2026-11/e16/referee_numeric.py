#!/usr/bin/env python3
"""Search for a numeric counterexample to the generalized statement read literally, with S only playable.

S = S*(n) + f - s: S*(n) the committed optimal set, f = qP_j a layer-2 column factor up to n/2 with P_j in R, s a
layer-2 source on the cycle that f closes in S*_2.  W' = (W - {n}) + {c}, c a cell with f as a maximal factor, not
in S, not a column factor of a cell of S, and no other cell of W' has f as a maximal factor.  Then no X holding c is
column-closed when read literally (f is outside Z and c alone lists it), and every other X is closed in W' iff it is
closed in W, so Y = X: the hypothesis holds.  A counterexample is an S that is playable with O + W' unplayable and
sum(O) + sum(W') > opt(n - 1), against the statement's conclusion opt(n - 1) >= sum(O) + sum(W').
"""
import gzip
import json
import sys
from collections import defaultdict

N = 2000
SPF = list(range(N + 1))
for i in range(2, int(N ** 0.5) + 1):
    if SPF[i] == i:
        for j in range(i * i, N + 1, i):
            if SPF[j] == j:
                SPF[j] = i
PRIMES = [p for p in range(2, N + 1) if SPF[p] == p]


def is_prime(x):
    return x >= 2 and SPF[x] == x


def prime_set(x):
    s = set()
    while x > 1:
        s.add(SPF[x])
        x //= SPF[x]
    return s


def layer(x):
    c = 0
    while x > 1:
        x //= SPF[x]
        c += 1
    return c


MF = [set()] + [{x // p for p in prime_set(x)} for x in range(1, N + 1)]


def layer_playable(T, k, n):
    """The layer theorem (F3): the layer instance of T at k, members T_k, pool layer k - 1 up to n/2 not in T."""
    members = [x for x in T if layer(x) == k]
    lists = {x: {f for f in MF[x] if f not in T} for x in members}
    count = defaultdict(int)
    for x in members:
        for f in lists[x]:
            count[f] += 1
    alive = set(members)
    changed = True
    while changed:
        changed = False
        for x in list(alive):
            if any(count[f] == 1 for f in lists[x]):
                alive.discard(x)
                for f in lists[x]:
                    count[f] -= 1
                changed = True
    return not alive


def playable(T, n):
    return all(layer_playable(T, k, n) for k in sorted(set(layer(x) for x in T)))


def tree_path(edges, a, b):
    """The edges on the path from a to b in a forest given as {number: (u, v)}."""
    adj = defaultdict(list)
    for x, (u, v) in edges.items():
        adj[u].append((v, x))
        adj[v].append((u, x))
    prev = {a: None}
    stack = [a]
    while stack:
        u = stack.pop()
        for v, x in adj[u]:
            if v not in prev:
                prev[v] = (u, x)
                stack.append(v)
    if b not in prev:
        return None
    path = []
    while b != a:
        u, x = prev[b]
        path.append(x)
        b = u
    return path


def ends(x):
    ps = sorted(prime_set(x))
    return (ps[0], ps[1]) if len(ps) == 2 else (ps[0], "g")


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    with gzip.open(sys.argv[3], "rt") as fh:
        lines = [json.loads(line) for _, line in zip(range(hi), fh)]
    opt = {d["n"]: d["score"] for d in lines}
    moves = {d["n"]: set(d["moves"]) for d in lines}
    found = 0
    for n in range(lo, hi + 1):
        R = [P for P in PRIMES if 2 * P * P > n and 4 * P <= n]
        cell = {k * P: (P, k) for P in R for k in range(4, n // P + 1) if not is_prime(k)}
        if n not in cell:
            continue
        Sstar = moves[n]
        S2 = {x: ends(x) for x in Sstar if layer(x) == 2}
        best = None
        for P in R:
            for q in PRIMES:
                f = q * P
                if 2 * f > n:
                    break
                if q == P or f in Sstar:
                    continue
                path = tree_path(S2, *ends(f))
                if not path:
                    continue
                for s in path:
                    S = (Sstar | {f}) - {s}
                    if not (layer_playable(S, 2, n) and layer_playable(S, 3, n)):
                        continue
                    W = {x for x in S if x in cell}
                    O = S - W
                    for p in PRIMES:
                        c = p * f
                        if c > n - 1:
                            break
                        if c in S or any(c * r in W for r in PRIMES if c * r <= n):
                            continue
                        Wp = (W - {n}) | {c}
                        if any(f in MF[y] for y in Wp if y != c):
                            continue
                        lhs = sum(O) + sum(Wp)
                        if lhs <= opt[n - 1]:
                            continue
                        if playable(O | Wp, n):
                            continue
                        excess = lhs - opt[n - 1]
                        if best is None or excess > best[0]:
                            best = (excess, f, s, c, sum(S), opt[n])
        if best:
            found += 1
            excess, f, s, c, sS, on = best
            print(f"n = {n}: S = S* + {f} - {s} (sum {sS}, opt(n) = {on}), W' = W - {{n}} + {{{c}}}: "
                  f"sum(O) + sum(W') exceeds opt(n - 1) = {opt[n - 1]} by {excess}", flush=True)
    print(f"{found} boards in {lo}..{hi} with a numeric counterexample")


if __name__ == "__main__":
    main()
