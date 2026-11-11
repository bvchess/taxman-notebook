#!/usr/bin/env python3
"""Tables 3 and 4 of the succession brief: the single-loss rule by kind of step, and the increments of the searched
games against the ceiling, with what predicts the shortfall.

    nice -n 19 python3 -I analyze.py > analyze_out.txt      # after settle.py and single_loss_tail.py

Inputs: settle.csv (settle.py), the October study's core_full.jsonl (n = 2..4955), single_loss_tail.jsonl
(4956..5060, single_loss_tail.py), and the committed results for the moves.

Words.  delta = n + opt(n - 1) - opt(n), the shortfall below the ceiling.  delta_pb = n - (PB(n) - PB(n - 1)), the parity
bound's own shortfall below its parity ceiling PB(n - 1) + n, computable in polynomial time.  rise = gap(n) - gap(n - 1)
= delta - delta_pb.  x_min = the smallest single loss (the single-loss rule); the rule holds when x_min = delta.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

KINDS = ["restrict", "relax", "exchange"]


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else float("nan")


def q(v, p):
    v = sorted(v)
    return v[int(p * (len(v) - 1))] if v else None


def formulas(srch, tc):
    """Which searched games have a delta given by a simple formula in the factorization of n.  P is the largest prime
    of n and P1 the prime before it; shadow(n) replaces every prime factor of an odd n by the prime before it."""
    spf = common.sieve_spf(20000)

    def prevp(p):
        q = p - 1
        while spf[q] != q:
            q -= 1
        return q

    def shadow(n):
        out = 1
        for p in common.factor(n):
            if p == 2:
                return None
            out *= prevp(p)
        return out

    print("Simple formulas for delta, searched games (the first that fits; P the largest prime of n, P1 the prime "
          "before it):")
    print("step | formula | games | share of the searched CPU | examples (n, delta)")
    table = {}
    for r in srch:
        n, d = r["n"], r["delta"]
        f = common.factor(n)
        P = f[-1]
        P1 = prevp(P) if P > 2 else None
        key = "none of these"
        if n % 2 == 1 and shadow(n) == d:
            key = "shadow(n)"
        else:
            for p in sorted(set(f)):
                m = n // p
                if m == d:
                    key = f"n/{p}"
                    break
                if P1 and m % P == 0 and m // P * P1 == d:
                    key = f"(n/{p}) with P replaced by P1"
                    break
        e = table.setdefault((r["step"], key), [0, 0.0, []])
        e[0] += 1
        e[1] += r["cpu"]
        if len(e[2]) < 5:
            e[2].append((n, d))
    for (st, key), (k, c, ex) in sorted(table.items(), key=lambda kv: (kv[0][0], -kv[1][1])):
        print(f"{st} | {key} | {k} | {100 * c / tc:.1f}% | {ex}")
    print("The formula (n/2) with P replaced by P1, by cofactor of n (searched relaxations of the cofactors with the most "
          "searched games): fits / games, and the range of n where it fits")
    by = {}
    for r in srch:
        if r["step"] != "relax":
            continue
        n, d = r["n"], r["delta"]
        f = common.factor(n)
        P = f[-1]
        fit = P > 2 and (n // 2) % P == 0 and (n // 2) // P * prevp(P) == d
        by.setdefault(r["cofactor"], []).append((n, fit))
    for c in sorted(by, key=lambda c: -len(by[c]))[:12]:
        v = by[c]
        fits = [n for n, ok in v if ok]
        print(f"  cofactor {c}: {len(fits)} / {len(v)}" + (f", n from {min(fits)} to {max(fits)}" if fits else "") +
              (f"; misses at {[n for n, ok in v if not ok][-8:]}" if len(fits) < len(v) else ""))
    print("The same formula past 5060 on the best-known scores of games.csv (delta_best_known of past5060.csv), "
          "cofactors 8 and 12:")
    with open(os.path.join(common.HERE, "past5060.csv")) as fh:
        past = list(csv.DictReader(fh))
    for c in (8, 12):
        sel = [r for r in past if int(r["cofactor"]) == c]
        fit = [r for r in sel if int(r["delta_best_known"]) == (c // 2) * prevp(int(r["n"]) // c)]
        print(f"  cofactor {c}: {len(sel)} games, kinds "
              f"{ {k: sum(r['kind'] == k for r in sel) for k in ('ceiling', 'repeat', 'searched')} }; fits {len(fit)}; "
              f"misses (n, best-known delta, formula): "
              f"{[(r['n'], r['delta_best_known'], (c // 2) * prevp(int(r['n']) // c)) for r in sel if r not in fit]}")


def main():
    rows = {}
    with open(os.path.join(common.HERE, "settle.csv")) as fh:
        for r in csv.DictReader(fh):
            for k, v in r.items():
                if k in ("outcome", "proof", "method", "step"):
                    continue
                r[k] = float(v) if k == "cpu" else int(v)
            rows[r["n"]] = r
    sl = common.single_loss()
    for x in common.jsonl(os.path.join(common.HERE, "single_loss_tail.jsonl")):
        if x["n"] > 4955:
            sl[x["n"]] = {"n": x["n"], "kind": x["kind"], "x_min": x["x_min"], "opt": x["opt"]}
    res = common.results()

    # ---- Table 3: the single-loss rule by kind of step and outcome.
    print("== Table 3: the single-loss rule (n-1's recorded optimal set, plus n, less the smallest move that makes it "
          "playable), 2..5060")
    print("(2..4955 from the October study's core_full.jsonl; 4956..5060 from single_loss_tail.jsonl)")
    for r in rows.values():
        s = sl.get(r["n"])
        if s is None:
            r["rule"] = "?"
            r["x_min"] = None
            continue
        r["x_min"] = s.get("x_min")
        if s["kind"] == "exact":
            r["rule"] = "exact"
        elif r["x_min"] == r["delta"]:
            r["rule"] = "holds"
        else:
            r["rule"] = "fails"
            assert r["x_min"] > r["delta"], r["n"]
    print("outcome, step | games | exact | holds | fails | fails' CPU share of the class | shortfall x_min - delta: "
          "median, p90")
    groups = [("all games", lambda r: True)]
    for o in ("prime", "ceiling", "repeat", "searched"):
        groups.append((o, lambda r, o=o: r["outcome"] == o))
    for k in KINDS + ["half-out"]:
        groups.append((f"searched, {k}", lambda r, k=k: r["outcome"] == "searched" and r["step"] == k))
        groups.append((f"ceiling, {k}", lambda r, k=k: r["outcome"] == "ceiling" and r["step"] == k))
        groups.append((f"repeat, {k}", lambda r, k=k: r["outcome"] == "repeat" and r["step"] == k))
    for name, f in groups:
        sel = [r for r in rows.values() if f(r) and r["rule"] != "?"]
        if not sel:
            continue
        c = sum(r["cpu"] for r in sel)
        fails = [r for r in sel if r["rule"] == "fails"]
        sh = [r["x_min"] - r["delta"] for r in fails]
        cs = f"{100 * sum(r['cpu'] for r in fails) / c:.1f}%" if c > 0 else "-"
        print(f"{name} | {len(sel)} | {sum(r['rule'] == 'exact' for r in sel)} | "
              f"{sum(r['rule'] == 'holds' for r in sel)} | {len(fails)} | {cs} | {q(sh, 0.5)}, {q(sh, 0.9)}")
    srch = [r for r in rows.values() if r["outcome"] == "searched"]
    tc = sum(r["cpu"] for r in srch)
    print(f"searched games where the rule holds hold {100 * sum(r['cpu'] for r in srch if r['rule'] == 'holds') / tc:.1f}% "
          f"of the searched CPU; where it fails, {100 * sum(r['cpu'] for r in srch if r['rule'] == 'fails') / tc:.1f}%")
    print("by band of n, searched games: holds / fails (CPU share of the band in holds)")
    for lo, hi in [(2, 1000), (1001, 2000), (2001, 3000), (3001, 4000), (4001, 5060)]:
        sel = [r for r in srch if lo <= r["n"] <= hi]
        c = sum(r["cpu"] for r in sel)
        h = [r for r in sel if r["rule"] == "holds"]
        print(f"  {lo}-{hi}: {len(h)} / {sum(r['rule'] == 'fails' for r in sel)} "
              f"({100 * sum(r['cpu'] for r in h) / c:.1f}%)")
    print("shortfall of the rule where it fails, searched games, by size (games):")
    sh = [r["x_min"] - r["delta"] for r in srch if r["rule"] == "fails"]
    for lo, hi in [(1, 10), (11, 100), (101, 300), (301, 1000), (1001, 10 ** 6)]:
        print(f"  {lo}-{hi}: {sum(lo <= s <= hi for s in sh)}")
    print("what x_min is, searched games where the rule holds, by step kind:")
    for k in KINDS:
        sel = [r for r in srch if r["step"] == k and r["rule"] == "holds"]
        if not sel:
            continue
        half = sum(r["x_min"] == r["n"] // 2 for r in sel)
        sh_ = 0
        if k == "exchange":
            sh_ = sum(r["x_min"] == r["n"] - r["bag_step"] for r in sel)
        print(f"  {k}: {len(sel)}; x_min = n/2 in {half}; x_min = the exchanged source in {sh_}")
    print()

    # ---- Table 4: increments and predictors.
    print("== Table 4: the increments opt(n) - opt(n-1) of the searched games against the ceiling's n")
    print("kind | games | inc/n: p10, p25, median, p75, p90 | delta: median | delta/n median")
    for k in KINDS + ["all"]:
        sel = [r for r in srch if k == "all" or r["step"] == k]
        inc = [(r["n"] - r["delta"]) / r["n"] for r in sel]
        print(f"{k} | {len(sel)} | " + ", ".join(f"{q(inc, p):.3f}" for p in (0.1, 0.25, 0.5, 0.75, 0.9)) +
              f" | {q([r['delta'] for r in sel], 0.5)} | {q([r['delta'] / r['n'] for r in sel], 0.5):.3f}")
    print()
    print("delta against delta_pb (the parity bound's shortfall below PB(n-1) + n), searched games:")
    print("kind | games | delta = delta_pb (rise 0): games, CPU | |rise| <= 10 | <= 100 | rise > 0 (delta above delta_pb)"
          " | rise < 0")
    for k in KINDS + ["all"]:
        sel = [r for r in srch if k == "all" or r["step"] == k]
        c = sum(r["cpu"] for r in sel)
        z = [r for r in sel if r["rise"] == 0]
        print(f"{k} | {len(sel)} | {len(z)}, {100 * sum(r['cpu'] for r in z) / c:.1f}% | "
              f"{sum(abs(r['rise']) <= 10 for r in sel)} | {sum(abs(r['rise']) <= 100 for r in sel)} | "
              f"{sum(r['rise'] > 0 for r in sel)} | {sum(r['rise'] < 0 for r in sel)}")
    ri = [r["rise"] for r in srch]
    print(f"rise on searched games: p5 {q(ri, 0.05)}, p25 {q(ri, 0.25)}, median {q(ri, 0.5)}, p75 {q(ri, 0.75)}, "
          f"p95 {q(ri, 0.95)}, min {min(ri)}, max {max(ri)}")
    other = [r for r in rows.values() if r["outcome"] in ("ceiling", "repeat", "prime")]
    print(f"rise on the other games (prime, ceiling, repeat; {len(other)}): 0 at {sum(r['rise'] == 0 for r in other)}, "
          f"negative at {sum(r['rise'] < 0 for r in other)} (all at the ceiling: "
          f"{sorted(r['n'] for r in other if r['rise'] < 0)})")
    print()
    print("Rank correlations (Spearman) with delta, searched games:")
    feats = {
        "n": lambda r: r["n"],
        "delta_pb": lambda r: r["n"] - r["bound_step"],
        "x_min": lambda r: r["x_min"] if r["x_min"] is not None else 0,
        "gap(n-1)": lambda r: r["gap_prev"],
        "layer": lambda r: r["layer"],
        "largest prime of n": lambda r: common.factor(r["n"])[-1],
        "cofactor": lambda r: r["cofactor"],
    }
    for k in KINDS + ["all"]:
        sel = [r for r in srch if (k == "all" or r["step"] == k)]
        d = [r["delta"] for r in sel]
        print(f"  {k} ({len(sel)}): " + ", ".join(f"{name} {spearman([f(r) for r in sel], d):+.2f}"
                                                for name, f in feats.items()))
    print("  delta/n against the same, all searched: " + ", ".join(
        f"{name} {spearman([f(r) for r in srch], [r['delta'] / r['n'] for r in srch]):+.2f}" for name, f in feats.items()))
    print()
    print("The gap's persistence: rise of game n against the rise of the searched game before it (same sign?)")
    prev = None
    same = diff = 0
    for r in sorted(srch, key=lambda r: r["n"]):
        if prev is not None and r["rise"] != 0 and prev["rise"] != 0:
            if (r["rise"] > 0) == (prev["rise"] > 0):
                same += 1
            else:
                diff += 1
        prev = r
    print(f"  consecutive searched games with both rises nonzero: same sign {same}, opposite {diff}")
    print()

    # The relax steps: is n/2 promoted in the optimal game of n?
    print("Relax steps (n even, s = n/2 in U*(n-1)), searched: does the optimal set of n play s?")
    rel = [r for r in srch if r["step"] == "relax"]
    ins = [r for r in rel if (r["n"] // 2) in set(res[r["n"]]["moves"])]
    print(f"  {len(rel)} relax steps; s in the recorded optimal set of n at {len(ins)}; delta = s at "
          f"{sum(r['delta'] == r['n'] // 2 for r in rel)} (those with s out: "
          f"{sorted(r['n'] for r in rel if (r['n'] // 2) not in set(res[r['n']]['moves']))})")
    rc = [r for r in rows.values() if r["outcome"] == "ceiling" and r["step"] == "relax"]
    print(f"  relax steps at the ceiling: {len(rc)}; s in the optimal set at "
          f"{sum((r['n'] // 2) in set(res[r['n']]['moves']) for r in rc)}")
    print()
    # Restrict steps: P* fall, delta relative to n
    rs = [r for r in srch if r["step"] == "restrict"]
    print("Restrict steps (n odd, U* gains n only), searched, by layer of n: games, median delta, median delta/n, CPU share")
    for lay in sorted({r["layer"] for r in rs}):
        sel = [r for r in rs if r["layer"] == lay]
        print(f"  layer {lay}: {len(sel)}, {q([r['delta'] for r in sel], 0.5)}, "
              f"{q([r['delta'] / r['n'] for r in sel], 0.5):.3f}, {100 * sum(r['cpu'] for r in sel) / tc:.1f}%")
    print("Relax steps by layer of n: games, median delta/(n/2), CPU share")
    for lay in sorted({r["layer"] for r in rel}):
        sel = [r for r in rel if r["layer"] == lay]
        print(f"  layer {lay}: {len(sel)}, {q([r['delta'] / (r['n'] // 2) for r in sel], 0.5):.3f}, "
              f"{100 * sum(r['cpu'] for r in sel) / tc:.1f}%")
    print("Ceiling and searched games of the restrict and relax kinds, by layer (ceiling/searched):")
    for k in ("restrict", "relax"):
        for lay in range(2, 13):
            c = sum(1 for r in rows.values() if r["step"] == k and r["layer"] == lay and r["outcome"] == "ceiling")
            s = sum(1 for r in rows.values() if r["step"] == k and r["layer"] == lay and r["outcome"] == "searched")
            if c or s:
                print(f"  {k}, layer {lay}: {c}/{s}")
    print()
    formulas(srch, tc)
    with open(os.path.join(common.HERE, "searched.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "step", "layer", "cofactor", "delta", "delta_pb", "rise", "gap", "x_min", "rule", "cpu_hours",
                    "nodes"])
        for r in sorted(srch, key=lambda r: r["n"]):
            w.writerow([r["n"], r["step"], r["layer"], r["cofactor"], r["delta"], r["n"] - r["bound_step"], r["rise"],
                        r["gap"], r["x_min"], r["rule"], round(r["cpu"] / 3600, 4), r["nodes"]])


if __name__ == "__main__":
    main()
