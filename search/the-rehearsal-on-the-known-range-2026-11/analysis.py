#!/usr/bin/env python3
"""The rehearsal of the unsound procedure on the proven games 3001-5060: what its passes did.

    nice -n 19 python3 -I analysis.py > out.txt

Reads the lines of the four passes (`p1.jsonl.gz` to `p4.jsonl.gz`), the rehearsal's best-known file
(`best-known.jsonl.gz`), the passes' logs (`p1.log` to `p4.log`) and `run.log` beside it, and opt(n) from the committed
results.  A game's line in a pass is the last line the pass's file has for it.  The best-known score of a game after
pass k is the best score of the lines of passes 1 to k, which the best-known file also gives, since each of its lines
names the file it came from.  A game is *short* when that score is below opt(n), a *miss* is a game short after the
pass, and a *streak* is a run of consecutive games.  Prints:

1. the checks of every line;
2. the table of the passes, recomputed from the lines;
3. the survival of pass 1's streaks;
4. where the streaks start;
5. the thread-hours of each pass.
"""

import gzip
import json
import os
import re
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
LO, HI = 3001, 5060
KNOWN_TO = 3000
PASSES = range(1, 5)
THREADS = 44
GAMES = range(LO, HI + 1)
DESCENT = r"the descent went down from (\d+) roots: (\d+) games played again, (\d+) of them raised"


def read_lines(name):
    with gzip.open(os.path.join(HERE, name), "rt") as f:
        return [json.loads(text) for text in f if text.strip()]


def read_text(name):
    with open(os.path.join(HERE, name)) as f:
        return f.read()


def streaks(games):
    """The runs of consecutive games, as [first, last] pairs."""
    out = []
    for n in sorted(games):
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return out


def name_of(streak):
    return str(streak[0]) if streak[0] == streak[1] else f"{streak[0]}-{streak[1]}"


def layers():
    """The layer of each n up to HI: the number of its prime factors, with repeats."""
    layer = [0] * (HI + 1)
    for n in range(2, HI + 1):
        m, p = n, 2
        while p * p <= m:
            while m % p == 0:
                m //= p
                layer[n] += 1
            p += 1
        layer[n] += m > 1
    return layer


def last_lines(lines):
    """The last line of each game; the lines of a game must not score less, line after line."""
    last = {}
    for line in lines:
        if line["n"] in last and line["score"] < last[line["n"]]["score"]:
            raise SystemExit(f"n={line['n']}: a line scores {line['score']} after one of {last[line['n']]['score']}")
        last[line["n"]] = line
    return last


def log_seconds(k):
    """The seconds of the games the pass's log lists, of its repair's walks, and its descent line's counts."""
    text = read_text(f"p{k}.log")
    games = sum(float(s) for s in re.findall(r"^n=\d+ .*? (\d+\.\d+) s ", text, re.M))
    repair = sum(float(s) for s in re.findall(r"the repair took ([\d.]+) s", text))
    return games, repair, tuple(int(g) for g in re.search(DESCENT, text).groups())


def wall_seconds():
    """The wall-clock seconds of each pass, from the times `run.sh` printed in `run.log` (a pass ends where the next
    begins, which adds the few seconds of score.py)."""
    text = read_text("run.log")
    stamps = [(int(k), 3600 * int(h) + 60 * int(m) + int(s))
              for k, h, m, s in re.findall(r"pass (\d+) began (\d+):(\d+):(\d+)", text)]
    h, m, s = re.search(r"done (\d+):(\d+):(\d+)", text).groups()
    stamps.append((0, 3600 * int(h) + 60 * int(m) + int(s)))
    return {k: (stamps[i + 1][1] - t) % 86400 for i, (k, t) in enumerate(stamps[:-1])}


def checks(passes, last, best_known, state, opt):
    print("## The checks\n")
    problems = []
    for k, lines in passes.items():
        for line in lines:
            n = line["n"]
            if not (line.get("unsound") and LO <= n <= HI and line["known_to"] == KNOWN_TO
                    and line["threads"] == THREADS):
                problems.append(f"p{k}: n={n}: not an unsound line of this run")
            if line["score"] > min(opt[n], line["bound"]):
                problems.append(f"p{k}: n={n}: score {line['score']} above opt(n) or the bound")
        if sorted(last[k]) != list(GAMES):
            problems.append(f"p{k} has not every game of {LO}-{HI}")
    was = {}
    for line in best_known:
        n = line["n"]
        if line["best_known"]["was"] != was.get(n) or line["score"] <= was.get(n, 0):
            problems.append(f"best-known: n={n}: line {line['score']} after {was.get(n)}")
        was[n] = line["score"]
    for k in PASSES:
        from_file = {}
        for line in best_known:
            if int(line["best_known"]["file"][1]) <= k:
                from_file[line["n"]] = max(from_file.get(line["n"], 0), line["score"])
        if from_file != state[k]:
            problems.append(f"after pass {k}: the pass files and the best-known file give different scores")
    print(f"{sum(len(lines) for lines in passes.values())} lines of the passes, {len(best_known)} of the best-known "
          f"file; problems: {len(problems)}")
    for problem in problems:
        print(f"* {problem}")
    builds = {(line["build"]["commit"][:7], line["build"]["dirty"]) for lines in passes.values() for line in lines}
    print(f"* builds recorded in the lines: {sorted(builds)}")


def table(passes, last, state, opt):
    """The table of the passes, and the streaks of raised games each pass found."""
    print("\n## The passes\n")
    print("| pass | at opt(n) | % | misses | streaks | points short | raised: games | raised: streaks "
          "| raised: points | descent: roots | descent: played again | descent: raised | estimate of streaks left "
          "| own file at opt(n) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    found, listed = [], []
    for k in PASSES:
        misses = [n for n in GAMES if state[k][n] < opt[n]]
        raised = [n for n in GAMES if k > 1 and state[k][n] > state[k - 1][n]]
        found.append(len(streaks(raised)))
        again = [line for line in passes[k] if line["descent"]]
        counts = (len({line["descent"]["root"] for line in again}), len(again),
                  sum(line["score"] > line["descent"]["was"] for line in again))
        assert counts == log_seconds(k)[2], (k, counts, log_seconds(k)[2])
        estimate, own = "", sum(last[k][n]["score"] == opt[n] for n in GAMES)
        if k >= 3 and found[-1] < found[-2]:
            c = 1 - found[-1] / found[-2]
            estimate = f"c = {c:.2f}, about {found[-1] * (1 - c) / c:.1f}"
        row = [k, f"{len(GAMES) - len(misses):,}", f"{100 * (len(GAMES) - len(misses)) / len(GAMES):.1f}", len(misses),
               len(streaks(misses)), f"{sum(opt[n] - state[k][n] for n in misses):,}"]
        gained = sum(state[k][n] - state[k - 1][n] for n in raised) if k > 1 else ""
        row += [len(raised), found[-1], f"{gained:,}"] if k > 1 else ["", "", ""]
        print("| " + " | ".join(str(cell) for cell in row + list(counts) + [estimate, f"{own:,}"]) + " |")
        listed.append(f"after pass {k}, the misses' streaks: {' '.join(name_of(s) for s in streaks(misses))}")
    print()
    for text in listed:
        print(f"* {text}")
    for k in PASSES:
        below = {n: state[k][n] - last[k][n]["score"] for n in GAMES if last[k][n]["score"] < state[k][n]}
        print(f"* pass {k}: games whose own line scores below the best-known score (n: points below): {below}")


def survival(state, opt, layer):
    """Pass 1's streaks: their size, points short, root, and the pass that closed each; returns {root: pass or None}."""
    print("\n## The survival of pass 1's streaks\n")
    first = streaks([n for n in GAMES if state[1][n] < opt[n]])
    closed_in = {}
    print("| streak | games | points short | root | layer of the root | short after pass 2 | after pass 3 "
          "| after pass 4 | closed in pass |")
    print("|---|---|---|---|---|---|---|---|---|")
    for streak in first:
        span = range(streak[0], streak[1] + 1)
        short = {k: [n for n in span if state[k][n] < opt[n]] for k in PASSES}
        points = {k: sum(opt[n] - state[k][n] for n in span) for k in PASSES}
        closed_in[streak[0]] = next((k for k in PASSES if k > 1 and not short[k]), None)
        cells = " | ".join(f"{len(short[k])} games, {points[k]}" if short[k] else "0" for k in (2, 3, 4))
        print(f"| {name_of(streak)} | {len(span)} | {points[1]} | {streak[0]} | {layer[streak[0]]} | {cells} "
              f"| {closed_in[streak[0]] or 'not'} |")
    left = [sum(any(state[k][n] < opt[n] for n in range(s[0], s[1] + 1)) for s in first) for k in PASSES]
    print(f"\nPass 1's {len(first)} streaks, left after each pass (any game short): {left}")
    print("Closed in each pass, of those left before it: "
          + ", ".join(f"pass {k}: {left[k - 2] - left[k - 1]} of {left[k - 2]}" for k in PASSES if k > 1))
    print("\n| closed in | streaks | games a streak (mean, median) | points short a streak (mean, median) "
          "| points short a game |")
    print("|---|---|---|---|---|")
    for label, keep in (("pass 2", 2), ("pass 3", 3), ("not", None), ("all", False)):
        group = [s for s in first if keep is False or closed_in[s[0]] == keep]
        size = [s[1] - s[0] + 1 for s in group]
        short = [sum(opt[n] - state[1][n] for n in range(s[0], s[1] + 1)) for s in group]
        print(f"| {label} | {len(group)} | {statistics.mean(size):.1f}, {statistics.median(size):g} "
              f"| {statistics.mean(short):.0f}, {statistics.median(short):g} | {sum(short) / sum(size):.0f} |")
    return closed_in


def starts(last, state, opt, layer, closed_in):
    """Where the streaks of pass 1 start: the games a search leaves below the ceiling, and the roots among them."""
    print("\n## Where the streaks start\n")
    line = last[1]

    def kind(n):
        if line[n]["method"] != "search":
            return line[n]["method"]
        below_it = line[n - 1]["score"] if n > LO else opt[n - 1]
        return "searched at the ceiling" if line[n]["score"] == below_it + n else "searched below the ceiling"

    kinds = {n: kind(n) for n in GAMES}
    at_flag = {n for n in GAMES if line[n]["method"] == "search" and line[n]["at_ceiling"]}
    print(f"Pass 1's lines by kind of game: {dict(sorted(Counter(kinds.values()).items()))}")
    print(f"The searched games at the ceiling by score(n - 1) + n are the lines' at_ceiling ones: "
          f"{at_flag == {n for n in GAMES if kinds[n] == 'searched at the ceiling'}}")
    candidates = {n for n in GAMES if kinds[n] == "searched below the ceiling"}
    short = [n for n in GAMES if state[1][n] < opt[n]]
    roots = [n for n in short if n == LO or state[1][n - 1] == opt[n - 1]]
    print(f"Pass 1's short games: {len(short)}; roots (short while n - 1 is at opt(n - 1)): {len(roots)}, "
          f"the first games of the streaks: {roots == [s[0] for s in streaks(short)]}")
    print(f"Searched games below the ceiling: {len(candidates)}; roots among them: "
          f"{len(candidates.intersection(roots))} of {len(roots)}; roots outside them: "
          f"{[n for n in roots if n not in candidates]}")
    followers = Counter(kinds[n] for n in short if n not in roots)
    print(f"Followers (short, with n - 1 short): {sum(followers.values())}, by kind {dict(sorted(followers.items()))}")
    print("\n| layer of n | games | primes | repeats | searched at the ceiling | searched below the ceiling "
          "| roots | roots per 100 below the ceiling |")
    print("|---|---|---|---|---|---|---|---|")
    for label, keep in (("1", lambda o: o == 1), ("2", lambda o: o == 2), ("3", lambda o: o == 3),
                        ("4", lambda o: o == 4), ("5 or more", lambda o: o >= 5), ("all", lambda o: True)):
        here = [n for n in GAMES if keep(layer[n])]
        count = [sum(kinds[n] == k for n in here) for k in
                 ("prime", "repeat", "searched at the ceiling", "searched below the ceiling")]
        hits = sum(n in candidates for n in here if n in roots)
        print(f"| {label} | {len(here)} | " + " | ".join(map(str, count)) + f" | {hits} "
              f"| {100 * hits / count[3] if count[3] else 0:.2f} |")
    print("\n| root | layer | points short | rounds | stopped | pushed | growth | trajectories | closed in pass |")
    print("|---|---|---|---|---|---|---|---|---|")
    for n in roots:
        print(f"| {n} | {layer[n]} | {opt[n] - line[n]['score']} | {line[n]['rounds']} | {line[n]['growth_stop']} "
              f"| {line[n]['pushed']} | {line[n]['growth']} | {len(line[n]['trajectories'])} "
              f"| {closed_in[n] or 'not'} |")
    searched = [line[n] for n in candidates]
    print(f"\nThe {len(candidates)} searched games below the ceiling: stopped "
          f"{sum(g['growth_stop'] for g in searched)}, pushed {sum(g['pushed'] for g in searched)}")
    for label, group in (("stopped", [n for n in roots if line[n]["growth_stop"]]),
                         ("not stopped", [n for n in roots if not line[n]["growth_stop"]])):
        print(f"Roots {label}: {len(group)}, closed in pass 2: {sum(closed_in[n] == 2 for n in group)}, "
              f"in pass 3: {sum(closed_in[n] == 3 for n in group)}, not: {sum(closed_in[n] is None for n in group)}")


def hours():
    """The thread-hours of each pass, from the wall-clock and from the games' seconds in the logs."""
    print("\n## Thread-hours\n")
    print("| pass | wall-clock s | thread-hours (wall x 44) | games' seconds in the log | repair s "
          "| thread-hours (log seconds x 44) | log over wall |")
    print("|---|---|---|---|---|---|---|")
    wall, total = wall_seconds(), [0.0, 0.0]
    for k in PASSES:
        games, repair, _ = log_seconds(k)
        by_wall, by_log = wall[k] * THREADS / 3600, (games + repair) * THREADS / 3600
        total = [total[0] + by_wall, total[1] + by_log]
        print(f"| {k} | {wall[k]} | {by_wall:.1f} | {games:.0f} | {repair:.0f} | {by_log:.1f} "
              f"| {by_log / by_wall:.3f} |")
    print(f"| all | {sum(wall.values())} | {total[0]:.1f} | | | {total[1]:.1f} | {total[1] / total[0]:.3f} |")


def main():
    with gzip.open(RESULTS, "rt") as f:
        opt = {line["n"]: line["score"] for line in map(json.loads, f)}
    passes = {k: read_lines(f"p{k}.jsonl.gz") for k in PASSES}
    last = {k: last_lines(lines) for k, lines in passes.items()}
    state = {0: {}}
    for k in PASSES:
        state[k] = {n: max(state[k - 1].get(n, 0), last[k][n]["score"]) for n in GAMES}
    checks(passes, last, read_lines("best-known.jsonl.gz"), state, opt)
    layer = layers()
    table(passes, last, state, opt)
    closed_in = survival(state, opt, layer)
    starts(last, state, opt, layer, closed_in)
    hours()


if __name__ == "__main__":
    main()
