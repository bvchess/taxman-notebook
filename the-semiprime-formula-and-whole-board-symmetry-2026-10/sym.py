"""Whole-board prime exchanges: pairs p < q > sqrt(n) whose exchange maps every optimal set into the board."""
import sys, math
from tx import *

def u2_greedy(n):
    kept = []
    for s in range(n, n // 2, -1):
        if omega(s) == 2 and is_forest_layer2(kept + [s], n):
            kept.append(s)
    return set(kept)

def pairs(n, extended=True):
    r = math.isqrt(n)
    ps = [p for p in primes_upto(n // 2) if p > r]
    u2 = u2_greedy(n) if extended else set()
    closed = len(u2) == len(primes_upto(n // 2)) if extended else False
    out = []
    for i, p in enumerate(ps):
        for qq in ps[i + 1:]:
            kp, kq = n // p, n // qq
            if kq < 1:
                continue
            obs = [p * t for t in range(kq + 1, kp + 1)]
            if not obs:
                out.append((p, qq, 'same floor'))
                continue
            if not extended:
                continue
            ok = True
            for x in obs:
                if omega(x) != 2:
                    ok = False; break
                if x > n // 2 and x in u2:
                    ok = False; break
                if x <= n // 2 and not closed:
                    ok = False; break
            if ok:
                out.append((p, qq, 'F4'))
    return out

def classes(n, prs):
    parent = {}
    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            a = parent[a]
        return a
    for p, qq, _ in prs:
        parent[find(p)] = find(qq)
    cl = {}
    for a in list(parent):
        cl.setdefault(find(a), []).append(a)
    return sorted(sorted(c) for c in cl.values())

for n in map(int, sys.argv[1:]):
    s = pairs(n, extended=False)
    e = pairs(n, extended=True)
    print(n, 'same floor:', classes(n, s))
    print(n, 'with F4  :', classes(n, e))
    # free numbers (layer >= 3) moved by some pair
    moved = set()
    for p, qq, _ in e:
        for x in range(2, n + 1):
            if omega(x) >= 3 and (x % p == 0 or x % qq == 0):
                moved.add(x)
    print(n, 'layer>=3 numbers moved:', len(moved), 'of', sum(1 for x in range(2, n + 1) if omega(x) >= 3))
