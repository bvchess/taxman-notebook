#!/usr/bin/env python3
"""How many distinct minimal cores does the smooth-only sub-instance of H hold?  Sampling by random deletion orders."""
import json, random, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore"); sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-1")
import parity as P
import cores as C
from pbsmooth import smooth_flags
random.seed(2)
n = int(sys.argv[1]); samples = int(sys.argv[2]); B = int(sys.argv[3]) if len(sys.argv) > 3 else 23
om, mf = P.omega_and_mf(n)
sm = smooth_flags(n, B)
d = P.board(n)
h = set(d["greedy_basis"] + d["heaviest_low"])
for k in sorted({om[x] for x in h}):
    layer = [x for x in h if om[x] == k and sm[x]]
    lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
    res = C.residual(layer, lists)
    if not res:
        continue
    seen = {}
    growth = []
    for i in range(samples):
        order = list(res); random.shuffle(order)
        c = frozenset(C.minimal_core(res, lists, order))
        seen[c] = seen.get(c, 0) + 1
        if (i + 1) % (samples // 5) == 0:
            growth.append(len(seen))
    sizes = sorted(len(c) for c in seen)
    freemem = sorted(sum(1 for x in c if x <= n // 2) for c in seen)
    pool = set().union(*(lists[x] for x in res))
    print(json.dumps({"n": n, "B": B, "layer": k, "smooth_members": len(layer), "smooth_residual": len(res), "pool": len(pool),
                      "wide": sum(len(lists[x]) >= 3 for x in res), "samples": samples, "distinct_cores_after_each_fifth": growth,
                      "core_sizes_min_med_max": [sizes[0], sizes[len(sizes)//2], sizes[-1]],
                      "free_members_per_core_min_med_max": [freemem[0], freemem[len(freemem)//2], freemem[-1]]}), flush=True)
