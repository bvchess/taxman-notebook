"""Number tables, the playability test of a set of moves, and the promotion sets of a game, for the studies of E5.

A set S of moves is playable iff dismantling its own instance deletes every member (the core theorem, P7).  A member of
layer k lists only factors of layer k - 1, so dismantling splits by layer (every cycle is flat, P3): a change to S
that adds or removes x touches only the layers of x and of x's multiples, Omega(x) and Omega(x) + 1.  The promotion
sets of game n are the sets L of numbers up to n/2 with U* + L playable (the exactness theorem, X7), and its
candidates are the x with U* + {x} playable; the second matches the candidates that setup counts on every board
checked (see the entry).

The results file is the one TAXMAN_RESULTS names, else results/optimal.jsonl.gz of the main repository whose checkout
holds this notebook's at solver/notebook/.
"""
import gzip
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.environ.get('TAXMAN_RESULTS', os.path.join(HERE, '..', '..', '..', '..', 'results', 'optimal.jsonl.gz'))


class Tables:
    """The prime factors, the layer and the maximal factors of every number up to n_max."""

    def __init__(self, n_max):
        spf = list(range(n_max + 1))
        for p in range(2, int(n_max ** .5) + 1):
            if spf[p] == p:
                for q in range(p * p, n_max + 1, p):
                    if spf[q] == q:
                        spf[q] = p
        self.primes_of = [()] * (n_max + 1)
        self.omega = [0] * (n_max + 1)
        for m in range(2, n_max + 1):
            f = []
            x = m
            while x > 1:
                f.append(spf[x])
                x //= spf[x]
            self.omega[m] = len(f)
            self.primes_of[m] = tuple(sorted(set(f)))
        self.mf = [()] * (n_max + 1)
        for m in range(2, n_max + 1):
            self.mf[m] = tuple(m // p for p in self.primes_of[m])

    def largest_prime(self, m):
        return self.primes_of[m][-1]

    def dismantle(self, members, in_set):
        """The residual of the members given, all of one layer, each listing its maximal factors f with not in_set(f)."""
        listers = defaultdict(set)
        lists = {}
        for x in members:
            lx = [f for f in self.mf[x] if not in_set(f)]
            lists[x] = lx
            for f in lx:
                listers[f].add(x)
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

    def residual(self, members):
        """The residual of the own instance of `members`: empty iff the set is playable."""
        members = set(members)
        by_layer = defaultdict(list)
        for x in members:
            by_layer[self.omega[x]].append(x)
        out = set()
        for xs in by_layer.values():
            out |= self.dismantle(xs, members.__contains__)
        return out


class Position:
    """A playable set of moves, with the residual of the set changed by a few members computed layer by layer."""

    def __init__(self, tables, members):
        self.t = tables
        self.members = set(members)
        self.by_layer = defaultdict(set)
        for x in self.members:
            self.by_layer[tables.omega[x]].add(x)

    def residual_after(self, add=(), remove=()):
        """The residual of the set with `add` added and `remove` removed (the set itself must be playable)."""
        add = set(add) - self.members
        remove = set(remove) & self.members
        om = self.t.omega
        layers = set()
        for x in add | remove:
            layers.add(om[x])
            layers.add(om[x] + 1)

        def in_set(f):
            return f in add or (f in self.members and f not in remove)
        out = set()
        for k in layers:
            xs = (self.by_layer.get(k, set()) | {x for x in add if om[x] == k}) - remove
            if xs:
                out |= self.t.dismantle(xs, in_set)
        return out

    def playable_after(self, add=(), remove=()):
        return not self.residual_after(add, remove)

    def add(self, x):
        self.members.add(x)
        self.by_layer[self.t.omega[x]].add(x)

    def remove(self, x):
        self.members.discard(x)
        self.by_layer[self.t.omega[x]].discard(x)


class Game:
    """Game n as the frame model sees it: U* (the recorded game's moves above n/2) and the candidates, computed unless
    they are given."""

    def __init__(self, tables, n, recorded_moves, candidates=None):
        self.t = tables
        self.n = n
        self.ustar = frozenset(m for m in recorded_moves if 2 * m > n)
        if candidates is None:
            base = Position(tables, self.ustar)
            candidates = (x for x in range(2, n // 2 + 1) if base.playable_after(add=(x,)))
        self.candidates = frozenset(candidates)

    def position(self, promotions):
        return Position(self.t, self.ustar | set(promotions))

    def promotable(self, promotions):
        return not self.t.residual(self.ustar | set(promotions))

    def survivors(self, seed):
        """What survives of a seed: its candidates that can still be promoted, from the largest down."""
        pos = Position(self.t, self.ustar)
        kept = []
        for x in sorted(set(seed) & self.candidates, reverse=True):
            if pos.playable_after(add=(x,)):
                pos.add(x)
                kept.append(x)
        return frozenset(kept)


def frame_graph_by_layer(tables, n):
    """The components of the frame graph of game n (each source joined to its maximal factors), by layer: for each
    layer, the number of sources and the numbers of sources of its components, largest first."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for s in range(n // 2 + 1, n + 1):
        parent.setdefault(s, s)
        for f in tables.mf[s]:
            parent.setdefault(f, f)
            ra, rb = find(s), find(f)
            if ra != rb:
                parent[ra] = rb
    comps = {}
    for s in range(n // 2 + 1, n + 1):
        comps.setdefault(find(s), []).append(s)
    out = {}
    for sources in comps.values():
        out.setdefault(tables.omega[sources[0]], []).append(len(sources))
    return {k: sorted(v, reverse=True) for k, v in sorted(out.items())}


def load_results(path=RESULTS):
    games = {}
    with gzip.open(path, 'rt') as f:
        for line in f:
            rec = json.loads(line)
            games[rec['n']] = dict(moves=frozenset(rec['moves']), promotions=frozenset(rec['promotions']),
                                   method=rec['method'], score=rec['score'], bag=rec['in_the_bag'],
                                   candidates=(rec['setup'] or {}).get('candidates'))
    return games


def seed_of(games, n, j=1):
    """The moves of game n - j that are factors of game n: what game n can take from it as promotions."""
    return frozenset(m for m in games[n - j]['moves'] if 2 * m <= n)
