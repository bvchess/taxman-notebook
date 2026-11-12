#!/usr/bin/env python3
"""E7: summary of the odd cores found by window_cores.py (cores_*.jsonl) and by the Rust example windowcores
(rust_cores_*.jsonl).

    nice -n 19 python3 -I e7/summarize.py FILE [FILE ...] [--cofactors C1,C2,...]

For each file: the number of odd cores (T, X) (columns in canonical order), the number of distinct T, and the
*minimal* ones: (T, X) such that no proper nonempty part of T is a core of the same instance (each sub-core of an odd
core is one too, with the rest of T among the moves, so every odd core holds a minimal one).  A window of cofactor
c' <= c holds exactly the cores whose rows are all at most c' (the conditions involve T's own lists alone), so
--cofactors lists the minimal cores for each smaller cofactor too.  Each column of a core is shown as T rows / X rows,
with dim, the dimension of the space of subsets of the column's part of T whose column lists sum to 0; the core is
independent exactly when these spaces, read as sets of rows, are in direct sum.
"""
import json
import sys
from collections import defaultdict


def primes_of(k):
    out, p = [], 2
    while p * p <= k:
        if k % p == 0:
            out.append(p)
            while k % p == 0:
                k //= p
        p += 1
    if k > 1:
        out.append(k)
    return out


def lists(core):
    """The list of each member (k, j) of T: its column factors in the pool and its hub, as hashable labels."""
    T = {tuple(x) for x in core["T"]}
    X = {tuple(x) for x in core["X"]}
    out_hubs = set(core.get("hubs_out", []))
    res = {}
    for k, j in T:
        fs = set()
        for q in primes_of(k):
            f = k // q
            if (f, j) not in T and (f, j) not in X:
                fs.add(("col", f, j))
        if k not in out_hubs:
            fs.add(("hub", k))
        res[(k, j)] = fs
    return res


def residual(ls, alive):
    alive = set(alive)
    listers = defaultdict(set)
    for x in alive:
        for f in ls[x]:
            listers[f].add(x)
    stack = [f for f, s in listers.items() if len(s) == 1]
    while stack:
        f = stack.pop()
        s = listers[f]
        if len(s) != 1:
            continue
        (x,) = tuple(s)
        alive.discard(x)
        for g in ls[x]:
            listers[g].discard(x)
            if len(listers[g]) == 1:
                stack.append(g)
    return alive


def minimal(core):
    ls = lists(core)
    T = set(ls)
    assert residual(ls, T) == T, "not a core"
    return all(not residual(ls, T - {x}) for x in T)


def column_dims(core):
    ls = lists(core)
    out = {}
    for j in sorted({j for _, j in ls}):
        members = [x for x in ls if x[1] == j]
        coords = {}
        basis, rank = {}, 0
        for x in members:
            v = 0
            for f in ls[x]:
                if f[0] == "col":
                    v |= 1 << coords.setdefault(f, len(coords))
            while v:
                p = v.bit_length() - 1
                if p not in basis:
                    basis[p] = v
                    rank += 1
                    break
                v ^= basis[p]
        out[j] = len(members) - rank
    return out


def show(core):
    T, X = defaultdict(list), defaultdict(list)
    for k, j in core["T"]:
        T[j].append(k)
    for k, j in core["X"]:
        X[j].append(k)
    dims = column_dims(core)
    parts = [f"col {j}: T {sorted(T[j])} / X {sorted(X[j])} (dim {dims[j]})" for j in sorted(T)]
    hubs = core.get("hubs_out", [])
    rows = {k for k, _ in core["T"]}
    return "; ".join(parts) + (f"; hubs out {hubs}" if hubs else "") + f"; rows {len(rows)}, members {len(core['T'])}"


def main():
    args = sys.argv[1:]
    cofactors = []
    if "--cofactors" in args:
        at = args.index("--cofactors")
        cofactors = [int(x) for x in args[at + 1].split(",")]
        args = args[:at] + args[at + 2:]
    for path in args:
        cores = [json.loads(t) for t in open(path) if t.strip()]
        print(f"== {path}: {len(cores)} odd cores (T, X)")
        if not cores:
            continue
        by_t = defaultdict(list)
        for c in cores:
            by_t[tuple(sorted(map(tuple, c["T"])))].append(c)
        mins = [c for c in cores if minimal(c)]
        indep = sum(1 for c in cores if c["T_plus_X_independent"])
        cols = defaultdict(int)
        for c in cores:
            cols[len({j for _, j in c["T"]})] += 1
        print(f"   distinct T: {len(by_t)}; with T + X independent: {indep}; nonempty columns: {dict(sorted(cols.items()))}"
              f"; minimal (T, X): {len(mins)}, with distinct T: {len({tuple(sorted(map(tuple, c['T']))) for c in mins})}")
        for cp in cofactors or [None]:
            sel = [c for c in mins if cp is None or max(k for k, _ in c["T"] + c["X"]) <= cp]
            if cp is not None:
                allc = [c for c in cores if max(k for k, _ in c["T"] + c["X"]) <= cp]
                print(f"   cofactor {cp}: {len(allc)} odd cores, {len(sel)} minimal")
            seen = set()
            for c in sorted(sel, key=lambda c: (len(c["T"]), sorted(map(tuple, c["T"])), sorted(map(tuple, c["X"])))):
                key = (tuple(sorted(map(tuple, c["T"]))), tuple(sorted(map(tuple, c["X"]))))
                if key in seen:
                    continue
                seen.add(key)
                print("     " + show(c))


if __name__ == "__main__":
    main()
