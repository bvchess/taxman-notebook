#!/usr/bin/env python3
"""The 12P theorem's hypotheses at the 12P games of 8192..10000, with U* by descending greedy (the arrival file ends
at 8191).   nice -n 19 python3 -I study/twelvep_hyp_tail.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
spf = exch.spf
exact = short = 0; shortlist = []; bad = []
for n in range(8196, 10001, 12):
    P = n // 12
    if spf[P] != P: continue
    P1 = prev_prime(P)
    u = exch.ustar_greedy(n)
    h2 = all(y in u for y in (8 * P, 8 * P1, 12 * P1))
    ts = [t for t in range(int(4 * P / 3) + 1, int(1.5 * P) + 1) if spf[t] == t and 8 * t in u]
    h4 = 15 * P1 > 12 * P
    if not (h2 and ts and h4):
        bad.append((n, h2, bool(ts), h4)); continue
    t1 = max(ts)
    if 4 * t1 >= 6 * P1: exact += 1
    else: short += 1; shortlist.append((n, 6 * P1 - 4 * t1))
    print(n, "ok", 4 * t1 >= 6 * P1); sys.stdout.flush()
print(f"12P games 8192..10000 meeting the hypotheses: {exact + short}; law proved given U: {exact}; only delta >= 4t': {short} {shortlist}; failures: {bad}")
