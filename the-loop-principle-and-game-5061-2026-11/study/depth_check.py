#!/usr/bin/env python3
"""rise by clean depth, refined by the depth the family's pattern needs (jmax of the family's modal pattern).
    nice -n 19 python3 -I study/depth_check.py   (from the loops folder)"""
import json, os, sys
from collections import Counter, defaultdict
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import predict, patterns  # noqa: E402

rows = predict.load_rows()
rows.sort(key=lambda r: r["n"])
for r in rows:
    r["pattern"] = patterns.pattern(r)
    r["depth"] = patterns.clean_depth(r["n"]) if r["n"] >= 187 else -1
chain = [r for r in rows if r["range"] == "chain" and r["n"] >= 187]
past = [r for r in rows if r["range"] == "past"]
tc = sum(r["cpu"] for r in chain)
# modal pattern per cofactor on the chain
byc = defaultdict(list)
for r in chain:
    if r["pattern"]:
        byc[r["cofactor"]].append(r["pattern"])
modal = {c: Counter(ps).most_common(1)[0][0] for c, ps in byc.items()}
need = {c: patterns.jmax(p) for c, p in modal.items()}

print("== rise by clean depth, relaxations and restrictions from 187 (chain) and past 5060")
for name, sel in (("chain", chain), ("past", past)):
    for d in range(0, 6):
        s = [r for r in sel if r["step"] != "exchange" and (r["depth"] == d if d < 5 else r["depth"] >= 5)]
        z = [r for r in s if r["delta"] == r["delta_pb"]]
        pos = [r for r in s if r["delta"] > r["delta_pb"]]
        neg = [r for r in s if r["delta"] < r["delta_pb"]]
        cpu = f" ({100*sum(r['cpu'] for r in s)/tc:.1f}% CPU)" if name == "chain" else ""
        print(f"  {name} depth {'>=5' if d == 5 else d}: {len(z)}/{len(s)} rise 0, {len(pos)} rise>0, {len(neg)} rise<0{cpu}")
for dmin in (2, 3, 4):
    for name, sel in (("chain", chain), ("past", past)):
        s = [r for r in sel if r["step"] != "exchange" and r["depth"] >= dmin]
        bad = [(r["n"], r["cofactor"], r["depth"], r["delta"] - r["delta_pb"]) for r in s if r["delta"] != r["delta_pb"]]
        cpu = f" ({100*sum(r['cpu'] for r in s)/tc:.1f}% CPU)" if name == "chain" else ""
        print(f"depth >= {dmin}, {name}: {len(s) - len(bad)}/{len(s)} rise 0{cpu}; exceptions (n, c, depth, rise): {bad}")
        print("   cofactors:", sorted(Counter(r["cofactor"] for r in s).items()))
print("\n== clean to the family's own depth (jmax of the chain's modal pattern of the cofactor), relax+restrict")
for name, sel in (("chain", chain), ("past", past)):
    s = [r for r in sel if r["step"] != "exchange" and r["cofactor"] in need and r["depth"] >= max(need[r["cofactor"]], 1)]
    bad = [(r["n"], r["cofactor"], r["depth"], need[r["cofactor"]], r["delta"] - r["delta_pb"]) for r in s if r["delta"] != r["delta_pb"]]
    cpu = f" ({100*sum(r['cpu'] for r in s)/tc:.1f}% CPU)" if name == "chain" else ""
    print(f"  {name}: {len(s)-len(bad)}/{len(s)} rise 0{cpu}; exceptions: {bad}")
print("\n== needed depth per cofactor (jmax of modal pattern):", sorted(need.items()))
print("\n== the 25 flagged past games (depth >= 2, rise != 0): n, cofactor, depth, step, rise, delta, delta_pb")
for r in past:
    if r["step"] != "exchange" and r["depth"] >= 2 and r["delta"] != r["delta_pb"]:
        print("  ", r["n"], r["cofactor"], r["depth"], r["step"], r["delta"] - r["delta_pb"], r["delta"], r["delta_pb"])
print("\n== 2512 and its family neighbors")
for r in rows:
    if r["cofactor"] == 16 and 2000 <= r["n"] <= 3000:
        print("  ", r["n"], "depth", r["depth"], "delta", r["delta"], "pb", r["delta_pb"], "D", r["dropped"], "A", r["added"], "pattern", r["pattern"])
