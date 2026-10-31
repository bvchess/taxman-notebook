"""The frame solver's repeats in 1301-2175 by kind, with what the prover spent searching them.

Reads a checkout of the main repository at commit 2896cdd: the folder named by TAXMAN_REPO, or the current folder.
With any argument, it also lists every repeat.
"""
import gzip, json, os, sys
from collections import Counter, defaultdict
W = os.environ.get('TAXMAN_REPO', '.')
res = {}
with gzip.open(W + '/results/optimal.jsonl.gz', 'rt') as f:
    for l in f:
        d = json.loads(l)
        res[d['n']] = d
prov = {}
with open(W + '/solver/noframe/data/exact_parity_1301_2175.jsonl') as f:
    for l in f:
        d = json.loads(l)
        prov[d['n']] = d

def factor(n):
    fs = []
    p = 2
    while p * p <= n:
        while n % p == 0:
            fs.append(p); n //= p
        p += 1
    if n > 1: fs.append(n)
    return fs

tot_secs = sum(d.get('secs', 0) for d in prov.values())
print('total prover secs', tot_secs, tot_secs / 3600)
cls = defaultdict(lambda: [0, 0.0, 0])
rows = []
for n in range(1301, 2176):
    d = res[n]; p = prov[n]
    if d['method'] != 'repeat':
        continue
    m = d['same_search']['n']
    fs = factor(n)
    ceil = d['score'] == res[n - 1]['score'] + n
    delta = d['score'] - res[m]['score']
    key = ('odd' if n % 2 else 'even', len(fs), 'm=n-1' if m == n - 1 else 'm=n-%d' % (n - m), 'ceil' if ceil else 'below')
    c = cls[key]; c[0] += 1; c[1] += p.get('secs', 0); c[2] += p.get('nodes', 0)
    rows.append((n, fs, m, ceil, p['relation'], p.get('search'), p.get('secs', 0), d['score'] - res[n-1]['score']))
for k, v in sorted(cls.items()):
    print(k, v[0], 'games', round(v[1] / 3600, 2), 'h', v[2], 'nodes')
print(len(rows), 'repeats', round(sum(r[6] for r in rows) / 3600, 2), 'h')
if len(sys.argv) > 1:
    for r in rows: print(r)
