#!/usr/bin/env python3
"""Summarize the lines of `restricted census`: what the search's conflicts hold, by depth and by largest prime.

Each argument is a file of census JSON lines.  For each line it prints the run, then for each depth (promotions of the
node, in tens) the conflicts the nodes went on with, their mean size and the share of their members that are in the
smooth part (B-smooth); the cumulative share of conflict members by the largest prime of the member; and the members
branched on most, with their largest primes.
"""

import json
import sys

BOUNDS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 43, 53, 71, 101, 151, 251)


def largest_prime(k: int) -> int:
    """The largest prime factor of k >= 2."""
    p, d = 1, 2
    while d * d <= k:
        while k % d == 0:
            p, k = d, k // d
        d += 1
    return max(p, k) if k > 1 else p


def summarize(d: dict) -> None:
    print(f"n={d['n']} B={d['smooth']} above={d['above']} score={d['score']} completed={d['completed']} "
          f"steps={d['nodes']} cpu={d['cpu']:.0f} s")
    print("  depth     conflicts  mean size  share in the smooth part")
    for i, (count, members, smooth) in enumerate(d["depths"]):
        if count:
            print(f"  {10 * i:3d}-{10 * i + 9:3d} {count:12d} {members / count:10.1f} {smooth / max(members, 1):10.2f}")
    total = sum(c for _, c in d["by_prime"])
    shares = []
    for bound in BOUNDS:
        shares.append(f"<={bound}: {sum(c for p, c in d['by_prime'] if p <= bound) / total:.2f}")
    print("  members by largest prime, cumulative: " + ", ".join(shares))
    top = ", ".join(f"{y} ({largest_prime(y)}) {c}" for y, c in d["top"][:25])
    print(f"  most branched on, member (largest prime) count: {top}")


def main() -> None:
    for path in sys.argv[1:]:
        with open(path) as f:
            for line in f:
                summarize(json.loads(line))


if __name__ == "__main__":
    main()
