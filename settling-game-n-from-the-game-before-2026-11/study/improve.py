#!/usr/bin/env python3
"""For random maximal promotion sets L of n that are not promotion sets of n - 1 (across an exchange): what the
core on board n - 1 looks like, what it costs to fix L there (lightest single removal), and whether L has a heavier
neighbor (single swap) on board n.

    nice -n 19 python3 -I study/improve.py SAMPLES N [N ...]
"""

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import common  # noqa: E402
import exch  # noqa: E402
from boxes import box_of  # noqa: E402
from promsets_full import random_maximal  # noqa: E402

spf = exch.spf


def fix_cost(u, L, board):
    """Lightest single member of L whose removal makes u + L playable on `board`; None if none does."""
    best = None
    for m in sorted(L):
        if common.playable((u | L) - {m}, board, spf):
            best = m
            break
    return best


def best_swap(u, L, cands, board):
    """The heaviest gain among single swaps L - m + c (c a candidate outside L) that stay promotion sets; the
    swap itself."""
    best = (0, None)
    Lset = set(L)
    for m in sorted(L):
        base = (u | Lset) - {m}
        for c in sorted(cands, reverse=True):
            if c <= m or c in Lset:
                continue
            if c - m <= best[0]:
                break
            if common.playable(base | {c}, board, spf):
                best = (c - m, (m, c))
                break
    return best


def run(n, samples, rng):
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    x = (u0 - u1).pop()
    box = box_of(n)
    c1 = [y for y in range(2, n // 2 + 1) if common.playable(u1 | {y}, n, spf)]
    print(f"== {n} = {exch.fac_str(n)}, x = {x} = {exch.fac_str(x)}, box {sorted(box)}")
    found = 0
    for _ in range(samples):
        L = set(random_maximal(u1, c1, n, rng))
        if common.playable(u0 | L, n - 1, spf):
            continue
        found += 1
        R = common.residual(u0 | L, spf)
        core_L = sorted(R & L)
        core_box = sorted(R & box)
        core_src = sorted(R - L - box)
        cost = fix_cost(u0, L, n - 1)
        gain, swap = best_swap(u1, L, c1, n)
        print(f"  L: {len(L)} members, sum {sum(L)}; residual on n-1: {len(R)} members = box {core_box}, "
              f"promotions {[(m, exch.fac_str(m)) for m in core_L]}, other sources {len(core_src)}")
        print(f"     cheapest single removal that fixes L on n-1: {cost}; best single swap on n: gain {gain} by {swap}"
              f"{'' if swap is None else ' = ' + exch.fac_str(swap[0]) + ' -> ' + exch.fac_str(swap[1])}")
        if found >= 6:
            break
    sys.stdout.flush()


if __name__ == "__main__":
    rng = random.Random(3)
    for a in sys.argv[2:]:
        run(int(a), int(sys.argv[1]), rng)
