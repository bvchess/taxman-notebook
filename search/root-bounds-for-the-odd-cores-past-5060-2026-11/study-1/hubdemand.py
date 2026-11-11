#!/usr/bin/env python3
"""At E1's leaf (B = 23) for n: per layer, each fiber's hub demand d_p = (fiber-p members) - (max matching of them into
their unpromoted fiber factors); total demand D; and whether SOME assignment of distinct hubs meeting the demands (each
fiber from the hubs its members list) leaves the smooth sub-instance playable without those hubs.  If none does, the
leaf violates the 'smooth-exact with hub demands' condition, so that bound is strictly below PB_s there."""
import json, sys, itertools
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore"); sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-1")
import parity as P
import cores as C
from leafres import largest_prime

def max_matching(adj):
    """adj: member -> list of factors.  Returns the size of a maximum matching (augmenting paths)."""
    match = {}
    def try_(u, seen):
        for v in adj[u]:
            if v in seen: continue
            seen.add(v)
            if v not in match or try_(match[v], seen):
                match[v] = u
                return True
        return False
    return sum(try_(u, set()) for u in adj)

n = int(sys.argv[1])
leaf = None
for line in open("/home/brian/taxman_work/lab/work/oddcore/e1/results.jsonl"):
    d = json.loads(line)
    if d["n"] == n and d["B"] == 23 and d.get("finished"):
        leaf = d
om, mf = P.omega_and_mf(n)
g = P.greedy_basis(n, om, mf)
h = set(g) | set(leaf["leaf_promotions"])
for k in sorted({om[x] for x in h}):
    layer = [x for x in h if om[x] == k]
    lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
    smooth = [x for x in layer if largest_prime(x) <= 23]
    fibers = {}
    for x in layer:
        p = largest_prime(x)
        if p > 23: fibers.setdefault(p, []).append(x)
    demand, hubs_of = {}, {}
    for p, mem in fibers.items():
        adj = {x: [f for f in lists[x] if f % p == 0] for x in mem}
        nu = max_matching(adj)
        dp = len(mem) - nu
        if dp > 0:
            demand[p] = dp
            hubs_of[p] = sorted({f for x in mem for f in lists[x] if f % p != 0})
    D = sum(demand.values())
    sl = {x: lists[x] for x in smooth}
    base = len(C.residual(smooth, sl))
    out = {"n": n, "layer": k, "smooth_members": len(smooth), "smooth_residual_with_all_hubs": base, "fibers_with_demand": len(demand),
           "total_demand_D": D, "demands": {str(p): [demand[p], len(hubs_of[p])] for p in sorted(demand)}}
    if D and base == 0:
        # search assignments: fiber by fiber, choose d_p distinct hubs from its list; test the smooth sub-instance
        order = sorted(demand, key=lambda p: len(hubs_of[p]))
        tried = [0]; found = [None]
        def rec(i, used):
            if found[0] is not None or tried[0] > 200000: return
            if i == len(order):
                tried[0] += 1
                sl2 = {x: lists[x] - used for x in smooth}
                if not C.residual(smooth, sl2):
                    found[0] = sorted(used)
                return
            p = order[i]
            for combo in itertools.combinations([f for f in hubs_of[p] if f not in used], demand[p]):
                rec(i + 1, used | set(combo))
                if found[0] is not None: return
        rec(0, frozenset())
        out["assignments_tried"] = tried[0]
        out["assignment_keeping_smooth_playable"] = found[0]
        if found[0] is None and tried[0] <= 200000:
            out["verdict"] = "NO assignment keeps the smooth sub-instance playable: the leaf violates the hub-demand condition"
        elif found[0] is None:
            out["verdict"] = "search cut off"
        else:
            out["verdict"] = "an assignment exists; condition satisfied here"
        # how much do the smooth members stall under the greedy worst assignment?
    print(json.dumps(out), flush=True)
