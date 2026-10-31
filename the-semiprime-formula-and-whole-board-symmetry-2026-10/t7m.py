"""Mutation check for t7: swap n for a source of layer 2 off the cycle; the check must see failures."""
import random
from tx import *
from t6 import u2_greedy, cycle_min, ends
random.seed(2)
checks = fails = 0
for n in range(51, 301, 2):
    if omega(n) != 2:
        continue
    B = u2_greedy(n - 1)
    x = cycle_min(B, n)
    if x is None:
        continue
    U2n = sorted(set(B) - {x} | {n})
    others = [y for y in range(n // 2 + 1, n) if omega(y) == 2 and y not in B]
    if not others:
        continue
    y = random.choice(others)
    S = [q(n)] + U2n
    T = [s for s in S if s != n] + [y]
    checks += 1
    fails += not playable(T)
print('mutation checks', checks, 'caught', fails)
