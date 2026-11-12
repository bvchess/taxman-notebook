#!/usr/bin/env python3
"""rise = gap(n) - gap(n-1) by kind of step over the whole proven chain (settle.csv), to check the corollaries of the
parity bound's exchange formula: rise = 0 at every prime, every odd semiprime from 189 on and every exchange step.
    nice -n 19 python3 -I study/rise_kinds.py"""
import csv, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/succession")
import common  # noqa: E402
rows = {int(r["n"]): r for r in csv.DictReader(open("/home/brian/taxman_work/lab/work/succession/settle.csv"))}
print("columns:", list(next(iter(rows.values())).keys()))
def rise(r):
    return int(r["rise"]) if r.get("rise") not in (None, "") else None
from collections import Counter, defaultdict
tab = defaultdict(Counter)
bad = defaultdict(list)
for n, r in sorted(rows.items()):
    if n < 3:
        continue
    f = common.factor(n)
    if len(f) == 1:
        kind = "prime"
    elif len(f) == 2 and n % 2 == 1 and n >= 189:
        kind = "odd semiprime >= 189"
    else:
        kind = r.get("step") or r.get("kind") or "?"
    rv = rise(r)
    if rv is None:
        tab[kind]["no rise"] += 1
        continue
    tab[kind]["rise 0" if rv == 0 else ("rise > 0" if rv > 0 else "rise < 0")] += 1
    if rv != 0 and kind in ("prime", "odd semiprime >= 189", "exchange"):
        bad[kind].append((n, rv, r.get("outcome")))
for k, c in tab.items():
    print(k, dict(c))
for k, v in bad.items():
    print("nonzero at", k, v[:20])
# the games at the ceiling where the gap falls
print("ceiling games with rise != 0:", [(n, rise(r), r.get("step")) for n, r in sorted(rows.items()) if r.get("outcome") == "ceiling" and rise(r) not in (None, 0)])
