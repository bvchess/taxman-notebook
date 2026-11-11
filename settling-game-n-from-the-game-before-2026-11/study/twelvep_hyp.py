#!/usr/bin/env python3
"""Hypotheses of the 12P theorem (given U) at every 12P game (P prime) of 228..8191: 8P, 8P1, 12P1 in U*(n); a prime
t' in (4P/3, 1.5P] with 8t' in U*(n) (take the largest); 15P1 > 12P; and whether 4t' >= 6P1 (then the law is proved
given U) or not (then only delta >= 4t' is proved).   nice -n 19 python3 -I study/twelvep_hyp.py"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
spf = exch.spf
searched = {int(r["n"]): r for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "searched.csv")))}
past = {int(r["n"]): r for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "past5060.csv")))}
arr = exch.arrival()
u = {2}
exact = short = 0; bad = []; shortlist = []
for n in range(3, 8192):
    row = arr[n]; u = (u | set(row["added"])) - set(row["dropped"])
    if n % 12 or spf[n // 12] != n // 12 or n < 228: continue
    P = n // 12; P1 = prev_prime(P)
    h2 = all(y in u for y in (8 * P, 8 * P1, 12 * P1))
    ts = [t for t in range(int(4 * P / 3) + 1, int(1.5 * P) + 1) if spf[t] == t and 8 * t in u]
    h3 = bool(ts); h4 = 15 * P1 > 12 * P
    t1 = max(ts) if ts else None
    if not (h2 and h3 and h4):
        bad.append((n, h2, h3, h4)); continue
    kind = searched[n]["step"] if n in searched else (past[n]["kind"] if n in past else "?")
    if 4 * t1 >= 6 * P1: exact += 1
    else:
        short += 1; shortlist.append((n, 6 * P1 - 4 * t1))
print(f"12P games 228..8191 meeting all hypotheses: {exact + short}; law proved given U (4t' >= 6P1): {exact}; "
      f"only delta >= 4t' proved: {short}, short of the law by (n, 6P1 - 4t'): {shortlist}")
print("hypothesis failures (n, 8P/8P1/12P1 in U*, some 8t' in U*, 15P1 > 12P):", bad)
