#!/usr/bin/env python3
"""E1's leaf at n: G + leaf_promotions.  Its layer residuals; fiber members of the residual by largest prime; and the
primes above 23 in a few sampled minimal cores.  Which B would capture the mixed cores?"""
import json, random, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore"); sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-1")
import parity as P
import cores as C
def largest_prime(x):
    p, big = 2, 1
    while p * p <= x:
        while x % p == 0:
            big = p; x //= p
        p += 1
    return max(big, x) if x > 1 else big
random.seed(3)
n = int(sys.argv[1])
leaf = None
for line in open("/home/brian/taxman_work/lab/work/oddcore/e1/results.jsonl"):
    d = json.loads(line)
    if d["n"] == n and d["B"] == 23 and d.get("finished"):
        leaf = d
if leaf is None:
    sys.exit("no finished leaf at %d" % n)
om, mf = P.omega_and_mf(n)
g = P.greedy_basis(n, om, mf)
h = set(g) | set(leaf["leaf_promotions"])
assert sum(h) == leaf["PB_s"], (sum(h), leaf["PB_s"])
out = {"n": n, "PB_s": leaf["PB_s"], "promotions": len(leaf["leaf_promotions"])}
for k in sorted({om[x] for x in h}):
    layer = [x for x in h if om[x] == k]
    lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
    res = C.residual(layer, lists)
    if not res:
        continue
    fib = sorted(x for x in res if largest_prime(x) > 23)
    sm = [x for x in res if largest_prime(x) <= 23]
    byp = {}
    for x in fib:
        byp[largest_prime(x)] = byp.get(largest_prime(x), 0) + 1
    # residual restricted to B-smooth members for several B
    stall = {}
    for B in (23, 29, 31, 37, 41, 47, 53):
        sub = [x for x in layer if largest_prime(x) <= B]
        stall[B] = "%d/%d" % (len(C.residual(sub, lists)), len(sub))
    # sampled minimal cores: primes > 23 per core
    cores = []
    for _ in range(12):
        order = list(res); random.shuffle(order)
        c = C.minimal_core(res, lists, order)
        ps = sorted({largest_prime(x) for x in c if largest_prime(x) > 23})
        cores.append({"size": len(c), "smooth": sum(1 for x in c if largest_prime(x) <= 23), "fiber_primes": ps})
    out["L%d" % k] = {"residual": len(res), "smooth": len(sm), "fiber": len(fib), "fiber_by_prime": dict(sorted(byp.items())),
                      "B_smooth_only_stall": stall, "cores": cores}
print(json.dumps(out))
