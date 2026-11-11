#!/usr/bin/env python3
"""promsets.py with the whole board's playability (U* of each board plus L on its own board), so every set tested is
a promotion set in the full sense.  Usage: nice -n 19 python3 -I study/promsets_full.py SAMPLES N [N ...]"""
import os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
spf = exch.spf

def random_maximal(base, cands, board, rng):
    order = list(cands); rng.shuffle(order); cur = set(base); L = []
    for c in order:
        cur.add(c)
        if common.playable(cur, board, spf): L.append(c)
        else: cur.discard(c)
    return L

def test(n, samples, rng):
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    x = (u0 - u1).pop()
    c0 = [y for y in range(2, n // 2 + 1) if common.playable(u0 | {y}, n - 1, spf)]
    c1 = [y for y in range(2, n // 2 + 1) if common.playable(u1 | {y}, n, spf)]
    bad01 = bad10 = 0; ex = []
    for _ in range(samples):
        L = random_maximal(u1, c1, n, rng)
        if not common.playable(u0 | set(L), n - 1, spf):
            bad10 += 1
            if len(ex) < 2: ex.append(("n-only", sorted(L), sum(L)))
        L = random_maximal(u0, c0, n - 1, rng)
        if not common.playable(u1 | set(L), n, spf):
            bad01 += 1
            if len(ex) < 2: ex.append(("n-1-only", sorted(L), sum(L)))
    print(f"{n} = {exch.fac_str(n)}, x = {x}: candidates {len(c0)} / {len(c1)} (same? {c0 == c1}); "
          f"sets of n not of n-1: {bad10}/{samples}; sets of n-1 not of n: {bad01}/{samples}")
    for e in ex: print("   example", e)
    sys.stdout.flush()

if __name__ == "__main__":
    rng = random.Random(2); samples = int(sys.argv[1])
    for a in sys.argv[2:]: test(int(a), samples, rng)
