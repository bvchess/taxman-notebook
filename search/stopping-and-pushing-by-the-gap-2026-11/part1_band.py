#!/usr/bin/env python3
"""Part 1 of study B13, the stop with the floor of level 1's budget, one-sided against a band.

    python3 -I part1_band.py

As part1_floor.py, with the floor at level 1's budget (131,072 work, E2's `e2` runs as the twins): the one-sided rule
stops a game where its growth is at most T, and the band where its growth is from −T to T, so that a gap that shrank
by more than T goes on.  For each level of E2 (2 to 6) and for B11's chains of 4861-5060 at level 3: the share of the
work saved with the line unchanged, the lines changed, and, of the searched games with no twin, those with a gain after
the floor's budget whose score before it the rule would stop at: where the rule may change a line that no twin shows.
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import B11, E2, games_of, growth_of, opt_scores, parity_bounds, segment_of  # noqa: E402
from part1_floor import twin_of  # noqa: E402

FLOOR = 131_072
RULES = [("at most 0", -10**9, 0), ("at most 25", -10**9, 25), ("within 0", 0, 0), ("within 25", -25, 25)]


def stop(game, twin, lo, hi, bounds):
    """Where the rule stops the game: (work, score), or None."""
    within = lambda score: lo <= growth_of(game, score, bounds) <= hi  # noqa: E731
    if within(twin.played["score"]):
        return twin.played["work"], twin.played["score"]
    for gain in game.played["improvements"]:
        if gain["work"] > twin.played["work"] and within(gain["score"]):
            return gain["work"], gain["score"]
    return None


def main():
    opt, bounds = opt_scores(), parity_bounds()
    arms = [(f"{effort - 1} (E2)", sorted(glob.glob(f"{E2}/e{effort}-*.jsonl.gz"))) for effort in range(3, 8)]
    arms.append(("3 (B11)", sorted(glob.glob(f"{B11}/*-4861.jsonl.gz"))))
    print("| level | rule | saved, line unchanged | lines changed (n: points lost) | untwinned games at risk |")
    print("|---|---|---|---|---|")
    for level, paths in arms:
        loaded = []
        for path in paths:
            segments = ["4861", "4961"] if B11 in path else [segment_of(path)]
            twins = {}
            for lo in segments:
                twins.update(games_of(f"{E2}/e2-{lo}.jsonl.gz", opt))
            loaded.append((games_of(path, opt), twins))
        total = sum(g.played["work"] + (g.played["other"]["work"] if g.played.get("other") else 0)
                    for games, _ in loaded for g in games.values())
        for name, lo, hi in RULES:
            saved, changed, risky = 0, [], []
            for games, twins in loaded:
                for n, g in sorted(games.items()):
                    if g.played["method"] != "search" or g.played.get("unseeded"):
                        continue
                    twin = twin_of(n, games, twins)
                    if twin is None:
                        late = [i for i in g.played["improvements"] if i["work"] > FLOOR]
                        early = [i["score"] for i in g.played["improvements"] if i["work"] <= FLOOR]
                        before = max([g.played["start"]] + early)
                        if late and lo <= growth_of(g, before, bounds) <= hi:
                            risky.append(str(n))
                        continue
                    at = stop(g, twin, lo, hi, bounds)
                    if at is None:
                        continue
                    if at[1] == g.played["score"]:
                        saved += g.played["work"] - at[0]
                    else:
                        changed.append(f"{n}: {g.played['score'] - at[1]}")
            print(f"| {level} | {name} | {100 * saved / total:.1f}% | {len(changed)}"
                  f"{': ' + ', '.join(changed) if changed else ''} | {', '.join(risky) or 'none'} |")


if __name__ == "__main__":
    main()
