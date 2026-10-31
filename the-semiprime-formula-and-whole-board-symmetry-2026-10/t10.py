"""Both whole-board prime exchanges on every optimal set the prover enumerates (187..989, sampled every 7th game):
the image is playable and on the board, and the inequality holds."""
import math
from tx import omega, playable, factors
from data import results, optsets
from sym2 import pairs

def pi(x, p, q):
    if x % p == 0:
        return x // p * q
    if x % q == 0:
        return x // q * p
    return x

res = results(); os_ = optsets(res)
stats = {'floor': [0, 0, 0], 'f4': [0, 0, 0]}
for n in range(187, 990, 7):
    if n not in os_:
        continue
    for mode in ('floor', 'f4'):
        for p, q in pairs(n, mode == 'f4'):
            for S in os_[n]:
                X = [x for x in S if omega(x) >= 3] if mode == 'f4' else list(S)
                rest = [x for x in S if x not in X]
                image = rest + [pi(x, p, q) for x in X]
                cp = sum(x // p for x in X if x % p == 0); cq = sum(x // q for x in X if x % q == 0)
                st = stats[mode]; st[0] += 1
                if max(image) > n or not playable(image):
                    st[1] += 1
                if cp > cq:
                    st[2] += 1
                    print('INEQUALITY FAILS', mode, n, p, q)
for k, v in stats.items():
    print(k, 'checks', v[0], 'image off the board or unplayable', v[1], 'inequality broken', v[2])
