#!/usr/bin/env python3
"""Part 2 of study B11: chains with and without games played twice (`--unseeded-every K`).

    python3 -I part2.py WITHOUT WITH

WITHOUT and WITH are files of unsound lines of one range.  A game's line is its last line in the file (a repair writes
it again).  Prints, for each chain: the games at opt(n) where the committed results have it, the streaks of short games
(the game each starts at, its length, how short its first game is, and the game that ended it), the games played twice
and those whose unseeded play was kept, the work (of both plays), and the seconds of the games and of the repair's
walks per 100 games.  Then the games whose scores differ, and whether any is lower with games played twice.
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optlib import opt_scores  # noqa: E402


def read(path):
    """The first line of each game (as played), the last (the game's), and the repairs' seconds."""
    played, last, repairs = {}, {}, []
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        for text in f:
            if not text.strip():
                continue
            line = json.loads(text)
            n = line["n"]
            if line.get("repaired") is None:
                played[n] = line
            else:
                repairs.append(line)
            last[n] = line
    return played, last, repairs


def streaks(games, short):
    """The stretches of consecutive short games: (first, length, shortfall at the first, the game after it)."""
    found, n = [], None
    ordered = sorted(games)
    i = 0
    while i < len(ordered):
        n = ordered[i]
        if short.get(n, 0) > 0:
            j = i
            while j + 1 < len(ordered) and short.get(ordered[j + 1], 0) > 0:
                j += 1
            after = ordered[j + 1] if j + 1 < len(ordered) else None
            found.append((n, j - i + 1, short[n], after))
            i = j + 1
        else:
            i += 1
    return found


def summary(name, path, opt):
    played, last, repairs = read(path)
    repair_seconds = sum(line["repaired"]["seconds"] for line in repairs)
    games = sorted(last)
    known = [n for n in games if n in opt]
    short = {n: opt[n] - last[n]["score"] for n in known}
    at_opt = sum(1 for n in known if short[n] == 0)
    twice = [n for n in games if played[n].get("other") is not None]
    kept = [n for n in twice if played[n]["unseeded"]]
    work = sum(p["work"] + (p["other"]["work"] if p.get("other") else 0) for p in played.values())
    seconds = sum(p["seconds"] for p in played.values())
    other_seconds = sum(p["other"]["seconds"] for p in played.values() if p.get("other"))
    per100 = 100 / len(games)
    print(f"{name}: {path}")
    print(f"  games {games[0]}-{games[-1]} ({len(games)}), lines the repair replaced {len(repairs)}: "
          f"{[(line['n'], line['repaired']['from']) for line in repairs]}")
    if known:
        print(f"  at opt(n): {at_opt} of {len(known)} ({100 * at_opt / len(known):.1f}%)")
        for first, length, size, after in streaks(known, short):
            print(f"  streak: {first}, {length} games, {size} short at the first, ended by {after}")
    print(f"  played twice: {len(twice)}; the unseeded play kept: {len(kept)} {kept}")
    if twice:
        # The unseeded play's score less the seeded play's, for each game played twice.
        gain = {}
        for n in twice:
            line, other = played[n], played[n]["other"]
            unseeded, seeded = (line, other) if line["unseeded"] else (other, line)
            gain[n] = unseeded["score"] - seeded["score"]
        lower = [(n, g) for n, g in gain.items() if g < 0]
        print(f"  the unseeded play scored more in {sum(g > 0 for g in gain.values())}, as much in "
              f"{sum(g == 0 for g in gain.values())}, less in {len(lower)}: {lower}")
    print(f"  work: {work:,} ({work * per100:,.0f} per 100 games)")
    print(f"  seconds of the games: {seconds:,.0f} ({seconds * per100:,.0f} per 100 games), of which the unseeded or "
          f"other plays {other_seconds:,.0f}; the repair's walks {repair_seconds:,.1f}")
    return last


def main():
    without_path, with_path = sys.argv[1], sys.argv[2]
    opt = opt_scores()
    without = summary("without", without_path, opt)
    with_ = summary("with", with_path, opt)
    differ = [(n, without[n]["score"], with_[n]["score"]) for n in sorted(without) if n in with_
              and without[n]["score"] != with_[n]["score"]]
    lower = [d for d in differ if d[2] < d[1]]
    moves = [n for n in sorted(without) if n in with_ and without[n]["moves"] != with_[n]["moves"]]
    print(f"games whose scores differ: {len(differ)}; lower with: {len(lower)}; whose moves differ: {len(moves)}")
    for n, a, b in differ:
        print(f"  {n}: {a} -> {b} ({b - a:+d})")


if __name__ == "__main__":
    main()
