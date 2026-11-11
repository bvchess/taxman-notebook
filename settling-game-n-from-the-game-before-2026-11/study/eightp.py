#!/usr/bin/env python3
"""The step 8P - 1 -> 8P (P prime): what the optimal sets do with the hub 8 and the numbers 4t, 8t, 2t.

    nice -n 19 python3 -I study/eightp.py N [N ...]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import common  # noqa: E402
import exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
from edges import payments  # noqa: E402

spf = exch.spf


def show(n):
    res = exch.results()
    P = n // 8
    P1 = prev_prime(P)
    u0, u1 = exch.ustar_from_arrival(n - 1), exch.ustar_from_arrival(n)
    S0, S1 = set(res[n - 1]["moves"]), set(res[n]["moves"])
    L0, L1 = S0 - u0, S1 - u1
    print(f"== {n} = 8*{P}, P1 = {P1}, 4P1 = {4 * P1}; delta = {res[n - 1]['score'] + n - res[n]['score']}; "
          f"U* gained {sorted(u1 - u0)}, lost {sorted(u0 - u1)}")
    print(f"  U at n-1? {all(y in S0 for y in u0 if exch.omega(y) >= 3)}; U at n? "
          f"{all(y in S1 for y in u1 if exch.omega(y) >= 3)}")
    print(f"  P*(n-1) = {sum(L0)} ({len(L0)} promotions), P*(n) = {sum(L1)} ({len(L1)}); "
          f"L(n) - L(n-1) = {sorted(L1 - L0)}, L(n-1) - L(n) = {sorted(L0 - L1)}")
    print(f"  moves of n-1 not of n: {sorted(S0 - S1)}; moves of n not of n-1: {sorted(S1 - S0)}")
    for board, S in ((n - 1, S0), (n, S1)):
        pay = payments(S, board)
        print(f"  board {board}: 8 in set? {8 in S}; 16 in set? {16 in S}; 8 paid to {[m for m, f in pay.items() if f == 8]}; "
              f"4 paid to {[m for m, f in pay.items() if f == 4]}")
        eights = sorted(m for m in S if m % 8 == 0 and spf[m // 8] == m // 8)
        print(f"    members 8t in set: {len(eights)}; those paying 8: {[m for m in eights if pay[m] == 8]}; "
              f"4t promoted (t prime, 8t in set): {sorted(4 * (m // 8) for m in eights if 4 * (m // 8) in S)}")
        fours = sorted(m for m in S if m % 4 == 0 and m // 4 > 1 and spf[m // 4] == m // 4 and m <= board // 2)
        print(f"    promoted 4t: {[(m, pay[m]) for m in fours]}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        show(int(a))
