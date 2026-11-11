#!/usr/bin/env python3
"""For several smoothness bounds B: does H's layer instance restricted to B-smooth members stall under peel?"""
import json, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore"); sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-1")
import parity as P
import cores as C
from pbsmooth import smooth_flags
n = int(sys.argv[1])
om, mf = P.omega_and_mf(n)
d = P.board(n)
h = set(d["greedy_basis"] + d["heaviest_low"])
for B in (5, 7, 11, 13, 17, 19, 23):
    sm = smooth_flags(n, B)
    row = {"n": n, "B": B}
    for k in sorted({om[x] for x in h}):
        layer = [x for x in h if om[x] == k and sm[x]]
        if not layer: continue
        lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
        r = C.residual(layer, lists)
        if r:
            row["L%d" % k] = "%d/%d" % (len(r), len(layer))
    print(json.dumps(row), flush=True)
