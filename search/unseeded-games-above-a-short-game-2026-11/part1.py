#!/usr/bin/env python3
"""Part 1 of study B11: games played unseeded against the same games played from the proven game below.

    python3 -I part1.py [DIR [R1]]

DIR (default: this script's folder) holds games-above.txt, games-p1.txt and part1/, the arms of run_games.py, a file an
arm: u4.jsonl.gz and u7.jsonl.gz (unseeded at efforts 4 and 7), s4.jsonl.gz (from the proven game of n - 1 at effort
4).  R1 (default: the notebook's entry of race R1) is race R1's folder, whose arm K25W4 (k25w4-*.jsonl) played its
hard games from the proven game below at effort 7, with the same options; it stands in for the seeded arm on its games
(below).  Every line has `--stop-at-known`, so it says whether the game reached opt(n) and after how much work.

A level runs the rounds of every level below it first, and with `--stop-at-known` a game ends at the same round
whatever its level, once it reaches opt(n).  So a game at opt(n) at effort 4 is at opt(n) at effort 7 with the same
line, and the arm of effort 7 plays only the games that effort 4 misses.  A line of effort 7 settles effort 4 when the
improvement that reached opt(n) has no more work than effort 4's budget (reached), or when the work before that
improvement's round is at least the budget, as it is when its work less more than a round's is (missed); else s4
plays the game.

Prints a row a game: opt(n), and for each arm the work at which it reached opt(n), or how far short it ended; then
the counts of each group of games.
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optlib import last_lines, opt_scores  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(HERE, "..", "a-share-of-tilted-neighborhoods-2026-11")
BUDGET = {4: 8 * 65536, 7: 64 * 65536}
# More work than a round takes: 64 neighborhoods of 32 work and their steps, which pass the unit's limit of 1,024 by
# less than another 1,024 (the engine looks at the limit after each block of 1,024 steps).
ROUND_MOST = 64 * (2 * 1024 + 32)


def arm(path):
    """The lines of an arm's file, by n; none if there is no file."""
    lines = {}
    if os.path.exists(path):
        with gzip.open(path, "rt") as f:
            for text in f:
                line = json.loads(text)
                lines[line["n"]] = line
    return lines


def reached(line):
    """The work at which the line reached the known score, or None if it did not."""
    known = line["stop_at_known"]
    if known["round"] is None:
        return None
    if known["round"] == 0:
        return 0
    return next(r["work"] for r in line["improvements"] if r["score"] >= known["known"])


def at_effort(line, effort):
    """Whether a line of `effort` or a higher one reached opt(n) within `effort`'s budget: True, False, or None when
    the line does not settle it."""
    work = reached(line)
    if line["effort"] == effort:
        return work is not None
    if work is not None and work <= BUDGET[effort]:
        return True
    if work is None or work - ROUND_MOST >= BUDGET[effort]:
        return False
    return None


def score_at(line, effort):
    """The line's score at `effort`: its own at its effort; from a line of a higher effort, the best of its start and
    of the improvements whose work is within `effort`'s budget, which the rounds of `effort` reach at least."""
    if line["effort"] == effort:
        return line["score"]
    within = [r["score"] for r in line["improvements"] if r["work"] <= BUDGET[effort]]
    return max([line["start"], *within])


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else HERE
    r1_folder = sys.argv[2] if len(sys.argv) > 2 else R1
    opt = opt_scores()
    runs = {name: arm(os.path.join(folder, "part1", f"{name}.jsonl.gz")) for name in ("u4", "u7", "s4")}
    r1 = {}
    for part in range(6):
        r1.update(last_lines(os.path.join(r1_folder, f"k25w4-{part}.jsonl")))
    games_above = [int(x) for x in open(os.path.join(folder, "games-above.txt"))]
    games_p1 = [int(x) for x in open(os.path.join(folder, "games-p1.txt")) if x.strip()]

    def cell(lines, n, effort):
        """The arm's result at `effort`: (at opt(n), text)."""
        line = lines.get(n)
        if line is None:
            return None, "?"
        ok = at_effort(line, effort)
        if ok:
            return True, f"{reached(line):>8}"
        if ok is None:
            return None, "?"
        return False, f"{'-' + str(opt[n] - score_at(line, effort)):>8}"

    def unseeded(n, effort):
        # At effort 7, a game that effort 4 brought to opt(n) has effort 4's line.
        if effort == 4 or (n in runs["u4"] and at_effort(runs["u4"][n], 4)):
            return cell(runs["u4"], n, 4)
        return cell(runs["u7"], n, 7)

    def seeded(n, effort):
        if effort == 4 and n in runs["s4"]:
            return cell(runs["s4"], n, 4)
        if n in r1:
            return cell(r1, n, effort)
        # A game that effort 4 brought to opt(n) has effort 4's line at effort 7.
        if n in runs["s4"] and at_effort(runs["s4"][n], 4):
            return cell(runs["s4"], n, 4)
        return None, "?"

    print("A cell is the work at which the game reached opt(n), or -S if it ended S short; ? if not played.")
    print(f"{'n':>5} {'opt(n)':>9} | {'seeded e4':>9} {'e7':>8} | {'unseeded e4':>11} {'e7':>8} | groups")
    groups = {"4951-4970": range(4951, 4971), "4915-4934": range(4915, 4935), "P1's 63": games_p1}
    arms = ("s4", "s7", "u4", "u7")
    counts = {(g, a): 0 for g in groups for a in arms}
    played = {(g, a): 0 for g in groups for a in arms}
    for n in sorted(set(games_above) | set(games_p1)):
        results = {"s4": seeded(n, 4), "s7": seeded(n, 7), "u4": unseeded(n, 4), "u7": unseeded(n, 7)}
        member = [g for g, games in groups.items() if n in games]
        for g in member:
            for a, (ok, _) in results.items():
                if ok is not None:
                    played[(g, a)] += 1
                    counts[(g, a)] += ok
        texts = {a: text for a, (_, text) in results.items()}
        print(f"{n:>5} {opt[n]:>9} | {texts['s4']:>9} {texts['s7']:>8} | {texts['u4']:>11} {texts['u7']:>8} | "
              f"{', '.join(member)}")
    print()
    print(f"{'games':<10} | at opt(n): seeded e4, e7 | unseeded e4, e7 (of the games each settles)")
    for g in groups:
        row = " ".join(f"{counts[(g, a)]}/{played[(g, a)]}" for a in ("s4", "s7"))
        row2 = " ".join(f"{counts[(g, a)]}/{played[(g, a)]}" for a in ("u4", "u7"))
        print(f"{g:<10} | {row:>24} | {row2}")


if __name__ == "__main__":
    main()
