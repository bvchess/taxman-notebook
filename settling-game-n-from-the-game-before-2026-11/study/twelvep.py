#!/usr/bin/env python3
"""The configuration of the optimal sets at every searched 12P game (P prime) of 2..5060: who pays 12, 8, 6P1, 4P1,
whether 6P1, 4P1, 4t' are moves (t' the largest prime with 8t' <= n), the law.
    nice -n 19 python3 -I study/twelvep.py > study/twelvep_all_out.txt"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import prev_prime  # noqa: E402
from edges import payments  # noqa: E402
spf = exch.spf

def payer(pay, f):
    return [m for m, g in pay.items() if g == f]

def main():
    res = exch.results()
    rows = [r for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "searched.csv")))
            if int(r["cofactor"]) == 12 and r["step"] == "relax"]
    counts = {}
    for r in rows:
        n = int(r["n"]); P = n // 12
        if spf[P] != P or n < 200: continue
        P1 = prev_prime(P)
        t1 = max(t for t in range(2, n // 8 + 1) if spf[t] == t)
        S0, S1 = set(res[n-1]["moves"]), set(res[n]["moves"])
        delta = res[n-1]["score"] + n - res[n]["score"]
        pay0, pay1 = payments(S0, n-1), payments(S1, n)
        conf = dict(law=(delta == 6*P1),
                    twelveP_pays=pay1.get(12*P), twelveP1_pays_n=pay1.get(12*P1), twelveP1_pays_prev=pay0.get(12*P1),
                    eightP1_pays_n=pay1.get(8*P1), eight_payer_n=payer(pay1, 8), eight_payer_prev=payer(pay0, 8),
                    sixP1_in_prev=6*P1 in S0, sixP1_in_n=6*P1 in S1, fourP1_in_n=4*P1 in S1, fourP1_in_prev=4*P1 in S0,
                    sixP_in_n=6*P in S1, fourtp_in_prev=4*t1 in S0, fourtp_in_n=4*t1 in S1, eightP_pays_n=pay1.get(8*P),
                    moves_lost=sorted(S0 - S1), moves_gained=sorted(S1 - S0))
        key = (conf["law"], conf["twelveP_pays"] == 12, conf["twelveP1_pays_n"] == 6*P1, conf["eightP1_pays_n"] == 4*P1,
               conf["sixP_in_n"], conf["fourtp_in_n"], tuple(conf["eight_payer_n"]) == (8*t1,))
        counts[key] = counts.get(key, 0) + 1
        print(n, f"12*{P}", f"P1={P1}", f"t'={t1}", f"delta={delta}", conf)
    print("\n(law, 12P pays 12, 12P1 pays 6P1, 8P1 pays 4P1, 6P in S(n), 4t' in S(n), 8 paid to 8t'): count")
    for k in sorted(counts): print(" ", k, counts[k])

main()
