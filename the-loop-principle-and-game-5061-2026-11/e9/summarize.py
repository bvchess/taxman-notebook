#!/usr/bin/env python3
"""E9: one row per game of the runs in e9-N-MODE.json (ghost, plain, hole).  Run as
`nice -n 19 python3 -I summarize.py` from this folder."""
import glob
import json

rows = {}
for path in glob.glob("e9-*.json"):
    d = json.loads(open(path).read())
    rows.setdefault(d["n"], {})[d["mode"]] = d
print("| n | x | P*(n − 1) | root parity bound above P* (plain = ghost) | ghost: answer, nodes, seconds | plain: answer, "
      "nodes, seconds | hole: answer, set's excess, nodes |")
print("|---:|---:|---:|---:|---|---|---|")
for n in sorted(rows):
    r = rows[n]
    any_d = next(iter(r.values()))

    def cell(mode):
        d = r.get(mode)
        if d is None:
            return "running or not run"
        text = f"{d['answer']}, {d['nodes']:,}, {d['seconds']:.1f}"
        if d["stats"][7]:
            text += f", {d['stats'][7]} uncertified"
        return text

    hole = r.get("hole")
    hole_text = "not run" if hole is None else (
        f"{hole['answer']}, +{hole['found']['above_pstar']} (playable {hole['found']['playable_again']}, independent "
        f"{hole['found']['independent_at_both_parities']}), {hole['nodes']:,}" if hole["found"] else
        f"{hole['answer']}, {hole['nodes']:,}")
    ghost, plain = r.get("ghost"), r.get("plain")
    bounds = {d["root_parity"] for d in (ghost, plain) if d}
    print(f"| {n} | {any_d['x']} | {any_d['pstar']:,} | {', '.join(str(b - any_d['pstar']) for b in sorted(bounds))} | "
          f"{cell('ghost')} | {cell('plain')} | {hole_text} |")
