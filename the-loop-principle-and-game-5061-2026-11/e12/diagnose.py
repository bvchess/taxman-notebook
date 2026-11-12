#!/usr/bin/env python3
"""E12: why an open state is open.  For each open state of a family's table, the gainful witnesses (best slack
first) and, for each, the signatures of its column-closed parts that no column-closed part of the state dominates,
with the rows those parts use once (the hubs whose holders the region would need).

    nice -n 19 python3 -I e12/diagnose.py FAMILY [WITNESSES]      # from the loops folder
"""
import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import window_law as wl  # noqa: E402


def main():
    family = sys.argv[1]
    many = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    c, d, law, extras = wl.FAMILIES[family]
    w = wl.Window(c, d, law, True, extras)
    digits = re.match(r"\d+", family).group()
    name = f"{digits}P{family[len(digits):]}"
    rows = [json.loads(t) for t in open(os.path.join(HERE, f"table_{name}.jsonl"))]
    n = w.n
    fixed_old = [n] + [x for x in w.sources if x != n]
    fixed_new = [x for x in w.sources if x != n]
    nval = [c * ray[0] for ray in w.irays]
    rowname = {i: k for k, i in w.rbit.items()}

    def rows_of(mask):
        return sorted(rowname[i] for i in range(len(w.rows)) if mask >> i & 1)
    free = [x for x in w.cells if x != n and x not in w.sources]
    for r in rows:
        if r["witness_cells"] is not None:
            continue
        C = [tuple(x) for x in r["state_cells"]]
        W0 = set(fixed_old) | set(C)
        w0 = w.weight_at(W0)
        need = [w0[i] - nval[i] + w.law_at[i] for i in range(len(w.rays))]
        so = w.signatures(W0)
        print(f"== open state: S holds {w.label(C) or '-'}")
        cands = []
        for size in range(len(free) + 1):
            if size > 4:
                break
            import itertools
            for Cn in itertools.combinations(free, size):
                Wn = set(fixed_new) | set(Cn)
                wn = w.weight_at(Wn)
                if all(wn[i] >= need[i] for i in range(len(w.rays))) and w.coreless(Wn):
                    cands.append((min(wn[i] - need[i] for i in range(len(w.rays))), Cn, Wn))
        cands.sort(key=lambda t: -t[0])
        for slack, Cn, Wn in cands[:many]:
            sn = w.signatures(Wn)
            bad = [(r1, r2) for r1, r2 in sn if not w.dominated({(r1, r2)}, so)]
            minimal = [b for b in bad if not any(o != b and (o[0] | o[1]) & ~(b[0] | b[1]) == 0 for o in bad)]
            print(f"   witness {w.label(Cn) or '-'} (slack {Fraction(slack, w.scale)}): {len(bad)} undominated parts; "
                  f"smallest: "
                  + "; ".join(f"rows {rows_of(r1 | r2)} once {rows_of(r1)}" for r1, r2 in minimal[:4]))


if __name__ == "__main__":
    main()
