#!/usr/bin/env python3
"""How often each game of 3001-5060 is a streak start, and short, over the runs; whether the recurrence is beyond
chance.  Writes recurrence.csv and prints the summary and the shuffle tests.

    cd /home/brian/taxman_work/lab/work/gapdash/hard && nice -n 19 python3 -I recurrence.py

Plain Python 3, standard library only.  Reads plays.csv.gz (extract.py) and the proven table.

In a run, a game is *short* when its line scores below opt(n), and a *start* when it is short and the moves for n - 1
that it started from (`prev` of its line) score opt(n - 1); a line with no `prev` (an unseeded play's) takes the run's
line of n - 1, and in a pass after the first the better of that and the state before the pass.  A searched game is an
*own failure* when it falls short by more than it carries: a start, or a game whose shortfall is more than that of the
moves it started from less its ceiling gap c(n) = n + opt(n - 1) - opt(n).  A game is in a run's *pool* when the run
searched it (method `search`), it lies below its ceiling, and the moves it started from were at opt(n - 1): the games
that could have been starts.

Groups of runs: p1, the first passes of the three rehearsals (seeds 1, 101, 201, the same procedure); pk, their later
passes (seeds 2-4, 102-104, 202-204, no stop, descending, from the state the passes before left); chains, the 19 chains
of B14 and B17 (seed 1, levels 1-4 and other settings; 7 on 3001-4000, 12 on 4001-5060), which are not independent of
rehearsal:p1 (b17:q3, b17:q3-h and b14:l3 have its lines exactly).  The shuffle draws each run's starts again from its
own pool, keeping its count (and, stratified, its count in each stratum of range and cofactor).
"""

import csv
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves this folder off the path
from common import HI, LO, RECURRENCE, cofactor, factor, kind, layer, load_opt, read_plays  # noqa: E402

SHUFFLES = 20000
SEED = 20261109


def classify(plays, opt):
    """run -> n -> (short_by, start, own, pool) for each game of the run."""
    out = {}
    state = {}  # rehearsal -> n -> best score over the passes so far
    for run in plays:
        rows = plays[run]
        family = next(iter(rows.values()))["family"]
        k = int(next(iter(rows.values()))["pass"])
        before = state.get(family, {}) if k > 1 else {}
        lo = min(rows)
        res = {}
        for n in sorted(rows):
            r = rows[n]
            sb = opt[n]["score"] - int(r["score"])
            if r["prev_score"] != "":
                prev = int(r["prev_score"])
            elif n == lo:
                prev = opt[n - 1]["score"]
            else:
                prev = max(int(rows[n - 1]["score"]), before.get(n - 1, 0))
            sb_prev = opt[n - 1]["score"] - prev
            c = n + opt[n - 1]["score"] - opt[n]["score"]
            searched = r["method"] == "search"
            start = sb > 0 and sb_prev == 0
            own = sb > 0 and (sb_prev == 0 or (searched and sb > max(0, sb_prev - c)))
            pool = searched and kind(n, opt) == "below" and sb_prev == 0
            res[n] = (sb, start, own, pool)
        out[run] = res
        if family.startswith("rehearsal"):
            s = state.setdefault(family, {})
            for n in rows:
                s[n] = max(s.get(n, 0), int(rows[n]["score"]))
    return out


def group_of(run):
    if run.startswith("rehearsal"):
        return "p1" if run.endswith(":p1") else "pk"
    return "chains"


def overlap_stats(sets):
    """Games in two or more of the sets, in three or more, and the sum of the pairwise overlaps."""
    c = Counter(g for s in sets for g in s)
    pairs = sum(len(a & b) for i, a in enumerate(sets) for b in sets[i + 1:])
    return sum(1 for v in c.values() if v >= 2), sum(1 for v in c.values() if v >= 3), pairs


def shuffle_test(runs, cls, strata, label):
    """Observed overlap of the runs' starts against SHUFFLES draws that keep each run's count per stratum."""
    sets, pools = [], []
    for run in runs:
        starts = {n for n, v in cls[run].items() if v[1]}
        pool = {n for n, v in cls[run].items() if v[3]}
        outside = starts - pool
        if outside:
            print(f"  note: {run} has starts outside its pool: {sorted(outside)}")
        sets.append(starts)
        pools.append(pool)
    obs = overlap_stats(sets)
    rng = random.Random(SEED)
    by = []
    for s, pool in zip(sets, pools):
        need = Counter(strata(n) for n in s)
        cells = {}
        for n in sorted(pool | s):
            cells.setdefault(strata(n), []).append(n)
        by.append((need, cells))
    sims = []
    for _ in range(SHUFFLES):
        draw = []
        for need, cells in by:
            d = set()
            for cell, m in need.items():
                d.update(rng.sample(cells[cell], m))
            draw.append(d)
        sims.append(overlap_stats(draw))
    print(f"{label}: runs {len(runs)}, starts {[len(s) for s in sets]}, pools {[len(p) for p in pools]}")
    for i, name in enumerate(("in 2+ runs", "in 3+ runs", "pairwise overlaps")):
        vals = sorted(x[i] for x in sims)
        mean = sum(vals) / len(vals)
        p = sum(1 for v in vals if v >= obs[i]) / len(vals)
        print(f"  {name}: observed {obs[i]}, shuffled mean {mean:.2f} (95th percentile {vals[int(0.95 * len(vals))]}"
              f", max {vals[-1]}), P(shuffled >= observed) = {p:.5f}")
    return obs


def main():
    opt = load_opt(LO - 1, HI, promotions=False)
    plays = read_plays()
    cls = classify(plays, opt)
    runs = list(plays)
    groups = {g: [r for r in runs if group_of(r) == g] for g in ("p1", "pk", "chains")}
    print("runs:", {g: len(v) for g, v in groups.items()}, "; passes after the first:", groups["pk"])

    # strata: the range (3001-4000, 4001-5060) and the quartile of the cofactor among the games below their ceiling
    below = sorted(cofactor(n) for n in range(LO, HI + 1) if kind(n, opt) == "below")
    cuts = [below[len(below) * q // 4] for q in (1, 2, 3)]

    def stratum(n):
        return (n > 4000, sum(cofactor(n) >= c for c in cuts))

    print(f"cofactor quartile cuts among the {len(below)} games below their ceiling: {cuts}")
    shuffle_test(groups["p1"], cls, lambda n: 0, "first passes, uniform")
    shuffle_test(groups["p1"], cls, stratum, "first passes, stratified by range and cofactor quartile")
    seeds = groups["p1"] + groups["pk"]
    shuffle_test(seeds, cls, lambda n: 0, "every pass (a seed each), uniform")
    shuffle_test(seeds, cls, stratum, "every pass, stratified")

    rows = []
    for n in range(LO, HI + 1):
        row = {"n": n, "kind": kind(n, opt), "factors": "*".join(map(str, factor(n))), "layer": layer(n),
               "cofactor": cofactor(n), "c": n + opt[n - 1]["score"] - opt[n]["score"]}
        for g, rs in groups.items():
            have = [r for r in rs if n in cls[r]]
            row[f"{g}_runs"] = len(have)
            row[f"{g}_pool"] = sum(cls[r][n][3] for r in have)
            row[f"{g}_starts"] = sum(cls[r][n][1] for r in have)
            row[f"{g}_own"] = sum(cls[r][n][2] for r in have)
            row[f"{g}_short"] = sum(cls[r][n][0] > 0 for r in have)
            row[f"{g}_max_short"] = max((cls[r][n][0] for r in have), default=0)
        row["p1_start_runs"] = " ".join(r.split(":")[0] for r in groups["p1"] if cls[r].get(n, (0, 0))[1])
        row["pk_start_runs"] = " ".join(r for r in groups["pk"] if cls[r].get(n, (0, 0))[1])
        row["chain_start_runs"] = " ".join(r.split(":")[1] for r in groups["chains"] if cls[r].get(n, (0, 0))[1])
        seeds_started = row["p1_starts"] + row["pk_starts"]
        row["seed_starts"] = seeds_started
        row["recurring"] = int(row["p1_starts"] >= 2 or seeds_started >= 3)
        rows.append(row)
    with open(RECURRENCE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print("\nper game, first passes (of 3): starts -> games:",
          dict(sorted(Counter(r["p1_starts"] for r in rows if r["p1_starts"]).items())))
    print("per game, first passes: own failures -> games:",
          dict(sorted(Counter(r["p1_own"] for r in rows if r["p1_own"]).items())))
    print("per game, first passes: short -> games:",
          dict(sorted(Counter(r["p1_short"] for r in rows if r["p1_short"]).items())))
    print("per game, every pass: starts -> games:",
          dict(sorted(Counter(r["seed_starts"] for r in rows if r["seed_starts"]).items())))
    print("\nthe games that start a streak in a first pass or in two passes:")
    print("  n  factors  cofactor  c  | p1 starts (runs) | later-pass starts | chains: starts/pool, short | max short")
    for r in rows:
        if r["p1_starts"] or r["seed_starts"] >= 2:
            print(f"  {r['n']} {r['factors']:>12} {r['cofactor']:>5} {r['c']:>5} | {r['p1_starts']} "
                  f"({r['p1_start_runs']}) | {r['pk_starts']}/{r['pk_pool']} of {r['pk_runs']} "
                  f"| {r['chains_starts']}/{r['chains_pool']} of {r['chains_runs']}, short {r['chains_short']} "
                  f"| {max(r['p1_max_short'], r['pk_max_short'])}{'  RECURRING' if r['recurring'] else ''}")


if __name__ == "__main__":
    main()
