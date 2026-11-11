#!/usr/bin/env python3
"""Is H's layer instance restricted to fiber members (largest prime > T) playable?  And the lightest promotion."""
import json, math, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P

def largest_prime(x):
    p, big = 2, 1
    while p * p <= x:
        while x % p == 0:
            big = p; x //= p
        p += 1
    return max(big, x) if x > 1 else big

def peel_residual(members, lists):
    alive = set(members)
    while True:
        count = {}
        for x in alive:
            for f in lists[x]:
                count[f] = count.get(f, 0) + 1
        drop = [x for x in alive if any(count[f] == 1 for f in lists[x])]
        if not drop:
            return alive
        alive -= set(drop)

for n in map(int, sys.argv[1:]):
    om, mf = P.omega_and_mf(n)
    d = P.board(n)
    h = set(d["greedy_basis"] + d["heaviest_low"])
    T = math.isqrt(n // 8)
    low = sorted(x for x in h if x <= n // 2)
    out = {"n": n, "gap": d.get("gap"), "T": T, "lightest_promotion_H": low[0], "lightest_opt": None}
    line = P.results_line(n)
    if line:
        out["lightest_opt"] = min(x for x in line["moves"] if x <= n // 2)
    for k in sorted({om[x] for x in h}):
        layer = [x for x in h if om[x] == k]
        lists = {x: set(f for f in mf[x] if f not in h) for x in layer}
        full = peel_residual(layer, lists)
        if not full:
            continue
        for thr_name, thr in (("T", T), ("23", 23)):
            fib = [x for x in layer if largest_prime(x) > thr]
            r = peel_residual(fib, lists)
            out[f"L{k}_residual_full"] = len(full)
            out[f"L{k}_fiber_only_gt{thr_name}"] = {"members": len(fib), "residual": len(r)}
            sm = [x for x in layer if largest_prime(x) <= thr]
            r2 = peel_residual(sm, lists)
            out[f"L{k}_smooth_only_le{thr_name}"] = {"members": len(sm), "residual": len(r2)}
    print(json.dumps(out), flush=True)
