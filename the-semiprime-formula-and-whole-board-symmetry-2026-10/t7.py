"""Random tests of the swap at the heart of the semiprime formula, with an independent playability check.

For odd n with two prime factors that closes a cycle with U*_2(n - 1), with x its smallest other member: build random
playable sets S of game n with S_1 = {q(n)}, S's sources of layer 2 = U*_2(n), any forest of small numbers of layer 2
beside them, and random numbers of layers 3 and up; check that S - n + x is playable.  Likewise sets T of game n - 1
built on U*_2(n - 1), and T - x + n.
"""
import random, sys
from tx import *
from t6 import u2_greedy, cycle_min

random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
N = int(sys.argv[1])
checks = fails = 0
for n in range(9, N + 1, 2):
    if omega(n) != 2:
        continue
    B = u2_greedy(n - 1)
    x = cycle_min(B, n)
    if x is None:
        continue
    U2n = sorted(set(B) - {x} | {n})
    for side in ('n', 'n-1'):
        top = n if side == 'n' else n - 1
        base = [q(n)] + (U2n if side == 'n' else B)
        small2 = [y for y in range(4, top // 2 + 1) if omega(y) == 2]
        high = [y for y in range(8, top + 1) if omega(y) >= 3]
        for trial in range(6):
            S = list(base)
            random.shuffle(small2)
            for y in small2[:random.randint(0, 3)]:
                if is_forest_layer2([s for s in S if omega(s) == 2] + [y], top) and playable(S + [y]):
                    S.append(y)
            random.shuffle(high)
            for y in high[:random.randint(0, len(high))]:
                if playable(S + [y]):
                    S.append(y)
            assert playable(S)
            if side == 'n':
                T = [s for s in S if s != n] + [x]
            else:
                T = [s for s in S if s != x] + [n]
            checks += 1
            if not playable(T):
                fails += 1
                print('FAIL', n, side, sorted(S))
print('checks', checks, 'fails', fails)
