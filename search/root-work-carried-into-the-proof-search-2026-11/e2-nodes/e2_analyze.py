#!/usr/bin/env python3
"""E2: the smooth test at sampled nodes (the study's report, Section 7.3): per band and per policy, the nodes saved
against the solves spent.

usage: e2_analyze.py RESULTS.jsonl POP0,POP1,POP2,POP3 STEP_MS

RESULTS.jsonl: the lines of e1_smooth --nodes.  POPk: how many branchings of the proof's trace lie in band k (the sample
is drawn from them).  STEP_MS: the proof's CPU milliseconds a step.
"""
import json
import statistics
import sys
from collections import defaultdict

rows = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
pop = [int(x) for x in sys.argv[2].split(",")]
step_ms = float(sys.argv[3])
BANDS = ["[100,300)", "[300,600)", "[600,959)", "[959,1500)"]
BUDGETS = [3, 10, 30, 100, 1000, 10000]
THRESHOLDS = [300, 600, 959, 1500]

by_band = defaultdict(list)
for r in rows:
    by_band[r["band"] if isinstance(r["band"], int) else int(r["band"])].append(r)


def cut_within(r, b):
    return r["cut"] and r["solves"] <= b


def med(xs):
    return statistics.median(xs) if xs else float("nan")


print(f"# E2: {len(rows)} sampled nodes, the depth-first smooth test, budget 10^4 solves\n")
print("| band | nodes | bound = solver's | cut (any budget) | cut within 3 | 10 | 30 | 100 | 1000 | "
      "leaf above incumbent | over budget |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for k in range(4):
    rs = by_band[k]
    if not rs:
        continue
    n = len(rs)
    same = sum(r["bound_e1"] == r["bound_solver"] for r in rs)
    cells = [sum(cut_within(r, b) for r in rs) for b in BUDGETS[:5]]
    print(
        f"| {BANDS[k]} | {n} | {same} | {sum(r['cut'] for r in rs)} | "
        + " | ".join(str(c) for c in cells)
        + f" | {sum(r['leaf'] is not None for r in rs)} | {sum(r['over_budget'] for r in rs)} |"
    )
print()

print("| band | median subtree (child) | median subtree (loop from here) | median solves of a cut | "
      "median solves, uncut, to the stop | mean reduction reached | mean gap | solves a cut / rest, summed |")
print("|---|---|---|---|---|---|---|---|")
for k in range(4):
    rs = by_band[k]
    if not rs:
        continue
    cuts = [r for r in rs if r["cut"]]
    uncut = [r for r in rs if not r["cut"]]
    red = [r["bound_e1"] - r["upper"] for r in rs]
    ratio = sum(r["solves"] for r in cuts) / max(1, sum(r["rest"] for r in cuts)) if cuts else float("nan")
    print(
        f"| {BANDS[k]} | {med([r['size'] for r in rs]):.0f} | {med([r['rest'] for r in rs]):.0f} | "
        f"{med([r['solves'] for r in cuts]):.0f} | {med([r['solves'] for r in uncut]):.0f} | "
        f"{statistics.mean(red):.0f} | {statistics.mean(r['gap'] for r in rs):.0f} | {ratio:.3f} |"
    )
print()

solve_ms = 1000 * sum(r["seconds"] for r in rows) / max(1, sum(r["solves"] for r in rows))
print(f"Measured here: {solve_ms:.2f} ms a solve (from scratch, with the smooth cores and the pricing), against "
      f"{step_ms:.2f} ms a step of the proof: a solve costs {solve_ms / step_ms:.1f} steps.\n")

print("### Policies: nodes saved against solves spent, scaled to the trace's populations of the bands\n")
print("A node of a band under the threshold gets the test with the budget; a cut saves the rest of the node's loop "
      "(steps) and costs its solves; an uncut node costs min(solves, budget).  Sample means times band populations; "
      "nested subtrees are counted once for each node that holds them, so the savings are an upper bound where "
      "cut nodes lie inside cut nodes.\n")
print("| threshold | budget | nodes tested | cut | steps saved | solves spent | steps saved a solve | "
      "net steps, 1 solve = 1 step | net steps, measured cost | saved / the proof's steps (22.7M) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for t in THRESHOLDS:
    bands = [k for k in range(4) if [300, 600, 959, 1500][k] <= t]
    for b in BUDGETS:
        tested = cuts = saved = spent = 0.0
        for k in bands:
            rs = by_band[k]
            if not rs:
                continue
            s = pop[k] / len(rs)
            tested += pop[k]
            for r in rs:
                if cut_within(r, b):
                    cuts += s
                    saved += s * r["rest"]
                    spent += s * r["solves"]
                else:
                    spent += s * min(r["solves"], b)
        ratio = saved / spent if spent else float("nan")
        net1 = saved - spent
        netm = saved - spent * solve_ms / step_ms
        print(
            f"| {t} | {b} | {tested:.0f} | {cuts:.0f} | {saved:.0f} | {spent:.0f} | {ratio:.2f} | {net1:.0f} | "
            f"{netm:.0f} | {100 * saved / 22.7e6:.0f}% |"
        )
print()

print("### Per node\n")
print("| id | gap | max add | picks | solver's bound | E1's bound | cut | solves | leaf | upper | child subtree | loop rest |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(rows, key=lambda r: r["id"]):
    print(
        f"| {r['id']} | {r['gap']} | {r['cap']} | {r['picks']} | {r['bound_solver']} | {r['bound_e1']} | {r['cut']} | "
        f"{r['solves']} | {r['leaf']} | {r['upper']} | {r['size']} | {r['rest']} |"
    )
