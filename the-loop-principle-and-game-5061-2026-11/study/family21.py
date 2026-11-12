#!/usr/bin/env python3
"""The 21P family: payments of the cells of columns 0 and 1 and the hub holders in peel's scheme of the recorded sets
of n - 1 and n (committed to 5060, best-known past it), at chosen games.
    nice -n 19 python3 -I study/family21.py N [N ...]"""
import sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops/study")
import predict, patterns, hubs  # noqa: E402
common = predict.common
res = common.results()
best = predict.load_best()


def moves(m):
    return set(res[m]["moves"]) if m <= 5060 else set(best[m]["moves"])


HUBS = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21]
for n in map(int, sys.argv[1:]):
    P = common.factor(n)[-1]
    pj = patterns.primes_around(P)
    print(f"== {n} = 21·{P}, depth {patterns.clean_depth(n)}, P1 {pj[1]}, P-1 {pj[-1]}")
    for m in (n - 1, n):
        S = moves(m)
        pay = hubs.scheme(S, m)
        if pay is None:
            print("  peel failed at", m)
            continue
        holder = {f: hubs.cell(x, pj) for x, f in pay.items() if f in HUBS}
        print(f"  game {m} (score {'opt' if m <= 5060 else 'best-known'}): hubs " +
              " ".join(f"{k}:{holder.get(k, '-' if k in S else '.')}" for k in HUBS))
        for j in (0, 1, -1):
            cells = []
            for k in (4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21):
                w = k * pj[j]
                if w > m:
                    continue
                if w in S:
                    cells.append(f"{k}->{hubs.cell(pay[w], pj) if pay[w] not in HUBS else 'h' + str(pay[w])}")
                else:
                    cells.append(f"{k}:out")
            print(f"    column {j} (P_{j} = {pj[j]}): " + " ".join(cells))
