#!/usr/bin/env python3
"""Size the gluing-lemma enumeration for 5061 over E10's region: the region's cells, which sources the proven set of
5060 holds, the candidate cells, and the fraction of candidate subsets whose state (sources + 5061 + subset) is
coreless in the region's own instance, by sampling (uniform, and biased to the density of the recorded sets).
    nice -n 19 python3 -I study/size5061.py"""
import random, sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import predict  # noqa: E402
common, spf = predict.common, predict.spf
res = common.results(); best = predict.load_best()
S60 = set(res[5060]["moves"]); B61 = set(best[5061]["moves"])
n = 5061
regions = {"E10": [149, 151, 157, 163, 241, 251, 421, 631], "study": [151, 157, 163, 241, 251],
           "chain": [241, 251, 157]}
def cells(primes):
    out = []
    for p in primes:
        for k in range(4, n // p + 1):
            if spf[k] != k:  # composite row
                out.append((k, p))
    return out
for name, primes in regions.items():
    C = cells(primes)
    src = [k * p for k, p in C if k * p > n // 2]
    cand = [k * p for k, p in C if k * p <= n // 2]
    src_in = [x for x in src if x in S60]; src_out = [x for x in src if x not in S60]
    cand60 = [x for x in cand if x in S60]; cand61 = [x for x in cand if x in B61]
    print(f"== region {name}: {len(C)} cells, {len(src)} sources ({len(src_in)} in S*(5060), out: {src_out}), "
          f"{len(cand)} candidates ({len(cand60)} in S*(5060), {len(cand61)} in best-known 5061)")
    fixed = set(src_in) | {n}
    random.seed(1)
    for label, prob in (("uniform", 0.5), ("density of the recorded sets", len(cand60) / len(cand)), ("sparse", 0.15)):
        trials, ok = 4000, 0
        for _ in range(trials):
            W = fixed | {x for x in cand if random.random() < prob}
            if not common.residual(W, spf):
                ok += 1
        est = ok / trials
        print(f"   p = {prob:.2f} ({label}): coreless {ok}/{trials} = {est:.4f}; uniform-count estimate 2^{len(cand)} x fraction = "
              f"{est * 2 ** len(cand):.3g}" if label == "uniform" else
              f"   p = {prob:.2f} ({label}): coreless {ok}/{trials} = {est:.4f}")
    # is the recorded state coreless?  (it must be)
    for lab, S in (("5060's set + 5061", S60 | {n}), ("best-known 5061", B61)):
        W = {x for x in S if x in set(k * p for k, p in C)} | ({n} if n in S else set())
        print(f"   recorded state {lab}: {len(W)} cells, coreless {not common.residual(W, spf)}")
