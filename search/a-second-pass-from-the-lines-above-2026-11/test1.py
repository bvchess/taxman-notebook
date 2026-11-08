#!/usr/bin/env python3
"""Test 1: a second pass from the best-known lines, with and without `--above 8`, on the known range's misses.

    python3 -I test1.py > out.txt

Reads start.jsonl.gz (the best-known file that fold.sh made for 3001-5060) and, for each arm `a` and `b`, the lines
`w*.jsonl.gz` and logs `w*.log` of arms.sh's windows and the arm's best-known file `best-known.jsonl.gz` after the
pass.  A game's line is the last line a file has for it (a line the repair wrote again replaces it), its *played* line
the first.  The *misses* are the games of start.jsonl below opt(n).  Prints:

1. the checks of every line;
2. the fold: the games at opt(n) of start.jsonl, the chains whose lines it keeps, the misses and their streaks;
3. each arm: the misses it closed, the points still short, the work and the seconds, the known range's games at opt(n);
4. each streak of misses in each arm: whether it closed, and the games whose lines a search made, with the source;
5. the lines of arm b that closed a streak's first game: the trajectories, the improvements, and the score the lines
   above held;
6. every game a window raised, by what made its line.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEARCH = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(SEARCH, "stopping-and-pushing-by-the-gap-2026-11"))
from b13lib import PARITY, opened, opt_scores, parity_bounds, streaks  # noqa: E402

COMMIT = "928ad6a"
LO, HI = 3001, 5060
KNOWN_TO = 3000
ARMS = {"a": 0, "b": 8}  # the arm's `--above`
SEED, THREADS, EFFORT = 2, 22, 3


def read_lines(path):
    with opened(path) as f:
        return [json.loads(text) for text in f if text.strip()]


def games_of(lines, where):
    """(played, last) by n: a game's first line and its last, which must score at least as much as any before it."""
    played, last = {}, {}
    for line in lines:
        n = line["n"]
        if n in last and line["score"] < last[n]["score"]:
            raise SystemExit(f"{where}: n={n}: a line scores {line['score']} after one of {last[n]['score']}")
        played.setdefault(n, line)
        last[n] = line
    return played, last


def window_of(path):
    """(first, last) game of a window, from its file's name `wFIRST-LAST.jsonl.gz`."""
    first, last = re.match(r"w(\d+)-(\d+)\.", os.path.basename(path)).groups()
    return int(first), int(last)


class Arm:
    """One arm: its windows' lines and logs, and its best-known file after the pass."""

    def __init__(self, name, above):
        self.name, self.above = name, above
        self.windows = sorted(window_of(p) for p in glob.glob(os.path.join(HERE, name, "w*.jsonl.gz")))
        self.played, self.last, self.lines = {}, {}, []
        self.repair_seconds, self.repaired_lines, self.added = 0.0, 0, 0
        for first, last in self.windows:
            stem = os.path.join(HERE, name, f"w{first}-{last}")
            lines = read_lines(f"{stem}.jsonl.gz")
            ns = {line["n"] for line in lines}
            if ns != set(range(first, last + 1)):
                raise SystemExit(f"{stem}: games {min(ns)}-{max(ns)}, not {first}-{last}")
            played, final = games_of(lines, stem)
            self.played.update(played)
            self.last.update(final)
            self.lines += lines
            with open(f"{stem}.log") as f:
                text = f.read()
            found = re.search(r"repaired (\d+) lines; the repair took ([\d.]+) s", text)
            self.repaired_lines += int(found.group(1))
            self.repair_seconds += float(found.group(2))
            self.added += int(re.search(r"(\d+) lines added", text).group(1))
        self.best = games_of(read_lines(os.path.join(HERE, name, "best-known.jsonl.gz")), name)[1]
        self.left = {}

    def work(self):
        """The work of the played lines, both plays of a game played twice."""
        return sum(p["work"] + (p["other"]["work"] if p.get("other") else 0) for p in self.played.values())

    def seconds(self):
        return sum(p["seconds"] for p in self.played.values())


def check_window_lines(arm, opt, bounds):
    """Every line of the arm's windows: unsound, the build and the options, the bound, no score above it or opt(n)."""
    problems = []
    for line in arm.lines:
        n = line["n"]
        if not line.get("unsound"):
            problems.append(f"n={n}: not unsound")
        if line["build"]["commit"][:7] != COMMIT or line["build"]["dirty"]:
            problems.append(f"n={n}: build {line['build']}")
        for key, want in (("effort", EFFORT), ("seed", SEED), ("threads", THREADS), ("known_to", KNOWN_TO),
                          ("stop_growth", None), ("above", arm.above), ("from_known", False),
                          ("stop_at_known", None), ("repair", True)):
            if line[key] != want:
                problems.append(f"n={n}: {key} {line[key]}, not {want}")
        if line["bound"] != bounds[n]:
            problems.append(f"n={n}: bound {line['bound']}, the parity bound {bounds[n]}")
        if line["score"] > min(bounds[n], opt[n]):
            problems.append(f"n={n}: score {line['score']} above the bound {bounds[n]} or opt {opt[n]}")
        if line["prev"] is not None and line["prev"]["source"] not in ("run", "best_known"):
            problems.append(f"n={n}: prev.source {line['prev']['source']}")
    return problems


def source_of(line):
    """What made the moves of a game's final line in a window: (kind, game).  `kind` is `repair` (the repair wrote the
    line again, from `game`), `repeat` or `prime` (a line that plays no rounds), `start` (no round raised the start, or
    the start's own trajectory did), or `below` or `above` (the trajectory of the last improvement began from the
    survivors of the line of `game`)."""
    n = line["n"]
    if line["repaired"] is not None:
        return "repair", line["repaired"]["from"]
    if line["method"] != "search":
        return line["method"], line["repeats"]
    if not line["improvements"]:
        return "start", None
    source = line["trajectories"][line["improvements"][-1]["trajectory"]]
    if source == "start":
        return "start", None
    return ("above" if source > n else "below"), source


def is_root(line):
    """Whether a search of the game's own, or the repair, made its line: a repeat, a prime, and a search that raised
    nothing past its start (the line of the game below, already raised) follow."""
    return line["repaired"] is not None or (line["method"] == "search" and bool(line["improvements"]))


def describe(line):
    """The source of a line in words, with the round of its last improvement and whether it is an unseeded play's."""
    kind, game = source_of(line)
    text = kind if game is None else f"{kind} {game}"
    if line["method"] == "search" and line["improvements"]:
        text += f", round {line['improvements'][-1]['round']}"
    return text + (", unseeded play" if line["unseeded"] else "")


def checks(start_lines, start_last, arms, opt, bounds):
    print("## The checks\n")
    problems, notes = [], []
    for line in start_lines:
        n = line["n"]
        if not line.get("unsound") or line.get("best_known") is None:
            problems.append(f"start: n={n}: not an unsound line of a best-known file")
        if not LO <= n <= HI or line["score"] > min(bounds[n], opt[n]):
            problems.append(f"start: n={n}: out of range or above the bound or opt(n)")
    if sorted(start_last) != list(range(LO, HI + 1)):
        problems.append("start has not every game of 3001-5060")
    for name, arm in arms.items():
        problems += [f"{name}: {p}" for p in check_window_lines(arm, opt, bounds)]
        if sorted(arm.best) != list(range(LO, HI + 1)):
            problems.append(f"{name}: best-known has not every game of 3001-5060")
        for n, best in arm.best.items():
            if best["score"] < start_last[n]["score"]:
                problems.append(f"{name}: n={n}: best-known {best['score']} below start {start_last[n]['score']}")
        for n, line in arm.last.items():
            if max(line["score"], start_last[n]["score"]) != arm.best[n]["score"]:
                problems.append(f"{name}: n={n}: window {line['score']}, best-known {arm.best[n]['score']}")
            if line["score"] < start_last[n]["score"]:
                notes.append(f"{name}: n={n}: the window's line scores {line['score']}, "
                             f"{start_last[n]['score'] - line['score']} below start.jsonl's; the best-known file "
                             f"keeps start.jsonl's")
    print(f"{len(start_lines)} lines of start.jsonl.gz, "
          f"{sum(len(a.lines) for a in arms.values())} lines of the windows; problems: {len(problems)}")
    for p in problems:
        print(f"* {p}")
    for note in notes:
        print(f"* note: {note}")


def fold(start_last, opt):
    """Print the fold's numbers; returns the misses and their points short."""
    print("\n## The fold\n")
    counts = {}
    for n in range(LO, HI + 1):
        file = start_last[n]["best_known"]["file"]
        counts[file] = counts.get(file, 0) + 1
    print("Games whose line in start.jsonl is the last line of a chain, by the chain:\n")
    for file, count in sorted(counts.items(), key=lambda item: -item[1]):
        print(f"* {file}: {count}")
    short = {n: opt[n] - start_last[n]["score"] for n in range(LO, HI + 1)}
    for lo, hi in ((3001, 4000), (4001, 5060), (LO, HI)):
        at = sum(1 for n in range(lo, hi + 1) if short[n] == 0)
        print(f"\nstart.jsonl, {lo}-{hi}: {at} of {hi - lo + 1} games at opt(n), "
              f"{sum(short[n] for n in range(lo, hi + 1))} points short")
    misses = [n for n in range(LO, HI + 1) if short[n] > 0]
    print(f"\nThe {len(misses)} misses (n: points short): " + ", ".join(f"{n}: {short[n]}" for n in misses))
    found = streaks(range(LO, HI + 1), short)
    print(f"\nThe {len(found)} streaks of misses (first game, games): "
          + ", ".join(f"{first} ({length})" for first, length, _ in found))
    return short, misses, found


def at_opt(scores, opt, lo, hi):
    """The games of lo to hi whose score (by n) is opt(n)."""
    return sum(1 for n in range(lo, hi + 1) if scores[n] == opt[n])


def arms_table(arms, start_last, opt, short, misses, found):
    print("\n## The arms\n")
    print("| arm | `--above` | misses closed | streaks closed | points still short | M work | seconds "
          "| repair seconds | lines added to the best-known file | 3001-4000 at opt(n) | 4001-5060 at opt(n) "
          "| 3001-5060 at opt(n) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    scores = {"start.jsonl": {n: line["score"] for n, line in start_last.items()}}
    scores.update({name: {n: line["score"] for n, line in arm.best.items()} for name, arm in arms.items()})

    def at_cells(name):
        return " | ".join(f"{at_opt(scores[name], opt, lo, hi):,} of {hi - lo + 1:,}"
                          for lo, hi in ((3001, 4000), (4001, 5060), (LO, HI)))

    print(f"| start.jsonl | | 0 of {len(misses)} | 0 of {len(found)} | {sum(short[n] for n in misses)} | | | | "
          f"| {at_cells('start.jsonl')} |")
    closed = {}
    for name, arm in arms.items():
        arm.left = {n: opt[n] - arm.best[n]["score"] for n in misses}
        closed[name] = [n for n in misses if arm.left[n] == 0]
        streaks_closed = sum(1 for first, length, _ in found
                             if all(arm.left[n] == 0 for n in range(first, first + length)))
        print(f"| {name} | {arm.above} | {len(closed[name])} of {len(misses)} | {streaks_closed} of {len(found)} "
              f"| {sum(arm.left.values())} | {arm.work() / 1e6:.1f} | {arm.seconds():,.0f} "
              f"| {arm.repair_seconds:.1f} | {arm.added} | {at_cells(name)} |")
    print()
    for name, arm in arms.items():
        raised = [n for n in range(LO, HI + 1) if arm.best[n]["score"] > start_last[n]["score"]]
        print(f"* Arm {name}: games raised {len(raised)}, all misses: "
              f"{all(n in misses for n in raised)}; short still: "
              + ", ".join(f"{n}: {arm.left[n]}" for n in misses if arm.left[n] > 0)
              + f"; lines the repair wrote again: {arm.repaired_lines}; "
              f"{sum(1 for p in arm.played.values() if p['method'] == 'search')} of {len(arm.played)} games "
              f"searched, {sum(1 for p in arm.played.values() if p['pushed'])} pushed; "
              f"{arm.work() / max(1, len(closed[name])) / 1e6:.2f} M work for each miss closed")
        trajectories = [len(p["trajectories"]) for p in arm.played.values() if p["trajectories"]]
        print(f"* Arm {name}: {sum(trajectories) / len(trajectories):.1f} trajectories a searched game on average "
              f"({min(trajectories)} to {max(trajectories)})")
    both = [n for n in misses if n in closed["a"] and n in closed["b"]]
    only_b = [n for n in misses if n in closed["b"] and n not in closed["a"]]
    only_a = [n for n in misses if n in closed["a"] and n not in closed["b"]]
    neither = [n for n in misses if n not in closed["a"] and n not in closed["b"]]
    print(f"* Closed by both: {len(both)}; by a only: {len(only_a)}; by b only: {len(only_b)} {only_b}; "
          f"by neither: {len(neither)} {neither}")
    return closed


def streak_table(arms, found, short, start_last):
    print("\n## Each streak of misses\n")
    print("A game follows when its line is a repeat or a prime, or a search that raised nothing past its start (the "
          "line of the game below, already raised).  A *root* is a game whose line a search of its own raised: "
          "its source is the start's trajectory, a trajectory that began from the survivors of the line of a game "
          "below or above it, or the repair; the round is that of its last improvement.\n")
    print("| streak | games | points short at start | arm a | arm b |")
    print("|---|---|---|---|---|")
    roots = {name: [] for name in arms}
    for first, length, _ in found:
        ns = list(range(first, first + length))
        cells = []
        for name, arm in arms.items():
            left = sum(arm.left[n] for n in ns)
            raised = [n for n in ns if arm.best[n]["score"] > start_last[n]["score"]]
            made = [n for n in raised if is_root(arm.last[n])]
            roots[name] += made
            status = "closed" if left == 0 else (f"{left} short" if raised else "no gain")
            if left and raised:
                status = f"{len(raised)} of {length} raised, {left} short"
            what = "; ".join(f"{n}: {describe(arm.last[n])}" for n in made)
            cells.append(f"{status}" + (f" ({what})" if what else ""))
        print(f"| {first}{f'-{first + length - 1}' if length > 1 else ''} | {length} "
              f"| {sum(short[n] for n in ns)} | {cells[0]} | {cells[1]} |")
    return roots


def roots_table(arm, roots, start_last, opt):
    print("\n## The lines of arm b that closed a streak\n")
    print("For each: the trajectories of the line (the start, then the game whose survivors each began from), its "
          "improvements as `round: game of the trajectory, score`, and the best score of the survivors of the games "
          "above and below, against start.jsonl's line and opt(n).\n")
    print("| game | trajectories | improvements | best survivor above | best survivor below | start.jsonl | opt(n) |")
    print("|---|---|---|---|---|---|---|")
    for n in roots:
        line = arm.last[n]
        steps = ", ".join(f"{s['round']}: {line['trajectories'][s['trajectory']]}, {s['score']}"
                          for s in line["improvements"])
        survivors = line["survivor_scores"] or []
        above = [score for game, score in survivors if game > n]
        below = [score for game, score in survivors if game < n]
        print(f"| {n} | {line['trajectories']} | {steps} | {max(above)} | {max(below) if below else '-'} "
              f"| {start_last[n]['score']} | {opt[n]} |")
    holding = [n for n in roots if any(score == opt[n] for game, score in arm.last[n]["survivor_scores"] if game > n)]
    print(f"\nRoots where the survivors of a line above score opt(n) before any round: {len(holding)} {holding}")
    first_equal = [n for n in roots if arm.last[n]["improvements"][0]["round"] == 0
                   and arm.last[n]["improvements"][0]["score"] == start_last[n]["score"]]
    print(f"Roots whose round-0 improvement scores what start.jsonl's line of the game does: {len(first_equal)} "
          f"{first_equal}")
    kinds = {}
    for n in roots:
        kinds[source_of(arm.last[n])[0]] = kinds.get(source_of(arm.last[n])[0], 0) + 1
    print(f"Roots of arm b by the source of the last improvement: {kinds}")


def raised_table(arms, start_last):
    print("\n## What made the line of each game an arm raised\n")
    print("| arm | raised | roots from the start's trajectory | roots from a game below | roots from a game above "
          "| roots by the repair | followers |")
    print("|---|---|---|---|---|---|---|")
    for name, arm in arms.items():
        tally = {}
        for n in range(LO, HI + 1):
            if arm.best[n]["score"] > start_last[n]["score"]:
                kind = source_of(arm.last[n])[0] if is_root(arm.last[n]) else "follower"
                tally[kind] = tally.get(kind, 0) + 1
        print(f"| {name} | {sum(tally.values())} | {tally.get('start', 0)} | {tally.get('below', 0)} "
              f"| {tally.get('above', 0)} | {tally.get('repair', 0)} | {tally.get('follower', 0)} |")


def main():
    opt = opt_scores()
    bounds = parity_bounds(PARITY)
    start_lines = read_lines(os.path.join(HERE, "start.jsonl.gz"))
    start_last = games_of(start_lines, "start.jsonl.gz")[1]
    arms = {name: Arm(name, above) for name, above in ARMS.items()}
    checks(start_lines, start_last, arms, opt, bounds)
    short, misses, found = fold(start_last, opt)
    window_games = {n for arm in arms.values() for n in arm.last}
    print(f"\nGames in the windows: {len(window_games)}; misses outside them: "
          f"{[n for n in misses if n not in window_games] or 'none'}; the arms play the same games: "
          f"{all(set(arm.last) == window_games for arm in arms.values())}")
    arms_table(arms, start_last, opt, short, misses, found)
    roots = streak_table(arms, found, short, start_last)
    closed_roots = [n for n in roots["b"] if arms["b"].left[n] == 0]
    roots_table(arms["b"], closed_roots, start_last, opt)
    raised_table(arms, start_last)


if __name__ == "__main__":
    main()
