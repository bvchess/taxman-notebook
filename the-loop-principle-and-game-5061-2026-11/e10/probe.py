#!/usr/bin/env python3
"""E10: the configuration behind the rises at 5061, 3297 and 3507.

    nice -n 19 python3 -I e10/probe.py > e10/probe_out.txt      # from the loops folder, after paritydump

For each game: (1) the circuits, in the heaviest set I(n-1) of n - 1 nearest the recorded set, of the one cell 8q that
the parity bound's own change I(n-1) -> I(n) adds for 6P; (2) the parity bound's extra beyond the game's change
(J -> K, see analyze.py) applied to the recorded set of n: the residual of the result (the union of its cores; all
odd, the result being independent at both parities), by column, and the number of its members listing each factor;
(3) the one-cell reading, the recorded set of n plus 8q.  A number is shown as k·p, p its largest prime.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e5"))
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import oddcore as oc  # noqa: E402
import predict  # noqa: E402

common, spf, MF = predict.common, predict.spf, predict.MF
res = common.results()
best = predict.load_best()


def recorded(m):
    return set(res[m]["moves"]) if m <= 5060 else set(best[m]["moves"])


def lab(w):
    if w == 1:
        return "1"
    p = common.factor(w)[-1]
    return f"{w // p}·{p}"


def by_column(ws):
    out = {}
    for w in sorted(ws):
        p = common.factor(w)[-1]
        out.setdefault(p, []).append(w // p)
    return "; ".join(f"{p}: rows {rows}" for p, rows in sorted(out.items(), reverse=True))


def main():
    sets, change = {}, {}
    for t in open(os.path.join(HERE, "paritydump.jsonl")):
        r = json.loads(t)
        if "set" in r:
            sets[(r["n"], r["m"], r["variant"])] = set(r["set"])
        elif r["variant"] == "game_change":
            change[r["n"]] = r
    for n in (5061, 3297, 3507):
        P = common.factor(n)[-1]
        I0, I1 = sets[(n, n - 1, "near_game")], sets[(n, n, "near_prev")]
        added = I1 - I0 - {n}
        print(f"== {n} = 21·{P}: the parity bound's own change: out {sorted(map(lab, I0 - I1))}, in "
              f"{sorted(map(lab, added))}")
        for y in sorted(added):
            for parity in (0, 1):
                c = oc.circuit(n - 1, I0, y, parity)
                print(f"  circuit of {lab(y)} at parity {parity} in I({n - 1}): "
                      + ("none" if c is None else f"{len(c)} members, by column: {by_column(c)}"))
            for parity in (0, 1):
                c = oc.circuit(n, I1 - {y}, y, parity)
                print(f"  circuit of {lab(y)} at parity {parity} in I({n}) less it: " + ("none" if c is None else
                                                                                       by_column(c)))
        ch = change[n]
        D, A = set(ch["dropped"]), set(ch["added"])
        J = (sets[(n, n - 1, "with_change")] - D) | A | {n}
        K = sets[(n, n, "near_change")]
        S = recorded(n)
        T = (S - (J - K)) | (K - J)
        ind, _ = oc.independent(n, T)
        R = common.residual(T, spf)
        lists = {x: MF[x] - T for x in R}
        listed = Counter(f for fs in lists.values() for f in fs)
        print(f"  the extra applied to the recorded set: - {sorted(map(lab, J - K))} + {sorted(map(lab, K - J))} "
              f"(worth {sum(K - J) - sum(J - K)}); independent at both parities {ind}; residual {len(R)} members, by "
              f"column: {by_column(R)}")
        print("  factors its members list (count of members listing each): "
              + " ".join(f"{lab(f)}x{k}" for f, k in sorted(listed.items(), key=lambda fk: (fk[0] > 40, fk[0]))))
        ind1, why = oc.independent(n, S | added)
        print(f"  the one-cell reading, the recorded set of {n} plus {sorted(map(lab, added))}: independent "
              f"{ind1}" + ("" if ind1 else f" (dependent at parity {why[0]})"))
        print()


if __name__ == "__main__":
    main()
