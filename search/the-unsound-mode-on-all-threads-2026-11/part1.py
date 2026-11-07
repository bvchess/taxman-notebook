#!/usr/bin/env python3
"""The tables of B9's diagnosis (Part 1), from the `B9` lines that the instrumented build wrote to stderr.

    python3 -I part1.py DIAG CHAIN

DIAG holds the runs of one game, g{n}-t{T}.err and .jsonl; CHAIN the chains, c{E}-t{T}.err and .jsonl; each may be
gzipped (.gz).  The build is master 50db88e with lines on stderr (instrument.patch, never committed): each
neighborhood's start, end and steps, each round's wall time against its longest neighborhood and the work of its
neighborhoods over the threads, the CPU of the process (from /proc/self/stat) and the parts of each game.
"""

import collections
import gzip
import json
import os
import re
import statistics
import sys


def text(path):
    """The file at `path`, or its gzipped copy at `path`.gz."""
    return open(path) if os.path.exists(path) else gzip.open(path + ".gz", "rt")


def fields(line):
    out = {}
    for word in line.split()[2:]:
        if "=" in word:
            key, value = word.split("=", 1)
            try:
                out[key] = float(value)
            except ValueError:
                out[key] = value
    return out


def read(path):
    records = collections.defaultdict(list)
    with text(path) as f:
        for line in f:
            if line.startswith("B9 "):
                records[line.split()[1]].append(fields(line))
    return records


def one_game_table(directory):
    runs = {}
    for name in os.listdir(directory):
        m = re.fullmatch(r"g(\d+)-t(\d+)\.err(\.gz)?", name)
        if m:
            runs[(int(m.group(1)), int(m.group(2)))] = read(os.path.join(directory, name.removesuffix(".gz")))
    print("| game | threads | game (s) | start (s) | rounds (s) | longest neighborhoods summed (s) | "
          "work over threads (s) | threads busy | time a step, against 4 threads | system CPU |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for n in sorted({n for n, _ in runs}):
        base = None
        for t in sorted(t for m, t in runs if m == n):
            r = runs[(n, t)]
            line = json.loads(text(os.path.join(directory, f"g{n}-t{t}.jsonl")).readline())
            rounds = r["round"]
            wall = sum(x["par"] for x in rounds)
            longest = sum(x["longest"] for x in rounds)
            total = sum(x["total"] for x in rounds)
            steps = sum(x["steps"] for x in r["nb"])
            per_step = total / steps
            base = base or per_step
            cpu = sum(x["utime"] + x["stime"] for x in rounds)
            sys_share = sum(x["stime"] for x in rounds) / cpu
            print(f"| {n} | {t} | {line['seconds']:.1f} | {line['start_seconds']:.2f} | {wall:.1f} | {longest:.1f} | "
                  f"{total / t:.1f} | {total / (t * wall):.0%} | x{per_step / base:.2f} | {sys_share:.1%} |")
    # The longest neighborhood against its round's mean, on 4 threads.
    for n in sorted({n for n, _ in runs}):
        r = runs[(n, 4)]
        by = collections.defaultdict(list)
        for x in r["nb"]:
            by[int(x["r"])].append(x["e"] - x["s"])
        ratios = [max(v) / statistics.mean(v) for v in by.values()]
        print(f"\n{n} on 4 threads: the longest neighborhood of a round is a median {statistics.median(ratios):.1f} "
              f"times its round's mean, at most {max(ratios):.1f}; between rounds "
              f"{sum(x['wall'] for x in r['call']) - sum(x['par'] for x in r['round']):.3f} s in all")


def chain_table(directory):
    runs = {}
    for name in os.listdir(directory):
        m = re.fullmatch(r"c(\d+)-t(\d+)\.err(\.gz)?", name)
        if m:
            runs[(int(m.group(1)), int(m.group(2)))] = read(os.path.join(directory, name.removesuffix(".gz")))
    print("\n| effort | threads | games' seconds | searched: start, local search | dive | rounds | "
          "longest neighborhoods summed | work over threads | setups: searched | repeat | prime | "
          "rest on one thread |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (effort, t), r in sorted(runs.items()):
        games = {int(g["n"]): g for g in r["game"]}
        setups = {int(s["n"]): s["setup"] for s in r["setup"]}
        by = collections.defaultdict(float)
        for n, g in games.items():
            by["setup " + g["method"]] += setups[n]
            by[g["method"]] += g["seconds"]
        dive = sum(d["wall"] for d in r["dive"])
        start = sum(s["start"] for s in r["start"])
        imp = r["improve"]
        rounds = sum(i["rounds"] for i in imp)
        longest = sum(x["longest"] for x in r["round"])
        spread = sum(x["total"] for x in r["round"]) / t
        # On one thread outside the rounds and the start's local search: the survivors, the moves of a searched game,
        # a repeat's moves and a prime's formula (a game's seconds less its setup), and the appending of the lines.
        rest = (sum(i["survivors"] + i["moves"] for i in imp)
                + sum(g["seconds"] - setups[n] for n, g in games.items() if g["method"] in ("repeat", "prime"))
                + sum(b["append"] + b["moves_before"] for b in r["between"]))
        print(f"| {effort} | {t} | {sum(g['seconds'] for g in games.values()):.1f} | {start - dive:.1f} | {dive:.1f} | "
              f"{rounds:.1f} | {longest:.1f} | {spread:.1f} | {by['setup search']:.1f} | {by['setup repeat']:.1f} | "
              f"{by['setup prime']:.1f} | {rest:.1f} |")
    for (effort, t), r in sorted(runs.items()):
        games = {int(g["n"]): g for g in r["game"]}
        count = collections.Counter(g["method"] for g in games.values())
        each = {m: sum(g["seconds"] for g in games.values() if g["method"] == m) / c for m, c in count.items()}
        print(f"effort {effort}, {t} threads: " + ", ".join(f"{c} {m} games at {each[m]:.3f} s each"
                                                          for m, c in sorted(count.items())))


if __name__ == "__main__":
    one_game_table(sys.argv[1])
    chain_table(sys.argv[2])
