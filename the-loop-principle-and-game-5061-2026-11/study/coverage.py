#!/usr/bin/env python3
"""Coverage of the parity form by clean depth, beyond the families 8P and 12P that L2 and L4 settle.
    nice -n 19 python3 -I study/coverage.py"""
import sys
from collections import Counter
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import predict, patterns  # noqa: E402
rows = predict.load_rows()
for r in rows:
    r["depth"] = patterns.clean_depth(r["n"]) if r["n"] >= 187 else -1
chain = [r for r in rows if r["range"] == "chain" and r["n"] >= 187]
past = [r for r in rows if r["range"] == "past"]
tc = sum(r["cpu"] for r in chain)
for dmin in (2, 3):
    for name, sel in (("chain", chain), ("past", past)):
        s = [r for r in sel if r["step"] != "exchange" and r["depth"] >= dmin]
        new = [r for r in s if r["cofactor"] not in (8, 12)]
        z = [r for r in new if r["delta"] == r["delta_pb"]]
        cpu = f"; CPU of all {100*sum(r['cpu'] for r in s)/tc:.1f}%, of those beyond 8P and 12P {100*sum(r['cpu'] for r in new)/tc:.2f}%, of the rise-0 ones among them {100*sum(r['cpu'] for r in z)/tc:.2f}%" if name == "chain" else ""
        print(f"depth >= {dmin}, {name}: {len(s)} games, {len(new)} beyond 8P/12P, {len(z)} of those with rise 0{cpu}")
        print("   beyond 8P/12P by cofactor (games, rise 0):", sorted((c, sum(1 for r in new if r['cofactor'] == c), sum(1 for r in z if r['cofactor'] == c)) for c in set(r['cofactor'] for r in new)))
# the dearest clean games beyond 8P/12P
s = sorted((r for r in chain if r["step"] != "exchange" and r["depth"] >= 2 and r["cofactor"] not in (8, 12)), key=lambda r: -r["cpu"])
print("dearest chain games clean to depth >= 2 beyond 8P/12P (n, c, depth, cpu h, rise):", [(r["n"], r["cofactor"], r["depth"], round(r["cpu"]/3600, 1), r["delta"] - r["delta_pb"]) for r in s[:8]])
