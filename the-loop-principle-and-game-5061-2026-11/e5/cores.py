#!/usr/bin/env python3
"""E5: where the parity bound's change parts from the game's, at 2512 (rise +98) and at 688, 1328, 1460 (rise -2,
-32, -39): the exchanges, the circuits behind them, and the odd cores they make in the recorded sets.

    nice -n 19 python3 -I e5/cores.py > e5/cores_out.txt      # from the loops folder, after paritydump

Words as in analyze.py.  The *defect* of board m is the pair (I - S, S - I) for S the recorded optimal set of m and I
the heaviest set independent at both parities nearest it (near_game); PB(m) - opt(m) = sum(I - S) - sum(S - I).  A
probe applies an exchange to a recorded set S: it reports whether S - out + in is independent at both parities and an
inclusion-minimal core of its own instance (odd when its lists are independent over GF(2)).
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import oddcore as oc  # noqa: E402
import patterns  # noqa: E402
import predict  # noqa: E402

common = predict.common
HERE = os.path.dirname(os.path.abspath(__file__))
res = common.results()
sets, change = {}, {}
for t in open(os.path.join(HERE, "paritydump.jsonl")):
    r = json.loads(t)
    if "set" in r:
        sets[(r["n"], r["m"], r["variant"])] = set(r["set"])
    elif r["variant"] == "game_change":
        change[r["n"]] = r


def labeler(n):
    pj = patterns.primes_around(common.factor(n)[-1])

    def lab(w):
        cell = patterns.label(w, pj)
        f = "·".join(map(str, common.factor(w)))
        return f"{w}=({cell[0]},{cell[1]})" if cell else f"{w}={f}"
    return lab


def fmt(ws, lab):
    return " ".join(lab(w) for w in sorted(ws)) or "-"


def probe(m, out, inn, lab):
    S = set(res[m]["moves"])
    assert set(out) <= S and not set(inn) & S, (m, out, inn)
    T = (S - set(out)) | set(inn)
    ind, why = oc.independent(m, T)
    core, lists = oc.minimal_core(T)
    kind = ("odd" if oc.is_odd(lists) else "not odd") if core else ""
    print(f"  probe on S({m}): - {sorted(out)} + {sorted(inn)} (worth {sum(inn) - sum(out):+d}): independent at both "
          f"parities {ind}; " + (f"a minimal core, {kind}, {len(core)} members: {fmt(core, lab)}" if core
                                 else "playable"))
    return ind, core


def defect(n, lab):
    for m, key in ((n - 1, (n, n - 1, "near_game")), (n, (n, n, "near_game"))):
        I, S = sets[key], set(res[m]["moves"])
        print(f"  defect of {m} (PB - opt = {sum(I) - sum(S)}): parity only {fmt(I - S, lab)}  |  recorded only "
              f"{fmt(S - I, lab)}")


def main():
    n = 2512
    lab = labeler(n)
    print(f"== {n}: rise +98")
    defect(n, lab)
    I0 = sets[(n, n - 1, "near_game")]
    D, A = set(change[n]["dropped"]), set(change[n]["added"])
    J = (sets[(n, n - 1, "with_change")] - D) | A | {n}
    for name, m, I in (("I(2511), every heaviest set of 2511 holds D", n - 1, I0),
                       ("J = I(2511) - D + A + n on 2512", n, J)):
        for parity in (0, 1):
            c = oc.circuit(m, I, 931, parity)
            print(f"  circuit of 931 at parity {parity} in {name}: "
                  + ("none (931 is independent of it)" if c is None else f"{len(c)} members: {fmt(c, lab)}"))
    for m in (n - 1, n):
        probe(m, [833], [931], lab)
    print()

    n = 688
    lab = labeler(n)
    print(f"== {n}: rise -2")
    defect(n, lab)
    I0 = sets[(n, n - 1, "near_game")]
    for parity in (0, 1):
        c = oc.circuit(n - 1, I0, 44, parity)
        print(f"  circuit of 44 at parity {parity} in I(687): "
              + ("none" if c is None else f"{len(c)} members: {fmt(c, lab)}"))
    pairs = [(44, 68), (238, 266), (325, 275)]
    for r in range(1, 4):
        for sub in itertools.combinations(pairs, r):
            probe(n - 1, [a for a, _ in sub], [b for _, b in sub], lab)
    print()

    n = 1328
    lab = labeler(n)
    print(f"== {n}: rise -32")
    defect(n, lab)
    W = sets[(n, n - 1, "with_change")]
    print(f"  heaviest sets of 1327 against the heaviest with D forced and A barred (worth "
          f"{sum(I0 := sets[(n, n - 1, 'near_game')]) - sum(W)}): {fmt(I0 - W, lab)}  |  {fmt(W - I0, lab)}")
    probe(n - 1, [44], [76], lab)
    for parity in (0, 1):
        c = oc.circuit(n - 1, I0, 44, parity)
        print(f"  circuit of 44 at parity {parity} in I(1327): "
              + ("none" if c is None else f"{len(c)} members: {fmt(c, lab)}"))
    print()

    n = 1460
    lab = labeler(n)
    print(f"== {n}: rise -39")
    defect(n, lab)
    I0, W = sets[(n, n - 1, "near_game")], sets[(n, n - 1, "with_change")]
    print(f"  heaviest sets of 1459 against the heaviest with D forced and A barred (worth {sum(I0) - sum(W)}): "
          f"{fmt(I0 - W, lab)}  |  {fmt(W - I0, lab)}")
    for parity in (0, 1):
        c = oc.circuit(n - 1, I0, 316, parity)
        print(f"  circuit of 316 at parity {parity} in I(1459): "
              + ("none" if c is None else f"{len(c)} members: {fmt(c, lab)}"))
    probe(n - 1, [588], [567], lab)


if __name__ == "__main__":
    main()
