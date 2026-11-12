#!/usr/bin/env python3
"""Referee's check of Theorem A against the chain: the greedy basis G(m) of every board m <= N from scratch, the
recurrence G(n) = G(n-1) + n or G(n-1) - x_G + n for odd n, and PB(n) - PB(n-1) = n - x_G at every exchange, with PB
read from settle.csv's `bound` column.  Standard library only.
    nice -n 19 python3 -I check_a.py [N]"""
import csv
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5060
SETTLE = "/home/brian/taxman_work/lab/work/succession/settle.csv"

spf = list(range(N + 1))
for p in range(2, int(N ** 0.5) + 1):
    if spf[p] == p:
        for m in range(p * p, N + 1, p):
            if spf[m] == m:
                spf[m] = p


def primes_of(x):
    out = []
    while x > 1:
        p = spf[x]
        out.append(p)
        while x % p == 0:
            x //= p
    return out


def omega(x):
    c = 0
    while x > 1:
        x //= spf[x]
        c += 1
    return c


def vec(x):
    """v(x) as a bitset over the coordinates 1..: a 1 at each maximal factor x/p."""
    v = 0
    for p in primes_of(x):
        v |= 1 << (x // p)
    return v


OMEGA = [0] * (N + 1)
VEC = [0] * (N + 1)
for x in range(1, N + 1):
    OMEGA[x] = omega(x)
    VEC[x] = vec(x)


def greedy_basis(m):
    """G(m): sources taken from m down, kept when v is outside the span of the kept.  Returns (kept list, pivots),
    pivots a dict lowbit -> (row, combo) with combo a bitset over the kept sources (bit s) that sum to row."""
    pivots = {}
    kept = []
    for s in range(m, m // 2, -1):
        v, combo = VEC[s], 0
        while v:
            low = v & -v
            if low in pivots:
                r, c = pivots[low]
                v ^= r
                combo ^= c
            else:
                pivots[low] = (v, combo | (1 << s))
                kept.append(s)
                break
    return kept, pivots


def represent(pivots, v):
    """The subset of the kept sources whose vectors sum to v, as a bitset, or None if v is outside the span."""
    combo = 0
    while v:
        low = v & -v
        if low not in pivots:
            return None
        r, c = pivots[low]
        v ^= r
        combo ^= c
    return combo


def main():
    rows = {int(r["n"]): r for r in csv.DictReader(open(SETTLE))}
    PB = {n: int(r["bound"]) for n, r in rows.items() if r["bound"] != ""}

    prev_kept, prev_piv = greedy_basis(2)
    bad = []
    counts = {"restrict": 0, "exchange": 0, "relax": 0, "half-out": 0}
    mismatch_step = []
    for n in range(3, N + 1):
        kept, piv = greedy_basis(n)
        G = set(kept)
        Gp = set(prev_kept)
        if n % 2 == 1:
            combo = represent(prev_piv, VEC[n])
            if combo is None:
                kind = "restrict"
                want = Gp | {n}
                xG = None
            else:
                C = [s for s in range(n) if combo >> s & 1]
                xG = min(C)
                kind = "exchange"
                want = (Gp - {xG}) | {n}
                # every member of C has n's layer
                if any(OMEGA[c] != OMEGA[n] for c in C):
                    bad.append(("layer", n, C))
            if G != want:
                bad.append(("G", n, kind, sorted(G ^ want)))
            if xG is not None and n in PB and n - 1 in PB and PB[n] - PB[n - 1] != n - xG:
                bad.append(("PB", n, PB[n] - PB[n - 1], n - xG))
            if kind == "restrict" and n in PB and n - 1 in PB and not (0 <= PB[n - 1] + n - PB[n]):
                bad.append(("PBrestrict", n))
        else:
            s = n // 2
            if s in Gp:
                kind = "relax"
                want = (Gp - {s}) | {n}
                if n in PB and n - 1 in PB and not (0 <= PB[n - 1] + n - PB[n] <= s):
                    bad.append(("PBrelax", n, PB[n - 1] + n - PB[n], s))
            else:
                kind = "half-out"
                want = Gp | {n}
                if n in PB and n - 1 in PB and PB[n] - PB[n - 1] != n:
                    bad.append(("PBhalf", n, PB[n] - PB[n - 1]))
            if G != want:
                bad.append(("G", n, kind, sorted(G ^ want)))
        counts[kind] += 1
        step = rows.get(n, {}).get("step")
        if step and step != "prime" and step != kind:
            mismatch_step.append((n, step, kind))
        prev_kept, prev_piv = kept, piv

    print("boards 3..%d, kinds by v(n) in V / s in G(n-1):" % N, counts)
    print("mismatches with settle.csv's step column (n, settle, mine):", mismatch_step[:30], "count", len(mismatch_step))
    print("failures:", bad[:30], "count", len(bad))


if __name__ == "__main__":
    main()
