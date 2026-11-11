#!/usr/bin/env python3
"""E2: draw the sample of nodes from the node files of a proof's trace (TAXMAN_BRANCH_TRACE_NODES).

usage: draw_sample.py PREFIX FINAL_BEST PER_BAND OUT [SEED]

Reads PREFIX.K.nodes, lines  BAND GAP BEST SUM CAP SIZE REST PROMOTED CANDS  (a '+' on SIZE or REST: cut short by a unit
hand-off).  Keeps the nodes whose incumbent was already the proof's final one (BEST == FINAL_BEST: the gap is then
against the target of the test) and whose sizes are complete, draws PER_BAND of each band at random, and writes
ID BAND GAP BEST SUM CAP SIZE REST PROMOTED CANDS to OUT, for e1_smooth --nodes.
"""
import glob
import random
import sys
from collections import defaultdict

prefix, final_best, per_band, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 2026

pool = defaultdict(list)
seen = defaultdict(int)
for path in sorted(glob.glob(prefix + ".*.nodes")):
    with open(path) as f:
        for line in f:
            fields = line.split()
            band, gap, best, total, cap, size, rest, promoted, cands = fields
            seen[int(band)] += 1
            if int(best) != final_best or "+" in size or "+" in rest:
                continue
            pool[int(band)].append(fields)

rng = random.Random(seed)
lines = []
print("band | sampled by the trace | kept (final incumbent, complete) | drawn")
for band in range(4):
    keep = pool[band]
    rng.shuffle(keep)
    drawn = keep[:per_band]
    print(f"{band} | {seen[band]} | {len(keep)} | {len(drawn)}")
    for i, fields in enumerate(drawn):
        lines.append(" ".join([f"{band}-{i}"] + fields))
with open(out, "w") as f:
    f.write("\n".join(lines) + "\n")
