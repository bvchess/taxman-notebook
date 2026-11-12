#!/usr/bin/env python3
"""Helpers for E5: independence at both parities, the residual of a set's own instance, and an inclusion-minimal
core inside it.  Imported by cores.py; nothing runs on import.

Parity vectors (docs/theory/parity-bound.md, W1): on board m, the parity-i vector of s is v(s), its maximal factors
(coordinates 1..m/2), when Omega(s) and i differ in parity; e_s when they agree and s <= m/2; and an extra coordinate,
which no other vector shares, when they agree and s > m/2.  A set is independent at both parities iff it is
independent with its own coordinates, iff the lists of its own instance are independent over GF(2) (W1, step 1), so
every core of an independent set's own instance is an odd core (playability.md, "Odd cores")."""
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import predict  # noqa: E402

common, spf, MF = predict.common, predict.spf, predict.MF


def omega(x):
    return len(common.factor(x))


def circuit(m, members, y, parity):
    """The members of `members` (independent at `parity` on board m) whose parity vectors sum to y's, or None when
    y's vector is independent of theirs.  An element with an extra coordinate is independent of everything."""
    def vec(s):
        if (omega(s) - parity) % 2:
            return sum(1 << f for f in MF[s])
        return (1 << s) if 2 * s <= m else None
    basis = {}  # pivot bit -> (vector, combination of members as a frozenset)
    order = sorted(members)
    for s in order:
        v = vec(s)
        if v is None:
            continue
        combo = {s}
        while v:
            p = v.bit_length() - 1
            if p not in basis:
                basis[p] = (v, frozenset(combo))
                break
            bv, bc = basis[p]
            v ^= bv
            combo ^= bc
        else:
            raise ValueError(f"the members are dependent at parity {parity}: {sorted(combo)}")
    v = vec(y)
    if v is None:
        return None
    combo = set()
    while v:
        p = v.bit_length() - 1
        if p not in basis:
            return None
        bv, bc = basis[p]
        v ^= bv
        combo ^= bc
    return combo


def independent(m, members):
    """Whether `members` is independent at both parities on board m; else (parity, a dependent subset)."""
    for parity in (0, 1):
        try:
            circuit(m, members, 2, parity)
        except ValueError as e:
            return False, (parity, str(e))
    return True, None


def lists_of(members):
    members = set(members)
    return {x: MF[x] - members for x in members}


def residual_of(lists, alive):
    """Dismantle the instance with these lists, restricted to the members `alive` (playability.md, P5)."""
    alive = set(alive)
    listers = {}
    for x in alive:
        for f in lists[x]:
            listers.setdefault(f, set()).add(x)
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


def minimal_core(members, keep=None):
    """An inclusion-minimal core of the own instance of `members` (holding `keep` if it can), or the empty set."""
    lists = lists_of(members)
    core = residual_of(lists, members)
    changed = True
    while changed:
        changed = False
        for x in sorted(core, key=lambda x: (x == keep, -x)):
            if x == keep:
                continue
            smaller = residual_of(lists, core - {x})
            if smaller and (keep is None or keep in smaller or keep not in core):
                core = smaller
                changed = True
                break
    return core, {x: sorted(lists[x]) for x in core}


def rank_gf2(rows):
    basis = {}
    r = 0
    for v in rows:
        while v:
            p = v.bit_length() - 1
            if p not in basis:
                basis[p] = v
                r += 1
                break
            v ^= basis[p]
    return r


def is_odd(core_lists):
    """A core is odd when its lists are independent over GF(2)."""
    return rank_gf2([sum(1 << f for f in fs) for fs in core_lists.values()]) == len(core_lists)
