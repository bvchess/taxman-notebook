#!/usr/bin/env python3
"""Game 5061: probes on the proven set of 5060 and the best-known set of 5061 (peel and residual), the far columns
of 151, 157, 163 at 5018, 5019, 5060, 5061, and the loss at every regime-(ii) 21P game when hub 18 leaves column 0.
    nice -n 19 python3 -I study/g5061.py"""
import sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops/study")
import predict, patterns, hubs  # noqa: E402
common, spf = predict.common, predict.spf
res = common.results()
best = predict.load_best()
S60 = set(res[5060]["moves"]); opt60 = res[5060]["score"]
B61 = set(best[5061]["moves"]); bk61 = best[5061]["score"]
print("opt(5060) =", opt60, " best-known(5061) =", bk61, " sum check:", sum(S60) == opt60, sum(B61) == bk61)
P, P1 = 241, 239
def probe(name, T, n):
    ok = common.playable(T, n, spf)
    R = common.residual(T, spf)
    print(f"  {name}: sum {sum(T)} ({sum(T) - bk61:+d} vs best-known), playable {ok}, residual {sorted(R)[:40]}{' ...' if len(R) > 40 else ''} ({len(R)})")
print("== probes on board 5061")
probe("S*(5060) - 6P + 5061", (S60 - {6 * P}) | {5061}, 5061)
probe("S*(5060) - 6P + 5061 + 942 (6·157)", (S60 - {6 * P}) | {5061, 942}, 5061)
probe("S*(5060) - 6P + 5061 + 1434 (6P1)", (S60 - {6 * P}) | {5061, 1434}, 5061)
probe("S*(5060) - 6P + 5061 + 942 + 250", (S60 - {6 * P}) | {5061, 942, 250}, 5061)
probe("best-known(5061) itself", B61, 5061)
probe("best-known(5061) + 242", B61 | {242}, 5061)
probe("best-known(5061) - 942 + 1434", (B61 - {942}) | {1434}, 5061)
print("== change 5060 -> best-known 5061: D", sorted(S60 - B61), "A", sorted(B61 - S60))
print("== far columns (rows 1..34) in the recorded sets; '*' = a move")
for t in (151, 157, 163):
    print(f"  column of {t}:")
    for m, S in ((5018, set(res[5018]["moves"])), (5019, set(res[5019]["moves"])), (5060, S60), (5061, B61)):
        pay = hubs.scheme(S, m)
        cells = []
        for k in range(2, 35):
            w = k * t
            if w > m:
                break
            if w in S:
                f = pay[w]
                cells.append(f"{k}*->{'h' + str(f) if f < 100 else f'{f // t}' if f % t == 0 else str(f)}")
        print(f"    {m}: " + " ".join(cells))
print("== regime (ii) games: holder of hub 18 at n, the cell it fell back on, and the loss 6P - delta (the recovery)")
rows = [r for r in predict.load_rows() if r["cofactor"] == 21 and r["n"] >= 2000 and 6 * r["P"] in r["dropped"]]
for r in rows:
    n, Pn = r["n"], r["P"]
    pj = patterns.primes_around(Pn)
    Sn = set(res[n]["moves"]) if n <= 5060 else set(best[n]["moves"])
    Sm = set(res[n - 1]["moves"]) if n - 1 <= 5060 else set(best[n - 1]["moves"])
    pay = hubs.scheme(Sn, n)
    h = [x for x, f in pay.items() if f == 18]
    hold = h[0] if h else None
    t = hold // 18 if hold else None
    paym = hubs.scheme(Sm, n - 1)
    before = f"{hold}->{paym.get(hold)}" if hold and hold in Sm else "not a move at n-1"
    print(f"  {n}: delta {r['delta']} pb {r['delta_pb']} | hub 18 at n: {hold} = 18·{t} ({hubs.cell(hold, pj) if hold else '-'}), at n-1 it paid {before} | "
          f"recovery 6P - delta = {6 * Pn - r['delta']}; 6t = {6 * t if t else '-'}, 9t = {9 * t if t else '-'}; "
          f"D {sorted(r['dropped'])} A {sorted(r['added'])}")
