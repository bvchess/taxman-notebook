"""The semiprime step on the proven range: the bound against the proven scores, and the exchange on every optimal set."""
import sys
from tx import *
from data import *

res = results()
osets = optsets(res)
print('optsets complete for', len(osets), 'games')
V = {n: d['score'] for n, d in res.items()}

def best_x(n, u2):
    if n not in u2:
        return None
    rest = [s for s in u2 if s != n]
    for y in range(n - 1, n // 2, -1):
        if omega(y) == 2 and y not in u2 and is_forest_layer2(rest + [y], n):
            return y
    return None

def u2_greedy(n):
    """U*_2 by the scan of F4 step 3: descending greedy on layer-2 sources is the forest scan."""
    kept = []
    for s in range(n, n // 2, -1):
        if omega(s) == 2 and is_forest_layer2(kept + [s], n):
            kept.append(s)
    return kept

N = int(sys.argv[1])
stats = {}
for n in range(9, N + 1):
    if n % 2 == 0 or omega(n) != 2:
        continue
    u2 = u2_greedy(n)
    closed = len(u2) == len(primes_upto(n // 2))
    x = best_x(n, u2)
    rep = res[n]['method'] == 'repeat'
    if x is None:
        key = ('closed' if closed else 'open', 'no x', rep)
        stats[key] = stats.get(key, 0) + 1
        continue
    bound = V[n - 1] + n - x
    rel = 'eq' if V[n] == bound else ('below' if V[n] < bound else 'ABOVE')
    key = ('closed' if closed else 'open', rel, 'repeat' if rep else 'not repeat')
    stats[key] = stats.get(key, 0) + 1
    if not closed or rel != 'eq' or not rep:
        print(n, factors(n), key, 'x', x, 'V', V[n], 'bound', bound)
    if n in osets:
        for S in osets[n]:
            if n in S:
                T = (S - {n}) | {x}
                ok = x not in S and playable(T) and max(T) <= n - 1
                if not ok:
                    print('EXCHANGE FAILS', n, closed)
                stats[('exchange', closed, ok)] = stats.get(('exchange', closed, ok), 0) + 1
for k, v in sorted(stats.items(), key=str):
    print(k, v)
