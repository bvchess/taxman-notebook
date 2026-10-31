#!/usr/bin/env python3
# table.py BASE LABEL...: nodes, counters and seconds of panel runs, per game, against the base run.
import json, os, sys
base, labels = sys.argv[1], sys.argv[2:]
here = os.path.dirname(os.path.abspath(__file__))
def load(label, n):
    try:
        return json.loads(open(f"{here}/{label}/{n}.jsonl").read())
    except Exception:
        return None
games = sorted({int(f.split(".")[0]) for f in os.listdir(f"{here}/{base}") if f.endswith(".jsonl")})
keys = ("nodes", "matching_nodes", "branched_on_sources", "barred_upper")
tot = {l: 0.0 for l in [base] + labels}
for n in games:
    b = load(base, n)
    row = f"{n:5d} nodes {b['nodes']:7d} {b['secs']:7.2f}"
    tot[base] += b["secs"]
    for l in labels:
        d = load(l, n)
        same = all(d[k] == b[k] for k in keys)
        tot[l] += d["secs"]
        row += f" | {l} {d['nodes']:7d} {d['secs']:7.2f} {'same' if same else 'DIFFERENT'}"
    print(row)
print("total", {l: round(t, 1) for l, t in tot.items()})
