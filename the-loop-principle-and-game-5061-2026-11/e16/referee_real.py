#!/usr/bin/env python3
"""The referee's test of the original form on the committed optimal sets.

For each board n = cP (P prime, c composite, 4 <= c <= CMAX) with 187 <= n <= HI, the clean window is every prime in
(n/(c + 1), P].  S is the committed optimal set of n, W its cells and O the rest.  When the window has at most MAXC
cells on board n - 1, every set W' of them is tried: whenever the lemma's hypothesis holds (column-closed read
literally, rows and R1 by occupancy, as in the original form), O u W' must be playable.  Counts the W' with the
hypothesis, and any counterexample.
"""
import gzip
import json
import sys
from collections import defaultdict
from itertools import combinations

N = 6000
SPF = list(range(N + 1))
for i in range(2, int(N ** 0.5) + 1):
    if SPF[i] == i:
        for j in range(i * i, N + 1, i):
            if SPF[j] == j:
                SPF[j] = i
PRIMES = [p for p in range(2, N + 1) if SPF[p] == p]
LAYER = [0, 0] + [0] * (N - 1)
for x in range(2, N + 1):
    LAYER[x] = LAYER[x // SPF[x]] + 1


def is_prime(x):
    return x >= 2 and SPF[x] == x


def prime_set(x):
    s = set()
    while x > 1:
        s.add(SPF[x])
        x //= SPF[x]
    return s


MF = [set()] + [{x // p for p in prime_set(x)} for x in range(1, N + 1)]


def layer_playable(T, members):
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


def playable_near(T, layers):
    """T is playable, given that its layer instances off `layers` are those of a playable set (F3)."""
    by_layer = defaultdict(list)
    for x in T:
        if LAYER[x] in layers:
            by_layer[LAYER[x]].append(x)
    return all(layer_playable(T, by_layer[k]) for k in layers)


def main():
    hi, cmax, maxc = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    with gzip.open(sys.argv[4], "rt") as fh:
        lines = [json.loads(line) for _, line in zip(range(hi), fh)]
    moves = {d["n"]: set(d["moves"]) for d in lines}
    stats = defaultdict(int)
    for n in range(187, hi + 1):
        S = moves[n]
        assert not any(LAYER[x] == 2 and 2 * x <= n for x in S), n
        for P in prime_set(n):
            c = n // P
            if c > cmax or c < 4 or is_prime(c):
                continue
            window = [Q for Q in PRIMES if Q <= P and (c + 1) * Q > n]
            cell = {k * Q: (Q, k) for Q in window for k in range(4, n // Q + 1) if not is_prime(k)}
            cellsp = sorted(x for x in cell if x <= n - 1)
            if len(cellsp) > maxc:
                stats["windows skipped (too many cells)"] += 1
                continue
            stats["windows"] += 1
            W = {x for x in S if x in cell}
            O = S - W
            colf = {x: {x // q for q in prime_set(k)} for x, (Q, k) in cell.items()}
            layers = set()
            for x in cell:
                layers |= {LAYER[x], LAYER[x] + 1}

            def closed(X, Z):
                return all(f in Z or any(f in MF[y] for y in X if y != x) for x in X for f in colf[x])

            def sig(X):
                cnt = defaultdict(int)
                for x in X:
                    cnt[cell[x][1]] += 1
                return frozenset(cnt), frozenset(k for k, v in cnt.items() if v == 1)

            ys = [sig(Y) for r in range(1, len(W) + 1) for Y in combinations(sorted(W), r) if closed(Y, W)]
            for r in range(len(cellsp) + 1):
                for Wp in combinations(cellsp, r):
                    Wp = set(Wp)
                    ok = True
                    nx = 0
                    for rx in range(1, len(Wp) + 1):
                        for X in combinations(sorted(Wp), rx):
                            if closed(X, Wp):
                                nx += 1
                                a, b = sig(X)
                                if not any(ry >= a and r1 <= b for ry, r1 in ys):
                                    ok = False
                                    break
                        if not ok:
                            break
                    if not ok:
                        continue
                    stats["W' with the hypothesis"] += 1
                    if nx and not Wp <= W:
                        stats["... non-trivial (a closed X, W' not in W)"] += 1
                    if not playable_near(O | Wp, layers):
                        stats["COUNTEREXAMPLE"] += 1
                        print("COUNTEREXAMPLE", n, P, c, sorted(W), sorted(Wp), flush=True)
    print(dict(stats))


if __name__ == "__main__":
    main()
