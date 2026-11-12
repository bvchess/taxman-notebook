#!/usr/bin/env python3
"""Print the change sets of chosen cofactor families, each number written as k·P_j (P_0 the largest prime of n).
    nice -n 19 python3 -I explore.py C [C ...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import predict, tables  # noqa: E402
rows = predict.load_rows()
for c in map(int, sys.argv[1:]):
    for r in rows:
        if r["cofactor"] != c:
            continue
        n = r["n"]
        lab = lambda xs: " ".join(tables.col_label(x, n) for x in xs)
        print(f"{n} {r['step']} c={c} P={r['P']} P1={r['P1']} d={r['delta']} pb={r['delta_pb']} half={r['half']} "
              f"shadow={r['shadow']} bp={r['boxpeel']} xm={r['xmin']} | D: {lab(r['dropped'])} | A: {lab(r['added'])}")
