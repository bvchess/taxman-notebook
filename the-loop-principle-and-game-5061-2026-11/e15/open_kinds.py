#!/usr/bin/env python3
"""E15: what the open leaves of a gluing run share: the rows their nearest miss names, the rows of column 0 they hold,
and how many candidates they hold.

    nice -n 19 python3 -I e15/open_kinds.py FILE.jsonl[.gz] P0"""
import collections
import gzip
import json
import sys

PATH, P0 = sys.argv[1], int(sys.argv[2])
missed, col0, sizes, both = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
n = 0
with (gzip.open(PATH, "rt") if PATH.endswith(".gz") else open(PATH)) as f:
    for line in f:
        for leaf in json.loads(line)["leaves"]:
            if leaf["outcome"] != "open":
                continue
            n += 1
            m = tuple((leaf.get("nearest_miss") or {}).get("missed", []))
            c0 = tuple(sorted(x // P0 for x in leaf["state"] if x % P0 == 0))
            missed[m] += 1
            col0[c0] += 1
            sizes[len(leaf["state"])] += 1
            both[(c0, m)] += 1
print(n, "open leaves")
print("rows the nearest miss names:", missed.most_common(12))
print("rows of column 0 held:", col0.most_common(12))
print("candidates held:", sorted(sizes.items()))
print("column 0 and the rows missed:", both.most_common(12))
