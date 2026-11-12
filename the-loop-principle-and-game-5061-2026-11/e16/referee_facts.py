#!/usr/bin/env python3
"""The referee's check of the gluing lemma's three facts, for 187 <= n <= 10,000.

Two forms:
* the region form: R = every prime P with 2P^2 > n and 4P <= n (the facts for a sub-region follow, since each check
  below is about one column, or rules out a coincidence between two);
* the clean form: n = cP with P prime, the window every prime P_j <= P with (c + 1)P_j > n and 4P_j <= n.

The cells are the numbers kP_j <= n with k composite.  For each cell x = kP_j it checks:
  F2: mf(x) = column factors {x/q : q | k} together with the hub k, the hub is no column factor, no cell and no
      multiple of a region prime, and P_j divides x once and is the only region prime dividing x;
  F1: every y <= n with a column factor f in mf(y) is a cell of f's column, and f has one column; a prime row's
      column factor lies in layer 2 and is at most n/2, a composite row's is a cell of the column;
  F3: every y <= n with x in mf(y) is a cell of x's column;
  H:  the cells that have a hub h as a maximal factor are exactly the cells of row h.
For the clean form it records the windows that break a check and the reason.
"""
import sys
from collections import defaultdict

N = 10000
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


def mf(x):
    return {x // p for p in prime_set(x)}


def check(n, region):
    """Return the list of failed checks for the cells of `region` on board n."""
    fails = []
    cells = {}
    for P in region:
        for k in range(4, n // P + 1):
            if not is_prime(k):
                x = k * P
                if x in cells:
                    fails.append(("cell in two columns", x))
                cells[x] = (P, k)
    rows = defaultdict(set)
    for x, (P, k) in cells.items():
        rows[k].add(x)
    listers = defaultdict(set)
    colf = defaultdict(set)
    for x, (P, k) in cells.items():
        for g in mf(x):
            listers[g].add(x)
        if (x // P) % P == 0:
            fails.append(("P^2 divides a cell", x))
        if sum(1 for Q in region if x % Q == 0) != 1:
            fails.append(("two region primes divide a cell", x))
        cf = {x // q for q in prime_set(k)}
        if mf(x) != cf | {k}:
            fails.append(("mf is not column factors and hub", x))
        if k in cf:
            fails.append(("hub is a column factor", x))
        if k in cells:
            fails.append(("hub is a cell", x))
        if any(k % Q == 0 for Q in region):
            fails.append(("hub is a multiple of a region prime", x))
        for f in cf:
            colf[f].add(P)
            m = f // P
            if f % P:
                fails.append(("column factor off its column", x))
            elif is_prime(m):
                if layer(f) != 2 or 2 * f > n:
                    fails.append(("prime-row column factor not layer 2 up to n/2", x))
            elif cells.get(f, (None,))[0] != P:
                fails.append(("composite-row column factor not a cell of its column", x))
        for p in PRIMES:
            y = p * x
            if y > n:
                break
            if cells.get(y, (None,))[0] != P:
                fails.append(("a non-cell lists a cell", x))
    for f, cols in colf.items():
        if len(cols) != 1:
            fails.append(("column factor in two columns", f))
        P = min(cols)
        for p in PRIMES:
            y = p * f
            if y > n:
                break
            if cells.get(y, (None,))[0] != P:
                fails.append(("a column factor is listed off its column", f))
    for h, members in rows.items():
        if listers[h] != members:
            fails.append(("hub listed by cells of other rows", h))
    return fails


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    region_bad = 0
    region_count = 0
    clean_count = 0
    clean_not_region = []
    clean_bad = defaultdict(list)
    for n in range(lo, hi + 1):
        region = [P for P in PRIMES if 2 * P * P > n and 4 * P <= n]
        region_count += 1
        f = check(n, region)
        if f:
            region_bad += 1
            print("REGION FAIL", n, sorted(set(r for r, _ in f)), flush=True)
        for P in prime_set(n):
            c = n // P
            window = [Q for Q in PRIMES if Q <= P and (c + 1) * Q > n and 4 * Q <= n]
            if not window:
                continue
            clean_count += 1
            if any(2 * Q * Q <= n for Q in window):
                clean_not_region.append((n, P, c, tuple(window)))
            f = check(n, window)
            for reason in sorted(set(r for r, _ in f)):
                clean_bad[reason].append((n, P, c, len(window)))
    print(f"region form: {region_count} boards, {region_bad} with a failed check")
    print(f"clean form: {clean_count} windows; {len(clean_not_region)} hold a prime with 2P^2 <= n")
    if clean_not_region:
        sizes = sorted(set(len(w) for _, _, _, w in clean_not_region))
        cmin = min(c / P for _, P, c, _ in clean_not_region)
        print(f"  those windows have sizes {sizes}, and c/P >= {cmin:.3f}; first {clean_not_region[:3]}")
    for reason, lst in sorted(clean_bad.items()):
        print(f"  clean windows failing '{reason}': {len(lst)}, first {lst[:3]}, max window size "
              f"{max(w for *_, w in lst)}")


if __name__ == "__main__":
    main()
