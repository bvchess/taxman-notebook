#!/usr/bin/env python3
"""The blocks of short games past 5060, and what settles the games at their ends (README.md, "Results").

nu.csv holds, for each n of 5061..10000, nu(n), the moves of the best-known game and short_by = nu(n) - moves.  The
files check/tool7.jsonl and check/ends-*.jsonl hold what the prover's `moves` tool settled: the most moves of a game,
ell(n), for games whose best-known line has fewer than nu(n) moves.  The script prints:

  1. the runs: maximal stretches of consecutive games with the same positive short_by;
  2. whether the games at both ends of every run are settled by `moves`, and how (parity bound or predecessor);
  3. how well short_by follows max(c(n) - 3, 0), where c(n) is the number of primes p with 48 <= floor(n / p) <= 53;
  4. the blocks of c(n) >= 4, with where each starts (48p for a prime p) and ends (54q - 1 for a prime q).

Run:  python3 -I blocks.py > blocks-output.txt      (reads nu.csv and check/*.jsonl only)
"""

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = 10000
LOW, HIGH, MARGIN = 48, 53, 3


def primes_to(top):
    """The primes up to top, by the sieve of Eratosthenes."""
    sieve = bytearray([1]) * (top + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(top**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i in range(top + 1) if sieve[i]]


def read_shortfalls():
    """{n: (nu, moves, short_by)} for every game of nu.csv."""
    with (HERE / "nu.csv").open() as f:
        return {int(r["n"]): (int(r["nu"]), int(r["moves"]), int(r["short_by"])) for r in csv.DictReader(f)}


def read_settled():
    """{n: how} for each game that `moves` settled with fewer moves than nu(n): by "parity" or "predecessor"."""
    settled = {}
    for name in ["tool7.jsonl", "ends-a.jsonl", "ends-b.jsonl", "ends-c.jsonl", "ends-d.jsonl"]:
        with (HERE / "check" / name).open() as f:
            for line in f:
                game = json.loads(line)
                if game["most"] is not None and game["most"] < game["nu"]:
                    settled[game["n"]] = game["how"]
    return settled


def stretches(numbers):
    """The maximal runs of consecutive numbers of the sorted list, as (first, last)."""
    out = []
    for n in numbers:
        if out and out[-1][1] == n - 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return [tuple(r) for r in out]


def runs_of_equal_shortfall(games):
    """The runs of consecutive games with the same positive short_by, as (first, last, short_by)."""
    out = []
    for n in sorted(games):
        short = games[n][2]
        if short == 0:
            continue
        if out and out[-1][1] == n - 1 and out[-1][2] == short:
            out[-1][1] = n
        else:
            out.append([n, n, short])
    return [tuple(r) for r in out]


def main():
    games = read_shortfalls()
    settled = read_settled()
    primes = primes_to(TOP)
    is_prime = set(primes)

    runs = runs_of_equal_shortfall(games)
    print(f"{len(runs)} runs of games with the same positive short_by (first, last, short_by):")
    for first, last, short in runs:
        print(f"  {first}-{last}: short by {short}, {last - first + 1} games")
    ends = sorted({n for first, last, _ in runs for n in (first, last)})
    missing = [n for n in ends if n not in settled]
    print(f"\n{len(ends)} games at the ends of the runs; settled by `moves` with fewer than nu moves: "
          f"{len(ends) - len(missing)}; not settled: {missing}")
    print(f"settled games not at an end of a run: {sorted(set(settled) - set(ends))}")
    print(f"how they were settled: {dict(Counter(settled[n] for n in ends if n in settled))}")

    count = {n: sum(1 for p in primes if LOW <= n // p <= HIGH) for n in games}
    follows = [n for n in games if max(count[n] - MARGIN, 0) == games[n][2]]
    print(f"\nshort_by = max(c(n) - {MARGIN}, 0) at {len(follows)} of {len(games)} games")
    off = sorted(set(games) - set(follows))
    for first, last in stretches(off):
        formula = {max(count[n] - MARGIN, 0) for n in range(first, last + 1)}
        recorded = {games[n][2] for n in range(first, last + 1)}
        print(f"  off at {first}-{last}: short_by {sorted(recorded)}, formula {sorted(formula)}")
    larger = [n for n in games if games[n][2] > max(count[n] - MARGIN, 0)]
    print(f"games whose short_by is larger than the formula's: {len(larger)}")

    print(f"\nblocks of c(n) >= {MARGIN + 1}: first game, last game, whether the first is 48p and the last 54q - 1")
    for first, last in stretches([n for n in sorted(games) if count[n] > MARGIN]):
        starts = first % LOW == 0 and first // LOW in is_prime
        stops = (last + 1) % 54 == 0 and (last + 1) // 54 in is_prime
        note = " (cut off by the top of the range)" if last == TOP else ""
        print(f"  {first}-{last}: starts at 48p: {starts}, ends at 54q - 1: {stops}{note}")


if __name__ == "__main__":
    main()
