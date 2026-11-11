#!/usr/bin/env python3
"""E3 cross-check on the proven chain: at every 8P game (P prime) of 232..5060 with 9P1 > 8P, the single-loss game
S*(n-1) - 4P1 + 8P is playable on board n and scores opt(n-1) + n - 4P1 = opt(n).
    nice -n 19 python3 -I study/eightp_check.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
spf = exch.spf
res = exch.results()
ok = bad = 0
for n in range(232, 5061, 8):
    P = n // 8
    if spf[P] != P: continue
    P1 = prev_prime(P)
    if 9 * P1 <= 8 * P: continue
    S0 = set(res[n-1]["moves"])
    game = (S0 - {4 * P1}) | {n}
    playable = 4 * P1 in S0 and common.playable(game, n, spf)
    exact = res[n-1]["score"] + n - 4 * P1 == res[n]["score"]
    if playable and exact: ok += 1
    else:
        bad += 1; print("  problem at", n, "4P1 in S*(n-1)?", 4*P1 in S0, "playable?", playable, "delta = 4P1?", exact)
print(f"8P games 232..5060 with 9P1 > 8P: {ok} pass, {bad} fail")
