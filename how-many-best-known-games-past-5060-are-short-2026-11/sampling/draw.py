#!/usr/bin/env python3
"""The order in which the sample plays the targets.

    cd /home/brian/taxman_work/lab/work/sampling && nice -n 19 python3 -I draw.py

Reads frame/targets.csv (a copy of ../audit/targets.csv as written at 07:20 on 2026-11-11: 1,559 targets) and writes
sample-order.csv: every target once, in an order drawn with a fixed random seed, stratified by the dedicated plays it
has had (targets.csv's `plays`: 0, 1, 2, 3 or more).  Within a stratum the order is a random permutation; the strata
are interleaved by the key (rank in the stratum + U) / stratum size, U uniform, so that the first k targets of the
order hold each stratum in proportion to its size, for every k.  The run plays the order from the top and stops at a
clock time fixed before it began, so whatever it reaches is a proportionally stratified random sample.  Also prints,
for sample sizes from 100 to the whole frame, the exact (hypergeometric) 95% upper bound on the number of targets in
the frame that one play would raise, if the sample raised none or one, and the hours each size would take.
"""

import csv
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261111
# seconds of a level-4 play on 12 threads, mean of the root-first pilot's plays by thousand (rootfirst/plays, 1,909)
SECONDS = {5: 116, 6: 142, 7: 195, 8: 268, 9: 306}


def stratum(plays):
    return min(int(plays), 3)


def hyper_upper(T, n, k, conf=0.95):
    """The largest R (raisable targets among T) with P(at most k raised in a sample of n) >= 1 - conf."""
    def p_at_most(R):
        total = math.comb(T, n)
        return sum(math.comb(R, j) * math.comb(T - R, n - j) for j in range(0, min(k, R) + 1)) / total
    R = k
    while R + 1 <= T and p_at_most(R + 1) >= 1 - conf:
        R += 1
    return R


def main():
    with open(os.path.join(HERE, "frame", "targets.csv")) as f:
        targets = list(csv.DictReader(f))
    rng = random.Random(SEED)
    strata = {}
    for t in targets:
        strata.setdefault(stratum(t["plays"]), []).append(t)
    keyed = []
    for h, members in sorted(strata.items()):
        members = sorted(members, key=lambda t: int(t["n"]))
        rng.shuffle(members)
        for i, t in enumerate(members):
            keyed.append(((i + rng.random()) / len(members), int(t["n"]), h, t))
    keyed.sort()
    with open(os.path.join(HERE, "sample-order.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order", "n", "stratum", "plays", "seeds_levels", "step", "layer", "best_known", "est_seconds"])
        for order, (_, n, h, t) in enumerate(keyed, 1):
            w.writerow([order, n, h, t["plays"], t["seeds_levels"], t["step"], t["layer"], t["best_known"],
                        SECONDS[min(n // 1000, 9)]])
    T = len(targets)
    print(f"frame: {T} targets; strata (plays so far 0, 1, 2, 3+): "
          + ", ".join(f"{h}: {len(m)}" for h, m in sorted(strata.items())))
    print("size  hours on 6 lanes  95% upper bound on raisable targets: none raised  one raised")
    for n in (100, 200, 300, 400, 600, 800, 1000, T):
        secs = sum(SECONDS[min(k[1] // 1000, 9)] for k in keyed[:n])
        print(f"{n:>5} {secs / 3600 / 6:>10.1f} {hyper_upper(T, n, 0):>28} {hyper_upper(T, n, 1):>11}")


if __name__ == "__main__":
    main()
