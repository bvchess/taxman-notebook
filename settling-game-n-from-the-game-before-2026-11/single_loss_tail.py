#!/usr/bin/env python3
"""The single-loss rule on games the October study did not reach (4956..5060), and a cross-check on a sample it did.

The rule: let M be the recorded optimal set of n - 1.  If M + n is playable, the rule's game scores the ceiling
(kind exact).  Otherwise x_min is the smallest x in M with M + n - x playable, and the rule scores opt(n-1) + n - x_min
(kind one_loss).  Every x is tried upward, one peel each, until one makes the set playable.

    nice -n 19 python3 -I single_loss_tail.py > single_loss_tail_out.txt   # writes single_loss_tail.jsonl

The output file is appended game by game, and a rerun skips the games already in it.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

OUT = os.path.join(common.HERE, "single_loss_tail.jsonl")
SAMPLE = [100, 211, 500, 1001, 2001, 3001, 4001, 4500, 4900, 4955]


def rule(n, res, spf):
    m = set(res[n - 1]["moves"])
    if common.playable(m | {n}, n, spf):
        return {"kind": "exact", "x_min": None}
    for x in sorted(m):
        if common.playable((m - {x}) | {n}, n, spf):
            return {"kind": "one_loss", "x_min": x}
    return {"kind": "none", "x_min": None}


def main():
    res = common.results()
    spf = common.sieve_spf(10000)
    done = {}
    if os.path.exists(OUT):
        done = {x["n"]: x for x in common.jsonl(OUT)}
    old = common.single_loss()
    todo = [n for n in SAMPLE + list(range(4956, 5061)) if n not in done]
    with open(OUT, "a") as fh:
        for n in todo:
            t = time.time()
            r = rule(n, res, spf)
            r.update({"n": n, "opt_prev": res[n - 1]["score"], "opt": res[n]["score"],
                      "rule_score": res[n - 1]["score"] + n - (r["x_min"] or 0), "seconds": round(time.time() - t, 2)})
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            done[n] = r
    agree = sum(1 for n in SAMPLE if done[n]["kind"] == old[n]["kind"] and done[n]["x_min"] == old[n].get("x_min"))
    print(f"cross-check against the October study's core_full.jsonl on {len(SAMPLE)} games: {agree} agree")
    for n in SAMPLE:
        if not (done[n]["kind"] == old[n]["kind"] and done[n]["x_min"] == old[n].get("x_min")):
            print("  differs:", n, done[n], old[n])
    tail = [done[n] for n in range(4956, 5061)]
    kinds = {}
    for r in tail:
        k = "exact" if r["kind"] == "exact" else ("holds" if r["rule_score"] == r["opt"] else "fails")
        kinds[k] = kinds.get(k, 0) + 1
    print("4956..5060:", kinds)


if __name__ == "__main__":
    main()
