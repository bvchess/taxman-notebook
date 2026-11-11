#!/usr/bin/env python3
"""Is every promotion set of n one of n - 1 across an exchange, and the other way round?  A random test.

    nice -n 19 python3 -I study/promsets.py SAMPLES N [N ...]

Only the layer-k instance changes across an odd exchange (k the layer of n), so the test is on that instance alone:
members A = U*_k(n-1) or A' = U*_k(n) = A - x + n, plus a set L of layer-k numbers up to n/2; the pool is every
layer-(k-1) number up to n/2 (no layer-2 number up to n/2 is ever promoted from 187 on, so for k = 3 the pool is
exact).  A random maximal L is built on one board (add candidates in random order while playable), then tested on
the other board.  Reports the sets that are playable on one board only.
"""

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import common  # noqa: E402
import exch  # noqa: E402

spf = exch.spf


def random_maximal(base, cands, n, rng):
    order = list(cands)
    rng.shuffle(order)
    cur = set(base)
    L = []
    for c in order:
        cur.add(c)
        if common.playable(cur, n, spf):
            L.append(c)
        else:
            cur.discard(c)
    return L


def test(n, samples, rng):
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    gained, lost = sorted(u1 - u0), sorted(u0 - u1)
    if gained != [n] or len(lost) != 1:
        print(f"{n}: not a one-for-one exchange ({gained}, {lost})")
        return
    x = lost[0]
    k = exch.omega(n)
    A = exch.layer_part(u0, k)
    A1 = exch.layer_part(u1, k)
    assert A1 == (A - {x}) | {n}
    nums_k = [y for y in range(2, n // 2 + 1) if exch.omega(y) == k]
    c0 = [y for y in nums_k if common.playable(A | {y}, n, spf)]
    c1 = [y for y in nums_k if common.playable(A1 | {y}, n, spf)]
    bad01 = bad10 = 0
    sizes = []
    examples = []
    for _ in range(samples):
        L = random_maximal(A1, c1, n, rng)
        sizes.append(len(L))
        if not common.playable(A | set(L), n, spf):
            bad10 += 1
            if len(examples) < 3:
                examples.append(("n-only", sorted(L)))
        L = random_maximal(A, c0, n, rng)
        if not common.playable(A1 | set(L), n, spf):
            bad01 += 1
            if len(examples) < 3:
                examples.append(("n-1-only", sorted(L)))
    print(f"{n} = {exch.fac_str(n)}, x = {x} = {exch.fac_str(x)}: candidates {len(c0)} / {len(c1)} "
          f"(same? {c0 == c1}); maximal L size median {sorted(sizes)[len(sizes) // 2]}; "
          f"sets of n unplayable with U*(n-1): {bad10} / {samples}; sets of n-1 unplayable with U*(n): {bad01} / {samples}")
    for kind, L in examples:
        print(f"   example ({kind}): {L}")
    sys.stdout.flush()


if __name__ == "__main__":
    rng = random.Random(1)
    samples = int(sys.argv[1])
    for arg in sys.argv[2:]:
        test(int(arg), samples, rng)
