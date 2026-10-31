"""Prime exchanges relative to F4's roles: pairs p < q, p^2 > n, whose exchange maps numbers up to n/2 onto themselves
(no t >= 1 with pt <= n/2 < qt) and numbers of layers 3 and up onto themselves (no composite t with pt <= n < qt)."""
import sys, math
from tx import primes_upto, omega
def pairs(n, f4=True):
    r = math.isqrt(n)
    ps = [p for p in primes_upto(n // 2) if p > r]
    out = []
    for i, p in enumerate(ps):
        for q in ps[i + 1:]:
            if f4:
                ok = n // (2 * p) == n // (2 * q) and all(omega(t) == 1 for t in range(n // q + 1, n // p + 1))
            else:
                ok = n // p == n // q
            if ok:
                out.append((p, q))
    return out
def classes(prs):
    parent = {}
    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a: a = parent[a]
        return a
    for p, q in prs: parent[find(p)] = find(q)
    cl = {}
    for a in list(parent): cl.setdefault(find(a), []).append(a)
    return sorted(sorted(c) for c in cl.values())
if __name__ == "__main__":
    for n in map(int, sys.argv[1:]):
        for f4 in (False, True):
            prs = pairs(n, f4)
            moved = {x for p, q in prs for x in range(2, n + 1) if omega(x) >= 3 and (x % p == 0 or x % q == 0)}
            cl = [c for c in classes(prs) if c[0] <= n // 4]
            print(n, 'F4-relative' if f4 else 'same floor ', 'classes below n/4:', cl, 'moved', len(moved))
