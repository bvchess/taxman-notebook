"""The semiprime formula against the recorded scores of every odd semiprime to the end of the chain."""
from collections import Counter
from tx import factors, omega, SPF
from data import results, prover_lines

res = results(); prov = prover_lines()
V = {n: d['score'] for n, d in res.items()}
N = max(V)

def ends(e):
    f = factors(e)
    return (f[0], f[1]) if f[0] != f[1] else (f[0], 'g')

def u2(n):
    parent = {}
    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    kept = []
    for s in range(n, n // 2, -1):
        if len(factors(s)) == 2:
            a, b = ends(s); ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb; kept.append(s)
    return kept

def cycle_min(B, n):
    adj = {}
    for e in B:
        a, b = ends(e)
        adj.setdefault(a, []).append((b, e)); adj.setdefault(b, []).append((a, e))
    s, t = ends(n)
    prev = {s: None}; stack = [s]
    while stack:
        u = stack.pop()
        for v, e in adj.get(u, []):
            if v not in prev:
                prev[v] = (u, e); stack.append(v)
    if t not in prev:
        return None
    m = None; v = t
    while prev[v] is not None:
        u, e = prev[v]; m = e if m is None else min(m, e); v = u
    return m

if __name__ == "__main__":
    c = Counter(); hours = Counter()
    for n in range(9, N + 1, 2):
        if omega(n) != 2:
            continue
        x = cycle_min(u2(n - 1), n)
        if x is None:
            c['no cycle', n <= 187] += 1
            continue
        ok = V[n] == V[n - 1] + n - x
        band = '2..2175' if n <= 2175 else '2176..%d' % N
        c[band, 'formula holds' if ok else 'FAILS'] += 1
        if not ok:
            print('FAILS', n)
        if 1301 <= n <= 2175:
            p = prov[n]
            hours[p['relation'], p.get('search')] += p.get('secs', 0) / 3600
            c['1301-2175', p['relation'], p.get('search')] += 1
    for k, v in sorted(c.items(), key=str): print(k, v)
    for k, v in hours.items(): print('thread-hours', k, round(v, 2))
