#!/usr/bin/env python3
"""The survivor test's score (2026-11-09): for each play gG-lL-sS.jsonl here, its game's score against opt(n) from the
proven chain, and for each game and level how many of the seeds reached the optimum.

    python3 -I score.py
"""

import collections
import glob
import gzip
import json
import re

RES = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
opt = {x["n"]: x["score"] for x in map(json.loads, gzip.open(RES, "rt"))}
reached = collections.defaultdict(list)
for path in sorted(glob.glob("g*-l*-s*.jsonl")):
    g, level, seed = map(int, re.match(r"g(\d+)-l(\d+)-s(\d+)\.jsonl", path).groups())
    with open(path) as f:
        score = max((json.loads(t)["score"] for t in f if t.strip()), default=None)
    if score is None:
        continue
    short = opt[g] - score
    reached[(g, level)].append(short)
    print(f"game {g}, level {level}, seed {seed}: {score}, {'at opt(n)' if short == 0 else f'{short} short'}")
print("game  level  seeds at opt(n)")
for (g, level), shorts in sorted(reached.items()):
    print(f"{g}  {level}  {sum(s == 0 for s in shorts)} of {len(shorts)}  (short by {sorted(shorts)})")
