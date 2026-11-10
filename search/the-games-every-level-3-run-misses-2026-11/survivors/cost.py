#!/usr/bin/env python3
"""The survivor test's cost (2026-11-09): for each level, the plays of gG-lL-sS.jsonl here, how many scored opt(n), and
the work, the rounds and the seconds they took (both plays of a game played twice).

    nice -n 19 python3 -I cost.py

Run in this folder.  Reads the plays' lines and the proven table (the path of score.py).  The seconds are of a machine
shared with other runs, at 12 threads.
"""

import collections
import glob
import gzip
import json
import re

RES = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
opt = {x["n"]: x["score"] for x in map(json.loads, gzip.open(RES, "rt"))}
total = collections.defaultdict(lambda: collections.Counter())
for path in sorted(glob.glob("g*-l*-s*.jsonl")):
    game, level, _ = map(int, re.match(r"g(\d+)-l(\d+)-s(\d+)\.jsonl", path).groups())
    with open(path) as f:
        line = [json.loads(t) for t in f if t.strip()][-1]
    other = line["other"] or {}
    cost = total[level]
    cost["plays"] += 1
    cost["at opt(n)"] += line["score"] == opt[game]
    cost["points short"] += opt[game] - line["score"]
    cost["work"] += line["work"] + other.get("work", 0)
    cost["rounds"] += line["rounds"] + other.get("rounds", 0)
    cost["seconds"] += line["seconds"]
print("level  plays  at opt(n)  points short  work M  rounds  seconds")
for level, cost in sorted(total.items()):
    print(f"{level:>5}  {cost['plays']:>5}  {cost['at opt(n)']:>9}  {cost['points short']:>12}  "
          f"{cost['work'] / 1e6:>6.1f}  {cost['rounds']:>6}  {cost['seconds']:>7.0f}")
base = total[min(total)]["seconds"]
print("seconds against level", min(total), ":", ", ".join(f"level {level} x{c['seconds'] / base:.2f}"
                                                         for level, c in sorted(total.items())))
