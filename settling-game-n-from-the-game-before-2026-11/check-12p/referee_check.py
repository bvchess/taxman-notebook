#!/usr/bin/env python3
"""Referee's independent checks of Theorem 12P.  Standard library only.

    nice -n 19 python3 -I referee_check.py [PMAX] [SAMPLES]

A. Arithmetic facts for every prime P >= 19 with 15 P1 > 12 P up to PMAX, by listing every x <= 12P that has each
   factor as a maximal factor; counts the games where 14 P1 <= 12 P (the slip in the text).
B. The proof walked on the recorded optimal set S of every 12P game of 228..5052 whose S holds 8P, 8P1, 12P1 and
   some 8t' (t' prime in (4P/3, 3P/2]): the case, the set the proof constructs, its playability by the residual of
   its own instance (P7), the inequalities, who pays 2P1 and 2P, and the shape of S's forced payments.
C. U*(n) by my own descending greedy at a few games, against the hypothesis "8P, 8P1, 12P1, 8t' in U*(n)".
D. Random playable layer-4 instances of board n holding 12P, 8P, 8P1, 12P1, 8t', with a random set of layer-3 moves:
   the layer-4 claim of each case of the proof, including the B1 sub-case in which another 8u pays 8 (never seen in
   the chain), tested by the residual of the instance the proof builds.
"""
import gzip
import json
import random
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


def residual_lists(lists):
    """Residual of an instance given as {member: set of listed factors} (P5/P7).  Empty iff playable."""
    by_factor = {}
    for x, L in lists.items():
        for f in L:
            by_factor.setdefault(f, set()).add(x)
    alive = set(lists)
    stack = [x for x in alive if any(len(by_factor[f]) == 1 for f in lists[x])]
    while stack:
        x = stack.pop()
        if x not in alive or not any(len(by_factor[f]) == 1 for f in lists[x]):
            continue
        alive.discard(x)
        for f in lists[x]:
            by_factor[f].discard(x)
            if len(by_factor[f]) == 1:
                stack.append(next(iter(by_factor[f])))
    return alive


def residual(S, spf):
    S = set(S)
    return residual_lists({x: mf(x, spf) - S for x in S})


def playable(S, spf):
    return not residual(S, spf)


def prev_prime(p, spf):
    q = p - 1
    while spf[q] != q:
        q -= 1
    return q


def listers(f, n, spf):
    return sorted(f * r for r in range(2, n // f + 1) if spf[r] == r)


def tprime(P, n, S, spf):
    """The largest prime t' in (4P/3, 3P/2] with 8t' in S, or None."""
    ts = [t for t in range(2, 3 * P // 2 + 1) if spf[t] == t and 3 * t > 4 * P and 8 * t in S]
    return max(ts) if ts else None


# ----------------------------------------------------------------------------------------------------- part A
def part_a(pmax):
    spf = sieve(14 * pmax + 1)
    bad = count = slip = 0
    sliplist = []
    for P in range(19, pmax + 1):
        if spf[P] != P:
            continue
        P1 = prev_prime(P, spf)
        if 15 * P1 <= 12 * P:
            continue
        n = 12 * P
        count += 1
        ts = [t for t in range(2, 3 * P // 2 + 1) if spf[t] == t and 3 * t > 4 * P]
        checks = {
            "4P by 8P, 12P": listers(4 * P, n, spf) == [8 * P, 12 * P],
            "6P by 12P": listers(6 * P, n, spf) == [12 * P],
            "5P by 10P": listers(5 * P, n, spf) == [10 * P],
            "3P by 6P, 9P": listers(3 * P, n, spf) == [6 * P, 9 * P],
            "2P by 4P, 6P, 10P": listers(2 * P, n, spf) == [4 * P, 6 * P, 10 * P],
            "4P1 by 8P1, 12P1": listers(4 * P1, n, spf) == [8 * P1, 12 * P1],
            "6P1 by 12P1": listers(6 * P1, n, spf) == [12 * P1],
            "5P1 by 10P1": listers(5 * P1, n, spf) == [10 * P1],
            "3P1 by 6P1, 9P1": listers(3 * P1, n, spf) == [6 * P1, 9 * P1],
            "7P1 by 14P1 at most": set(listers(7 * P1, n, spf)) <= {14 * P1},
            "2P1 by 4P1, 6P1, 10P1 (+14P1)": set(listers(2 * P1, n, spf)) - {14 * P1} == {4 * P1, 6 * P1, 10 * P1},
            "mf(12P)": mf(12 * P, spf) == {6 * P, 4 * P, 12},
            "mf(12P1)": mf(12 * P1, spf) == {6 * P1, 4 * P1, 12},
            "mf(8P)": mf(8 * P, spf) == {4 * P, 8},
            "mf(8P1)": mf(8 * P1, spf) == {4 * P1, 8},
            "mf(6P1)": mf(6 * P1, spf) == {6, 2 * P1, 3 * P1},
            "mf(6P)": mf(6 * P, spf) == {6, 2 * P, 3 * P},
            "mf(10P), mf(10P1), mf(14P1)": mf(10 * P, spf) == {5 * P, 2 * P, 10} and mf(10 * P1, spf) == {5 * P1, 2 * P1, 10}
            and mf(14 * P1, spf) == {7 * P1, 2 * P1, 14},
            "t' facts": all(listers(4 * t, n, spf) == [8 * t] and listers(2 * t, n, spf) == [4 * t, 6 * t]
                            and listers(3 * t, n, spf) == [6 * t] and 4 * t < 6 * P and 8 * t > 6 * P and 4 * t > 4 * P
                            and 6 * t > 6 * P and mf(8 * t, spf) == {4 * t, 8} and mf(4 * t, spf) == {2 * t, 4}
                            and mf(6 * t, spf) == {3 * t, 2 * t, 6} for t in ts),
            "sides of n/2": 6 * P1 < 6 * P and 4 * P1 < 4 * P and 8 * P1 > 6 * P and 10 * P1 > 6 * P and 12 * P1 > 6 * P
            and 9 * P1 < 12 * P and 14 * P1 > 6 * P,
            "layers": all(omega(x, spf) == k for x, k in
                          ((12 * P, 4), (12 * P1, 4), (8 * P, 4), (8 * P1, 4), (6 * P, 3), (4 * P, 3), (12, 3), (8, 3),
                           (6 * P1, 3), (4 * P1, 3), (10 * P, 3), (10 * P1, 3), (14 * P1, 3), (9 * P, 3), (9 * P1, 3),
                           (2 * P, 2), (3 * P, 2), (5 * P, 2), (2 * P1, 2), (3 * P1, 2), (5 * P1, 2), (7 * P1, 2))),
            "no collisions": len({12 * P, 12 * P1, 8 * P, 8 * P1, 6 * P, 4 * P, 12, 8, 6 * P1, 4 * P1, 10 * P, 10 * P1,
                                  14 * P1, 9 * P, 9 * P1}) == 15,
        }
        if 14 * P1 <= n:
            slip += 1
            if len(sliplist) < 10:
                sliplist.append(n)
        for name, ok in checks.items():
            if not ok:
                bad += 1
                print(f"  A FAIL at P = {P} (n = {n}, P1 = {P1}): {name}")
    print(f"A. arithmetic facts: {count} primes P in 19..{pmax} with 15P1 > 12P checked, {bad} failures; "
          f"14P1 <= 12P at {slip} of them (first: {sliplist})")


# ----------------------------------------------------------------------------------------------------- part B
def load_results():
    res = {}
    with gzip.open(RESULTS, "rt") as f:
        for line in f:
            d = json.loads(line)
            res[d["n"]] = (d["score"], d["moves"])
    return res


def scheme_possible(lists):
    return not residual_lists(lists)


def layer_lists(S, n, k, spf, members=None):
    """Lists of the layer-k instance of S on board n: members S_k (or the given ones), pool layer k-1 numbers
    <= n/2 not in S."""
    half = n // 2
    mem = [x for x in S if omega(x, spf) == k] if members is None else members
    return {x: {f for f in mf(x, spf) if f <= half and f not in S} for x in mem}


def part_b(res):
    spf = sieve(5100)
    print("B. the proof walked on the recorded optimal set of each 12P game of 228..5052 meeting the hypotheses")
    cases = {}
    bad = total = 0
    for n in range(228, 5053, 12):
        P = n // 12
        if spf[P] != P:
            continue
        P1 = prev_prime(P, spf)
        opt_n, S = res[n][0], set(res[n][1])
        opt_m = res[n - 1][0]
        assert sum(S) == opt_n
        hyp = {"15P1>12P": 15 * P1 > 12 * P, "8P": 8 * P in S, "8P1": 8 * P1 in S, "12P1": 12 * P1 in S}
        t1 = tprime(P, n, S, spf)
        hyp["8t'"] = t1 is not None
        if not all(hyp.values()):
            print(f"  {n} = 12*{P}: hypotheses fail: {[k for k, v in hyp.items() if not v]}")
            continue
        total += 1
        problems = []
        if n not in S:
            problems.append("12P not in S")
        if any(omega(x, spf) == 2 and x <= n // 2 for x in S):
            problems.append("layer-2 number <= n/2 in S (F10)")
        if not playable(S, spf):
            problems.append("S not playable by residual")
        T = S - {n}
        if not playable(T, spf):
            problems.append("T not playable")
        L4 = layer_lists(S, n, 4, spf)
        # Which payments are forced / possible in S's layer-4 instance.
        def can(**fix):
            L = {x: set(v) for x, v in L4.items()}
            for x, f in fix.items():
                L[int(x)] = {f} if f in L[int(x)] else set()
            return scheme_possible(L)
        twelveP_12 = can(**{str(12 * P): 12})
        twelveP_4P = can(**{str(12 * P): 4 * P})
        twelveP1_12_given_4P = can(**{str(12 * P): 4 * P, str(12 * P1): 12})
        if 6 * P not in S:
            if 9 * P not in S:
                case = "A1"
            elif 4 * P not in S:
                case = "A2"
            else:
                case = "A3"
            if case in ("A1", "A2"):
                new, bound = T | {6 * P}, 6 * P
            else:
                if 8 in S:
                    problems.append("8 in S in A3")
                if 4 * t1 in S:
                    problems.append("4t' in S in A3")
                new, bound = (T - {4 * P}) | {6 * P, 4 * t1}, 2 * P + 4 * t1
        else:
            if 6 * P1 in S:
                problems.append("6P1 in S with 6P in S (cycle lemma)")
            if 4 * P1 in S:
                case = "G4"
                for name, ok in (("8 in S", 8 in S), ("4P in S", 4 * P in S), ("12 in S", 12 in S), ("4t' in S", 4 * t1 in S)):
                    if ok:
                        problems.append(f"G4: {name}")
                new, bound = (T - {4 * P1}) | {6 * P1, 4 * t1}, 6 * P1 + 4 * t1 - 4 * P1
            elif twelveP_12:
                case = "B1"
                new, bound = T | {6 * P1}, 6 * P1
            else:
                if not twelveP_4P:
                    problems.append("12P can pay neither 12 nor 4P")
                if 4 * P in S:
                    problems.append("G2: 4P in S")
                if twelveP1_12_given_4P:
                    case = "G2-i"
                    new, bound = T | {6 * P1}, 6 * P1
                else:
                    case = "G2-ii"
                    new, bound = T | {4 * t1}, 4 * t1
        if not playable(new, spf):
            problems.append(f"constructed set not playable in case {case}")
        if sum(new) > opt_m:
            problems.append("constructed set beats opt(n-1)")
        if sum(T) > opt_m - min(6 * P1, 4 * t1):
            problems.append("inequality sum T <= opt(n-1) - min(6P1, 4t') fails")
        delta = opt_m + n - opt_n
        law = delta == 6 * P1
        if 4 * t1 >= 6 * P1 and not law:
            problems.append("4t' >= 6P1 but delta != 6P1")
        if 4 * t1 < 6 * P1 and delta < 4 * t1:
            problems.append("delta < 4t'")
        # Layer-3 detail: who lists 2P1 and 2P among S's layer-3 members, and 14P1.
        L3 = layer_lists(S, n, 3, spf)
        l2p1 = sorted(x for x, L in L3.items() if 2 * P1 in L)
        l2p = sorted(x for x, L in L3.items() if 2 * P in L)
        note = ""
        if 14 * P1 <= n:
            note = f"  [14P1 = {14 * P1} on board; in S: {14 * P1 in S}; listers of 2P1 in S3: {l2p1}]"
        if any(x not in (4 * P1, 6 * P1, 10 * P1, 14 * P1) for x in l2p1):
            problems.append(f"unexpected lister of 2P1: {l2p1}")
        if any(x not in (4 * P, 6 * P, 10 * P) for x in l2p):
            problems.append(f"unexpected lister of 2P: {l2p}")
        key = (case, 6 * P in S, 4 * t1 in S, 10 * P1 in S, 14 * P1 in S if 14 * P1 <= n else None, 6 * t1 in S,
               9 * P1 in S, 10 * P in S)
        cases[case] = cases.get(case, 0) + 1
        if problems or note:
            print(f"  {n} = 12*{P} (P1 {P1}, t' {t1}): case {case}, delta {delta}, 6P1 {6 * P1}, 4t' {4 * t1}: "
                  + "; ".join(problems) + note)
        if problems:
            bad += 1
    print(f"  {total} games checked, {bad} with problems; cases met: {cases}")
    return total


# ----------------------------------------------------------------------------------------------------- part C
def ustar_greedy(n, spf):
    """Descending greedy on the sources of n, playability by the residual of the own instance (sources list all their
    maximal factors; nothing in the kept set is a maximal factor of another source)."""
    kept = {}
    count = {}
    for s in range(n, n // 2, -1):
        L = mf(s, spf)
        kept[s] = L
        if residual_lists(kept):
            del kept[s]
    return set(kept)


def part_c(res):
    spf = sieve(5100)
    print("C. U*(n) by my own descending greedy, against the hypothesis, at a few games")
    for n in (276, 444, 1668, 2004, 2316, 2748, 4308):
        P = n // 12
        P1 = prev_prime(P, spf)
        u = ustar_greedy(n, spf)
        S = set(res[n][1])
        src = {x for x in S if x > n // 2}
        ts = [t for t in range(2, 3 * P // 2 + 1) if spf[t] == t and 3 * t > 4 * P and 8 * t in u]
        u3 = {x for x in u if omega(x, spf) >= 3}
        print(f"  {n}: 8P, 8P1, 12P1 in U*: {8 * P in u}, {8 * P1 in u}, {12 * P1 in u}; t' with 8t' in U*: {ts}; "
              f"U*_(>=3) subset of S: {u3 <= S}; sources of S == U*: {src == u}; 14P1 in U*: {14 * P1 in u if 14 * P1 <= n else '-'}")


# ----------------------------------------------------------------------------------------------------- part D
def part_d(samples, seed=1):
    """Random layer-4 instances.  Members: a random playable set of layer-4 numbers <= n holding the key members.
    Pool: layer-3 numbers <= 6P less a random set M3 of layer-3 'moves', arranged per case."""
    rng = random.Random(seed)
    spf = sieve(5100)
    print("D. random layer-4 instances: the layer-4 claim of each case, by the residual of the constructed instance")
    totals = {}
    fails = 0
    for n in (276, 444, 996, 1668, 2004):
        P = n // 12
        P1 = prev_prime(P, spf)
        half = n // 2
        l4 = [x for x in range(2, n + 1) if omega(x, spf) == 4]
        l3 = [x for x in range(2, half + 1) if omega(x, spf) == 3]
        tcands = [t for t in range(2, 3 * P // 2 + 1) if spf[t] == t and 3 * t > 4 * P]
        eights = [x for x in l4 if x % 8 == 0 and x not in (8 * P, 8 * P1)]
        for _ in range(samples):
            t1 = rng.choice(tcands)
            key = {12 * P, 8 * P, 8 * P1, 12 * P1, 8 * t1}
            case_wanted = rng.choice(["A", "B"])
            # layer-3 moves
            M3 = {x for x in l3 if rng.random() < 0.12 and x not in (4 * P1, 6 * P1, 4 * t1, 8, 12)}
            if case_wanted == "B":
                M3.add(6 * P)
                M3.discard(6 * P1)
                if rng.random() < 0.3:
                    M3.add(4 * P1)
                else:
                    M3.discard(4 * P1)
                M3.discard(4 * P)
                if rng.random() < 0.3:
                    M3.add(4 * P)
            else:
                M3.discard(6 * P)
                if rng.random() < 0.5:
                    M3.add(4 * P)
            # bias toward another 8u paying 8: make some 4u a move so that 8u must pay 8
            for e in rng.sample(eights, min(3, len(eights))):
                if rng.random() < 0.5 and e // 2 <= half and e // 2 not in (4 * P, 4 * P1, 4 * t1):
                    M3.add(e // 2)
            pool = {x for x in l3 if x not in M3}
            mem = set(key) | {x for x in l4 if x > half and rng.random() < 0.7} | {x for x in l4 if x <= half and rng.random() < 0.15}
            mem -= M3  # not relevant (M3 is layer 3) but keep clean
            L = {x: mf(x, spf) & pool for x in mem}
            # make it playable by removing random non-key members of the residual
            ok = True
            while True:
                R = residual_lists(L)
                if not R:
                    break
                choices = [x for x in R if x not in key]
                if not choices:
                    ok = False
                    break
                del L[rng.choice(choices)]
            if not ok:
                totals["unusable"] = totals.get("unusable", 0) + 1
                continue
            S4 = set(L)

            def can(**fix):
                LL = {x: set(v) for x, v in L.items()}
                for x, f in fix.items():
                    LL[int(x)] = {f} if f in LL[int(x)] else set()
                return not residual_lists(LL)

            def new_instance(drop_pool, add_pool, new_members=()):
                pool2 = (pool - set(drop_pool)) | set(add_pool)
                pool2.discard(6 * P)  # a source on board n-1
                mem2 = (S4 - {12 * P}) | set(new_members)
                return {x: mf(x, spf) & pool2 for x in mem2}

            if 6 * P not in M3:
                if 4 * P not in M3:
                    case = "A1/A2"
                    inst = new_instance([], [])
                else:
                    case = "A3"
                    inst = new_instance([4 * t1], [4 * P])
            else:
                if 4 * P1 in M3:
                    case = "G4"
                    inst = new_instance([6 * P1, 4 * t1], [4 * P1])
                elif can(**{str(12 * P): 12}):
                    case = "B1"
                    # sub-case with another 8u paying 8 while 12P pays 12, 12P1 pays 6P1, 8P1 pays 4P1
                    sub = "plain"
                    for e in eights:
                        if e in S4 and e != 8 * t1 and can(**{str(12 * P): 12, str(12 * P1): 6 * P1, str(8 * P1): 4 * P1, str(e): 8}):
                            sub = "other-8u-pays-8"
                            break
                    if sub == "plain" and can(**{str(12 * P): 12, str(12 * P1): 6 * P1, str(8 * P1): 4 * P1, str(8 * t1): 8}):
                        sub = "8t'-pays-8"
                    elif sub == "plain" and can(**{str(12 * P): 12, str(12 * P1): 6 * P1, str(8 * P1): 4 * P1, str(8 * P): 8}):
                        sub = "8P-pays-8"
                    case = "B1:" + sub
                    inst = new_instance([6 * P1], [])
                elif can(**{str(12 * P): 4 * P, str(12 * P1): 12}):
                    case = "G2-i"
                    inst = new_instance([6 * P1], [])
                else:
                    case = "G2-ii"
                    inst = new_instance([4 * t1], [])
            good = not residual_lists(inst)
            totals[case] = totals.get(case, 0) + 1
            if not good:
                fails += 1
                print(f"  FAIL n {n} t' {t1} case {case}: members {sorted(S4)} M3 {sorted(M3)}")
    print(f"  samples by case: {totals}; failures: {fails}")


if __name__ == "__main__":
    pmax = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    samples = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    part_a(pmax)
    res = load_results()
    part_b(res)
    part_c(res)
    part_d(samples)
