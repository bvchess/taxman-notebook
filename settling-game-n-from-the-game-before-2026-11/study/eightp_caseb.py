#!/usr/bin/env python3
"""Theorem 8P, case B forced: random maximal promotion sets of n = 8P that contain 4P (4P added first), then the
check that U*(n-1) + (L - 4P) + 4P1 is playable on n - 1.   nice -n 19 python3 -I study/eightp_caseb.py SAMPLES N..."""
import os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
spf = exch.spf

def run(n, samples, rng):
    P = n // 8; P1 = prev_prime(P)
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    c1 = [y for y in range(2, n // 2 + 1) if y != 4 * P and common.playable(u1 | {4 * P, y}, n, spf)]
    fail = 0
    for _ in range(samples):
        order = list(c1); rng.shuffle(order)
        cur = u1 | {4 * P}; L = {4 * P}
        for c in order:
            cur.add(c)
            if common.playable(cur, n, spf): L.add(c)
            else: cur.discard(c)
        assert 4 * P1 not in L
        if not common.playable(u0 | (L - {4 * P}) | {4 * P1}, n - 1, spf):
            fail += 1; print("   FAIL", sorted(L))
    print(f"{n} = 8*{P}: case B samples {samples}, |L| ~ {len(L)}, failures {fail}"); sys.stdout.flush()

if __name__ == "__main__":
    rng = random.Random(7)
    for x in sys.argv[2:]: run(int(x), int(sys.argv[1]), rng)
