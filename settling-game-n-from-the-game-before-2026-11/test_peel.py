#!/usr/bin/env python3
"""Checks of common.playable: against a search over all orders on every subset of small boards, on the recorded
optimal sets, and on known unplayable sets.  Run: nice -n 19 python3 -I test_peel.py"""

import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

spf = common.sieve_spf(10000)


def brute(members, n):
    """Some order of `members` is a legal game on board n (each move has a proper divisor in the pot)."""
    members = sorted(members)
    seen = {}

    def rec(left, pot):
        key = (left, pot)
        if key in seen:
            return seen[key]
        if not left:
            return True
        ok = False
        for x in left:
            divs = [d for d in pot if d < x and x % d == 0]
            if divs:
                if rec(left - {x}, pot - {x} - set(divs)):
                    ok = True
                    break
        seen[key] = ok
        return ok

    return rec(frozenset(members), frozenset(range(1, n + 1)))


count = 0
for n in range(2, 13):
    for k in range(0, 7):
        for s in itertools.combinations(range(2, n + 1), k):
            a, b = common.playable(s, n, spf), brute(s, n)
            assert a == b, (n, s, a, b)
            count += 1
print("subsets of boards 2..12 with at most 6 members compared with all orders:", count, "agree")

res = common.results()
for n in range(2, 5061):
    assert common.playable(res[n]["moves"], n, spf), n
print("recorded optimal sets 2..5060: all playable")
assert not common.playable(set(res[20]["moves"]) | {21}, 21, spf)
print("the optimal set of 20 with 21 added: unplayable, as expected")
