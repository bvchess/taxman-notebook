#!/usr/bin/env python3
"""Column patterns of the change from game n - 1 to game n, and the family laws they give.

    nice -n 19 python3 -I patterns.py > patterns_out.txt      # after predict.py

Words.  P_0 = P is the largest prime of n, P_1 the prime before it, P_2 the one before that, and P_-1 the prime after
P.  A number w is in *column form* when w = k·P_j with P_j the largest prime of w and |j| <= 12; its *label* is (k, j).
D and A are the moves the optimal set of n - 1 gives up and the moves the optimal set of n takes up besides n (from
predict.jsonl: the committed sets to 5060, the best-known sets past it), so delta = sum(D) - sum(A).  A game's *pattern*
is the pair of multisets of labels of D and of A, when every member of D and A is in column form; it is a formula,
delta = sum over D of k·P_j - sum over A of k·P_j, that can be evaluated at any n of the same cofactor.

Family laws.  For a cofactor c (n = c·P), the *modal pattern* is the commonest pattern among the searched games of the
family in 187..5060.  Three predictors of delta from patterns:
  modal_loo   the modal pattern of the other searched games of the family in 187..5060 (the game itself left out),
              if at least 2 of them have it
  modal       the modal pattern of all the family's searched games in 187..5060 (for past 5060; in-sample on the chain)
  previous    the pattern of the last earlier searched game of the family (any range) that has one
"""

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import predict  # noqa: E402

common = predict.common
J = 12


def primes_around(P):
    """{j: P_j} for -J <= j <= J (None where no prime)."""
    out = {0: P}
    p = P
    for j in range(1, J + 1):
        p = predict.prev_prime(p) if p and p > 2 else None
        out[j] = p
    p = P
    for j in range(1, J + 1):
        p += 1
        while not predict.is_prime(p):
            p += 1
        out[-j] = p
    return out


def label(w, pj):
    q = common.factor(w)[-1]
    for j, p in pj.items():
        if p == q:
            return (w // q, j)
    return None


def pattern(r):
    if r["n"] < 187:
        return None
    pj = primes_around(r["P"])
    d = [label(w, pj) for w in r["dropped"]]
    a = [label(w, pj) for w in r["added"]]
    if any(x is None for x in d + a):
        return None
    return (tuple(sorted(d)), tuple(sorted(a)))


def evaluate(pat, n):
    P = common.factor(n)[-1]
    pj = primes_around(P)
    total = 0
    for sign, part in ((1, pat[0]), (-1, pat[1])):
        for k, j in part:
            if pj.get(j) is None:
                return None
            total += sign * k * pj[j]
    return total


def clean_depth(n):
    """The largest j <= J such that every column P_1..P_j holds exactly the rows k <= c, c = n / P: (c + 1)·P_i > n."""
    P = common.factor(n)[-1]
    c = n // P
    pj = primes_around(P)
    d = 0
    for i in range(1, J + 1):
        if pj[i] is None or (c + 1) * pj[i] <= n:
            break
        d = i
    return d


def jmax(pat):
    return max([j for part in pat for (_, j) in part] + [0])


def show(pat):
    def one(part):
        return " + ".join(f"{k}·P{j}" if j >= 0 else f"{k}·P+{-j}" for k, j in part) or "0"
    return f"[{one(pat[0])}] - [{one(pat[1])}]"


def main():
    rows = predict.load_rows()
    rows.sort(key=lambda r: r["n"])
    for r in rows:
        r["pattern"] = pattern(r)
    chain = [r for r in rows if r["range"] == "chain"]
    past = [r for r in rows if r["range"] == "past"]
    tc = sum(r["cpu"] for r in chain)

    print("== Column form of the change sets (games from 187 on)")
    for name, sel in (("chain", [r for r in chain if r["n"] >= 187]), ("past", past)):
        for k in ("relax", "restrict", "exchange", None):
            s = [r for r in sel if k is None or r["step"] == k]
            cf = [r for r in s if r["pattern"] is not None]
            c = (f" ({100 * sum(r['cpu'] for r in cf) / tc:.1f}% of all CPU, of "
                 f"{100 * sum(r['cpu'] for r in s) / tc:.1f}%)") if name == "chain" else ""
            sizes = Counter(len(r["pattern"][0]) + len(r["pattern"][1]) for r in cf)
            cf3 = [r for r in cf if max(abs(j) for part in r["pattern"] for (_, j) in part) <= 3]
            c3 = f" ({100 * sum(r['cpu'] for r in cf3) / tc:.1f}% of all CPU)" if name == "chain" else ""
            print(f"  {name} {k or 'all'}: {len(cf3)} with every member within three primes of P (|j| <= 3){c3}")
            print(f"  {name} {k or 'all'}: {len(cf)} of {len(s)} in column form{c}; sizes |D|+|A| "
                  f"{dict(sorted(sizes.items()))}")
    print()

    fam = {}
    for r in chain:
        if r["n"] >= 187 and r["pattern"] is not None:
            fam.setdefault(r["cofactor"], []).append(r)

    def modal(c, skip=None):
        cnt = Counter(r["pattern"] for r in fam.get(c, []) if r is not skip)
        if not cnt:
            return None, 0
        pat, k = cnt.most_common(1)[0]
        return pat, k

    last = {}
    for r in rows:
        c = r["cofactor"]
        pat, k = modal(c, skip=r)
        r["modal_loo"] = evaluate(pat, r["n"]) if pat is not None and k >= 2 else None
        pat, k = modal(c)
        r["modal"] = evaluate(pat, r["n"]) if pat is not None and k >= 2 else None
        r["previous"] = evaluate(last[c], r["n"]) if c in last else None
        if r["pattern"] is not None:
            last[c] = r["pattern"]

    print("== Pattern predictors (hits = value equals delta), games from 187 on")
    print("predictor | chain all (CPU of hits) | relax | restrict | exchange | past all | relax | restrict | exchange")
    for p in ("modal_loo", "modal", "previous"):
        cells = []
        for name, sel in (("chain", [r for r in chain if r["n"] >= 187]), ("past", past)):
            for k in (None, "relax", "restrict", "exchange"):
                s = [r for r in sel if k is None or r["step"] == k]
                h = [r for r in s if r[p] is not None and r[p] == r["delta"]]
                c = f" ({100 * sum(r['cpu'] for r in h) / tc:.1f}%)" if name == "chain" else ""
                cells.append(f"{len(h)}/{len(s)}{c}")
        print(f"{p} | " + " | ".join(cells))
    ch187 = [r for r in chain if r["n"] >= 187]
    print(f"(chain from 187: {len(ch187)} searched games, {100 * sum(r['cpu'] for r in ch187) / tc:.1f}% of the CPU)")
    either = [r for r in ch187 if any(r[p] == r["delta"] for p in ("modal_loo", "previous"))]
    print(f"chain from 187, modal_loo or previous hits: {len(either)} ({100 * sum(r['cpu'] for r in either) / tc:.1f}%)")
    ep = [r for r in past if any(r[p] == r["delta"] for p in ("modal", "previous"))]
    print(f"past, modal or previous hits: {len(ep)} of {len(past)}")
    print()

    print("== Clean windows: the modal formula of the game's family (fitted on the chain from 187, the game itself left "
          "out on the chain) against the depth to which the columns P_1, P_2, ... hold exactly the rows k <= c")
    for name, sel, key in (("chain", ch187, "modal_loo"), ("past", past, "modal")):
        for clean in (True, False):
            s = []
            for r in sel:
                pat, k = modal(r["cofactor"], skip=r if name == "chain" else None)
                if pat is None or k < 2:
                    continue
                if (clean_depth(r["n"]) >= jmax(pat)) == clean:
                    s.append(r)
            h = [r for r in s if r[key] == r["delta"]]
            c = (f" (hits {100 * sum(r['cpu'] for r in h) / tc:.1f}% of all CPU, of "
                 f"{100 * sum(r['cpu'] for r in s) / tc:.1f}%)") if name == "chain" else ""
            print(f"  {name}, window {'clean' if clean else 'not clean'} to the formula's depth: {len(h)} hits of "
                  f"{len(s)}{c}")
    print()

    print("== The parity form in clean windows: games from 187 with rise = 0 (delta = delta_pb), by the depth to which "
          "the window is clean (columns P_1..P_d hold exactly the rows k <= c)")
    print("step | depth | chain: rise 0 / games (CPU of the games) | past: rise 0 / games")
    for k in ("relax", "restrict", "exchange"):
        for d in range(0, 5):
            ch = [r for r in ch187 if r["step"] == k and min(clean_depth(r["n"]), 4) == d]
            pa = [r for r in past if r["step"] == k and min(clean_depth(r["n"]), 4) == d]
            if not ch and not pa:
                continue
            z = sum(r["delta"] == r["delta_pb"] for r in ch)
            print(f"{k} | {d if d < 4 else '4+'} | {z}/{len(ch)} ({100 * sum(r['cpu'] for r in ch) / tc:.1f}%) | "
                  f"{sum(r['delta'] == r['delta_pb'] for r in pa)}/{len(pa)}")
    for d in (1, 2):
        ch = [r for r in ch187 if clean_depth(r["n"]) >= d and r["step"] != "exchange"]
        z = [r for r in ch if r["delta"] == r["delta_pb"]]
        pa = [r for r in past if clean_depth(r["n"]) >= d and r["step"] != "exchange"]
        print(f"relax and restrict clean to depth >= {d}: chain {len(z)}/{len(ch)} rise 0 "
              f"({100 * sum(r['cpu'] for r in z) / tc:.1f}% of the CPU), cofactors "
              f"{sorted(Counter(r['cofactor'] for r in ch).items())}; past "
              f"{sum(r['delta'] == r['delta_pb'] for r in pa)}/{len(pa)}")
        print(f"  chain games with rise != 0: {[(r['n'], r['delta'] - r['delta_pb']) for r in ch if r not in z]}")
        print(f"  past games with rise != 0 (best-known delta - delta_pb): "
              f"{[(r['n'], r['delta'] - r['delta_pb']) for r in pa if r['delta'] != r['delta_pb']]}")
    print()

    print("== Family laws: the modal pattern of each cofactor with at least 4 searched games of 187..5060 in it")
    print("cofactor | steps | modal pattern | games with it / column-form / searched (chain) | formula hits chain | "
          "past hits / searched | chain CPU share of the family | formula exact from (both ranges) | hits where the "
          "window is clean to the formula's depth / not clean (both ranges)")
    allfam = {}
    for r in rows:
        if r["n"] >= 187:
            allfam.setdefault(r["cofactor"], []).append(r)
    out = []
    for c, frs in fam.items():
        pat, k = modal(c)
        if k < 4:
            continue
        ch = [r for r in allfam[c] if r["range"] == "chain"]
        pa = [r for r in allfam[c] if r["range"] == "past"]
        hits_ch = [r for r in ch if evaluate(pat, r["n"]) == r["delta"]]
        hits_pa = [r for r in pa if evaluate(pat, r["n"]) == r["delta"]]
        seq = allfam[c]
        n0 = None
        for i in range(len(seq)):
            if all(evaluate(pat, r["n"]) == r["delta"] for r in seq[i:]):
                n0 = seq[i]["n"]
                break
        cpu = sum(r["cpu"] for r in ch)
        cl = [r for r in seq if clean_depth(r["n"]) >= jmax(pat)]
        clh = sum(evaluate(pat, r["n"]) == r["delta"] for r in cl)
        ucl = [r for r in seq if clean_depth(r["n"]) < jmax(pat)]
        uch = sum(evaluate(pat, r["n"]) == r["delta"] for r in ucl)
        out.append((cpu, c, sorted({r["step"] for r in seq}), pat, k, len(frs), len(ch), len(hits_ch),
                    sum(r["cpu"] for r in hits_ch), len(hits_pa), len(pa), n0, len(seq), f"{clh}/{len(cl)}",
                    f"{uch}/{len(ucl)}"))
    for cpu, c, steps, pat, k, ncf, nch, hch, chcpu, hpa, npa, n0, nseq, clean, unclean in sorted(out, reverse=True):
        tail = f"{n0} ({sum(1 for r in allfam[c] if r['n'] >= n0)} games)" if n0 is not None else "-"
        print(f"{c} | {','.join(steps)} | {show(pat)} | {k}/{ncf}/{nch} | {hch} ({100 * chcpu / tc:.2f}% CPU) | "
              f"{hpa}/{npa} | {100 * cpu / tc:.2f}% | {tail} | {clean} / {unclean}")
    tot = sum(x[8] for x in out)
    print(f"families listed: {len(out)}; their formula hits hold {100 * tot / tc:.1f}% of the chain's CPU; "
          f"chain hits {sum(x[7] for x in out)}, past hits {sum(x[9] for x in out)} of {sum(x[10] for x in out)}")
    print()

    print("== Deviations from the modal pattern in the 8 largest families by searched games (chain and past): "
          "the members of D and A outside the modal pattern")
    big = sorted(fam, key=lambda c: -len(allfam[c]))[:8]
    for c in big:
        pat, _ = modal(c)
        pd, pa_ = Counter(pat[0]), Counter(pat[1])
        print(f"  cofactor {c}, modal {show(pat)}:")
        shown = 0
        for r in allfam[c]:
            if evaluate(pat, r["n"]) == r["delta"]:
                continue
            pj = primes_around(r["P"])
            lab = lambda w: (lambda x: f"{x[0]}·P{x[1]}" if x and x[1] >= 0 else (f"{x[0]}·P+{-x[1]}" if x else
                             "·".join(map(str, common.factor(w)))))(label(w, pj))
            dl = Counter(label(w, pj) for w in r["dropped"])
            al = Counter(label(w, pj) for w in r["added"])
            extra_d = [lab(w) for w in r["dropped"] if label(w, pj) not in pd or dl[label(w, pj)] > pd[label(w, pj)]]
            extra_a = [lab(w) for w in r["added"] if label(w, pj) not in pa_ or al[label(w, pj)] > pa_[label(w, pj)]]
            miss_d = [f"{k}·P{j}" for (k, j) in pd if (k, j) not in dl]
            miss_a = [f"{k}·P{j}" for (k, j) in pa_ if (k, j) not in al]
            print(f"    {r['n']} ({r['range']}): delta {r['delta']}, formula {evaluate(pat, r['n'])}; extra D {extra_d}, "
                  f"extra A {extra_a}; modal members absent: D {miss_d}, A {miss_a}")
            shown += 1
            if shown >= 14:
                print("    ...")
                break
    with open(os.path.join(predict.HERE, "patterns.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps({"n": r["n"], "range": r["range"], "pattern": r["pattern"], "modal_loo": r["modal_loo"],
                                "modal": r["modal"], "previous": r["previous"]}) + "\n")


if __name__ == "__main__":
    main()
