#!/usr/bin/env python3
"""Sanity checks for signcheck.py: (1) the theta core of board 45 is GF(3)-dependent under the plain signing (det 3);
(2) K78 (det 1) is not, but some signing kills it (B5); (3) T11 at 5000: random NON-uniform signings (one sign per
entry) -- how many of a sample kill it?"""
import json, random, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore"); sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-1")
from signcheck import rank_gf3, template_cores, largest_prime
random.seed(7)

def rank_with(core, lists, sign):
    cols = sorted({f for x in core for f in lists[x]}); ci = {c: i for i, c in enumerate(cols)}
    rows = []
    for x in core:
        row = [0] * len(cols)
        for f in lists[x]:
            row[ci[f]] = sign(x, f)
        rows.append(row)
    return rank_gf3(rows), len(core)

theta = [12, 18, 20, 30, 45]; tl = {12: [4, 6], 18: [6, 9], 20: [4, 10], 30: [6, 10, 15], 45: [9, 15]}
print("theta45 plain rank/members:", rank_with(theta, tl, lambda x, f: 1))
k78 = [28, 30, 42, 45, 50, 52, 63, 75, 78]
kl = {28: [4, 14], 30: [6, 10, 15], 42: [6, 14, 21], 45: [9, 15], 50: [10, 25], 52: [4, 26], 63: [9, 21], 75: [15, 25], 78: [6, 26]}
print("K78 plain rank/members:", rank_with(k78, kl, lambda x, f: 1))
hits = 0
for _ in range(2000):
    s = {(x, f): random.choice((1, 2)) for x in k78 for f in kl[x]}
    r, m = rank_with(k78, kl, lambda x, f: s[(x, f)])
    hits += r < m
print("K78: random entrywise signings that kill it:", hits, "of 2000")
for core, lists in template_cores(5000):
    pat = tuple(sorted({x // largest_prime(x) for x in core}))
    if pat != (12, 18, 20, 27, 30):
        continue
    hits = 0
    N = 20000
    for _ in range(N):
        s = {(x, f): random.choice((1, 2)) for x in core for f in lists[x]}
        r, m = rank_with(core, lists, lambda x, f: s[(x, f)])
        hits += r < m
    print("T11 at 5000: random entrywise signings that kill it:", hits, "of", N, "| entries:", sum(len(lists[x]) for x in core))
    break
