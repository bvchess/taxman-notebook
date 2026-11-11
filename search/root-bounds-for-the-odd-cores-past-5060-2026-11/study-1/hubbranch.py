#!/usr/bin/env python3
"""Hub-ownership branching at E1's leaf node for n (picks = leaf_picks, bars = leaf_bars): for a layer k with a hub
conflict, pick a hub a demanded by a fiber with a single listed hub.  Child S ("no fiber member pays a"): every
fiber member of layer k listing a loses coordinate a.  Child F ("a fiber member pays a"): every smooth member of
layer k listing a loses coordinate a.  Compare the children's parity bounds with the node's, and with the bounds of
the literal bars E11 would use: un-promote the fiber member's promoted fiber factor; bar a free smooth member of the
stalled residual; un-promote a column the residual lists."""
import json, sys, time
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

def max_matching(adj):
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

n = int(sys.argv[1]); K = int(sys.argv[2])  # the layer to branch in
leaf = None
for line in open("/home/brian/taxman_work/lab/work/oddcore/e1/results.jsonl"):
    d = json.loads(line)
    if d["n"] == n and d["B"] == 23 and d.get("finished"):
        leaf = d
om, mf = P.omega_and_mf(n)
g = P.greedy_basis(n, om, mf)
picks, bars = frozenset(leaf["leaf_picks"]), frozenset(leaf["leaf_bars"])
h = set(g) | set(leaf["leaf_promotions"])

def pv(x, i, proj):
    v = P.parity_vector(x, i, n, om, mf)
    if v is not None and x in proj and om[x] % 2 != i:
        v &= ~(1 << proj[x])
    return v

def bound(picks, bars, proj):
    """parity bound with picks, bars and projections {member: coordinate removed}; returns (weight, inset) or None."""
    bases = []
    for i in (0, 1):
        b = P.Echelon()
        for s in g:
            v = pv(s, i, proj)
            if v is not None and v and not b.insert(v, 0):
                pass  # a fixed source whose projected vector is dependent: the configuration is infeasible
            if v is not None and v == 0:
                return None
        for x in picks:
            v = pv(x, i, proj)
            if v is not None and (v == 0 or not b.insert(v, 0)):
                return None
        bases.append(b)
    vecs, ground = {}, []
    for x in range(2, n // 2 + 1):
        if x in bars or x in picks:
            continue
        vs = [pv(x, i, proj) for i in (0, 1)]
        if all(bases[i].reduce(vs[i])[0] for i in (0, 1)):
            vecs[x] = vs; ground.append(x)
    inset = []
    while True:
        index = {x: k for k, x in enumerate(inset)}
        echs = []
        for i in (0, 1):
            e = P.Echelon(bases[i])
            for k, x in enumerate(inset):
                e.insert(vecs[x][i], 1 << k)
            echs.append(e)
        outside = [y for y in ground if y not in index]
        circ = {0: {}, 1: {}}; free = {0: set(), 1: set()}
        for y in outside:
            for i in (0, 1):
                r, combo = echs[i].reduce(vecs[y][i])
                if r: free[i].add(y)
                else: circ[i][y] = [inset[k] for k in range(len(inset)) if combo >> k & 1]
        succ = {}
        for y, c in circ[1].items(): succ.setdefault(y, []).extend(c)
        for y, c in circ[0].items():
            for x in c: succ.setdefault(x, []).append(y)
        INF = (float("inf"), 0); dist, pred, frontier = {}, {}, []
        for y in free[0]:
            dist[y] = (-y, 0); pred[y] = None; frontier.append(y)
        while frontier:
            nxt = set()
            for u in frontier:
                du = dist[u]
                for v in succ.get(u, ()):
                    dv = (du[0] + (v if v in index else -v), du[1] + 1)
                    if dv < dist.get(v, INF):
                        dist[v] = dv; pred[v] = u; nxt.add(v)
            frontier = list(nxt)
        ends = [y for y in free[1] if y in dist]
        if not ends: break
        best = min(ends, key=lambda y: dist[y])
        if dist[best][0] >= 0: break
        path, u = [], best
        while u is not None:
            path.append(u); u = pred[u]
        for u in path:
            if u in index: inset.remove(u)
            else: inset.append(u)
    return sum(g) + sum(picks) + sum(inset), sorted(inset)

t0 = time.time()
layer = [x for x in h if om[x] == K]
lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
smooth = [x for x in layer if largest_prime(x) <= 23]
fibers = {}
for x in layer:
    p = largest_prime(x)
    if p > 23: fibers.setdefault(p, []).append(x)
# a fiber with demand whose members list a single hub
cand = []
for p, mem in fibers.items():
    adj = {x: [f for f in lists[x] if f % p == 0] for x in mem}
    dp = len(mem) - max_matching(adj)
    hubs = sorted({f for x in mem for f in lists[x] if f % p != 0})
    if dp > 0: cand.append((len(hubs), p, dp, hubs, mem))
cand.sort()
MODE = sys.argv[3] if len(sys.argv) > 3 else "contended"
if MODE == "contended":
    best = None
    for nh, p, dp, hubs, mem in cand:
        for hb in hubs:
            sl = sum(1 for x in smooth if hb in lists[x])
            key = (-sl, nh, hb)
            if sl and (best is None or key < best[0]): best = (key, p, dp, hubs, mem, hb)
    _, p, dp, hubs, mem, a = best
else:
    nh, p, dp, hubs, mem = cand[0]
    a = hubs[0]
fiber_listers = [x for x in layer if largest_prime(x) > 23 and a in lists[x]]
smooth_listers = [x for x in smooth if a in lists[x]]
print(json.dumps({"n": n, "layer": K, "hub": a, "fiber": p, "demand": dp, "fiber_members": len(mem), "fiber_listers_of_hub": len(fiber_listers),
                  "smooth_listers_of_hub": len(smooth_listers), "sources_among_fiber_listers": sum(x > n // 2 for x in fiber_listers)}), flush=True)
root = bound(picks, bars, {})
print(json.dumps({"node_bound": root[0], "PB_s_leaf": leaf["PB_s"], "seconds": round(time.time() - t0, 1)}), flush=True)
projS = {x: a for x in fiber_listers}
bS = bound(picks, bars, projS)
print(json.dumps({"child": "S: no fiber member pays the hub", "bound": bS[0] if bS else None, "drop": root[0] - bS[0] if bS else "infeasible", "seconds": round(time.time() - t0, 1)}), flush=True)
projF = {x: a for x in smooth_listers}
bF = bound(picks, bars, projF)
print(json.dumps({"child": "F: a fiber member pays the hub", "bound": bF[0] if bF else None, "drop": root[0] - bF[0] if bF else "infeasible", "seconds": round(time.time() - t0, 1)}), flush=True)
# E11-style literal bars for comparison
res = C.residual(smooth, {x: lists[x] - {a} for x in smooth})  # the smooth residual once the hub is gone
lits = []
for x in mem:  # promoted fiber factors of the demanding fiber's members
    for f in mf[x]:
        if f in h and f <= n // 2 and f % p == 0 and f not in picks: lits.append(("unpromote fiber factor", f))
for x in sorted(res):
    if x <= n // 2 and x not in picks: lits.append(("bar free smooth member", x))
for x in res:
    for f in mf[x]:
        if f in h and f <= n // 2 and f not in picks: lits.append(("unpromote column of the residual", f))
seen = set(); out = []
for kind, lit in lits:
    if lit in seen: continue
    seen.add(lit)
    if len(out) >= 6: break
    b = bound(picks, bars | {lit}, {})
    out.append({"literal": kind, "number": lit, "bound": b[0] if b else None, "drop": root[0] - b[0] if b else "infeasible"})
    print(json.dumps(out[-1] | {"seconds": round(time.time() - t0, 1)}), flush=True)
