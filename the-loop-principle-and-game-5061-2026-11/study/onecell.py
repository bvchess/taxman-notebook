#!/usr/bin/env python3
"""At the 21P regime-(ii) exceptions: is the rise the value of one cell of a hub row, and is the recorded set plus
that cell independent at both parities (the parity bound could hold it) yet unplayable (a core)?  GF(2) check with
bitsets; peel and residual from common.py.
    nice -n 19 python3 -I study/onecell.py"""
import sys
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import predict  # noqa: E402
common, spf, MF = predict.common, predict.spf, predict.MF
res = common.results()
best = predict.load_best()


def omega(x):
    return len(common.factor(x))


def parity_vectors(S, n):
    """The parity-0 and parity-1 vectors of the members of S on board n, as bit masks; an extra coordinate is a
    bit above n/2 + 1, unique per member."""
    half = n // 2
    vec = {0: [], 1: []}
    extra = half + 2
    for s in S:
        om = omega(s) % 2
        v = 0
        for f in MF[s]:
            v |= 1 << f
        for i in (0, 1):
            if om != i:
                vec[i].append(v)
            elif s <= half:
                vec[i].append(1 << s)
            else:
                vec[i].append(1 << extra)
                extra += 1
    return vec


def independent(vectors):
    basis = {}  # pivot bit -> vector
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
        else:
            return False
    return True


def both(S, n):
    vec = parity_vectors(S, n)
    return independent(vec[0]) and independent(vec[1])


cases = [(3297, 236, "4·59"), (3507, 215, "5·43 (layer 2)"), (5061, 492, "12·41"), (5943, 496, "16·31"),
         (6153, 568, "8·71"), (6573, 764, "4·191"), (6657, 764, "4·191")]
for n, cell, name in cases:
    S = set(res[n]["moves"]) if n <= 5060 else set(best[n]["moves"])
    print(f"== {n}: rise {cell} = {name}; cell in the set already: {cell in S}; set independent at both parities: {both(S, n)}")
    T = S | {cell}
    ok = common.playable(T, n, spf)
    R = common.residual(T, spf)
    print(f"   set + {cell}: independent at both parities {both(T, n)}, playable {ok}, residual size {len(R)}, "
          f"residual {sorted(R)[:30]}{' ...' if len(R) > 30 else ''}")
    # the members of the residual that list the cell's hub, and the hub's holder
    hub = cell // common.factor(cell)[-1]
    listers = sorted(x for x in R if hub in MF[x])
    print(f"   hub {hub}: residual members listing it {listers}")
