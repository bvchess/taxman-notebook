#!/usr/bin/env python3
"""The circuit of v(n) across every odd exchange of layer 3 (searched or repeat), boards to 8191: is it the box
{p', p} x {q', q} x {r', r} less n, with x = p'q'r' its smallest member?

    nice -n 19 python3 -I study/boxes.py > study/boxes_out.txt
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import common  # noqa: E402
import exch  # noqa: E402

spf = exch.spf
TOP = 8191


def prev_prime(p):
    p -= 1
    while p > 1 and spf[p] != p:
        p -= 1
    return p


def box_of(n):
    ps = common.factor(n)
    ps1 = [prev_prime(p) for p in ps]
    out = set()
    for mask in range(8):
        out.add((ps1[0] if mask & 1 else ps[0]) * (ps1[1] if mask & 2 else ps[1]) * (ps1[2] if mask & 4 else ps[2]))
    return out


def main():
    rows = {int(r["n"]): r for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "settle.csv")))}
    rows5 = {int(r["n"]): r for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "past5060.csv")))}
    arr = exch.arrival()
    u = {2}
    stats = {}
    for n in range(3, TOP + 1):
        row = arr[n]
        u_prev = set(u)
        u = (u | set(row["added"])) - set(row["dropped"])
        if n % 2 == 0 or exch.omega(n) != 3 or row["added"] != [n] or len(row["dropped"]) != 1:
            continue
        x = row["dropped"][0]
        kind = rows[n]["outcome"] if n in rows else rows5[n]["kind"]
        A = exch.layer_part(u_prev, 3)
        circ = exch.gf2_circuit(A, n)
        box = box_of(n)
        p = min(common.factor(n))
        ok_box = circ is not None and set(circ) | {n} == box
        in_u = box - {n} <= u_prev
        key = (kind, p == 3, ok_box, in_u)
        stats[key] = stats.get(key, 0) + 1
        if not ok_box or not in_u or p != 3:
            print(f"{n} = {exch.fac_str(n)} ({kind}): x = {x} = {exch.fac_str(x)}, p = {p}, circuit = box? {ok_box}, "
                  f"box - n in U*(n-1)? {in_u}; circuit {None if circ is None else [(c, exch.fac_str(c)) for c in circ]}; "
                  f"box {sorted(box)}, min box = x? {min(box) == x}")
    print("\n(kind, p == 3, circuit == box - n, box - n in U*(n-1)): count")
    for k in sorted(stats):
        print(f"  {k}: {stats[k]}")


if __name__ == "__main__":
    main()
