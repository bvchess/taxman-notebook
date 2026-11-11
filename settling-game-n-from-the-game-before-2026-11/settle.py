#!/usr/bin/env python3
"""Tables 1 and 2 of the succession brief: how each game was settled, and for the searched games how far opt(n) fell
below the ceiling, with the chain's CPU by that distance.

    nice -n 19 python3 -I settle.py > settle_out.txt      # also writes settle.csv

Inputs: results/optimal.jsonl.gz (games 1..5060, proven), the gap dashboard's games.csv (2..10000: the parity bound,
U*, and past 5060 the best-known scores), and the arrival entry's arrival.jsonl.gz (U* gained and lost at each board
3..8191, and whether n/2 was in U*(n - 1)).

Classification (the "outcome" of a game):
  trivial   proof kind trivial (boards with no candidates)
  prime     proof kind prime_formula
  ceiling   score = score(n - 1) + n (whatever the proof kind: a start or search that reached the ceiling, a repeat at it)
  repeat    proof kind same_search, below the ceiling
  searched  proof kind exhausted, below the ceiling
Past 5060 the same rule on games.csv's best-known scores (its column `kind`).

Step kind of a searched or repeated composite n (from arrival.jsonl.gz, U*(n) against U*(n - 1)):
  relax     n even and n/2 in U*(n - 1): n/2 leaves U* (it becomes a factor and a candidate) and n joins
  restrict  n odd, U* gains n and loses nothing: n takes a freedom of a frame
  exchange  n odd, U* gains n and loses one source x (the shadow, in every case measured)
  half-out  n even and n/2 not in U*(n - 1) (U* gains n only)
  other     anything else
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

BANDS_N = [(2, 1000), (1001, 2000), (2001, 3000), (3001, 4000), (4001, 4500), (4501, 5060)]
BANDS_D = [(1, 10), (11, 30), (31, 100), (101, 300), (301, 1000), (1001, 3000), (3001, 10 ** 9)]


def step_kind(a, n):
    if a is None:
        return "?"
    added, dropped = set(a["added"]), set(a["dropped"])
    if n % 2 == 0:
        if a["half_in_ustar"]:
            return "relax" if added == {n} and dropped == {n // 2} else "relax*"
        return "half-out" if added == {n} and not dropped else "other"
    if added == {n} and not dropped:
        return "restrict"
    if added == {n} and len(dropped) == 1:
        return "exchange"
    return "other"


def kind_by_bag(n, gc):
    """The step kind read from the change of the sum of U* (games.csv's ustar), for any n of 3..10000."""
    f = common.factor(n)
    if len(f) == 1:
        return "prime"
    b = gc[n]["ustar"] - gc[n - 1]["ustar"]
    if n % 2 == 0:
        if b == n:
            return "half-out"
        return "relax" if b == n - n // 2 else "other"
    if b == n:
        return "restrict"
    return "exchange" if b < n else "other"


def band_label(b):
    lo, hi = b
    return f"{lo}-{hi}" if hi < 10 ** 8 else f">{lo - 1}"


def main():
    res = common.results()
    gc = common.games_csv()
    arr = common.arrival()
    rows = []
    for n in range(2, 5061):
        x, prev = res[n], res[n - 1]
        f = common.factor(n)
        at_ceiling = x["score"] == prev["score"] + n
        if x["proof"] == "trivial":
            outcome = "trivial"
        elif x["proof"] == "prime_formula":
            outcome = "prime"
        elif at_ceiling:
            outcome = "ceiling"
        elif x["proof"] == "same_search":
            outcome = "repeat"
        elif x["proof"] == "exhausted":
            outcome = "searched"
        else:
            raise SystemExit(f"unclassified {n} {x['proof']}")
        delta = prev["score"] + n - x["score"]
        if x.get("setup") and x["proof"] == "exhausted":
            pstar = x["score"] - x["in_the_bag"]
            assert x["setup"]["cap"] - pstar == delta, n
        g = gc[n]
        bag_prev = gc[n - 1]["ustar"] if n > 2 else 0
        rows.append({
            "n": n, "outcome": outcome, "proof": x["proof"], "method": x["method"], "score": x["score"],
            "delta": delta, "ceiling": prev["score"] + n, "bound": g["bound"], "gap": g["gap"],
            "gap_prev": gc[n - 1]["gap"] if n > 2 else 0, "rise": g["rise"] if g["rise"] is not None else 0,
            "bound_step": g["bound"] - gc[n - 1]["bound"] if n > 2 else g["bound"],
            "bag_step": g["ustar"] - bag_prev, "pstar_step": (x["score"] - g["ustar"]) - (prev["score"] - bag_prev),
            "cpu": x["seconds"]["cpu"], "nodes": x["nodes"], "layer": len(f), "cofactor": n // f[-1],
            "parity": n % 2, "step": kind_by_bag(n, gc) if n > 2 else "prime",
            "omega_distinct": len(set(f)),
        })
    with open(os.path.join(common.HERE, "settle.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    both = [n for n in range(3, 10001) if n in arr]
    same = sum(kind_by_bag(n, gc) == (step_kind(arr[n], n) if len(common.factor(n)) > 1 else "prime") for n in both)
    print(f"Step kinds read from the sum of U* agree with those read from the sets of arrival.jsonl.gz at {same} of "
          f"{len(both)} boards 3..8191")
    total_cpu = sum(r["cpu"] for r in rows)
    print(f"Games 2..5060: {len(rows)}; chain CPU {total_cpu:,.0f} s = {total_cpu / 3600:,.0f} CPU-hours")
    print()
    print("== Table 1a: outcome by band of n (games; CPU-hours)")
    outs = ["trivial", "prime", "ceiling", "repeat", "searched"]
    print("band | " + " | ".join(outs) + " | CPU-hours of searched")
    for b in BANDS_N + [(2, 5060)]:
        sel = [r for r in rows if b[0] <= r["n"] <= b[1]]
        cnt = [sum(r["outcome"] == o for r in sel) for o in outs]
        cpu = sum(r["cpu"] for r in sel if r["outcome"] == "searched") / 3600
        print(f"{band_label(b)} | " + " | ".join(str(c) for c in cnt) + f" | {cpu:,.1f}")
    print()
    print("== Table 1b: proof kind against outcome, 2..5060")
    kinds = sorted({(r["proof"], r["method"]) for r in rows})
    for k in kinds:
        sel = [r for r in rows if (r["proof"], r["method"]) == k]
        by = {o: sum(r["outcome"] == o for r in sel) for o in outs}
        print(k, len(sel), {o: v for o, v in by.items() if v}, f"CPU-h {sum(r['cpu'] for r in sel) / 3600:,.2f}")
    sp = [r for r in rows if r["layer"] == 2 and r["parity"] == 1 and r["n"] >= 189]
    print(f"odd numbers with two prime factors, 189..5060: {len(sp)}; outcomes "
          f"{ {o: sum(r['outcome'] == o for r in sp) for o in outs} } (the semiprime formula J3 settles all of them)")
    cap_search = [r for r in rows if r["proof"] == "cap" and r["method"] == "search"]
    print("ceiling reached by a search (proof cap, method search):", [(r["n"], round(r["cpu"], 2)) for r in cap_search])
    print()

    srch = [r for r in rows if r["outcome"] == "searched"]
    scpu = sum(r["cpu"] for r in srch)
    print(f"== Table 1c: searched games below the ceiling: {len(srch)}, CPU {scpu / 3600:,.1f} CPU-hours "
          f"({100 * scpu / total_cpu:.2f}% of the chain)")
    print("delta = ceiling - opt(n) = n + opt(n-1) - opt(n), in points")
    print("band of n | games | median delta | " + " | ".join(band_label(d) for d in BANDS_D))
    for b in BANDS_N + [(2, 5060)]:
        sel = sorted([r for r in srch if b[0] <= r["n"] <= b[1]], key=lambda r: r["delta"])
        med = sel[len(sel) // 2]["delta"] if sel else 0
        cells = []
        bc = sum(r["cpu"] for r in sel)
        for d in BANDS_D:
            ss = [r for r in sel if d[0] <= r["delta"] <= d[1]]
            cells.append(f"{len(ss)} ({100 * sum(r['cpu'] for r in ss) / bc:.1f}%)" if bc else str(len(ss)))
        print(f"{band_label(b)} | {len(sel)} | {med} | " + " | ".join(cells))
    print("(cells: games, and in brackets the share of that band's searched CPU)")
    print()
    print("Share of the searched games' CPU (and of the games) with delta at most D, 2..5060 and 3001..5060:")
    for lo in (2, 3001, 4001):
        sel = [r for r in srch if r["n"] >= lo]
        c = sum(r["cpu"] for r in sel)
        cells = []
        for dmax in (10, 30, 100, 300, 1000, 3000):
            ss = [r for r in sel if r["delta"] <= dmax]
            cells.append(f"<= {dmax}: {100 * sum(r['cpu'] for r in ss) / c:.1f}% CPU, {len(ss)} games")
        print(f"  from {lo}: " + "; ".join(cells))
    print()
    print("delta relative to n and to the root's parity gap (gap = PB(n) - opt(n)), searched games:")
    for lo, hi in BANDS_N + [(2, 5060)]:
        sel = [r for r in srch if lo <= r["n"] <= hi]
        c = sum(r["cpu"] for r in sel)
        below = [r for r in sel if r["delta"] < r["gap"]]
        dn = sorted(r["delta"] / r["n"] for r in sel)
        print(f"  {lo}-{hi}: median delta/n {dn[len(dn) // 2]:.3f}; ceiling below the parity bound "
              f"(delta < gap) in {len(below)} of {len(sel)} games, {100 * sum(r['cpu'] for r in below) / c:.1f}% "
              f"of the CPU")
    print()
    print("The 25 dearest searched games:")
    print("n | CPU-hours | share of chain | delta | gap | rise | step | layer | cofactor")
    for r in sorted(srch, key=lambda r: -r["cpu"])[:25]:
        print(f"{r['n']} | {r['cpu'] / 3600:,.1f} | {100 * r['cpu'] / total_cpu:.2f}% | {r['delta']} | {r['gap']} | "
              f"{r['rise']} | {r['step']} | {r['layer']} | {r['cofactor']}")
    top = sorted(srch, key=lambda r: -r["cpu"])
    for k in (10, 50, 100, 200):
        print(f"  the {k} dearest hold {100 * sum(r['cpu'] for r in top[:k]) / total_cpu:.1f}% of the chain's CPU")
    print()

    print("== Table 1d: step kind of the searched games (U*(n) against U*(n-1))")
    print("step | games | CPU share of searched | median delta | delta = 0? | median pstar_step | delta <= 100 CPU share")
    for st in ["restrict", "relax", "exchange", "relax*", "half-out", "other", "?"]:
        sel = sorted([r for r in srch if r["step"] == st], key=lambda r: r["delta"])
        if not sel:
            continue
        c = sum(r["cpu"] for r in sel)
        med = sel[len(sel) // 2]["delta"]
        ps = sorted(r["pstar_step"] for r in sel)[len(sel) // 2]
        small = sum(r["cpu"] for r in sel if r["delta"] <= 100)
        print(f"{st} | {len(sel)} | {100 * c / scpu:.1f}% | {med} | {sum(r['delta'] == 0 for r in sel)} | {ps} | "
              f"{100 * small / c:.1f}%")
    for lo in (3001, 4001):
        print(f"  from {lo}:")
        sel0 = [r for r in srch if r["n"] >= lo]
        c0 = sum(r["cpu"] for r in sel0)
        for st in ["restrict", "relax", "exchange", "relax*", "other"]:
            sel = sorted([r for r in sel0 if r["step"] == st], key=lambda r: r["delta"])
            if sel:
                print(f"    {st}: {len(sel)} games, {100 * sum(r['cpu'] for r in sel) / c0:.1f}% CPU, median delta "
                      f"{sel[len(sel) // 2]['delta']}")
    print()
    print("Relax steps: delta against s = n/2 (delta <= s always; delta = s - (rise of P*))")
    rel = [r for r in srch if r["step"] == "relax"]
    eq = [r for r in rel if r["delta"] == r["n"] // 2]
    print(f"  {len(rel)} relax steps; delta = n/2 at {len(eq)}; delta/(n/2) quartiles "
          f"{[round(sorted(r['delta'] / (r['n'] // 2) for r in rel)[int(q * (len(rel) - 1))], 3) for q in (0.1, 0.25, 0.5, 0.75, 0.9)]}")
    print("Restrict steps: delta = the fall of P* (U* gains n only)")
    rs = [r for r in srch if r["step"] == "restrict"]
    print(f"  {len(rs)} restrict steps; delta quartiles "
          f"{[sorted(r['delta'] for r in rs)[int(q * (len(rs) - 1))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)]}")
    ex = [r for r in srch if r["step"] == "exchange"]
    if ex:
        print(f"Exchange steps: {len(ex)}; delta quartiles "
              f"{[sorted(r['delta'] for r in ex)[int(q * (len(ex) - 1))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)]}; "
              f"P* unchanged (a near repeat) at {sum(r['pstar_step'] == 0 for r in ex)}")
    print()

    # Repeats and ceilings by step kind, for the record.
    print("All composite non-trivial games 2..5060 by step kind and outcome:")
    for st in ["restrict", "relax", "exchange", "half-out", "relax*", "other", "?"]:
        sel = [r for r in rows if r["step"] == st and r["outcome"] not in ("trivial", "prime")]
        if sel:
            print(f"  {st}: " + ", ".join(f"{o} {sum(r['outcome'] == o for r in sel)}" for o in outs[2:]))
    print()

    # Table 2: past 5060.
    print("== Table 2: games 5061..10000 by the best-known scores (games.csv kind)")
    past = [gc[n] for n in range(5061, 10001)]
    print("band | " + " | ".join(["prime", "ceiling", "repeat", "searched"]))
    for lo, hi in [(5061, 6000), (6001, 7000), (7001, 8000), (8001, 9000), (9001, 10000), (5061, 10000)]:
        sel = [g for g in past if lo <= g["n"] <= hi]
        print(f"{lo}-{hi} | " + " | ".join(str(sum(g["kind"] == k for g in sel)) for k in
                                         ["prime", "ceiling", "repeat", "searched"]))
    print("searched past 5060 by step kind (from the sum of U*), and best-known delta (not proven):")
    for st in ["exchange", "relax", "restrict", "half-out"]:
        print(f"  all games of kind {st}: " + ", ".join(f"{k} {sum(1 for g in past if g['kind'] == k and kind_by_bag(g['n'], gc) == st)}"
                                                    for k in ["ceiling", "repeat", "searched"]))
    exs = [g for g in past if g["kind"] == "searched" and kind_by_bag(g["n"], gc) == "exchange"]
    print(f"  searched exchange games past 5060: {len(exs)}; best-known delta = the exchanged source (P* unchanged) at "
          f"{sum(gc[g['n'] - 1]['score'] + g['n'] - g['score'] == g['n'] - (g['ustar'] - gc[g['n'] - 1]['ustar']) for g in exs)}")
    for st in ["restrict", "relax", "exchange", "relax*", "half-out", "other"]:
        sel = [g for g in past if g["kind"] == "searched" and kind_by_bag(g["n"], gc) == st]
        if sel:
            ds = sorted(gc[g["n"] - 1]["score"] + g["n"] - g["score"] for g in sel)
            print(f"  {st}: {len(sel)}; best-known delta median {ds[len(ds) // 2]}, quartiles "
                  f"{ds[len(ds) // 4]}..{ds[3 * len(ds) // 4]}")
    sp = [g for g in past if g["layer"] == 2 and g["n"] % 2 == 1]
    print(f"odd two-prime games 5061..10000: {len(sp)}, kinds "
          f"{ {k: sum(g['kind'] == k for g in sp) for k in ['ceiling', 'repeat', 'searched']} }")
    sel = [g for g in past if g["kind"] == "searched"]
    ds = sorted(gc[g["n"] - 1]["score"] + g["n"] - g["score"] for g in sel)
    print(f"searched past 5060: best-known delta quartiles {ds[len(ds) // 10]}, {ds[len(ds) // 4]}, {ds[len(ds) // 2]}, "
          f"{ds[3 * len(ds) // 4]}, {ds[9 * len(ds) // 10]} (10/25/50/75/90%); gap median "
          f"{sorted(g['gap'] for g in sel)[len(sel) // 2]}")
    for dmax in (10, 30, 100, 300, 1000):
        print(f"  best-known delta <= {dmax}: {sum(d <= dmax for d in ds)} of {len(ds)}")
    with open(os.path.join(common.HERE, "past5060.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "kind", "best_known", "delta_best_known", "gap", "rise", "layer", "cofactor", "step"])
        for g in past:
            n = g["n"]
            w.writerow([n, g["kind"], g["score"], gc[n - 1]["score"] + n - g["score"], g["gap"], g["rise"], g["layer"],
                        g["cofactor"], kind_by_bag(n, gc)])


if __name__ == "__main__":
    main()
