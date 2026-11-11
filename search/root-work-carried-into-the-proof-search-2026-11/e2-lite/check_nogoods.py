#!/usr/bin/env python3
"""Checks E2's nogoods from the definitions alone, with the brief's parity.py (no code of the solver).

    python3 -I check_nogoods.py N EXPORT.jsonl KEPT.txt

G is the greedy GF(2) basis of the sources (U*, the moves the frame model fixes).  Two checks:

* every conflict that e1_smooth exported (EXPORT.jsonl: its core K and its literals L): every member of K is in
  S = G + L, its sources in G and the rest in L, and K is a core of S's instance (every factor that a member of K lists,
  a maximal factor not in S, is listed by two members of K or more).  A superset of S only shortens the lists, so K
  stays a core: no playable set holds G and L.
* every nogood the solver kept (KEPT.txt, from e2_validate, one a line): its members are at most n/2, and the instance
  of S = G + N has a nonempty residual in some layer (a linear dismantling), so S is not playable, and neither is any
  superset of it.

It prints one JSON line with the counts; "ok" is true when every set passes.
"""

import json
import sys
from collections import defaultdict

sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
import parity as P  # noqa: E402


def residual_nonempty(members, lists):
    """Whether dismantling the instance (members, each with its list) leaves a member: repeatedly delete a member
    that lists a factor no other live member lists."""
    listers = defaultdict(list)
    for x in members:
        for f in lists[x]:
            listers[f].append(x)
    count = {f: len(v) for f, v in listers.items()}
    alive = set(members)
    stack = list(members)
    while stack:
        x = stack.pop()
        if x not in alive or not any(count[f] == 1 for f in lists[x]):
            continue
        alive.discard(x)
        for f in lists[x]:
            count[f] -= 1
            if count[f] == 1:
                stack.extend(y for y in listers[f] if y in alive)
    return bool(alive)


def main():
    n, export, kept = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    om, mf = P.omega_and_mf(n)
    g = set(P.greedy_basis(n, om, mf))
    half = n // 2
    out = {"n": n, "G": len(g), "G_sum": sum(g)}

    cores_ok = cores_bad = 0
    for raw in open(export):
        c = json.loads(raw)
        core, lits = c["core"], set(c["literals"])
        s = g | lits
        ok = all(x <= half for x in lits)
        ok &= all((x in g) if x > half else (x in lits) for x in core)
        listed = defaultdict(int)
        for x in core:
            for f in mf[x]:
                if f not in s:
                    listed[f] += 1
        ok &= all(v >= 2 for v in listed.values())
        cores_ok += ok
        cores_bad += not ok
    out["exported_cores_ok"], out["exported_cores_bad"] = cores_ok, cores_bad

    by_layer = defaultdict(list)
    for x in g:
        by_layer[om[x]].append(x)
    nogoods_ok = nogoods_bad = 0
    for raw in open(kept):
        nogood = [int(x) for x in raw.split()]
        if not nogood:
            continue
        s = g | set(nogood)
        ok = all(x <= half for x in nogood)
        # Only the layers of the nogood's members, and the layers above them, differ from G's instance.
        layers = {om[x] for x in nogood} | {om[x] + 1 for x in nogood}
        stuck = False
        for k in sorted(layers):
            members = by_layer[k] + [x for x in nogood if om[x] == k]
            lists = {x: [f for f in mf[x] if f not in s] for x in members}
            if residual_nonempty(members, lists):
                stuck = True
                break
        ok &= stuck
        nogoods_ok += ok
        nogoods_bad += not ok
    out["kept_nogoods_ok"], out["kept_nogoods_bad"] = nogoods_ok, nogoods_bad
    # G alone is playable (descending greedy keeps only what is playable together), so a stuck layer is the nogood's.
    out["G_playable"] = not any(
        residual_nonempty(by_layer[k], {x: [f for f in mf[x] if f not in g] for x in by_layer[k]}) for k in by_layer
    )
    out["ok"] = cores_bad == 0 and nogoods_bad == 0 and out["G_playable"]
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
