#!/usr/bin/env python3
"""Uniform GF(3) signings that kill a lifted template.  A template core (members m·P, columns: hubs m and fiber factors
(m/q)·P) gets entries sigma(m, m/q) in {1, 2} that depend only on the cofactors (the same in every fiber) and
sigma(m, hub) = h(m) in {1, 2}.  Search all such signings for one under which the core's rows are dependent over GF(3),
i.e. the GF(3) rank is below the number of members.  Reports how many signings kill each core and whether one signing
kills every instance of the template found (several boards)."""
import json, sys, itertools
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P
import cores as C

def largest_prime(x):
    p, big = 2, 1
    while p * p <= x:
        while x % p == 0:
            big = p; x //= p
        p += 1
    return max(big, x) if x > 1 else big

def rank_gf3(rows):
    rows = [r[:] for r in rows]
    rank, ncol = 0, len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = next((i for i in range(rank, len(rows)) if rows[i][c] % 3), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        inv = 1 if rows[rank][c] % 3 == 1 else 2
        rows[rank] = [(v * inv) % 3 for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][c] % 3:
                f = rows[i][c]
                rows[i] = [(a - f * b) % 3 for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank

def template_cores(n, B=23):
    om, mf = P.omega_and_mf(n)
    d = P.board(n)
    h = set(d["greedy_basis"] + d["heaviest_low"])
    out = []
    r = d["residual"].get("4")
    if not r:
        return out
    layer = [x for x in h if om[x] == 4]
    lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
    res = set(r["members"])
    seen = set()
    import random
    random.seed(5)
    for _ in range(120):
        order = list(res); random.shuffle(order)
        c = C.minimal_core(res, lists, order)
        if not c or frozenset(c) in seen or any(largest_prime(x) <= B for x in c):
            continue
        seen.add(frozenset(c))
        out.append((sorted(c), {x: sorted(lists[x]) for x in c}))
    return out

def edges_of(core, lists):
    """Cofactor edges (m, m/q) and hub cofactors of a lifted core."""
    E, Hb = set(), set()
    for x in core:
        p = largest_prime(x); m = x // p
        for f in lists[x]:
            if f % p == 0:
                E.add((m, f // p))
            else:
                assert f == m, (x, f)
                Hb.add(m)
    return sorted(E), sorted(Hb)

def killers(core, lists, E, Hb):
    cols = sorted({f for x in core for f in lists[x]})
    ci = {c: i for i, c in enumerate(cols)}
    keys = [("e", e) for e in E] + [("h", m) for m in Hb]
    found = []
    for bits in itertools.product((1, 2), repeat=len(keys)):
        sig = dict(zip(keys, bits))
        rows = []
        for x in core:
            p = largest_prime(x); m = x // p
            row = [0] * len(cols)
            for f in lists[x]:
                row[ci[f]] = sig[("e", (m, f // p))] if f % p == 0 else sig[("h", m)]
            rows.append(row)
        if rank_gf3(rows) < len(core):
            found.append(bits)
    return keys, found

boards = [int(a) for a in sys.argv[1:]] or [5000]
by_pattern = {}
for n in boards:
    for core, lists in template_cores(n):
        E, Hb = edges_of(core, lists)
        pat = tuple(sorted({x // largest_prime(x) for x in core}))
        if len(E) + len(Hb) > 18:
            print(json.dumps({"n": n, "pattern": pat, "size": len(core), "skipped": "too many keys", "keys": len(E) + len(Hb)}), flush=True)
            continue
        keys, found = killers(core, lists, E, Hb)
        plain = tuple([1] * len(keys)) in found
        print(json.dumps({"n": n, "pattern": pat, "primes": sorted({largest_prime(x) for x in core}), "size": len(core),
                          "cols": len({f for x in core for f in lists[x]}), "edges": len(E), "hubs": len(Hb),
                          "signings": 2 ** len(keys), "killing": len(found), "plain_kills": plain}), flush=True)
        by_pattern.setdefault(pat, []).append((keys, set(found)))
for pat, inst in by_pattern.items():
    if len(inst) < 2:
        continue
    # a signing common to all instances: compare on the shared keys only
    common_keys = set(inst[0][0])
    for k, _ in inst[1:]:
        common_keys &= set(k)
    common_keys = sorted(common_keys, key=str)
    def project(keys, found):
        idx = [keys.index(k) for k in common_keys]
        return {tuple(b[i] for i in idx) for b in found}
    inter = None
    for keys, found in inst:
        pr = project(keys, found)
        inter = pr if inter is None else inter & pr
    print(json.dumps({"pattern": pat, "instances": len(inst), "shared_keys": len(common_keys), "common_killing_signings": len(inter)}))
