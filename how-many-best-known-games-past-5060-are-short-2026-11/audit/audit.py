#!/usr/bin/env python3
"""Consistency audit of the best-known Taxman games 5061..10000: every best-known score against every known relation
between neighboring games.

    nice -n 19 python3 -I audit.py            # a few minutes; writes the files listed in README.md beside it

It reads best-known.jsonl once, at its start, up to the size the file has then, and the proven chain 1..5060 and the
proven games past it; it changes nothing outside this folder.  README.md says what each relation is, where it is proved
or why it is believed, and how a disagreement is read.  Words (S is ../succession/brief.md): opt(n) the best score of
game n, A = the best-known score of n - 1 (opt(n - 1) where n - 1 is proven) and B = the best-known score of n.  A
best-known score is the score of a game that the audit replays by the rules, so it is a lower bound of opt; a relation
that bounds opt(n) therefore says that a best-known score is *at least* so short, never that it is optimal.
"""

import array
import bisect
import collections
import csv
import datetime
import hashlib
import heapq
import itertools
import json
import os
import sys
import time
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/brian/taxman_work/lab/work/succession")
import common  # noqa: E402  the loaders and peel of the succession study, read only

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("AUDIT_OUT", HERE)          # the files go here (a test aid: point it elsewhere to keep these)
BEST = os.environ.get("AUDIT_BEST", "/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl")
BEYOND = "/home/brian/taxman_work/research/results/beyond-the-chain.jsonl"
PAST = "/home/brian/taxman_work/lab/work/succession/past5060.csv"
# The dedicated plays: ledgers named by a comma-separated list, each `path` or `path:mark`; the mark (default `h` for a
# ledger in a folder called hammer, none otherwise) ends the play's name in seeds_levels, as in s51L4h.
LEDGERS = os.environ.get("AUDIT_LEDGER", "/home/brian/taxman_work/lab/work/rootfirst/ledger2.tsv,"
                         "/home/brian/taxman_work/lab/work/rootfirst/ledger.tsv,"
                         "/home/brian/taxman_work/lab/work/hammer/ledger.tsv")
PILOT_LEVEL = 3         # rootfirst/ledger.tsv, the pilot's first round, has five columns and no level: it played at 3
# the succession brief's step kinds (the keys) as parity-bound.md, W4, names them (a prime is an exchange step there)
W4_STEP = {"prime": "exchange", "restrict": "added", "relax": "half-in", "exchange": "exchange",
           "half-out": "half-out", "other": "other"}
FIRST = 5061            # the first game that is only best-known
CHAIN_END = 5060        # the last game of the proven chain
TOP = int(os.environ.get("AUDIT_TOP", "10000"))
WINDOWS = (8, 40, 100, 400, 10 ** 9)   # the projection windows N - n that summary.txt reports
T0 = time.time()

# Each relation: (code, how it stands, the sides it can speak for).  "yes" = proved with no assumption beyond the
# rules; "yes, given U" = proved given statement U; "no" = conjectured or measured.
RELATIONS = {
    "N3": ("yes", "monotonicity: the game of n - 1 extended (opt(n) > opt(n - 1))"),
    "N4": ("yes", "the ceiling lemma: opt(n) <= opt(n - 1) + n"),
    "N5": ("yes", "the prime formula: opt(p) = opt(p - 1) + p - q(p - 1)"),
    "N6": ("yes", "the step theorem: a game of n - 1 that stays playable with n added reaches the ceiling"),
    "N7a": ("yes", "the half lemma, read on the line: even n, the line of n - 1 leaves n/2 out"),
    "N7b": ("yes, given U", "the half lemma, read on U*: even n, n/2 not in U*(n - 1), given U at n - 1"),
    "S1": ("yes", "the single-loss rule: the line of n - 1 plus n, less its smallest move that makes it playable"),
    "R6": ("yes", "the repeat lemma, part 1: games with one root problem share the promotion sum of their best line"),
    "J3": ("yes", "the semiprime formula: opt(n) = opt(n - 1) + n - x at an odd n with two prime factors, n >= 189"),
    "L2": ("yes", "the 8p theorem: opt(8p) <= opt(8p - 1) + 8p - 4r"),
    "L4": ("yes, given U", "the 12p theorem: opt(12p) <= opt(12p - 1) + 12p - 6r, given 8p, 8r, 12r, 8t in U*(n)"),
    "PROJ": ("yes", "projection: the moves of a game of N that are at most n are a game of n"),
    "PROVEN": ("yes", "a proven game past the chain against the best-known score of the same game"),
    "W1": ("yes", "the parity bound: opt(n) <= PB(n)"),
    "STRUCT": ("yes", "N1, N2, F10: an optimal game is over, opens with q(n), plays no other prime, and from 187 on "
                      "no layer-2 number up to n/2"),
    "EXL": ("no", "the exchange law: at an exchange step delta(n) = x, the displaced source (the shadow)"),
    "FAM8": ("no", "the 8P law: delta(8P) = 4P1 (L2 proves delta >= 4P1)"),
    "FAM12": ("no", "the 12P law: delta(12P) = 6P1 (L4 proves delta >= 6P1, given U)"),
    "FAM16": ("no", "the 16P pattern: delta = 8P1 + 6P2 + 4P3 - 6P1 - 4P2, in a window clean to depth 3"),
    "FAM20": ("no", "the 20P pattern: delta = 10P1 + 6P2 + 9P2 - 6P1 - 10P2, in a window clean to depth 2"),
    "FAM24": ("no", "the 24P pattern: delta = 12P1 + 10P2 - 10P1, in a window clean to depth 2"),
    "FAM40": ("no", "the 40P pattern: delta = 18P1, in a window clean to depth 1"),
    "COF9": ("no", "the cofactor rule: n = 9P is at its ceiling"),
    "CWEQ": ("no", "the clean-window parity form: delta = delta_PB at a relaxation or restriction clean to depth 3"),
    "CWEQ2": ("no", "the same form at depth exactly 2, where it failed once in the chain (2512)"),
    "CWINEQ": ("no", "the clean-window inequality: delta >= delta_PB at a relaxation or restriction clean to depth 2"),
}
FAMILIES = {   # cofactor -> (relation, [(coefficient, column j)], depth of the pattern)
    8: ("FAM8", [(4, 1)], 1),
    12: ("FAM12", [(6, 1)], 1),
    16: ("FAM16", [(8, 1), (6, 2), (4, 3), (-6, 1), (-4, 2)], 3),
    20: ("FAM20", [(10, 1), (6, 2), (9, 2), (-6, 1), (-10, 2)], 2),
    24: ("FAM24", [(12, 1), (10, 2), (-10, 1)], 2),
    40: ("FAM40", [(18, 1)], 1),
}

# ---------------------------------------------------------------------------------------------------------------
# Number tables, the rules, peel
# ---------------------------------------------------------------------------------------------------------------

SPF = OMEGA = LPF = DIVS = MF = PREV_PRIME = QPRIME = None


def init_tables(top):
    """Smallest and largest prime factor, number of prime factors, proper divisors (1 included), maximal factors."""
    global SPF, OMEGA, LPF, DIVS, MF, PREV_PRIME, QPRIME
    SPF = common.sieve_spf(top + 1)
    OMEGA = [0] * (top + 2)
    LPF = [1] * (top + 2)
    for x in range(2, top + 1):
        y = x // SPF[x]
        OMEGA[x] = OMEGA[y] + 1
        LPF[x] = max(SPF[x], LPF[y])
    DIVS = [[] for _ in range(top + 1)]
    for d in range(1, top // 2 + 1):
        for m in range(2 * d, top + 1, d):
            DIVS[m].append(d)
    MF = [()] * (top + 1)
    for x in range(2, top + 1):
        MF[x] = tuple(sorted(common.maximal_factors(x, SPF)))
    PREV_PRIME = {}
    QPRIME = [0] * (top + 1)
    last = None
    for x in range(2, top + 1):
        if SPF[x] == x:
            PREV_PRIME[x] = last
            last = x
        QPRIME[x] = last


def is_prime(x):
    return x > 1 and SPF[x] == x


def replay(moves, n):
    """The score of the sequence `moves` on board n if it is a legal game (every move in the pot with a proper
    divisor in the pot; the taxman takes the divisors), else None.  The game need not be over."""
    pot = bytearray(b"\x01") * (n + 1)
    total = 0
    for x in moves:
        if x < 2 or x > n or not pot[x]:
            return None
        tax = [d for d in DIVS[x] if pot[d]]
        if not tax:
            return None
        for d in tax:
            pot[d] = 0
        pot[x] = 0
        total += x
    return total


def replay_extension(moves, n, target):
    """Replay the game `moves` of board n and, from the same pass, the construction of monotonicity (N3, step 3) that
    puts `target` = n + 1 into it (none if target is None).  Returns (score, extended score, m, left out, playable)
    with m the move before which target goes (None if target can follow the game) and `playable` the numbers still in
    the pot that have a proper divisor in the pot (the game is over iff there are none), or None if the game is not
    legal."""
    probe = DIVS[target] if target else ()
    probe_set = set(probe)
    leave = {}
    pot = bytearray(b"\x01") * (n + 1)
    taxes = []
    total = 0
    for i, x in enumerate(moves):
        if x < 2 or x > n or not pot[x]:
            return None
        tax = [d for d in DIVS[x] if pot[d]]
        if not tax:
            return None
        for d in tax:
            pot[d] = 0
            if d in probe_set:
                leave[d] = i
        pot[x] = 0
        if x in probe_set:
            leave[x] = i
        taxes.append(tax)
        total += x
    playable = [y for y in itertools.compress(range(n + 1), pot) if y > 1 and any(pot[d] for d in DIVS[y])]
    if target is None:
        return total, None, None, False, playable
    if len(leave) < len(probe):
        return total, total + target, None, False, playable      # a proper divisor of target is still in the pot
    last = max(leave.values())
    m = moves[last]
    d_m = {d for d in probe if leave[d] == last}
    left_out = m in d_m or all(t in d_m for t in taxes[last])
    return total, total + target - (m if left_out else 0), m, left_out, playable


def dismantle(lists):
    """The residual of an instance given as {member: list of the factors it lists}: members are deleted while one
    lists a factor that no other remaining member lists (Theorems P5, P7); the instance is playable iff none is left."""
    listers = collections.defaultdict(set)
    for x, fs in lists.items():
        for f in fs:
            listers[f].add(x)
    alive = set(lists)
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


def single_loss(moves, n):
    """(x_min, tried) for the set M of `moves` of board n - 1: x_min is 0 if M + n is playable on board n, else the
    smallest move y of M with M + n - y playable, else None; `tried` lists the candidates that failed before it.  By
    the layer theorem (F3) only the layer instance of n, at k = Omega(n), is not playable in M + n; giving up y
    helps only if y is a member of layer k or a move of layer k - 1 that is at most n/2 (it returns to the pool),
    and then only if y is in the residual R of that instance or is a maximal factor of a member of R (a move
    outside both leaves every core of R intact)."""
    k = OMEGA[n]
    mset = set(moves)
    s = mset | {n}
    members = [x for x in mset if OMEGA[x] == k]
    members.append(n)
    lists = {x: [f for f in MF[x] if f not in s] for x in members}
    res = dismantle(lists)
    if not res:
        return 0, []
    cands = set(res)
    cands.discard(n)
    for z in res:
        for y in MF[z]:
            if y in mset:
                cands.add(y)
    tried = []
    for y in sorted(cands):
        if y in res:
            sub = {z: lists[z] for z in res if z != y}
        else:
            sub = {z: (lists[z] + [y] if y in MF[z] else lists[z]) for z in res}
        if not dismantle(sub):
            return y, tried
        tried.append(y)
    return None, tried


def peel_pay(members):
    """A payment scheme {member: factor} of the playable set `members` found by peel (P4), or None."""
    s = set(members)
    lists = {x: {f for f in MF[x] if f not in s} for x in s}
    listers = collections.defaultdict(set)
    for x, fs in lists.items():
        for f in fs:
            listers[f].add(x)
    pay = {}
    live_m = set(s)
    live_f = set(listers)
    stack_m = [x for x in s if len(lists[x]) <= 1]
    stack_f = [f for f in live_f if len(listers[f]) == 1]
    while live_m:
        pair = None
        while stack_m and pair is None:
            x = stack_m.pop()
            if x in live_m:
                fs = [g for g in lists[x] if g in live_f]
                if not fs:
                    return None
                if len(fs) == 1:
                    pair = (x, fs[0])
        while stack_f and pair is None:
            f = stack_f.pop()
            if f in live_f:
                ys = [y for y in listers[f] if y in live_m]
                if len(ys) == 1:
                    pair = (ys[0], f)
                elif not ys:
                    live_f.discard(f)
        if pair is None:
            return None
        x, f = pair
        pay[x] = f
        live_m.discard(x)
        live_f.discard(f)
        for g in lists[x]:
            if g in live_f:
                listers[g].discard(x)
                if len(listers[g]) == 1:
                    stack_f.append(g)
        for y in listers[f]:
            if y in live_m:
                lists[y].discard(f)
                if len(lists[y]) <= 1:
                    stack_m.append(y)
    return pay


def build_game(members, n):
    """A legal game of board n that plays exactly the set `members`: a payment scheme from peel, then a topological
    order of its precedence (a before b when pay(a) divides b or a divides b), checked by replay.  Returns the list of
    moves, or None when the set is not playable or the replay disagrees."""
    s = set(members)
    pay = peel_pay(s)
    if pay is None:
        return None
    succ = {x: set() for x in s}
    indeg = dict.fromkeys(s, 0)
    for a in s:
        f = pay[a]
        for b in itertools.chain(range(f, n + 1, f), range(2 * a, n + 1, a)):
            if b in s and b != a and b not in succ[a]:
                succ[a].add(b)
                indeg[b] += 1
    ready = [x for x in s if indeg[x] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        x = heapq.heappop(ready)
        order.append(x)
        for b in succ[x]:
            indeg[b] -= 1
            if indeg[b] == 0:
                heapq.heappush(ready, b)
    if len(order) != len(s) or replay(order, n) != sum(s):
        return None
    return order


def ustar_layer(n, k):
    """The sources of layer k of board n kept by descending greedy, read as the greedy basis over GF(2) of their
    maximal-factor vectors (the span conjecture (♦), checked in every game to 100,000, makes the two the same)."""
    basis = {}
    kept = []
    for x in range(n, n // 2, -1):
        if OMEGA[x] != k:
            continue
        v = 0
        for f in MF[x]:
            v |= 1 << f
        while v:
            h = v.bit_length() - 1
            b = basis.get(h)
            if b is None:
                basis[h] = v
                kept.append(x)
                break
            v ^= b
    return kept


def ustar(n):
    out = []
    for k in range(1, n.bit_length() + 1):
        out += ustar_layer(n, k)
    return out


# ---------------------------------------------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------------------------------------------

class Line:
    """One recorded game: its number, score, moves (None if not kept), method, root-problem digest and sum of U*."""
    __slots__ = ("n", "score", "moves", "method", "digest", "bag", "big")

    def __init__(self, n, score, moves, method, digest, bag):
        self.n, self.score, self.moves, self.method, self.digest, self.bag = n, score, moves, method, digest, bag
        half = n // 2
        self.big = sum(x for x in moves if x > half) if moves is not None else None


def digest_of(d):
    if d.get("setup"):
        return d["setup"]["digest"]
    if d.get("same_search"):
        return d["same_search"]["digest"]
    return None


def now_pacific():
    return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M %Z")


def load_best_known(path):
    """Read the best-known file once, up to the bytes it holds now.  Every line is kept (a legal game is a lower
    bound whether or not it is the highest of its game); a torn last line is dropped."""
    started = now_pacific()
    with open(path, "rb") as f:
        st = os.fstat(f.fileno())
        data = f.read(st.st_size)
    meta = {"read_at": started, "bytes": st.st_size, "sha256": hashlib.sha256(data).hexdigest(),
            "mtime": datetime.datetime.fromtimestamp(st.st_mtime, ZoneInfo("America/Los_Angeles"))
            .strftime("%Y-%m-%d %H:%M %Z")}
    pieces = data.split(b"\n")
    meta["torn_last_line"] = pieces[-1] != b""
    pieces.pop()
    del data
    lines = []
    for raw in pieces:
        if not raw.strip():
            continue
        d = json.loads(raw)
        lines.append(Line(d["n"], d["score"], array.array("H", d["moves"]), d["method"], digest_of(d),
                          d["in_the_bag"]))
    meta["lines"] = len(lines)
    return lines, meta


def load_chain():
    """The proven chain 1..5060: a Line per game, with moves kept for the last game only (the one game that a
    best-known game builds on)."""
    out = {}
    for d in common.jsonl(common.RESULTS):
        n = d["n"]
        moves = array.array("H", d["moves"]) if n == CHAIN_END else None
        out[n] = Line(n, d["score"], moves, d["method"], digest_of(d), d["in_the_bag"])
    return out


def load_beyond():
    out = {}
    for d in common.jsonl(BEYOND):
        out[d["n"]] = Line(d["n"], d["score"], array.array("H", d["moves"]), d["method"], digest_of(d),
                           d["in_the_bag"])
    return out


def load_ledgers(spec):
    """The dedicated plays, from each ledger in the comma-separated `spec`, read once, whole lines only.  A row is
    game, level, seed, known score, new score, time of day (no dates); the pilot's first ledger has no level column
    and is read as level PILOT_LEVEL.  Returns ({game: [(level, seed, known, new, mark)]}, [meta of each ledger])."""
    plays = collections.defaultdict(list)
    metas = []
    for entry in spec.split(","):
        path, _, mark = entry.partition(":") if ":" in entry else (entry, "", None)
        if mark is None:
            mark = "h" if os.path.basename(os.path.dirname(path)) == "hammer" else ""
        read_at = now_pacific()
        with open(path) as f:
            st = os.fstat(f.fileno())
            data = f.read()
        rows = data.split("\n")
        rows.pop()                  # the last piece is empty, or a line that is still being written
        bad, games = 0, set()
        for text in rows:
            parts = text.split("\t")
            try:
                nums = [int(x) for x in parts[:-1]]          # the last column is the time of day
                if len(nums) == 5:
                    game, level, seed, known, new = nums
                elif len(nums) == 4:
                    (game, seed, known, new), level = nums, PILOT_LEVEL
                else:
                    raise ValueError(text)
            except ValueError:
                bad += 1
                continue
            plays[game].append((level, seed, known, new, mark))
            games.add(game)
        metas.append({"path": path, "read_at": read_at, "rows": len(rows) - bad, "bad": bad, "games": len(games),
                      "mtime": datetime.datetime.fromtimestamp(st.st_mtime, ZoneInfo("America/Los_Angeles"))
                      .strftime("%Y-%m-%d %H:%M %Z")})
    return plays, metas


# ---------------------------------------------------------------------------------------------------------------
# Number-theoretic helpers for the relations
# ---------------------------------------------------------------------------------------------------------------

def shadow(n):
    """n odd: each prime factor replaced by the prime just below it, with multiplicity."""
    out = 1
    y = n
    while y > 1:
        p = SPF[y]
        out *= PREV_PRIME[p]
        y //= p
    return out


def clean_depth(n, limit=12):
    """The largest j <= limit such that (c + 1)·P_i > n for 1 <= i <= j, with P the largest prime factor of n,
    c = n/P its cofactor and P_i the i-th prime below P (loops brief, Section 1)."""
    big_p = LPF[n]
    c = n // big_p
    depth = 0
    p = big_p
    for i in range(1, limit + 1):
        p = PREV_PRIME.get(p) if p > 2 else None
        if p is None or (c + 1) * p <= n:
            break
        depth = i
    return depth


def family_delta(n, pattern):
    ps = [LPF[n]]
    for _ in range(3):
        ps.append(PREV_PRIME.get(ps[-1]))
    return sum(coef * ps[j] for coef, j in pattern)


def j3_x(n, layer2):
    """For odd n with two prime factors, n >= 189: the smallest member other than n of the cycle that n closes with
    U*_2(n - 1) in the graph G_n (vertices the primes and a ground vertex 0, p·q the edge p-q, p² the edge p-0), the
    forest that descending greedy keeps among the layer-2 sources of board n - 1 (Kruskal, largest first)."""
    low = (n - 1) // 2
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def ends(x):
        p = SPF[x]
        q = x // p
        return p, (0 if q == p else q)

    adj = collections.defaultdict(list)
    i = bisect.bisect_right(layer2, n - 1) - 1
    while i >= 0 and layer2[i] > low:
        x = layer2[i]
        u, v = ends(x)
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            adj[u].append((v, x))
            adj[v].append((u, x))
        i -= 1
    u, v = ends(n)
    if find(u) != find(v):
        return None
    prev = {u: None}
    queue = collections.deque([u])
    while queue:
        a = queue.popleft()
        if a == v:
            break
        for b, x in adj[a]:
            if b not in prev:
                prev[b] = (a, x)
                queue.append(b)
    path = []
    a = v
    while prev[a] is not None:
        a, x = prev[a]
        path.append(x)
    return min(path)


# ---------------------------------------------------------------------------------------------------------------
# The audit
# ---------------------------------------------------------------------------------------------------------------

class Audit:
    def __init__(self):
        self.rows = []                                    # disagreements
        self.applies = collections.Counter()              # relation -> games it applies to
        self.tight = collections.Counter()                # relation -> games where the best-known score meets it
        self.met = collections.defaultdict(set)           # game -> relations that its best-known score meets
        self.hits = collections.defaultdict(set)          # relation -> {game that must be short}
        self.checks = []                                  # (name, text) data checks, for the summary
        self.consistency = []                             # root-problem and data consistency rows
        self.constructions = []                           # games built and replayed that beat a best-known score
        self.contradictions = []                          # a proven game or a proved bound against a best-known score
        self.l4_skipped = collections.Counter()
        self.unverified = []                              # (n, relation): a bound beat B but its game did not replay

    def log(self, text):
        print(f"[{time.time() - T0:6.1f} s] {text}", file=sys.stderr, flush=True)

    def emit(self, n, rel, short, by, note, via=None):
        if short in self.proven:
            self.contradictions.append((n, rel, short, by))
            note = f"CONTRADICTION: game {short} is proven; " + note
        if via is None:
            who = "n" if short == n else "n-1"
        else:
            who = f"n via projection from N={via}"
        known = self.score[short]
        self.rows.append({"n": n, "relation": rel, "proved": RELATIONS[rel][0], "short_game": short, "short_is": who,
                          "at_least": by, "known_score": known, "must_reach": known + by, "note": note})
        self.hits[rel].add(short)

    # -- the three shapes of a relation between opt(n - 1) and opt(n) ------------------------------------------

    def equal(self, n, rel, c, note=""):
        """opt(n) = opt(n - 1) + n - c."""
        self.applies[rel] += 1
        d = (self.B - self.A) - (n - c)
        text = f"B - A = {self.B - self.A}, formula n - {c} = {n - c}; {note}".strip("; ")
        if d < 0:
            self.emit(n, rel, n, -d, text)
        elif d > 0:
            self.emit(n, rel, n - 1, d, text)
        else:
            self.tight[rel] += 1
            self.met[n].add(rel)

    def at_most(self, n, rel, c, note=""):
        """opt(n) <= opt(n - 1) + n - c: a best-known B above A + n - c makes n - 1 short."""
        self.applies[rel] += 1
        d = (self.B - self.A) - (n - c)
        if d > 0:
            self.emit(n, rel, n - 1, d, f"B - A = {self.B - self.A}, bound n - {c} = {n - c}; {note}".strip("; "))
        elif d == 0:
            self.tight[rel] += 1
            self.met[n].add(rel)

    def at_least(self, n, rel, bound, note=""):
        """opt(n) >= bound: a best-known B below it makes n short."""
        self.applies[rel] += 1
        if bound > self.B:
            self.emit(n, rel, n, bound - self.B, f"B = {self.B}, bound {bound} = A + {bound - self.A}; {note}"
                      .strip("; "))
        elif bound == self.B:
            self.tight[rel] += 1
            self.met[n].add(rel)

    # -- set-up ----------------------------------------------------------------------------------------------------

    def prepare(self, lines, meta, chain, beyond):
        """The best line of each game (highest score, the last if tied), the best-known score B and the known score
        A of every game (proven where it is proven), the sum of U* and the kind of step of every game."""
        self.meta, self.lines, self.chain, self.beyond = meta, lines, chain, beyond
        self.gc = common.games_csv()
        self.proven = set(range(1, CHAIN_END + 1)) | set(beyond)
        best = {}
        for ln in lines:
            if FIRST <= ln.n <= TOP and (ln.n not in best or ln.score >= best[ln.n].score):
                best[ln.n] = ln
        missing = [n for n in range(FIRST, TOP + 1) if n not in best]
        if missing:
            raise SystemExit(f"best-known.jsonl has no line of {len(missing)} games, the first {missing[:5]}")
        self.best = best
        self.bscore = {n: ln.score for n, ln in best.items()}
        self.known = {CHAIN_END: chain[CHAIN_END]}
        self.score = {n: chain[n].score for n in chain}
        for n in range(FIRST, TOP + 1):
            ln = beyond[n] if n in beyond and beyond[n].score > best[n].score else best[n]
            self.known[n] = ln
            self.score[n] = ln.score
        self.digest = {n: chain[n].digest for n in chain if chain[n].digest}
        for ln in lines:
            if ln.digest and FIRST <= ln.n <= TOP:
                self.digest.setdefault(ln.n, ln.digest)
        for n, ln in beyond.items():
            if ln.digest:
                self.digest.setdefault(n, ln.digest)
        self.layer2 = [x for x in range(4, TOP + 1) if OMEGA[x] == 2]
        self.kind = {n: self.step_kind(n) for n in range(FIRST - 1, TOP + 1)}

    def step_kind(self, n):
        """The kind of step, read from the change of the sum of U* (games.csv); exchange gives up the source x =
        n - change.  Prime, half-out (n even, n/2 not in U*(n - 1)), relax (n even, n/2 in it), restrict (n odd,
        U* gains n), exchange (n odd, U* gains n and loses x)."""
        if is_prime(n):
            return "prime"
        diff = self.gc[n]["ustar"] - self.gc[n - 1]["ustar"]
        if n % 2 == 0:
            return "half-out" if diff == n else "relax" if diff == n - n // 2 else "other"
        return "restrict" if diff == n else "exchange" if 0 < diff < n else "other"

    def exchange_x(self, n):
        return n - (self.gc[n]["ustar"] - self.gc[n - 1]["ustar"])

    # -- the games themselves --------------------------------------------------------------------------------------

    def replay_all(self):
        """Replay every recorded line of every game 5060..TOP by the rules: the best-known file keeps all its lines,
        and a legal game is a lower bound on its game whether or not it is the highest.  The same pass gives the
        construction of monotonicity (N3) that puts the next game into each line."""
        self.by_game = collections.defaultdict(list)
        self.by_game[CHAIN_END].append(self.chain[CHAIN_END])
        for ln in itertools.chain(self.lines, self.beyond.values()):
            if CHAIN_END < ln.n <= TOP:
                self.by_game[ln.n].append(ln)
        self.legal = set()
        self.cands = collections.defaultdict(list)     # n -> [(line of n - 1, its extension to n)], legal lines only
        self.unfinished = {}
        bad, off, count = [], [], 0
        for g in range(CHAIN_END, TOP + 1):
            for ln in self.by_game[g]:
                count += 1
                res = replay_extension(ln.moves, g, g + 1 if g < TOP else None)
                if res is None:
                    bad.append((g, ln.score))
                elif res[0] != ln.score:
                    off.append((g, ln.score))
                else:
                    if g < TOP:
                        self.cands[g + 1].append((ln, res[:4]))
                    if ln is self.known[g]:
                        self.legal.add(g)
                        if res[4]:
                            self.unfinished[g] = res[4]
        self.checks.append(("replay", f"{count - len(bad) - len(off)} of {count} recorded lines of the games "
                                      f"{CHAIN_END}..{TOP} replay legally with the score recorded; illegal {bad[:10]}, "
                                      f"score off {off[:10]}; the best line of {len(self.legal)} of "
                                      f"{TOP - CHAIN_END + 1} games; best lines that are not over: "
                                      f"{sorted(self.unfinished)[:10]}"))
        self.log(f"replayed {count} lines")

    def single_losses(self):
        """For every legal line of n - 1: x_min, the smallest move whose loss makes room for n (0 if none need be
        lost, None if no single move will)."""
        self.sl = {}
        for n in range(FIRST, TOP + 1):
            self.sl[n] = [(ln, single_loss(ln.moves, n)[0]) for ln, _ in self.cands.get(n, ())]
        self.log("single-loss rule done")

    def construct(self, n, kind, order, detail):
        """Keep a game built by the audit that scores above the best-known score of n, after a replay by the rules."""
        score = replay(order, n) if order else None
        if score is None or score <= self.bscore[n]:
            self.unverified.append((n, kind))
            return False
        self.constructions.append({"n": n, "kind": kind, "score": score, "best_known": self.bscore[n],
                                   "gain": score - self.bscore[n], "legal": True, "detail": detail,
                                   "moves": list(order)})
        return True

    # -- the relations of one game ---------------------------------------------------------------------------------

    def audit_game(self, n):
        a, b = self.score[n - 1], self.bscore[n]
        self.A, self.B = a, b
        kind = self.kind[n]
        self.applies["W1"] += 1
        if b > self.gc[n]["bound"]:
            self.contradictions.append((n, "W1", n, b - self.gc[n]["bound"]))
        self.structure(n)
        # N4, the ceiling: also the only relation that speaks for the proven game 5060 at n = 5061
        self.at_most(n, "N4", 0, "opt(n) <= opt(n-1) + n")
        # the lines of n - 1: N3 (monotonicity, by the construction of its proof), N6 and S1 (the step theorem and the
        # single-loss rule), N7a (the half lemma); each gives a game of n, and the highest of them is the bound
        cands = self.cands.get(n, ())
        if cands:
            ln, (_, ext_score, m, left_out) = max(cands, key=lambda c: c[1][1])
            how = (f"n follows a game of score {ln.score}" if m is None else
                   f"n goes before {m}, {'left out' if left_out else 'kept'}, in a game of score {ln.score}")
            plain = "; B <= A, which N3 alone forbids" if b <= a else ""
            self.at_least(n, "N3", ext_score, how + plain)
            if ext_score > b:
                self.construct(n, "N3", self.n3_order(n, ln, m, left_out), how)
            zero = [ln for ln, x in self.sl[n] if x == 0]
            if zero:
                ln = max(zero, key=lambda t: t.score)
                self.at_least(n, "N6", ln.score + n, f"a line of n-1 scoring {ln.score} is playable with n")
                if ln.score + n > b:
                    self.construct(n, "N6", build_game(set(ln.moves) | {n}, n),
                                   f"the line of n-1 scoring {ln.score} plus n")
            loss = [(ln, x) for ln, x in self.sl[n] if x]
            if loss:
                ln, x = max(loss, key=lambda t: t[0].score - t[1])
                self.at_least(n, "S1", ln.score + n - x, f"x_min = {x} on a line of n-1 scoring {ln.score}")
                if ln.score + n - x > b:
                    self.construct(n, "S1", build_game((set(ln.moves) | {n}) - {x}, n),
                                   f"the line of n-1 scoring {ln.score} plus n, less {x}")
            if n % 2 == 0:
                left = [ln for ln, _ in cands if n // 2 not in set(ln.moves)]
                if left:
                    ln = max(left, key=lambda t: t.score)
                    self.at_least(n, "N7a", ln.score + n, f"a line of n-1 scoring {ln.score} leaves {n // 2} out")
        if kind == "prime":
            self.equal(n, "N5", PREV_PRIME[n], f"q(n-1) = {PREV_PRIME[n]}")
        if kind == "half-out":
            self.at_least(n, "N7b", a + n, f"{n // 2} not in U*(n-1), U at n-1")
        # J3, the semiprime formula (also the check of x against the sum of U*)
        if n % 2 == 1 and OMEGA[n] == 2 and n >= 189:
            x = j3_x(n, self.layer2)
            if x is None:
                self.consistency.append((n, "J3", "n closes a cycle", "no cycle", ""))
            else:
                self.equal(n, "J3", x, f"x = {x}")
                if kind == "exchange" and self.exchange_x(n) != x:
                    self.consistency.append((n, "J3x", f"x = {x} (the cycle)", f"x = {self.exchange_x(n)} (U*)", ""))
        # L2 and L4
        if n % 8 == 0 and is_prime(n // 8) and n >= 187:
            p = n // 8
            r = PREV_PRIME[p]
            if 9 * r > n:
                self.at_most(n, "L2", 4 * r, f"p = {p}, r = {r}")
        if n % 12 == 0 and is_prime(n // 12) and n >= 187:
            self.check_l4(n)
        # the conjectured laws
        if kind == "exchange":
            x = self.exchange_x(n)
            sh = shadow(n)
            self.equal(n, "EXL", x, f"x = {x}" + ("" if x == sh else f"; the shadow is {sh}, not x"))
            if x != sh:
                self.consistency.append((n, "SHADOW", f"x = shadow = {sh}", f"x = {x}", "from the sum of U*"))
        c = n // LPF[n]
        if c in FAMILIES and is_prime(LPF[n]):
            rel, pattern, depth = FAMILIES[c]
            if clean_depth(n) >= depth:
                self.equal(n, rel, family_delta(n, pattern), f"window clean to depth {clean_depth(n)}")
        if c == 9 and is_prime(LPF[n]):
            self.equal(n, "COF9", 0, "n = 9P is at its ceiling")
        if kind in ("relax", "restrict") and n >= 187:
            delta_pb = n - (self.gc[n]["bound"] - self.gc[n - 1]["bound"])
            depth = clean_depth(n)
            if depth >= 3:
                self.equal(n, "CWEQ", delta_pb, f"delta_PB = {delta_pb}, depth {depth}")
            elif depth == 2:
                self.equal(n, "CWEQ2", delta_pb, f"delta_PB = {delta_pb}, depth {depth}")
            if depth >= 2:
                self.at_most(n, "CWINEQ", delta_pb, f"delta_PB = {delta_pb}, depth {depth}")

    def structure(self, n):
        """N1, N2 and F10 on the best line of n: it is over, opens with q(n), plays no other prime, and from 187 on
        plays no number of layer 2 up to n/2; a game that does not is not optimal (short by at least 1, or by the
        largest number that can still be played)."""
        self.applies["STRUCT"] += 1
        moves = self.best[n].moves
        primes = [x for x in moves if OMEGA[x] == 1]
        low = [x for x in moves if n >= 187 and OMEGA[x] == 2 and x <= n // 2]
        if primes != [QPRIME[n]] or moves[0] != QPRIME[n] or low:
            self.emit(n, "STRUCT", n, 1, f"primes played {primes[:3]}, opens with {moves[0]}, layer 2 up to n/2: "
                                         f"{low[:3]}")
        if self.unfinished.get(n):
            left = self.unfinished[n]
            self.emit(n, "STRUCT", n, max(left), f"the game is not over (N2): {left[:5]} can still be played")

    @staticmethod
    def n3_order(n, line, m, left_out):
        """The game of n that the proof of monotonicity builds from a line of n - 1: n put before m (m dropped if it
        is left out), or after the last move if n can follow."""
        moves = list(line.moves)
        if m is None:
            return moves + [n]
        i = moves.index(m)
        return moves[:i] + [n] + ([] if left_out else [m]) + moves[i + 1:]

    def check_l4(self, n):
        """The 12p theorem needs 8p, 8r, 12r and 8t in U*(n) for a prime t with 4p/3 < t <= 3p/2, and 15r > n."""
        p = n // 12
        r = PREV_PRIME[p]
        if 15 * r <= n:
            self.l4_skipped["15r <= n"] += 1
            return
        kept = set(ustar_layer(n, 4))
        ts = [t for t in range(4 * p // 3, 3 * p // 2 + 1) if is_prime(t) and 3 * t > 4 * p and 2 * t <= 3 * p]
        t_ok = [t for t in ts if 8 * t in kept]
        if {8 * p, 8 * r, 12 * r} <= kept and t_ok:
            self.at_most(n, "L4", 6 * r, f"p = {p}, r = {r}, t = {t_ok[0]}")
        else:
            miss = [name for name, v in (("8p", 8 * p), ("8r", 8 * r), ("12r", 12 * r)) if v not in kept]
            self.l4_skipped["hypothesis not in U*(n): " + (",".join(miss) if miss else "no 8t")] += 1

    # -- relations between games that are not neighbors ------------------------------------------------------------

    def repeat_groups(self):
        """The repeat lemma (R6, part 1).  Games with one root problem (one digest, as the solver's setup compares
        them) share the promotion sum P = score - sum of U* of their best line, when each line plays all of U* and
        promotions (the moves above n/2 add to the sum of U*): a game of one is a game of each other, made from the
        same promotions.  So every game whose P is below the group's greatest is short by the difference."""
        groups = collections.defaultdict(list)
        for g, d in self.digest.items():
            groups[d].append(g)
        self.groups = groups
        self.group_sizes = collections.Counter(len(v) for v in groups.values())

        def promotion_sum(g):
            if g <= CHAIN_END:
                ln = self.chain[g]
                return None if ln.bag is None else ln.score - ln.bag
            ln = self.known[g] if g in self.proven else self.best[g]
            if ln.bag is None or ln.big != ln.bag:
                return None
            return ln.score - ln.bag

        self.r6_unrealized = []
        for members in groups.values():
            if len(members) < 2:
                continue
            vals = {g: promotion_sum(g) for g in members}
            vals = {g: v for g, v in vals.items() if v is not None}
            if len(vals) < 2 or max(vals) <= CHAIN_END:
                continue
            top = max(vals.values())
            src = min(g for g, v in vals.items() if v == top)
            proven_vals = [v for g, v in vals.items() if g <= CHAIN_END or g in self.proven]
            if proven_vals:
                for g, v in vals.items():
                    if g not in self.proven and g > CHAIN_END and v > max(proven_vals):
                        self.contradictions.append((g, "R6", g, v - max(proven_vals)))
            for g, v in sorted(vals.items()):
                if g <= CHAIN_END or g in self.proven:
                    continue
                self.applies["R6"] += 1
                if v == top:
                    self.tight["R6"] += 1
                    continue
                note = f"promotion sum {v} against {top} of game {src}; group {sorted(members)}"
                self.emit(g, "R6", g, top - v, note)
                src_ln = self.known.get(src) if src > CHAIN_END else (self.chain[src] if src == CHAIN_END else None)
                if src_ln is None or src_ln.moves is None:
                    continue
                half = src // 2
                members_set = {x for x in self.best[g].moves if x > g // 2} | {x for x in src_ln.moves if x <= half}
                order = build_game(members_set, g)
                if order is None:
                    self.r6_unrealized.append(g)
                else:
                    self.construct(g, "R6", order, f"the sources of g with the promotions of the line of {src}")
        self.log("repeat groups done")

    def root_problem_checks(self):
        """J2 (proved: a number with two prime factors from 188 on poses the root problem of n - 1, of n - 2 if n - 1
        is prime) and the half law (measured: an even n poses it iff n/2 is not in U*(n - 1)), read from the digests
        that the miner's setup computed.  These test the miner's root problems, not a score."""
        counts = collections.Counter()
        for n in range(FIRST, TOP + 1):
            kind = self.kind[n]
            m = n - 2 if is_prime(n - 1) else n - 1
            if n in self.digest and m in self.digest:
                same = self.digest[n] == self.digest[m]
            else:
                same = None
            if OMEGA[n] == 2 and n >= 188 and not is_prime(n):
                if same is None:
                    counts["J2 no digest"] += 1
                else:
                    counts["J2 agree" if same else "J2 differ"] += 1
                    if not same:
                        self.consistency.append((n, "J2", f"root problem of game {m}", "another root problem", ""))
            if n % 2 == 0 and kind in ("half-out", "relax") and n != 14 and same is not None:
                expect = kind == "half-out"
                counts["half law agree" if same == expect else "half law differ"] += 1
                if same != expect:
                    self.consistency.append((n, "HALF", "same root problem" if expect else "another root problem",
                                             "same root problem" if same else "another root problem", f"{kind}"))
        self.root_counts = counts

    def proven_games(self):
        """The proven games past the chain against their best-known scores."""
        for n, ln in sorted(self.beyond.items()):
            self.applies["PROVEN"] += 1
            if self.bscore[n] < ln.score:
                self.emit(n, "PROVEN", n, ln.score - self.bscore[n], f"proven {ln.score}, best-known {self.bscore[n]}")
            elif self.bscore[n] > ln.score:
                self.contradictions.append((n, "PROVEN", n, self.bscore[n] - ln.score))
            else:
                self.tight["PROVEN"] += 1

    def projections(self):
        """The moves of a game of N that are at most n, in their order, form a game of n (the ceiling lemma N4 applied
        once for each number above n; neighbors.md, and solver/docs/unsound/shortfalls.md uses it as its repair).
        Every recorded line of every N > n is projected onto every n; the best one that beats the best-known score of
        n is replayed by the rules before it is kept."""
        sources = list(self.lines) + [ln for ln in self.beyond.values()]
        bs = [0] * (TOP + 2)
        for n, v in self.bscore.items():
            bs[n] = v
        beats = collections.defaultdict(list)
        for idx, ln in enumerate(sources):
            srt = sorted(ln.moves)
            pre = list(itertools.accumulate(srt))
            j = len(srt)
            for n in range(min(ln.n - 1, TOP), FIRST - 1, -1):
                while j and srt[j - 1] > n:
                    j -= 1
                if j and pre[j - 1] > bs[n]:
                    beats[n].append((pre[j - 1], -ln.n, idx))
        self.log("projections scanned")
        self.proj, self.proj_windows = {}, {}
        for w in WINDOWS:
            games = {n: max((s for s, negn, _ in v if -negn - n <= w), default=None) for n, v in beats.items()}
            games = {n: s - bs[n] for n, s in games.items() if s is not None}
            self.proj_windows[w] = (len(games), max(games.values(), default=0), sum(games.values()))
        self.applies["PROJ"] = TOP - FIRST
        for n, v in sorted(beats.items()):
            score, negn, idx = max(v)
            big_n = -negn
            order = [x for x in sources[idx].moves if x <= n]
            if replay(order, n) != score:
                self.checks.append(("projection replay", f"game {n} from N={big_n} did not replay"))
                continue
            gain = score - bs[n]
            self.proj[n] = {"n": n, "source_N": big_n, "score": score, "best_known": bs[n], "gain": gain,
                            "window": big_n - n, "sources_beating": len(v), "legal": True, "moves": order}
            self.emit(n, "PROJ", n, gain, f"N - n = {big_n - n}; {len(v)} recorded lines beat it", via=big_n)
        self.log(f"projections: {len(self.proj)} games beaten")

    # -- the mining targets ----------------------------------------------------------------------------------------

    def targets(self, plays, ledger_meta):
        """The games past 5060 whose best-known score no proved relation determines from the game before: not a prime
        (N5), not at the ceiling (N4; N7 where n is a half-out step), not at the bound of L2 or L4 with its hypothesis
        met, not at J3's value, and not a later member of a group of games that pose one root problem (R6).  A short
        streak can start only at such a game."""
        self.ledger_meta = ledger_meta
        self.ledger_plays = plays
        rank = ["N5", "N7", "N4", "L2", "L4", "J3", "R6"]
        by_game, by_short = collections.defaultdict(list), collections.defaultdict(list)
        for r in self.rows:
            if r["proved"] == "no":
                by_game[r["n"]].append(r)
                if r["short_game"] != r["n"]:
                    by_short[r["short_game"]].append(r)
        r6_short = {r["short_game"] for r in self.rows if r["relation"] == "R6"}
        self.settled = collections.Counter()
        self.only_j3 = []
        self.targets_rows = []
        for n in range(FIRST, TOP + 1):
            met = self.met[n]
            settles = set()
            if "N5" in met:
                settles.add("N5")
            if met & {"N7a", "N7b"}:
                settles.add("N7")
            for code in ("N4", "L2", "L4", "J3"):
                if code in met:
                    settles.add(code)
            d = self.digest.get(n)
            if d and n not in r6_short and any(g < n for g in self.groups[d]):
                settles.add("R6")
            if settles:
                self.settled[min(settles, key=rank.index)] += 1
                if settles == {"J3"}:
                    self.only_j3.append(n)
                continue
            a, b = self.score[n - 1], self.bscore[n]
            history = plays.get(n, [])
            counts = collections.Counter(f"s{seed}L{level}{mark}" for level, seed, _, _, mark in history)
            raises = [new - known for _, _, known, new, _ in history if new > known]
            laws = by_game.get(n, []) + by_short.get(n, [])
            self.targets_rows.append({
                "n": n, "step": W4_STEP[self.kind[n]], "brief_step": self.kind[n], "layer": OMEGA[n],
                "cofactor": n // LPF[n], "parity_gap": self.gc[n]["bound"] - b, "best_known": b,
                "delta_best_known": a + n - b, "plays": len(history),
                "seeds_levels": ",".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(counts.items())),
                "raised_by_play": "yes" if raises else "no", "best_raise": max(raises, default=0),
                "law_disagreements": "; ".join(f"{r['relation']}: game {r['short_game']} short by {r['at_least']}"
                                               for r in laws)})
        self.log(f"targets: {len(self.targets_rows)}")

    # -- checks of the inputs and of the audit's own steps ---------------------------------------------------------

    def data_checks(self):
        """What the audit leans on that is not a theorem: the sums of U* and the parity bounds of games.csv, the step
        kinds of past5060.csv, and the audit's own peel and single-loss shortcuts, each against a slower direct way."""
        add = self.checks.append
        bag_bad = [n for n in range(FIRST, TOP + 1) if self.best[n].bag is not None
                   and self.best[n].bag != self.gc[n]["ustar"]]
        add(("sum of U*", f"the in_the_bag of every best line equals games.csv's ustar: {len(bag_bad)} differ "
                          f"{bag_bad[:5]}; at 5060 the chain says {self.chain[CHAIN_END].bag}, games.csv "
                          f"{self.gc[CHAIN_END]['ustar']}"))
        with open(PAST) as f:
            past = {int(r["n"]): r for r in csv.DictReader(f)}
        diff = [n for n in range(FIRST, TOP + 1) if n in past and past[n]["step"] != self.kind[n]]
        add(("step kinds", f"past5060.csv's step against the one read from games.csv's ustar: {len(diff)} differ "
                           f"{[(n, past[n]['step'], self.kind[n]) for n in diff[:5]]}; "
                           f"{collections.Counter(self.kind[n] for n in range(FIRST, TOP + 1))}"))
        pb = self.gc
        ceil_bad = [n for n in range(FIRST, TOP + 1) if pb[n]["bound"] > pb[n - 1]["bound"] + n]
        prime_bad = [n for n in range(FIRST, TOP + 1)
                     if is_prime(n) and pb[n]["bound"] != pb[n - 1]["bound"] + n - PREV_PRIME[n]]
        add(("parity bound", f"games.csv's bound obeys PB(n) <= PB(n-1) + n (fails at {len(ceil_bad)}) and the prime "
                             f"step PB(p) = PB(p-1) + p - q(p-1) (fails at {len(prime_bad)})"))
        # the sum of U* by Gaussian elimination, on boards spread over the range
        step = max(1, (TOP - FIRST) // 24)
        picks = [CHAIN_END] + list(range(FIRST + 17, TOP + 1, step))
        bad = []
        for n in picks:
            got = sum(ustar(n))
            if got != self.gc[n]["ustar"]:
                bad.append((n, got, self.gc[n]["ustar"]))
        add(("sum of U* again", f"descending greedy as a GF(2) basis on {len(picks)} boards agrees with games.csv at "
                                f"{len(picks) - len(bad)}; differences {bad}"))
        self.log("U* sample done")
        # the single-loss shortcut against the whole-set peel of the succession study
        done, wrong = 0, []
        for n in range(FIRST + 5, TOP + 1, max(1, (TOP - FIRST) // 30)):
            moves = self.known[n - 1].moves
            x, tried = single_loss(moves, n)
            if x is None:
                continue
            full = set(moves) | {n}
            ok = common.playable(full - {x}, n, SPF)
            others = [y for y in sorted(moves) if y < x and y not in tried][:3]
            ok_fail = all(not common.playable(full - {y}, n, SPF) for y in tried[:3] + others)
            done += 1
            if not (ok and ok_fail):
                wrong.append(n)
        add(("single-loss shortcut", f"x_min of the layer-instance method against the whole-set peel on {done} "
                                     f"games (x_min playable; three failed candidates and three other smaller moves "
                                     f"not): wrong at {wrong}"))
        # monotonicity's construction replayed in full on a sample
        done, wrong = 0, []
        for n in sorted(self.cands):
            if n % 97:
                continue
            for ln, (_, ext_score, m, left_out) in self.cands[n]:
                done += 1
                if replay(self.n3_order(n, ln, m, left_out), n) != ext_score:
                    wrong.append((n, ln.score))
        add(("monotonicity's construction", f"replayed in full on {done} (game, line) pairs: wrong at {wrong}"))
        add(("constructions", f"every game that a bound above says is short and that the audit tried to build "
                              f"was built and replayed above the best-known score; not so for {self.unverified}"))
        self.log("checks done")

    def targets_summary(self):
        t = self.targets_rows
        out = [f"MINING TARGETS (targets.csv): games past 5060 whose best-known score no proved relation determines "
               f"from the game before: {len(t)} of {TOP - FIRST + 1}"]
        steps = collections.Counter(r["step"] for r in t)
        brief = {r["step"]: r["brief_step"] for r in t}
        out.append("  by step kind (W4 name, the brief's name): " + ", ".join(
            f"{k} ({brief[k]}) {v}" for k, v in sorted(steps.items(), key=lambda kv: -kv[1])))
        plays = collections.Counter(min(r["plays"], 3) for r in t)
        out.append("  by plays so far in all the ledgers: " + ", ".join(
            f"{'3 or more' if k == 3 else k}: {plays[k]}" for k in range(4)))
        for step in sorted(steps, key=lambda k: -steps[k]):
            sub = collections.Counter(min(r["plays"], 3) for r in t if r["step"] == step)
            out.append(f"    {step:9} plays 0: {sub[0]:>4}  1: {sub[1]:>4}  2: {sub[2]:>4}  3 or more: {sub[3]:>4}")
        raised = [r for r in t if r["raised_by_play"] == "yes"]
        laws = [r for r in t if r["law_disagreements"]]
        gain = sum(r["best_raise"] for r in raised)
        out.append(f"  raised by a dedicated play: {len(raised)} games, {gain} points in their largest raises; "
                   f"disagreeing with a conjectured law: {len(laws)}")
        out.append("  settled instead, by the first of N5, N7, N4, L2, L4, J3, R6 that holds: "
                   + ", ".join(f"{k} {self.settled[k]}" for k in ("N5", "N7", "N4", "L2", "L4", "J3", "R6"))
                   + f"; settled by J3 and by none of the others: {len(self.only_j3)}")
        played = set(self.ledger_plays)
        for m in self.ledger_meta:
            name = os.path.relpath(m["path"], "/home/brian/taxman_work/lab/work")
            out.append(f"  {name} read at {m['read_at']} (last written {m['mtime']}): {m['rows']} plays of "
                       f"{m['games']} games, {m['bad']} unreadable lines")
        out.append(f"  {sum(m['rows'] for m in self.ledger_meta)} plays of {len(played)} games in all; "
                   f"{len(played - {r['n'] for r in t})} of those games are not targets now (a play raised them to a "
                   f"relation's value, or they are settled)")
        out.append("")
        return "\n".join(out)

    # -- the files -------------------------------------------------------------------------------------------------

    def write_files(self):
        order = {code: i for i, code in enumerate(RELATIONS)}
        rows = sorted(self.rows, key=lambda r: (r["n"], order[r["relation"]], r["short_game"]))
        cols = ["n", "relation", "proved", "short_game", "short_is", "at_least", "known_score", "must_reach", "note"]
        with open(os.path.join(OUT, "disagreements.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(OUT, "projections.jsonl"), "w") as f:
            for n in sorted(self.proj):
                f.write(json.dumps(self.proj[n]) + "\n")
        with open(os.path.join(OUT, "constructions.jsonl"), "w") as f:
            for rec in sorted(self.constructions, key=lambda r: (r["n"], r["kind"])):
                f.write(json.dumps(rec) + "\n")
        with open(os.path.join(OUT, "consistency.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["n", "check", "expected", "found", "note"])
            w.writerows(sorted(self.consistency))
        cols = ["n", "step", "brief_step", "layer", "cofactor", "parity_gap", "best_known", "delta_best_known", "plays",
                "seeds_levels", "raised_by_play", "best_raise", "law_disagreements"]
        with open(os.path.join(OUT, "targets.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(self.targets_rows)
        self.rows_sorted = rows

    def summary(self):
        out = []
        p = out.append
        m = self.meta
        p(f"Audit of the best-known Taxman games {FIRST}..{TOP}  (audit.py; README.md says what each relation is)")
        p(f"best-known.jsonl read once at {m['read_at']}: {m['bytes']:,} bytes (last written {m['mtime']}), "
          f"{m['lines']:,} lines, sha256 of those bytes {m['sha256'][:16]}..., torn last line dropped: "
          f"{m['torn_last_line']}")
        p(f"run finished {now_pacific()}, {time.time() - T0:,.0f} s; A = best-known (or proven) score of n - 1, "
          f"B = best-known score of n")
        p("")
        p("PER RELATION: games it applies to / of them met with equality by the best-known score / games it says "
          "are short (rows) / the most any is short by, at least")
        p(f"{'relation':8} {'proved':13} {'applies':>8} {'equal':>6} {'short games':>12} {'rows':>6} {'most':>10}  "
          f"what")
        for code, (status, what) in RELATIONS.items():
            rows = [r for r in self.rows if r["relation"] == code]
            most = max((r["at_least"] for r in rows), default=0)
            p(f"{code:8} {status:13} {self.applies[code]:>8} {self.tight[code]:>6} {len(self.hits[code]):>12} "
              f"{len(rows):>6} {most:>10}  {what}")
        p("")
        p(f"L4's hypothesis (8p, 8r, 12r and some 8t in U*(n), 15r > n) was not met at: {dict(self.l4_skipped)}")
        p(f"R6: root-problem groups by size {dict(sorted(self.group_sizes.items()))}; transfers that were not "
          f"playable: {self.r6_unrealized}")
        p(f"root problems against J2 and the half law: {dict(self.root_counts)} (consistency.csv lists the "
          f"differences)")
        p("")
        for status, label in (("yes", "proved, no assumption beyond the rules"), ("yes, given U", "proved given U")):
            games, n_rows = set(), 0
            for code, (st, _) in RELATIONS.items():
                if st == status:
                    games |= self.hits[code]
                    n_rows += sum(1 for r in self.rows if r["relation"] == code)
            p(f"Games certainly short by relations {label}: {len(games)} ({n_rows} rows)")
        proved_all = set()
        for code, (st, _) in RELATIONS.items():
            if st.startswith("yes"):
                proved_all |= self.hits[code]
        in_range = {g for g in proved_all if FIRST <= g <= TOP}
        p(f"Contradictions (a proven game, or a proved bound, against a best-known score): "
          f"{self.contradictions if self.contradictions else 'none'}")
        verdict = "YES" if not in_range else "NO"
        p(f"EVERY BEST-KNOWN GAME PAST 5060 AGREES WITH EVERY PROVED RELATION: {verdict}"
          + ("" if verdict == "YES" else f" ({len(in_range)} games are certainly short)"))
        p("")
        p("PROJECTIONS (moves of a recorded game of N that are at most n): games beaten, largest gain, total gain, "
          "by the largest N - n allowed")
        for w, (cnt, mx, tot) in self.proj_windows.items():
            label = "any N" if w >= 10 ** 9 else f"N - n <= {w}"
            p(f"  {label:12} {cnt:>6} games {mx:>10} {tot:>12}")
        p(f"  {len(self.proj)} games are beaten by a replayed projection (projections.jsonl); "
          f"{len(self.constructions)} further games built and replayed (constructions.jsonl)")
        by_kind = collections.Counter(c["kind"] for c in self.constructions)
        p(f"  constructions by relation {dict(by_kind)}")
        p("")
        p("LARGEST DISAGREEMENTS WITH CONJECTURED LAWS, by the game that would be short (the laws and the rows they "
          "come from)")
        short = {}
        for r in self.rows:
            if r["proved"] == "no":
                e = short.setdefault(r["short_game"], [0, set(), set()])
                e[0] = max(e[0], r["at_least"])
                e[1].add(r["relation"])
                e[2].add(r["n"])
        p(f"  {len(short)} games would be short if the laws held ({sum(1 for e in short.values() if e[0] >= 100)} by "
          f"100 or more)")
        for g, (by, rels, ns) in sorted(short.items(), key=lambda kv: -kv[1][0])[:25]:
            p(f"  game {g:>5} by at least {by:>5} to {self.score[g] + by:>11}   {', '.join(sorted(rels))}   (row n = "
              f"{', '.join(map(str, sorted(ns)))})")
        p("")
        p(self.targets_summary())
        p("DATA CHECKS")
        for name, text in self.checks:
            p(f"  {name}: {text}")
        return "\n".join(out) + "\n"


def run(lines, meta, chain, beyond):
    """Every check, in order, on the given lines (selftest.py runs it on lines with planted defects)."""
    plays, ledger_meta = load_ledgers(LEDGERS)
    audit = Audit()
    audit.prepare(lines, meta, chain, beyond)
    audit.replay_all()
    audit.single_losses()
    for n in range(FIRST, TOP + 1):
        audit.audit_game(n)
    audit.log("relations of each game done")
    audit.repeat_groups()
    audit.root_problem_checks()
    audit.proven_games()
    audit.projections()
    audit.targets(plays, ledger_meta)
    audit.data_checks()
    return audit


def main():
    init_tables(TOP)
    print(f"[{time.time() - T0:6.1f} s] tables built", file=sys.stderr, flush=True)
    lines, meta = load_best_known(BEST)
    print(f"[{time.time() - T0:6.1f} s] best-known read: {len(lines)} lines", file=sys.stderr, flush=True)
    audit = run(lines, meta, load_chain(), load_beyond())
    audit.write_files()
    text = audit.summary()
    with open(os.path.join(OUT, "summary.txt"), "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
