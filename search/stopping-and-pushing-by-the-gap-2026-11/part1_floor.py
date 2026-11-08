#!/usr/bin/env python3
"""Part 1 of study B13, the stop rule with a floor: no stop before the rounds of a lower budget have run.

    python3 -I part1_floor.py

A searched game at level L stops at the end of the rounds of the floor's budget, F, if its growth there is at most T,
else at the first gain after it whose growth is at most T.  The rounds of a lower budget are the first rounds of a
higher one, so the game's score and work at the end of F's rounds are those of its line at F, from E2's run of that
budget over the same segment: its *twin*, where the lines of n − 1 to n − 8 that the two games start from are the same
moves (the `prev.moves_digest` of the lines n − 7 to n agree) and both are searched.  The floors are old effort 1
(65,536 work, E2's `e1` runs) and level 1 (131,072, `e2`).  The chains are E2's runs at levels 2 to 6 (old efforts 3
to 7) and B11's Part 2 chains of 4861-5060 at level 3, whose twins are E2's runs of 4861-4960 and 4961-5060.  A game
with no twin is counted apart, and its work is not counted as saved.
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import B11, E2, games_of, growth_of, opt_scores, parity_bounds, segment_of  # noqa: E402

FLOORS = [(1, 65_536), (2, 131_072)]
STOP_T = [-25, 0, 25, 50]


def digest(game):
    prev = game.played.get("prev")
    return prev["moves_digest"] if prev else None


def twin_of(n, games, twins):
    """The twin of game n among `twins` (the games of the floor's runs), or None."""
    twin = twins.get(n)
    if twin is None or twin.played["method"] != "search" or games[n].played["method"] != "search":
        return None
    for k in range(n - 7, n + 1):
        if k in games and k in twins and digest(games[k]) != digest(twins[k]):
            return None
        if (k in games) != (k in twins):
            return None
    return twin


def stop(game, twin, t, bounds):
    """Where the stop rule with the floor of `twin` stops the game: (work, score), or None if it never does."""
    line = game.played
    score_at, work_at = twin.played["score"], twin.played["work"]
    # The rounds up to the floor are the twin's: the gains of the line up to its work are the twin's.
    early = [(i["work"], i["score"]) for i in line["improvements"] if i["work"] <= work_at]
    assert early == [(i["work"], i["score"]) for i in twin.played["improvements"]], (line["n"], early)
    if growth_of(game, score_at, bounds) <= t:
        return work_at, score_at
    for i in line["improvements"]:
        if i["work"] > work_at and growth_of(game, i["score"], bounds) <= t:
            return i["work"], i["score"]
    return None


def main():
    opt, bounds = opt_scores(), parity_bounds()
    arms = []
    for effort in range(3, 8):
        for path in sorted(glob.glob(f"{E2}/e{effort}-*.jsonl.gz")):
            arms.append((effort - 1, path, [segment_of(path)]))
    for path in sorted(glob.glob(f"{B11}/*-4861.jsonl.gz")):
        arms.append((3, path, ["4861", "4961"]))
    print("| level | chains | floor | T | work | saved, line unchanged | lines changed (n: points lost) | "
          "searched games with no twin |")
    print("|---|---|---|---|---|---|---|---|")
    for level in sorted({a[0] for a in arms}):
        for source in ["e2", "b11"]:
            chosen = [a for a in arms if a[0] == level and (B11 in a[1]) == (source == "b11")]
            if not chosen:
                continue
            for effort, floor in FLOORS:
                loaded = []
                for _, path, segments in chosen:
                    twins = {}
                    for lo in segments:
                        twins.update(games_of(f"{E2}/e{effort}-{lo}.jsonl.gz", opt))
                    loaded.append((games_of(path, opt), twins))
                total = sum(g.played["work"] + (g.played["other"]["work"] if g.played.get("other") else 0)
                            for games, _ in loaded for g in games.values())
                for t in STOP_T:
                    saved, unchanged, changed, alone = 0, 0, [], 0
                    for games, twins in loaded:
                        for n, g in sorted(games.items()):
                            if g.played["method"] != "search" or g.played.get("unseeded"):
                                continue
                            twin = twin_of(n, games, twins)
                            if twin is None:
                                alone += 1
                                continue
                            at = stop(g, twin, t, bounds)
                            if at is None:
                                continue
                            if at[1] == g.played["score"]:
                                saved += g.played["work"] - at[0]
                                unchanged += 1
                            else:
                                changed.append(f"{n}: {g.played['score'] - at[1]}")
                    print(f"| {level} | {len(chosen)} {source} | {floor:,} | {t} | {total / 1e6:.1f} M | "
                          f"{100 * saved / total:.1f}% ({unchanged} games) | {len(changed)}"
                          f"{': ' + ', '.join(changed) if changed else ''} | {alone} |")


if __name__ == "__main__":
    main()
