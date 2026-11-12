#!/usr/bin/env python3
"""E15's diagnosis: for the state W of the recorded set of n (committed, or the best-known one past the chain) and the
witness W' = the committed set of n - 1 on a region, the smallest column-closed X of W' that no column-closed Y of W
stands for (Y uses every row X uses, and uses once only rows X uses once).  Brute force over the column-closed parts
of each column, by the number of columns X uses; it shares no code with the Rust tool.

    nice -n 19 python3 -I e15/diag.py N P1,P2,... [MAX_COLUMNS]"""
import gzip
import itertools
import json
import sys

N = int(sys.argv[1])
PRIMES = [int(x) for x in sys.argv[2].split(",")]
MAXCOLS = int(sys.argv[3]) if len(sys.argv) > 3 else 3
RES = "/home/brian/taxman_work/research/.claude/worktrees/loops-e15/results/optimal.jsonl.gz"
BEST = "/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl"


def spf_table(m):
    s = list(range(m + 1))
    for p in range(2, int(m ** 0.5) + 1):
        if s[p] == p:
            for q in range(p * p, m + 1, p):
                if s[q] == q:
                    s[q] = p
    return s


SPF = spf_table(N + 10)


def primes_of(k):
    out = []
    while k > 1:
        p = SPF[k]
        out.append(p)
        while k % p == 0:
            k //= p
    return out


def composite(k):
    return k >= 4 and SPF[k] != k


sets = {}
with gzip.open(RES, "rt") as f:
    for line in f:
        r = json.loads(line)
        if r.get("n") in (N - 1, N):
            sets[r["n"]] = set(r["moves"])
if N not in sets:
    pre = '{"unsound":true,"n":%d,' % N
    best = None
    with open(BEST) as f:
        for line in f:
            if line.startswith(pre):
                r = json.loads(line)
                if best is None or r["score"] >= best["score"]:
                    best = r
    sets[N] = set(best["moves"])


def parts(p, Z):
    """Every column-closed part of the column of p whose cells are the rows Z (the empty one too)."""
    rows = sorted(Z, reverse=True)
    lists = {k: [m for m in (k // q for q in primes_of(k)) if not composite(m) or m not in Z] for k in rows}
    listers = {}
    for k in rows:
        for m in lists[k]:
            listers.setdefault(m, []).append(k)
    check_at = {}
    for m, ls in listers.items():
        check_at.setdefault(min(ls), []).append(m)
    out, chosen = [], set()

    def rec(i):
        if i == len(rows):
            out.append(frozenset(chosen))
            return
        k = rows[i]
        for take in (True, False):
            if take:
                chosen.add(k)
            if all(sum(1 for x in listers[m] if x in chosen) != 1 for m in check_at.get(k, ())):
                rec(i + 1)
            if take:
                chosen.discard(k)
    rec(0)
    return out


W = {p: {k for k in range(4, N // p + 1) if composite(k) and k * p in sets[N]} for p in PRIMES}
Wp = {p: {k for k in range(4, N // p + 1) if composite(k) and k * p in sets[N - 1] and k * p != N} for p in PRIMES}
for p in PRIMES:
    print(p, "W", sorted(W[p]), "W'", sorted(Wp[p]))

# Every Y profile of W, as (rows used at least once, rows used at least twice).
ys = {(frozenset(), frozenset())}
for p in PRIMES:
    ps = parts(p, W[p])
    ys = {(a | m, b | (a & m)) for a, b in ys for m in ps}
print("Y profiles of W:", len(ys))


def covered(xa, xb):
    xo = xa - xb
    return any(xa <= a and (a - b) <= xo for a, b in ys)


xparts = {p: [m for m in parts(p, Wp[p]) if m] for p in PRIMES}
found = []
for k in range(1, MAXCOLS + 1):
    for cols in itertools.combinations(PRIMES, k):
        for combo in itertools.product(*(xparts[p] for p in cols)):
            a, b = frozenset(), frozenset()
            for m in combo:
                a, b = a | m, b | (a & m)
            if not covered(a, b):
                found.append((sum(len(m) for m in combo), cols, combo, a, b))
    if found:
        break
found.sort(key=lambda t: t[0])
print("uncovered X's using", k, "columns:", len(found))
for size, cols, combo, a, b in found[:8]:
    cells = [f"{r}·{p}" for p, m in zip(cols, combo) for r in sorted(m)]
    print(f"  {size} cells: {' '.join(cells)}; rows once {sorted(a - b)}, twice {sorted(b)}")
