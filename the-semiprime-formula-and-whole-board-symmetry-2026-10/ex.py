from tx import *
from t6 import u2_greedy, cycle_min, ends
from data import results, moves
res = results()
V = {n: d['score'] for n, d in res.items()}
def path(B, n):
    adj = {}
    for e in B:
        a, b = ends(e); adj.setdefault(a, []).append((b, e)); adj.setdefault(b, []).append((a, e))
    s, t = ends(n); prev = {s: None}; st = [s]
    while st:
        u = st.pop()
        for v, e in adj.get(u, []):
            if v not in prev: prev[v] = (u, e); st.append(v)
    if t not in prev: return None
    p = []; v = t
    while prev[v] is not None:
        u, e = prev[v]; p.append(e); v = u
    return p
for n in (21, 33, 39, 49, 51, 111, 119):
    B = sorted(u2_greedy(n - 1)); B2 = sorted(u2_greedy(n))
    print(n, factors(n), 'U2(n-1)=', B, 'U2(n)=', B2, 'path', path(B, n), 'V(n-1)', V[n-1], 'V(n)', V[n],
          'closed n-1', layer2_closed(n-1), 'closed n', layer2_closed(n), 'repeat', res[n]['method'])
o38, s38 = brute_opt(38); o39, s39 = brute_opt(39)
print(38, o38, s38); print(39, o39, s39)
print('exchange', sorted(set(s38[0]) - {22} | {39}) == s39[0])
