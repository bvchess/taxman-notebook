from tx import factors
from data import *
from collections import Counter
res = results()
N = max(res)
print('chain to', N)
c = Counter()
for n in range(2176, N + 1):
    d = res[n]
    fs = factors(n)
    ceil = d['score'] == res[n - 1]['score'] + n
    prime = len(fs) == 1
    if prime or ceil:
        c['free (prime or ceiling)'] += 1; continue
    if d['method'] == 'repeat':
        m = d['same_search']['n']
        c[('repeat', 'odd' if n % 2 else 'even', len(fs), n - m)] += 1
    else:
        c[('searched', d['method'])] += 1
for k, v in sorted(c.items(), key=str): print(k, v)
