#!/usr/bin/env python3
"""The tables of the loops brief, from predict.jsonl (predict.py).

    nice -n 19 python3 -I tables.py > tables_out.txt

A predictor hits a game when its value equals delta(n).  CPU shares are of the 1,745 searched games of 2..5060 (all of
the chain's CPU).  Past 5060 delta is best-known(n - 1) + n - best-known(n), so a hit there is agreement with the
best-known scores, not a proof.
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import predict  # noqa: E402

common = predict.common
HERE = predict.HERE
SEARCHED = "/home/brian/taxman_work/lab/work/succession/searched.csv"
KINDS = ["relax", "restrict", "exchange"]
PREDICTORS = [
    ("shift", "shadow (odd n) or half (even n)"),
    ("shadow", "shadow, odd n"),
    ("half", "half, even n"),
    ("boxmove", "smallest member of C(n) that is a move of S"),
    ("boxpeel", "smallest member y of C(n) and S with S - y + n playable"),
    ("cascade", "a loss or down-shift in C(n), then up-shifts along the columns (chain.py; from 187)"),
    ("xmin", "single-loss rule (any move of S)"),
    ("delta_pb", "parity bound's own shortfall"),
    ("oracle", "delta is the value of some member of C(n)"),
]


def value(r, p):
    if p == "shift":
        return r["shadow"] if r["n"] % 2 else r["half"]
    if p == "oracle":
        return r["delta"] if r["delta_in_cluster"] else None
    return r[p]


def hit(r, p):
    v = value(r, p)
    return v is not None and v == r["delta"]


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "-"


def load():
    rows = predict.load_rows()
    casc = {}
    if os.path.exists(os.path.join(HERE, "chain.jsonl")):
        casc = {x["n"]: x["cascade"] for x in map(json.loads, open(os.path.join(HERE, "chain.jsonl"))) if x}
    for r in rows:
        r["cascade"] = casc.get(r["n"])
    return [r for r in rows if r["range"] == "chain"], [r for r in rows if r["range"] == "past"]


def col_label(w, n):
    """w as k·P_j: P_0 the largest prime of n, P_1 the prime before it, ..., P_-1 the prime after it."""
    q = common.factor(w)[-1]
    P = common.factor(n)[-1]
    k = w // q
    j, p = 0, P
    if q <= P:
        while p > q and j < 12:
            p = predict.prev_prime(p)
            j += 1
    else:
        while p < q and j > -12:
            p += 1
            while not predict.is_prime(p):
                p += 1
            j -= 1
    if p != q:
        return "·".join(str(x) for x in common.factor(w))
    return f"{k}·P{j}" if j >= 0 else f"{k}·P+{-j}"


def table_predictors(chain, past):
    tc = sum(r["cpu"] for r in chain)
    print("== Table A: hit rates of the predictors (hits / games; CPU share of the hits, of all searched CPU)")
    print("predictor | chain all | relax | restrict | exchange | past 5060 all | relax | restrict | exchange")
    for p, desc in PREDICTORS:
        cells = []
        for rows, with_cpu in ((chain, True), (past, False)):
            for k in [None] + KINDS:
                sel = [r for r in rows if k is None or r["step"] == k]
                h = [r for r in sel if hit(r, p)]
                s = f"{len(h)}/{len(sel)}"
                if with_cpu:
                    s += f" ({pct(sum(r['cpu'] for r in h), tc)})"
                cells.append(s)
        print(f"{p} [{desc}] | " + " | ".join(cells))
    print(f"(chain: {len(chain)} searched games, {tc / 3600:,.0f} CPU-hours; past 5060: {len(past)} searched games by "
          f"the current best-known file)")
    done = [r for r in past if r["cascade"] is not None or r["n"] <= max([x["n"] for x in past if x["cascade"]
                                                                          is not None] or [0])]
    if done:
        top = max(r["n"] for r in done)
        cells = []
        for k in [None] + KINDS:
            sel = [r for r in done if k is None or r["step"] == k]
            for p in ("cascade", "boxpeel", "xmin"):
                cells.append(f"{p} {sum(hit(r, p) for r in sel)}/{len(sel)}")
        print(f"cascade past 5060, on the {len(done)} searched games of 5061..{top} that chain.py reached (all, relax, "
              f"restrict, exchange; boxpeel and xmin on the same games): " + "; ".join(cells))
    print()


def check_xmin(chain):
    sc = {int(r["n"]): r for r in csv.DictReader(open(SEARCHED))}
    bad = [r["n"] for r in chain if str(r["xmin"]) != sc[r["n"]]["x_min"] and
           not (r["xmin"] is None and sc[r["n"]]["x_min"] in ("", "None"))]
    print(f"cross-check: xmin here against x_min of searched.csv: {len(chain) - len(bad)} of {len(chain)} agree; "
          f"differ at {bad[:20]}")
    print()


def table_layers(chain, past, p):
    tc = sum(r["cpu"] for r in chain)
    print(f"== Table B: {p} by layer (chain: hits/games, CPU share of the layer's searched CPU that the hits hold; "
          f"past: hits/games)")
    for lay in range(2, 12):
        for k in KINDS:
            sel = [r for r in chain if r["layer"] == lay and r["step"] == k]
            ps = [r for r in past if r["layer"] == lay and r["step"] == k]
            if not sel and not ps:
                continue
            c = sum(r["cpu"] for r in sel)
            h = [r for r in sel if hit(r, p)]
            print(f"  layer {lay} {k}: chain {len(h)}/{len(sel)} ({pct(sum(r['cpu'] for r in h), c)} of the class's "
                  f"CPU; class {pct(c, tc)} of all), past {sum(hit(r, p) for r in ps)}/{len(ps)}")
    print()


def table_cofactors(chain, past):
    print("== Table C: cofactor families (n = c·P, P the largest prime), searched games of both ranges")
    print("A predictor is exact on a family from n0 when it hits every searched game of the family from n0 on "
          "(both ranges); listed when that holds for at least 5 games and n0 <= 5060.")
    allr = sorted(chain + past, key=lambda r: r["n"])
    fam = {}
    for r in allr:
        fam.setdefault(r["cofactor"], []).append(r)
    tc = sum(r["cpu"] for r in chain)
    print("cofactor | steps | chain games (CPU share) | past games | hits chain/past: shift, boxmove, boxpeel, cascade, "
          "xmin, delta_pb | exact (predictor from n0: games covered chain+past; misses before n0)")
    order = sorted(fam, key=lambda c: -sum(r["cpu"] or 0 for r in fam[c]))
    for c in order:
        rows = fam[c]
        ch = [r for r in rows if r["range"] == "chain"]
        pa = [r for r in rows if r["range"] == "past"]
        if len(rows) < 5:
            continue
        steps = sorted({r["step"] for r in rows})
        hs = []
        for p in ("shift", "boxmove", "boxpeel", "cascade", "xmin", "delta_pb"):
            hs.append(f"{sum(hit(r, p) for r in ch)}/{sum(hit(r, p) for r in pa)}")
        exact = []
        for p in ("shift", "boxpeel", "cascade", "xmin", "delta_pb"):
            n0 = None
            for i in range(len(rows)):
                if all(hit(r, p) for r in rows[i:]):
                    n0 = rows[i]["n"]
                    tail = rows[i:]
                    break
            if n0 is not None and len(tail) >= 5 and n0 <= 5060:
                misses = [r["n"] for r in rows if r["n"] < n0 and not hit(r, p)]
                exact.append(f"{p} from {n0}: {sum(r['range'] == 'chain' for r in tail)}+"
                             f"{sum(r['range'] == 'past' for r in tail)}; misses {misses[-6:]}")
        print(f"{c} | {','.join(steps)} | {len(ch)} ({pct(sum(r['cpu'] for r in ch), tc)}) | {len(pa)} | "
              f"{' '.join(hs)} | {'; '.join(exact) if exact else '-'}")
    print()


def table_failures(chain, past, p):
    tc = sum(r["cpu"] for r in chain)
    print(f"== Table D: where {p} fails (value - delta, by step; chain)")
    for k in KINDS:
        sel = [r for r in chain if r["step"] == k and not hit(r, p)]
        miss = sorted((value(r, p) - r["delta"]) if value(r, p) is not None else None for r in sel
                      if value(r, p) is not None)
        none = sum(value(r, p) is None for r in sel)
        if not sel:
            print(f"  {k}: no failures")
            continue
        bands = [(1, 10), (11, 100), (101, 300), (301, 1000), (1001, 10 ** 6)]
        bt = ", ".join(f"{lo}-{hi if hi < 10 ** 6 else ''}: {sum(lo <= m <= hi for m in miss)}" for lo, hi in bands)
        print(f"  {k}: {len(sel)} failures ({pct(sum(r['cpu'] for r in sel), tc)} of all CPU); undefined {none}; "
              f"miss median {miss[len(miss) // 2] if miss else '-'}; negative {sum(m < 0 for m in miss)}; {bt}")
    print()


def table_changes(chain, past):
    print("== Table E: the change from the optimal set of n - 1 to that of n (chain, recorded sets): D the moves "
          "given up, A the moves taken up besides n; delta = sum(D) - sum(A)")
    print("  'in C' = every member of D and A lies in the cluster C(n)")
    tc = sum(r["cpu"] for r in chain)
    for rows, name in ((chain, "chain"), (past, "past")):
        for k in KINDS:
            sel = [r for r in rows if r["step"] == k]
            if not sel:
                continue
            single = [r for r in sel if len(r["dropped"]) == 1 and not r["added"]]
            inC = [r for r in sel if all(x in predict.cluster(r["n"]) for x in r["dropped"] + r["added"])]
            sizes = sorted(len(r["dropped"]) + len(r["added"]) for r in sel)
            cpu = (lambda s: f" ({pct(sum(x['cpu'] for x in s), tc)})") if name == "chain" else (lambda s: "")
            print(f"  {name} {k}: {len(sel)} games; one move given up, none taken: {len(single)}{cpu(single)}; "
                  f"all changes in C(n): {len(inC)}{cpu(inC)}; |D|+|A| median "
                  f"{sizes[len(sizes) // 2]}, 90th percentile {sizes[int(0.9 * (len(sizes) - 1))]}, max {sizes[-1]}")
    print()


def table_parity(chain, past, p):
    tc = sum(r["cpu"] for r in chain)
    print(f"== Table F: {p} against the parity bound (rise = delta - delta_pb = gap(n) - gap(n - 1))")
    for rows, name in ((chain, "chain"), (past, "past")):
        for k in KINDS + [None]:
            sel = [r for r in rows if k is None or r["step"] == k]
            cells = []
            for hv in (True, False):
                for rz in ("=0", ">0", "<0"):
                    s = [r for r in sel if hit(r, p) == hv and
                         ((r["delta"] == r["delta_pb"]) if rz == "=0" else
                          (r["delta"] > r["delta_pb"]) if rz == ">0" else (r["delta"] < r["delta_pb"]))]
                    c = f" {pct(sum(r['cpu'] for r in s), tc)}" if name == "chain" else ""
                    cells.append(f"{len(s)}{c}")
            print(f"  {name} {k or 'all'}: {p} hits & rise =0, >0, <0: {cells[0]}, {cells[1]}, {cells[2]} | misses & "
                  f"rise =0, >0, <0: {cells[3]}, {cells[4]}, {cells[5]}")
        # Is the parity bound's own loss a cluster member?
        cl = sum(r["delta_pb"] in predict.cluster(r["n"]) for r in rows)
        print(f"  {name}: delta_pb is the value of a member of C(n) at {cl} of {len(rows)}; sum of rises "
              f"{sum(r['delta'] - r['delta_pb'] for r in rows):,}")
    print()


def table_detours(chain, past, p):
    """Where p fails, the members of D and A that are cells (k, j) with a row k beyond the cofactor c (k > c, j >= 1):
    numbers that exist only because column j is not clean, the candidate detours."""
    import patterns
    tc = sum(r["cpu"] for r in chain)
    print(f"== Table G: where {p} fails, the change's members in rows beyond c (k > c, column j >= 1)")
    for rows, name in ((chain, "chain"), (past, "past")):
        for k in KINDS:
            sel = [r for r in rows if r["step"] == k and not hit(r, p) and r["n"] >= 187]
            if not sel:
                continue
            with_x, cnt = [], {}
            for r in sel:
                pj = patterns.primes_around(r["P"])
                xs = []
                for w in r["dropped"] + r["added"]:
                    lab = patterns.label(w, pj)
                    if lab and lab[1] >= 1 and lab[0] > r["cofactor"]:
                        xs.append(lab)
                if xs:
                    with_x.append(r)
                for lab in set(xs):
                    key = f"row c + {lab[0] - r['cofactor']}"
                    cnt[key] = cnt.get(key, 0) + 1
            cpu = f" ({pct(sum(r['cpu'] for r in with_x), tc)})" if name == "chain" else ""
            top = sorted(cnt.items(), key=lambda kv: -kv[1])[:6]
            clean = sum(patterns.clean_depth(r["n"]) >= 1 for r in sel)
            print(f"  {name} {k}: {len(sel)} failures from 187, {clean} of them clean to depth 1; with a member in a row "
                  f"beyond c: {len(with_x)}{cpu}; commonest such rows: {top}")
    print()


def table_union(chain, past):
    import patterns
    pat = {}
    for t in open(os.path.join(HERE, "patterns.jsonl")):
        x = json.loads(t)
        pat[x["n"]] = x
    tc = sum(r["cpu"] for r in chain)
    print("== Table H: union of the loop predictors (boxpeel, cascade, the family pattern left out, the previous "
          "pattern), from 187")
    for rows, name, keys in ((chain, "chain", ("modal_loo", "previous")), (past, "past", ("modal", "previous"))):
        for k in KINDS + [None]:
            sel = [r for r in rows if (k is None or r["step"] == k) and r["n"] >= 187]
            h = [r for r in sel if hit(r, "boxpeel") or hit(r, "cascade") or
                 any(pat[r["n"]][q] == r["delta"] for q in keys)]
            cpu = f" ({pct(sum(r['cpu'] for r in h), tc)})" if name == "chain" else ""
            print(f"  {name} {k or 'all'}: {len(h)} of {len(sel)}{cpu}")
    print()


def main():
    chain, past = load()
    check_xmin(chain)
    table_predictors(chain, past)
    best = sys.argv[1] if len(sys.argv) > 1 else "boxpeel"
    table_layers(chain, past, best)
    table_cofactors(chain, past)
    table_failures(chain, past, best)
    table_changes(chain, past)
    table_parity(chain, past, best)
    table_detours(chain, past, best)
    table_union(chain, past)


if __name__ == "__main__":
    main()
