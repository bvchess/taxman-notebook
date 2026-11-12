#!/usr/bin/env python3
"""The tables of the controls.  For each run of fix-smooth: which part was fixed, its size, the gap of the restricted
root's GF(2) bound over opt(n), and the search's steps and CPU.  A run found in several files is shown once, its
finished line first, then the line of the file given first.

    python3 -I summarize_fix.py fix.jsonl scan.jsonl [--fit] [--min-gap G]

With --fit, per game: least-squares fits of log10(steps) over the finished runs whose gap is at least --min-gap
(default 1100), on the gap alone, on the gap and log10 of the free candidates, and on those with an indicator of the
smooth part fixed (the smooth part of B = 13 fixed, in whole or at random, the rest free), with each run's residual
from the second fit.  With --pairs, the gaps of the runs that fix a part and of those that fix its complement (the
rough part against the smooth part of the same B, a random draw against the rest of its part), against the root's.
"""

import argparse
import json
import math
import statistics


def key_of(line):
    return (line["n"], line["smooth"], bool(line.get("rough")), line.get("random"), line.get("seed"),
            bool(line.get("complement")))


def part_of(line):
    """A short name for the part a line fixed."""
    b = line["smooth"]
    kind = "rough" if line.get("rough") else "smooth"
    if kind == "smooth" and b >= line["n"]:
        kind, b = "any", None
    name = kind if b is None else f"{kind} {b}"
    if line.get("random") is not None:
        drawn = "all but " if line.get("complement") else ""
        name += f", {drawn}{line['random']} at random (seed {line['seed']})"
    return name


def smooth_fixed(line):
    """Whether the run fixes candidates of the smooth part only (all of them, or some drawn at random)."""
    return not line.get("rough") and line["smooth"] < line["n"]


def load(paths):
    runs = {}
    for path in paths:
        with open(path) as f:
            for text in f:
                line = json.loads(text)
                k = key_of(line)
                if k not in runs or (line["completed"] and not runs[k]["completed"]):
                    runs[k] = line
    return list(runs.values())


def gap_of(line):
    return line["bound"] - line["opt"] if line.get("bound") is not None else None


def solve(rows, ys):
    """Least squares: the coefficients b with rows · b nearest ys, by the normal equations."""
    m = len(rows[0])
    a = [[sum(r[i] * r[j] for r in rows) for j in range(m)] for i in range(m)]
    v = [sum(r[i] * y for r, y in zip(rows, ys)) for i in range(m)]
    for c in range(m):
        p = max(range(c, m), key=lambda i: abs(a[i][c]))
        a[c], a[p], v[c], v[p] = a[p], a[c], v[p], v[c]
        for i in range(m):
            if i != c:
                f = a[i][c] / a[c][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[c])]
                v[i] -= f * v[c]
    return [v[i] / a[i][i] for i in range(m)]


def inverse(a):
    """The inverse of the small square matrix `a`, by Gauss-Jordan elimination."""
    m = len(a)
    work = [row[:] + [1.0 if i == j else 0.0 for j in range(m)] for i, row in enumerate(a)]
    for c in range(m):
        p = max(range(c, m), key=lambda i: abs(work[i][c]))
        work[c], work[p] = work[p], work[c]
        pivot = work[c][c]
        work[c] = [x / pivot for x in work[c]]
        for i in range(m):
            if i != c:
                f = work[i][c]
                work[i] = [x - f * y for x, y in zip(work[i], work[c])]
    return [row[m:] for row in work]


def fit(points, features, names):
    """The least-squares fit, its residuals, their sd, and the coefficients with their standard errors as text."""
    rows = [features(line, gap) for line, gap, _ in points]
    ys = [y for _, _, y in points]
    b = solve(rows, ys)
    res = [y - sum(x * c for x, c in zip(r, b)) for r, y in zip(rows, ys)]
    sd = math.sqrt(sum(e * e for e in res) / max(1, len(ys) - len(b)))
    m = len(b)
    cov = inverse([[sum(r[i] * r[j] for r in rows) for j in range(m)] for i in range(m)])
    terms = ", ".join(f"{name} {c:+.5f} ± {sd * math.sqrt(cov[i][i]):.5f}" for i, (name, c) in enumerate(zip(names, b)))
    return b, res, sd, terms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--fit", action="store_true")
    parser.add_argument("--pairs", action="store_true")
    parser.add_argument("--bands", action="store_true")
    parser.add_argument("--band", type=int, default=200, help="the width of a band of gap")
    parser.add_argument("--min-gap", type=int, default=1100)
    args = parser.parse_args()
    runs = sorted(load(args.files), key=lambda line: (line["n"], gap_of(line) or -10**9))
    print("| n | part | fixed + barred | free | gap | steps | CPU s | finished |")
    print("|---:|---|---:|---:|---:|---:|---:|---|")
    for line in runs:
        print(f"| {line['n']} | {part_of(line)} | {line['fixed']} + {line['barred']} | {line['free']} | "
              f"{gap_of(line)} | {line['nodes']:,} | {line['cpu']:.1f} | {'yes' if line['completed'] else 'no'} |")
    if args.pairs:
        by_key = {key_of(line): line for line in runs}
        print("\nSplits of all the candidates in two: the gap with one side fixed, with the other fixed, their sum, "
              "and the root's gap")
        for line in runs:
            n, b, rough, random, seed, comp = key_of(line)
            if comp or rough or (random is None) == (b >= n):
                continue
            other = by_key.get((n, b, True, None, None, False) if random is None else (n, b, False, random, seed, True))
            if other is None:
                continue
            root = line["root_bound"] - line["opt"]
            g1, g2 = gap_of(line), gap_of(other)
            print(f"  {n} {part_of(line)}: {g1} + {part_of(other)}: {g2} = {g1 + g2} against {root} "
                  f"({g1 + g2 - root:+d})")
        print("\nSplits of a part in two: the gap each half removes when fixed, their sum, and what the whole part "
              "removes")
        for line in runs:
            n, b, rough, random, seed, comp = key_of(line)
            if comp or random is None or b >= n:
                continue
            other = by_key.get((n, b, rough, random, seed, True))
            whole = by_key.get((n, b, rough, None, None, False))
            if other is None or whole is None:
                continue
            root = line["root_bound"] - line["opt"]
            r1, r2, r = root - gap_of(line), root - gap_of(other), root - gap_of(whole)
            print(f"  {n} {part_of(line)}: {r1} + the rest of it: {r2} = {r1 + r2} against {r} ({r1 + r2 - r:+d})")
    if args.bands:
        for n in sorted({line["n"] for line in runs}):
            done = [line for line in runs if line["n"] == n and line["completed"]]
            kinds = [("small primes fixed", lambda line: smooth_fixed(line)),
                     ("small primes free", lambda line: bool(line.get("rough"))),
                     ("drawn from all", lambda line: not line.get("rough") and line["smooth"] >= line["n"])]
            print(f"\nn = {n}: the median steps of the finished runs by band of gap (runs in parentheses)")
            print("| gap | " + " | ".join(name for name, _ in kinds) + " |")
            print("|---|" + "---:|" * len(kinds))
            for lo in range(0, 2600, args.band):
                cells = []
                for _, is_kind in kinds:
                    steps = sorted(line["nodes"] for line in done
                                   if is_kind(line) and lo <= gap_of(line) < lo + args.band)
                    cells.append(f"{statistics.median(steps):,.0f} ({len(steps)})" if steps else "")
                if any(cells):
                    print(f"| {lo}-{lo + args.band - 1} | " + " | ".join(cells) + " |")
    if not args.fit:
        return
    for n in sorted({line["n"] for line in runs}):
        points = [(line, gap_of(line), math.log10(line["nodes"])) for line in runs
                  if line["n"] == n and line["completed"] and gap_of(line) is not None
                  and gap_of(line) >= args.min_gap]
        if len(points) < 5:
            continue
        print(f"\nn = {n}: {len(points)} finished runs of gap >= {args.min_gap}, log10(steps) fitted on")
        _, _, sd, terms = fit(points, lambda line, gap: [1.0, gap], ["1", "gap"])
        print(f"  the gap: {terms}; residual sd {sd:.2f}")
        _, res, sd, terms = fit(points, lambda line, gap: [1.0, gap, math.log10(line["free"])],
                                ["1", "gap", "log10 free"])
        print(f"  the gap and the free candidates: {terms}; residual sd {sd:.2f}")
        _, _, sd3, terms = fit(points, lambda line, gap: [1.0, gap, math.log10(line["free"]),
                                                          1.0 if smooth_fixed(line) else 0.0],
                               ["1", "gap", "log10 free", "smooth fixed"])
        print(f"  those and the smooth part fixed: {terms}; residual sd {sd3:.2f}")
        for (line, gap, _), e in sorted(zip(points, res), key=lambda p: p[0][1]):
            print(f"    {part_of(line)}: gap {gap}, free {line['free']}, residual {e:+.2f} decades")


if __name__ == "__main__":
    main()
