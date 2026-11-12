#!/usr/bin/env python3
"""The table of the rough part's error under other arrangements of the smooth part (run-arrangements.py): for each
living leaf, how many members of the smooth part it sets otherwise than the optimal arrangement, its bound over
opt(5060), the best game with it less opt, the rough part's error (the bound less that best), and the search's steps.
The optimal arrangement's own error is the gap of fix-smooth 5060 --smooth 13.

    python3 -I summarize_arrangements.py arrangements.jsonl
"""

import json
import statistics
import sys


def main():
    rows = []
    with open(sys.argv[1]) as f:
        for text in f:
            line = json.loads(text)
            opt, bound, score = line["opt"], line["leaf_bound"], line["score"]
            best = None if score is None else score - opt
            error = None if score is None else bound - score
            rows.append((line["differ"], bound - opt, best, error, line["nodes"], line["completed"], line["leaf"]))
    rows.sort()
    print("| leaf | members set otherwise | bound − opt | best − opt | rough error | steps | finished |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for differ, over, best, error, nodes, completed, leaf in rows:
        shown = (lambda v: "none" if v is None else str(v))
        print(f"| {leaf} | {differ} | {over} | {shown(best)} | {shown(error)} | {nodes:,} | "
              f"{'yes' if completed else 'no'} |")
    errors = [r[3] for r in rows if r[3] is not None and r[5]]
    if errors:
        print(f"\nThe rough error over {len(errors)} finished leaves: min {min(errors)}, median "
              f"{statistics.median(errors):.0f}, max {max(errors)}")


if __name__ == "__main__":
    main()
