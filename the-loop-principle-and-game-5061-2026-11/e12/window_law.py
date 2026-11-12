#!/usr/bin/env python3
"""E12: the finite case table of a family law delta(cP) >= L, by the window argument (study-report.md, Sections 5.3,
11.2 and 14).

    nice -n 19 python3 -I e12/window_law.py FAMILY [--no-sources] [--table FILE] [--local A,D] [--not-held K:J,...]

FAMILY is a key of FAMILIES below: 8, 12, 16, 40 (the window alone), 16h8 and 12h8 (with the column of the holder of
hub 8, 8·q(2P) and 8·q(3P/2)), 21 (column 0 alone), 21m1 (with column -1), 20, 24, 25.  An *extra column* is the
column of a prime q given by a rule (the largest prime up to F·P, or the i-th prime above P) and assumed to lie in
(lo·P, hi·P]; its rows are the composite k with k·hi <= c, and a composite k with k·lo < c < k·hi is refused.  The
cone then is the window's times these intervals.  The lemma needs 2·p² > n for every prime p of the region.

With --local A,D the witnesses are searched among the state's own candidate cells less up to D of them plus up to A
others (for 40P, whose 22 candidate cells make the full search too large); a state that search does not close is
open for that search only.  --not-held lists source cells (row:column) that S does not hold, the others being fixed
in S (at 40P all the window's sources together have a core, and the chain's clean games hold all but 22P_1).

The window.  n = c·P with the columns P_0 = P, P_1, ..., P_d clean: (c + 1)·P_j > n.  The cell (k, j) = k·P_j for a
composite k <= c (the members that matter; layer-2 cells and P_j are never moves from 187 on, by F4 and F10, and a
layer-2 cell above n/2 is no factor of a cell).  It lists its column factors (k/q, j), one for each prime q | k, and
its hub k.  In a clean column a column factor is listed by cells of its own column only, and a cell lists nothing but
column factors and its hub; the hubs are the only factors cells share with the rest of the board.

The lemma that glues (core domination; proved in README.md from the core theorem P7).  Let S be playable on board n,
W its cells, O = S - W, and W' a set of cells on board n - 1.  Call a nonempty X ⊆ Z *column-closed in Z* when each
column factor in the pool of Z (a prime row's always; a composite row's when its cell is not in Z) that a member of X
lists is listed by another member of X; its *signature* is (R1, R2), the rows of X used by one member of X and by two
or more.  If every column-closed X ⊆ W' has a column-closed Y ⊆ W with rows(Y) ⊇ rows(X) and R1(Y) ⊆ R1(X), then
O + W' is playable on board n - 1.  (A core of O + W' meets W' in a column-closed X; swapping X for Y gives a core of
S.)  So delta(n) >= sum(W') - sum(W) + n for every such W'.

What is enumerated.  States: every set W of cells of board n holding n that has no core in its own window instance
(all hubs in the pool) and, unless --no-sources, holds every source cell (rows k > c/2, layer >= 3: statement U gives
them when they lie in U*(n)).  For each state, a witness W' on board n - 1 (the same source cells less n, any
candidate cells, rows k <= c/2) with the domination above and sum(W') - sum(W) + n - L >= 0 at every extreme ray of
the cone of clean primes P = P_0 >= P_1 >= ... >= P_d >= c·P/(c + 1), so for every prime P whose window is clean to
depth d.  A state with no witness is *open*; an open state that some W+ of board n (holding n, dominating W, and
heavier on the whole cone) improves is no optimal set's, and is reported as *excluded by optimality*.
"""
import itertools
import json
import math
import sys
import time
from fractions import Fraction

F = Fraction
LAW8, LAW12 = {(4, 1): 1}, {(6, 1): 1}
LAW16 = {(8, 1): 1, (6, 2): 1, (4, 3): 1, (6, 1): -1, (4, 2): -1}
LAW21 = {(10, 0): 1, (9, 0): -1}
# key: (c, d, law as {(k, j): coefficient} (delta >= sum coefficient·k·P_j), extra columns)
# an extra column: (name, rule, lo, hi); rule ("le", F) is the largest prime <= F·P, ("next", i) the i-th prime above P
FAMILIES = {
    "8": (8, 1, LAW8, []),
    "12": (12, 1, LAW12, []),
    "16": (16, 3, LAW16, []),
    "40": (40, 1, {(18, 1): 1}, []),
    "12h8": (12, 1, LAW12, [("q", ("le", F(3, 2)), F(4, 3), F(3, 2))]),
    "16h8": (16, 3, LAW16, [("q", ("le", F(2)), F(16, 9), F(2))]),
    "21": (21, 0, LAW21, []),
    "21m1": (21, 0, LAW21, [("P-1", ("next", 1), F(1), F(21, 20))]),
    "20": (20, 2, {(10, 1): 1, (6, 2): 1, (9, 2): 1, (6, 1): -1, (10, 2): -1}, []),
    "24": (24, 2, {(12, 1): 1, (10, 2): 1, (10, 1): -1}, []),
    "25": (25, 2, {(9, 1): 1}, []),
}
LAWS = {int(k): v[:3] for k, v in FAMILIES.items() if k.isdigit()}  # the first round's families, as before


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


def omega(k):
    n, p = 0, 2
    while p * p <= k:
        while k % p == 0:
            k //= p
            n += 1
        p += 1
    return n + (k > 1)


class Window:
    def __init__(self, c, d, law, sources_fixed=True, extras=()):
        self.c, self.d, self.law = c, d, law
        self.rows = [k for k in range(2, c + 1) if omega(k) >= 2]
        self.rbit = {k: i for i, k in enumerate(self.rows)}
        self.extras = list(extras)
        self.names = {j: f"P{j}" for j in range(d + 1)}
        col_rows = {j: list(self.rows) for j in range(d + 1)}
        self.kind = {}
        for k in self.rows:
            for j in range(d + 1):
                self.kind[(k, j)] = "source" if 2 * k > c else "candidate"
        for e, (name, _rule, lo, hi) in enumerate(self.extras):
            j = d + 1 + e
            self.names[j] = name
            col_rows[j] = []
            for k in self.rows:
                if k * hi <= c:
                    col_rows[j].append(k)
                    if 2 * k * lo >= c:
                        self.kind[(k, j)] = "source"
                    elif 2 * k * hi <= c:
                        self.kind[(k, j)] = "candidate"
                    else:
                        raise ValueError(f"row {k} of column {name} is a source for some q and not for others")
                elif k * lo < c:
                    raise ValueError(f"row {k} of column {name} is on the board for some q and not for others")
        self.cells = [(k, j) for j in sorted(col_rows) for k in col_rows[j]]
        self.n = (c, 0)
        self.factors = {k: [k // q for q in primes_of(k)] for k in self.rows}
        self.composite = set(self.rows)
        self.sources = [x for x in self.cells if self.kind[x] == "source"]
        self.candidates = [x for x in self.cells if self.kind[x] == "candidate"]
        self.sources_fixed = sources_fixed
        r = Fraction(c, c + 1)
        # Extreme rays: those of P_0 = 1 >= P_1 >= ... >= P_d >= r, times the ends of each extra column's interval.
        base = [tuple([Fraction(1)] * (i + 1) + [r] * (d - i)) for i in range(d + 1)]
        ends = [(lo, hi) for _name, _rule, lo, hi in self.extras]
        self.rays = [b + tuple(t) for b in base for t in itertools.product(*ends)]
        # Integer arithmetic: every ray scaled by the common denominator of its coordinates (comparisons unchanged).
        self.scale = 1
        for ray in self.rays:
            for x in ray:
                self.scale = self.scale * x.denominator // math.gcd(self.scale, x.denominator)
        self.irays = [tuple(int(x * self.scale) for x in ray) for ray in self.rays]
        self.law_at = [sum(co * k * ray[j] for (k, j), co in law.items()) for ray in self.irays]

    def label(self, cells):
        return " ".join(f"{k}{self.names[j]}" for k, j in sorted(cells, key=lambda x: (x[1], x[0])))

    def weight_at(self, cells):
        """The weight of the cells at each ray, scaled by self.scale (integers)."""
        return [sum(k * ray[j] for k, j in cells) for ray in self.irays]

    def lists(self, Z):
        """Each member's list in the window instance of Z: column factors in the pool, and the hub."""
        out = {}
        for k, j in Z:
            fs = [("c", m, j) for m in self.factors[k] if m not in self.composite or (m, j) not in Z]
            out[(k, j)] = fs + [("h", k)]
        return out

    def coreless(self, Z):
        ls = self.lists(Z)
        alive = set(Z)
        listers = {}
        for x, fs in ls.items():
            for f in fs:
                listers.setdefault(f, set()).add(x)
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
        return not alive

    def signatures(self, Z):
        """The signatures (R1, R2) of the column-closed parts of Z, rows as bitmasks."""
        per_col = []
        for j in sorted(self.names):
            Zj = sorted((k for k, jj in Z if jj == j), reverse=True)
            pool_listers = {}
            for k in Zj:
                for m in self.factors[k]:
                    if m not in self.composite or (m, j) not in Z:
                        pool_listers.setdefault(m, []).append(k)
            # A factor's count is final once its lowest lister is decided (rows go down).
            check_at = {}
            for m, ls in pool_listers.items():
                check_at.setdefault(min(ls), []).append(m)
            masks = set()
            chosen = set()

            def rec(i, mask):
                if i == len(Zj):
                    masks.add(mask)
                    return
                k = Zj[i]
                for take in (True, False):
                    if take:
                        chosen.add(k)
                    if all(sum(1 for x in pool_listers[m] if x in chosen) != 1 for m in check_at.get(k, ())):
                        rec(i + 1, mask | (1 << self.rbit[k]) if take else mask)
                    if take:
                        chosen.discard(k)
            rec(0, 0)
            per_col.append(masks)
        states = {(0, 0)}
        for masks in per_col:
            new = set()
            for r1, r2 in states:
                for x in masks:
                    n2 = r2 | (r1 & x)
                    new.add(((r1 | x) & ~n2, n2))
            states = new
        states.discard((0, 0))
        return states

    @staticmethod
    def dominated(sig_new, sig_old, memo=None):
        """Every (R1', R2') of sig_new has an (R1, R2) in sig_old with rows ⊇ rows' and R1 ⊆ R1'.  With memo (a
        dict kept for one sig_old), each signature's answer is computed once."""
        if memo is not None and "items" in memo:
            items = memo["items"]
        else:
            by_r1 = {}
            for r1, r2 in sig_old:
                by_r1.setdefault(r1, []).append(r1 | r2)
            items = list(by_r1.items())
            if memo is not None:
                memo["items"] = items
        for sig in sig_new:
            if memo is not None and sig in memo:
                if not memo[sig]:
                    return False
                continue
            r1n, r2n = sig
            rows_n = r1n | r2n
            ok = any((r1 & ~r1n) == 0 and any((rows & rows_n) == rows_n for rows in rl) for r1, rl in items)
            if memo is not None:
                memo[sig] = ok
            if not ok:
                return False
        return True


def label(cells):
    return " ".join(f"{k}P{j}" for k, j in sorted(cells, key=lambda x: (x[1], x[0])))


def run(family, sources_fixed=True, table=None, local=None, not_held=()):
    c, d, law, extras = FAMILIES[str(family)]
    w = Window(c, d, law, sources_fixed, extras)
    label = w.label
    w.sources = [x for x in w.sources if x not in not_held]
    t0 = time.time()
    n = w.n
    old_free = [x for x in w.cells if x != n and not (sources_fixed and x in w.sources) and x not in not_held]
    new_free = [x for x in w.cells if x != n and not (sources_fixed and x in w.sources) and x not in not_held]
    fixed_old = [n] + ([x for x in w.sources if x != n] if sources_fixed else [])
    fixed_new = [x for x in w.sources if x != n] if sources_fixed else []
    # Witnesses: every coreless W' on board n - 1, with its signatures and weight at the rays.
    def coreless_sets(fixed, free):
        """Every C ⊆ free with fixed + C coreless (a down-closed family: a part of a playable set is playable)."""
        out = []

        def rec(i, C):
            out.append(tuple(C))
            for t in range(i, len(free)):
                C.append(free[t])
                if w.coreless(set(fixed) | set(C)):
                    rec(t + 1, C)
                C.pop()
        if w.coreless(set(fixed)):
            rec(0, [])
        return out
    sigs_new = {}
    states = [(C, set(fixed_old) | set(C)) for C in coreless_sets(fixed_old, old_free)]
    if local is None:
        witnesses = [(C, set(fixed_new) | set(C), w.weight_at(set(fixed_new) | set(C)))
                     for C in coreless_sets(fixed_new, new_free)]
    nval = [c * ray[0] for ray in w.irays]
    law_text = " + ".join(f"{co}·{k}{w.names[j]}" for (k, j), co in law.items())
    region = "" if not extras else " plus " + ", ".join(f"the column of {nm} in ({lo}·P, {hi}·P]"
                                                         for nm, _r, lo, hi in extras)
    print(f"== {family}P: c = {c}, depth {d}{region}, law delta >= {law_text}; "
          f"sources {'fixed in S' if sources_fixed else 'free'}"
          + (f" (all but {label(not_held)}, which S does not hold)" if not_held else "") + f"; {len(states)} states, "
          + (f"{len(witnesses)} coreless witness sets" if local is None else
             f"witnesses searched locally (up to {local[0]} cells added, {local[1]} dropped)")
          + f"; rays {[[str(x) for x in r] for r in w.rays]}", flush=True)
    closed, open_ = 0, []
    out = open(table, "w") if table else None
    for C, W0 in states:
        w0 = w.weight_at(W0)
        need = [w0[i] - nval[i] + w.law_at[i] for i in range(len(w.rays))]  # sum(W') must reach this at each ray
        sig_old = w.signatures(W0)
        found = None
        if local is None:
            pool = witnesses
        else:
            # Local search: the state's own candidate cells, less up to local[1] of them, plus up to local[0] others.
            base = [x for x in C]
            others = [x for x in new_free if x not in C]
            pool = []
            for nd in range(local[1] + 1):
                for dels in itertools.combinations(base, nd):
                    for na in range(local[0] + 1):
                        for adds in itertools.combinations(others, na):
                            Cn = tuple(sorted(set(base) - set(dels) | set(adds)))
                            Wn = set(fixed_new) | set(Cn)
                            pool.append((Cn, Wn, w.weight_at(Wn)))
        cands = [(min(wn[i] - need[i] for i in range(len(w.rays))), Cn, Wn) for Cn, Wn, wn in pool
                 if all(wn[i] >= need[i] for i in range(len(w.rays))) and (local is None or w.coreless(Wn))]
        cands.sort(key=lambda t: -t[0])
        memo = {}
        for slack, Cn, Wn in cands:
            key = tuple(sorted(Wn))
            if key not in sigs_new:
                sigs_new[key] = w.signatures(Wn)
            if w.dominated(sigs_new[key], sig_old, memo):
                found = (Cn, slack)
                break
        rec = {"state_cells": sorted(C), "witness_cells": sorted(found[0]) if found else None,
               "slack_min_over_rays_in_P": str(Fraction(found[1], w.scale)) if found else None}
        if found:
            closed += 1
        else:
            open_.append((C, W0))
        if out:
            out.write(json.dumps(rec) + "\n")
    # Optimality: an open state improved (dominated, heavier on the whole cone) by a W+ of board n is no optimal set's.
    excluded, really_open = [], []
    if open_:
        ups = [(C, W0, w.weight_at(W0)) for C, W0 in states]
        sigs_old = {}

        def sig_of(Z):
            key = tuple(sorted(Z))
            if key not in sigs_old:
                sigs_old[key] = w.signatures(Z)
            return sigs_old[key]
        for C, W0 in open_:
            w0 = w.weight_at(W0)
            sig_old = sig_of(W0)
            better = None
            memo = {}
            heavier = [t for t in ups if all(t[2][i] > w0[i] for i in range(len(w.rays)))]
            for Cp, Wp, wp in sorted(heavier, key=lambda t: -min(t[2][i] - w0[i] for i in range(len(w.rays)))):
                if w.dominated(sig_of(Wp), sig_old, memo):
                    better = Cp
                    break
            (excluded if better else really_open).append((C, better))
    print(f"   closed {closed}, open {len(open_)}: excluded by optimality {len(excluded)}, left open {len(really_open)}"
          f"; {time.time() - t0:.0f} s", flush=True)
    for C, _ in really_open:
        print(f"   OPEN: S holds {label(C) or '(no candidate cell)'}", flush=True)
    if out:
        out.close()
    return closed, excluded, really_open


def main():
    args = sys.argv[1:]
    table = None
    if "--table" in args:
        at = args.index("--table")
        table = args[at + 1]
        args = args[:at] + args[at + 2:]
    local = None
    if "--local" in args:
        at = args.index("--local")
        local = tuple(int(x) for x in args[at + 1].split(","))
        args = args[:at] + args[at + 2:]
    not_held = ()
    if "--not-held" in args:
        at = args.index("--not-held")
        not_held = tuple(tuple(int(v) for v in x.split(":")) for x in args[at + 1].split(","))
        args = args[:at] + args[at + 2:]
    run(args[0], sources_fixed="--no-sources" not in args, table=table, local=local, not_held=not_held)


if __name__ == "__main__":
    main()
