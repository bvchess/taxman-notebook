#!/usr/bin/env python3
"""H's layer instance with every fiber member (largest prime > 23) stripped of its hub (the smooth maximal factor x/p):
does the whole instance, and the fiber part alone, then peel?  A relaxation 'hubs reserved for smooth members'."""
import json, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore"); sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-1")
import parity as P
import cores as C
from pbsmooth import smooth_flags
n = int(sys.argv[1])
om, mf = P.omega_and_mf(n)
sm = smooth_flags(n, 23)
d = P.board(n)
h = set(d["greedy_basis"] + d["heaviest_low"])
for k in sorted({om[x] for x in h}):
    layer = [x for x in h if om[x] == k]
    lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
    full = C.residual(layer, lists)
    if not full: continue
    nohub = {x: (lists[x] if sm[x] else set(f for f in lists[x] if not sm[f])) for x in layer}
    r_all = C.residual(layer, nohub)
    fib = [x for x in layer if not sm[x]]
    r_fib = C.residual(fib, nohub)
    hubs = sorted({f for x in fib for f in lists[x] if sm[f]})
    print(json.dumps({"n": n, "layer": k, "members": len(layer), "full_residual": len(full),
                      "hubs_listed_by_fiber_members": len(hubs), "residual_hubs_reserved_for_smooth": len(r_all),
                      "fiber_only_without_hubs_residual": "%d/%d" % (len(r_fib), len(fib)),
                      "fiber_members_with_empty_list_without_hubs": sum(1 for x in fib if not nohub[x])}), flush=True)
