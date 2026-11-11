#!/usr/bin/env python3
"""One line a run of variants.jsonl (or the file given): board, variant, value against E11's, nodes, seconds, and the
ownership counters."""
import json
import sys

REF = {}
for path in ("/home/brian/taxman_work/lab/work/oddcore/e1/hubval2.jsonl", "/home/brian/taxman_work/lab/work/oddcore/e1/hubs.jsonl"):
    for raw in open(path):
        d = json.loads(raw)
        if d.get("finished"):
            REF[d["n"]] = (d["PB_s"], d["processed"])

for raw in open(sys.argv[1] if len(sys.argv) > 1 else "variants.jsonl"):
    d = json.loads(raw)
    o = d["own_stats"]
    ref = REF.get(d["n"], (None, None))
    value = d["PB_s"] if d["finished"] else f"<= {d['PB_s_upper']}"
    same = "" if ref[0] is None else ("same" if d["PB_s"] == ref[0] else "DIFF")
    print(f"{d['n']:5} {d.get('variant', '?'):14} {value!s:>12} {same:4} share {d['share_high']:.3f} "
          f"nodes {d['processed']:>8} (E11 {ref[1]}) {d['seconds']:7.1f} s  br {o['branchings']:>6} "
          f"S {o['s_solved']}/{o['s_cut']}/{o['s_infeasible']} mean {o['s_drop_mean']} circ {o['circuits']}/{o.get('circuits_s')} "
          f"stall/fb {o['stalls']}/{o['fallbacks']}")
