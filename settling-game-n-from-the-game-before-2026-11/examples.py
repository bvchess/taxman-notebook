#!/usr/bin/env python3
"""The worked examples of the succession brief, computed from the rules alone (small boards).

    nice -n 19 python3 -I examples.py > examples_out.txt

For each board n it computes U* (descending greedy over the sources, each kept if it is playable with those kept),
the candidates (x up to n/2 with U* + {x} playable), every promotion set (L with U* + L playable, the exactness
theorem X7) by enumeration, P*, and compares in_the_bag + P* with the committed opt(n).  For a step n - 1 -> n it lists
the promotion sets of n - 1 whose value lies in the band (P*(n) + change, P*(n - 1)] that the proof of n must refute,
and the single-loss rule's x_min.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

spf = common.sieve_spf(1000)
res = common.results()


def ustar(n):
    kept = []
    for s in range(n, n // 2, -1):
        if common.playable(kept + [s], n, spf):
            kept.append(s)
    return sorted(kept)


def candidates(n, u):
    return [x for x in range(2, n // 2 + 1) if common.playable(u + [x], n, spf)]


def promotion_sets(n, u, cands):
    """Every promotion set, by a depth-first enumeration that extends only promotable sets (closed under removal)."""
    out = []

    def rec(i, cur):
        out.append(tuple(cur))
        for j in range(i, len(cands)):
            nxt = cur + [cands[j]]
            if common.playable(u + nxt, n, spf):
                rec(j + 1, nxt)
    rec(0, [])
    return out


def show(n):
    u = ustar(n)
    c = candidates(n, u)
    ps = promotion_sets(n, u, c)
    best = max(sum(p) for p in ps)
    opt_sets = [p for p in ps if sum(p) == best]
    bag = sum(u)
    print(f"  game {n} = {'*'.join(map(str, common.factor(n)))}: U* = {u} (sum {bag})")
    print(f"    candidates {c}; {len(ps)} promotion sets; P* = {best} by {opt_sets}; in_the_bag + P* = {bag + best}, "
          f"committed opt = {res[n]['score']}")
    return {"u": u, "c": c, "ps": ps, "pstar": best, "bag": bag, "opt_sets": opt_sets}


def single_loss(n):
    m = set(res[n - 1]["moves"])
    if common.playable(m | {n}, n, spf):
        return None
    for x in sorted(m):
        if common.playable((m - {x}) | {n}, n, spf):
            return x


def step(n, band=True):
    print(f"== Step {n - 1} -> {n}")
    a = show(n - 1)
    b = show(n)
    opt0, opt1 = res[n - 1]["score"], res[n]["score"]
    delta = opt0 + n - opt1
    print(f"    ceiling opt({n - 1}) + {n} = {opt0 + n}; opt({n}) = {opt1}; delta = {delta}")
    print(f"    U* gained {sorted(set(b['u']) - set(a['u']))}, lost {sorted(set(a['u']) - set(b['u']))}; "
          f"in_the_bag {a['bag']} -> {b['bag']}; P* {a['pstar']} -> {b['pstar']}")
    m0, m1 = set(res[n - 1]["moves"]), set(res[n]["moves"])
    print(f"    optimal set of {n - 1}: {sorted(m0)}")
    print(f"    optimal set of {n}: {sorted(m1)}")
    print(f"    it drops {sorted(m0 - m1)} and adds {sorted(m1 - m0)}")
    full = set(m0) | {n}
    if common.playable(full, n, spf):
        order, taxes = common.legal_order(full, n, spf)
        i = order.index(n)
        print(f"    optimal set of {n - 1} plus {n} is playable; a legal order: {order}; {n} is move {i + 1} and "
              f"takes {taxes[i]}")
    else:
        core = sorted(common.residual(full, spf))
        lists = {y: sorted(common.maximal_factors(y, spf) - full) for y in core}
        print(f"    optimal set of {n - 1} plus {n} is unplayable; its residual (the union of its cores): {lists}")
    order, taxes = common.legal_order(m1, n, spf)
    print(f"    a legal order of the optimal set of {n}: {list(zip(order, taxes))}")
    x = single_loss(n)
    print(f"    single-loss rule: x_min = {x}; rule's score {opt0 + n - (x or 0)} ({'exact' if x is None else ('holds' if opt0 + n - x == opt1 else 'fails')})")
    if band:
        # Promotion sets of n - 1 above what n reaches, read through the change of in_the_bag.
        shift = b["bag"] - a["bag"] - n  # 0 for a restriction, -n/2 for a relaxation, -x for an exchange
        lo = b["pstar"] + shift + n - (opt0 + n - opt1) - (b["bag"] - a["bag"]) + (b["bag"] - a["bag"])
        thr = opt1 - n - a["bag"]  # a set T of n - 1 with sum(T) > thr would give, with n, more than opt(n)
        above = sorted([p for p in a["ps"] if sum(p) > thr], key=lambda p: -sum(p))
        print(f"    promotion sets of {n - 1} worth more than opt({n}) - {n} - in_the_bag({n - 1}) = {thr}: "
              f"{len(above)}")
        for p in above[:12]:
            ok = common.playable(set(a["u"]) | set(p) | {n}, n, spf)
            print(f"      {list(p)} sum {sum(p)}: U*({n - 1}) + it + {n} playable on board {n}? {ok}")
        _ = lo
    print()


def main():
    print("Worked examples (each P* by enumeration of every promotion set; U* by descending greedy)")
    print()
    for n in (63, 40, 55, 77, 54, 51, 21):
        step(n)


if __name__ == "__main__":
    main()
