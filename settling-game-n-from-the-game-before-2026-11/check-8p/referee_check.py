#!/usr/bin/env python3
"""Referee's independent checks of Theorem 8P.  Standard library only.

    nice -n 19 python3 -I referee_check.py [PMAX]

A. Arithmetic facts (i)-(iv) for every prime P with 29 <= P <= PMAX and 9 P1 > 8 P, by listing every x <= 8P that
   has the factor in question as a maximal factor.
B. Table of every 8P game of 2..5060: delta against 4 P1, hypothesis status.
C. For every 8P game meeting the hypotheses: the recorded optimal set S of n, fact (v), the case of the proof it
   falls in, the set the proof constructs, its playability by the residual (P7, own instance), and the inequality.
"""
import gzip
import json
import sys

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"


def sieve(limit):
    spf = list(range(limit + 1))
    for i in range(2, int(limit ** 0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


def factor_primes(x, spf):
    ps = set()
    while x > 1:
        ps.add(spf[x])
        x //= spf[x]
    return ps


def omega(x, spf):
    k = 0
    while x > 1:
        x //= spf[x]
        k += 1
    return k


def mf(x, spf):
    return {x // p for p in factor_primes(x, spf)}


def residual(S, spf):
    """Residual of the own instance of S (P5/P7): dismantle by back moves.  Empty iff S playable."""
    S = set(S)
    lists = {x: mf(x, spf) - S for x in S}
    count = {}
    for x, L in lists.items():
        for f in L:
            count[f] = count.get(f, 0) + 1
    alive = set(S)
    stack = [x for x in alive if any(count[f] == 1 for f in lists[x])]
    while stack:
        x = stack.pop()
        if x not in alive:
            continue
        if not any(count[f] == 1 for f in lists[x]):
            continue
        alive.discard(x)
        for f in lists[x]:
            count[f] -= 1
            if count[f] == 1:
                for y in alive:
                    if f in lists[y]:
                        stack.append(y)
                        break
    return alive


def playable(S, spf):
    return not residual(S, spf)


def prev_prime(p, spf):
    q = p - 1
    while spf[q] != q:
        q -= 1
    return q


def listers(f, n, spf):
    """Numbers x <= n with f in mf(x): x = f*r, r prime."""
    return [f * r for r in range(2, n // f + 1) if spf[r] == r]


def part_a(pmax):
    spf = sieve(8 * pmax + 1)
    bad = 0
    count = 0
    for P in range(29, pmax + 1):
        if spf[P] != P:
            continue
        P1 = prev_prime(P, spf)
        if 9 * P1 <= 8 * P:
            continue
        n = 8 * P
        count += 1
        checks = {
            "4P by 8P alone": listers(4 * P, n, spf) == [8 * P],
            "4P1 by 8P1 alone": listers(4 * P1, n, spf) == [8 * P1],
            "2P1 by 4P1, 6P1": listers(2 * P1, n, spf) == [4 * P1, 6 * P1],
            "3P1 by 6P1 alone": listers(3 * P1, n, spf) == [6 * P1],
            "2P by 4P, 6P": listers(2 * P, n, spf) == [4 * P, 6 * P],
            "3P by 6P alone": listers(3 * P, n, spf) == [6 * P],
            "mf(8P)": mf(8 * P, spf) == {4 * P, 8},
            "mf(8P1)": mf(8 * P1, spf) == {4 * P1, 8},
            "mf(4P1)": mf(4 * P1, spf) == {2 * P1, 4},
            "mf(6P1)": mf(6 * P1, spf) == {6, 2 * P1, 3 * P1},
            "mf(4P)": mf(4 * P, spf) == {2 * P, 4},
            "mf(6P)": mf(6 * P, spf) == {6, 2 * P, 3 * P},
            "8P1 > 4P (source on n-1)": 8 * P1 > 4 * P,
            "4P1 < 4P": 4 * P1 < 4 * P,
            "8 not in {4P,4P1,2P,2P1,3P,3P1,6}": 8 not in {4 * P, 4 * P1, 2 * P, 2 * P1, 3 * P, 3 * P1, 6},
            "layers": all(omega(x, spf) == k for x, k in
                          ((8 * P, 4), (8 * P1, 4), (4 * P, 3), (4 * P1, 3), (6 * P, 3), (6 * P1, 3), (8, 3),
                           (2 * P, 2), (3 * P, 2), (2 * P1, 2), (3 * P1, 2), (4, 2), (6, 2))),
        }
        for name, ok in checks.items():
            if not ok:
                bad += 1
                print(f"  A FAIL at P = {P} (n = {n}, P1 = {P1}): {name}")
    print(f"A. arithmetic facts: {count} primes P in 29..{pmax} with 9P1 > 8P checked, {bad} failures")


def load_results():
    res = {}
    with gzip.open(RESULTS, "rt") as f:
        for line in f:
            d = json.loads(line)
            res[d["n"]] = (d["score"], d["moves"])
    return res


def part_bc():
    res = load_results()
    nmax = max(res)
    spf = sieve(nmax + 1)
    print(f"B. every 8P game of 2..{nmax} (P prime): delta vs 4P1")
    print("      n     P    P1   4P1  delta  delta-4P1  n>=187  9P1>8P")
    for n in range(16, nmax + 1, 8):
        P = n // 8
        if spf[P] != P:
            continue
        P1 = prev_prime(P, spf) if P > 2 else None
        if P1 is None:
            continue
        delta = res[n - 1][0] + n - res[n][0]
        print(f"  {n:5d} {P:5d} {P1:5d} {4 * P1:5d} {delta:6d} {delta - 4 * P1:10d}  {str(n >= 187):6s}  "
              f"{str(9 * P1 > 8 * P):6s}")
    print()
    print("C. proof walk on the recorded optimal set of each 8P game meeting the hypotheses")
    cases = {}
    bad = 0
    total = 0
    for n in range(187, nmax + 1):
        if n % 8:
            continue
        P = n // 8
        if spf[P] != P:
            continue
        P1 = prev_prime(P, spf)
        if 9 * P1 <= 8 * P:
            continue
        total += 1
        opt_n, S = res[n][0], set(res[n][1])
        opt_m = res[n - 1][0]
        assert sum(S) == opt_n
        problems = []
        if n not in S:
            problems.append("8P not in S")
        if any(omega(x, spf) == 2 and x <= n // 2 for x in S):
            problems.append("layer-2 number <= n/2 in S (F10)")
        if not playable(S, spf):
            problems.append("S not playable by residual")
        T = S - {n}
        if 4 * P not in S:
            case = "A" + ("+6P" if 6 * P in T else "-6P")
            new = T | {4 * P}
            bound = 4 * P
        else:
            if 8 in S:
                problems.append("8 in S in case B")
            if 8 * P1 in S:
                case = "B1" + ("+6P1" if 6 * P1 in T else "-6P1")
                if 4 * P1 in S:
                    problems.append("4P1 in S in case B1")
                new = T | {4 * P1}
                bound = 4 * P1
            else:
                case = "B2"
                new = T | {8 * P1}
                bound = 8 * P1
        if not playable(new, spf):
            problems.append(f"constructed set not playable in case {case}")
        if sum(T) + bound > opt_m:
            problems.append("constructed set beats opt(n-1)")
        if sum(T) > opt_m - 4 * P1:
            problems.append("inequality sum T <= opt(n-1) - 4P1 fails")
        if opt_n != opt_m + n - 4 * P1:
            problems.append("delta != 4P1")
        cases[case] = cases.get(case, 0) + 1
        if problems:
            bad += 1
            print(f"  {n} = 8*{P}: case {case}: " + "; ".join(problems))
    print(f"  {total} games checked, {bad} with problems; cases met: {cases}")


if __name__ == "__main__":
    pmax = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    part_a(pmax)
    part_bc()
