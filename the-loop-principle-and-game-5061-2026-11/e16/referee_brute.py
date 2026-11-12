#!/usr/bin/env python3
"""The referee's brute-force test of the gluing lemma on small regions, and its counterexamples.

Random states: a region R of a board n, a set W of cells, a set O of numbers off the region with n not in O and
S = O u W playable, and a set W' of cells of board n - 1.  The hypothesis is checked over every nonempty X of W' and Y
of W, and the conclusion (O u W' playable) whenever it holds.  Three modes:
  pool:     column-closed read in the pool of O u Z (column factors in Z or in O are not listed), the rows and R1 of a
            set counted only at hubs outside O; O may hold the layer-2 numbers qP_j up to n/2;
  original: column-closed read literally (every column factor outside Z), O holds no layer-2 number up to n/2, as F4
            and F10 give an optimal set from 187 on;
  literal:  column-closed read literally, with O free to hold the numbers qP_j: the generalized statement as written.
"""
import gzip
import json
import random
import sys
from collections import defaultdict
from itertools import combinations

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


def playable(T):
    """The core theorem: T is playable iff dismantling its own instance deletes every member."""
    T = set(T)
    lists = {x: MF[x] - T for x in T}
    count = defaultdict(int)
    for x in T:
        for f in lists[x]:
            count[f] += 1
    alive = set(T)
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


class Region:
    def __init__(self, n, R):
        self.n, self.R = n, list(R)
        self.cell = {}
        for P in R:
            for k in range(4, n // P + 1):
                if not is_prime(k):
                    self.cell[k * P] = (P, k)
        self.colf = {x: {x // q for q in prime_set(k)} for x, (P, k) in self.cell.items()}
        self.layer2 = {q * P for P in R for q in PRIMES if q * P <= n // 2 and q != P}

    def closed(self, X, Z, O, reading):
        for x in X:
            for f in self.colf[x]:
                if f in Z or (reading == "pool" and f in O):
                    continue
                if not any(f in MF[y] for y in X if y != x):
                    return False
        return True

    def signature(self, X, O, reading):
        cnt = defaultdict(int)
        for x in X:
            k = self.cell[x][1]
            if reading == "pool" and k in O:
                continue
            cnt[k] += 1
        return frozenset(cnt), frozenset(k for k, v in cnt.items() if v == 1)

    def hypothesis(self, W, Wp, O, reading):
        ys = []
        for r in range(1, len(W) + 1):
            for Y in combinations(sorted(W), r):
                if self.closed(Y, W, O, reading):
                    ys.append(self.signature(Y, O, reading))
        nx = 0
        for r in range(1, len(Wp) + 1):
            for X in combinations(sorted(Wp), r):
                if not self.closed(X, Wp, O, reading):
                    continue
                nx += 1
                rx, r1x = self.signature(X, O, reading)
                if not any(ry >= rx and r1y <= r1x for ry, r1y in ys):
                    return False, nx
        return True, nx


def random_trial(reg, rng, mode):
    n = reg.n
    cols = rng.sample(reg.R, rng.randint(1, min(3, len(reg.R))))
    grid = [x for x, (P, k) in reg.cell.items() if P in cols]
    rows = sorted(set(reg.cell[x][1] for x in grid))
    keep_rows = set(rng.sample(rows, rng.randint(1, min(5, len(rows)))))
    for k in list(keep_rows):
        for q in prime_set(k):
            if not is_prime(k // q) and rng.random() < 0.7:
                keep_rows.add(k // q)
    grid = [x for x in grid if reg.cell[x][1] in keep_rows]
    if not grid:
        return None
    W = set(rng.sample(grid, rng.randint(0, min(7, len(grid)))))
    gridp = [x for x in grid if x <= n - 1]
    if W and rng.random() < 0.6:
        Wp = {x for x in W if x <= n - 1 and rng.random() < 0.7}
        for x in W:
            same_row = [y for y in gridp if reg.cell[y][1] == reg.cell[x][1] and y != x]
            if same_row and rng.random() < 0.5:
                Wp.add(rng.choice(same_row))
        if not Wp:
            return None
    else:
        Wp = set(rng.sample(gridp, rng.randint(1, min(7, len(gridp))))) if gridp else set()
    hubs = sorted(keep_rows)
    pool = set(hubs)
    for h in hubs:
        for p in PRIMES[:6]:
            if p * h < n and p * h not in reg.cell:
                pool.add(p * h)
    for f in set().union(*(MF[h] for h in hubs)):
        pool.add(f)
    if mode != "original":
        for x in grid:
            pool |= {f for f in reg.colf[x] if f in reg.layer2}
    else:
        pool = {x for x in pool if not (layer(x) == 2 and 2 * x <= n)}
    pool.discard(n)
    pool -= set(reg.cell)
    pool = sorted(x for x in pool if x >= 2)
    O = set(rng.sample(pool, rng.randint(0, min(6, len(pool)))))
    if not playable(O | W):
        return None
    reading = "pool" if mode == "pool" else "literal"
    hyp, nx = reg.hypothesis(W, Wp, O, reading)
    return hyp, nx, playable(O | Wp), (sorted(O), sorted(W), sorted(Wp))


def counterexamples():
    out = []
    reg = Region(200, [11, 13])
    O, W, Wp = {22, 26}, set(), {44, 52}
    out.append(("literal reading, n = 200, R = {11, 13}, O = {22, 26}, W = {}, W' = {44, 52}",
                playable(O | W), reg.hypothesis(W, Wp, O, "literal"), reg.hypothesis(W, Wp, O, "pool"),
                playable(O | Wp)))
    with gzip.open(sys.argv[2], "rt") as fh:
        lines = [json.loads(line) for _, line in zip(range(191), fh)]
    opt = {d["n"]: d["score"] for d in lines}
    S = set(lines[190]["moves"])
    reg = Region(191, [11])
    W = {x for x in S if x in reg.cell}
    O = S - W
    out.append((f"n in O: n = 191, R = {{11}}, S the committed optimal set, W' = W = {sorted(W)}",
                playable(S), reg.hypothesis(W, W, O, "pool"), 191 in O, opt[190], opt[191],
                opt[190] + 191 - opt[191]))
    return out


def main():
    trials = int(sys.argv[1])
    for c in counterexamples():
        print("EXAMPLE", c, flush=True)
    rng = random.Random(16)
    boards = [(200, [11, 13, 17]), (252, [13, 17, 19]), (300, [13, 17, 19, 23]), (360, [17, 19, 23]),
              (440, [17, 19, 23]), (196, [7]), (243, [3]), (250, [5]), (338, [13])]
    for mode in ("pool", "original", "literal"):
        stats = defaultdict(int)
        first = None
        for t in range(trials):
            n, R = boards[t % len(boards)]
            res = random_trial(Region(n, R), rng, mode)
            if res is None:
                continue
            hyp, nx, concl, state = res
            stats["states"] += 1
            if hyp:
                stats["hypothesis holds"] += 1
                if nx:
                    stats["... with a closed X"] += 1
                    if not set(state[2]) <= set(state[1]):
                        stats["... and W' not in W"] += 1
                if nx and not concl:
                    stats["... COUNTEREXAMPLE"] += 1
                    if first is None:
                        first = (n, R, state)
            elif not concl:
                stats["hypothesis fails, conclusion fails"] += 1
        print(mode, dict(stats), "first counterexample:", first, flush=True)


if __name__ == "__main__":
    main()
