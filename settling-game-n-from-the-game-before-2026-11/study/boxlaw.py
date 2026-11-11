#!/usr/bin/env python3
"""The box law, a test: for every odd n of layer 3 in 189..5060, let B = {p',p} x {q',q} x {r',r} (n = pqr).  If
B - n lies in the optimal set of n - 1, is delta(n) = min(B)?  Counts by outcome (searched/ceiling/repeat) and step.
    nice -n 19 python3 -I study/boxlaw.py > study/boxlaw_out.txt"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import box_of  # noqa: E402
spf = exch.spf
res = exch.results()
settle = {int(r["n"]): r for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "settle.csv")))}
stats = {}; misses = []
for n in range(189, 5061, 2):
    if exch.omega(n) != 3: continue
    B = box_of(n)
    if len(B) < 6: continue
    S0 = set(res[n-1]["moves"])
    if not (B - {n}) <= S0: continue
    x = min(B); delta = res[n-1]["score"] + n - res[n]["score"]
    r = settle[n]; key = (r["outcome"], r["step"], x > n / 2, delta == x)
    stats[key] = stats.get(key, 0) + 1
    if delta != x: misses.append((n, exch.fac_str(n), x, delta))
print("odd n of layer 3, 189..5060, whose box less n lies in S*(n-1): (outcome, step, x is a source, delta == min box): count")
for k in sorted(stats): print(" ", k, stats[k])
print("misses (n, factorization, min box, delta):", misses)
