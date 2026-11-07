#!/usr/bin/env python3
"""Study E2 of the unsound mode: checks the lines of the chains and of the thread runs, prints every number of the
entry, and writes the chart.

    nice -n 19 python3 -I analyze.py [--results optimal.jsonl.gz] [--runs DIR] [--threads DIR] [--race DIR]
        [--continue DIR] [--chart FILE] [--partial] > out.txt

`--results` is the proven results file of the main repository (`results/optimal.jsonl.gz`); by default the script looks
for it four folders above its own, where the notebook's checkout at `solver/notebook/` of that repository puts it.
`--runs` (default: `runs/` beside the script) holds the lines of Part 1, `eE-LO.jsonl.gz` for effort E and the segment
that starts at LO, and `e4pc-LO.jsonl.gz` for effort 4 with `--past-ceiling`; `--threads` (default: `threads/`) holds
the lines of Part 2, `threadsN-T.jsonl.gz`; `--continue` (default: `continue/`) holds the lines of Part 1b,
`cont-eE.jsonl.gz`.  `--race` (default: the folder of the entry of race R1, beside this one) holds R1's lines
`k25w4-*.jsonl` of its hard games, of which the script takes those of 4561-5060.  Any file may be `.jsonl` as well as
`.jsonl.gz`.  `--partial` accepts runs that are not finished (to look at a study that is running); without it an
unfinished run is a failed check.  The script changes nothing, except that it writes the chart; everything it prints
is a number of the entry.
"""

import argparse
import glob
import gzip
import json
import math
import os
import statistics
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = "a2a1a2e"
RACE_ENTRY = "a-share-of-tilted-neighborhoods-2026-11"
RACE_LINES = "k25w4-*.jsonl"
SEGMENTS = [(4561, 4660), (4661, 4760), (4761, 4860), (4861, 4960), (4961, 5060)]
LEVELS = range(8)
PAST_CEILING_EFFORT = 4
THREAD_COUNTS = (4, 8, 16, 32, 64)
PART2_GAMES = (4752, 4864, 5016)
PART2_EFFORT = 5
NEIGHBORHOOD_WORK = 32
OPTIONS = {"fix": [0.7, 0.9], "tilt": 25, "back": 8, "widen": 4, "seed": 1}
PROVEN_METHODS = ("search", "start", "prime", "repeat")
LINE_METHODS = ("search", "prime", "repeat", "trivial")
IGNORED_IN_COMPARISON = ("seconds", "start_seconds", "threads", "build")


def budget_of(effort):
    """The work a level of effort runs its rounds until."""
    return 0 if effort == 0 else 65536 << (effort - 1)


def threads_of(effort):
    """The threads of Part 1's runs: 4, and 8 at effort 7."""
    return 8 if effort == 7 else 4


def pct(part, whole):
    """A share, in percent, to one decimal."""
    return f"{100 * part / whole:.1f}%" if whole else "-"


def cell(part, whole):
    """A count and its share."""
    return f"{part} ({pct(part, whole)})"


def percentile(values, q):
    """The q quantile of values, by linear interpolation between the closest ranks."""
    values = sorted(values)
    if not values:
        return float("nan")
    at = q * (len(values) - 1)
    low, high = math.floor(at), math.ceil(at)
    return values[low] + (values[high] - values[low]) * (at - low)


def median(values):
    return percentile(values, 0.5)


# ---------------------------------------------------------------------------------------------------------------------
# Reading


def find(directory, name):
    """The path of the file `name` (without its extension) in directory, `.jsonl.gz` or `.jsonl`, or None."""
    for extension in (".jsonl.gz", ".jsonl"):
        path = os.path.join(directory, name + extension)
        if os.path.exists(path):
            return path
    return None


def read_lines(path):
    """The lines of a JSON lines file, gzipped or not."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_race(directory):
    """The lines of race R1's arm `--tilt 25 --back 8 --widen 4` for the games of 4561-5060, {n: line}: its entry holds
    them in six files (`k25w4-0.jsonl` to `k25w4-5.jsonl`) for the 251 hard games of 3441-5060."""
    race = {}
    for path in sorted(glob.glob(os.path.join(directory, RACE_LINES))):
        for d in read_lines(path):
            if SEGMENTS[0][0] <= d["n"] <= SEGMENTS[-1][1]:
                race[d["n"]] = d
    return race


def read_results(path):
    """What the proven results file says of each game: its score, its method, and the seconds and times of its run."""
    table = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            d = json.loads(line)
            table[d["n"]] = {
                "score": d["score"], "method": d["method"], "proof": d["proof"], "seconds": d["seconds"]["total"],
                "cpu": d["seconds"]["cpu"], "started": d["started"], "finished": d["finished"],
                "ceiling": d["n"] + d["prev"]["score"] if d["prev"] else None,
            }
    return table


def annotate(lines, opt):
    """Adds to the lines of a run, in the order of n, the proven score `opt`, the `short` of the score, whether the game
    before it in the run was short (`prev_short`), and the `kind` of the game: clean (at opt(n) after a game at
    opt(n - 1)), recovered (at opt(n) after a short game), own (short after a game at opt(n - 1)) or handed (short after
    a short game)."""
    before = 0
    for d in lines:
        d["opt"] = opt[d["n"]]["score"]
        d["short"] = d["opt"] - d["score"]
        d["prev_short"] = before
        if d["short"] == 0:
            d["kind"] = "clean" if before == 0 else "recovered"
        else:
            d["kind"] = "own" if before == 0 else "handed"
        before = d["short"]
    return lines


def read_runs(directory, opt, partial):
    """Part 1's runs: {(effort, past_ceiling): {segment lo: [lines]}}, each line annotated (`annotate`) and given its
    `segment`."""
    runs = {}
    for effort in LEVELS:
        for past in (False, True):
            if past and effort != PAST_CEILING_EFFORT:
                continue
            for lo, _ in SEGMENTS:
                path = find(directory, f"e{effort}{'pc' if past else ''}-{lo}")
                if path is None:
                    continue
                lines = annotate(sorted(read_lines(path), key=lambda d: d["n"]), opt)
                for d in lines:
                    d["segment"] = lo
                runs.setdefault((effort, past), {})[lo] = lines
    if not partial:
        for past in (False, True):
            for effort in LEVELS:
                if not past or effort == PAST_CEILING_EFFORT:
                    for lo, _ in SEGMENTS:
                        assert lo in runs.get((effort, past), {}), f"run missing: effort {effort}, segment {lo}"
    return runs


def games(runs, effort, past=False):
    """All the lines of a level, in the order of n."""
    return sorted((d for lines in runs.get((effort, past), {}).values() for d in lines), key=lambda d: d["n"])


# ---------------------------------------------------------------------------------------------------------------------
# The checks


class Checks:
    """Counts the lines checked and collects the failures."""

    def __init__(self):
        self.lines = 0
        self.failures = []

    def expect(self, ok, text):
        if not ok:
            self.failures.append(text)


def check_runs(runs, opt, partial, checks):
    """Every line of Part 1 against the rules of the study and of the mode."""
    for (effort, past), by_segment in sorted(runs.items()):
        for lo, hi in SEGMENTS:
            lines = by_segment.get(lo)
            name = f"e{effort}{'pc' if past else ''}-{lo}"
            if lines is None:
                continue
            expected = list(range(lo, hi + 1))
            if not partial:
                checks.expect([d["n"] for d in lines] == expected, f"{name}: the games are not {lo}-{hi} once each")
            previous = None
            for i, d in enumerate(lines):
                checks.lines += 1
                n = d["n"]
                where = f"{name} game {n}"
                checks.expect(d.get("unsound") is True, f"{where}: not marked unsound")
                checks.expect(d["build"]["commit"].startswith(BUILD) and d["build"]["dirty"] is False,
                              f"{where}: build {d['build']}")
                checks.expect(d["effort"] == effort and d["budget"] == budget_of(effort),
                              f"{where}: effort {d['effort']} budget {d['budget']}")
                checks.expect(all(d[k] == v for k, v in OPTIONS.items()), f"{where}: options differ")
                checks.expect(d["threads"] == threads_of(effort), f"{where}: threads {d['threads']}")
                checks.expect(not d["from_known"] and d["stop_at_known"] is None, f"{where}: measuring option set")
                checks.expect(d["score"] <= d["opt"], f"{where}: score {d['score']} above the table's {d['opt']}")
                prev = d["prev"]
                checks.expect(prev is not None and prev["n"] == n - 1, f"{where}: prev {prev}")
                if prev is not None:
                    want = "table" if i == 0 else "run"
                    checks.expect(prev["source"] == want, f"{where}: prev.source {prev['source']}, want {want}")
                    want_score = opt[n - 1]["score"] if i == 0 else previous["score"]
                    checks.expect(prev["score"] == want_score, f"{where}: prev.score {prev['score']} != {want_score}")
                    checks.expect(prev["short_by"] == max(0, d["score"] - (n + prev["score"])) or d["method"] in (
                        "prime", "repeat", "trivial"), f"{where}: short_by {prev['short_by']}")
                checks.expect(d["work"] == d["steps"] + NEIGHBORHOOD_WORK * d["neighborhoods"], f"{where}: work")
                scores = [x["score"] for x in d["improvements"]]
                checks.expect(scores == sorted(set(scores)) and (not scores or scores[-1] == d["score"]),
                              f"{where}: improvements {scores} to score {d['score']}")
                if d["method"] == "search":
                    checks.expect(d["start"] is not None and d["score"] >= d["start"], f"{where}: start")
                    if not past and prev is not None:
                        checks.expect(d["ceiling"] == n + prev["score"], f"{where}: ceiling {d['ceiling']}")
                        checks.expect(d["at_ceiling"] == (d["score"] >= d["ceiling"]), f"{where}: at_ceiling")
                    checks.expect(past or d["ceiling"] is not None, f"{where}: no ceiling")
                    if past:
                        checks.expect(d["ceiling"] is None and d["at_ceiling"] is False, f"{where}: ceiling kept")
                    if effort >= 1 and d["work"] < d["budget"]:
                        checks.expect(d["at_ceiling"], f"{where}: stopped at work {d['work']} short of the budget")
                    if effort >= 1 and not d["at_ceiling"]:
                        checks.expect(d["work"] >= d["budget"], f"{where}: work {d['work']} below the budget")
                    if d["at_ceiling"] and d["prev_short"] == 0:
                        checks.expect(d["short"] == 0, f"{where}: at the ceiling of an optimal game, short")
                else:
                    checks.expect(d["rounds"] == 0 and d["start"] is None, f"{where}: {d['method']} with rounds")
                    checks.expect(d["method"] != "repeat" or d["repeats"] is not None, f"{where}: repeat of none")
                previous = d


def same_line(a, b, limit=None):
    """Whether two lines of the same game agree but for their seconds, threads and build.  With a limit, only the
    first `limit` improvements are compared."""
    keys = set(a) | set(b)
    for k in keys:
        if k in IGNORED_IN_COMPARISON:
            continue
        if k == "improvements":
            xs = [{j: v for j, v in x.items() if j != "seconds"} for x in a[k]]
            ys = [{j: v for j, v in x.items() if j != "seconds"} for x in b[k]]
            if limit is not None:
                xs, ys = xs[:limit], ys[:limit]
            if xs != ys:
                return False
        elif a.get(k) != b.get(k):
            return False
    return True


# ---------------------------------------------------------------------------------------------------------------------
# 1. The share of optimal scores and the shortfalls


def level_label(effort, past=False):
    return f"{effort}{' past the ceiling' if past else ''}"


def share_tables(runs, opt):
    """Item 1: the share of the 500 games at opt(n), by segment and by method, for each level."""
    print("\n== 1a. Games with the proven score, by level ==")
    header = "  effort |  all 500        | " + " | ".join(f"{lo}-{hi}" for lo, hi in SEGMENTS)
    print(header)
    keys = [(e, False) for e in LEVELS] + [(PAST_CEILING_EFFORT, True)]
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        by_segment = []
        for lo, _ in SEGMENTS:
            part = [d for d in gs if d["segment"] == lo]
            by_segment.append(f"{sum(d['short'] == 0 for d in part):>3}/{len(part)}")
        print(f"  {level_label(effort, past):>6} | {cell(sum(d['short'] == 0 for d in gs), len(gs)):>15} | "
              + " | ".join(f"{c:>8}" for c in by_segment))
    print("\n== 1b. Games with the proven score, by the method of the proven run (counts of the 500) ==")
    gs = games(runs, 0)
    if gs:
        print("  proven method: " + ", ".join(
            f"{m} {sum(opt[d['n']]['method'] == m for d in gs)}" for m in PROVEN_METHODS))
    print(f"  {'effort':>6} | " + " | ".join(f"{m:>16}" for m in PROVEN_METHODS))
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        cells = []
        for m in PROVEN_METHODS:
            part = [d for d in gs if opt[d["n"]]["method"] == m]
            cells.append(cell(sum(d["short"] == 0 for d in part), len(part)))
        print(f"  {level_label(effort, past):>6} | " + " | ".join(f"{c:>16}" for c in cells))
    print("\n== 1c. Games with the proven score, by the method of the unsound line (counts of the 500) ==")
    print(f"  {'effort':>6} | " + " | ".join(f"{m:>16}" for m in LINE_METHODS))
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        cells = []
        for m in LINE_METHODS:
            part = [d for d in gs if d["method"] == m]
            cells.append(cell(sum(d["short"] == 0 for d in part), len(part)))
        print(f"  {level_label(effort, past):>6} | " + " | ".join(f"{c:>16}" for c in cells))
    print("\n== 1d. The proven method of the games that a line of the run played otherwise (proven -> unsound line) ==")
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        moved = {}
        for d in gs:
            a, b = opt[d["n"]]["method"], d["method"]
            if (a, b) not in (("search", "search"), ("start", "search"), ("prime", "prime"), ("repeat", "repeat")):
                moved.setdefault((a, b), []).append(d["n"])
        print(f"  effort {level_label(effort, past)}: {dict(sorted(moved.items()))}")


def shortfall_tables(runs):
    """Item 1: the shortfalls, own and handed on, and how they run in a chain."""
    print("\n== 1e. The shortfalls (opt(n) - score) of the games below the proven score ==")
    print(f"  {'effort':>6} | {'short':>5} | {'own':>5} {'handed':>6} | size: median / 90th / max | "
          f"own: median / max | handed: median / max | sum")
    keys = [(e, False) for e in LEVELS] + [(PAST_CEILING_EFFORT, True)]
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        short = [d for d in gs if d["short"] > 0]
        own = [d["short"] for d in short if d["kind"] == "own"]
        handed = [d["short"] for d in short if d["kind"] == "handed"]
        sizes = [d["short"] for d in short]
        print(f"  {level_label(effort, past):>6} | {len(short):>5} | {len(own):>5} {len(handed):>6} | "
              f"{median(sizes):>6.0f} / {percentile(sizes, 0.9):>5.0f} / {max(sizes, default=0):>6} | "
              f"{median(own):>5.0f} / {max(own, default=0):>5} | {median(handed):>5.0f} / {max(handed, default=0):>5}"
              f" | {sum(sizes)}")
    sets = {key: {d["n"] for d in games(runs, *key) if d["short"] > 0} for key in keys if games(runs, *key)}
    if (4, False) in sets and (5, False) in sets and (6, False) in sets and (4, True) in sets:
        print(f"\n  the games below the proven score at effort 4, 5, 6 and 4 past the ceiling are the same "
              f"{len(sets[(4, False)])}: {sets[(4, False)] == sets[(5, False)] == sets[(6, False)] == sets[(4, True)]}"
              f"; at effort 7: {sorted(sets[(7, False)])}")
    print("\n== 1f. What a handed-on shortfall does (the game before was short too): by the method of the line ==")
    print(f"  {'effort':>6} | method  | handed | same size | smaller | larger | recovered (games after a short game)")
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        for m in ("search", "repeat", "prime"):
            after = [d for d in gs if d["prev_short"] > 0 and d["method"] == m]
            if not after:
                continue
            handed = [d for d in after if d["short"] > 0]
            print(f"  {level_label(effort, past):>6} | {m:<7} | {len(handed):>6} | "
                  f"{sum(d['short'] == d['prev_short'] for d in handed):>9} | "
                  f"{sum(0 < d['short'] < d['prev_short'] for d in handed):>7} | "
                  f"{sum(d['short'] > d['prev_short'] for d in handed):>6} | "
                  f"{len(after) - len(handed):>4} of {len(after)}")


def streaks_of(lines):
    """The streaks of a run: maximal stretches of games below the proven score.  Each has its games and the game
    that ended it (None: the end of the segment)."""
    out, current = [], []
    for d in lines:
        if d["short"] > 0:
            current.append(d)
        elif current:
            out.append((current, d))
            current = []
    if current:
        out.append((current, None))
    return out


def streak_tables(runs):
    """Item 1: how long a shortfall lasts in a chain, and what ended it."""
    print("\n== 1g. Streaks: games in a row below the proven score, and what ended each ==")
    print(f"  {'effort':>6} | streaks | games | length: mean / median / 90th / max | of 1 | 2-3 | 4-9 | 10+ | "
          f"ended by: search / repeat / prime / segment end | started by: search / repeat / prime")
    keys = [(e, False) for e in LEVELS] + [(PAST_CEILING_EFFORT, True)]
    for effort, past in keys:
        by_segment = runs.get((effort, past), {})
        if not by_segment:
            continue
        streaks = [s for lines in by_segment.values() for s in streaks_of(lines)]
        if not streaks:
            print(f"  {level_label(effort, past):>6} | none")
            continue
        lengths = [len(g) for g, _ in streaks]
        ends = [e["method"] if e else "end" for _, e in streaks]
        starts = [g[0]["method"] for g, _ in streaks]
        print(f"  {level_label(effort, past):>6} | {len(streaks):>7} | {sum(lengths):>5} | "
              f"{statistics.mean(lengths):>5.1f} / {median(lengths):>4.1f} / {percentile(lengths, 0.9):>4.1f} / "
              f"{max(lengths):>3} | {sum(x == 1 for x in lengths):>4} | {sum(2 <= x <= 3 for x in lengths):>3} | "
              f"{sum(4 <= x <= 9 for x in lengths):>4} | {sum(x >= 10 for x in lengths):>3} | "
              f"{ends.count('search')} / {ends.count('repeat')} / {ends.count('prime')} / {ends.count('end')} | "
              f"{starts.count('search')} / {starts.count('repeat')} / {starts.count('prime')}")
    print("\n== 1h. The longest streaks of each level (first game, games, size at the start -> at the end, "
          "ended by) ==")
    for effort in LEVELS:
        streaks = [s for lines in runs.get((effort, False), {}).values() for s in streaks_of(lines)]
        longest = sorted(streaks, key=lambda s: -len(s[0]))[:4]
        print(f"  effort {effort}: " + "; ".join(
            f"{g[0]['n']} x{len(g)} ({g[0]['short']} -> {g[-1]['short']}, "
            f"{e['method'] + ' ' + str(e['n']) if e else 'end'})" for g, e in longest))


# ---------------------------------------------------------------------------------------------------------------------
# 2. The run's ceiling


def ceiling_tables(runs, opt):
    """Item 2: the games that stopped at the run's ceiling, and effort 4 with and without the stop."""
    print("\n== 2a. Searched games and the run's ceiling, by level ==")
    print(f"  {'effort':>6} | searched | at the ceiling | of those below opt(n) | not at it, below opt(n) | "
          f"not at it, at opt(n) (ran the whole budget) | prev.short_by > 0")
    for effort in LEVELS:
        gs = [d for d in games(runs, effort) if d["method"] == "search"]
        if not gs:
            continue
        at = [d for d in gs if d["at_ceiling"]]
        print(f"  {effort:>6} | {len(gs):>8} | {len(at):>14} | {sum(d['short'] > 0 for d in at):>21} | "
              f"{sum(d['short'] > 0 for d in gs if not d['at_ceiling']):>23} | "
              f"{sum(d['short'] == 0 for d in gs if not d['at_ceiling']):>43} | "
              f"{sum(d['prev']['short_by'] > 0 for d in gs):>3}")
    for effort in LEVELS:
        listed = [d["n"] for d in games(runs, effort) if d["method"] == "search" and d["at_ceiling"] and d["short"] > 0]
        if effort >= 1:
            print(f"  effort {effort}: stopped at the ceiling below opt(n): {listed}")
    print("\n== 2b. Effort 4 with the stop at the run's ceiling and with --past-ceiling ==")
    stop, past = games(runs, PAST_CEILING_EFFORT), games(runs, PAST_CEILING_EFFORT, True)
    if not stop or not past:
        return
    print(f"  {'':>14} | at opt(n)  | searched | seconds of the 500 games: sum / per 100 | work of searched games: sum")
    for name, gs in (("stop (default)", stop), ("past ceiling", past)):
        searched = [d for d in gs if d["method"] == "search"]
        seconds = sum(d["seconds"] for d in gs)
        print(f"  {name:>14} | {cell(sum(d['short'] == 0 for d in gs), len(gs)):>10} | {len(searched):>8} | "
              f"{seconds:>8.0f} s / {seconds / len(gs) * 100 / 3600:.2f} h | {sum(d['work'] for d in searched):,}")
    by_n = {d["n"]: d for d in stop}
    gained = [d["n"] for d in past if d["short"] == 0 and by_n[d["n"]]["short"] > 0]
    lost = [d["n"] for d in past if d["short"] > 0 and by_n[d["n"]]["short"] == 0]
    print(f"  past the ceiling reaches opt(n) in {len(gained)} games the stop falls short in, and falls short in "
          f"{len(lost)} games the stop reaches")
    passing = [d for d in past if d["method"] == "search" and d["prev"]["short_by"] > 0]
    print(f"  past the ceiling, {len(passing)} games passed n + score(n - 1), proving the line before short "
          f"(prev.short_by 1 .. {max((d['prev']['short_by'] for d in passing), default=0)}): "
          f"{[(d['n'], d['prev']['short_by']) for d in passing][:12]}")
    ratio = [d["seconds"] / by_n[d["n"]]["seconds"] for d in past
             if d["method"] == "search" and by_n[d["n"]]["seconds"] > 5]
    print(f"  seconds of a searched game, past the ceiling over the stop: median {median(ratio):.2f} "
          f"(90th percentile {percentile(ratio, 0.9):.2f})")
    for lo, hi in SEGMENTS:
        a = sum(d["seconds"] for d in stop if d["segment"] == lo)
        b = sum(d["seconds"] for d in past if d["segment"] == lo)
        sa = sum(d["short"] == 0 for d in stop if d["segment"] == lo)
        sb = sum(d["short"] == 0 for d in past if d["segment"] == lo)
        print(f"  segment {lo}: stop {a / 3600:.2f} h, {sa} at opt(n); past the ceiling {b / 3600:.2f} h, "
              f"{sb} at opt(n)")


def read_continuation(directory, opt, checks):
    """Part 1b: the runs of 4861-4960 played on into 4961-5060, {effort: [200 lines of 4861-5060]}."""
    out = {}
    if directory is None or not os.path.isdir(directory):
        return out
    for effort in LEVELS:
        path = find(directory, f"cont-e{effort}")
        if path is None:
            continue
        lines = annotate(sorted(read_lines(path), key=lambda d: d["n"]), opt)
        if [d["n"] for d in lines] != list(range(4861, 5061)):
            print(f"  continuation at effort {effort}: {len(lines)} games, not 200 (unfinished)")
            continue
        for i, d in enumerate(lines):
            checks.lines += 1
            where = f"cont-e{effort} game {d['n']}"
            checks.expect(d["unsound"] is True and d["effort"] == effort and all(d[k] == v for k, v in OPTIONS.items()),
                          f"{where}: options")
            checks.expect(d["build"]["commit"].startswith(BUILD) and not d["build"]["dirty"], f"{where}: build")
            checks.expect(d["score"] <= d["opt"], f"{where}: score above the table's")
            checks.expect(d["prev"]["n"] == d["n"] - 1 and d["prev"]["score"] == (
                lines[i - 1]["score"] if i else opt[4860]["score"]), f"{where}: prev")
            want = "table" if i == 0 else "results" if d["n"] == 4961 else "run"
            checks.expect(d["prev"]["source"] == want, f"{where}: prev.source {d['prev']['source']}, want {want}")
        out[effort] = lines
    return out


def continuation_tables(runs, cont):
    """Part 1b: the streaks that reach the end of a segment, played on."""
    print("\n== 1i. The chain of 4861-4960 played on into 4961-5060 (the streak that reaches 4960 is not cut) ==")
    if not cont:
        print("  no continuation runs")
        return
    print(f"  {'effort':>6} | the streak that reaches 4960: first game, games, ended by | short in 4961-5060: "
          f"Part 1 -> continuation | at opt(n) of the 200 games: Part 1 -> continuation | streaks of 4961-5060 in the "
          f"continuation | games of 4961-5060 whose score differs from Part 1's")
    for effort, lines in sorted(cont.items()):
        first = {d["n"]: d for d in games(runs, effort)}
        before = sum(first[n]["short"] > 0 for n in range(4861, 4961))
        after_part1 = sum(first[n]["short"] > 0 for n in range(4961, 5061))
        after_cont = sum(d["short"] > 0 for d in lines if d["n"] >= 4961)
        reaching = [(g, e) for g, e in streaks_of(lines) if g[0]["n"] <= 4960 <= g[-1]["n"]]
        text = "; ".join(f"{g[0]['n']}, {len(g)} games, ended by "
                         f"{e['method'] + ' ' + str(e['n']) if e else 'the end of the range'}" for g, e in reaching)
        others = [f"{g[0]['n']} x{len(g)}" for g, e in streaks_of(lines) if g[0]["n"] >= 4961]
        different = sum(d["score"] != first[d["n"]]["score"] for d in lines if d["n"] >= 4961)
        print(f"  {effort:>6} | {text} | {after_part1} -> {after_cont} | {200 - before - after_part1} -> "
              f"{200 - before - after_cont} | {others} | {different}")
    for effort, lines in sorted(cont.items()):
        shown = [(d["n"], d["prev"]["short_by"]) for d in lines if d["n"] >= 4961 and d["prev"]["short_by"] > 0]
        shortcount = sum(d["short"] > 0 for d, after in zip(lines, lines[1:]) if d["n"] >= 4961)
        print(f"  effort {effort}: of the {shortcount} short games of 4961-5060 that have a game after, "
              f"{len(shown)} have a line after that shows them short (prev.short_by above 0) {shown}")


# ---------------------------------------------------------------------------------------------------------------------
# Part 2: the threads


def read_threads(directory):
    """Part 2's lines: {n: {threads: line}}, for every game that has a file `threadsN-T`."""
    out = {}
    if directory is None or not os.path.isdir(directory):
        return out
    for name in sorted(os.listdir(directory)):
        stem = name.split(".jsonl")[0]
        if name.startswith("threads") and ".jsonl" in name and stem[7:].replace("-", "").isdigit():
            n, t = map(int, stem[7:].split("-"))
            lines = read_lines(os.path.join(directory, name))
            if lines:
                out.setdefault(n, {})[t] = lines[-1]
    return out


def thread_tables(threads, runs, opt, checks):
    """Part 2: the lines agree across thread counts, and the seconds of the start and of the rounds.  Returns the
    speedups over 4 threads, {threads: (start, rounds)}, pooled over the games that ran on every thread count.  The
    games that ran on 4 threads alone calibrate the chain's seconds against an idle machine."""
    print("\n== P2. One game on more threads (effort 5, from the table's moves for n - 1, alone) ==")
    if not threads:
        print("  no thread runs")
        return {4: (1.0, 1.0)}, (1.0, 1.0)
    complete = [n for n, by_t in sorted(threads.items()) if all(t in by_t for t in THREAD_COUNTS)]
    for n, by_t in sorted(threads.items()):
        base = by_t.get(4)
        for t, d in sorted(by_t.items()):
            checks.lines += 1
            checks.expect(d["threads"] == t and d["effort"] == PART2_EFFORT and d["from_known"], f"threads{n}-{t}: run")
            checks.expect(d["build"]["commit"].startswith(BUILD) and not d["build"]["dirty"], f"threads{n}-{t}: build")
            checks.expect(all(d[k] == v for k, v in OPTIONS.items()), f"threads{n}-{t}: options")
            checks.expect(d["score"] <= opt[n]["score"], f"threads{n}-{t}: score above the table's")
            if base is not None and t != 4:
                checks.expect(same_line(base, d), f"threads{n}-{t}: the line differs from the line on 4 threads")
    print(f"  {'game':>5} {'threads':>7} | {'score':>8} {'work':>9} {'rounds':>6} | seconds: {'game':>7} {'start':>7} "
          f"{'rounds':>7} | speedup over 4 threads: the rounds / the start / the game")
    base_total = [0.0, 0.0, 0.0]
    for n in complete:
        base = threads[n][4]
        for t in THREAD_COUNTS:
            d = threads[n][t]
            rounds_s = d["seconds"] - d["start_seconds"]
            b_rounds = base["seconds"] - base["start_seconds"]
            print(f"  {n:>5} {t:>7} | {d['score']:>8} {d['work']:>9,} {d['rounds']:>6} | {d['seconds']:>16.1f} "
                  f"{d['start_seconds']:>7.1f} {rounds_s:>7.1f} | {b_rounds / rounds_s:>5.2f} / "
                  f"{base['start_seconds'] / d['start_seconds']:>5.2f} / {base['seconds'] / d['seconds']:>5.2f}")
        for i, v in enumerate((base["start_seconds"], base["seconds"] - base["start_seconds"], base["seconds"])):
            base_total[i] += v
    speedups = {4: (1.0, 1.0)}
    if complete:
        print(f"\n  pooled over the {len(complete)} games with every thread count ({complete}):")
        print(f"  {'threads':>7} | {'start s':>8} {'rounds s':>9} {'game s':>8} | speedup: start / rounds / game | "
              f"efficiency of the rounds (speedup over threads / 4)")
        for t in THREAD_COUNTS:
            s = sum(threads[n][t]["start_seconds"] for n in complete)
            g = sum(threads[n][t]["seconds"] for n in complete)
            r = g - s
            su = (base_total[0] / s, base_total[1] / r)
            speedups[t] = su
            print(f"  {t:>7} | {s:>8.1f} {r:>9.1f} {g:>8.1f} | {su[0]:>5.2f} / {su[1]:>5.2f} / "
                  f"{base_total[2] / g:>5.2f} | {su[1] / (t / 4):.2f}")
    return speedups, calibration(threads, runs)


def calibration(threads, runs):
    """The chain's seconds against the same game alone on 4 threads (the machine had 80 threads busy during most of
    the chain): the ratio of the seconds of the start, and of the seconds a unit of work of the rounds takes.  Returns
    the factors (start, rounds), the medians of the games' ratios, by which the chain's seconds exceed an idle
    machine's."""
    chain = {d["n"]: d for d in games(runs, PART2_EFFORT)}
    rows = []
    for n, by_t in sorted(threads.items()):
        alone, loaded = by_t.get(4), chain.get(n)
        if alone is None or loaded is None or loaded["method"] != "search" or alone["work"] < 100_000:
            continue
        a_rounds, c_rounds = alone["seconds"] - alone["start_seconds"], loaded["seconds"] - loaded["start_seconds"]
        rows.append({
            "n": n, "same": loaded["work"] == alone["work"] and loaded["score"] == alone["score"],
            "start": (alone["start_seconds"], loaded["start_seconds"]),
            "rate": (a_rounds / alone["work"] * 1e6, c_rounds / loaded["work"] * 1e6)})
    if not rows:
        return 1.0, 1.0
    print("\n  Load: each game alone on 4 threads against the chain's line of the same game at effort 5 (the chain "
          "ran with up to 80 threads busy)")
    print(f"  {'game':>5} | same line | start s: alone / chain | rounds, s per 10^6 work: alone / chain | chain over "
          f"alone: start / rounds")
    for r in rows:
        print(f"  {r['n']:>5} | {'yes' if r['same'] else 'no':>9} | {r['start'][0]:>6.1f} / {r['start'][1]:>5.1f} | "
              f"{r['rate'][0]:>14.1f} / {r['rate'][1]:>5.1f} | {r['start'][1] / r['start'][0]:>5.2f} / "
              f"{r['rate'][1] / r['rate'][0]:>5.2f}")
    start = [r["start"][1] / r["start"][0] for r in rows]
    rate = [r["rate"][1] / r["rate"][0] for r in rows]
    print(f"  {len(rows)} games: the chain over alone, start {median(start):.2f} "
          f"(range {min(start):.2f}-{max(start):.2f}), rounds {median(rate):.2f} "
          f"(range {min(rate):.2f}-{max(rate):.2f})")
    return median(start), median(rate)


def at_threads(d, measured, target, speedups, load=(1.0, 1.0)):
    """The seconds of a game on `target` threads, from its seconds on `measured` threads: a searched game's start
    and rounds scale by Part 2's speedups, any other game's seconds do not.  The `load` factors (start, rounds) divide
    the chain's seconds first, to give the seconds on an idle machine."""
    if d["method"] != "search":
        return d["seconds"]
    start, rounds = d["start_seconds"] / load[0], (d["seconds"] - d["start_seconds"]) / load[1]
    if measured == target or measured not in speedups or target not in speedups:
        return start + rounds
    return start * speedups[measured][0] / speedups[target][0] + rounds * speedups[measured][1] / speedups[target][1]


# ---------------------------------------------------------------------------------------------------------------------
# 3. Time


def proven_hours(opt):
    """The proven mode's hours for each segment of 100 games: the wall time from the first game's start to the last
    game's finish, and the sum of the games' own seconds (up to four games at once, on 88 threads), and the CPU
    hours."""
    def stamp(s):
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()

    out = {}
    for lo, hi in SEGMENTS:
        rows = [opt[n] for n in range(lo, hi + 1)]
        wall = max(stamp(r["finished"]) for r in rows) - min(stamp(r["started"]) for r in rows)
        out[lo] = {"wall": wall / 3600, "games": sum(r["seconds"] for r in rows) / 3600,
                   "cpu": sum(r["cpu"] for r in rows) / 3600}
    return out


def time_tables(runs, opt, speedups, load):
    """Item 3: the seconds of a game and the hours per 100 games for each level, on its threads and on others."""
    print("\n== 3a. Seconds of a game on the run's threads (4; 8 at effort 7), the 500 games of 4561-5060 ==")
    print(f"  {'effort':>6} | all 500 games: median / 90th / mean | searched: n, median / 90th | start s: sum | "
          f"rounds s: sum | hours per 100 games: mean (lowest - highest segment)")
    keys = [(e, False) for e in LEVELS] + [(PAST_CEILING_EFFORT, True)]
    for effort, past in keys:
        gs = games(runs, effort, past)
        if not gs:
            continue
        secs = [d["seconds"] for d in gs]
        searched = [d["seconds"] for d in gs if d["method"] == "search"]
        starts = sum(d["start_seconds"] for d in gs)
        total = sum(secs)
        seg = [sum(d["seconds"] for d in gs if d["segment"] == lo) / 3600 for lo, _ in SEGMENTS]
        print(f"  {level_label(effort, past):>6} | {median(secs):>6.1f} / {percentile(secs, 0.9):>6.1f} / "
              f"{statistics.mean(secs):>6.1f} | {len(searched):>3}, {median(searched):>6.1f} / "
              f"{percentile(searched, 0.9):>6.1f} | {starts:>7.0f} | {total - starts:>8.0f} | "
              f"{statistics.mean(seg):>5.2f} ({min(seg):.2f} - {max(seg):.2f})")
    print("\n== 3a2. The searched games: the start, the rounds, and the seconds a unit of work takes ==")
    print(f"  {'effort':>6} | searched | start s: median / 90th | rounds s: median / 90th | games with rounds (work >= "
          f"100k): n, median work, seconds per 10^6 work (pooled, median of games) | at the ceiling")
    for effort, past in keys:
        searched = [d for d in games(runs, effort, past) if d["method"] == "search"]
        if not searched:
            continue
        starts = [d["start_seconds"] for d in searched]
        rounds = [d["seconds"] - d["start_seconds"] for d in searched]
        worked = [d for d in searched if d["work"] >= 100_000]
        per = [(d["seconds"] - d["start_seconds"]) / d["work"] * 1e6 for d in worked]
        pooled = sum(d["seconds"] - d["start_seconds"] for d in worked) / max(1, sum(d["work"] for d in worked)) * 1e6
        print(f"  {level_label(effort, past):>6} | {len(searched):>8} | {median(starts):>6.1f} / "
              f"{percentile(starts, 0.9):>5.1f} | {median(rounds):>7.1f} / {percentile(rounds, 0.9):>6.1f} | "
              f"{len(worked):>3}, "
              f"{median([d['work'] for d in worked]) if worked else 0:>10,.0f}, {pooled:>6.1f}, "
              f"{median(per) if per else 0:>6.1f} | {sum(d['at_ceiling'] for d in searched)}")
    print("\n== 3b. Hours per 100 games by segment (the run's threads) ==")
    print(f"  {'effort':>6} | " + " | ".join(f"{lo}-{hi}" for lo, hi in SEGMENTS))
    for effort, past in keys:
        gs = games(runs, effort, past)
        if gs:
            print(f"  {level_label(effort, past):>6} | " + " | ".join(
                f"{sum(d['seconds'] for d in gs if d['segment'] == lo) / 3600:>9.2f}" for lo, _ in SEGMENTS))
    for name, factors in (("as measured in the chains, on a machine with 80 threads busy", (1.0, 1.0)),
                          (f"alone: the chains' seconds divided by the load factors {load[0]:.2f} (start) and "
                           f"{load[1]:.2f} (rounds)", load)):
        print(f"\n== 3c. The levels on other thread counts, {name}, by Part 2's speedups: hours per 100 games / "
              f"median seconds of a searched game ==")
        print(f"  {'effort':>6} | " + " | ".join(f"{t:>3} threads".rjust(16) for t in THREAD_COUNTS))
        for effort in LEVELS:
            gs = games(runs, effort)
            if not gs:
                continue
            cells = []
            for t in THREAD_COUNTS:
                if t not in speedups:
                    cells.append("-".rjust(16))
                    continue
                secs = [at_threads(d, threads_of(effort), t, speedups, factors) for d in gs]
                found = [x for x, d in zip(secs, gs) if d["method"] == "search"]
                cells.append(f"{sum(secs) / len(gs) * 100 / 3600:>6.2f} h {median(found):>5.1f}s".rjust(16))
            print(f"  {effort:>6} | " + " | ".join(cells))
    print("\n== 3d. The proven mode over the same stretch (88 threads, up to four games at once) ==")
    proven = proven_hours(opt)
    print(f"  {'segment':>9} | wall hours | sum of the games' hours | CPU hours | "
          f"methods: search / start / prime / repeat")
    for lo, hi in SEGMENTS:
        counts = [sum(opt[n]["method"] == m for n in range(lo, hi + 1)) for m in PROVEN_METHODS]
        print(f"  {lo}-{hi} | {proven[lo]['wall']:>10.2f} | {proven[lo]['games']:>23.2f} | {proven[lo]['cpu']:>9.1f} | "
              + " / ".join(map(str, counts)))
    wall = [proven[lo]["wall"] for lo, _ in SEGMENTS]
    games_h = [proven[lo]["games"] for lo, _ in SEGMENTS]
    cpu = [proven[lo]["cpu"] for lo, _ in SEGMENTS]
    print(f"  per 100 games, mean of the segments: wall {statistics.mean(wall):.2f} h, games "
          f"{statistics.mean(games_h):.2f} h, CPU {statistics.mean(cpu):.1f} h; median wall {median(wall):.2f} h; "
          f"total wall {sum(wall):.1f} h")
    seconds_search = [opt[n]["seconds"] for n in range(4561, 5061) if opt[n]["method"] == "search"]
    print(f"  the proven searched games (170 of 500): median {median(seconds_search):.0f} s, 90th percentile "
          f"{percentile(seconds_search, 0.9):.0f} s, in 88 threads")
    return proven


# ---------------------------------------------------------------------------------------------------------------------
# 5. The chain against the race


def reached_in_race(line, budget):
    """Whether the race's game held the known score within a budget of work (the lower bound: the round that crosses
    the budget would also run)."""
    s = line["stop_at_known"]
    if s["round"] is None:
        return False
    if s["round"] == 0:
        return True
    first = next(x for x in line["improvements"] if x["score"] >= s["known"])
    return first["work"] <= budget


def race_tables(runs, race, opt, checks):
    """Item 5: the hard games of the race among the 500, seeded with the proven game and in the chain."""
    print("\n== 5. The hard games of the race R1 among the 500, seeded with the proven game (race) and in the chain ==")
    hard = sorted(race)
    print(f"  hard games in 4561-5060: {len(hard)} (of 500; the other {500 - len(hard)} held the known score at the "
          f"start of the proven run of 2026-11-01 or needed no search)")
    for n in hard:
        checks.expect(race[n]["stop_at_known"]["known"] == opt[n]["score"], f"race game {n}: known != table")
        checks.expect(race[n]["build"]["commit"].startswith("8dc6500"), f"race game {n}: build")
    print(f"  {'effort':>6} | race: at the known score within the budget | chain: at opt(n) | both | race only | "
          f"chain only | neither | all 500: race estimate / chain")
    summary = {}
    for effort in LEVELS:
        gs = {d["n"]: d for d in games(runs, effort)}
        if not gs:
            continue
        got = {n: reached_in_race(race[n], budget_of(effort)) for n in hard if n in gs}
        chain = {n: gs[n]["short"] == 0 for n in hard if n in gs}
        both = sum(got[n] and chain[n] for n in got)
        race_only = [n for n in got if got[n] and not chain[n]]
        chain_only = [n for n in got if chain[n] and not got[n]]
        neither = sum(not got[n] and not chain[n] for n in got)
        total_chain = sum(d["short"] == 0 for d in gs.values())
        race_all = len(gs) - sum(not v for v in got.values())
        summary[effort] = (sum(got.values()), sum(chain.values()), race_all, total_chain, race_only, chain_only)
        print(f"  {effort:>6} | {cell(sum(got.values()), len(got)):>40} | {cell(sum(chain.values()), len(got)):>15} | "
              f"{both:>4} | {len(race_only):>9} | {len(chain_only):>10} | {neither:>7} | "
              f"{race_all}/{len(gs)} / {total_chain}/{len(gs)}")
    print("\n  The hard games the chain lost against the race (race reaches, chain falls short), with the state of the "
          "game before in the chain:")
    for effort in LEVELS:
        if effort not in summary:
            continue
        gs = {d["n"]: d for d in games(runs, effort)}
        race_only, chain_only = summary[effort][4], summary[effort][5]
        kinds = {}
        for n in race_only:
            kinds[gs[n]["kind"]] = kinds.get(gs[n]["kind"], 0) + 1
        gains = {}
        for n in chain_only:
            gains[gs[n]["kind"]] = gains.get(gs[n]["kind"], 0) + 1
        print(f"  effort {effort}: lost {len(race_only)} {dict(sorted(kinds.items()))}; "
              f"gained {len(chain_only)} {dict(sorted(gains.items()))}")
    print("\n  The games the race did not list (the start held the best score, or no search), short in the chain:")
    for effort in LEVELS:
        gs = games(runs, effort)
        if not gs:
            continue
        rest = [d for d in gs if d["n"] not in race]
        short = [d for d in rest if d["short"] > 0]
        kinds = {}
        for d in short:
            kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
        print(f"  effort {effort}: {len(short)} of {len(rest)} short {dict(sorted(kinds.items()))}, by line method "
              f"{ {m: sum(d['method'] == m for d in short) for m in LINE_METHODS} }")
    print("\n  Where the chain's lines are the race's lines (a hard searched game at effort 7 whose improvements agree "
          "with the race's through its stop):")
    gs = {d["n"]: d for d in games(runs, 7)}
    same = [n for n in hard if n in gs and gs[n]["method"] == "search" and same_line_as_race(gs[n], race[n])]
    print(f"  {len(same)} of the {len([n for n in hard if n in gs])} hard games; "
          f"of the others {sum(gs[n]['prev_short'] > 0 for n in hard if n in gs and n not in same)} follow a "
          f"short game")
    both_ok = [n for n in same if reached_in_race(race[n], budget_of(7)) == (gs[n]["short"] == 0)]
    print(f"  of those, the chain and the race agree on the known score in {len(both_ok)}")
    # The lower bound of the race, against games where the chain's line is the race's line, at every level.
    print("  The race's lower bound against the chain's exact result, where the lines are the race's (all levels):")
    wrong = []
    checked = 0
    for effort in LEVELS:
        gs_e = {d["n"]: d for d in games(runs, effort)}
        for n in same:
            if n in gs_e and same_line_as_race(gs_e[n], race[n], same_start=True):
                checked += 1
                if reached_in_race(race[n], budget_of(effort)) != (gs_e[n]["short"] == 0):
                    wrong.append((effort, n))
    print(f"  {checked} game-levels compared; they disagree in {len(wrong)}: {wrong[:20]}")
    return summary


def origin_tables(runs, race):
    """The first game of each streak (a shortfall of its own: the game before it is at opt(n - 1)) against the race:
    does the game stay short when played alone from the proven game before it?"""
    print("\n== 5b. The first game of each streak, against the race (alone from the proven game before it) ==")
    print(f"  {'effort':>6} | streaks | first game short in the race too | reached in the race (a game the chain's "
          f"line missed) | not a hard game of the race | games in the streaks: of the first kind / the others")
    listing = []
    for effort in LEVELS:
        origins = [s for lines in runs.get((effort, False), {}).values() for s in streaks_of(lines)]
        stuck, reached, easy = [], [], []
        for g, end in origins:
            n = g[0]["n"]
            if n not in race:
                easy.append((g, end))
            elif reached_in_race(race[n], budget_of(effort)):
                reached.append((g, end))
            else:
                stuck.append((g, end))
        print(f"  {effort:>6} | {len(origins):>7} | {len(stuck):>33} | {len(reached):>62} | {len(easy):>27} | "
              f"{sum(len(g) for g, _ in stuck)} / {sum(len(g) for g, _ in reached + easy)}")
        if effort >= 1:
            listing.append((effort, [(g[0]["n"], g[0]["short"], len(g), "short alone" if (g[0]["n"] in race and not
                reached_in_race(race[g[0]["n"]], budget_of(effort))) else "reached alone",
                f"{e['method']} {e['n']}" if e else "segment end") for g, e in origins]))
    for effort, rows in listing:
        print(f"  effort {effort}: " + "; ".join(f"{n} short {size}, {length} games, {alone}, ended by {end}"
                                                   for n, size, length, alone, end in rows))


def same_line_as_race(d, r, same_start=False):
    """Whether a chain line is the race's line of the same game: the same start and trajectories and the same
    improvements as far as the race's game went (it stopped at the known score).  With `same_start`, a chain line of a
    lower level is compared on the improvements that its budget includes."""
    if d["start"] != r["start"] or d["trajectories"] != r["trajectories"]:
        return False
    key = ("round", "trajectory", "stage", "neighborhoods", "steps", "work", "score")
    xs = [tuple(x[k] for k in key) for x in d["improvements"]]
    ys = [tuple(x[k] for k in key) for x in r["improvements"]]
    if same_start:
        return xs == ys[:len(xs)] and len(xs) <= len(ys)
    return xs[:len(ys)] == ys


# ---------------------------------------------------------------------------------------------------------------------
# 6. The remedy


def remedy_tables(runs, opt):
    """Whether a line of n + 1 shows the line of n short, and what the shortfalls cost."""
    print("\n== 6. Would the game after show a shortfall? (a remedy: play game n again from the moves of n + 1) ==")
    print(f"  slack(n) = n + opt(n - 1) - opt(n): the points by which the proven ceiling of n lies above opt(n); a "
          f"perfect game n + 1 shows game n short by s only if s > slack(n + 1)")
    slack = {n: opt[n]["ceiling"] - opt[n]["score"] for n in range(4562, 5061)}
    print(f"  slack(n + 1) = 0 for {sum(v == 0 for v in slack.values())} of the 499 games; "
          f"median {median(list(slack.values())):.0f}")
    print(f"  {'effort':>6} | short games with a game after | shown by a perfect game after (s > slack) | "
          f"shown by the real line after (prev.short_by > 0) | short games whose streak ended in a search")
    keys = [(e, False) for e in LEVELS] + [(PAST_CEILING_EFFORT, True)]
    for effort, past in keys:
        by_segment = runs.get((effort, past), {})
        if not by_segment:
            continue
        count = shown_oracle = shown = 0
        for lines in by_segment.values():
            for d, after in zip(lines, lines[1:]):
                if d["short"] > 0:
                    count += 1
                    shown_oracle += d["short"] > slack[after["n"]]
                    shown += after["prev"]["short_by"] > 0
        ended = sum(1 for lines in by_segment.values() for g, e in streaks_of(lines) if e and e["method"] == "search")
        print(f"  {level_label(effort, past):>6} | {count:>29} | {shown_oracle:>40} | {shown:>46} | {ended}")


def signal_tables(runs):
    """Whether the line of a searched game that ran its whole budget shows that the game fell short."""
    print("\n== 6b. Searched games that ran their whole budget (not at the ceiling): is a game short if its line "
          "looks different? ==")
    print(f"  {'effort':>6} | at opt(n): games, with an improvement in the rounds, median share of rounds at stage 2 | "
          f"short: games (own / handed), with an improvement, median share at stage 2")

    def stage2(d):
        total = sum(map(sum, d["stage_rounds"]))
        return sum(x[2] for x in d["stage_rounds"]) / total if total else 0.0

    for effort in LEVELS:
        if effort == 0:
            continue
        whole = [d for d in games(runs, effort) if d["method"] == "search" and not d["at_ceiling"]]
        good = [d for d in whole if d["short"] == 0]
        short = [d for d in whole if d["short"] > 0]
        print(f"  {effort:>6} | {len(good):>4}, {sum(bool(d['improvements']) for d in good):>3}, "
              f"{median([stage2(d) for d in good]):.2f} | {len(short):>3} ({sum(d['kind'] == 'own' for d in short)} / "
              f"{sum(d['kind'] == 'handed' for d in short)}), {sum(bool(d['improvements']) for d in short):>2}, "
              f"{median([stage2(d) for d in short]) if short else float('nan'):.2f}")


# ---------------------------------------------------------------------------------------------------------------------
# 4. The datasheet


def datasheet(runs, speedups, load, proven):
    """Item 4: one row a level, where more effort stops paying, and where the unsound mode's time reaches the proven
    mode's.  The times are those of an idle machine (the chains' seconds divided by the load factors), and the times
    as measured are beside them."""
    print("\n== 4. The datasheet ==")
    best = max(speedups, key=lambda t: speedups[t][1])
    wall = statistics.mean(proven[lo]["wall"] for lo, _ in SEGMENTS)
    cpu = statistics.mean(proven[lo]["cpu"] for lo, _ in SEGMENTS)
    print(f"  best thread count of Part 2: {best}; load factors (start, rounds): {load[0]:.2f}, {load[1]:.2f}; "
          f"the proven mode: {wall:.1f} hours per 100 games (wall, 88 threads), {cpu:.0f} CPU hours")
    print(f"  {'effort':>6} {'budget':>10} | share | median searched game, s: alone 4 threads / measured | "
          f"90th of the 500, s | hours per 100 games: measured on its threads / alone 4 threads / alone {best} "
          f"threads | thread-hours "
          f"(alone, 4 threads)")
    rows = []
    for effort in LEVELS:
        gs = games(runs, effort)
        if not gs:
            continue
        row = {"effort": effort, "share": sum(d["short"] == 0 for d in gs) / len(gs)}
        for key, target, factors in (("4", 4, load), ("b", best, load), ("m", 4, (1.0, 1.0))):
            secs = [at_threads(d, threads_of(effort), target, speedups, factors) for d in gs]
            row["hours" + key] = sum(secs) / len(gs) * 100 / 3600
            row["searched" + key] = median([x for x, d in zip(secs, gs) if d["method"] == "search"])
            row["p90" + key] = percentile(secs, 0.9)
            row["segments" + key] = [
                sum(x for x, d in zip(secs, gs) if d["segment"] == lo) / 3600 for lo, _ in SEGMENTS]
        row["measured"] = sum(d["seconds"] for d in gs) / len(gs) * 100 / 3600
        rows.append(row)
        print(f"  {effort:>6} {budget_of(effort):>10,} | {100 * row['share']:>4.1f}% | "
              f"{row['searched4']:>9.1f} / {row['searchedm']:>8.1f} | {row['p904']:>7.1f} | "
              f"{row['measured']:>6.2f} h ({threads_of(effort)}) / {row['hours4']:>6.2f} / {row['hoursb']:>6.2f} | "
              f"{4 * row['hours4']:>6.2f}")
    print("  gain in points over the level below: " + ", ".join(
        f"{r['effort']}: {100 * (r['share'] - p['share']):+.1f}" for p, r in zip(rows, rows[1:])))
    stop = next((r["effort"] for p, r in zip(rows, rows[1:]) if r["share"] - p["share"] < 0.01), None)
    print(f"  the first level whose gain over the level below is under one point: {stop} (the level below it, "
          f"{stop - 1 if stop else None}, is where more effort stops paying)")
    print(f"\n  hours of the 100 games of each segment alone, on 4 threads / on {best} threads, against the proven "
          "mode's wall hours and CPU hours")
    print(f"  {'effort':>6} | " + " | ".join(f"{lo}-{hi}".rjust(13) for lo, hi in SEGMENTS))
    for r in rows:
        print(f"  {r['effort']:>6} | " + " | ".join(
            f"{a:>5.2f} / {b:>5.2f}" for a, b in zip(r["segments4"], r["segmentsb"])))
    print(f"  {'proven':>6} | " + " | ".join(f"{proven[lo]['wall']:>13.2f}" for lo, _ in SEGMENTS) + "   (wall hours)")
    print(f"  {'proven':>6} | " + " | ".join(f"{proven[lo]['cpu']:>13.1f}" for lo, _ in SEGMENTS) + "   (CPU hours)")
    for key, name in (("4", "4 threads"), ("b", f"{best} threads")):
        crossing = []
        for i, (lo, hi) in enumerate(SEGMENTS):
            level = next((r["effort"] for r in rows if r["segments" + key][i] >= proven[lo]["wall"]), None)
            crossing.append(f"{lo}-{hi}: {level if level is not None else 'none'}")
        print(f"  the lowest level whose time alone on {name} reaches the proven mode's wall time: "
              + "; ".join(crossing))
    top = rows[-1]
    levels = []
    for i, (lo, hi) in enumerate(SEGMENTS):
        thread_hours = 4 * top["segments4"][i]
        meet = 7 + math.log2(proven[lo]["cpu"] / thread_hours)
        levels.append(f"{lo}-{hi}: {thread_hours:.1f} thread-hours at level 7, level {meet:.1f} if each level "
                      f"doubles it, against {proven[lo]['cpu']:.0f} CPU hours")
    print("  thread-hours of level 7 on 4 threads against the proven mode's CPU hours, and the level (doubling "
          "the time a level) where they meet: " + "; ".join(levels))
    return rows, best, wall


def chart(rows, best, proven_wall, proven_range, path):
    """The chart: the share of optimal scores against the hours per 100 games, a point per level, on 4 threads and on
    the best thread count of Part 2, with the proven mode marked.  A hand-written SVG, light and dark.  Effort 0 lies
    below the axis and is named in a note."""
    width, height, left, right, top, bottom = 900, 580, 76, 24, 124, 64
    plot_w, plot_h = width - left - right, height - top - bottom
    x_min, x_max = 0.01, 200.0
    y_min, y_max = 0.85, 1.0
    boxes = []  # (x0, y0, x1, y1, text): the text labels, to check that none overlaps another

    def px(hours):
        return left + plot_w * (math.log10(hours) - math.log10(x_min)) / (math.log10(x_max) - math.log10(x_min))

    def py(share):
        return top + plot_h * (1 - (share - y_min) / (y_max - y_min))

    def text(x, y, content, anchor="start", cls="", size=12):
        """A label; its box is kept for the overlap check (6.2 pixels a character at 12 pixels)."""
        w = 6.2 * len(content) * size / 12
        x0 = x if anchor == "start" else x - w / 2 if anchor == "middle" else x - w
        boxes.append((x0, y - size * 0.8, x0 + w, y + size * 0.25, content))
        cls_attr = f' class="{cls}"' if cls else ""
        return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{cls_attr}>{content}</text>'

    css = """
<style>
  :root { --surface: #ffffff; --ink: #1f2328; --muted: #59636e; --grid: #d1d9e0; --a: #2a78d6; --b: #eb6834; }
  @media (prefers-color-scheme: dark) { :root { --surface: #1a1a19; --ink: #f0efec; --muted: #c3c2b7; --grid: #3a3a38;
    --a: #3987e5; --b: #d95926; } }
  text { font-family: Helvetica, Arial, sans-serif; font-size: 12px; fill: var(--muted); }
  .ink { fill: var(--ink); } .title { font-size: 16px; font-weight: 600; }
  .grid { stroke: var(--grid); stroke-width: 1; }
</style>"""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
           f'aria-labelledby="title desc">', '<title id="title">The datasheet of the unsound mode</title>',
           '<desc id="desc">The share of the 500 games of 4561-5060 with the proven score against the hours per 100 '
           'games, a point for each level of effort from 1 to 7, on 4 threads and on 64 threads, and the proven '
           'mode.</desc>', css, '<rect width="100%" height="100%" fill="var(--surface)"/>',
           text(left, 26, "The share of optimal scores against the time (the 500 games of 4561-5060)",
                cls="ink title", size=16),
           text(left, 46, "Five chains of 100 games, a point for each level of effort (the number beside it), one "
                          "seed, no game stops at a known score."),
           text(left, 62, f"Times alone on an idle machine, estimated from the chains: blue 4 threads, orange "
                          f"{best} threads (Part 2's speedups).")]
    for hours in (0.01, 0.1, 1, 10, 100):
        x = px(hours)
        out.append(f'<line class="grid" x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}"/>')
        out.append(text(x, top + plot_h + 18, f"{hours:g} h", "middle"))
    for share in (0.85, 0.90, 0.95, 1.0):
        y = py(share)
        out.append(f'<line class="grid" x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(text(left - 8, y + 4, f"{round(100 * share)}%", "end"))
    out.append(text(left + plot_w / 2, height - 14, "hours per 100 games (wall time, log axis)", "middle"))
    out.append(f'<text transform="translate(18 {top + plot_h / 2:.0f}) rotate(-90)" text-anchor="middle">'
               f'games with the proven score</text>')
    out.append(text(left + 8, top + plot_h - 8, "The axis starts at 85%.  Effort 0 (5.6% of the games, 0.09 h on 4 "
                                                 "threads) is below it."))
    for key, color, dy, name in (("hours4", "var(--a)", -10, "4 threads"),
                                 ("hoursb", "var(--b)", 17, f"{best} threads")):
        pts = [(px(r[key]), py(r["share"])) for r in rows if r["effort"] >= 1]
        out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{color}" '
                   f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        for (x, y), r in zip(pts, [r for r in rows if r["effort"] >= 1]):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}" stroke="var(--surface)" '
                       f'stroke-width="2"/>')
            out.append(text(x, y + dy, str(r["effort"]), "middle", "ink"))
        out.append(text(pts[-1][0] + 12, pts[-1][1] + 4, name, cls="ink"))
    x0, x1, y = px(proven_range[0]), px(proven_range[1]), py(1.0)
    out.append(f'<line x1="{x0:.1f}" x2="{x1:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--ink)" stroke-width="2"/>')
    out.append(f'<path d="M{px(proven_wall):.1f},{y - 7:.1f} l7,7 l-7,7 l-7,-7 z" fill="var(--ink)" '
               f'stroke="var(--surface)" stroke-width="2"/>')
    out.append(text(x0, y - 30, "proven mode, 88 threads: 100% of the games", cls="ink"))
    out.append(text(x0, y - 14, f"diamond: {proven_wall:.1f} h on average; bar: {proven_range[0]:.2f} h to "
                                f"{proven_range[1]:.1f} h over the five segments"))
    for i, (color, name) in enumerate((("var(--a)", "unsound mode on 4 threads"),
                                       ("var(--b)", f"unsound mode on {best} threads"),
                                       ("var(--ink)", "proven mode on 88 threads"))):
        y_l = top + plot_h - 70 + 18 * i
        out.append(f'<circle cx="{width - 250}" cy="{y_l}" r="4.5" fill="{color}"/>')
        out.append(text(width - 238, y_l + 4, name, cls="ink"))
    out.append("</svg>")
    overlaps = [(a[4], b[4]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]]
    outside = [t[4] for t in boxes if t[0] < 0 or t[2] > width or t[1] < 0 or t[3] > height]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"\n  chart written: {path}; labels overlapping: {overlaps}; outside the chart: {outside}")


# ---------------------------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default=os.path.join(HERE, "..", "..", "..", "..", "results", "optimal.jsonl.gz"))
    parser.add_argument("--runs", default=os.path.join(HERE, "runs"))
    parser.add_argument("--threads", default=os.path.join(HERE, "threads"))
    parser.add_argument("--continue", dest="cont", default=os.path.join(HERE, "continue"))
    parser.add_argument("--race", default=os.path.join(HERE, "..", RACE_ENTRY))
    parser.add_argument("--chart", default=os.path.join(HERE, "datasheet.svg"))
    parser.add_argument("--partial", action="store_true")
    args = parser.parse_args()

    opt = read_results(args.results)
    runs = read_runs(args.runs, opt, args.partial)
    race = read_race(args.race)
    threads = read_threads(args.threads)
    checks = Checks()
    cont = read_continuation(args.cont, opt, checks)
    total = sum(len(lines) for by_segment in runs.values() for lines in by_segment.values())
    print(f"Study E2: runs {sorted(runs)}, {total} lines")
    check_runs(runs, opt, args.partial, checks)
    share_tables(runs, opt)
    shortfall_tables(runs)
    streak_tables(runs)
    continuation_tables(runs, cont)
    ceiling_tables(runs, opt)
    speedups, load = thread_tables(threads, runs, opt, checks)
    proven = time_tables(runs, opt, speedups, load)
    race_tables(runs, race, opt, checks)
    origin_tables(runs, race)
    remedy_tables(runs, opt)
    signal_tables(runs)
    rows, best, wall = datasheet(runs, speedups, load, proven)
    walls = [proven[lo]["wall"] for lo, _ in SEGMENTS]
    chart(rows, best, wall, (min(walls), max(walls)), args.chart)
    print(f"\n== Checks: {checks.lines} lines checked, {len(checks.failures)} failures ==")
    for failure in checks.failures[:40]:
        print("  FAIL", failure)
    if checks.failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
