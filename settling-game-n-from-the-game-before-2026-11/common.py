"""Shared loaders and number tables for the succession brief's scripts (standard library only).

Every script here runs as `nice -n 19 python3 -I SCRIPT` from this folder; -I keeps the folder off sys.path, so each
script adds it explicitly before importing this module.
"""

import csv
import gzip
import json
import os

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
GAMES_CSV = "/home/brian/taxman_work/lab/work/gapdash/games.csv"
NOTEBOOK = "/home/brian/taxman_work/research/solver/notebook"
ARRIVAL = os.path.join(NOTEBOOK, "the-arrival-of-n-in-the-frame-model-2026-10/arrival.jsonl.gz")
SINGLE_LOSS = os.path.join(NOTEBOOK, "the-smallest-single-loss-over-all-moves-2026-10/core_full.jsonl")
STEPS_JSON = os.path.join(NOTEBOOK, "search/how-the-optimal-game-changes-with-n-2026-11/steps.json")
HERE = os.path.dirname(os.path.abspath(__file__))


def jsonl(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        for text in f:
            if text.strip():
                yield json.loads(text)


def results():
    """The committed chain, one line a game 1..5060, keyed by n."""
    return {x["n"]: x for x in jsonl(RESULTS)}


def games_csv():
    """games.csv of the gap dashboard, keyed by n, with numeric fields converted."""
    out = {}
    with open(GAMES_CSV) as f:
        for row in csv.DictReader(f):
            r = {}
            for k, v in row.items():
                if v == "":
                    r[k] = None
                elif k == "kind":
                    r[k] = v
                else:
                    r[k] = int(v)
            out[r["n"]] = r
    return out


def arrival():
    """The arrival entry's lines, boards 3..8191, keyed by n."""
    return {x["n"]: x for x in jsonl(ARRIVAL)}


def single_loss():
    """The single-loss rule's lines, n = 2..4955, keyed by n."""
    return {x["n"]: x for x in jsonl(SINGLE_LOSS)}


def factor(n):
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def sieve_spf(limit):
    """Smallest prime factor of every number up to limit."""
    spf = list(range(limit + 1))
    for p in range(2, int(limit ** 0.5) + 1):
        if spf[p] == p:
            for m in range(p * p, limit + 1, p):
                if spf[m] == m:
                    spf[m] = p
    return spf


def maximal_factors(x, spf):
    """{x/p : p prime, p | x}; for a prime, {1}."""
    out, y = set(), x
    while y > 1:
        p = spf[y]
        out.add(x // p)
        while y % p == 0:
            y //= p
    return out


def playable(members, n, spf):
    """Whether the set `members` of {2..n} is playable on board n: peel its own instance (the peel theorem P4).

    Members are the set; the pool is the union of their maximal factors less the set; a member lists its maximal
    factors outside the set.  A front move pairs a member listing one live factor with it; a back move pairs a live
    factor listed by one live member with that member.  Playable iff every member gets paired.
    """
    members = set(members)
    lists = {x: maximal_factors(x, spf) - members for x in members}
    listers = {}
    for x, fs in lists.items():
        for f in fs:
            listers.setdefault(f, set()).add(x)
    live_m = set(members)
    live_f = set(listers)
    stack_m = [x for x in members if len(lists[x]) <= 1]
    stack_f = [f for f in live_f if len(listers[f]) == 1]

    def remove_pair(x, f):
        live_m.discard(x)
        live_f.discard(f)
        for g in lists[x]:
            if g in live_f:
                listers[g].discard(x)
                if len(listers[g]) == 1:
                    stack_f.append(g)
        for y in listers.get(f, ()):
            if y in live_m and y != x:
                lists[y].discard(f)
                if len(lists[y]) <= 1:
                    stack_m.append(y)

    while live_m:
        moved = False
        while stack_m:
            x = stack_m.pop()
            if x not in live_m:
                continue
            fs = [g for g in lists[x] if g in live_f]
            if not fs:
                return False
            if len(fs) == 1:
                remove_pair(x, fs[0])
                moved = True
                break
        if moved:
            continue
        while stack_f:
            f = stack_f.pop()
            if f not in live_f:
                continue
            ys = [y for y in listers[f] if y in live_m]
            if len(ys) == 1:
                remove_pair(ys[0], f)
                moved = True
                break
            if not ys:
                live_f.discard(f)
        if not moved:
            return False
    return True


def residual(members, spf):
    """The residual of the own instance of `members` (Theorems P5, P7): dismantling deletes, while it can, a member
    that lists a factor no other remaining member lists.  Empty iff the set is playable."""
    members = set(members)
    lists = {x: maximal_factors(x, spf) - members for x in members}
    listers = {}
    for x, fs in lists.items():
        for f in fs:
            listers.setdefault(f, set()).add(x)
    alive = set(members)
    stack = [f for f, s in listers.items() if len(s) == 1]
    while stack:
        f = stack.pop()
        s = listers[f]
        if len(s) != 1:
            continue
        (x,) = tuple(s)
        alive.discard(x)
        for g in lists[x]:
            listers[g].discard(x)
            if len(listers[g]) == 1:
                stack.append(g)
    return alive


def legal_order(members, n, spf):
    """A legal order of a playable set: a payment scheme from peel's pairs, then a topological order of its
    precedence (a -> b when pay(a) | b or a | b), checked by replay.  Returns (order, taxes) or None."""
    members = set(members)
    lists = {x: maximal_factors(x, spf) - members for x in members}
    pay = {}
    live_m, live_f = set(members), set().union(*lists.values()) if lists else set()
    while live_m:
        moved = False
        for x in sorted(live_m):
            fs = [g for g in lists[x] if g in live_f]
            if len(fs) == 1:
                pay[x] = fs[0]
                live_m.discard(x)
                live_f.discard(fs[0])
                moved = True
                break
        if moved:
            continue
        for f in sorted(live_f):
            ys = [y for y in live_m if f in lists[y]]
            if len(ys) == 1:
                pay[ys[0]] = f
                live_m.discard(ys[0])
                live_f.discard(f)
                moved = True
                break
        if not moved:
            return None
    succ = {x: set() for x in members}
    indeg = {x: 0 for x in members}
    for a in members:
        for b in members:
            if a != b and (b % pay[a] == 0 or b % a == 0):
                succ[a].add(b)
                indeg[b] += 1
    ready = sorted(x for x in members if indeg[x] == 0)
    order = []
    while ready:
        x = ready.pop(0)
        order.append(x)
        for b in sorted(succ[x]):
            indeg[b] -= 1
            if indeg[b] == 0:
                ready.append(b)
        ready.sort()
    if len(order) != len(members):
        return None
    pot = set(range(1, n + 1))
    taxes = []
    for x in order:
        tax = {d for d in pot if d < x and x % d == 0}
        if x not in pot or not tax:
            return None
        pot -= tax | {x}
        taxes.append(sorted(tax))
    return order, taxes
