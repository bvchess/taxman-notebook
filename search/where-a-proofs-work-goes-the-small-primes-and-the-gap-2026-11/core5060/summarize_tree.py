#!/usr/bin/env python3
"""Summarize the samples of `restricted core-tree` (Knuth's estimator over the core's arrangements).

Each argument is a file of core-tree JSON lines.  For each it prints: the samples, the share that reached a leaf (an
arrangement of the whole core whose GF(2) bound exceeds the score to beat), the estimates of the core tree's nodes and
leaves (the mean over samples of the path's node sum and of its weight at a leaf, as log10), and with solved leaves the
estimate of their searches' steps in all (the mean of weight times steps), the share of leaf searches that finished,
and any leaf whose search found a score above the one to beat (none may, on a proven game, at the default).
"""

import json
import math
import sys


def log10_mean(logs: list[float], count: int) -> float:
    """log10 of the mean of 10**x over `logs`, padded with zeros to `count` terms (-inf when all are zero)."""
    if not logs:
        return float("-inf")
    top = max(logs)
    return top + math.log10(sum(10 ** (x - top) for x in logs)) - math.log10(count)


def share_of_top(logs: list[float]) -> float:
    """The share of the largest term in the sum of 10**x: near 1 means one sample decides the estimate."""
    if not logs:
        return float("nan")
    top = max(logs)
    return 1 / sum(10 ** (x - top) for x in logs)


def summarize(path: str) -> None:
    rows, summary = [], None
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("summary"):
                summary = d
            elif not d.get("skipped"):
                rows.append(d)
    if not rows:
        print(f"{path}: no samples")
        return
    count = len(rows)
    leaves = [r for r in rows if r["leaf"]]
    leaf_logs = [r["log10_weight"] for r in leaves]
    node_logs = [r["log10_nodes"] for r in rows]
    head = path
    if summary:
        head += f": n={summary['n']} B={summary['smooth']} smooth part={summary['smooth_part']}"
        head += f" above={summary['above']}"
    print(head)
    print(f"  samples {count}, reached a leaf {len(leaves)} ({len(leaves) / count:.0%}), "
          f"mean depth {sum(r['depth'] for r in rows) / count:.1f}")
    print(f"  log10 nodes {log10_mean(node_logs, count):.2f}, log10 leaves {log10_mean(leaf_logs, count):.2f} "
          f"(largest sample's share {share_of_top(leaf_logs):.2f})")
    solved = [r for r in leaves if "steps" in r]
    if solved:
        cost_logs = [r["log10_weight"] + math.log10(max(r["steps"], 1)) for r in solved]
        cpu_logs = [r["log10_weight"] + math.log10(max(r["cpu"], 1e-3)) for r in solved]
        finished = sum(r["completed"] for r in solved)
        above = [r for r in solved if r.get("score") is not None]
        steps = sorted(r["steps"] for r in solved)
        print(f"  leaf searches {len(solved)}, finished {finished}, steps median {steps[len(steps) // 2]} "
              f"max {steps[-1]}")
        print(f"  log10 total leaf steps {log10_mean(cost_logs, count):.2f}, log10 total leaf CPU s "
              f"{log10_mean(cpu_logs, count):.2f} (largest sample's share {share_of_top(cost_logs):.2f})")
        bounds = sorted(r["bound"] - summary["above"] for r in solved if r.get("bound") is not None) if summary else []
        if bounds:
            print(f"  leaf bound less the score to beat: min {bounds[0]} median {bounds[len(bounds) // 2]} "
                  f"max {bounds[-1]}")
        for r in above:
            print(f"  ABOVE: sample {r['sample']} scored {r['score']}")


def main() -> None:
    for path in sys.argv[1:]:
        summarize(path)


if __name__ == "__main__":
    main()
