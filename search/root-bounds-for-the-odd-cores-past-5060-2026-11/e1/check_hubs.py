#!/usr/bin/env python3
"""The hub test of E11 at a run's leaf, from the definitions, with the brief's parity.py and cores.py (no code of the
solver).  The leaf is S = G + leaf_promotions.  In each layer, the fiber of a prime p > B is S's members whose largest
prime is p; member x = m·p lists its hub m (if p does not divide m and m is not in S) and its fiber factors (the
maximal factors divisible by p not in S).  Its demand d_p is the members less a largest matching into fiber factors;
a choice is d_p members with hubs whose others match into fiber factors; the hubs of all choices must be distinct.
The layer passes if some choice for every fiber with demand leaves the smooth sub-instance playable without the
chosen hubs.  For each layer: the demands (p: d_p of members, hubs available) and whether it passes, by an exhaustive
search with the same cut as the solver's (a step that already stalls the smooth members), up to --budget tests.

    python3 -I check_hubs.py RESULTS.jsonl [--budget N]     # every line with a leaf
"""

import itertools
import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import cores as C  # noqa: E402
import parity as P  # noqa: E402


def largest_prime(x):
    big, p = 1, 2
    while p * p <= x:
        while x % p == 0:
            big, x = p, x // p
        p += 1
    return max(big, x) if x > 1 else big


def matching(lists, members):
    """The size of a largest matching of `members` into the factors they list."""
    owner = {}

    def augment(u, seen):
        for f in lists[u]:
            if f in seen:
                continue
            seen.add(f)
            if f not in owner or augment(owner[f], seen):
                owner[f] = u
                return True
        return False

    return sum(1 for u in members if augment(u, set()))


def layer_test(k, s, om, mf, b, budget):
    layer = [x for x in s if om[x] == k]
    smooth = [x for x in layer if largest_prime(x) <= b]
    slists = {x: set(f for f in mf[x] if f not in s) for x in smooth}
    fibers = {}
    for x in layer:
        p = largest_prime(x)
        if p > b:
            fibers.setdefault(p, []).append(x)
    report, choices = {}, []
    for p in sorted(fibers):
        mem = fibers[p]
        lists = {x: [f for f in mf[x] if f % p == 0 and f not in s] for x in mem}
        hub = {x: x // p for x in mem if (x // p) % p != 0 and (x // p) not in s}
        d = len(mem) - matching(lists, mem)
        if d == 0:
            continue
        opts = []
        for combo in itertools.combinations(sorted(hub), d):
            rest = [x for x in mem if x not in combo]
            if matching(lists, rest) == len(rest):
                opts.append(frozenset(hub[x] for x in combo))
        report[p] = [d, len(mem), len(hub), len(opts)]
        if not opts:
            return report, "fails: a fiber has no choice"
        opts.sort(key=lambda o: len(o & set().union(*slists.values())) if slists else 0)
        choices.append(opts)
    if not choices:
        return report, "no demand"
    choices.sort(key=len)
    tests = [0]

    def search(i, used):
        if i == len(choices):
            return True
        for o in choices[i]:
            if o & used:
                continue
            u = used | o
            tests[0] += 1
            if tests[0] > budget:
                raise TimeoutError
            if C.residual(smooth, {x: slists[x] - u for x in smooth}):
                continue
            if search(i + 1, u):
                return True
        return False

    try:
        ok = search(0, frozenset())
    except TimeoutError:
        return report, f"undecided after {budget} tests"
    return report, ("passes" if ok else "fails") + f" ({tests[0]} tests)"


def main():
    budget = 200000
    if "--budget" in sys.argv:
        budget = int(sys.argv[sys.argv.index("--budget") + 1])
    for raw in open(sys.argv[1]):
        line = json.loads(raw)
        if not line.get("leaf_promotions"):
            continue
        n, b = line["n"], line["B"]
        om, mf = P.omega_and_mf(n)
        s = set(P.greedy_basis(n, om, mf)) | set(line["leaf_promotions"])
        out = {"n": n, "B": b, "hubs": line.get("hubs", False), "layers": {}}
        for k in sorted({om[x] for x in s}):
            report, verdict = layer_test(k, s, om, mf, b, budget)
            if report:
                out["layers"][k] = {"demands (p: d, members, with hubs, choices)": report, "verdict": verdict}
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
