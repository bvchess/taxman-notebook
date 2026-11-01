#!/usr/bin/env python3
"""Phase A of the gate study: the CPU of the gate trial's 24 units under each gate, game by game, and what it projects
for the whole chain.

Reads the trial lines that phase A's searches wrote to stderr (phase-a-trial-lines.txt, made by
`grep -h "gate trial" a-*.err | sort -t= -k2 -n`) and the weights, each game's own search hours in the original chain
(`seconds.own`, else `seconds.search`, of its line in results/optimal.jsonl.gz).  Prints

  1. a row a game: its weight in hours, the step the trial ran at, and its CPU under each gate as a ratio to the gate of
     1,200, with the gate the trial kept;
  2. the weighted mean of each gate's ratio over the games: the projection of a fixed gate;
  3. the weighted mean of the ratio of the gate that a trial over a set of gates keeps, taking the gate of least CPU
     only if it is at least 3% under the gate of 1,200 (the solver's rule), and with no margin.

usage: phase_a.py [TRIAL_LINES [RESULTS]]
TRIAL_LINES defaults to phase-a-trial-lines.txt beside this script; RESULTS to the environment variable TAXMAN_RESULTS,
the path of results/optimal.jsonl.gz of the main repository (at commit 7a856a3 for the numbers of the entry)."""
import gzip
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 1200
MARGIN = 0.03
TRIAL_SETS = {
    "1200..600": (1200, 1000, 800, 600),
    "all eight": (2000, 1200, 1000, 800, 600, 400, 300, 150),
}
PIECE = re.compile(r"(\d+) ([\d.]+) s \((\d+) steps, (\d+) stopped\)")
KEPT = re.compile(r"the gate is (\d+) from now on|the gate stays (\d+)")


def weights(results):
    """Each game's own search hours in the original chain."""
    hours = {}
    with gzip.open(results, "rt") as lines:
        for line in lines:
            game = json.loads(line)
            seconds = game["seconds"]
            hours[game["n"]] = (seconds.get("own") or seconds["search"]) / 3600
    return hours


def trials(path):
    """Game -> (step the trial ran at, {gate: CPU seconds}, the gate it kept)."""
    found = {}
    for line in open(path):
        if "gate trial" not in line:
            continue
        game = int(re.match(r"n=(\d+)", line).group(1))
        steps = int(re.search(r"gate trial at (\d+) steps", line).group(1))
        cpu = {int(gate): float(seconds) for gate, seconds, _, _ in PIECE.findall(line.split("CPU by gate ")[1])}
        kept = KEPT.search(line)
        found[game] = (steps, cpu, int(kept.group(1) or kept.group(2)))
    return found


def kept_gate(cpu, gates, margin):
    """The gate of least CPU among GATES, if it is under the gate of 1,200 by the margin; else 1,200."""
    best = min(gates, key=lambda gate: cpu[gate])
    return best if cpu[best] < (1 - margin) * cpu[BASE] else BASE


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "phase-a-trial-lines.txt")
    results = sys.argv[2] if len(sys.argv) > 2 else os.environ["TAXMAN_RESULTS"]
    hours = weights(results)
    found = trials(path)
    games = sorted(found)
    total = sum(hours[n] for n in games)
    gates = sorted(found[games[0]][1])
    others = [gate for gate in gates if gate != BASE]
    print(f"{len(games)} games, {total:.1f} hours of the original chain's own search")
    print()
    print("CPU of the trial's 24 units under each gate, over the gate of 1,200; kept: the gate the search kept")
    print(f"{'game':>5} {'hours':>6} {'at (M)':>7} " + " ".join(f"{gate:>6}" for gate in others) + "   kept")
    for n in games:
        steps, cpu, kept = found[n]
        row = " ".join(f"{cpu[gate] / cpu[BASE]:6.3f}" for gate in others)
        print(f"{n:5d} {hours[n]:6.1f} {steps / 1e6:7.1f} {row}   {kept}")
    print()
    print("A fixed gate: the mean of its ratios over the games, weighted by hours; games under 1.000")
    for gate in gates:
        mean = sum(hours[n] * found[n][1][gate] / found[n][1][BASE] for n in games) / total
        under = sum(found[n][1][gate] < found[n][1][BASE] for n in games)
        print(f"  gate {gate:>5}: {mean:.3f}   {under:2d} of {len(games)}")
    print()
    print("A trial that keeps the gate of least CPU of its set, over the same units")
    for name, gates_tried in TRIAL_SETS.items():
        for margin in (MARGIN, 0.0):
            mean = sum(
                hours[n] * found[n][1][kept_gate(found[n][1], gates_tried, margin)] / found[n][1][BASE] for n in games
            ) / total
            print(f"  over {name}, margin {margin:.0%}: {mean:.3f}")
    mean = sum(hours[n] * found[n][1][found[n][2]] / found[n][1][BASE] for n in games) / total
    print(f"  as the searches kept it (all eight, margin {MARGIN:.0%}): {mean:.3f}")
    tally = Counter(found[n][2] for n in games)
    print("  the gates the searches kept: " + ", ".join(f"{gate} on {count}" for gate, count in sorted(tally.items())))
    print()
    heavy = sorted(games, key=lambda n: -hours[n])[:2]
    share = sum(hours[n] for n in heavy) / total
    print(f"The two heaviest games, {heavy[0]} and {heavy[1]}, hold {share:.1%} of the weight")


if __name__ == "__main__":
    main()
