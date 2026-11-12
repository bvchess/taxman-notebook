#!/usr/bin/env python3
"""E7, the same enumeration as window_cores.py with the rows taken from the bottom up (see that file for the window
instance, the members, the pool and what is enumerated).

    nice -n 19 python3 -I e7/window_cores_up.py C D [--hubs-removable] [--list N] [--progress DEPTH]

Order.  Rows are decided from 4 up to c, all d + 1 columns of a row at once.  A member's factors lie in lower rows, so
its list is final when it is placed, and the members' lists are kept in an echelon basis over GF(2): a member whose
list is in the span of those placed before it cuts the branch at once.  A hub's listers are the cells of its own row,
so its condition is checked with the row.  The conditions of one column (each of its column factors and prime
factors in the pool listed by no member or by two or more, and a move only where a member lists it) are checked
through a table made first: every prefix of one column's states up the rows that extends to a full column meeting
them.  The columns are interchangeable, so only assignments whose columns, read as strings of states up the rows, are
in nondecreasing order are kept.

Each odd core is written as it is found to e7/up_cores_cC_dD[_hubs_removable].jsonl.
"""
import json
import os
import sys
import time

T, X, O = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))


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
    def __init__(self, c, d, hubs_removable=False):
        self.c, self.d, self.cols = c, d, d + 1
        self.hubs_removable = hubs_removable
        self.rows = [k for k in range(2, c + 1) if omega(k) >= 2]  # composite rows, ascending
        self.composite = set(self.rows)
        self.factors = {k: sorted(k // q for q in primes_of(k)) for k in self.rows}
        self.listers = {}
        for k in self.rows:
            for f in self.factors[k]:
                self.listers.setdefault(f, []).append(k)
        self.bit = {}
        for f in sorted(self.listers):
            for j in range(self.cols):
                self.bit[(f, j)] = len(self.bit)
        for k in self.rows:
            self.bit[("hub", k)] = len(self.bit)
        # A factor's condition is checked once its highest lister's row is decided.
        self.check_at = {}
        for f, ls in self.listers.items():
            self.check_at.setdefault(max(ls), []).append(f)
        self.state = {}
        self.hub_out = set()
        self.basis = {}
        self.found = []
        self.nodes = 0
        self.progress_depth = 0
        self.t0 = time.time()
        self.out = None

    def column_ok_at(self, st, k):
        """One column's conditions that become decidable when row k is decided (st: row -> state)."""
        if st.get(k) == X and k not in self.listers:
            return False
        for f in self.check_at.get(k, ()):
            cnt = sum(1 for m in self.listers[f] if st.get(m) == T)
            fs = st.get(f, O) if f in self.composite else O
            if fs == O and cnt == 1:
                return False
            if fs == X and cnt == 0:
                return False
        return True

    def column_prefixes(self):
        rows = self.rows
        feasible = [set() for _ in range(len(rows) + 1)]
        st = {}

        def rec(i, code):
            if i == len(rows):
                feasible[i].add(code)
                return True
            k = rows[i]
            any_ok = False
            for s in (T, X, O):
                st[k] = s
                if self.column_ok_at(st, k) and rec(i + 1, code * 3 + s):
                    any_ok = True
                del st[k]
            if any_ok:
                feasible[i].add(code)
            return any_ok
        rec(0, 0)
        return feasible

    def vector(self, k, j):
        v = 0
        for f in self.factors[k]:
            if f not in self.composite or self.state[(f, j)] == O:
                v |= 1 << self.bit[(f, j)]
        if k not in self.hub_out:
            v |= 1 << self.bit[("hub", k)]
        return v

    def insert(self, v):
        while v:
            p = v.bit_length() - 1
            if p not in self.basis:
                self.basis[p] = v
                return p
            v ^= self.basis[p]
        return None

    def column_choices(self, i):
        nxt = self.feasible[i + 1]
        options = [[s for s in (T, X, O) if self.codes[j] * 3 + s in nxt] for j in range(self.cols)]
        out = []

        def rec(j, acc):
            if j == self.cols:
                out.append(tuple(acc))
                return
            for s in options[j]:
                if j > 0 and self.equal_so_far[j - 1] and s < acc[-1]:
                    continue
                acc.append(s)
                rec(j + 1, acc)
                acc.pop()
        rec(0, [])
        return out

    def search(self, i=0):
        self.nodes += 1
        if i == len(self.rows):
            members = [key for key, s in self.state.items() if s == T]
            if members:
                self.record(members)
            return
        k = self.rows[i]
        choices = self.column_choices(i)
        for at, choice in enumerate(choices):
            if i < self.progress_depth:
                print(f"   progress: row {k} choice {at + 1}/{len(choices)} {choice}; {self.nodes} nodes, "
                      f"{len(self.found)} found, {time.time() - self.t0:.0f} s", file=sys.stderr, flush=True)
            nt = sum(1 for s in choice if s == T)
            for j, s in enumerate(choice):
                self.state[(k, j)] = s
            modes = [False] + ([True] if self.hubs_removable and nt >= 1 else [])
            for removed in modes:
                if not removed and nt == 1:
                    continue
                if removed:
                    self.hub_out.add(k)
                added, ok = [], True
                for j, s in enumerate(choice):
                    if s == T:
                        piv = self.insert(self.vector(k, j))
                        if piv is None:
                            ok = False
                            break
                        added.append(piv)
                if ok:
                    saved, saved_codes = list(self.equal_so_far), list(self.codes)
                    for j in range(self.cols - 1):
                        self.equal_so_far[j] = self.equal_so_far[j] and choice[j] == choice[j + 1]
                    for j in range(self.cols):
                        self.codes[j] = self.codes[j] * 3 + choice[j]
                    self.search(i + 1)
                    self.equal_so_far, self.codes = saved, saved_codes
                for piv in added:
                    del self.basis[piv]
                if removed:
                    self.hub_out.discard(k)
            for j in range(self.cols):
                del self.state[(k, j)]

    def record(self, members):
        moves = [key for key, s in self.state.items() if s == X]
        basis, indep = {}, True
        for (k, j) in members + moves:
            v = self.vector(k, j)
            while v:
                p = v.bit_length() - 1
                if p not in basis:
                    basis[p] = v
                    break
                v ^= basis[p]
            else:
                indep = False
                break
        core = (sorted(members), sorted(moves), sorted(self.hub_out), indep)
        self.found.append(core)
        if self.out:
            self.out.write(json.dumps({"c": self.c, "d": self.d, "T": core[0], "X": core[1], "hubs_out": core[2],
                                       "T_plus_X_independent": indep}) + "\n")
            self.out.flush()

    def run(self):
        t = time.time()
        self.feasible = self.column_prefixes()
        print(f"   column prefixes: {sum(len(f) for f in self.feasible)}, full columns {len(self.feasible[-1])} "
              f"(with the empty one), {time.time() - t:.1f} s", file=sys.stderr, flush=True)
        self.equal_so_far = [True] * (self.cols - 1)
        self.codes = [0] * self.cols
        self.search(0)
        return self.found


def show(core):
    members, moves, hubs, indep = core
    cols, xs = {}, {}
    for k, j in members:
        cols.setdefault(j, []).append(k)
    for k, j in moves:
        xs.setdefault(j, []).append(k)
    parts = [f"col {j}: T {sorted(cols.get(j, []))} X {sorted(xs.get(j, []))}" for j in sorted(set(cols) | set(xs))]
    return "; ".join(parts) + (f"; hubs out {hubs}" if hubs else "") + f"; T+X independent: {indep}"


def main():
    args = sys.argv[1:]
    opts = {}
    for name in ("--list", "--progress"):
        if name in args:
            at = args.index(name)
            opts[name] = int(args[at + 1])
            args = args[:at] + args[at + 2:]
    removable = "--hubs-removable" in args
    nums = [int(a) for a in args if a.isdigit()]
    for c, d in zip(nums[0::2], nums[1::2]):
        t0 = time.time()
        w = Window(c, d, removable)
        w.progress_depth = opts.get("--progress", 0)
        name = f"up_cores_c{c}_d{d}" + ("_hubs_removable" if removable else "") + ".jsonl"
        with open(os.path.join(HERE, name), "w") as w.out:
            found = w.run()
        mode = "hubs removable" if removable else "hubs in the pool"
        print(f"== (c, d) = ({c}, {d}), {mode}, rows bottom up: {len(w.rows)} composite rows x {d + 1} columns; "
              f"{w.nodes} search nodes, {time.time() - t0:.1f} s; odd cores (T, X), columns in canonical order: "
              f"{len(found)}; with T + X independent: {sum(1 for f in found if f[3])}", flush=True)
        for core in sorted(found, key=lambda f: (len(f[0]), f))[:opts.get("--list", 20)]:
            print("   " + show(core), flush=True)


if __name__ == "__main__":
    main()
