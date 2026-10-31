"""Part 3 of J3 on the prover's enumeration of every optimal set to 989: the exchange maps the sets of n onto those of n - 1."""
from tx import omega, playable
from data import results, optsets
from t8 import u2, cycle_min
res = results(); os_ = optsets(res)
ok = bad = skipped = 0
for n in range(9, 990, 2):
    if omega(n) != 2:
        continue
    x = cycle_min(u2(n - 1), n)
    if x is None:
        continue
    if n not in os_ or n - 1 not in os_:
        skipped += 1; continue
    A = {frozenset(s) for s in os_[n]}
    B = {frozenset(s) for s in os_[n - 1]}
    mapped = {frozenset((s - {n}) | {x}) for s in A}
    if all(n in s and x not in s for s in A) and all(x in t for t in B) and mapped == B:
        ok += 1
    else:
        bad += 1; print('MISMATCH', n, len(A), len(B))
print('bijection holds', ok, 'fails', bad, 'skipped (n or n-1 not enumerated)', skipped)
