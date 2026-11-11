#!/usr/bin/env python3
"""Referee's check of the closed case G2-ii of Theorem 12P (the version of 2026-11-10, second draft).

    nice -n 19 python3 -I referee_check_g2ii.py [SAMPLES]

Random playable layer-4 instances of board n holding 12P, 8P, 8P1, 12P1, 8t', with a random set M3 of layer-3
moves holding 6P and not 4P, 4P1, 6P1 (the G2 shape), biased so that 12 is sometimes a move.  Where no scheme pays
12P with 12 (G2) and no scheme pays 12P1 with 12 (G2-ii), the layer-4 instance of T + 6P1 on board n - 1 with the
new scheme (8P -> 4P, 8P1 -> 8, 12P1 -> 4P1) is tested by its residual; the three sub-shapes are counted: 12 paid by
some member, 12 a move, 12 unpaid.  Uses the helpers of referee_check.py.
"""
import random
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/succession/check-12p")
from referee_check import mf, omega, prev_prime, residual_lists, sieve  # noqa: E402


def main(samples, seed=7):
    rng = random.Random(seed)
    spf = sieve(5100)
    totals = {}
    fails = 0
    for n in (276, 444, 996, 1668, 2004, 4308):
        P = n // 12
        P1 = prev_prime(P, spf)
        half = n // 2
        l4 = [x for x in range(2, n + 1) if omega(x, spf) == 4]
        l3 = [x for x in range(2, half + 1) if omega(x, spf) == 3]
        tcands = [t for t in range(2, 3 * P // 2 + 1) if spf[t] == t and 3 * t > 4 * P]
        twelves = [x for x in l4 if x % 12 == 0 and x != 12 * P and x != 12 * P1]
        for _ in range(samples):
            t1 = rng.choice(tcands)
            key = {12 * P, 8 * P, 8 * P1, 12 * P1, 8 * t1}
            M3 = {x for x in l3 if rng.random() < 0.12 and x not in (4 * P1, 6 * P1, 4 * t1, 8, 12, 4 * P)}
            M3.add(6 * P)
            if rng.random() < 0.3:
                M3.add(12)
            # make 12 contested: some 12t with 6t or 4t a move must pay 12
            for e in rng.sample(twelves, min(4, len(twelves))):
                if rng.random() < 0.6:
                    for f in mf(e, spf):
                        if f != 12 and f <= half and f not in (4 * P1, 6 * P1, 4 * t1, 8, 4 * P):
                            M3.add(f)
            pool = {x for x in l3 if x not in M3}
            mem = set(key) | {x for x in l4 if x > half and rng.random() < 0.7} | {x for x in l4 if x <= half and rng.random() < 0.15}
            L = {x: mf(x, spf) & pool for x in mem}
            ok = True
            while True:
                R = residual_lists(L)
                if not R:
                    break
                choices = [x for x in R if x not in key]
                if not choices:
                    ok = False
                    break
                del L[rng.choice(choices)]
            if not ok:
                totals["unusable"] = totals.get("unusable", 0) + 1
                continue
            S4 = set(L)

            def can(**fix):
                LL = {x: set(v) for x, v in L.items()}
                for x, f in fix.items():
                    LL[int(x)] = {f} if f in LL[int(x)] else set()
                return not residual_lists(LL)

            if can(**{str(12 * P): 12}):
                totals["B1"] = totals.get("B1", 0) + 1
                continue
            if can(**{str(12 * P): 4 * P, str(12 * P1): 12}):
                totals["G2-i"] = totals.get("G2-i", 0) + 1
                continue
            # G2-ii.  Shape of 12: a move, or paid by some member in some scheme, or unpaid in every scheme.
            if 12 in M3:
                shape = "12 a move"
            elif any(can(**{str(e): 12}) for e in S4 if 12 in L[e]):
                shape = "12 paid by some 12t0"
            else:
                shape = "12 unpaid"
            pool2 = pool - {6 * P1, 6 * P}
            inst = {x: mf(x, spf) & pool2 for x in S4 - {12 * P}}
            # the proof's scheme, forced: 8P -> 4P, 8P1 -> 8, 12P1 -> 4P1
            forced = {x: set(v) for x, v in inst.items()}
            forced[8 * P] = {4 * P} & inst[8 * P]
            forced[8 * P1] = {8} & inst[8 * P1]
            forced[12 * P1] = {4 * P1} & inst[12 * P1]
            good_any = not residual_lists(inst)
            good_forced = not residual_lists(forced)
            k = "G2-ii: " + shape
            totals[k] = totals.get(k, 0) + 1
            if not good_forced or not good_any:
                fails += 1
                print(f"  FAIL n {n} t' {t1} {k}: playable {good_any}, with the proof's scheme {good_forced}; members {sorted(S4)}; M3 {sorted(M3)}")
    print(f"F. G2-ii closed: samples {totals}; failures {fails}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
