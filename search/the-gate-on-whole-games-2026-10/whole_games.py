#!/usr/bin/env python3
"""The whole-game runs of the gate study, side by side with the lines of the same games in the chain's re-run and in
the original chain.

Prints, from the last line of the game in each run's out.jsonl (folders b/, c/ and d/ of STUDY_DIR), then the lines of
the same games in the re-run's results file and in the original chain's, and then each fixed-gate run over the run it
replaces, in own hours and in nodes.  A game's hours are `seconds.own`, else `seconds.search`.

usage: whole_games.py
Environment variables: STUDY_DIR, the folder of the study's runs (default: beside this script); RERUN_RESULTS, the
re-run's results file (strict.jsonl of its data folder); TAXMAN_RESULTS, results/optimal.jsonl.gz of the main repository
(at commit 7a856a3 for the numbers of the entry)."""
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.environ.get("STUDY_DIR", HERE)
# (the fixed-gate run, what it replaces): another run of the study, or the re-run's line of the game.
PAIRS = [
    ("c/4875-g300", "c/4875-default"),
    ("c/4879-g300", "c/4879-default"),
    ("c/4893-g300", "c/4893-default"),
    ("c/5052-g300", "c/5052-default"),
    ("b/4875-g300", "rerun"),
    ("d/3942-g300", "rerun"),
    ("d/4192-g300", "rerun"),
    ("d/3441-g300", "rerun"),
]


def hours(line):
    seconds = line["seconds"]
    return (seconds.get("own") or seconds["search"]) / 3600


def last_lines(path, wanted=None):
    """The last line of each game in a JSON-lines file (of the games WANTED, if given)."""
    last = {}
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as lines:
        for text in lines:
            if not text.strip():
                continue
            line = json.loads(text)
            if wanted is None or line["n"] in wanted:
                last[line["n"]] = line
    return last


def describe(line):
    """(completed, hours, nodes in millions, gate, the gate the trial kept) of a result line."""
    options = line.get("options") or {}
    trial = (line.get("engine") or {}).get("gate_trial") or {}
    return (
        bool(line.get("completed")),
        hours(line),
        (line.get("nodes") or 0) / 1e6,
        options.get("gate", "default"),
        trial.get("chosen", "-"),
    )


def main():
    runs = {}
    named = {run for pair in PAIRS for run in pair if "/" in run}
    for run in sorted(named | {"c/4875-g150", "c/4984-g300", "c/4984-default"}):
        game = int(re.search(r"/(\d+)-", run).group(1))
        runs[run] = (game, last_lines(os.path.join(STUDY, run, "out.jsonl"), {game})[game])
    games = {game for game, _ in runs.values()}
    rerun = last_lines(os.environ["RERUN_RESULTS"], games)
    chain = last_lines(os.environ["TAXMAN_RESULTS"], games)

    print("Runs of the study (all 88 threads, the re-run's build; c/ runs were capped at 10,800 s)")
    print(f"{'run':<16} {'done':<5} {'own h':>6} {'nodes M':>8}  gate     trial kept")
    for run, (game, line) in sorted(runs.items()):
        done, own, nodes, gate, kept = describe(line)
        print(f"{run:<16} {'yes' if done else 'no':<5} {own:6.3f} {nodes:8.1f}  {gate!s:<8} {kept}")
    print()
    print("The same games in the re-run (tag rerun-2026-10, commit 3ca11bf; its last line of the game)")
    print(f"{'game':<6} {'done':<5} {'own h':>6} {'nodes M':>8}  gate     trial kept")
    for game in sorted(games & set(rerun)):
        done, own, nodes, gate, kept = describe(rerun[game])
        print(f"{game:<6} {'yes' if done else 'no':<5} {own:6.3f} {nodes:8.1f}  {gate!s:<8} {kept}")
    print()
    print("The same games in the original chain (results/optimal.jsonl.gz; builds and thread counts differ)")
    print(f"{'game':<6} {'own h':>6} {'nodes M':>8}  {'build':<8} threads")
    for game in sorted(games & set(chain)):
        line = chain[game]
        build = line["build"]["commit"][:7]
        print(f"{game:<6} {hours(line):6.3f} {line['nodes'] / 1e6:8.1f}  {build:<8} {line['threads']}")
    print()
    print("A fixed gate of 300 over the run it replaces (a < means the other run stopped at its cap: an upper bound)")
    print(f"{'fixed gate':<14} {'against':<15} {'hours':>7} {'nodes':>7}")
    for fixed, other in PAIRS:
        game, line = runs[fixed]
        _, own, nodes, _, _ = describe(line)
        if other == "rerun":
            label, base = "re-run", rerun[game]
        else:
            label, base = other, runs[other][1]
        done, base_own, base_nodes, _, _ = describe(base)
        bound = " " if done else "<"
        print(f"{fixed:<14} {label:<15} {bound}{own / base_own:6.3f} {bound}{nodes / base_nodes:6.3f}")


if __name__ == "__main__":
    main()
