#!/usr/bin/env python3
"""The cascade predictor: a single loss or a single down-shift in the cluster, then up-shifts along the columns.

    nice -n 19 python3 -I chain.py          # writes chain.jsonl as it goes, resumes; after predict.py

For the searched games from 187 on, the chain's first.  S is the optimal set of n - 1 (committed to 5060, best-known
past it, as in predict.py); cells, columns and P_j are those of patterns.py.  A *start* gives up one member y of
C(n) ∩ S, or moves it down its row (y = k·P_j
replaced by k·P_i, i = j + 1 .. j + 4, a number not in S); it must make S + n playable (peel), and it costs y, or the
fall in value.  From the two cheapest starts the predictor then makes *up-shifts* while one is playable: a move
z = k·P_j of the set with 1 <= j <= 4 and k <= c is replaced by k·P_(j-1), the largest gain first (at most 30
candidates a round, at most 6 rounds).  The value is the cheapest cost reached.  Each step is a game of n, so
delta(n) <= cascade(n) <= boxpeel(n).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import predict  # noqa: E402
import patterns  # noqa: E402

common = predict.common
spf = predict.spf
OUT = os.path.join(predict.HERE, "chain.jsonl")


def playable(T, n):
    return common.playable(T, n, spf)


def cascade(S, n):
    P = common.factor(n)[-1]
    c = n // P
    pj = patterns.primes_around(P)
    C = predict.cluster(n)
    starts = []
    for y in sorted(C & S):
        starts.append((y, None, y))
        lab = patterns.label(y, pj)
        if lab:
            k, j = lab
            for i in range(j + 1, j + 5):
                if i <= patterns.J and pj.get(i) and k * pj[i] not in S and k * pj[i] > 1:
                    starts.append((y, k * pj[i], y - k * pj[i]))
    starts.sort(key=lambda s: s[2])
    good = []
    for y, y2, cost in starts:
        T = (S - {y}) | {n} | ({y2} if y2 else set())
        if playable(T, n):
            good.append((cost, T, y, y2))
            if len(good) == 2:
                break
    if not good:
        return None, None
    best, how = None, None
    for cost, T, y, y2 in good:
        steps = []
        for _ in range(6):
            cands = []
            for z in T:
                lab = patterns.label(z, pj)
                if not lab:
                    continue
                k, j = lab
                if 1 <= j <= 4 and k <= c:
                    up = k * pj[j - 1]
                    if up not in T and up < n:
                        cands.append((up - z, z, up))
            cands.sort(reverse=True)
            moved = False
            for gain, z, up in cands[:30]:
                T2 = (T - {z}) | {up}
                if playable(T2, n):
                    T, cost = T2, cost - gain
                    steps.append([z, up])
                    moved = True
                    break
            if not moved:
                break
        if best is None or cost < best:
            best, how = cost, {"y": y, "to": y2, "ups": steps}
    return best, how


def main():
    rows = predict.load_rows()
    todo = sorted((r for r in rows if r["n"] >= 187), key=lambda r: r["n"])
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(t)["n"] for t in open(OUT) if t.strip()}
    res = common.results()
    best = predict.load_best()
    print(f"games: {len(todo)}, done {len(done)}", flush=True)
    with open(OUT, "a") as out:
        for r in todo:
            n = r["n"]
            if n in done:
                continue
            S = set(res[n - 1]["moves"] if n - 1 <= 5060 else best[n - 1]["moves"])
            v, how = cascade(S, n)
            out.write(json.dumps({"n": n, "cascade": v, "how": how, "delta": r["delta"]}) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
