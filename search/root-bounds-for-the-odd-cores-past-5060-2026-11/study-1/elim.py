#!/usr/bin/env python3
"""Elimination graph of sampled minimal cores: how many can one matroid exclude?

For a layer's residual of H, sample many minimal cores (deletion filter from random orders), then for each pair
(C1, C2) sharing an element e, test whether (C1 u C2) - e is core-free (peel empties it).  If so, no matroid containing
the playable sets has both as circuits (brief, Section 4 lemma).  Report the independence number of the graph
'incompatible' (greedy + exact for small graphs) = the most minimal cores any one matroid could exclude.
"""
import json, math, random, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P
import cores as C

def max_indep(adj, nodes):
    """Exact maximum independent set by simple branching (small graphs)."""
    best = []
    order = sorted(nodes, key=lambda v: -len(adj[v]))
    def rec(cand, chosen):
        nonlocal best
        if len(chosen) + len(cand) <= len(best):
            return
        if not cand:
            best = list(chosen); return
        v = cand[0]
        rec([u for u in cand[1:] if u not in adj[v]], chosen + [v])
        rec(cand[1:], chosen)
    rec(order, [])
    return best

random.seed(1)
n = int(sys.argv[1]); samples = int(sys.argv[2]) if len(sys.argv) > 2 else 60
om, mf = P.omega_and_mf(n)
d = P.board(n)
h = set(d["greedy_basis"] + d["heaviest_low"])
for k, r in d["residual"].items():
    k = int(k)
    layer = [x for x in h if om[x] == k]
    lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
    res = set(r["members"])
    cores = []
    seen = set()
    for _ in range(samples):
        order = list(res); random.shuffle(order)
        c = C.minimal_core(res, lists, order)
        if c and frozenset(c) not in seen:
            seen.add(frozenset(c)); cores.append(frozenset(c))
    m = len(cores)
    adj = {i: set() for i in range(m)}
    pairs = tested = 0
    for i in range(m):
        for j in range(i + 1, m):
            shared = cores[i] & cores[j]
            if not shared: continue
            pairs += 1
            for e in shared:
                tested += 1
                if not C.residual((cores[i] | cores[j]) - {e}, lists):
                    adj[i].add(j); adj[j].add(i); break
    mis = max_indep(adj, list(range(m))) if m <= 60 else None
    sizes = sorted(len(c) for c in cores)
    print(json.dumps({"n": n, "layer": k, "residual": len(res), "distinct_cores": m, "sizes": [sizes[0], sizes[len(sizes)//2], sizes[-1]],
                      "pairs_sharing": pairs, "incompatible_pairs": sum(len(a) for a in adj.values()) // 2,
                      "max_cores_one_matroid_can_exclude": len(mis) if mis is not None else "n/a",
                      "union_of_cores": len(set().union(*cores)) if cores else 0}), flush=True)
