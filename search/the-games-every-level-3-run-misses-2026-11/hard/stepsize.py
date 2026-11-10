#!/usr/bin/env python3
"""Can the size of the proven step from n - 1 to n be foreseen without the optimum?  And does a game that should need
a big step but whose line made a small one point to the stuck games?  Prints the held-out tests.

    cd /home/brian/taxman_work/lab/work/gapdash/hard && OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
        nice -n 19 /home/brian/taxman_work/lab/work/stats-venv/bin/python3 -I -B stepsize.py

The stats venv's Python (numpy, scikit-learn), about a minute.  Reads the proven table, the notebook's parity files,
E5's steps.json, recurrence.csv and features.csv (pattern.py).

The target: a *big step*, 7 or more drops (every recurring start has 7 or more, bigsteps.py).  The features are those
a best-known line has past 5060: the number theory of n, the setup of its board, its bound, U*, and the scores of the
lines of n and n - 1 (from the proven table here, where they are opt(n) and opt(n - 1); past 5060 the best-known
scores would stand in).  The model: an L2 logistic regression on standardized features, fitted on the searched games
below their ceiling of 1001-5060 with blocks of 500 games held out in turn, so each game's P(big) comes from a fit that
never saw its block.  The rules flag the top share of a first pass's pool by P(big), the cut taken from the pool
outside the block tested, alone or with the line's own step at most a few drops.
"""

import csv
import gzip
import json
import math
import os
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves this folder off the path
from common import HERE, HI, RESULTS, STEPS, cofactor, factor, layer, load_parity, read_recurrence  # noqa: E402

TRAIN_LO = 1001
BIG = 7
BLOCK = 500
NAMES = ["logcof", "layer", "distinct_primes", "log_largest_prime", "even", "below_is_prime", "ceiling_gap_per_n",
         "log_ceiling_gap", "parity_gap_per_n", "bound_less_ceiling_per_n", "frames", "cands_per_n", "d_cands",
         "slack", "cap_less_greedy_per_n", "ustar_step_less_n_per_n"]


def feature_row(n, score, below, bag, setup, npromo, par):
    """The features of game n from its line's score, the score of the line of n - 1, in_the_bag, setup and promotions,
    and the parity files' U* sums, bounds and candidates."""
    f = factor(n)
    c = n + below - score
    return [math.log(cofactor(n)), layer(n), len(set(f)), math.log(f[-1]), n % 2 == 0, layer(n - 1) == 1, c / n,
            math.log1p(max(c, 0)), (par[n][1] - score) / n, (par[n][1] - (n + below)) / n, setup["frames"],
            setup["candidates"] / n, par[n][2] - par[n - 1][2], setup["max_total"] - npromo,
            ((n + below - bag) - setup["greedy_sum"]) / n, (par[n][0] - par[n - 1][0] - n) / n]


def training(par):
    """n -> (features, drops) for the searched games below their ceiling of TRAIN_LO..HI."""
    with open(STEPS) as f:
        steps = {int(k): len(v["drops"]) for k, v in json.load(f).items()}
    out, prev = {}, None
    with gzip.open(RESULTS, "rt") as f:
        for text in f:
            x = json.loads(text)
            n = x["n"]
            if prev is not None and TRAIN_LO <= n <= HI and x["method"] == "search" and n in steps \
                    and x["score"] < n + prev:
                out[n] = (feature_row(n, x["score"], prev, x["in_the_bag"], x["setup"], len(x["promotions"]), par),
                          steps[n])
            prev = x["score"]
    return out


def fit(X, y):
    scaler = StandardScaler().fit(X)
    model = LogisticRegression(C=1.0, max_iter=2000).fit(scaler.transform(X), y)
    return scaler, model


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    par = load_parity(2, HI)
    data = training(par)
    ns = sorted(data)
    X = np.array([data[n][0] for n in ns], dtype=float)
    y = np.array([data[n][1] >= BIG for n in ns])
    block = np.array([(n - TRAIN_LO) // BLOCK for n in ns])
    p = np.zeros(len(ns))
    for b in sorted(set(block)):
        scaler, model = fit(X[block != b], y[block != b])
        p[block == b] = model.predict_proba(scaler.transform(X[block == b]))[:, 1]
    p_big = dict(zip(ns, p))
    print(f"training: {len(ns)} searched games below their ceiling of {TRAIN_LO}-{HI}, {int(y.sum())} with a big step "
          f"({BIG}+ drops)")
    print(f"held-out AUC of P(big) for a big step: {roc_auc_score(y, p):.3f}; Spearman with the drops: "
          f"{spearman(p, [data[n][1] for n in ns]):+.2f}")
    for i, k in enumerate(NAMES):
        a = roc_auc_score(y, X[:, i])
        print(f"  {k:26s} AUC alone {max(a, 1 - a):.3f} ({'+' if a >= 0.5 else '-'})")
    scaler, model = fit(X, y)
    print("  weights per standard deviation, all of the training:",
          ", ".join(f"{k} {w:+.2f}" for k, w in zip(NAMES, model.coef_[0])))

    rec = read_recurrence()
    R = {n for n in rec if rec[n]["recurring"]}
    C = {n for n in rec if rec[n]["kind"] == "below" and rec[n]["p1_short"] + rec[n]["pk_short"]
         + rec[n]["chains_short"] == 0 and rec[n]["p1_pool"] == rec[n]["p1_runs"]
         and rec[n]["pk_pool"] == rec[n]["pk_runs"] and rec[n]["chains_pool"] == rec[n]["chains_runs"]}
    rows = {}
    with open(os.path.join(HERE, "features.csv"), newline="") as f:
        for r in csv.DictReader(f):
            rows.setdefault(r["run"], {})[int(r["n"])] = r
    for run, F in rows.items():
        pool = [n for n in sorted(F) if n in p_big]
        r_in = [n for n in pool if n in R]
        c_in = [n for n in pool if n in C]
        starts = [n for n in pool if F[n]["start_here"] == "1"]
        a_rc = roc_auc_score([n in R for n in r_in + c_in], [p_big[n] for n in r_in + c_in])
        a_st = roc_auc_score([n in starts for n in pool], [p_big[n] for n in pool])
        print(f"\n{run}: pool {len(pool)}, R {len(r_in)}, C {len(c_in)}, starts {len(starts)}; held-out AUC of P(big): "
              f"R/C {a_rc:.2f}, starts/rest {a_st:.2f}")
        for top in (0.05, 0.10, 0.20):
            for small in (None, 2, 4):
                caught = flagged = hits = starts_hit = 0
                for b in sorted({(n - TRAIN_LO) // BLOCK for n in pool}):
                    # the cut: the quantile of P(big) over the pool outside the block (no label used)
                    train = [n for n in pool if (n - TRAIN_LO) // BLOCK != b]
                    cut = sorted(p_big[n] for n in train)[int((1 - top) * len(train))]
                    test = [n for n in pool if (n - TRAIN_LO) // BLOCK == b]
                    hit = [n for n in test if p_big[n] >= cut
                           and (small is None or int(F[n]["line_drops"]) <= small)]
                    caught += sum(n in R for n in hit)
                    flagged += sum(n in C for n in hit)
                    starts_hit += sum(n in starts for n in hit)
                    hits += len(hit)
                rule = f"P(big) in the top {top:.0%}" + (f" and the line's drops <= {small}" if small is not None else "")
                print(f"  {rule:48s}: flags {hits} ({hits / len(pool):.1%}), R {caught}/{len(r_in)}, "
                      f"C {flagged}/{len(c_in)}, this run's starts {starts_hit}/{len(starts)}")


if __name__ == "__main__":
    main()
