#!/usr/bin/env python3
"""The worked examples of the loops brief: for each n, the change from the optimal set of n - 1 to that of n, in cells
k·P_j, the rows of the change across the columns, the residual of S(n - 1) + n, and the payments of the cells involved
in a scheme of each optimal set (peel's front and back moves, as the succession study's edges.py makes them).

    nice -n 19 python3 -I examples.py N [N ...] > examples_out.txt
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/home/brian/taxman_work/lab/work/succession/study")
import predict  # noqa: E402
import patterns  # noqa: E402
from edges import payments  # noqa: E402

common = predict.common
spf = predict.spf


def cell(w, pj):
    lab = patterns.label(w, pj)
    if lab is None:
        return "·".join(map(str, common.factor(w)))
    k, j = lab
    return f"{k}·P{j}" if j >= 0 else f"{k}·P+{-j}"


def show(n, res):
    S0, S1 = set(res[n - 1]["moves"]), set(res[n]["moves"])
    f = common.factor(n)
    P = f[-1]
    c = n // P
    pj = patterns.primes_around(P)
    D, A = sorted(S0 - S1), sorted(S1 - S0 - {n})
    delta = res[n - 1]["score"] + n - res[n]["score"]
    print(f"== {n} = {'·'.join(map(str, f))}, cofactor {c}; P0..P4 = {[pj[j] for j in range(5)]}; "
          f"opt(n-1) = {res[n - 1]['score']}, opt(n) = {res[n]['score']}, delta = {delta}; "
          f"window clean to depth {patterns.clean_depth(n)}")
    print(f"  D = {[(w, cell(w, pj)) for w in D]}; A = {[(w, cell(w, pj)) for w in A]}; "
          f"sum D - sum A = {sum(D) - sum(A)}")
    C = predict.cluster(n)
    print(f"  cluster C(n) in S(n-1): {sorted(C & S0)}; boxpeel = {next((y for y in sorted(C & S0) if common.playable((S0 | {n}) - {y}, n, spf)), None)}")
    R = common.residual(S0 | {n}, spf)
    print(f"  residual of S(n-1) + n: {len(R)} members: {[(w, cell(w, pj)) for w in sorted(R)]}")
    rows = sorted({patterns.label(w, pj)[0] for w in D + A + [n] if patterns.label(w, pj)})
    for k in rows:
        line = []
        for j in range(-1, 6):
            if pj[j] is None or k * pj[j] > n:
                continue
            w = k * pj[j]
            tag = ("n" if w == n else "") + ("a" if w in S0 else ".") + ("b" if w in S1 else ".")
            line.append(f"{k}·P{j}={w}:{tag}")
        print(f"  row {k}: " + "  ".join(line) + "   (a: move of n-1, b: move of n)")
    rows_up = {m for k in rows for m in range(k, c + 1, k)}
    ladder = sorted(w for w in S0 | S1 | {n} if patterns.label(w, pj) and -1 <= patterns.label(w, pj)[1] <= 4
                    and patterns.label(w, pj)[0] in rows_up)
    for board, S in ((n - 1, S0), (n, S1)):
        pay = payments(S, board)
        print(f"  board {board}, the moves of those rows and their multiples up to c, in columns P-1..P4, and what they pay with: " +
              ", ".join(f"{w} ({cell(w, pj)}) pays {pay[w]}" for w in ladder if w in S))
    for board, S in ((n - 1, S0), (n, S1)):
        pay = payments(S, board)
        inv = {}
        for m, g in pay.items():
            inv.setdefault(g, []).append(m)
        involved = sorted(set(D + A + [n]) & S)
        txt = []
        for w in involved:
            txt.append(f"{w} pays {pay[w]}")
        facs = sorted({g for w in set(D + A + [n]) for g in predict.MF[w]})
        own = [f"{g}<-{inv.get(g, ['-'])}" + ("(move)" if g in S else "") for g in facs]
        print(f"  board {board}: {'; '.join(txt)}")
        print(f"    the maximal factors of D, A and n, and who pays with them: {', '.join(own)}")
    print()


def main():
    res = common.results()
    for a in sys.argv[1:]:
        show(int(a), res)


if __name__ == "__main__":
    main()
