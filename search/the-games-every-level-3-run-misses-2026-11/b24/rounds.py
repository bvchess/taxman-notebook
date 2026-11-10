#!/usr/bin/env python3
"""B24's rounds (2026-11-09): does a variant's change cut the rounds a game gets at level 3's budget?  For each game
and seed played by both V0 and the variant (V3 by default), the rounds of each play (seeded, and unseeded for a game
played twice) and their work per round; for each play that reached opt(n), which play reached it, in which round and
at which stage of the ladder; and the pairs that one build reached and the other did not.

    python3 -I rounds.py [VARIANT]
"""

import gzip
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
REC = [3192, 3311, 3332, 3384, 3549, 3565, 3723, 3844, 3968, 4107, 4134, 4225, 5060]
CTL = [3213, 3321, 3328, 3392, 3553, 3542, 3735, 3828, 3944, 4100, 4130, 4224, 5054]
SEEDS = range(31, 37)


def line(variant, n, seed):
    path = os.path.join(HERE, "plays", variant, f"g{n}-s{seed}.jsonl")
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    with open(path) as f:
        return [json.loads(t) for t in f if t.strip()][-1]


def plays_of(x):
    """The seeded and the unseeded play of a line: (rounds, work) each, None for an unseeded play not made."""
    other = x["other"]
    mine = (x["rounds"], x["work"])
    theirs = (other["rounds"], other["work"]) if other else None
    return (theirs, mine) if x["unseeded"] else (mine, theirs)


def reach(x, opt):
    """Which play reached opt(n), in which round (0 for the start) and at which stage, or None."""
    if x["score"] < opt:
        return None
    play = "unseeded" if x["unseeded"] else "seeded"
    if x["start"] is not None and x["start"] >= opt:
        return (play, 0, 0)
    first = next(i for i in x["improvements"] if i["score"] >= opt)
    return (play, first["round"], first["stage"])


def said(r):
    if r is None:
        return None
    return f"{r[0]}, start" if r[1] == 0 else f"{r[0]}, round {r[1]} stage {r[2]}"


def cell(p):
    return f"{p[0]:>3} {p[1] / p[0] / 1000:>5.1f}k" if p else "    -     "


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "v3"
    b_ = variant.upper()
    opt = {x["n"]: x["score"] for x in map(json.loads, gzip.open(RES, "rt"))}
    print(f"game seed | V0 seeded rounds, work/round | {b_} seeded | V0 unseeded | {b_} unseeded | V0 reached | "
          f"{b_} reached")
    summary, discordant = {}, []
    for role, games in (("rec", REC), ("ctl", CTL)):
        pairs = []
        for n in games:
            for seed in SEEDS:
                a, b = line("v0", n, seed), line(variant, n, seed)
                if a is None or b is None:
                    continue
                pa, pb = plays_of(a), plays_of(b)
                pairs.append((n, seed, pa, pb))
                ra, rb = reach(a, opt[n]), reach(b, opt[n])
                print(f"{n} {seed} | {cell(pa[0])} | {cell(pb[0])} | {cell(pa[1])} | {cell(pb[1])} | "
                      f"{said(ra) or opt[n] - a['score']} | {said(rb) or opt[n] - b['score']}")
                if (ra is None) != (rb is None):
                    discordant.append((n, seed, pa, pb, ra, rb))
        summary[role] = pairs
    print()
    print(f"seeded plays, {b_} against V0 on the same game and seed")
    for role, pairs in summary.items():
        r0 = [pa[0][0] for _, _, pa, _ in pairs]
        r1 = [pb[0][0] for _, _, _, pb in pairs]
        w0 = [pa[0][1] / pa[0][0] for _, _, pa, _ in pairs]
        w1 = [pb[0][1] / pb[0][0] for _, _, _, pb in pairs]
        fewer = sum(b < a for a, b in zip(r0, r1))
        same = sum(b == a for a, b in zip(r0, r1))
        more = sum(b > a for a, b in zip(r0, r1))
        print(f"{role}: {len(pairs)} pairs; rounds median {statistics.median(r0)} against {statistics.median(r1)}, "
              f"total {sum(r0)} against {sum(r1)} ({sum(r1) / sum(r0) - 1:+.0%}); {b_} fewer in {fewer}, the same "
              f"in {same}, more in {more}; work a round median {statistics.median(w0) / 1000:.1f}k against "
              f"{statistics.median(w1) / 1000:.1f}k")
        un = [(pa[1], pb[1]) for _, _, pa, pb in pairs if pa[1] and pb[1]]
        if un:
            u0, u1 = sum(a[0] for a, _ in un), sum(b[0] for _, b in un)
            print(f"     unseeded plays made by both: {len(un)}, rounds {u0} against {u1} ({u1 / u0 - 1:+.0%})")
    print()
    print("the pairs that one build reached and the other did not; for each, the play and round that reached it, and")
    print("the rounds the other build's same play got")
    for n, seed, pa, pb, ra, rb in discordant:
        won, r, other = ("V0", ra, pb) if ra else (b_, rb, pa)
        got = other[0 if r[0] == "seeded" else 1]
        print(f"{n} {seed}: {won} only, {said(r)}; the other's {r[0]} play had {got[0] if got else '-'} rounds")
    print(f"V0 only {sum(1 for d in discordant if d[4])}, {b_} only {sum(1 for d in discordant if d[5])}")


if __name__ == "__main__":
    main()
