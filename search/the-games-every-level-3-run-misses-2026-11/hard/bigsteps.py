#!/usr/bin/env python3
"""Among the games whose proven step is big, which are the ones the search misses?  Writes bigsteps.csv and prints
the start rate by the step's size and by the chance that a round frees it.

    cd /home/brian/taxman_work/lab/work/gapdash/hard && OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
        nice -n 19 /home/brian/taxman_work/lab/work/stats-venv/bin/python3 -I -B bigsteps.py

The stats venv's Python (numpy), a few minutes.  Reads the proven table, E5's steps.json and recurrence.csv, and uses
compare.py's chances of freeing a swap.  These use the optimum: they say what the search must do, not where.

For each searched game below its ceiling of 3001-5060, the seed (the proven moves of n - 1 up to n/2, E5's) and its
drops toward the proven set of n, the drops' sizes, and where the step drops 5 or more, the chance that one round of
64 from the seed frees every drop at each stage.  The seed stands in for its survivors, from which the trajectory of
n - 1 begins; compare.py has the survivors themselves for the recurring starts and their controls.  The plays: the
first passes and the later passes in which the game was searched from moves for n - 1 at opt(n - 1).
"""

import csv
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # python3 -I leaves this folder off the path
from common import HI, LO, cofactor, factor, kind, load_opt, read_recurrence  # noqa: E402
from compare import SEED, p_free, size_median  # noqa: E402

MIN_DROPS = 5


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    return sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))


def main():
    rng = np.random.default_rng(SEED)
    rec = read_recurrence()
    opt = load_opt(LO - 1, HI)
    rows = []
    for n in range(LO, HI + 1):
        r = rec[n]
        if kind(n, opt) != "below" or opt[n]["method"] != "search":
            continue
        seed = set(opt[n - 1]["promotions"]) | ({n // 2} if opt[n - 1]["half_up"] else set())
        T = opt[n]["promotions"]
        drops = seed - T
        pf = p_free(seed, T, n, rng) if len(drops) >= MIN_DROPS else None
        rows.append({"n": n, "factors": "*".join(map(str, factor(n))), "cofactor": cofactor(n),
                     "drops": len(drops), "adds": len(T - seed), "drops_size": size_median(drops, n),
                     "drops_below_0.35n": sum(x < 0.35 * n for x in drops),
                     **{f"p_round_s{s}": float(f"{pf[s][2]:.4g}") if pf else "" for s in range(3)},
                     "plays": r["p1_pool"] + r["pk_pool"], "starts": r["p1_starts"] + r["pk_starts"],
                     "p1_starts": r["p1_starts"], "recurring": r["recurring"],
                     "never_short": int(r["p1_short"] + r["pk_short"] + r["chains_short"] == 0)})
    with open(os.path.join(HERE, "bigsteps.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    big = [r for r in rows if r["drops"] >= MIN_DROPS]
    print(f"{len(rows)} searched games below their ceiling of {LO}-{HI}; {len(big)} with a proven step of "
          f"{MIN_DROPS}+ drops, {sum(r['recurring'] for r in big)} of the {sum(r['recurring'] for r in rows)} "
          f"recurring starts")

    def table(label, key, bins, rows):
        print(f"\nby {label}: bin | games | recurring | never short | starts / plays (first and later passes)")
        for lo, hi in bins:
            g = [r for r in rows if lo <= r[key] < hi]
            st, pl = sum(r["starts"] for r in g), sum(r["plays"] for r in g)
            print(f"  {lo:g}-{hi:g} | {len(g)} | {sum(r['recurring'] for r in g)} | {sum(r['never_short'] for r in g)}"
                  f" | {st}/{pl} ({st / max(1, pl):.3f})")

    table("the drops", "drops", [(0, 1), (1, 2), (2, 3), (3, 5), (5, 7), (7, 10), (10, 13), (13, 99)], rows)
    table(f"the chance that a round at stage 1 (50-70% fixed) frees every drop, {MIN_DROPS}+ drops", "p_round_s1",
          [(0, 0.1), (0.1, 0.3), (0.3, 0.6), (0.6, 1.01)], big)
    table(f"the chance that a round at stage 0 (70-90% fixed) frees every drop, {MIN_DROPS}+ drops", "p_round_s0",
          [(0, 0.001), (0.001, 0.01), (0.01, 0.1), (0.1, 1.01)], big)
    rr = [r for r in big if r["recurring"]]
    cc = [r for r in big if r["never_short"]]
    print("\nrecurring starts against the big steps that no run missed (AUC; above 0.5: higher at the recurring):")
    for k in ("drops", "adds", "drops_size", "drops_below_0.35n", "p_round_s0", "p_round_s1", "p_round_s2",
              "cofactor"):
        print(f"  {k:20s} {auc([r[k] for r in rr], [r[k] for r in cc]):.2f}   medians {np.median([r[k] for r in rr]):g}"
              f" against {np.median([r[k] for r in cc]):g}")


if __name__ == "__main__":
    main()
