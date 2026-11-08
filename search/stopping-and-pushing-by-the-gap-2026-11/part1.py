#!/usr/bin/env python3
"""Part 1 of study B13: the stop rule and the push rule simulated on the existing lines.

    python3 -I part1.py

The bound of n is the parity bound; a line's gap is its bound less its score, and its growth its gap less the gap of the
line of n − 1 the game started from (b13lib.py; the study's question calls the growth the step).  Prints:

* the growth of the proven games (the committed results);
* the growth of the games that start a streak of short games, and of the games at opt(n), in E2's 45 runs;
* the stop rule: a searched game stops at the first point, the end of its start or of a round that raised its score,
  where its growth is at most T.  A stop after the game's last gain leaves its line as it is and saves the rest of its
  work; a stop before it changes the line, and counts as a loss.  For each level and T: the share of the work saved,
  and the games whose line would change;
* the push rule: the games whose growth after the level's budget (the seeded play's final score) exceeds T, against
  the games that start a streak (by the game's last line), the other short games, and the games at opt(n).

The chains: E2's 30 runs at levels 1 to 6 (old efforts 2 to 7, five segments of 100 games each), and B11's four chains
of Part 2 at level 3 (old effort 4).  A game is short if its last line scores below opt(n).
"""

import glob
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import B11, E2, games_of, gap_before, growth_of, opt_scores, parity_bounds, streaks  # noqa: E402

STOP_T = [-50, -25, 0, 25, 50]
PUSH_T = [0, 50, 100, 200]


def chains():
    """(level, name, path) of the chains of Part 1."""
    found = []
    for effort in range(2, 8):
        for path in sorted(glob.glob(f"{E2}/e{effort}-*.jsonl.gz")):
            found.append((effort - 1, os.path.basename(path), path))
    for path in sorted(glob.glob(f"{B11}/*.jsonl.gz")):
        found.append((3, "b11/" + os.path.basename(path), path))
    return found


def proven_growth(opt, bounds):
    print("## The growth of the proven games")
    growth = {n: (bounds[n] - opt[n]) - (bounds[n - 1] - opt[n - 1]) for n in range(1001, 5061)}
    window = [growth[n] for n in range(3001, 5061)]
    share = lambda test: 100 * sum(1 for s in window if test(s)) / len(window)  # noqa: E731
    print(f"3001-5060: {len(window)} games; growth 0 on {share(lambda s: s == 0):.1f}%, below 0 on "
          f"{share(lambda s: s < 0):.1f}%, above 0 on {share(lambda s: s > 0):.1f}%")
    for t in [0, 25, 50, 100, 200, 300]:
        print(f"  above {t}: {share(lambda s: s > t):.2f}%   below {-t}: {share(lambda s: s < -t):.2f}%")
    print(f"1001-5060: the largest growth {max(growth.values())} (n={max(growth, key=growth.get)}), the least "
          f"{min(growth.values())} (n={min(growth, key=growth.get)})")
    print()


def e2_starts(opt, bounds):
    print("## E2's 45 runs: the growth of the games that start a streak, and of the games at opt(n)")
    starts, at_opt = [], []
    for path in sorted(glob.glob(f"{E2}/e*-*.jsonl.gz")):
        games = games_of(path, opt)
        short = {n: opt[n] - g.last["score"] for n, g in games.items()}
        for first, _, _ in streaks(games, short):
            starts.append(growth_of(games[first], games[first].played["score"], bounds))
        at_opt += [growth_of(g, g.played["score"], bounds) for n, g in games.items() if short[n] == 0]
    print(f"{len(starts)} streak starts: median {statistics.median(starts)}, from {min(starts)} to {max(starts)}, "
          f"{sum(1 for s in starts if s > 0)} above 0")
    print(f"{len(at_opt)} games at opt(n): growth from {min(at_opt)} to {max(at_opt)}")
    print()


def stop_point(game, t, bounds):
    """The work at which the stop rule at `t` stops the seeded play, and its score there; None if it never does."""
    score, _, improvements = game.seeded()
    line = game.played
    if line["method"] != "search" or improvements is None:
        return None
    first = max([line["start"]] + [i["score"] for i in improvements if i["round"] == 0])
    points = [(0, first)] + [(i["work"], i["score"]) for i in improvements if i["round"] > 0]
    for work, at in points:
        if growth_of(game, at, bounds) <= t:
            return work, at
    return None


def stop_rule(opt, bounds, levels):
    print("## The stop rule: stop at the first point where the growth is at most T")
    print("| level | chains | T | work of the chains | saved, line unchanged | lines changed (n: points lost) |")
    print("|---|---|---|---|---|---|")
    for level, paths in levels:
        everything = [games_of(path, opt) for path in paths]
        total = sum(g.played["work"] + (g.played["other"]["work"] if g.played.get("other") else 0)
                    for games in everything for g in games.values())
        for t in STOP_T:
            saved, changed, searched_unchanged = 0, [], 0
            for games in everything:
                for g in games.values():
                    stop = stop_point(g, t, bounds)
                    if stop is None:
                        continue
                    score, work, _ = g.seeded()
                    if stop[1] == score:
                        saved += work - stop[0]
                        searched_unchanged += 1
                    else:
                        changed.append(f"{g.n}: {score - stop[1]}")
            shown = ", ".join(changed[:12]) + (f", ... ({len(changed)})" if len(changed) > 12 else "")
            print(f"| {level} | {len(paths)} | {t} | {total / 1e6:.1f} M | {100 * saved / total:.1f}% "
                  f"({searched_unchanged} games) | {len(changed)}{': ' + shown if changed else ''} |")
    print()


def push_rule(opt, bounds, levels):
    print("## The push rule: the games whose growth after the level's budget exceeds T")
    print("| level | chains | T | streak starts flagged | other short games flagged | games at opt(n) flagged |")
    print("|---|---|---|---|---|---|")
    for level, paths in levels:
        rows = []
        for path in paths:
            games = games_of(path, opt)
            short = {n: opt[n] - g.last["score"] for n, g in games.items() if n in opt}
            firsts = {first for first, _, _ in streaks(short, short)}
            for n, g in games.items():
                if n not in short:
                    continue
                kind = "start" if n in firsts else "short" if short[n] > 0 else "opt"
                rows.append((kind, growth_of(g, g.seeded()[0], bounds), g.played["method"], n, path))
        count = {kind: sum(1 for r in rows if r[0] == kind) for kind in ["start", "short", "opt"]}
        for t in PUSH_T:
            flagged = {kind: [r for r in rows if r[0] == kind and r[1] > t] for kind in count}
            starts = ", ".join(f"{r[3]} ({r[2]}, {r[1]})" for r in flagged["start"])
            print(f"| {level} | {len(paths)} | {t} | {len(flagged['start'])} of {count['start']}"
                  f"{': ' + starts if starts else ''} | {len(flagged['short'])} of {count['short']} | "
                  f"{len(flagged['opt'])} of {count['opt']} |")
        missed = [r for r in rows if r[0] == "start" and r[1] <= 0]
        if missed:
            print(f"|  | | streak starts with a growth of at most 0: "
                  f"{', '.join(f'{r[3]} ({r[2]}, {r[1]})' for r in missed)} | | |")
    print()


def main():
    opt, bounds = opt_scores(), parity_bounds()
    proven_growth(opt, bounds)
    e2_starts(opt, bounds)
    by_level = {}
    for level, name, path in chains():
        by_level.setdefault((level, "b11" if name.startswith("b11") else "e2"), []).append(path)
    levels = [(f"{level} ({source})", paths) for (level, source), paths in sorted(by_level.items())]
    stop_rule(opt, bounds, levels)
    push_rule(opt, bounds, levels)
    # The gap of the line below at each streak start, against the gap of the proven game below.
    print("## The streak starts of the chains of Part 1: n, method, growth, gap below, gap of the proven game below")
    for level, paths in levels:
        for path in paths:
            games = games_of(path, opt)
            short = {n: opt[n] - g.last["score"] for n, g in games.items() if n in opt}
            for first, length, size in streaks(short, short):
                g = games[first]
                print(f"{level} {os.path.basename(path)}: {first} ({g.played['method']}, {length} games, {size} "
                      f"short): growth {growth_of(g, g.seeded()[0], bounds)}, gap below {gap_before(g, bounds)}, "
                      f"proven gap below {bounds[first - 1] - opt[first - 1]}")


if __name__ == "__main__":
    main()
