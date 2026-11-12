#!/usr/bin/env python3
"""Referee's check of the corollaries: x_G against the chain's delta at every prime and odd semiprime >= 189 (A2), at
the other exchanges (A1's exchange law), and against the shadow of n at every exchange.
    nice -n 19 python3 -I check_a2.py"""
import csv
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops/check-a")
sys.argv = [sys.argv[0], "5060"]
import check_a  # noqa: E402

N = check_a.N
spf = check_a.spf
rows = {int(r["n"]): r for r in csv.DictReader(open(check_a.SETTLE))}


def factor_mult(x):
    out = []
    while x > 1:
        out.append(spf[x])
        x //= spf[x]
    return out


primes = [p for p in range(2, N + 1) if spf[p] == p]
below = {}
for i, p in enumerate(primes[1:], 1):
    below[p] = primes[i - 1]


def shadow(n):
    s = 1
    for p in factor_mult(n):
        s *= below[p]
    return s


tally = {"prime": [0, []], "odd semiprime >= 189": [0, []], "other exchange": [0, []]}
not_shadow = []
prev = check_a.greedy_basis(2)
for n in range(3, N + 1):
    cur = check_a.greedy_basis(n)
    if n % 2 == 1:
        combo = check_a.represent(prev[1], check_a.VEC[n])
        if combo is not None:
            C = [s for s in range(n) if combo >> s & 1]
            xG = min(C)
            f = factor_mult(n)
            kind = "prime" if len(f) == 1 else ("odd semiprime >= 189" if len(f) == 2 and n >= 189 else "other exchange")
            delta = int(rows[n]["delta"])
            tally[kind][0] += 1
            if delta != xG:
                tally[kind][1].append((n, delta, xG, int(rows[n]["rise"])))
            if xG != shadow(n):
                not_shadow.append((n, xG, shadow(n)))
    prev = cur
for k, (c, bad) in tally.items():
    print(f"{k}: {c} games; delta != x_G at {len(bad)}: {bad[:20]}")
print("x_G != shadow at", len(not_shadow), "exchanges:", not_shadow[:20])
