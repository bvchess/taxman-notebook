#!/usr/bin/env python3
"""Checks the leaf of an e1_smooth run from the definitions alone, with the brief's parity.py and cores.py (no code of
the solver): the set S = G + the leaf's promotions, G the greedy GF(2) basis of the sources, must weigh PB_s, be
independent at both parities, keep the leaf's picks and avoid its bars, and have every B-smooth sub-instance playable
(an empty residual in every layer).  It also reports the residual of S's whole layer instances, which need not be empty,
as [members, of them B-smooth] by layer.

    python3 -I check_leaf.py RESULTS.jsonl     # every line of the file with a leaf (a stopped run's: PB_s_lower)
"""

import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import cores as C  # noqa: E402
import parity as P  # noqa: E402


def smooth(x, b):
    for p in range(2, b + 1):
        while x % p == 0:
            x //= p
    return x == 1


def check(line):
    n, b = line["n"], line["B"]
    om, mf = P.omega_and_mf(n)
    g = P.greedy_basis(n, om, mf)
    promo = line["leaf_promotions"]
    s = set(g) | set(promo)
    out = {"n": n, "B": b}
    out["greedy_basis_is_the_bag"] = sum(g) == line["in_the_bag"]
    out["weight_is_PB_s"] = sum(s) == (line["PB_s"] if line["finished"] else line["PB_s_lower"])
    out["picks_kept"] = set(line["leaf_picks"]) <= set(promo)
    out["bars_avoided"] = not (set(line["leaf_bars"]) & set(promo))
    independent = True
    for i in (0, 1):
        ech = P.Echelon()
        for x in sorted(s):
            v = P.parity_vector(x, i, n, om, mf)
            if v is not None and not ech.insert(v, 0):
                independent = False
    out["independent_at_both_parities"] = independent
    stalled, whole = {}, {}
    for k in sorted({om[x] for x in s}):
        layer = [x for x in s if om[x] == k]
        lists = {x: [f for f in mf[x] if f not in s] for x in layer}
        res = C.residual([x for x in layer if smooth(x, b)], lists)
        if res:
            stalled[k] = len(res)
        res = C.residual(layer, lists)
        if res:
            whole[k] = [len(res), sum(1 for x in res if smooth(x, b))]
    out["smooth_residual_by_layer"] = stalled
    out["whole_residual_by_layer"] = whole
    checks = ["greedy_basis_is_the_bag", "weight_is_PB_s", "picks_kept", "bars_avoided", "independent_at_both_parities"]
    out["ok"] = all(out[c] for c in checks) and not stalled
    return out


def main():
    for raw in open(sys.argv[1]):
        line = json.loads(raw)
        if line.get("leaf_promotions"):
            print(json.dumps(check(line)), flush=True)


if __name__ == "__main__":
    main()
