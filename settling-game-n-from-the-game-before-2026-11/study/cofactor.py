#!/usr/bin/env python3
"""The step cP - 1 -> cP (P prime, c the cofactor): the moves that change, and the payments of the small hubs.
    nice -n 19 python3 -I study/cofactor.py C N [N ...]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
from edges import payments  # noqa: E402
spf = exch.spf

def show(c, n):
    res = exch.results(); P = n // c; P1 = prev_prime(P)
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    S0, S1 = set(res[n - 1]["moves"]), set(res[n]["moves"])
    L0, L1 = S0 - u0, S1 - u1
    print(f"== {n} = {c}*{P}, P1 = {P1}; delta = {res[n-1]['score'] + n - res[n]['score']} (c/2*P1 = {c//2*P1}); "
          f"U* gained {sorted(u1-u0)}, lost {sorted(u0-u1)}; U at n-1,n: "
          f"{all(y in S0 for y in u0 if exch.omega(y)>=3)}, {all(y in S1 for y in u1 if exch.omega(y)>=3)}")
    print(f"  moves of n-1 not of n: {[(m, exch.fac_str(m)) for m in sorted(S0-S1)]}; of n not of n-1: {[(m, exch.fac_str(m)) for m in sorted(S1-S0)]}")
    hubs = [4, 6, 8, 9, 10, 12, 16, 18, 20, 24, 2*P, 3*P, 4*P, 2*P1, 3*P1, 4*P1, 6*P1]
    for board, S in ((n-1, S0), (n, S1)):
        pay = payments(S, board)
        who = {}
        for m, f in pay.items(): who.setdefault(f, []).append(m)
        print(f"  board {board}: " + "; ".join(f"{h}->{[(m, exch.fac_str(m)) for m in who.get(h, [])]}" for h in hubs if h <= board//2))
        print(f"    in set: {[h for h in hubs if h in S]}")

if __name__ == "__main__":
    for a in sys.argv[2:]: show(int(sys.argv[1]), int(a))
