#!/usr/bin/env python3
"""How the optimal sets of an exchange pair use the box's edges.

    nice -n 19 python3 -I study/edges.py N [N ...]

For n = pqr (p < q < r) with shadow x = p'q'r': the twelve edges of the box and the eight "special" edges
(p'q, pq, p'r, pr, p'q', pq', p'r', pr'), who lists each among U* + L* on each board, and a legal order's payments.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import common  # noqa: E402
import exch  # noqa: E402
from boxes import prev_prime  # noqa: E402

spf = exch.spf


def payments(members, board):
    """A payment scheme from peel (front/back moves, as legal_order does), as {member: factor}."""
    members = set(members)
    lists = {x: common.maximal_factors(x, spf) - members for x in members}
    pay = {}
    live_m, live_f = set(members), set().union(*lists.values())
    while live_m:
        moved = False
        for x in sorted(live_m):
            fs = [g for g in lists[x] if g in live_f]
            if len(fs) == 1:
                pay[x] = fs[0]
                live_m.discard(x)
                live_f.discard(fs[0])
                moved = True
                break
        if moved:
            continue
        for f in sorted(live_f):
            ys = [y for y in live_m if f in lists[y]]
            if len(ys) == 1:
                pay[ys[0]] = f
                live_m.discard(ys[0])
                live_f.discard(f)
                moved = True
                break
        if not moved:
            return None
    return pay


def show(n):
    res = exch.results()
    p, q, r = common.factor(n)
    p1, q1, r1 = prev_prime(p), prev_prime(q), prev_prime(r)
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    x = (u0 - u1).pop()
    S1 = set(res[n]["moves"])
    S0 = set(res[n - 1]["moves"])
    L = S1 - u1
    assert L == S0 - u0, "different promotions"
    print(f"== {n} = {p}*{q}*{r}, x = {x} = {p1}*{q1}*{r1}; P* = {sum(L)}, |L| = {len(L)}")
    special = {f"{a}*{b}": a * b for a in (p1, p) for b in (q1, q, r1, r)}
    for board, S in ((n, S1), (n - 1, S0)):
        pay = payments(S, board)
        used = set(pay.values())
        print(f"  board {board}: scheme found? {pay is not None}")
        for name, e in sorted(special.items(), key=lambda kv: kv[1]):
            listers = sorted(m for m in S if e in common.maximal_factors(m, spf))
            tags = []
            for m in listers:
                tag = f"{m}={exch.fac_str(m)}"
                if m in L:
                    tag += "(L)"
                if pay and pay.get(m) == e:
                    tag += "[pays]"
                tags.append(tag)
            print(f"    edge {name} = {e}: {'unused' if e not in used else 'used'}; listed by {tags}")
    # the layer-3 multiples of the special edges that are NOT in the set but are candidates
    print("  layer-3 multiples of the special edges up to n/2 not promoted:")
    for name, e in sorted(special.items(), key=lambda kv: kv[1]):
        mults = [m for m in range(e * 2, n // 2 + 1, e) if exch.omega(m) == 3 and m not in L]
        print(f"    {name} = {e}: {[(m, exch.fac_str(m)) for m in mults]}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        show(int(a))
