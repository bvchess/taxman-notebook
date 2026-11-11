#!/usr/bin/env python3
"""X*, the hubs paid by fiber rows in a peel of the optimal set S*, for experiment 1 of study-report-2.md (Section 4).

The peel is study-2/exp_d.py's own (hubs_paid_in_peel), so X* is the one the Python study used.  The same peel with the
members and columns scanned in ascending and in descending order gives two more X*, to show how much X* depends on the
peel.  Each X* is cut down to the hubs (smooth cofactors x / p of the fiber rows x, p their largest prime): exp_d's
also records a fiber row x with p^2 | x paying x / p, which is not a hub and changes neither E nor F.

Usage: python3 -I xstar.py N [N ...] > xstar.jsonl
"""

import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
import parity as P  # noqa: E402
from exp_d import hubs_paid_in_peel  # noqa: E402
from lib import largest_prime  # noqa: E402
from split import SMOOTH  # noqa: E402


class LightBoard:
    """What hubs_paid_in_peel reads of a board: each number's layer, maximal factors and largest prime."""

    def __init__(self, n):
        self.n = n
        self.om, self.mf = P.omega_and_mf(n)
        self.lp = [0] * (n + 1)
        for x in range(2, n + 1):
            self.lp[x] = largest_prime(x)


def sorted_peel(board, members, reverse):
    """hubs_paid_in_peel with every scan in sorted order: the first front move, else the first back move."""
    mem = set(members)
    paid = set()
    for k in sorted({board.om[x] for x in members}):
        lists = {x: set(f for f in board.mf[x] if f not in mem) for x in members if board.om[x] == k}
        alive = set(lists)
        live = set().union(*lists.values()) if lists else set()
        while alive:
            pair = None
            for x in sorted(alive, reverse=reverse):
                cols = [f for f in lists[x] if f in live]
                if len(cols) == 1:
                    pair = (x, cols[0])
                    break
            if pair is None:
                for f in sorted(live, reverse=reverse):
                    listers = [x for x in alive if f in lists[x]]
                    if len(listers) == 1:
                        pair = (listers[0], f)
                        break
            assert pair is not None, f"layer {k} did not peel"
            x, f = pair
            alive.discard(x)
            live.discard(f)
            if board.lp[x] > SMOOTH and f == x // board.lp[x]:
                paid.add(f)
    return paid


def hubs(board, sources, n):
    """The smooth cofactors x / p of the fiber sources and the fiber candidates (layer >= 3, up to n / 2)."""
    out = set()
    fiber = [s for s in sources if board.lp[s] > SMOOTH]
    fiber += [x for x in range(2, n // 2 + 1) if board.lp[x] > SMOOTH and board.om[x] >= 3]
    for x in fiber:
        h = x // board.lp[x]
        if h <= n // 2 and (h == 1 or board.lp[h] <= SMOOTH):
            out.add(h)
    return out


def main():
    for n in map(int, sys.argv[1:]):
        b = LightBoard(n)
        line = P.results_line(n)
        s = set(line["moves"])
        hub_set = hubs(b, [x for x in s if x > n // 2], n)
        raw = hubs_paid_in_peel(b, s)
        out = {"n": n, "xstar": sorted(raw & hub_set), "not_hubs": sorted(raw - hub_set)}
        for name, rev in (("asc", False), ("desc", True)):
            out["xstar_" + name] = sorted(sorted_peel(b, line["moves"], rev) & hub_set)
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
