#!/usr/bin/env python3
"""Random check of the two cases of Theorem 8P in the frame model: for random maximal promotion sets L of n = 8P,
if 4P in L then U*(n-1) + (L - 4P) + 4P1 is playable on n-1, else U*(n-1) + L is.
    nice -n 19 python3 -I study/eightp_cases.py SAMPLES N [N ...]"""
import os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
from promsets_full import random_maximal  # noqa: E402
spf = exch.spf

def run(n, samples, rng):
    P = n // 8; P1 = prev_prime(P)
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    assert u1 == (u0 - {4 * P}) | {n}
    c1 = [y for y in range(2, n // 2 + 1) if common.playable(u1 | {y}, n, spf)]
    a = b = fail = 0
    for _ in range(samples):
        L = set(random_maximal(u1, c1, n, rng))
        if 4 * P in L:
            a += 1
            assert 4 * P1 not in L and 8 * P1 in u0
            ok = common.playable(u0 | (L - {4 * P}) | {4 * P1}, n - 1, spf)
        else:
            b += 1
            ok = common.playable(u0 | L, n - 1, spf)
        if not ok:
            fail += 1
            print("   FAIL", sorted(L))
    print(f"{n} = 8*{P}: case A (4P out) {b}, case B (4P in) {a}, failures {fail}")
    sys.stdout.flush()

if __name__ == "__main__":
    rng = random.Random(5)
    for x in sys.argv[2:]: run(int(x), int(sys.argv[1]), rng)
