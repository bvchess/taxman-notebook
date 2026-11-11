#!/usr/bin/env python3
"""Experiment A: where does the gap live, smooth or fiber?

For each board n: H (parity's heaviest set), S* (the optimum), the e1 leaf H_s (heaviest under the smooth condition).
1. Classify the residual members of H and H_s per layer: smooth (all primes <= 23), fiber (a live internal column),
   plug (a fiber member whose only live column is its hub, or none).
2. Parity bound with the smooth candidates fixed to S*'s choice (fibers free): the "smooth-fixed" bound.
3. Parity bound with the fiber candidates fixed to S*'s choice (smooth free): the "fiber-fixed" bound.
Usage: python3 -I exp_a.py N [N ...]
"""

import json
import sys
import time

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board, residual, classify, load_e1_leaf  # noqa: E402


def residual_report(board, members, label):
    out = {}
    for k in sorted({board.om[x] for x in members}):
        lists = board.layer_instance(members, k)
        res = residual(lists)
        if not res:
            continue
        kinds = {}
        for x in res:
            c = classify(board, lists, x)
            kinds[c] = kinds.get(c, 0) + 1
        pool = set().union(*(lists[x] for x in res))
        # smooth sub-instance of the residual: smooth rows over smooth columns, with plug hubs removed
        plug_hubs = {f for x in res if classify(board, lists, x) == "plug" for f in lists[x]}
        smooth_rows = [x for x in lists if board.smooth(x)]
        sm_lists = {x: set(f for f in lists[x]) for x in smooth_rows}
        sm_res_all = residual(sm_lists)
        sm_lists2 = {x: set(f for f in lists[x] if f not in plug_hubs) for x in smooth_rows}
        sm_res_minus = residual(sm_lists2)
        out[k] = {"residual": len(res), "pool": len(pool), "kinds": kinds, "plug_hubs": len(plug_hubs),
                  "smooth_alone_residual": len(sm_res_all), "smooth_minus_plughubs_residual": len(sm_res_minus)}
    print(label, json.dumps(out), flush=True)
    return out


def main():
    for arg in sys.argv[1:]:
        n = int(arg)
        t0 = time.time()
        b = Board(n)
        low, pb = b.heaviest()
        h = set(b.g) | set(low)
        line = b.opt_line()
        s = set(line["moves"])
        opt = line["score"]
        assert set(x for x in s if x > n // 2) == b.gset, "sources differ"
        print(f"n={n} PB={pb} opt={opt} gap={pb - opt} promotions H={len(low)} S*={len([x for x in s if x <= n // 2])}"
              f" ({time.time() - t0:.1f}s)", flush=True)
        residual_report(b, h, f"n={n} H residual:")
        leaf = load_e1_leaf(n)
        if leaf:
            hs = set(b.g) | set(leaf["leaf_promotions"])
            print(f"n={n} e1 leaf: PB_s={sum(hs)} (file {leaf['PB_s']}) gap_s={sum(hs) - opt}", flush=True)
            residual_report(b, hs, f"n={n} H_s residual:")
        half = n // 2
        s_low = {x for x in s if x <= half}
        smooth_all = {x for x in range(2, half + 1) if b.smooth(x)}
        fiber_all = {x for x in range(2, half + 1) if not b.smooth(x)}
        t0 = time.time()
        low2, pb2 = b.heaviest(picks=s_low & smooth_all, bars=smooth_all - s_low)
        print(f"n={n} smooth-fixed bound={pb2} gap={pb2 - opt} ({time.time() - t0:.1f}s)", flush=True)
        t0 = time.time()
        low3, pb3 = b.heaviest(picks=s_low & fiber_all, bars=fiber_all - s_low)
        print(f"n={n} fiber-fixed bound={pb3} gap={pb3 - opt} ({time.time() - t0:.1f}s)", flush=True)
        if pb2 > opt:
            residual_report(b, set(b.g) | set(low2), f"n={n} smooth-fixed residual:")
        if pb3 > opt:
            residual_report(b, set(b.g) | set(low3), f"n={n} fiber-fixed residual:")


if __name__ == "__main__":
    main()
