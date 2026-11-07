#!/usr/bin/env python3
"""The proven games above n, taken down to n two ways, against opt(n), on the games of Part 1.

    python3 -I projection.py part1/e7-a4.jsonl

For each game n of the file and each j of 1 to 4: the moves of the proven game of n + j less those above n, which are
a game of n (the ceiling lemma, N4, once for each number above n), finished with the largest legal move first until
none is left ("greedy"); and what the solver's survivors give, the score that the line's `survivors` records for n + j
(the candidates of those moves that n's frames can still promote, from the largest down, and the moves they make).
Prints how far each falls short of opt(n), then how often each reaches it and how often each is the higher.
"""

import gzip
import json
import sys

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"


def divisors_up_to(n):
    """The proper divisors of each number up to n."""
    divisors = [[] for _ in range(n + 1)]
    for d in range(1, n // 2 + 1):
        for k in range(2 * d, n + 1, d):
            divisors[k].append(d)
    return divisors


def projected(n, moves, divisors):
    """The moves of a game above n less those above n, played on the board of n, then finished greedily: the score."""
    pot = bytearray([1]) * (n + 1)
    pot[0] = 0
    score = 0
    for m in moves:
        if m > n:
            continue
        assert pot[m] and any(pot[d] for d in divisors[m]), (n, m)
        pot[m] = 0
        score += m
        for d in divisors[m]:
            pot[d] = 0
    for m in range(n, 1, -1):
        if pot[m] and any(pot[d] for d in divisors[m]):
            pot[m] = 0
            score += m
            for d in divisors[m]:
                pot[d] = 0
    return score


def main():
    games = {}
    with gzip.open(RESULTS, "rt") as f:
        for text in f:
            d = json.loads(text)
            if d["n"] >= 3400:
                games[d["n"]] = (d["score"], d["moves"])
    divisors = divisors_up_to(max(games))
    reach = {"greedy": [0] * 4, "survivors": [0] * 4}
    higher = {"greedy": 0, "survivors": 0, "equal": 0}
    with (gzip.open(sys.argv[1], "rt") if sys.argv[1].endswith(".gz") else open(sys.argv[1])) as f:
        for text in f:
            line = json.loads(text)
            n = line["n"]
            best = games[n][0]
            survivors = {m: s for m, s in line.get("survivors") or [] if m > n}
            row = []
            for j in range(1, 5):
                if n + j not in games or n + j not in survivors:
                    continue
                greedy = projected(n, games[n + j][1], divisors)
                frame = survivors[n + j]
                reach["greedy"][j - 1] += greedy == best
                reach["survivors"][j - 1] += frame == best
                higher["greedy" if greedy > frame else "survivors" if frame > greedy else "equal"] += 1
                row.append(f"+{j}: {best - greedy}/{best - frame}")
            print(n, "short by, greedy/survivors:", " ".join(row))
    print("reach opt(n), from n + 1 .. n + 4:", reach)
    print("the higher of the two:", higher)


if __name__ == "__main__":
    main()
