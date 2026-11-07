#!/usr/bin/env python3
"""What the cost model says the games 2531-2630 would cost the prover, and how the model did on the run's own games.

    python3 -I next100.py solver/noframe/data/exact_parity_2_2530.jsonl pre_2531_2630.jsonl

The second file is `exact --from 2531 --to 2630 --budget 1 --out pre_2531_2630.jsonl` (21 s on 4 threads): no search,
the root's parity bound and the relation of each game.  The model is the fit of log10 nodes on the root's parity gap,
the parity bound less the recorded score; `summarize.py cost` prints its slope.  A fit by n is printed beside it.
"""

import json
import math
import statistics
import sys

MS_A_NODE = (2.2, 3.6)  # the least and the most of the bands from 2400 on (3.12 on average)


def lines(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def fit(xs, ys):
    """Least squares: the intercept, the slope and the residual's standard deviation."""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    sd = math.sqrt(sum((y - intercept - slope * x) ** 2 for x, y in zip(xs, ys)) / (len(xs) - 2))
    return intercept, slope, sd


def mean_factor(sd):
    """The mean of a lognormal over its median, for a residual of sd decades."""
    return math.exp((sd * math.log(10)) ** 2 / 2)


def gap_model(searched, name, below=None):
    """The fit on the root gap of the searches from 900 on (those of gap below `below`, if given), tried on the searches
    of 2176-2530."""
    part = [r for r in searched if r["n"] >= 900 and (below is None or r["gap"] < below)]
    a, b, sd = fit([r["gap"] for r in part], [math.log10(r["nodes"]) for r in part])
    factor = mean_factor(sd)
    print(f"\n{name}: {len(part)} searches, log10 nodes = {a:.3f} + {100 * b:.4f} per 100 of gap, "
          f"residual sd {sd:.3f}, mean over median {factor:.2f}")
    late = [r for r in searched if r["n"] >= 2176 and (below is None or r["gap"] < below)]
    predicted = sum(10 ** (a + b * r["gap"]) for r in late) * factor
    print(f"  on the {len(late)} searches of 2176-2530 (gap below {below or 'any'}): "
          f"{sum(r['nodes'] for r in late) / 1e6:.0f}M nodes, the model {predicted / 1e6:.0f}M")
    return a, b, factor


def main():
    run = lines(sys.argv[1])
    ahead = lines(sys.argv[2])
    for r in run:
        r["gap"] = r["parity_bound"] - r["score"]
    searched = [r for r in run if r["search"] == "proven"]
    need = [r for r in ahead if r["relation"] == "none"]
    gaps = [r["parity_bound"] - r["score"] for r in need]
    before = statistics.mean(r["gap"] for r in searched if 2400 <= r["n"] < 2500)
    print(f"2531-2630: {len(ahead)} games, {len(need)} need a search; root gaps {min(gaps)} to {max(gaps)}, mean "
          f"{statistics.mean(gaps):.0f} (2400-2499: {before:.0f})")
    kinds = ("chain", "prime", "semiprime", "none")
    print("by relation:", {k: sum(1 for r in ahead if r["relation"] == k) for k in kinds})

    for name, below in [("fit on the gaps below 1000", 1000), ("fit on every gap", None)]:
        a, b, factor = gap_model(searched, name, below)
        nodes = sum(10 ** (a + b * g) for g in gaps) * factor
        low, high = (nodes * ms / 3.6e6 for ms in MS_A_NODE)
        print(f"  the next 100: {nodes / 1e6:.0f}M nodes, {low:.0f} to {high:.0f} thread-hours at {MS_A_NODE[0]} to "
              f"{MS_A_NODE[1]} ms a node, {low / 88:.1f} to {high / 88:.1f} hours on 88 threads")

    # The mean of the run's searches whose gap lies in the same band of 100 points (n from 1301), with no model.
    seconds = nodes_ = 0.0
    for g in gaps:
        lo = g // 100 * 100
        same = [r for r in searched if lo <= r["gap"] < lo + 100 and r["n"] >= 1301]
        seconds += statistics.mean(r["thread_secs"] for r in same)
        nodes_ += statistics.mean(r["nodes"] for r in same)
    print(f"\nthe mean of the searches in the same 100 points of gap: {nodes_ / 1e6:.0f}M nodes, "
          f"{seconds / 3600:.0f} thread-hours")

    # The fit by n.
    part = [r for r in searched if r["n"] >= 900]
    a, b, sd = fit([r["n"] for r in part], [math.log10(r["nodes"]) for r in part])
    nodes = 10 ** (a + b * 2581) * mean_factor(sd) * len(need)
    print(f"\nthe fit by n: log10 nodes = {a:.3f} + {100 * b:.4f} per 100 in n, residual sd {sd:.3f}; "
          f"the next 100: {nodes / 1e6:.0f}M nodes, {nodes * MS_A_NODE[0] / 3.6e6:.0f} to "
          f"{nodes * MS_A_NODE[1] / 3.6e6:.0f} thread-hours")


if __name__ == "__main__":
    main()
