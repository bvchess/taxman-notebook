#!/usr/bin/env python3
"""Study H1 of the unsound mode: checks the lines of every run, prints every number of the entry, and writes the chart.

    nice -n 19 python3 -I analyze.py --results optimal.jsonl.gz [--bounds fm_bound.json] [--runs DIR] [--e2 DIR]
        [--chart FILE] [--machine-chart FILE] > out.txt

`--results` is the proven results file of the main repository (`results/optimal.jsonl.gz`).  `--bounds` (default:
`fm_bound.json` beside the script) holds the Franklin-Moniot upper bound of every game 2..5160, which fm_bound.py
writes.  `--runs` (default: `runs/` beside the script) holds the lines of this study: `unsound/eE-5061.jsonl.gz` (the
unsound mode on 5061-5160) and `heur/{B,C}-NAME.jsonl.gz` (the heuristics on 4561-5060, `B`, and on 5061-5160, `C`;
a job cut into parts has the files `NAME-pK`).  `--e2` (default: the folder `runs/` of the entry of study E2, beside
this one) holds E2's chains `eE-LO.jsonl.gz` for 4561-5060, the unsound mode's lines there.  Any file may be `.jsonl`
as well as `.jsonl.gz`.  A row has the games its run reached, and its table says how many.  The script changes nothing,
except that it writes the two charts.

The games 5061-5160 are past the proven games, so they have no opt(n).  Their reference is the best score that any
method of the study found for the game (a lower bound on opt(n)), and a method's shortfall there is the points it
falls short of that score.
"""

import argparse
import glob
import gzip
import heapq
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_H1 = "50db88e"
BUILD_E2 = "a2a1a2e"
B_LO, B_HI = 4561, 5060
C_LO, C_HI = 5061, 5160
SEGMENT = 100
E2_EFFORTS = range(8)
H1_EFFORTS = (2, 4, 7)
MONIOT = (("OneTax", "moniot-onetax"), ("GreedyOneTax", "moniot-greedyonetax"), ("PureOneTax", "moniot-pureonetax"),
          ("MaxTurn+", "moniot-maxturnplus"), ("MaxTurn", "moniot-maxturn"), ("OddsEvens", "moniot-oddsevens"),
          ("MaxPick", "moniot-maxpick"))
PYTHON = (("maxturn", "maxturn"), ("onetax", "onetax"), ("cascade", "cascade"), ("solvent", "solvent"),
          ("solvent-b", "solvent_b"))
PAIRED_LEVELS = ("level 1", "level 6")  # the old efforts 2 and 7
WORKERS = 88  # the machine's CPUs: games that are independent run this many at once
# What study E2 measured (its entry, parts 5 and 6), to convert the unsound mode's seconds on 4 threads to 64 threads
# alone on the machine: the busy machine's seconds over an idle machine's, and the speedups from 4 to 8 and to 64
# threads, for the start of a searched game and for its rounds.
E2_BUSY = {"start": 1.78, "rounds": 1.73}
E2_SPEEDUP = {8: {"start": 1.72, "rounds": 1.68}, 64: {"start": 5.87, "rounds": 4.15}}
MACHINE_THREADS = 64
LISTED = 12
CHAIN_LABEL = "continuation chain"


def level_name(effort):
    """The name of a run's level in the numbering of master 19a6c24, which has levels 1 to 6: the old effort E (the runs
    are of master 50db88e, whose lines record the effort and the budget) is the level E - 1 from effort 2 up.  The
    start alone (effort 0) and the budget of 65,536 (effort 1) are no levels there."""
    if effort == 0:
        return "start alone"
    if effort == 1:
        return "65,536 work"
    return f"level {effort - 1}"


def level_short(effort):
    """The short name for a mark of the chart."""
    return "start" if effort == 0 else str(effort - 1)


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


def read_results(path):
    """The proven score of each game of the results file."""
    with gzip.open(path, "rt") as f:
        return {d["n"]: d["score"] for d in map(json.loads, f)}


def proper_divisors(top):
    """The proper divisors of each number up to top."""
    divs = [[] for _ in range(top + 1)]
    for d in range(1, top // 2 + 1):
        for m in range(2 * d, top + 1, d):
            divs[m].append(d)
    return divs


def replay(n, moves, divs):
    """Plays the moves as a game of n.  Returns the score and whether a legal move was left at the end; raises
    ValueError at the first move that is not legal (a number out of the pot, or with no divisor left in the pot)."""
    pot = bytearray([1]) * (n + 1)
    pot[0] = 0
    score = 0
    for c in moves:
        if not 1 <= c <= n or not pot[c]:
            raise ValueError(f"game {n}: move {c} is not in the pot")
        tax = [d for d in divs[c] if pot[d]]
        if not tax:
            raise ValueError(f"game {n}: move {c} has no divisor left")
        for d in tax:
            pot[d] = 0
        pot[c] = 0
        score += c
    left = any(pot[c] and any(pot[d] for d in divs[c]) for c in range(2, n + 1))
    return score, left


def load_lines(directory, name, lo, hi, failures):
    """The lines of a heuristic's files by n, or None if there is none: the file `name`, or the parts of a job that
    was cut into parts, `name-p0`, `name-p1`, ... ."""
    paths = [find(directory, name)]
    for path in sorted(glob.glob(os.path.join(directory, name + "-p*.jsonl*"))):
        base = os.path.basename(path)
        paths.append(find(directory, base[:base.index(".jsonl")]))
    paths = [p for p in dict.fromkeys(paths) if p]
    if not paths:
        return None
    lines = {}
    for path in paths:
        for d in read_lines(path):
            if d["n"] in lines:
                failures.append(f"{name}: game {d['n']} is in two files")
            lines[d["n"]] = d
    bad = [n for n in lines if not lo <= n <= hi]
    if bad:
        failures.append(f"{name}: games outside {lo}-{hi}: {bad[:5]}")
    return lines


# ---------------------------------------------------------------------------------------------------------------------
# Rows


class Row:
    """One row of a table: a strategy, or a level of the unsound mode, on the games it played."""

    def __init__(self, label, family, threads, games, seconds):
        self.label, self.family, self.threads = label, family, threads
        self.games = games  # {n: score}
        self.seconds = seconds  # {n: seconds}
        self.short = label  # the label of a mark of the chart
        self.moves = {}
        self.start_seconds = {}  # {n: seconds of the start of a searched game}, for the unsound mode
        self.loads = []  # the load average at the start of each game, for the rows that record it
        self.resumed = []  # the games that started from the file's line, where a run went on from its file
        self.ended_with_move = 0  # games that ended with a legal move left (the taxman's leftovers could be picked)


def stat_row(row, ref, bound, games=None):
    """The numbers of a row's table line over its games (or over `games`, a subset)."""
    ns = sorted(row.games if games is None else games)
    at = sum(1 for n in ns if row.games[n] == ref[n])
    points = sum(row.games[n] for n in ns)
    best = sum(ref[n] for n in ns)
    ratio, worst_n = min((row.games[n] / ref[n], n) for n in ns)
    times = [row.seconds[n] for n in ns if n in row.seconds]
    loads = row.loads if games is None else []
    return {"games": len(ns), "at": at, "share": at / len(ns), "points": points / best, "short": best - points,
            "worst": ratio, "worst_n": worst_n, "below": 1 - points / sum(bound[n] for n in ns),
            "median": statistics.median(times) if times else None, "mean": sum(times) / len(times) if times else None,
            "total": sum(times) if times else None, "load": sum(loads) / len(loads) if loads else None}


def pct(x, digits=1):
    """A share, in percent."""
    return f"{100 * x:.{digits}f}%"


def points_text(x):
    """A point share, in percent: three decimals, and four where it is closer than 0.01 percent to 100."""
    return pct(x, 4 if x > 0.9999 else 3)


def seconds_text(x):
    """Seconds with the digits that tell them apart."""
    if x is None:
        return "-"
    if x < 0.1:
        return f"{x:.3f}"
    if x < 10:
        return f"{x:.2f}"
    return f"{x:,.0f}" if x >= 100 else f"{x:.1f}"


def hours_text(seconds):
    """Hours with the digits that tell them apart."""
    hours = seconds / 3600
    if hours < 0.0001:
        return f"{hours:.1e}"
    if hours < 0.001:
        return f"{hours:.5f}"
    if hours < 0.1:
        return f"{hours:.4f}"
    return f"{hours:.2f}" if hours < 10 else f"{hours:.1f}"


def lpt_makespan(durations, workers):
    """The time to play games on `workers` workers, each game on one worker, the longest first onto the worker with
    the least work."""
    loads = [0.0] * workers
    heapq.heapify(loads)
    for d in sorted(durations, reverse=True):
        heapq.heappush(loads, heapq.heappop(loads) + d)
    return max(loads)


def segment_of(n):
    """The stretch and the segment of 100 games that a game lies in."""
    return ("B", (n - B_LO) // SEGMENT) if n <= B_HI else ("C", (n - C_LO) // SEGMENT)


def machine_seconds_per_100(row):
    """The seconds that 100 games take on the whole machine.  Games that are independent (moniot/'s strategies, and
    the Python ones but the chain) run WORKERS at once: the time of the longest-first schedule of the segment's 100
    games on WORKERS workers, a sample of fewer games repeated to 100, averaged over the segments the row played in.  A
    chain plays one game after another on its one thread, so it takes the sum.  The unsound mode plays one game after
    another on MACHINE_THREADS threads, which the seconds on its own threads are converted to by E2's measurements of
    the busy machine and of the speedups: the time alone."""
    if row.family in ("moniot", "python"):
        groups = {}
        for n, seconds in row.seconds.items():
            groups.setdefault(segment_of(n), []).append(seconds)
        spans = [lpt_makespan([times[i % len(times)] for i in range(SEGMENT)], WORKERS) for times in groups.values()]
        return sum(spans) / len(spans)
    if row.family == "chain":
        return 100 * sum(row.seconds.values()) / len(row.seconds)
    total = 0.0
    for n, seconds in row.seconds.items():
        start = min(row.start_seconds.get(n, 0.0), seconds)
        rounds = seconds - start
        if row.threads == 8:  # to the 4 threads of the other runs
            start, rounds = start * E2_SPEEDUP[8]["start"], rounds * E2_SPEEDUP[8]["rounds"]
        total += (start / E2_BUSY["start"] / E2_SPEEDUP[MACHINE_THREADS]["start"]
                  + rounds / E2_BUSY["rounds"] / E2_SPEEDUP[MACHINE_THREADS]["rounds"])
    return 100 * total / len(row.seconds)


def check_row(row, lines, ref, bound, divs, failures):
    """The checks every row passes: no score above opt(n) where it is known (`ref`), none above the bound, and the moves
    replay as a legal game of the score the line gives."""
    for n, d in sorted(lines.items()):
        what = f"{row.label} game {n}"
        if ref is not None and d["score"] > ref[n]:
            failures.append(f"{what}: scores {d['score']}, above opt(n) {ref[n]}")
        if d["score"] > bound[n]:
            failures.append(f"{what}: scores {d['score']}, above the bound {bound[n]}")
        if d.get("moves") is not None:
            row.moves[n] = d["moves"]
            try:
                score, left = replay(n, d["moves"], divs)
            except ValueError as error:
                failures.append(f"{what}: {error}")
                continue
            if score != d["score"]:
                failures.append(f"{what}: replays to {score}, the line says {d['score']}")
            row.ended_with_move += left


def heuristic_row(label, family, lines, opt, bound, divs, failures):
    """A row of a heuristic's lines.  `opt` is the proven scores where the stretch has them, else None."""
    row = Row(label, family, 1, {n: d["score"] for n, d in lines.items()}, {n: d["seconds"] for n, d in lines.items()})
    row.loads = [d["load"] for d in lines.values() if "load" in d]
    check_row(row, lines, opt, bound, divs, failures)
    return row


def unsound_row(label, lines, opt, bound, divs, failures, build, effort, threads, first_games):
    """A row of the unsound mode's lines, checked as E2 checked them: unsound lines of the build, at the effort, with
    the study's options and seed, on the threads; the first game of a run starts from the table's moves and every
    later one from the run's own (or the file's, where a run went on from its file)."""
    row = Row(label, "unsound", threads, {n: d["score"] for n, d in lines.items()},
              {n: d["seconds"] for n, d in lines.items()})
    row.start_seconds = {n: d["start_seconds"] for n, d in lines.items()}
    for n, d in sorted(lines.items()):
        what = f"{label} game {n}"
        if not d.get("unsound") or not d["build"]["commit"].startswith(build) or d["build"]["dirty"]:
            failures.append(f"{what}: not an unsound line of build {build}, not dirty")
        if (d["effort"], d["seed"], d["back"], d["tilt"], d["widen"], d["threads"]) != (effort, 1, 8, 25, 4, threads):
            failures.append(f"{what}: effort, seed, options or threads are not the study's")
        allowed = ("table",) if n in first_games else ("run", "results")
        if d["prev"] is not None and d["prev"]["source"] not in allowed:
            failures.append(f"{what}: starts from {d['prev']['source']}, not {' or '.join(allowed)}")
        if d["prev"] is not None and d["prev"]["source"] == "results":
            row.resumed.append(n)
    check_row(row, lines, opt, bound, divs, failures)
    return row


# ---------------------------------------------------------------------------------------------------------------------
# The stretches


def heuristic_rows(args, stretch, lo, hi, opt, bound, divs, failures):
    """The rows of the heuristics on a stretch (`B` or `C`), in the order of the tables."""
    heur = os.path.join(args.runs, "heur")
    rows = []
    for label, name in MONIOT:
        lines = load_lines(heur, f"{stretch}-{name}", lo, hi, failures)
        if lines:
            rows.append(heuristic_row(f"moniot {label}", "moniot", lines, opt, bound, divs, failures))
    for label, name in PYTHON:
        lines = load_lines(heur, f"{stretch}-{name}", lo, hi, failures)
        if lines:
            rows.append(heuristic_row(label, "python", lines, opt, bound, divs, failures))
    lines = {}
    if stretch == "B":
        for first in range(lo, hi + 1, SEGMENT):
            lines.update(load_lines(heur, f"B-chain-{first}", first, first + SEGMENT - 1, failures) or {})
    else:
        lines = load_lines(heur, "C-chain", lo, hi, failures) or {}
    if lines:
        rows.append(heuristic_row(CHAIN_LABEL, "chain", lines, opt, bound, divs, failures))
    return rows


def unsound_rows_b(args, opt, bound, divs, failures):
    """The unsound mode on 4561-5060: E2's chains of 100 games at its efforts 0 to 7."""
    rows = []
    for effort in E2_EFFORTS:
        lines = {}
        for first in range(B_LO, B_HI + 1, SEGMENT):
            path = find(args.e2, f"e{effort}-{first}")
            if path:
                lines.update({d["n"]: d for d in read_lines(path)})
        if lines:
            threads = 8 if effort == 7 else 4
            row = unsound_row(f"unsound, {level_name(effort)}", lines, opt, bound, divs, failures, BUILD_E2, effort,
                              threads, set(range(B_LO, B_HI + 1, SEGMENT)))
            row.short = level_short(effort)
            rows.append(row)
    return rows


def unsound_rows_c(args, bound, divs, failures):
    """The unsound mode on 5061-5160: one chain at each of efforts 2, 4 and 7."""
    rows = []
    for effort in H1_EFFORTS:
        path = find(os.path.join(args.runs, "unsound"), f"e{effort}-{C_LO}")
        if path:
            lines = {d["n"]: d for d in read_lines(path)}
            if lines:
                row = unsound_row(f"unsound, {level_name(effort)}", lines, None, bound, divs, failures, BUILD_H1,
                                  effort, 4, {C_LO})
                row.short = level_short(effort)
                rows.append(row)
    return rows


def best_known(rows):
    """The best score any row has for each game: {n: score}."""
    best = {}
    for row in rows:
        for n, score in row.games.items():
            if score > best.get(n, 0):
                best[n] = score
    return best


# ---------------------------------------------------------------------------------------------------------------------
# Tables


def print_time_table(rows, ref, bound):
    """The seconds of a stretch's rows: the wall seconds of a game as measured, the core-seconds (wall seconds times the
    threads), and the hours that 100 games take played in a row as run and on the whole machine.  All are means over the
    games the row played."""
    print("\n| strategy | threads | mean wall s a game | total wall s | mean core-s a game | 100 games in a row, h "
          "| 100 games on the 88 CPUs, h | load |")
    print("|---|---|---|---|---|---|---|---|")
    for row in rows:
        s = stat_row(row, ref, bound)
        load_text = f"{s['load']:.0f}" if s["load"] else "-"
        print(f"| {row.label} | {row.threads} | {seconds_text(s['mean'])} | {seconds_text(s['total'])} | "
              f"{seconds_text(s['mean'] * row.threads)} | {hours_text(100 * s['mean'])} | "
              f"{hours_text(machine_seconds_per_100(row))} | {load_text} |")


def print_table_b(rows, opt, bound):
    """The tables of 4561-5060, in Markdown: the scores, then the seconds."""
    print("\nStretch B: 4561-5060 (500 games)\n")
    print("| strategy | games | at opt(n) | point share | worst game (n) | below the bound |")
    print("|---|---|---|---|---|---|")
    for row in rows:
        s = stat_row(row, opt, bound)
        print(f"| {row.label} | {s['games']} | {s['at']} ({pct(s['share'])}) | {points_text(s['points'])} | "
              f"{pct(s['worst'], 2)} ({s['worst_n']}) | {pct(s['below'], 3)} |")
    ns = range(B_LO, B_HI + 1)
    gaps = [1 - opt[n] / bound[n] for n in ns]
    print(f"\n  opt(n) itself is {pct(1 - sum(opt[n] for n in ns) / sum(bound[n] for n in ns), 3)} of the points below "
          f"the bound over the 500 games (per game: median {pct(statistics.median(gaps), 3)}, "
          f"smallest {pct(min(gaps), 3)}, largest {pct(max(gaps), 3)})")
    print_time_table(rows, opt, bound)


def print_table_c(rows, best, bound):
    """The tables of 5061-5160, in Markdown: the scores, then the seconds."""
    print("\nStretch C: 5061-5160 (100 games, no opt(n): the reference is the best score any row found)\n")
    print("| strategy | games | at the best | points short of it (total) | point share of the best | worst game (n) "
          "| below the bound |")
    print("|---|---|---|---|---|---|---|")
    for row in rows:
        s = stat_row(row, best, bound)
        print(f"| {row.label} | {s['games']} | {s['at']} ({pct(s['share'])}) | {s['short']:,} | "
              f"{points_text(s['points'])} | {pct(s['worst'], 2)} ({s['worst_n']}) | {pct(s['below'], 3)} |")
    holders = {row.label: sum(1 for n in best if row.games.get(n) == best[n]) for row in rows}
    print("\n  games where a row holds the best: " + "; ".join(f"{k} {v}" for k, v in holders.items() if v))
    ns = sorted(best)
    gaps = [1 - best[n] / bound[n] for n in ns]
    print(f"  the best known is {pct(1 - sum(best.values()) / sum(bound[n] for n in ns), 3)} of the points below the "
          f"bound (per game: median {pct(statistics.median(gaps), 3)}, smallest {pct(min(gaps), 3)}, "
          f"largest {pct(max(gaps), 3)})")
    print_time_table(rows, best, bound)


def print_segments(rows, opt, bound):
    """The trend over the five segments of 4561-5060: for each row the games at opt(n) and the points below the bound
    in each segment of 100 games, and the same for opt(n)."""
    firsts = list(range(B_LO, B_HI + 1, SEGMENT))
    names = [f"{f}-{f + SEGMENT - 1}" for f in firsts]
    print("\nThe trend over the segments of 4561-5060: games at opt(n) of the games the row played in the segment\n")
    print("| strategy | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(firsts))
    for row in rows:
        cells = []
        for f in firsts:
            games = [n for n in row.games if f <= n < f + SEGMENT]
            cells.append(f"{sum(1 for n in games if row.games[n] == opt[n])}/{len(games)}" if games else "-")
        print(f"| {row.label} | " + " | ".join(cells) + " |")
    print("\nThe trend over the segments: points below the bound, in percent of the bound's points\n")
    print("| strategy | " + " | ".join(names) + " | slope per segment |")
    print("|---|" + "---|" * (len(firsts) + 1))
    series = [("opt(n)", {n: opt[n] for n in range(B_LO, B_HI + 1)})] + [(r.label, r.games) for r in rows]
    for label, games in series:
        cells, points = [], []
        for i, f in enumerate(firsts):
            ns = [n for n in games if f <= n < f + SEGMENT]
            if ns:
                gap = 100 * (1 - sum(games[n] for n in ns) / sum(bound[n] for n in ns))
                cells.append(f"{gap:.3f}")
                points.append((i, gap))
            else:
                cells.append("-")
        slope = ""
        if len(points) >= 3:
            xs, ys = [p[0] for p in points], [p[1] for p in points]
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            slope = f"{sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x in xs):+.4f}"
        print(f"| {label} | " + " | ".join(cells) + f" | {slope} |")


def sign_test(a_only, b_only):
    """The two-sided exact p of a sign test of two counts of unpaired wins."""
    n, k = a_only + b_only, min(a_only, b_only)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def print_pairs(stretch, rows, ref, ref_name):
    """Game by game, which games each strategy has at the reference that the unsound mode at levels 1 and 6 does not,
    and the reverse, over the games both played."""
    print(f"\nStretch {stretch}: games at {ref_name} that one has and the other does not (over the games both "
          f"played)\n")
    print("| strategy | against | both | only the strategy | only the unsound mode | neither | strategy scores higher "
          "| p (sign test) |")
    print("|---|---|---|---|---|---|---|---|")
    details = []
    unsound = {r.label: r for r in rows if r.family == "unsound"}
    for row in rows:
        if row.family == "unsound":
            continue
        for name in PAIRED_LEVELS:
            other = unsound.get(f"unsound, {name}")
            if other is None:
                continue
            effort = name
            common = sorted(set(row.games) & set(other.games))
            if not common:
                continue
            only_row = [n for n in common if row.games[n] == ref[n] and other.games[n] != ref[n]]
            only_other = [n for n in common if other.games[n] == ref[n] and row.games[n] != ref[n]]
            both = sum(1 for n in common if row.games[n] == ref[n] and other.games[n] == ref[n])
            neither = len(common) - both - len(only_row) - len(only_other)
            higher = sum(1 for n in common if row.games[n] > other.games[n])
            print(f"| {row.label} | {effort} ({len(common)} games) | {both} | {len(only_row)} | "
                  f"{len(only_other)} | {neither} | {higher} | {sign_test(len(only_row), len(only_other)):.2g} |")
            details.append((row, other, effort, only_row, only_other))
    for row, other, effort, only_row, only_other in details:
        if only_row:
            shown = ", ".join(f"{n} (unsound short by {ref[n] - other.games[n]})" for n in only_row[:LISTED])
            print(f"\n  {row.label} at {ref_name}, the unsound mode at {effort} not: {len(only_row)} games: "
                  f"{shown}{' ...' if len(only_row) > LISTED else ''}")
        if only_other:
            shortfalls = [ref[n] - row.games[n] for n in only_other]
            print(f"  the unsound mode at {effort} at {ref_name}, {row.label} not: {len(only_other)} games, "
                  f"shortfall of {row.label} median {statistics.median(shortfalls):.0f}, largest {max(shortfalls)}")


def print_dominance(stretch, rows, ref, bound):
    """For each heuristic row, the lowest level of the unsound mode with at least its share of games at the reference
    and at least its point share, over the heuristic's own games, and the seconds of that level against its own."""
    print(f"\nStretch {stretch}: the lowest level of the unsound mode that matches each strategy on its own games\n")
    print("| strategy | share | point share | mean s | lowest matching level | its share on the same games "
          "| its point share | its mean s |")
    print("|---|---|---|---|---|---|---|---|")
    levels = [r for r in rows if r.family == "unsound"]
    for row in rows:
        if row.family == "unsound":
            continue
        own = stat_row(row, ref, bound)
        match = None
        for level in levels:
            common = sorted(set(row.games) & set(level.games))
            if len(common) < len(row.games):
                continue
            stats = stat_row(level, ref, bound, common)
            if stats["share"] >= own["share"] and stats["points"] >= own["points"]:
                match = (level, stats)
                break
        head = f"| {row.label} | {pct(own['share'])} | {points_text(own['points'])} | {seconds_text(own['mean'])} |"
        if match is None:
            print(f"{head} none of the levels run | | | |")
        else:
            level, stats = match
            print(f"{head} {level.label} | {pct(stats['share'])} | {points_text(stats['points'])} | "
                  f"{seconds_text(stats['mean'])} |")


def count_checks(rows, stretch):
    """How many lines the stretch's rows have and how many of them replayed as legal games."""
    lines = sum(len(row.games) for row in rows)
    replayed = sum(len(row.moves) for row in rows)
    print(f"  stretch {stretch}: {lines} lines in {len(rows)} rows, {replayed} replayed as legal games of the score "
          f"they give, {lines - replayed} with no moves to replay (the Python onetax and maxturn: none ran)")


def cross_checks(rows, failures, stretch):
    """The Python onetax and maxturn are reimplementations of moniot/'s OneTax and MaxTurn: the scores agree."""
    by_label = {r.label: r for r in rows}
    for mine, theirs in (("maxturn", "moniot MaxTurn"), ("onetax", "moniot OneTax")):
        if mine in by_label and theirs in by_label:
            a, b = by_label[mine], by_label[theirs]
            common = sorted(set(a.games) & set(b.games))
            differ = [n for n in common if a.games[n] != b.games[n]]
            print(f"  stretch {stretch}: Python {mine} against {theirs}: {len(common)} games, {len(differ)} differ")
            if differ:
                failures.append(f"Python {mine} differs from {theirs} in {len(differ)} games")
    for row in rows:
        if row.ended_with_move:
            print(f"  stretch {stretch}: {row.label}: {row.ended_with_move} of {len(row.moves)} replayed games end "
                  f"with a legal move left")
        if row.resumed:
            print(f"  stretch {stretch}: {row.label}: {len(row.resumed)} games started from the file's line "
                  f"(a run went on from its file): {row.resumed[:8]}")


def print_loads(runs):
    """The load average at the start and the end of the unsound run and of the chain of 5061-5160, from jobs.log."""
    path = os.path.join(runs, "jobs.log")
    if not os.path.exists(path):
        return
    print("\nThe load average (one minute) at the start and at the end of the unsound runs and of the chain of "
          "5061-5160, from jobs.log\n")
    starts = {}
    with open(path) as f:
        for line in f:
            words = line.split()
            if len(words) > 4 and "load" in words and words[3] in ("start", "end") and (
                    words[4] == "unsound/e7-5061" or words[4] == "heur/C-chain"):
                load = float(words[words.index("load") + 1])
                if words[3] == "start":
                    starts[words[4]] = load
                else:
                    print(f"  {words[4]}: {starts.get(words[4], float('nan')):.0f} at the start, {load:.0f} at the end "
                          f"({' '.join(words[5:9])})")


# ---------------------------------------------------------------------------------------------------------------------
# The chart

FAMILY_STYLE = {  # family -> (CSS class of the fill, marker, legend text)
    "unsound": ("unsound", "circle", "the unsound mode (4 threads; 8 at level 6 on 4561-5060)"),
    "moniot": ("moniot", "square", "moniot/ (C++, 1 thread)"),
    "python": ("python", "diamond", "heuristics/ (Python, 1 thread)"),
    "chain": ("python", "triangle", "heuristics/ (Python, 1 thread)"),
}
LABELED = ("continuation chain", "solvent-b", "solvent", "moniot OneTax")  # the best few heuristics get a label


def marker(kind, x, y, cls, hollow, title):
    """A mark of 5 pixels around (x, y): a circle, square, diamond or triangle, filled or (a sample) outlined."""
    r = 5.5
    style = f'class="{cls}{" hollow" if hollow else ""}"'
    tip = f"<title>{title}</title>"
    if kind == "circle":
        return f'<circle {style} cx="{x:.1f}" cy="{y:.1f}" r="{r}">{tip}</circle>'
    if kind == "square":
        return f'<rect {style} x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}">{tip}</rect>'
    if kind == "diamond":
        pts = f"{x:.1f},{y - r - 1.5:.1f} {x + r + 1.5:.1f},{y:.1f} {x:.1f},{y + r + 1.5:.1f} {x - r - 1.5:.1f},{y:.1f}"
    else:
        pts = f"{x:.1f},{y - r - 1:.1f} {x + r + 1.5:.1f},{y + r:.1f} {x - r - 1.5:.1f},{y + r:.1f}"
    return f'<polygon {style} points="{pts}">{tip}</polygon>'


def chart(panels, path, axis):
    """The chart: the share of games at the reference against a time (log axis), a point for each strategy and each
    level of the unsound mode, a panel for each stretch.  A hand-written SVG, light and dark.  `panels` is a list of
    (title, rows, ref, bound, the games of the stretch, a note), and `axis` describes the time: its `title`,
    `subtitle`, `label`, the range `x_min` to `x_max`, the `ticks` as (seconds, label), and `value(row, stats)`, the
    seconds of a row.  A hollow mark is a row whose share or time come from some of the games only."""
    width, left, right = 900, 70, 24
    plot_w, plot_h, gap, head = width - left - right, 250, 96, 118
    x_min, x_max = axis["x_min"], axis["x_max"]
    height = head + len(panels) * (plot_h + gap) - gap + 70
    boxes = []

    def px(seconds):
        return left + plot_w * (math.log10(seconds) - math.log10(x_min)) / (math.log10(x_max) - math.log10(x_min))

    def text(x, y, content, anchor="start", cls="", size=12):
        """A label; its box is kept for the overlap check (6.2 pixels a character at 12 pixels)."""
        w = 6.2 * len(content) * size / 12
        x0 = x if anchor == "start" else x - w / 2 if anchor == "middle" else x - w
        boxes.append((x0, y - size * 0.8, x0 + w, y + size * 0.25, content))
        cls_attr = f' class="{cls}"' if cls else ""
        return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{cls_attr}>{content}</text>'

    css = """
<style>
  :root { --surface: #ffffff; --ink: #1f2328; --muted: #59636e; --grid: #d1d9e0; --unsound: #2a78d6;
    --moniot: #eb6834; --python: #1f2328; }
  @media (prefers-color-scheme: dark) { :root { --surface: #1a1a19; --ink: #f0efec; --muted: #c3c2b7; --grid: #3a3a38;
    --unsound: #3987e5; --moniot: #d95926; --python: #f0efec; } }
  text { font-family: Helvetica, Arial, sans-serif; font-size: 12px; fill: var(--muted); }
  .ink { fill: var(--ink); } .title { font-size: 16px; font-weight: 600; } .sub { font-size: 13px; font-weight: 600; }
  .grid { stroke: var(--grid); stroke-width: 1; }
  .unsound { fill: var(--unsound); stroke: var(--surface); stroke-width: 2; }
  .moniot { fill: var(--moniot); stroke: var(--surface); stroke-width: 2; }
  .python { fill: var(--python); stroke: var(--surface); stroke-width: 2; }
  .hollow { fill: var(--surface); stroke-width: 2.5; }
  .unsound.hollow { stroke: var(--unsound); } .moniot.hollow { stroke: var(--moniot); }
  .python.hollow { stroke: var(--python); }
  .link { fill: none; stroke: var(--unsound); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
</style>"""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
           f'aria-labelledby="title desc">', '<title id="title">The unsound mode against the other heuristics</title>',
           '<desc id="desc">For each of two stretches of games, the share of games at the reference score against the '
           'mean seconds a game, a point for each heuristic strategy and for each level of effort of the unsound '
           'mode.</desc>', css, '<rect width="100%" height="100%" fill="var(--surface)"/>',
           text(left, 26, axis["title"], cls="ink title", size=16),
           text(left, 46, axis["subtitle"]),
           text(left, 62, "A hollow mark takes its share and its seconds from some of the games only (the note under "
                          "each panel).")]
    for i, family in enumerate(("unsound", "moniot", "python")):
        cls, kind, name = FAMILY_STYLE[family]
        x = left + (0, 400, 560)[i]
        out.append(marker(kind, x + 6, 82, cls, False, name))
        out.append(text(x + 18, 86, name, cls="ink"))
    for index, (title, rows, ref, bound, size, note) in enumerate(panels):
        top = head + index * (plot_h + gap)
        out.append(text(left, top - 12, title, cls="ink sub", size=13))
        for seconds, label in axis["ticks"]:
            x = px(seconds)
            out.append(f'<line class="grid" x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}"/>')
            out.append(text(x, top + plot_h + 22, label, "middle"))
        for share in (0, 25, 50, 75, 100):
            y = top + plot_h * (1 - share / 100)
            out.append(f'<line class="grid" x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}"/>')
            out.append(text(left - 8, y + 4, f"{share}%", "end"))
        out.append(text(left + plot_w / 2, top + plot_h + 40, axis["label"], "middle"))
        out.append(f'<text transform="translate(16 {top + plot_h / 2:.0f}) rotate(-90)" text-anchor="middle">'
                   f'games at the reference</text>')
        points = []
        for row in rows:
            stats = stat_row(row, ref, bound)
            seconds = axis["value"](row, stats)
            if seconds is None or seconds <= 0:
                continue
            points.append((row, px(seconds), top + plot_h * (1 - stats["share"]), stats))
        levels = [(x, y) for row, x, y, _ in points if row.family == "unsound"]
        if len(levels) > 1:
            out.append(f'<polyline class="link" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in levels)}"/>')
        for row, x, y, _ in points:
            boxes.append((x - 7, y - 7, x + 7, y + 7, f"mark {row.label}"))
        labeled = {id(p[0]) for p in points if p[0].label in LABELED}
        for row, x, y, stats in points:
            cls, kind, _ = FAMILY_STYLE[row.family]
            hollow = stats["games"] < size
            title_text = (f"{row.label}: {pct(stats['share'])} at the reference, {points_text(stats['points'])} of "
                          f"its points, {seconds_text(stats['mean'] * row.threads)} core-s a game over "
                          f"{stats['games']} games, "
                          f"{hours_text(machine_seconds_per_100(row))} h for 100 games on the machine")
            out.append(marker(kind, x, y, cls, hollow, title_text))
        for row, x, y, stats in points:
            if row.family == "unsound":
                content = row.short
                spots = [(x + 9, y + 18, "start"), (x - 9, y + 18, "end"), (x + 9, y - 10, "start"),
                         (x - 9, y - 10, "end"), (x, y - 12, "middle"), (x, y + 22, "middle"),
                         (x + 12, y + 4, "start"), (x - 12, y + 4, "end")]
            elif id(row) in labeled:
                content = row.label.replace("moniot ", "")
                spots = [(x + 11, y + 4, "start"), (x - 11, y + 4, "end"), (x, y - 12, "middle"), (x, y + 22, "middle"),
                         (x + 11, y - 14, "start"), (x + 11, y + 20, "start"), (x - 11, y - 14, "end"),
                         (x - 11, y + 20, "end")]
            else:
                continue
            for sx, sy, anchor in spots:
                w = 6.2 * len(content)
                x0 = sx if anchor == "start" else sx - w / 2 if anchor == "middle" else sx - w
                box = (x0, sy - 10, x0 + w, sy + 3)
                clash = any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in boxes)
                outside = (box[0] < left - 4 or box[2] > left + plot_w + 4 or box[1] < top - 4
                           or box[3] > top + plot_h + 10)
                if not clash and not outside:
                    break
            out.append(text(sx, sy, content, anchor, "ink"))
        out.append(text(left, top + plot_h + 58, note))
    out.append("</svg>")
    overlaps = [(a[4], b[4]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
                if not (a[4].startswith("mark ") and b[4].startswith("mark "))
                and a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]]
    outside = [t[4] for t in boxes if t[0] < 0 or t[2] > width or t[1] < 0 or t[3] > height]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"\nchart written: {os.path.basename(path)}; labels overlapping: {overlaps}; outside the chart: {outside}")


# ---------------------------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--results", required=True)
    parser.add_argument("--bounds", default=os.path.join(HERE, "fm_bound.json"))
    parser.add_argument("--runs", default=os.path.join(HERE, "runs"))
    parser.add_argument("--e2", default=os.path.join(HERE, "..", "the-datasheet-of-the-unsound-mode-2026-11", "runs"))
    parser.add_argument("--chart", default=os.path.join(HERE, "h1.svg"))
    parser.add_argument("--machine-chart", default=os.path.join(HERE, "h1-machine.svg"))
    args = parser.parse_args()

    opt = read_results(args.results)
    with open(args.bounds) as f:
        bound = {int(n): b for n, b in json.load(f).items()}
    divs = proper_divisors(C_HI)
    failures = []
    for n in range(B_LO, B_HI + 1):
        if opt[n] > bound[n]:
            failures.append(f"opt({n}) {opt[n]} is above the bound {bound[n]}")

    b_rows = heuristic_rows(args, "B", B_LO, B_HI, opt, bound, divs, failures) + unsound_rows_b(
        args, opt, bound, divs, failures)
    c_rows = heuristic_rows(args, "C", C_LO, C_HI, None, bound, divs, failures) + unsound_rows_c(
        args, bound, divs, failures)
    best = best_known(c_rows)
    print_table_b(b_rows, opt, bound)
    if best:
        print_table_c(c_rows, best, bound)
    print_segments(b_rows, opt, bound)
    print("\nChecks of the lines\n")
    count_checks(b_rows, "B")
    cross_checks(b_rows, failures, "B")
    count_checks(c_rows, "C")
    cross_checks(c_rows, failures, "C")
    print_loads(args.runs)
    print_pairs("B", b_rows, opt, "opt(n)")
    print_dominance("B", b_rows, opt, bound)
    if best:
        print_pairs("C", c_rows, best, "the best known")
        print_dominance("C", c_rows, best, bound)
    panels = [("4561-5060 (500 games)", b_rows, opt, bound, 500,
               "Hollow: some of the games only (solvent-b 47, the chain 74, a prefix of the games for four moniot/ "
               "rows)."),
              ("5061-5160 (100 games, past the proven games)", c_rows, best, bound, 100,
               "The reference is the best score any method found for the game.  Hollow: some of the games only.")]
    minute, hour = 60, 3600
    chart(panels, args.chart, {
        "title": "The share of games at the reference score against the core-seconds a game",
        "subtitle": "Mean wall seconds times the threads, as measured on a shared machine; the number beside a blue "
                    "point is its level.",
        "label": "core-seconds a game (mean, log axis)", "x_min": 0.003, "x_max": 30000.0,
        "ticks": [(10.0 ** e, f"{10.0 ** e:g} s") for e in range(-2, 5)],
        "value": lambda row, stats: stats["mean"] * row.threads})
    chart(panels, args.machine_chart, {
        "title": "The share of games at the reference score against the time of 100 games on the machine",
        "subtitle": "88 CPUs: independent games 88 at a time, a chain one game after another; the unsound mode on 64 "
                    "threads (converted).",
        "label": "time of 100 games on the 88-CPU machine (log axis)", "x_min": 0.005, "x_max": 400 * hour,
        "ticks": [(0.01, "0.01 s"), (0.1, "0.1 s"), (1, "1 s"), (10, "10 s"), (minute, "1 min"),
                  (10 * minute, "10 min"), (hour, "1 h"), (10 * hour, "10 h"), (100 * hour, "100 h")],
        "value": lambda row, stats: machine_seconds_per_100(row)})
    print(f"\nchecks failed: {len(failures)}")
    for failure in failures[:50]:
        print("  FAILED:", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
