#!/usr/bin/env python3
"""Pattern games past 5060: does a family's law, applied to the best-known game of n - 1, give a game of n that beats
the best-known game of n?

    nice -n 19 python3 -I improve.py > improve_out.txt      # after predict.py and patterns.py

For every searched game n of 5061..10000 (predict.load_rows) and every pattern of its cofactor family seen on a
searched game of 187..5060 (patterns.py's column patterns, each distinct one once), take S, the best-known set of
n - 1; if every cell the pattern gives up is a move of S and every cell it takes up is a number of 2..n - 1 that is not, the set
S - D + A + n is tested by peel on board n.  A playable one is a game of n scoring best-known(n - 1) + n - (value of
the pattern at n).  Printed: every game where such a set scores more than the best-known score of n, and the counts;
those games' moves (as a set, in increasing order; peel gives an order) go to improved.jsonl.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import predict  # noqa: E402
import patterns  # noqa: E402

common = predict.common
spf = predict.spf


def cells(pat, n):
    P = common.factor(n)[-1]
    pj = patterns.primes_around(P)
    out = []
    for part in pat:
        side = []
        for k, j in part:
            if pj.get(j) is None:
                return None
            side.append(k * pj[j])
        out.append(side)
    return out


def main():
    rows = predict.load_rows()
    best = predict.load_best()
    best[5060] = common.results()[5060]
    fam = {}
    for r in rows:
        if r["range"] == "chain":
            pat = patterns.pattern(r)
            if pat is not None:
                fam.setdefault(r["cofactor"], set()).add(pat)
    tried = applied = better = 0
    out = open(os.path.join(predict.HERE, "improved.jsonl"), "w")
    for r in rows:
        if r["range"] != "past":
            continue
        n = r["n"]
        S = set(best[n - 1]["moves"])
        top = None
        for pat in sorted(fam.get(r["cofactor"], ())):
            cl = cells(pat, n)
            if cl is None:
                continue
            d, a = cl
            if (not all(w in S for w in d) or any(w in S or w >= n or w < 2 for w in a) or len(set(d)) != len(d)
                    or len(set(a)) != len(a)):
                continue
            value = sum(d) - sum(a)
            if value >= r["delta"]:
                continue
            tried += 1
            T = (S - set(d)) | set(a) | {n}
            if common.playable(T, n, spf):
                applied += 1
                if top is None or value < top[0]:
                    top = (value, patterns.show(pat), sorted(T))
        if top is not None:
            better += 1
            print(f"{n} ({r['step']}, cofactor {r['cofactor']}): best-known delta {r['delta']}, pattern game delta "
                  f"{top[0]} by {top[1]}: a game of n {r['delta'] - top[0]} above best-known(n) = "
                  f"{best[n]['score']}, scoring {best[n - 1]['score'] + n - top[0]}", flush=True)
            assert sum(top[2]) == best[n - 1]["score"] + n - top[0]
            out.write(json.dumps({"n": n, "score": sum(top[2]), "best_known": best[n]["score"], "moves": top[2]}) + "\n")
    print(f"pattern sets below the best-known delta tried: {tried}; playable: {applied}; games improved: {better}")


if __name__ == "__main__":
    main()
