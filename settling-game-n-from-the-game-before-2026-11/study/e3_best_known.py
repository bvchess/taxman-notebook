#!/usr/bin/env python3
"""E3: Theorem 8P applied to the best-known games past 5060.  For every n = 8P (P prime, 9P1 > 8P) in 5061..10000:
the best-known game of n-1 (highest score per n in best-known.jsonl, the last if tied) less 4P1 plus 8P is playable on
board n (peel), and best-known(n) = best-known(n-1) + n - 4P1.  Then n is optimal whenever n-1 is (Theorem 8P).
    nice -n 19 python3 -I study/e3_best_known.py > study/e3_best_known_out.txt"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
spf = exch.spf
BEST = "/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl"
best = {}
with open(BEST) as f:
    for line in f:
        if not line.strip(): continue
        r = json.loads(line); n = r["n"]
        if n not in best or r["score"] >= best[n]["score"]:
            best[n] = r
print(f"best-known lines: games {min(best)}..{max(best)}, {len(best)} games")
settled = []; short = []; missing = []
for n in range(5064, 10001, 8):
    P = n // 8
    if spf[P] != P: continue
    P1 = prev_prime(P)
    if 9 * P1 <= 8 * P:
        print(f"  {n} = 8*{P}: hypothesis 9P1 > 8P fails (P1 = {P1})"); continue
    if n not in best or n - 1 not in best:
        missing.append(n); continue
    S0 = set(best[n-1]["moves"]); s0, s1 = best[n-1]["score"], best[n]["score"]
    assert sum(S0) == s0
    game = (S0 - {4 * P1}) | {n}
    playable = (4 * P1 in S0) and common.playable(game, n, spf)
    law = s1 == s0 + n - 4 * P1
    if playable and law: settled.append(n)
    else:
        short.append(n)
        print(f"  {n} = 8*{P}, P1 = {P1}: 4P1 in best-known(n-1)? {4*P1 in S0}; single-loss game playable? {playable}; "
              f"best-known(n) - (best-known(n-1) + n - 4P1) = {s1 - (s0 + n - 4*P1)}")
print(f"8P games 5061..10000 with 9P1 > 8P: {len(settled) + len(short) + len(missing)}; settled by Theorem 8P given n-1: "
      f"{len(settled)}; not at the law or game not playable: {len(short)} {short}; missing from the file: {missing}")
print("settled:", settled)
