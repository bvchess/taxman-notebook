#!/usr/bin/env python3
"""21P: the regime of each game from 2000 on against the holder of hub 18 and the moves 6P, 9P, 10P in game n - 1.
    nice -n 19 python3 -I study/family21_regimes.py"""
import sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops/study")
import predict, patterns, hubs  # noqa: E402
common = predict.common
res = common.results()
best = predict.load_best()
rows = [r for r in predict.load_rows() if r["cofactor"] == 21 and r["n"] >= 2000]
print("n | range | depth | delta | delta_pb | rise | regime by delta | n-1: hub 18 holder; 6P, 9P, 10P moves? | n: 10P move?")
for r in rows:
    n, P = r["n"], r["P"]
    pj = patterns.primes_around(P)
    S = set(res[n - 1]["moves"]) if n - 1 <= 5060 else set(best[n - 1]["moves"])
    pay = hubs.scheme(S, n - 1)
    h18 = next((hubs.cell(x, pj) for x, f in pay.items() if f == 18), "-" if 18 in S else ".")
    d, pb = r["delta"], r["delta_pb"]
    regime = "i (P)" if d == P else ("ii (6P-rec)" if 6 * P in r["dropped"] else "other")
    Sn = set(res[n]["moves"]) if n <= 5060 else set(best[n]["moves"])
    print(f"{n} | {r['range']} | {patterns.clean_depth(n)} | {d} | {pb} | {d - pb} | {regime} | {h18}; "
          f"{6*P in S}, {9*P in S}, {10*P in S} | {10*P in Sn}")
