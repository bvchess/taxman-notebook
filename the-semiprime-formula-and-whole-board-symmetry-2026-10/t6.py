"""Odd semiprimes to 400: closure of layer 2 at n - 1 and n, the cycle n closes with U*_2(n - 1), and the formula."""
from tx import *

def u2_greedy(n):
    kept = []
    for s in range(n, n // 2, -1):
        if omega(s) == 2 and is_forest_layer2(kept + [s], n):
            kept.append(s)
    return kept

def ends(e):
    f = factors(e)
    return (f[0], f[1]) if f[0] != f[1] else (f[0], 'g')

def cycle_min(B, n):
    """The smallest member of the cycle that n closes with the forest B, or None."""
    adj = {}
    for e in B:
        a, b = ends(e)
        adj.setdefault(a, []).append((b, e)); adj.setdefault(b, []).append((a, e))
    s, t = ends(n)
    # path from s to t in the forest
    prev = {s: None}
    stack = [s]
    while stack:
        u = stack.pop()
        for v, e in adj.get(u, []):
            if v not in prev:
                prev[v] = (u, e); stack.append(v)
    if t not in prev:
        return None
    path = []
    v = t
    while prev[v] is not None:
        u, e = prev[v]; path.append(e); v = u
    return min(path)

if __name__ == "__main__":
    from data import *
    res = results()
    V = {n: d['score'] for n, d in res.items()}
    rows = []
    for n in range(9, 401, 2):
        if omega(n) != 2:
            continue
        B = u2_greedy(n - 1); B2 = u2_greedy(n)
        np2 = len(primes_upto(n // 2))
        c1, c2 = len(B) == np2, len(B2) == np2
        x = cycle_min(B, n)
        if x is None:
            f = 'no cycle; ceiling' if V[n] == V[n - 1] + n else 'no cycle; below ceiling by %d' % (V[n - 1] + n - V[n])
        else:
            assert sorted(B2) == sorted(set(B) - {x} | {n}), n
            f = 'formula holds' if V[n] == V[n - 1] + n - x else 'FORMULA FAILS: V(n)-V(n-1)-n+x = %d' % (V[n] - V[n - 1] - n + x)
        if not (c1 and c2) or x is None or 'FAILS' in f:
            print(n, factors(n), 'closed n-1:', c1, 'closed n:', c2, 'x:', x, f)
