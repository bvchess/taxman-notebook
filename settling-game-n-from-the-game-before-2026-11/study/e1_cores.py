#!/usr/bin/env python3
"""What n forbids in the sets that beat opt(n-1) - x on the holed board Y: for each E1 game, the best set T_Y of Y
(e1-holes/e1-show.jsonl, field "moves"), the residual of T_Y + n on board n (the core n creates), and which members
of the box and which promotions it holds.   nice -n 19 python3 -I study/e1_cores.py > study/e1_cores_out.txt"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import common, exch  # noqa: E402
from boxes import box_of  # noqa: E402
spf = exch.spf
res = exch.results()
for line in open(os.path.join(os.path.dirname(HERE), "e1-holes", "e1-show.jsonl")):
    if not line.strip(): continue
    r = json.loads(line); m = r["n"]; n = m + 1; x = r["holes"][0]
    TY = set(r["moves"]); S0 = set(res[m]["moves"]); S1 = set(res[n]["moves"])
    assert sum(TY) == r["score"] and x not in TY
    excess = r["score"] - (res[m]["score"] - x)
    box = box_of(n)
    play = common.playable(TY | {n}, n, spf)
    R = common.residual(TY | {n}, spf)
    print(f"== {n} = {exch.fac_str(n)}, x = {x}: opt(Y) = {r['score']} = opt(n-1) - x + {excess}; T_Y + n playable? {play}")
    print(f"   T_Y vs S*(n-1): dropped {sorted(S0 - TY)}, added {[(y, exch.fac_str(y)) for y in sorted(TY - S0)]}")
    print(f"   residual of T_Y + n on board n: {len(R)} members; box members in it {sorted(R & box)} (box {sorted(box)}); "
          f"promotions in it {[(y, exch.fac_str(y)) for y in sorted(R) if y <= n // 2]}; sources in it (not box) "
          f"{len([y for y in R if y > n // 2 and y not in box])}")
    even = all(sum(1 for z in R if f in common.maximal_factors(z, spf)) % 2 == 0 for z in R for f in common.maximal_factors(z, spf))
    print(f"   residual is an even core? {even}; T_Y - (added) + n playable? "
          f"{common.playable((TY - (TY - S0)) | {n}, n, spf)}")
