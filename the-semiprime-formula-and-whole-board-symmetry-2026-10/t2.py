"""Check the semiprime step on small boards by brute force."""
import sys, time
from tx import *

N = int(sys.argv[1])
opt = {}
sets = {}
for n in range(2, N + 1):
    opt[n], sets[n] = brute_opt(n)

def best_x(n, U):
    u2 = [s for s in U if omega(s) == 2]
    if n not in u2:
        return None
    rest = [s for s in u2 if s != n]
    for y in range(n - 1, n // 2, -1):
        if omega(y) == 2 and y not in u2 and is_forest_layer2(rest + [y], n):
            return y
    return None

for n in range(9, N + 1):
    if n % 2 == 0 or omega(n) != 2:
        continue
    U = ustar(n)
    closed = layer2_closed(n, U)
    x = best_x(n, U)
    if x is None:
        print(n, 'no x', 'closed' if closed else 'open'); continue
    bound = opt[n - 1] + n - x
    ok_bound = opt[n] <= bound
    # every optimal set holding n: is S - n + x playable (in game n - 1)?
    exch = []
    for S in sets[n]:
        if n in S:
            T = [s for s in S if s != n] + [x]
            exch.append(x not in S and playable(T))
    print(n, factors(n), 'closed' if closed else 'OPEN', 'x', x, 'opt', opt[n], 'bound', bound,
          'eq' if opt[n] == bound else ('ok' if ok_bound else 'FAILS'), 'exchanges', exch, flush=True)
