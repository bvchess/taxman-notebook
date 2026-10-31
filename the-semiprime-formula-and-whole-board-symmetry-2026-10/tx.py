"""Small, independent Taxman tools for checking theorems on small boards.

Playability by dismantling (the core theorem P7), descending greedy for U*, and an exhaustive branch and bound that
lists every optimal set of a small board.  Shares no code with the prover or the frame solver.
"""
from functools import lru_cache


def spf_table(n):
    spf = list(range(n + 1))
    for i in range(2, int(n ** 0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, n + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


SPF = spf_table(20000)


def factors(x):
    fs = []
    while x > 1:
        p = SPF[x]
        fs.append(p)
        x //= p
    return fs


def omega(x):
    return len(factors(x))


def mf(x):
    """Maximal factors of x (x / p for each distinct prime p of x); a prime's is 1."""
    return sorted({x // p for p in set(factors(x))})


def is_prime(x):
    return x >= 2 and SPF[x] == x


def q(n):
    while not is_prime(n):
        n -= 1
    return n


def playable_instance(members, pool):
    """Dismantling: delete a member that lists a factor no other remaining member lists.  Playable iff it empties."""
    lists = {x: [f for f in mf(x) if f in pool] for x in members}
    alive = set(members)
    count = {}
    for x in alive:
        for f in lists[x]:
            count[f] = count.get(f, 0) + 1
    changed = True
    while changed and alive:
        changed = False
        for x in list(alive):
            if any(count[f] == 1 for f in lists[x]):
                alive.discard(x)
                for f in lists[x]:
                    count[f] -= 1
                changed = True
    return not alive


def playable(S):
    """A set S of numbers >= 2 is playable iff its own instance is (P2, P7)."""
    S = set(S)
    pool = {f for x in S for f in mf(x)} - S
    return playable_instance(S, pool)


def ustar(n):
    """Descending greedy over the sources of n: keep each source still playable with those kept above it."""
    kept = []
    for s in range(n, n // 2, -1):
        if s < 2:
            continue
        if playable(kept + [s]):
            kept.append(s)
    return kept


def primes_upto(m):
    return [p for p in range(2, m + 1) if is_prime(p)]


def is_forest_layer2(edges, n):
    """Edges: numbers of layer 2; vertices: primes up to n/2 and the ground g.  Union-find."""
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for e in edges:
        fs = factors(e)
        a, b = (fs[0], fs[1]) if fs[0] != fs[1] else (fs[0], 'g')
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
    return True


def layer2_closed(n, U=None):
    """The frames of layer 2 are closed iff U*_2 has one edge for each prime up to n/2 (F4, step 7)."""
    if U is None:
        U = ustar(n)
    u2 = [s for s in U if omega(s) == 2]
    return len(u2) == len(primes_upto(n // 2))


def brute_opt(n, want_sets=True):
    """Exhaustive branch and bound over the numbers n down to 2: every playable set of the largest weight.

    Playability is hereditary (restriction), so a branch whose chosen set is unplayable is cut.  The bound is the
    chosen weight plus the largest numbers still undecided, no more of them than the factors not yet chosen could pay
    for: every member pays with a distinct number outside the set, so |S| <= n - |S|.
    """
    order = list(range(n, 1, -1))
    best = [0, []]
    chosen = []

    def rec(i, w):
        rest = order[i:]
        # members so far + k more, payments distinct and outside S, all in 1..n
        room = (n - 2 * len(chosen)) // 2 + 1
        bound = w + sum(rest[:max(0, room)])
        if bound < best[0] or (not want_sets and bound <= best[0]):
            return
        if i == len(order):
            if w > best[0]:
                best[0] = w
                best[1] = [sorted(chosen)]
            elif w == best[0] and want_sets:
                best[1].append(sorted(chosen))
            return
        x = order[i]
        chosen.append(x)
        if playable(chosen):
            rec(i + 1, w + x)
        chosen.pop()
        rec(i + 1, w)

    rec(0, 0)
    return best[0], best[1]
