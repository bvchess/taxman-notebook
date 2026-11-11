#!/usr/bin/env python3
"""The layer-3 instance across an exchange step n - 1 -> n (n odd, U*(n) = U*(n-1) - x + n).

    nice -n 19 python3 -I study/exch.py N [N ...]      (run from the succession folder)

For each n: U*(n-1) and U*(n) (cumulated from the arrival file, checked once against descending greedy), the
optimal sets of both games (committed results), the promotions L (optimal set less U*), whether L of n is a
promotion set of n - 1 and L' of n - 1 one of n, the GF(2) circuit of v(n) in U*(n-1)_3, and the core of
U*(n)_3 + x.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402

LIMIT = 10100
spf = common.sieve_spf(LIMIT)
_arrival = None
_results = None


def omega(x):
    return len(common.factor(x))


def arrival():
    global _arrival
    if _arrival is None:
        _arrival = common.arrival()
    return _arrival


def results():
    global _results
    if _results is None:
        _results = common.results()
    return _results


def ustar_from_arrival(n):
    """U*(n) cumulated from the arrival file's added/dropped lists, boards 3..8191; U*(2) = {2}."""
    arr = arrival()
    u = {2}
    for m in range(3, n + 1):
        row = arr[m]
        u |= set(row["added"])
        u -= set(row["dropped"])
    return u


def ustar_greedy(n):
    kept = []
    for s in range(n, n // 2, -1):
        if common.playable(kept + [s], n, spf):
            kept.append(s)
    return set(kept)


def layer_part(S, k):
    return {x for x in S if omega(x) == k}


def gf2_circuit(members, target):
    """The unique subset of `members` (layer-3 numbers, vectors = maximal-factor sets) whose vectors sum to
    v(target) over GF(2), or None if v(target) is not in their span.  Members are assumed independent."""
    coords = {}

    def vec(x):
        v = 0
        for f in common.maximal_factors(x, spf):
            if f not in coords:
                coords[f] = len(coords)
            v |= 1 << coords[f]
        return v

    rows = []  # (vector, combination bitmask over members)
    mem = sorted(members)
    for i, x in enumerate(mem):
        v, c = vec(x), 1 << i
        for rv, rc in rows:
            if v & (rv & -rv):
                v ^= rv
                c ^= rc
        if v == 0:
            raise ValueError("dependent members")
        rows.append((v, c))
        rows.sort(key=lambda r: r[0] & -r[0])
    t, c = vec(target), 0
    for rv, rc in rows:
        if t & (rv & -rv):
            t ^= rv
            c ^= rc
    if t != 0:
        return None
    return sorted(mem[i] for i in range(len(mem)) if c >> i & 1)


def fac_str(x):
    return "*".join(map(str, common.factor(x)))


def study(n, check_greedy=False):
    res = results()
    u0, u1 = ustar_from_arrival(n - 1), ustar_from_arrival(n)
    if check_greedy:
        g0 = ustar_greedy(n - 1)
        print(f"  greedy check at {n - 1}: {'agrees' if g0 == u0 else 'DIFFERS'}")
    gained, lost = sorted(u1 - u0), sorted(u0 - u1)
    print(f"== {n} = {fac_str(n)}: U* gained {gained}, lost {[(x, fac_str(x)) for x in lost]}")
    if gained != [n] or len(lost) != 1:
        print("  not a one-for-one exchange")
        return
    x = lost[0]
    k = omega(n)
    A, A1 = layer_part(u0, k), layer_part(u1, k)
    print(f"  layer {k}: |U*_{k}(n-1)| = {len(A)}, |U*_{k}(n)| = {len(A1)}; x = {x} > n/2 = {n / 2}")
    out = {"n": n, "x": x}
    if n - 1 in res and n in res:
        S1, S0 = set(res[n]["moves"]), set(res[n - 1]["moves"])
        L1 = S1 - u1
        L0 = S0 - u0
        print(f"  opt(n-1) = {res[n - 1]['score']}, opt(n) = {res[n]['score']}, delta = "
              f"{res[n - 1]['score'] + n - res[n]['score']}")
        print(f"  U holds at n (set contains U*_>=3)? {all(y in S1 for y in u1 if omega(y) >= 3)}; "
              f"at n-1? {all(y in S0 for y in u0 if omega(y) >= 3)}")
        print(f"  promotions: n has {len(L1)} (sum {sum(L1)}), n-1 has {len(L0)} (sum {sum(L0)}); "
              f"same set? {L1 == L0}; by layer n: { {j: len(layer_part(L1, j)) for j in range(2, 12) if layer_part(L1, j)} }")
        if L1 != L0:
            print(f"    only in n: {sorted(L1 - L0)}, only in n-1: {sorted(L0 - L1)}")
        p1 = common.playable(u0 | L1, n - 1, spf)
        p0 = common.playable(u1 | L0, n, spf)
        print(f"  L(n) is a promotion set of n-1? {p1};  L(n-1) is a promotion set of n? {p0}")
        out.update(L_n_in_prev=p1, L_prev_in_n=p0, same=L1 == L0)
    circ = gf2_circuit(A, n)
    if circ is None:
        print("  v(n) is NOT in the span of U*_k(n-1)")
    else:
        print(f"  circuit of v(n) in U*_{k}(n-1): {len(circ)} members, min {min(circ)} ({'= x' if min(circ) == x else '!= x'}): "
              f"{[(c, fac_str(c)) for c in circ]}")
    core = common.residual(A1 | {x}, spf)
    print(f"  residual of U*_{k}(n) + x: {len(core)} members: {sorted(core)}")
    even = all(sum(1 for m in core if f in common.maximal_factors(m, spf)) % 2 == 0
               for m in core for f in common.maximal_factors(m, spf))
    print(f"  residual is an even core (every factor listed an even number of times)? {even}")
    return out


if __name__ == "__main__":
    first = True
    for arg in sys.argv[1:]:
        study(int(arg), check_greedy=first and "--check" in sys.argv)
        first = False
