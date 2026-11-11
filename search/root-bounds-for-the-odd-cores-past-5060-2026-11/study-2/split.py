#!/usr/bin/env python3
"""The smooth/fiber split bound.

Smooth = every prime <= 23.  Hubs = smooth numbers <= n/2 listed by fiber rows (x/p for a fiber row x = m.p).
E(X): the exact optimum of the smooth sub-board (smooth sources fixed, smooth candidates of layers >= 3 free) with the
hubs X barred and deleted as columns.  F(X): the parity bound of the fiber part with every hub outside X deleted.
E_mu, F'_mu: the Lagrangian forms with hub prices mu (selling a hub earns mu_h on the smooth side, giving one up earns
mu_h on the fiber side); B_mu = E_mu + F'_mu - mu(hubs) >= max_X [E(X) + F(X)] >= opt.
"""

import heapq
import itertools
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import residual, minimal_core  # noqa: E402
from mi import max_weight_common  # noqa: E402

SMOOTH = 23


class Split:
    def __init__(self, board):
        self.b = board
        n = board.n
        self.half = n // 2
        om, mf, lp = board.om, board.mf, board.lp
        self.smooth_sources = [s for s in board.g if lp[s] <= SMOOTH]
        self.fiber_sources = [s for s in board.g if lp[s] > SMOOTH]
        self.smooth_cands = [x for x in range(2, self.half + 1) if lp[x] <= SMOOTH and om[x] >= 3]
        self.fiber_cands = [x for x in range(2, self.half + 1) if lp[x] > SMOOTH and om[x] >= 3]
        hubs = set()
        for x in self.fiber_sources + self.fiber_cands:
            h = x // lp[x]
            if h <= self.half and lp[h] <= SMOOTH:
                hubs.add(h)
        self.hubs = sorted(hubs)
        self.smooth_elems = {x: (self.pv(x, 0), self.pv(x, 1), x) for x in self.smooth_cands}
        self.fiber_elems = {x: (self.pv(x, 0), self.pv(x, 1), x) for x in self.fiber_cands}

    def pv(self, x, i):
        n, om, mf = self.b.n, self.b.om, self.b.mf
        if om[x] % 2 != i:
            v = 0
            for f in mf[x]:
                v |= 1 << f
            return v
        if x <= self.half:
            return 1 << x
        return None

    def unit(self, h):
        """The unit vector e_h as a pair of parity vectors (e_h at parity Omega(h) mod 2, private at the other)."""
        i = self.b.om[h] % 2
        return (1 << h, None) if i == 0 else (None, 1 << h)

    def base_vectors(self, sources, deleted):
        base = [[], []]
        for s in sources:
            for i in (0, 1):
                v = self.pv(s, i)
                if v is not None:
                    base[i].append(v)
        for h in deleted:
            base[self.b.om[h] % 2].append(1 << h)
        return base

    # ---- the smooth side -------------------------------------------------------------------------------------
    def smooth_playable(self, promoted, deleted):
        """Every layer >= 3 of the smooth sub-board peels, with `promoted` candidates played and `deleted` columns gone."""
        members = set(self.smooth_sources) | set(promoted)
        for k in sorted({self.b.om[x] for x in members}):
            if k < 3:
                continue
            lists = {x: set(f for f in self.b.mf[x] if f not in members and f not in deleted)
                     for x in members if self.b.om[x] == k}
            if residual(lists):
                return False, k, lists
        return True, None, None

    def smooth_exact(self, mu=None, deleted=(), budget=600.0, max_nodes=None):
        """E(deleted) if mu is None, else E_mu (hubs sellable at price mu[h]).  Best-first B&B, core branching.
        Returns dict(value, sold, promoted, evaluated, finished)."""
        elems = dict(self.smooth_elems)
        deleted = set(deleted)
        if mu is not None:
            for h, price in mu.items():
                if price > 0 and h not in deleted:
                    elems[("sell", h)] = self.unit(h) + (price,)
        base = self.base_vectors(self.smooth_sources, deleted)
        t0 = time.time()
        counter = itertools.count()
        heap = [(0, next(counter), frozenset(), frozenset(deleted), None)]
        evaluated = 0
        while heap and time.time() - t0 < budget and (max_nodes is None or evaluated < max_nodes):
            prio, _, picks, bars, done = heapq.heappop(heap)
            if done is not None:
                done["seconds"] = round(time.time() - t0, 1)
                done["evaluated"] = evaluated
                return done
            sub = {x: e for x, e in elems.items() if x not in bars}
            try:
                chosen, value = max_weight_common(sub, base[0], base[1], picks)
            except ValueError:
                continue
            evaluated += 1
            sold = {x[1] for x in chosen if isinstance(x, tuple)}
            promoted = [x for x in chosen if not isinstance(x, tuple)]
            ok, k, lists = self.smooth_playable(promoted, deleted | sold)
            if ok:
                heapq.heappush(heap, (-value, next(counter), picks, bars,
                                      {"value": value, "sold": sorted(sold), "promoted": promoted, "finished": True}))
                continue
            core = minimal_core(lists, set(lists), sorted(lists, reverse=True))
            members = set(self.smooth_sources) | set(promoted)
            conflict = set(core) | {f for x in core for f in self.b.mf[x] if f in members}
            literals = sorted(x for x in conflict if x not in picks and x <= self.half)
            # a sold hub listed by the core could be bought back: unselling is barring the sale
            listed_sold = sorted({f for x in core for f in self.b.mf[x] if f in sold})
            literals += [("sell", h) for h in listed_sold if ("sell", h) not in picks]
            for i, x in enumerate(literals):
                heapq.heappush(heap, (-value, next(counter), picks | frozenset(literals[:i]), bars | {x}, None))
        return {"value": -min(heap)[0] if heap else None, "finished": False, "evaluated": evaluated,
                "seconds": round(time.time() - t0, 1)}

    # ---- the fiber side --------------------------------------------------------------------------------------
    def fiber_bound(self, mu=None, usable=(), picks=(), bars=()):
        """F(usable) if mu is None (hubs outside `usable` deleted), else F'_mu (every hub usable, giving one up earns
        mu[h]).  Returns (value, given_up, chosen)."""
        elems = {x: e for x, e in self.fiber_elems.items() if x not in bars}
        if mu is None:
            deleted = [h for h in self.hubs if h not in set(usable)]
        else:
            deleted = []
            for h in self.hubs:
                elems[("free", h)] = self.unit(h) + (mu.get(h, 0),)
        base = self.base_vectors(self.fiber_sources, deleted)
        chosen, value = max_weight_common(elems, base[0], base[1], picks)
        given_up = sorted(x[1] for x in chosen if isinstance(x, tuple))
        return value, given_up, [x for x in chosen if not isinstance(x, tuple)]

    def lagrangian(self, mu, budget=600.0):
        e = self.smooth_exact(mu=mu, budget=budget)
        if not e["finished"]:
            return None
        f, given_up, _ = self.fiber_bound(mu=mu)
        total = sum(self.smooth_sources) + sum(self.fiber_sources) + e["value"] + f - sum(mu.values())
        return {"bound": total, "sold": e["sold"], "given_up": given_up, "E_nodes": e["evaluated"],
                "E_value": e["value"], "F_value": f}


def smooth_enumerate(sp, margin, deleted=(), budget=1200.0):
    """All playable smooth configurations (sets of promoted smooth candidates) of weight >= E(deleted) - margin, by
    best-first branch and bound that also splits feasible leaves (k-best enumeration).  Returns (E, list of (weight,
    frozenset)), the list possibly truncated if the budget runs out (then truncated=True)."""
    elems = dict(sp.smooth_elems)
    deleted = set(deleted)
    base = sp.base_vectors(sp.smooth_sources, deleted)
    t0 = time.time()
    counter = itertools.count()
    heap = [(0, next(counter), frozenset(), frozenset(deleted))]
    found = {}
    best = None
    evaluated = 0
    truncated = False
    while heap:
        if time.time() - t0 > budget:
            truncated = True
            break
        prio, _, picks, bars = heapq.heappop(heap)
        if best is not None and -prio < best - margin:
            break
        sub = {x: e for x, e in elems.items() if x not in bars}
        try:
            chosen, value = max_weight_common(sub, base[0], base[1], picks)
        except ValueError:
            continue
        evaluated += 1
        if best is not None and value < best - margin:
            continue
        ok, k, lists = sp.smooth_playable(chosen, deleted)
        members = set(sp.smooth_sources) | set(chosen)
        if ok:
            if best is None:
                best = value
            found[frozenset(chosen)] = value
            literals = sorted(x for x in chosen if x not in picks)  # split off this set: next-best enumeration
        else:
            core = minimal_core(lists, set(lists), sorted(lists, reverse=True))
            conflict = set(core) | {f for x in core for f in sp.b.mf[x] if f in members}
            literals = sorted(x for x in conflict if x not in picks and x <= sp.half)
        for i, x in enumerate(literals):
            heapq.heappush(heap, (-value, next(counter), picks | frozenset(literals[:i]), bars | {x}))
    return best, sorted(((v, s) for s, v in found.items()), reverse=True), evaluated, truncated
