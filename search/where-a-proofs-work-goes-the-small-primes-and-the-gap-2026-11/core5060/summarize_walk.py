#!/usr/bin/env python3
"""Summarize the lines of `restricted smooth-tree --exact` (walk.jsonl) beside the plain search of each game.

Usage: summarize_walk.py WALKS.jsonl BASELINE.jsonl [RESULTS.jsonl.gz]

The plain search is BASELINE's line of the game (`fix-smooth N --smooth 1 --above opt(N)`: nothing fixed, the search
of the whole game from an incumbent worth opt(N), with no ceiling, seed, near-repeat cut or rule of symmetric pairs);
for a game it lacks, the chain's proof in RESULTS stands in.  For each walk it prints the game, B, the order, whether
the walk was whole or a sample of its frontier (and how many sampled subtrees the time limit cut, which makes the
estimates lower bounds), the tree's nodes and leaves, the leaves' search steps, any set found above the score to beat,
the bound checks, and the tree's CPU against the plain search's steps and CPU.
"""

import gzip
import json
import sys


def chain_lines(path: str, games: set[int]) -> dict[int, dict]:
    """The chain's proof of each game of `games`, as {'nodes', 'cpu'}, from the committed results file."""
    out = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            d = json.loads(line)
            if d["n"] in games:
                out[d["n"]] = {"nodes": d["nodes"], "cpu": d["seconds"]["cpu_all_runs"], "chain": True}
    return out


def main() -> None:
    walks = [json.loads(line) for line in open(sys.argv[1])]
    plain = {}
    for line in open(sys.argv[2]):
        d = json.loads(line)
        plain[d["n"]] = d
    missing = {w["n"] for w in walks} - set(plain)
    if len(sys.argv) > 3 and missing:
        plain.update(chain_lines(sys.argv[3], missing))
    for w in walks:
        base = plain.get(w["n"])
        whole = w["walked"] == w["frontier"] and not w.get("cut")
        nodes = w.get("est_nodes", w["nodes"])
        leaves = w.get("est_leaves", w["leaves"])
        cpu = w.get("est_tree_cpu", w["tree_cpu"])
        how = "whole" if whole else f"sample {w['walked']} of {w['frontier']}, {w.get('cut', 0)} cut"
        bound = "at least " if w.get("cut") else ""
        line = (f"n={w['n']} B={w['smooth']} part={w['smooth_part']} {'asc' if w.get('ascending') else 'desc'} {how}: "
                f"nodes {bound}{nodes:.3g}, leaves {bound}{leaves:.3g}, leaf steps {w['leaf_steps']} "
                f"(most {w['leaf_most']}), found {w['found']}, bound checks {w['checked']} differed {w['differed']}, "
                f"tree CPU {bound}{cpu:.3g} s")
        if base:
            what = "the chain's proof" if base.get("chain") else "plain search"
            ratio = cpu / max(base["cpu"], 1e-3)
            line += (f"; {what} {base['nodes']} steps, {base['cpu']:.0f} CPU s; "
                     f"nodes/steps {bound}{nodes / base['nodes']:.3g}, CPU ratio {bound}{ratio:.3g}")
        print(line)


if __name__ == "__main__":
    main()
