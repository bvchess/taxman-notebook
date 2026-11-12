#!/usr/bin/env python3
"""E7: the odd cores of the window instance (study-report.md, Section 5.3), by exhaustive search.

    nice -n 19 python3 -I e7/window_cores.py C D [C D ...] [--hubs-removable] [--list N] [--progress DEPTH] [--guided]

Each odd core found is written as it is found to e7/cores_cC_dD[_hubs_removable].jsonl, and a summary with the first N
(default 20, smallest first) goes to standard output.

The window instance for a cofactor c and depth d: d + 1 clean columns j = 0..d, each holding the rows 1..c; the cell
(k, j) = k·P_j lists its column factors (k/q, j), one for each prime q dividing k, and its hub k, which every cell of
row k lists (playability.md for instances, lists, cores and odd cores).  A column factor is listed only by cells of
its own column: in a clean column (c + 1)·P_j > n, so a number listing k·P_j is a cell of row qk <= c of column j.

Members and pool.  The members are the cells of the composite rows k <= c (Omega(k) >= 2, the cells of layer 3 and
up).  A cell of a prime row (layer 2) lists P_j and the prime hub q, which only layer-2 cells list, so the layer-2
members of a core form a core by themselves, whose members list two factors each, which is not odd (P11): no odd core
holds a layer-2 cell.  The pool holds the factors of the members that are no move: a column factor of a prime row,
and P_j, is always in it (F4 and F10: a game from 187 on plays no prime but q(n) and no number of layer 2 up to n/2,
and a layer-2 cell above n/2 is no factor of any cell); a column factor (m, j) of a composite row is in it unless the
cell (m, j) is a move.  A hub is in the pool (it is a number up to c, never a move of these games); with
--hubs-removable a hub may also be left out of the pool, as if it were a move, the wider question.

What is enumerated.  Every pair (T, X) of disjoint sets of member cells, T nonempty, where X holds moves outside T,
such that T is a core of the instance whose pool leaves out T and X: each factor that a member of T lists is listed by
another member of T.  X is kept to the column factors that some member of T lists (others change no list of T).  An
odd core is such a T whose lists are linearly independent over GF(2).  For each, the search also says whether T + X,
the moves of the window, is independent with its own lists (so that a set independent at both parities could hold it).

How.  Rows are decided from c down, all d + 1 columns of a row at once, each cell in T, in X or neither.  Every lister
of a factor lies in a higher row, so each core condition is checked when its factor's row is reached (for the prime
rows, once their lowest lister's row is done).  At every step the members' lists, with each factor whose row is not
decided yet counted as in the pool, must be independent over GF(2): deciding a factor later can only delete its
coordinate from every list that holds it, a projection, which keeps any dependency, and later members only add
vectors; so a dependency found early stays to the end, and the branch is cut.  The conditions of one column (its
column factors and its prime factors listed twice or not at all, a move only where a member lists it) involve that
column alone, so a first pass lists, for one column, every prefix of states down the rows that extends to a full
column meeting them, with the largest surplus |K| - 2 dim of such a full column (K its members, dim that of the
subsets of K whose column lists sum to 0); with --guided the search takes for each column only such prefixes, and
cuts a branch whose columns' largest surpluses sum below 0 (an odd core needs the sum of the dims at most the number
of rows it uses, and every row in two columns, so the surpluses sum to 0 or more).  Without --guided (the default)
the search checks the same conditions as it goes; the two give the same cores, and the table costs memory at large
c, so it is a cross-check.  The columns are interchangeable, so the search keeps only the assignments whose columns, read
as strings of states down the rows, are in nondecreasing order.
"""
import json
import os
import sys
import time

T, X, O = 0, 1, 2  # in the core, a move outside the core, in the pool (not a move)


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
        self.rows = [k for k in range(c, 1, -1) if omega(k) >= 2]  # composite rows, descending
        self.composite = set(self.rows)
        self.primes = [p for p in range(2, c + 1) if omega(p) == 1]
        self.factors = {k: sorted(k // q for q in primes_of(k)) for k in self.rows}
        self.listers = {}
        for k in self.rows:
            for f in self.factors[k]:
                self.listers.setdefault(f, []).append(k)
        # Bits: column factor (f, j) for f in 1..c that some member lists, and hub k for composite k.
        self.bit = {}
        for f in sorted(self.listers):
            for j in range(self.cols):
                self.bit[(f, j)] = len(self.bit)
        for k in sorted(self.rows):
            self.bit[("hub", k)] = len(self.bit)
        # Prime column factors are checked once their lowest lister, row 2p (or p*p), is decided.
        self.prime_check_at = {}
        for p in self.primes:
            if p in self.listers:
                self.prime_check_at.setdefault(min(self.listers[p]), []).append(p)
        self.state = {}
        self.hub_out = set()
        self.found = []
        self.nodes = 0
        self.progress_depth = 0
        self.guided = True
        self.t0 = time.time()
        self.out = None

    def column_prefixes(self):
        """feasible[i]: for each code (base 3, a digit a row) of the states of one column's first i rows that extends
        to a full assignment of the column meeting its own conditions (a column core with its moves, or no member at
        all), the largest surplus of such an extension (see surplus below)."""
        rows = self.rows
        feasible = [dict() for _ in range(len(rows) + 1)]
        st = {}

        def count(f):
            return sum(1 for k in self.listers.get(f, ()) if st.get(k) == T)

        def surplus():
            """|K| - 2 dim, for K the column's members and dim that of the space of subsets of K whose column lists
            (the column factors in the pool) sum to 0; 0 for the empty column."""
            K = [k for k in rows if st[k] == T]
            basis, rank = {}, 0
            for k in K:
                v = 0
                for f in self.factors[k]:
                    if f not in self.composite or st[f] == O:
                        v |= 1 << f
                while v:
                    p = v.bit_length() - 1
                    if p not in basis:
                        basis[p] = v
                        rank += 1
                        break
                    v ^= basis[p]
            return len(K) - 2 * (len(K) - rank)

        def rec(i, code):
            """The largest surplus of a full column extending this prefix, or None if none does."""
            if i == len(rows):
                best = surplus()
                feasible[i][code] = best
                return best
            k = rows[i]
            cnt = count(k)
            best = None
            for s in (T, X, O):
                if (s == X and cnt == 0) or (s == O and cnt == 1):
                    continue
                st[k] = s
                if all(count(p) != 1 for p in self.prime_check_at.get(k, ())):
                    b = rec(i + 1, code * 3 + s)
                    if b is not None and (best is None or b > best):
                        best = b
                del st[k]
            if best is not None:
                feasible[i][code] = best
            return best
        rec(0, 0)
        return feasible

    def tcount(self, f, j):
        return sum(1 for k in self.listers.get(f, ()) if self.state.get((k, j)) == T)

    def vector(self, k, j):
        """The list of (k, j) as a bit vector; a factor whose row is not decided yet counts as in the pool."""
        v = 0
        for f in self.factors[k]:
            if f not in self.composite or self.state.get((f, j), O) == O:
                v |= 1 << self.bit[(f, j)]
        if k not in self.hub_out:
            v |= 1 << self.bit[("hub", k)]
        return v

    @staticmethod
    def independent(vectors):
        basis = {}
        for v in vectors:
            while v:
                p = v.bit_length() - 1
                if p not in basis:
                    basis[p] = v
                    break
                v ^= basis[p]
            else:
                return False
        return True

    def column_choices(self, i):
        """The state tuples for row index i, in nondecreasing order within runs of columns equal so far."""
        k = self.rows[i]
        options = []
        for j in range(self.cols):
            if self.guided:
                nxt = self.feasible[i + 1]
                opts = [s for s in (T, X, O) if self.codes[j] * 3 + s in nxt]
            else:
                cnt = self.tcount(k, j)
                opts = [T]
                if cnt >= 1:
                    opts.append(X)
                if cnt != 1:
                    opts.append(O)
            options.append(opts)
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
            # Prime factors whose lowest lister is a composite row were checked on the way; all lists are complete.
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
            hub_modes = [False]
            if self.hubs_removable and nt >= 1:
                hub_modes.append(True)
            for j, s in enumerate(choice):
                self.state[(k, j)] = s
            for removed in hub_modes:
                if not removed and nt == 1:
                    continue
                if removed:
                    self.hub_out.add(k)
                ok = True
                for p in self.prime_check_at.get(k, ()):
                    for j in range(self.cols):
                        if self.tcount(p, j) == 1:
                            ok = False
                if ok and self.guided:
                    nxt = self.feasible[i + 1]
                    ok = sum(nxt[self.codes[j] * 3 + choice[j]] for j in range(self.cols)) >= 0
                if ok:
                    members = [key for key, s in self.state.items() if s == T]
                    ok = self.independent([self.vector(m, j) for m, j in members])
                if ok:
                    saved = list(self.equal_so_far)
                    saved_codes = list(self.codes)
                    for j in range(self.cols - 1):
                        self.equal_so_far[j] = self.equal_so_far[j] and choice[j] == choice[j + 1]
                    for j in range(self.cols):
                        self.codes[j] = self.codes[j] * 3 + choice[j]
                    self.search(i + 1)
                    self.equal_so_far = saved
                    self.codes = saved_codes
                if removed:
                    self.hub_out.discard(k)
            for j in range(self.cols):
                del self.state[(k, j)]

    def record(self, members):
        moves = [key for key, s in self.state.items() if s == X]
        # T + X independent with its own lists (the lists of X's members leave out T + X too).
        basis = {}
        indep = True
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
        self.equal_so_far = [True] * (self.cols - 1)
        self.codes = [0] * self.cols
        if self.guided:
            t = time.time()
            self.feasible = self.column_prefixes()
            print(f"   column prefixes: {sum(len(f) for f in self.feasible)}, of them full columns "
                  f"{len(self.feasible[-1])} (with the empty one), {time.time() - t:.1f} s", file=sys.stderr, flush=True)
        self.search(0)
        return self.found


def show(core):
    members, moves, hubs, indep = core
    cols = {}
    for k, j in members:
        cols.setdefault(j, []).append(k)
    xs = {}
    for k, j in moves:
        xs.setdefault(j, []).append(k)
    parts = []
    for j in sorted(set(cols) | set(xs)):
        parts.append(f"col {j}: T {sorted(cols.get(j, []))} X {sorted(xs.get(j, []))}")
    tail = f"; hubs out {hubs}" if hubs else ""
    return "; ".join(parts) + tail + f"; T+X independent: {indep}"


def main():
    args = sys.argv[1:]
    removable = "--hubs-removable" in args
    limit = 20
    if "--list" in args:
        at = args.index("--list")
        limit = int(args[at + 1])
        args = args[:at] + args[at + 2:]
    progress = 0
    if "--progress" in args:
        at = args.index("--progress")
        progress = int(args[at + 1])
        args = args[:at] + args[at + 2:]
    nums = [int(a) for a in args if a.isdigit()]
    for c, d in zip(nums[0::2], nums[1::2]):
        t0 = time.time()
        w = Window(c, d, removable)
        w.progress_depth = progress
        w.guided = "--guided" in args
        name = f"cores_c{c}_d{d}" + ("_hubs_removable" if removable else "") + ".jsonl"
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), name), "w") as w.out:
            found = w.run()
        mode = ("hubs removable" if removable else "hubs in the pool") + (", guided" if w.guided else "")
        print(f"== (c, d) = ({c}, {d}), {mode}: {len(w.rows)} composite rows x {d + 1} columns; "
              f"{w.nodes} search nodes, {time.time() - t0:.1f} s; odd cores (T, X), columns in canonical order: "
              f"{len(found)}; with T + X independent: {sum(1 for f in found if f[3])}", flush=True)
        for core in sorted(found, key=lambda f: (len(f[0]), f))[:limit]:
            print("   " + show(core), flush=True)


if __name__ == "__main__":
    main()
