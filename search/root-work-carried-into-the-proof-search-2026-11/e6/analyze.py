#!/usr/bin/env python3
"""E6: classify the members of the branchings that the branch trace recorded (solver/frame/src/search/branch_trace.rs).

usage: analyze.py N PREFIX [BOUND]

Reads PREFIX.K.txt for every K, one line per branching:  KIND FORCED PROMOTED GAP SIZE OUTCOME N K A
and classifies each member x by its layer (Omega(x)) and as smooth (largest prime factor <= BOUND, default 23) or
fiber (a prime above BOUND).  Prints markdown tables.

Branchings fall in four categories:
  choice  not forced, the conflict has 2 or more members: strong branching picks the member N to bar
  single  not forced, the conflict has one member
  none    the node has no conflict among its candidates and branches on its largest candidate
  forced  the child promotes the node's forced members and the node's loop ends; nothing is barred

Weights: count (1 a branching), and subtree (1 + the steps in the child's subtree: what the choice leaves to explore).
"""
import glob
import sys
from collections import defaultdict

n_game = int(sys.argv[1])
prefix = sys.argv[2]
bound = int(sys.argv[3]) if len(sys.argv) > 3 else 23

# Largest prime factor and Omega of every number up to n.
spf = list(range(n_game + 1))
for p in range(2, int(n_game**0.5) + 1):
    if spf[p] == p:
        for m in range(p * p, n_game + 1, p):
            if spf[m] == m:
                spf[m] = p
lpf = [0] * (n_game + 1)
omega = [0] * (n_game + 1)
for x in range(2, n_game + 1):
    rest, big, count = x, 0, 0
    while rest > 1:
        p = spf[rest]
        big = max(big, p)
        rest //= p
        count += 1
    lpf[x], omega[x] = big, count
smooth = [x >= 2 and lpf[x] <= bound for x in range(n_game + 1)]

# The search's candidates by layer and class: the base rate against which the members are compared.
pool = defaultdict(int)
try:
    with open(prefix + ".cands") as f:
        for x in f.read().strip().split(","):
            pool[(omega[int(x)], smooth[int(x)])] += 1
except FileNotFoundError:
    pass

CATEGORIES = ("choice", "single", "none", "forced")
WEIGHTS = ("count", "subtree")


def band(gap):
    return "<300" if gap < 300 else "300-999" if gap < 1000 else ">=1000"


# members[cat][weight][(layer, smooth)] ; barred[cat][weight][(layer, smooth)]
members = {c: {w: defaultdict(float) for w in WEIGHTS} for c in CATEGORIES}
barred = {c: {w: defaultdict(float) for w in WEIGHTS} for c in CATEGORIES}
# the conflict's composition (all smooth, all fiber, mixed) and, in a choice, whether the barred member is smooth
mixture = {c: {w: defaultdict(float) for w in WEIGHTS} for c in CATEGORIES}
pick_in_mixed = {w: defaultdict(float) for w in WEIGHTS}
# by gap band, the barred member of a choice (smooth, fiber) and its conflict's members
by_band = {w: defaultdict(float) for w in WEIGHTS}
by_depth = {w: defaultdict(float) for w in WEIGHTS}
outcomes = defaultdict(lambda: [0, 0.0])
totals = {c: [0, 0.0, 0] for c in CATEGORIES}  # branchings, weight, partial

lines = 0
for path in sorted(glob.glob(prefix + ".*.txt")):
    with open(path) as f:
        for line in f:
            kind, forced, promoted, gap, size, outcome, n, k, added = line.split()
            lines += 1
            short = size.endswith("+")
            size = int(size.rstrip("+"))
            K = [int(x) for x in k.split(",")] if k != "-" else []
            n = int(n)
            gap = int(gap)
            if forced == "1":
                cat = "forced"
            elif kind == "N":
                cat = "none"
            elif len(K) == 1:
                cat = "single"
            else:
                cat = "choice"
            w = {"count": 1.0, "subtree": 1.0 + size}
            t = totals[cat]
            t[0] += 1
            t[1] += w["subtree"]
            t[2] += short
            outcomes[(cat, outcome)][0] += 1
            outcomes[(cat, outcome)][1] += w["subtree"]
            for x in K:
                key = (omega[x], smooth[x])
                for wn in WEIGHTS:
                    members[cat][wn][key] += w[wn]
            if cat != "forced":
                key = (omega[n], smooth[n])
                for wn in WEIGHTS:
                    barred[cat][wn][key] += w[wn]
            else:
                for x in added.split(",") if added != "-" else [str(n)]:
                    x = int(x)
                    key = (omega[x], smooth[x])
                    for wn in WEIGHTS:
                        barred["forced"][wn][key] += w[wn]  # promoted forced members, not barred
            if K:
                s = sum(smooth[x] for x in K)
                comp = "all smooth" if s == len(K) else "all fiber" if s == 0 else "mixed"
                for wn in WEIGHTS:
                    mixture[cat][wn][comp] += w[wn]
                if cat == "choice":
                    for wn in WEIGHTS:
                        if comp == "mixed":
                            pick_in_mixed[wn]["smooth" if smooth[n] else "fiber"] += w[wn]
                            # the share a blind pick would give: the smooth share of the conflict
                            pick_in_mixed[wn]["blind smooth"] += w[wn] * s / len(K)
                        by_band[wn][(band(gap), "smooth" if smooth[n] else "fiber")] += w[wn]
                        by_depth[wn][(min(int(promoted) // 4 * 4, 24), "smooth" if smooth[n] else "fiber")] += w[wn]

print(f"# E6 branch classes, game {n_game}, smooth = every prime <= {bound}, {lines} branchings\n")
print("| category | branchings | share | subtree weight share | partial subtrees |")
print("|---|---|---|---|---|")
all_n = sum(t[0] for t in totals.values())
all_w = sum(t[1] for t in totals.values())
for c in CATEGORIES:
    t = totals[c]
    print(f"| {c} | {t[0]} | {100 * t[0] / all_n:.1f}% | {100 * t[1] / all_w:.1f}% | {t[2]} |")
print()


def share_table(title, table, cats):
    """Rows: layer; columns: smooth count and share, fiber count and share, for each weight."""
    print(f"### {title}\n")
    for wn in WEIGHTS:
        merged = defaultdict(float)
        for c in cats:
            for key, v in table[c][wn].items():
                merged[key] += v
        layers = sorted({layer for layer, _ in merged})
        print(f"weight = {wn}\n")
        print("| layer | smooth | fiber | smooth share | smooth share of the candidates |")
        print("|---|---|---|---|---|")
        tot_s = tot_f = 0.0
        for layer in layers:
            s, f = merged.get((layer, True), 0.0), merged.get((layer, False), 0.0)
            tot_s += s
            tot_f += f
            ps, pf = pool.get((layer, True), 0), pool.get((layer, False), 0)
            base = f"{100 * ps / (ps + pf):.1f}% ({ps} of {ps + pf})" if ps + pf else "-"
            print(f"| {layer} | {s:.0f} | {f:.0f} | {100 * s / (s + f):.1f}% | {base} |")
        if tot_s + tot_f:
            ps, pf = sum(v for (_, sm), v in pool.items() if sm), sum(v for (_, sm), v in pool.items() if not sm)
            base = f"{100 * ps / (ps + pf):.1f}% ({ps} of {ps + pf})" if ps + pf else "-"
            print(f"| all | {tot_s:.0f} | {tot_f:.0f} | {100 * tot_s / (tot_s + tot_f):.1f}% | {base} |")
        print()


share_table("Conflict members, choices (not forced, 2 or more members)", members, ["choice"])
share_table("Barred member, choices", barred, ["choice"])
share_table("Conflict members, all categories", members, CATEGORIES)
for c in ("single", "none", "forced"):
    share_table(f"Conflict members, {c}", members, [c])
share_table("Members promoted by forced steps (the forced set, or its largest)", barred, ["forced"])
share_table("Branched-on member of single-member and no-conflict steps", barred, ["single", "none"])

print("### Composition of the conflict\n")
for wn in WEIGHTS:
    print(f"weight = {wn}\n")
    print("| category | all smooth | all fiber | mixed |")
    print("|---|---|---|---|")
    for c in CATEGORIES:
        m = mixture[c][wn]
        tot = sum(m.values()) or 1
        row = " | ".join(f"{100 * m[kind] / tot:.1f}%" for kind in ("all smooth", "all fiber", "mixed"))
        print(f"| {c} | {row} |")
    print()

print("### In a choice whose conflict mixes smooth and fiber members: the barred member\n")
for wn in WEIGHTS:
    p = pick_in_mixed[wn]
    tot = p["smooth"] + p["fiber"]
    if tot:
        print(
            f"weight = {wn}: barred member smooth {100 * p['smooth'] / tot:.1f}%, fiber {100 * p['fiber'] / tot:.1f}%; "
            f"a blind pick within the conflict would be smooth {100 * p['blind smooth'] / tot:.1f}%\n"
        )

print("### Barred member of a choice, by gap band and by the node's promotions\n")
for wn in WEIGHTS:
    print(f"weight = {wn}\n")
    print("| band | smooth | fiber | smooth share |")
    print("|---|---|---|---|")
    for b in ("<300", "300-999", ">=1000"):
        s, f = by_band[wn][(b, "smooth")], by_band[wn][(b, "fiber")]
        if s + f:
            print(f"| gap {b} | {s:.0f} | {f:.0f} | {100 * s / (s + f):.1f}% |")
    for d in range(0, 28, 4):
        s, f = by_depth[wn][(d, "smooth")], by_depth[wn][(d, "fiber")]
        if s + f:
            label = f"{d}-{d + 3}" if d < 24 else "24+"
            print(f"| promoted {label} | {s:.0f} | {f:.0f} | {100 * s / (s + f):.1f}% |")
    print()

print("### Outcome of the child\n")
print("| category | outcome | branchings | subtree weight |")
print("|---|---|---|---|")
for (c, o), (cnt, wt) in sorted(outcomes.items()):
    print(f"| {c} | {o} | {cnt} | {wt:.0f} |")
