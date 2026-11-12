#!/usr/bin/env python3
"""Hub holders: in a payment scheme of the recorded optimal set of n - 1 and of n (peel's scheme, common.legal_order),
which member pays with each hub k <= c, written as a cell (k, j) when it is one.  For the chain's games of chosen
cofactors from 1000 on, clean to depth >= 1.
    nice -n 19 python3 -I study/hubs.py C [C ...]"""
import sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import predict, patterns  # noqa: E402
common, spf = predict.common, predict.spf


def scheme(S, n):
    members = set(S)
    lists = {x: predict.MF[x] - members for x in members}
    pay = {}
    live_m, live_f = set(members), set().union(*lists.values())
    listers = {}
    for x, fs in lists.items():
        for f in fs:
            listers.setdefault(f, set()).add(x)
    stack_m = [x for x in members if len(lists[x]) <= 1]
    stack_f = [f for f in live_f if len(listers[f]) == 1]
    def take(x, f):
        pay[x] = f
        live_m.discard(x); live_f.discard(f)
        for g in lists[x]:
            if g in live_f:
                listers[g].discard(x)
                if len(listers[g]) == 1:
                    stack_f.append(g)
        for y in listers.get(f, ()):
            if y in live_m:
                lists[y].discard(f)
                if len(lists[y]) <= 1:
                    stack_m.append(y)
    while live_m:
        moved = False
        while stack_m and not moved:
            x = stack_m.pop()
            if x in live_m:
                fs = [g for g in lists[x] if g in live_f]
                if len(fs) == 1:
                    take(x, fs[0]); moved = True
        while stack_f and not moved:
            f = stack_f.pop()
            if f in live_f:
                ys = [y for y in listers[f] if y in live_m]
                if len(ys) == 1:
                    take(ys[0], f); moved = True
                elif not ys:
                    live_f.discard(f)
        if not moved:
            return None
    return pay


def cell(w, pj):
    lab = patterns.label(w, pj)
    return f"({lab[0]},{lab[1]})" if lab else str(w)


rows = predict.load_rows()
res = common.results()
for c in map(int, sys.argv[1:]):
    hubs = [k for k in range(2, c + 1) if c % k == 0 or k in (4, 6, 8, 9, 10, 12, 16, 18, 20, 24, 36)]
    hubs = sorted(set(hubs) & set(range(2, c + 1)))
    print(f"== cofactor {c}: hubs {hubs}; holder in game n-1 -> holder in game n (cells (k,j)); '-' = hub is a move or unpaid")
    for r in rows:
        n = r["n"]
        if r["cofactor"] != c or r["range"] != "chain" or n < 1000:
            continue
        d = patterns.clean_depth(n)
        if d < 1:
            continue
        P = r["P"]
        pj = patterns.primes_around(P)
        out = []
        for m in (n - 1, n):
            S = set(res[m]["moves"])
            pay = scheme(S, m)
            if pay is None:
                out.append("peel failed")
                continue
            holder = {}
            for x, f in pay.items():
                if f in hubs:
                    holder[f] = cell(x, pj)
            out.append(" ".join(f"{k}:{holder.get(k, '-' if k in S else '.')}" for k in hubs))
        print(f"  {n} depth {d} delta {r['delta']} pb {r['delta_pb']} | n-1: {out[0]} | n: {out[1]}")
