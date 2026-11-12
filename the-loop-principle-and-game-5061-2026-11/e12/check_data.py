#!/usr/bin/env python3
"""E12: the case tables against the committed chain.

    nice -n 19 python3 -I e12/check_data.py FAMILY [FAMILY ...]      # from the loops folder, after window_law.py

FAMILY is a key of window_law.FAMILIES.  A game past 5060 counts as *settled* (optimal if n - 1 is, given U and the
table's hypotheses) when its state is closed and its best-known delta equals the law; with open states in the table
the count holds only under the hypothesis that no optimal set of n is in one.

For every game n = c·P of 187..10000 (the chain to 5060, the best-known file's highest score past it) whose window
is clean to the family's depth: the cells of the recorded set of n; whether it holds every source cell (the
hypothesis U supplies) and has no core in the window instance (it must, being playable); its state in
table_cP.jsonl (closed or open); and, where closed, the witness's value sum(W') - sum(W) + n at this P against the
law and against delta(n) (proven to 5060, best-known past it).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import patterns  # noqa: E402
import predict  # noqa: E402
import window_law as wl  # noqa: E402

common = predict.common
res = common.results()
best = predict.load_best()


def game(m):
    """(score, moves): the committed chain to 5060, the best-known file's highest score past it."""
    return (res[m]["score"], res[m]["moves"]) if m <= 5060 else (best[m]["score"], best[m]["moves"])


def table_name(family):
    """16h8 -> 16Ph8, 21m1 -> 21Pm1, 16 -> 16P."""
    digits = re.match(r"\d+", family).group()
    return f"{digits}P{family[len(digits):]}"


def extra_prime(rule, P):
    kind, arg = rule
    if kind == "le":
        q = int(arg * P)
        while not predict.is_prime(q):
            q -= 1
        return q
    q = P
    for _ in range(arg):
        q += 1
        while not predict.is_prime(q):
            q += 1
    return q


def main():
    for family in sys.argv[1:]:
        c, d, law, extras = wl.FAMILIES[family]
        w = wl.Window(c, d, law, True, extras)
        name = table_name(family)
        rows = map(json.loads, open(os.path.join(HERE, f"table_{name}.jsonl")))
        table = {tuple(map(tuple, r["state_cells"])): r for r in rows}
        print(f"== {name} (depth {d}{', extra columns ' + ', '.join(e[0] for e in extras) if extras else ''})")
        counts = {"games": 0, "sources held": 0, "closed": 0, "open": 0, "law met by the witness": 0,
                  "outside the extra columns' intervals": 0, "settled past 5060": 0}
        for n in range(187, 10001):
            P = common.factor(n)[-1]
            if n != c * P or patterns.clean_depth(n) < d:
                continue
            pj = patterns.primes_around(P)
            prime = {j: pj[j] for j in range(d + 1)}
            inside = True
            for e, (_nm, rule, lo, hi) in enumerate(extras):
                q = extra_prime(rule, P)
                prime[d + 1 + e] = q
                inside &= lo * P < q <= hi * P
            if not inside:
                counts["outside the extra columns' intervals"] += 1
                print(f"  {n} = {c}·{P}: an extra column's prime is outside its interval; not covered")
                continue
            if any(2 * p * p <= n for p in prime.values()):
                counts["a region prime with 2p² <= n"] = counts.get("a region prime with 2p² <= n", 0) + 1
                print(f"  {n} = {c}·{P}: a prime of the region has 2p² <= n; the lemma does not apply")
                continue
            val = {(k, j): k * prime[j] for k, j in w.cells}
            S = set(game(n)[1])
            W = {x for x in w.cells if val[x] in S}
            counts["games"] += 1
            src = all(x in W for x in w.sources)
            counts["sources held"] += src
            if not w.coreless(W):
                print(f"  {n}: the recorded window part has a core (not playable)")
                continue
            C = tuple(sorted(x for x in W if x in w.candidates))
            rec = table.get(C)
            Lval = sum(co * val[x] for x, co in law.items())
            delta = game(n - 1)[0] + n - game(n)[0]
            line = (f"  {n} = {c}·{P}{'' if n <= 5060 else ' (best-known)'}: sources held {src}; "
                    f"state {w.label(C) or '-'}: ")
            if not src:
                line += "outside the table (a source is not a move)"
            elif rec is None:
                line += "not a state of the table"
            elif rec["witness_cells"] is None:
                counts["open"] += 1
                line += "OPEN"
            else:
                counts["closed"] += 1
                Wn = {x for x in w.sources if x != w.n} | set(map(tuple, rec["witness_cells"]))
                gain = sum(val[x] for x in Wn) - sum(val[x] for x in W) + n
                counts["law met by the witness"] += gain >= Lval
                counts["settled past 5060"] += n > 5060 and delta == Lval
                witness = w.label(map(tuple, rec["witness_cells"])) or "-"
                line += (f"closed by {witness}: witness gives delta >= {gain}, "
                         f"law {Lval}, {'proven' if n <= 5060 else 'best-known'} delta {delta}")
            print(line)
        print(f"  {counts}")


if __name__ == "__main__":
    main()
