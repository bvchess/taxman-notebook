#!/usr/bin/env python3
"""Pilot P1 of the unsound mode: checks the lines of the two seeds and prints the entry's numbers.

    nice -n 19 python3 -I analyze.py [DIR]

DIR (default: the folder of this script) holds sample.json (the games, with the numbers of the run of 2026-11-01 that
the experiment `where-the-best-scores-came-from-2026-11` found), and seed-1.jsonl and seed-2.jsonl (the unsound lines of
the two seeds).  The script changes nothing; everything it prints is a number of the entry.
"""

import json
import math
import os
import statistics
import sys

SEEDS = (1, 2)
EFFORT = 9
ROUNDS = 1 << (EFFORT - 1)  # 256
LEVELS = [(e, 0 if e == 0 else 1 << (e - 1)) for e in range(EFFORT + 1)]  # (effort, rounds)
EARLY = 16  # a last improvement by this round counts as stuck early
SEARCHED, SEARCHED_WITH_START_OPTIMAL = 568, 317  # games of 3441-5060 of method search, and those whose start held P*
COMMIT = "e37d6a1"
BANDS = [(3441, 3800), (3801, 4200), (4201, 4600), (4601, 5060)]
THREADS = 4
NEIGHBORHOODS = 64  # a round's neighborhoods (NEIGHBORHOODS of search::finder)
UNIT_LIMIT = 1024  # the steps allowed a neighborhood
MANY = 8  # the cost of a round is measured on lines of at least this many rounds


def median(values):
    return statistics.median(values) if values else None


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "-"


def fmt(x, digits=1):
    return "-" if x is None else f"{x:.{digits}f}" if isinstance(x, float) else str(x)


def clopper_pearson(k, n, alpha=0.10):
    """The exact two-sided binomial interval of k successes in n trials, at confidence 1 - alpha."""

    def tail_ge(p):  # P(X >= k)
        return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def tail_le(p):  # P(X <= k)
        return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(0, k + 1))

    def bisect(f, target, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if (f(mid) < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    low = 0.0 if k == 0 else bisect(tail_ge, alpha / 2, True)
    high = 1.0 if k == n else bisect(tail_le, alpha / 2, False)
    return low, high


def load(directory):
    with open(os.path.join(directory, "sample.json")) as f:
        sample = json.load(f)
    lines = {}
    for seed in SEEDS:
        lines[seed] = {}
        path = os.path.join(directory, f"seed-{seed}.jsonl")
        with open(path) as f:
            for text in f:
                if text.strip():
                    line = json.loads(text)
                    lines[seed][line["n"]] = line
    return sample, lines


def score_after(line, rounds):
    """The score of the game after `rounds` rounds: the start's, or the last improvement's by then."""
    score = line["start"]
    for raised in line["improvements"]:
        if raised["round"] <= rounds:
            score = raised["score"]
    return score


def reached_round(line):
    """The round after which the game held the known score, or None."""
    return line["stop_at_known"]["round"]


def check_lines(sample, lines):
    """Section A: the checks of the lines.  Returns the number of failures."""
    print("== A. Checks of the lines ==")
    failures = 0

    def fail(text):
        nonlocal failures
        failures += 1
        print("  FAIL:", text)

    for seed in SEEDS:
        missing = [g["n"] for g in sample if g["n"] not in lines[seed]]
        extra = sorted(set(lines[seed]) - {g["n"] for g in sample})
        print(f"  seed {seed}: {len(lines[seed])} lines; missing {missing}; extra {extra}")
        failures += len(missing) + len(extra)
    methods = {}
    builds = set()
    for seed in SEEDS:
        for line in lines[seed].values():
            methods.setdefault(line["method"], []).append((seed, line["n"]))
            builds.add((line["build"]["commit"][:7], line["build"]["dirty"]))
            for key, want in (("effort", EFFORT), ("threads", THREADS), ("from_known", True), ("seed", seed)):
                if line[key] != want:
                    fail(f"seed {seed} game {line['n']}: {key} is {line[key]}, not {want}")
            if line["prev"]["source"] != "table":
                fail(f"seed {seed} game {line['n']}: prev.source {line['prev']['source']}")
            if line["prev"]["short_by"] > 0:
                print(f"  note: seed {seed} game {line['n']}: the game before is short by at least "
                      f"{line['prev']['short_by']}")
    print("  methods:", {m: len(v) for m, v in methods.items()}, "(want only search)")
    for method, where in methods.items():
        if method != "search":
            fail(f"method {method}: {where}")
    print("  builds:", sorted(builds), f"(want [('{COMMIT}', False)])")
    if builds != {(COMMIT, False)}:
        fail("build differs")
    start_diffs, over, known_diffs = [], [], []
    relation = {"equal": 0, "higher": 0, "lower": 0}
    at_known_at_start = {seed: 0 for seed in SEEDS}
    for g in sample:
        for seed in SEEDS:
            line = lines[seed].get(g["n"])
            if line is None:
                continue
            bag = line["in_the_bag"]
            start = line["start"] - bag
            relation["equal" if start == g["start"] else "higher" if start > g["start"] else "lower"] += 1
            if start != g["start"]:
                start_diffs.append((seed, g["n"], start, g["start"], g["opt"]))
            at_known_at_start[seed] += start == g["opt"]
            if line["score"] - bag > g["opt"]:
                over.append((seed, g["n"], line["score"] - bag, g["opt"]))
            if line["stop_at_known"]["known"] - bag != g["opt"]:
                known_diffs.append((seed, g["n"], line["stop_at_known"]["known"] - bag, g["opt"]))
    print(f"  start less in_the_bag against the start of the run of 2026-11-01: {relation} of {2 * len(sample)} lines")
    print(f"  lines whose start already holds the known score: {at_known_at_start} (the run's starts held it in "
          f"none of the {len(sample)} games, which were chosen so)")
    for item in start_diffs:
        print("    (seed, n, line's start, run's start, opt):", item)
    print(f"  score above the table's: {len(over)}; known less in_the_bag differs from opt: {len(known_diffs)}")
    failures += len(over) + len(known_diffs) + relation["lower"]
    differ = []
    for g in sample:
        a, b = lines[1].get(g["n"]), lines[2].get(g["n"])
        if a and b and (a["start"], a["in_the_bag"], a["setup"]) != (b["start"], b["in_the_bag"], b["setup"]):
            differ.append(g["n"])
    print(f"  the two seeds differ in start, in_the_bag or setup in {len(differ)} games: {differ}")
    failures += len(differ)
    return failures


def per_game_rows(sample, lines):
    """Section 1: one row a game."""
    print("\n== 1. Per game ==")
    print("  e0 = opt less the start of the run of 2026-11-01; b1 = opt less this build's start; reach = round at "
          "which the known score was held ('-' never); last = round of the last improvement (0: none); fin = final "
          "shortfall; s = seconds; st/nb = steps per neighborhood")
    header = (f"{'n':>5} {'e0':>5} {'b1':>5} | " + " | ".join(
        f"s{seed}: {'reach':>5} {'last':>4} {'fin':>4} {'s':>7} {'st/nb':>6}" for seed in SEEDS))
    print(header)
    rows = []
    for g in sample:
        row = {"n": g["n"], "short0": g["opt"] - g["start"]}
        cells = []
        for seed in SEEDS:
            line = lines[seed][g["n"]]
            bag = line["in_the_bag"]
            last = max((r["round"] for r in line["improvements"]), default=0)
            reach = reached_round(line)
            final = g["opt"] - (line["score"] - bag)
            per_nb = line["steps"] / line["neighborhoods"] if line["neighborhoods"] else None
            row[seed] = {"reach": reach, "last": last, "final": final, "seconds": line["seconds"],
                         "start_seconds": line["start_seconds"], "rounds": line["rounds"],
                         "steps_per_nb": per_nb, "start_short": g["opt"] - (line["start"] - bag)}
            cells.append(f"{fmt(reach):>5} {last:>4} {final:>4} {line['seconds']:>7.1f} {fmt(per_nb, 1):>6}")
        rows.append(row)
        start_short = row[1]["start_short"]
        print(f"{g['n']:>5} {row['short0']:>5} {start_short:>5} | " + " | ".join(f"{c:>31}" for c in cells))
    return rows


def shortfall_tables(sample, lines, rows):
    """Adds to each row the shortfall of each seed after each level's rounds (0 once the known score is held)."""
    for g, row in zip(sample, rows):
        for seed in SEEDS:
            line = lines[seed][g["n"]]
            bag = line["in_the_bag"]
            row[seed]["short_at"] = {rounds: g["opt"] - (score_after(line, rounds) - bag) for _, rounds in LEVELS}


def short_after(row, seed, rounds):
    """The shortfall of a game after `rounds` rounds of one seed, or of the better of the two ("better")."""
    if seed == "better":
        return min(row[s]["short_at"][rounds] for s in SEEDS)
    return row[seed]["short_at"][rounds]


def print_curve(rows):
    """Section 2: the share at the known score after each effort, per seed and for the better of the two."""
    total = len(rows)
    print("\n== 2. The curve: the share of the sample at the known score after R rounds ==")
    print(f"  {total} games.  For the games left short: the median and maximum shortfall, in points.")
    print(f"  {'effort':>6} {'rounds':>6} | " + " | ".join(
        f"seed {seed}: {'at known':>8} {'share':>6} {'med':>5} {'max':>5}" for seed in SEEDS + ("better",)))
    out = []
    for effort, rounds in LEVELS:
        cells = []
        record = {"effort": effort, "rounds": rounds}
        for seed in SEEDS + ("better",):
            shorts = [short_after(row, seed, rounds) for row in rows]
            at = sum(1 for s in shorts if s == 0)
            left = [s for s in shorts if s > 0]
            record[seed] = (at, left)
            cells.append(f"{at:>8} {pct(at, total):>6} {fmt(median(left)):>5} {fmt(max(left) if left else None):>5}")
        out.append(record)
        print(f"  {effort:>6} {rounds:>6} | " + " | ".join(f"{c:>27}" for c in cells))
    short_at_start = [r for r in rows if r[1]["short_at"][0] > 0]
    print(f"\n  Of the {len(short_at_start)} games short at the start (the start is the same for both seeds), "
          "the share at the known score:")
    print(f"  {'effort':>6} {'rounds':>6} | " + " | ".join(f"{label:>14}" for label in ("seed 1", "seed 2", "better")))
    for effort, rounds in LEVELS:
        cells = []
        for seed in SEEDS + ("better",):
            at = sum(1 for r in short_at_start if short_after(r, seed, rounds) == 0)
            cells.append(f"{at}/{len(short_at_start)} {pct(at, len(short_at_start)):>6}")
        print(f"  {effort:>6} {rounds:>6} | " + " | ".join(f"{c:>14}" for c in cells))
    print("\n  The same total rounds, one seed or two (two seeds at R rounds each against one seed at 2R rounds):")
    print(f"  {'total':>5} | {'seed 1 at 2R':>12} {'seed 2 at 2R':>12} | {'better of two at R':>18}")
    by_rounds = {record["rounds"]: record for record in out}
    for rounds in (1, 2, 4, 8, 16, 32, 64, 128):
        double = by_rounds[2 * rounds]
        print(f"  {2 * rounds:>5} | {double[1][0]:>12} {double[2][0]:>12} | {by_rounds[rounds]['better'][0]:>18}")
    return out


def estimate(curve_rows, total):
    """Section 3: the estimate for the 568 searched games of 3441-5060."""
    print(f"\n== 3. Estimate for all {SEARCHED} searched games of 3441-5060 (one estimate, from one sample) ==")
    hard = SEARCHED - SEARCHED_WITH_START_OPTIMAL
    print(f"  ({SEARCHED_WITH_START_OPTIMAL} + {hard} x the sample's share) / {SEARCHED};"
          " 90% interval: the exact (Clopper-Pearson) binomial interval of the sample's share")
    print(f"  {'effort':>6} {'rounds':>6} | " + " | ".join(
        f"{label:>34}" for label in ("seed 1", "seed 2", "better of the two")))
    for record in curve_rows:
        cells = []
        for seed in SEEDS + ("better",):
            k = record[seed][0]
            low, high = clopper_pearson(k, total)
            est = lambda p: 100 * (SEARCHED_WITH_START_OPTIMAL + hard * p) / SEARCHED
            cells.append(f"{k}/{total}={100 * k / total:5.1f}% -> {est(k / total):5.1f}% "
                         f"[{est(low):5.1f}, {est(high):5.1f}]")
        print(f"  {record['effort']:>6} {record['rounds']:>6} | " + " | ".join(f"{c:>34}" for c in cells))
    print(f"  (the interval of the share itself is not corrected for the sample being {total} of {hard} games)")


def stalls(rows):
    """Sections 4 and 5: the games a seed missed, when its last improvement came, and what the other seed did."""
    print("\n== 4. The games a seed did not reach: when its last improvement came ==")
    missed = {seed: [r for r in rows if r[seed]["reach"] is None] for seed in SEEDS}
    for seed in SEEDS:
        ms = missed[seed]
        print(f"  seed {seed}: missed {len(ms)} of {len(rows)} games: {[r['n'] for r in ms]}")
        if not ms:
            continue
        lasts = sorted(r[seed]["last"] for r in ms)
        early = [r for r in ms if r[seed]["last"] <= EARLY]
        print(f"    last improvement round, sorted: {lasts}")
        print(f"    by round {EARLY}: {len(early)} of {len(ms)} (never improved at all: "
              f"{sum(1 for r in ms if r[seed]['last'] == 0)}); by round 64: {sum(1 for x in lasts if x <= 64)}; "
              f"after round 128: {sum(1 for x in lasts if x > 128)}")
        print(f"    final shortfall median {median([r[seed]['final'] for r in ms])}, maximum "
              f"{max(r[seed]['final'] for r in ms)}; the start's median {median([r[seed]['start_short'] for r in ms])}")
        for r in ms:
            print(f"      {r['n']}: start short {r[seed]['start_short']} (the run's start {r['short0']}), last "
                  f"improvement round {r[seed]['last']}, final short {r[seed]['final']}")
    for seed in SEEDS:
        reached = [r for r in rows if r[seed]["reach"] is not None and r[seed]["start_short"] > 0]
        rr = sorted(r[seed]["reach"] for r in reached)
        print(f"  seed {seed}: the {len(reached)} games short at the start and reached took rounds {rr}")
        print(f"    median {median(rr)}; after round 16: {sum(1 for x in rr if x > 16)}; after round 64: "
              f"{sum(1 for x in rr if x > 64)}")
    print("\n== 5. One seed on the games the other missed ==")
    for a, b in ((1, 2), (2, 1)):
        ms = missed[a]
        got = [r for r in ms if r[b]["reach"] is not None]
        print(f"  seed {b} on the {len(ms)} games seed {a} missed: reached {len(got)}: "
              f"{[(r['n'], r[b]['reach']) for r in got]}")
    both = [r for r in rows if r[1]["reach"] is None and r[2]["reach"] is None]
    print(f"  missed by both: {len(both)}: {[r['n'] for r in both]}")
    for r in both:
        print(f"    {r['n']}: start short {r[1]['start_short']}; final short seed 1 {r[1]['final']}, seed 2 "
              f"{r[2]['final']}; last improvement rounds {r[1]['last']} and {r[2]['last']}")
    same = sum(1 for r in both if r[1]["final"] == r[2]["final"])
    print(f"  of the {len(both)}, the two seeds end at the same score in {same}; never improved by either seed: "
          f"{sum(1 for r in both if r[1]['last'] == 0 and r[2]['last'] == 0)}; ending within 20 points: "
          f"{sum(1 for r in both if r[1]['final'] <= 20)}")
    shorts = [r for r in rows if r[1]["start_short"] > 0]
    print(f"  among the {len(shorts)} games short at the start, {len(both)} are missed by both seeds "
          f"({pct(len(both), len(shorts))})")
    print(f"  the start's shortfall (points), median: both-missed {median([r[1]['start_short'] for r in both])}, "
          f"the others short at the start {median([r[1]['start_short'] for r in shorts if r not in both])}")
    print(f"  n of the both-missed: {[r['n'] for r in both]}; the others short at the start have n from "
          f"{min(r['n'] for r in shorts if r not in both)} to {max(r['n'] for r in shorts if r not in both)}")
    return both


def old_finder(rows, sample):
    """Section 5b: what found the known score in the run of 2026-11-01, for the games the seeds missed."""
    print("\n== 5b. The same games in the run of 2026-11-01 ==")
    by_n = {g["n"]: g for g in sample}
    print("  source = what held the best score in that run (finder: the finder on one thread beside the search; "
          "tree_before_finder: the search, before the finder started; tree: the search, with no finder or the finder "
          "short); found = the finder's seconds on its own clock when it reached its best")
    print(f"  {'n':>5} {'source':>18} {'finder best/opt':>16} {'found s':>8} {'finder s':>8}")
    for r in rows:
        if r[1]["reach"] is None and r[2]["reach"] is None:
            g = by_n[r["n"]]
            f = g["finder"]
            print(f"  {r['n']:>5} {g['source']:>18} {f['best']}/{g['opt']:>6} {f['found_seconds']:>8.1f} "
                  f"{f['seconds']:>8.1f}")
    print(f"\n  by the source in the run of 2026-11-01 (games: held at the start / reached by 256 rounds by the better "
          f"seed / missed by both)")
    for source in ("finder", "tree_before_finder", "tree"):
        rs = [r for r in rows if by_n[r["n"]]["source"] == source]
        start = sum(1 for r in rs if r[1]["start_short"] == 0)
        reached = sum(1 for r in rs if r[1]["reach"] is not None or r[2]["reach"] is not None)
        print(f"  {source:>18}: {len(rs):>3} games, {start:>3} held at the start, {reached:>3} reached, "
              f"{len(rs) - reached:>3} missed")
    found = [(by_n[r["n"]]["finder"]["found_seconds"], r) for r in rows if by_n[r["n"]]["source"] == "finder"]
    quick = [x for x in found if x[0] <= 10]
    slow = [x for x in found if x[0] > 10]
    for label, group in (("found by the finder within 10 s", quick), ("found by the finder after 10 s", slow)):
        missed = sum(1 for _, r in group if r[1]["reach"] is None and r[2]["reach"] is None)
        print(f"  {label}: {len(group)} games, {missed} missed by both seeds")


def line_fit(xs, ys):
    """Least squares of y on x: (intercept, slope, correlation)."""
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)
    return mean_y - slope * mean_x, slope, statistics.correlation(xs, ys)


def costs(rows):
    """Section 6: the cost of a round, of a neighborhood and of the start against n."""
    print("\n== 6. Cost: seconds per round, steps per neighborhood and the start's seconds against n ==")
    print("  4 threads at nice 19 on a machine whose other threads run the prover at idle priority; wall seconds.")
    print(f"  seconds per round = (seconds - start_seconds) / rounds, over the lines of at least {MANY} rounds, "
          "so that what the line spends besides the rounds weighs little")
    zero = [d["seconds"] - d["start_seconds"] for r in rows for d in (r[1], r[2]) if d["rounds"] == 0]
    print(f"  what a line spends after the start with no round (the replay and the line): median "
          f"{median(zero):.3f} s, maximum {max(zero):.3f} s, over {len(zero)} lines")
    print(f"  {'band':>11} {'lines':>5} | {'s/round median':>14} {'min':>6} {'max':>6} | "
          f"{'steps/nb med':>12} {'min':>6} {'max':>6} | {'ms/step med':>11} | "
          f"{'start s med':>11} {'min':>6} {'max':>6}")
    whole = (BANDS[0][0], BANDS[-1][1])
    for band in BANDS + [whole]:
        spr, spn, mss, sts = [], [], [], []
        for r in rows:
            if not band[0] <= r["n"] <= band[1]:
                continue
            sts.append(statistics.fmean(r[seed]["start_seconds"] for seed in SEEDS))
            for seed in SEEDS:
                d = r[seed]
                if d["rounds"] >= MANY:
                    spr.append((d["seconds"] - d["start_seconds"]) / d["rounds"])
                    spn.append(d["steps_per_nb"])
                    mss.append(1000 * spr[-1] * THREADS / NEIGHBORHOODS / d["steps_per_nb"])
        print(f"  {band[0]:>5}-{band[1]:<5} {len(spr):>5} | {median(spr):>14.3f} {min(spr):>6.3f} {max(spr):>6.3f} | "
              f"{median(spn):>12.1f} {min(spn):>6.1f} {max(spn):>6.1f} | {median(mss):>11.2f} | {median(sts):>11.2f} "
              f"{min(sts):>6.2f} {max(sts):>6.2f}")
    spr, spn, tms = [], [], []
    for r in rows:
        for seed in SEEDS:
            d = r[seed]
            if d["rounds"] >= MANY:
                spr.append((d["seconds"] - d["start_seconds"]) / d["rounds"])
                spn.append(d["steps_per_nb"])
                tms.append(1000 * spr[-1] * THREADS / NEIGHBORHOODS)
    low, high = BANDS[0][0], BANDS[-1][1]
    print(f"  over the {len(spn)} lines: steps per neighborhood {min(spn):.1f}-{max(spn):.1f} (median "
          f"{median(spn):.1f}), against a limit of {UNIT_LIMIT:,}")
    a, b, c = line_fit(spn, tms)
    typical = a + b * median(spn)
    print(f"  thread-milliseconds a neighborhood on its steps: {a:.1f} + {b:.2f} x steps (correlation {c:.2f}); at the "
          f"median {median(spn):.1f} steps, the part that does not depend on the steps is {100 * a / typical:.0f}% of "
          f"{typical:.1f} ms")
    print(f"  (wall time x {THREADS} threads / {NEIGHBORHOODS} neighborhoods, so it includes the threads' waits at the "
          "end of a round, and the other work that shares the core)")
    mean_start = statistics.fmean(statistics.fmean(r[seed]["start_seconds"] for seed in SEEDS) for r in rows)
    mean_round = statistics.fmean(spr)
    print(f"  the cost of a level for a game, with the sample's mean start {mean_start:.1f} s and mean round "
          f"{mean_round:.3f} s on {THREADS} threads, and for the {SEARCHED} searched games of {low}-{high} in "
          "thread-hours (the run does not stop at the known score):")
    print(f"  {'effort':>6} {'rounds':>6} | {'seconds':>8} {'thread-s':>8} | {'568 games, thread-h':>19}")
    for effort, rounds in LEVELS:
        seconds = mean_start + rounds * mean_round
        print(f"  {effort:>6} {rounds:>6} | {seconds:>8.1f} {seconds * THREADS:>8.0f} | "
              f"{SEARCHED * seconds * THREADS / 3600:>19.1f}")
    full = [d["seconds"] for r in rows for d in (r[1], r[2]) if d["rounds"] == ROUNDS]
    print(f"  the {len(full)} lines that ran all {ROUNDS} rounds took {median(full):.1f} s at the median "
          f"({min(full):.1f} to {max(full):.1f})")
    total = {seed: sum(r[seed]["seconds"] for r in rows) for seed in SEEDS}
    print(f"  total seconds of the lines: seed 1 {total[1]:.0f} ({total[1] / 3600:.2f} h), seed 2 {total[2]:.0f} "
          f"({total[2] / 3600:.2f} h)")


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    sample, lines = load(directory)
    print(f"{len(sample)} games, n {sample[0]['n']} to {sample[-1]['n']}")
    failures = check_lines(sample, lines)
    rows = per_game_rows(sample, lines)
    shortfall_tables(sample, lines, rows)
    curve_rows = print_curve(rows)
    estimate(curve_rows, len(rows))
    stalls(rows)
    old_finder(rows, sample)
    costs(rows)
    print(f"\nchecks failed: {failures}")


if __name__ == "__main__":
    main()
