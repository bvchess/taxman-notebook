#!/usr/bin/env python3
"""E6, a side check: are E1's best games of Y = board n - 1 without x independent at both parities?

For each E1 game, L' is the part up to (n - 1)/2 of E1's best set on Y (e1-show.jsonl), a promotion set worth more than
P*(n - 1).  The script says whether L' is x-bound (U*(n - 1) + L' unplayable, B + L' playable, B = U*(n - 1) - x),
whether it can be promoted in game n (U*(n) + L' playable), and whether U*(n - 1) + L' is independent at both parities
(docs/theory/parity-bound.md, "The parity vectors"): a set that is not is refused by the parity bound outright, with no
conflict.  Playability is the core residual of the succession brief's Theorems P5 and P7 (delete members that list a
factor no other remaining member lists; playable iff nothing is left), with each member's list its maximal factors that
are not members.  It shares nothing with the frame solver.  U*(m) is the committed optimal set of m above m/2, checked
against descending greedy.  Run as `nice -n 19 python3 -I e1_sets.py` from this folder.
"""
import gzip
import json

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
E1_SHOW = "/home/brian/taxman_work/lab/work/succession/e1-holes/e1-show.jsonl"
TOP = 2301


def sieve(n):
    spf = list(range(n + 1))
    for p in range(2, int(n ** 0.5) + 1):
        if spf[p] == p:
            for q in range(p * p, n + 1, p):
                if spf[q] == q:
                    spf[q] = p
    return spf


SPF = sieve(TOP)


def primes_of(s):
    out = []
    while s > 1:
        p = SPF[s]
        out.append(p)
        s //= p
    return out


def omega(s):
    return len(primes_of(s))


def max_factors(s):
    return sorted({s // p for p in set(primes_of(s))})


def residual(members):
    """The core residual: members deleted while some factor of theirs is listed by no other remaining member."""
    live = set(members)
    lists = {s: [f for f in max_factors(s) if f not in live] for s in live}
    listers = {}
    for s in live:
        for f in lists[s]:
            listers.setdefault(f, set()).add(s)
    stack = [s for s in live if any(len(listers[f]) == 1 for f in lists[s])]
    while stack:
        s = stack.pop()
        if s not in live:
            continue
        live.remove(s)
        for f in lists[s]:
            listers[f].discard(s)
            if len(listers[f]) == 1:
                stack.extend(listers[f])
    return live


def is_playable(members):
    return not residual(members)


def independent_both(members, m):
    """Whether `members` (numbers of 2..m) is independent at both parities on the board of m."""
    half = m // 2
    for i in (0, 1):
        basis = {}  # pivot bit -> vector
        for s in members:
            if omega(s) % 2 != i:
                v = 0
                for f in max_factors(s):
                    v |= 1 << f
            elif s <= half:
                v = 1 << s
            else:
                continue  # an extra coordinate: in no circuit
            while v:
                top = v.bit_length() - 1
                if top in basis:
                    v ^= basis[top]
                else:
                    basis[top] = v
                    break
            if v == 0:
                return False
    return True


def greedy_ustar(m):
    kept = []
    for s in range(m, m // 2, -1):
        kept.append(s)
        if not is_playable(kept):
            kept.pop()
    return sorted(kept)


def main():
    wanted = {}
    for line in open(E1_SHOW):
        d = json.loads(line)
        wanted[d["n"]] = d
    games = {}
    with gzip.open(RESULTS, "rt") as f:
        for line in f:
            d = json.loads(line)
            if d["n"] in wanted or d["n"] - 1 in wanted:
                games[d["n"]] = d
            if d["n"] > max(wanted) + 1:
                break
    print("m n x | sum L' - P*(m) | Y sources = B | x-bound | promotable in n | U*(m)+L' indep. both parities "
          "| S*(m) indep. (check)")
    for m in sorted(wanted):
        e1, x, n = wanted[m], wanted[m]["holes"][0], m + 1
        committed = games[m]["moves"]
        ustar_m = sorted(s for s in committed if 2 * s > m)
        assert ustar_m == greedy_ustar(m), f"U*({m}) is not descending greedy's"
        ustar_n = greedy_ustar(n)
        assert sorted(set(ustar_m) - set(ustar_n)) == [x] and sorted(set(ustar_n) - set(ustar_m)) == [n]
        pstar = games[m]["score"] - sum(ustar_m)
        base = [s for s in ustar_m if s != x]
        moves = e1["moves"]
        lower = sorted(s for s in moves if 2 * s <= m)
        sources = sorted(s for s in moves if 2 * s > m)
        assert is_playable(moves)
        xbound = (not is_playable(ustar_m + lower)) and is_playable(base + lower)
        promotable_n = is_playable(ustar_n + lower)
        indep = independent_both(ustar_m + lower, m)
        check = independent_both(committed, m)
        print(m, n, x, "|", sum(lower) - pstar, "|", sources == base, "|", xbound, "|", promotable_n, "|", indep, "|",
              check)


if __name__ == "__main__":
    main()
