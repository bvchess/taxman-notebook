#!/usr/bin/env python3
"""Is there a property, computable without the optimum, that separates the recurring starts from the controls?
Writes features.csv (a row for each searched game below its ceiling of each first pass) and prints the tests.

    cd /home/brian/taxman_work/lab/work/gapdash/hard && nice -n 19 python3 -I pattern.py

Plain Python 3, standard library only, about a minute.  Reads plays.csv.gz (extract.py), recurrence.csv
(recurrence.py), starts.csv (compare.py, for the matched controls), the proven table (for the labels and to rebuild
the lines' sets, never for a feature) and the notebook's parity files (U* sums).

Every feature is one that the best-known lines past 5060 also have: the number theory of n, the setup of its line,
and the line of n and the lines below it in the same run.  Groups: R, the recurring starts (recurrence.csv); C, the
clean games, searched below their ceiling from moves for n - 1 at opt(n - 1) in every run and short in none; the
rest of a run's pool (games that some run left short) is counted in the rate of a rule but is neither R nor C.

Tests, for each feature and each direction: the AUC of R against C; the held-out rule, a threshold chosen on three of
four blocks of n (3001-3515, 3516-4030, 4031-4545, 4546-5060) to maximize the share of R caught less the share of C
flagged, applied to the fourth, summed over the four; and the matched comparison, each recurring start against its
3 controls of compare.py (the same thousand, cofactor within a factor of 1.5, nearest n), as the share of the pairs
where the start's value is higher (ties count half) with its two-sided sign-test P.
"""

import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves this folder off the path
from common import (HERE, HI, LO, STEPS, cofactor, factor, kind, layer, load_opt, load_parity,  # noqa: E402
                    promotions_of, read_plays, read_recurrence, seed_of, started_from)

RUNS = ["rehearsal:p1", "rehearsal2:p1", "rehearsal3:p1"]
BLOCKS = [(3001, 3515), (3516, 4030), (4031, 4545), (4546, 5060)]
REFERENCE = "proven_step_drops"  # uses the optimum: the reference, not a candidate
DROP_BINS = [(0, 0), (1, 1), (2, 2), (3, 4), (5, 6), (7, 9), (10, 99)]
YOUNG = 10  # a promotion of the line of n - 1 is young if the line of n - 1 - YOUNG lacks it


def features(run, plays, opt, par, sets):
    """n -> the features of the run's line of n, for each searched game below its ceiling that started from moves for
    n - 1 at opt(n - 1)."""
    out = {}
    rows = plays[run]
    for n in sorted(rows):
        r = rows[n]
        if r["method"] != "search" or kind(n, opt) != "below":
            continue
        s_row = started_from(plays, run, n)
        if s_row is None or int(s_row["score"]) != opt[n - 1]["score"]:
            continue
        score, below = int(r["score"]), int(s_row["score"])
        O, S, seed = sets[run][n], promotions_of(s_row, opt), seed_of(s_row, opt)
        surv = [int(t.split(":")[1]) for t in r["surv"].split()]
        surv_back = dict((int(a), int(s)) for a, s in (t.split(":") for t in r["surv"].split()))
        old = sets[run].get(n - 1 - YOUNG)
        f = factor(n)
        out[n] = {
            "logcof": math.log(cofactor(n)), "layer": layer(n), "distinct_primes": len(set(f)),
            "log_largest_prime": math.log(f[-1]), "even": int(n % 2 == 0), "below_is_prime": int(layer(n - 1) == 1),
            "ceiling_gap_per_n": (n + below - score) / n, "ceiling_gap": n + below - score,
            "parity_gap": int(r["bound"]) - score, "bound_less_ceiling": int(r["bound"]) - (n + below),
            "growth": int(r["growth"]) if r["growth"] != "" else 0,
            "rounds_gain": score - int(r["start"]),
            "start_over_surv": int(r["start"]) - surv_back[n - 1] if n - 1 in surv_back else 0,
            "improvements": int(r["n_impr"]), "trajectories": int(r["ntraj"]),
            "surv_spread": max(surv) - min(surv) if surv else 0,
            "frames": int(r["frames"]), "cands": int(r["cands"]), "d_cands": par[n][2] - par[n - 1][2],
            "slack": int(r["max_total"]) - int(r["npromo"]),
            "cap_less_greedy": (n + below - int(r["in_the_bag"])) - int(r["greedy_sum"]),
            "ustar_step_less_n": (par[n][0] - par[n - 1][0]) - n,
            "line_step": len(O ^ seed), "line_drops": len(seed - O),
            "young_share": len(S - old) / len(S) if old is not None and S else 0.0,
        }
    return out


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def best_threshold(pos, neg, sign):
    """The threshold t maximizing the share of pos with sign * x >= sign * t less the share of neg."""
    best = (-2.0, None)
    for t in sorted(set(pos) | set(neg)):
        tp = sum(sign * x >= sign * t for x in pos) / len(pos)
        fp = sum(sign * x >= sign * t for x in neg) / len(neg)
        if tp - fp > best[0]:
            best = (tp - fp, t)
    return best[1]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2
        i = j + 1
    return out


def spearman(xs, ys):
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    var = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return cov / var if var else 0.0


def sign_p(k, m):
    """Two-sided sign-test P of k successes in m pairs (ties already split)."""
    k = round(k)
    tail = sum(math.comb(m, i) for i in range(0, min(k, m - k) + 1)) / 2 ** m
    return min(1.0, 2 * tail)


def main():
    rec = read_recurrence()
    plays = read_plays()
    opt = load_opt(LO - 1, HI)
    par = load_parity(LO - 1, HI)
    sets = {run: {n: promotions_of(row, opt) for n, row in plays[run].items()} for run in RUNS}
    with open(os.path.join(HERE, "starts.csv"), newline="") as f:
        matched = [(int(r["matched_to"]), int(r["n"])) for r in csv.DictReader(f) if r["role"] == "control"]
    R = {n for n in rec if rec[n]["recurring"]}
    C = {n for n in rec if rec[n]["kind"] == "below" and rec[n]["p1_short"] + rec[n]["pk_short"]
         + rec[n]["chains_short"] == 0 and rec[n]["p1_pool"] == rec[n]["p1_runs"]
         and rec[n]["pk_pool"] == rec[n]["pk_runs"] and rec[n]["chains_pool"] == rec[n]["chains_runs"]}

    feats = {run: features(run, plays, opt, par, sets) for run in RUNS}
    names = list(next(iter(feats[RUNS[0]].values())))
    # the reference that uses the optimum: the drops of the proven step from n - 1 to n (E5's steps.json, the seed's
    # members that the proven set of n lacks)
    with open(STEPS) as f:
        step = {int(k): len(v["drops"]) for k, v in json.load(f).items()}
    for run in RUNS:
        for n, x in feats[run].items():
            x[REFERENCE] = step.get(n, 0)
    names.append(REFERENCE)
    with open(os.path.join(HERE, "features.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "n", "group", "start_here"] + names)
        for run in RUNS:
            for n, x in feats[run].items():
                group = "R" if n in R else "C" if n in C else "other"
                start = int(int(plays[run][n]["score"]) < opt[n]["score"])
                w.writerow([run, n, group, start] + [round(x[k], 6) if isinstance(x[k], float) else x[k]
                                                     for k in names])

    print(f"R: {len(R)} recurring starts {sorted(R)}; C: {len(C)} clean games")
    print(f"\nThe proven step at the searched games below their ceiling in the pool of every first pass, by its drops "
          f"({REFERENCE}, from the optimum):")
    print("drops | games | starts in the 3 first passes (per game and run) | R | C | short in a first pass")
    pool_all = sorted(set.intersection(*(set(feats[run]) for run in RUNS)))
    for lo, hi in DROP_BINS:
        gs = [n for n in pool_all if lo <= step.get(n, 0) <= hi]
        st = sum(int(plays[run][n]["score"]) < opt[n]["score"] for run in RUNS for n in gs)
        print(f"{lo}-{hi if hi < 99 else ''} | {len(gs)} | {st} ({st / max(1, 3 * len(gs)):.3f}) | "
              f"{sum(n in R for n in gs)} | {sum(n in C for n in gs)} | {sum(rec[n]['p1_short'] > 0 for n in gs)}")
    print("\nSpearman correlation of each feature with the proven step's drops, over the pool of rehearsal:p1:")
    F0 = feats[RUNS[0]]
    print("  " + ", ".join(f"{k} {spearman([F0[n][k] for n in F0], [F0[n][REFERENCE] for n in F0]):+.2f}"
                           for k in names if k != REFERENCE))

    print("\nThe line's own step as a mark of a streak's end (the first game above a streak, which the lines above a "
          "later pass give the streak): K | searched games with K+ drops | streak ends | ends among them | those "
          "with the game below short")
    for run in RUNS:
        rows = plays[run]
        short = {n for n in rows if int(rows[n]["score"]) < opt[n]["score"]}
        ends = {n + 1 for n in short if n + 1 not in short and n + 1 in rows}
        drops = {n: len(seed_of(rows[n - 1], opt) - sets[run][n]) for n in rows
                 if n - 1 in rows and rows[n]["method"] == "search"}
        for k in (7, 10, 13):
            flag = [n for n in drops if drops[n] >= k]
            print(f"  {run} | {k} | {len(flag)} of {len(drops)} | {len(ends)} | {sum(n in ends for n in flag)} | "
                  f"{sum(n - 1 in short for n in flag)}")

    totals = {k: [] for k in names}  # per run: (AUC, caught, of, flagged, of, rate, top, higher, pairs)
    for run in RUNS:
        F = feats[run]
        pool = sorted(F)
        r_in = [n for n in pool if n in R]
        c_in = [n for n in pool if n in C]
        starts = [n for n in pool if int(plays[run][n]["score"]) < opt[n]["score"]]
        print(f"\n== features of {run}'s lines: {len(pool)} games in its pool, R {len(r_in)}, C {len(c_in)}, "
              f"its own starts {len(starts)}")
        print("feature                 AUC R/C  AUC own starts/rest | held out: R caught/of, C flagged/of, rate in "
              "pool | top 10%: R caught | matched: share higher, sign P")
        for k in names:
            a = auc([F[n][k] for n in r_in], [F[n][k] for n in c_in])
            a_own = auc([F[n][k] for n in starts], [F[n][k] for n in pool if n not in starts])
            caught = flagged = rate = top = top_rate = 0
            for lo, hi in BLOCKS:
                train = [n for n in pool if not lo <= n <= hi]
                pos = [F[n][k] for n in train if n in R]
                neg = [F[n][k] for n in train if n in C]
                sign = 1 if auc(pos, neg) >= 0.5 else -1  # the direction, too, from the training blocks
                t = best_threshold(pos, neg, sign)
                test = [n for n in pool if lo <= n <= hi]
                hit = [n for n in test if sign * F[n][k] >= sign * t]
                caught += sum(n in R for n in hit)
                flagged += sum(n in C for n in hit)
                rate += len(hit)
                ranked = sorted(sign * F[n][k] for n in train)
                t10 = ranked[int(0.9 * len(ranked))]
                top += sum(n in R and sign * F[n][k] >= t10 for n in test)
                top_rate += sum(sign * F[n][k] >= t10 for n in test)  # ties at the cut can flag more than 10%
            pairs = [(g, c) for g, c in matched if g in F and c in F]
            higher = sum((F[g][k] > F[c][k]) + 0.5 * (F[g][k] == F[c][k]) for g, c in pairs)
            print(f"{k:24s} {a:5.2f}    {a_own:5.2f}           | {caught:2d}/{len(r_in)}"
                  f"  {flagged:4d}/{len(c_in)}  {rate / len(pool):5.1%} | {top:2d} | {higher / len(pairs):4.2f} of "
                  f"{len(pairs)}, P {sign_p(higher, len(pairs)):.3f}")
            totals[k].append((a, caught, len(r_in), flagged, len(c_in), rate / len(pool), top, top_rate / len(pool),
                              higher / len(pairs), sign_p(higher, len(pairs))))

    print("\n== over the three first passes: AUC R/C, mean (range) | held out: R caught, C flagged, mean share of the "
          "pool flagged | top 10%: R caught, share flagged | matched: share higher (mean), the largest sign P")
    for k in names:
        t = totals[k]
        caught, of_r, flagged, of_c = (sum(x[i] for x in t) for i in (1, 2, 3, 4))
        print(f"{k:24s} {sum(x[0] for x in t) / len(t):.2f} ({min(x[0] for x in t):.2f}-{max(x[0] for x in t):.2f}) | "
              f"{caught}/{of_r}, {flagged}/{of_c}, {sum(x[5] for x in t) / len(t):.1%} | {sum(x[6] for x in t)}/{of_r}, "
              f"{sum(x[7] for x in t) / len(t):.1%} | {sum(x[8] for x in t) / len(t):.2f}, P {max(x[9] for x in t):.3f}")


if __name__ == "__main__":
    main()
