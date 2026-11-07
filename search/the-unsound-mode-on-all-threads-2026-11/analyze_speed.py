#!/usr/bin/env python3
"""The speed tables of B9 (Part 3): the games alone and the chains, before and after, from the runs of run_b9.py.

    python3 -I analyze_speed.py games DIR [AFTER]
    python3 -I analyze_speed.py chains DIR...

A game alone is DIR/g{n}-e{E}-t{T}-{b,a}.jsonl (b: before, master; a: after); its rounds take its seconds less its
start_seconds.  A chain is c{E}-t{T}-{b,a}.jsonl (or .jsonl.gz) in one of the DIRs, timed by its process (runs.log),
and with AFTER the after runs are those of AFTER, a form of the remedy kept apart.  Every line of a
game or a chain must be the same, but for its seconds, threads and build, on every thread count before and after; the
script says so, or stops.
"""

import collections
import glob
import gzip
import json
import os
import re
import sys

VARYING = ("seconds", "start_seconds", "threads", "build")
THREADS = [4, 8, 16, 32, 64, 88]


def timeless(line):
    line = {key: value for key, value in line.items() if key not in VARYING}
    line["improvements"] = [{k: v for k, v in i.items() if k != "seconds"} for i in line.get("improvements") or []]
    return line


def read_lines(path):
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        return [json.loads(line) for line in f]


def process_seconds(directory):
    """The seconds of each run's process, and its CPU seconds (user and system), from runs.log."""
    out = {}
    with open(os.path.join(directory, "runs.log")) as f:
        for line in f:
            m = re.search(r" end (\S+): exit 0 after ([0-9.]+) s, cpu user ([0-9.]+) s, system ([0-9.]+) s", line)
            if m:
                out[m.group(1)] = (float(m.group(2)), float(m.group(3)) + float(m.group(4)))
    return out


def check_same(runs):
    """Every run's lines the same as the first's but for what varies; returns the number of lines compared."""
    (first_label, first), *others = runs
    base = [timeless(line) for line in first]
    for label, lines in others:
        if [timeless(line) for line in lines] != base:
            sys.exit(f"{label} differs from {first_label}")
    return len(base) * len(others)


def games(directory, after=None):
    """The games of `directory`, the after runs from `after` if it is given (a form of the remedy kept apart)."""
    used = process_seconds(directory)
    runs = {}
    paths = glob.glob(os.path.join(directory, "g*-e*-t*-b.jsonl"))
    if after:
        used.update(process_seconds(after))
        paths += glob.glob(os.path.join(after, "g*-e*-t*-a.jsonl"))
    else:
        paths += glob.glob(os.path.join(directory, "g*-e*-t*-a.jsonl"))
    for path in paths:
        n, effort, threads, which = re.match(r"g(\d+)-e(\d+)-t(\d+)-([ab])", os.path.basename(path)).groups()
        lines = read_lines(path)
        if lines:  # A game still in play has no line yet.
            runs[(int(n), int(effort), int(threads), which)] = lines[0]
    for (n, effort) in sorted({(n, e) for n, e, _, _ in runs}):
        mine = sorted((t, w, line) for (m, e, t, w), line in runs.items() if (m, e) == (n, effort))
        compared = check_same([(f"t{t}-{w}", [line]) for t, w, line in mine])
        line = mine[0][2]
        print(f"\n### {n} at effort {effort}: {line['rounds']} rounds, {line['work']} work, score {line['score']}; "
              f"the {len(mine)} lines are the same but for their times ({compared} compared)\n")
        print("| threads | before: game | rounds | start | after: game | rounds | start | "
              "speedup over 4, before: game | rounds | after: game | rounds | after against before | CPU, after over "
              "before |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        got = {(t, w): line for t, w, line in mine}
        base = {w: got.get((4, w)) for w in "ba"}
        for t in THREADS:
            cells = [str(t)]
            for w in "ba":
                line = got.get((t, w))
                cells += [f"{line['seconds']:.1f}", f"{line['seconds'] - line['start_seconds']:.1f}",
                          f"{line['start_seconds']:.2f}"] if line else ["", "", ""]
            for w in "ba":
                line, four = got.get((t, w)), base[w]
                if line and four:
                    rounds = (four["seconds"] - four["start_seconds"]) / (line["seconds"] - line["start_seconds"])
                    cells += [f"{four['seconds'] / line['seconds']:.1f}", f"{rounds:.1f}"]
                else:
                    cells += ["", ""]
            b, a = got.get((t, "b")), got.get((t, "a"))
            cells.append(f"{b['seconds'] / a['seconds']:.2f}" if a and b else "")
            cpu = [used.get(f"g{n}-e{effort}-t{t}-{w}", (0, 0))[1] for w in "ba"]
            cells.append(f"{cpu[1] / cpu[0]:.2f}" if all(cpu) else "")
            print("| " + " | ".join(cells) + " |")


def chains(directories):
    runs, seconds = {}, {}
    for directory in directories:
        seconds.update(process_seconds(directory))
        for path in glob.glob(os.path.join(directory, "c*-t*-[ab].jsonl*")):
            label = os.path.basename(path).removesuffix(".gz").removesuffix(".jsonl")
            effort, threads, which = re.match(r"c(\d+)-t(\d+)-([ab])", label).groups()
            runs[(int(effort), int(threads), which)] = (label, read_lines(path))
    for effort in sorted({e for e, _, _ in runs}):
        # Before, then after, at each number of threads.
        mine = sorted((t, w == "a", label, lines) for (e, t, w), (label, lines) in runs.items() if e == effort)
        compared = check_same([(label, sorted(lines, key=lambda line: line["n"])) for _, _, label, lines in mine])
        print(f"\n### The chain 4861-4960 at effort {effort}: {len(mine[0][3])} games; the {len(mine)} runs' lines are "
              f"the same but for their times ({compared} lines compared)\n")
        print("| threads | build | process (s) | CPU (s) | searched: start | the rest of a searched game | prime | "
              "repeat | speedup over 4 threads | over before on as many threads |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        wall_of = {(t, after): seconds.get(label, (float("nan"), 0))[0] for t, after, label, _ in mine}
        for t, after, label, lines in mine:
            by = collections.defaultdict(float)
            for line in lines:
                by[line["method"]] += line["seconds"]
            start = sum(line["start_seconds"] for line in lines if line["method"] == "search")
            wall, cpu = seconds.get(label, (float("nan"), float("nan")))
            speedup, against = wall_of.get((4, after), float("nan")) / wall, wall_of.get((t, False), float("nan")) / wall
            print(f"| {t} | {'after' if after else 'before'} | {wall:.1f} | {cpu:.0f} | {start:.1f} | "
                  f"{by['search'] - start:.1f} | {by['prime']:.1f} | {by['repeat']:.1f} | {speedup:.1f} | "
                  f"{against:.2f} |")


if __name__ == "__main__":
    mode, *args = sys.argv[1:]
    if mode == "games":
        games(*args)
    else:
        chains(args)
