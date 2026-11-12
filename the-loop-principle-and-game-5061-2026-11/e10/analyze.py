#!/usr/bin/env python3
"""E10: the parity bound's change against the game's at the 21P steps 5060 -> 5061, 5018 -> 5019, 3296 -> 3297 and
3506 -> 3507 (study-report.md, Sections 10 and 14), from the prover's example paritydump.

    nice -n 19 python3 -I e10/analyze.py > e10/analyze_out.txt      # from the loops folder, after paritydump

Words as in e5/analyze.py and e5/cores.py.  The recorded set of a board is the committed chain's up to 5060 and the
best-known file's highest score past it (predict.load_best).  D, A: the moves of the recorded set of n - 1 that the
recorded set of n gives up, and those it takes up besides n.  Parity sets (paritydump's variants): I(n-1) the heaviest
set of n - 1 nearest the recorded one; I(n) the heaviest set of n nearest I(n-1); W(n-1) the heaviest set of n - 1
holding D and avoiding A, nearest the recorded one; J = W(n-1) - D + A + n; K(n) the heaviest set of n nearest J.
When W(n-1) is heaviest and J is independent, J weighs PB(n) - rise, and the exchange J -> K is the parity bound's
extra beyond the game's change.  The *defect* of a board is (parity only, recorded only) between the recorded set and
its nearest heaviest set.  A number is labeled k·p, p its largest prime; the window's columns are those of P_j.

The probe applies the extra exchange to the recorded set of n: S(n) - (J - K) + (K - J).  It says whether that set is
independent at both parities and gives an inclusion-minimal core of its own instance (odd when its lists are
independent over GF(2)), with each member's list; if the set is playable, it is a game of n, replayed by the rules.
The circuits of each member of K - J in J (board n) and in W(n-1) (board n - 1) say why it enters only after the step.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e5"))
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import oddcore as oc  # noqa: E402
import patterns  # noqa: E402
import predict  # noqa: E402

common, spf = predict.common, predict.spf
res = common.results()
best = predict.load_best()


def recorded(m):
    return set(res[m]["moves"]) if m <= 5060 else set(best[m]["moves"])


def labeler(n):
    P = common.factor(n)[-1]
    pj = patterns.primes_around(P)
    col = {p: j for j, p in pj.items() if p}

    def lab(w):
        if w == 1:
            return "1"
        p = common.factor(w)[-1]
        j = col.get(p)
        return f"{w}={w // p}·{p}" + (f"(col {j})" if j is not None and -3 <= j <= 3 else "")
    return lab


def fmt(ws, lab):
    return " ".join(lab(w) for w in sorted(ws)) or "-"


def by_prime(ws):
    out = {}
    for w in sorted(ws):
        p = common.factor(w)[-1]
        out.setdefault(p, []).append(w // p)
    return "; ".join(f"{p}: rows {rows}" for p, rows in sorted(out.items(), reverse=True))


def main():
    rows = [json.loads(t) for t in open(os.path.join(HERE, "paritydump.jsonl")) if t.strip()]
    sets, change, forced = {}, {}, {}
    for r in rows:
        if r["variant"] == "game_change":
            change[r["n"]] = r
        elif r["variant"] == "forced":
            forced[(r["n"], r["m"])] = r["can_hold_can_avoid"]
        else:
            sets[(r["n"], r["m"], r["variant"])] = set(r["set"])
    for n in change:
        ch = change[n]
        lab = labeler(n)
        P = common.factor(n)[-1]
        s0, s1 = recorded(n - 1), recorded(n)
        D, A = s0 - s1, s1 - s0 - {n}
        assert sorted(D) == ch["dropped"] and sorted(A) == ch["added"], f"{n}: the recorded sets differ from the dump's"
        pb0, pb1 = ch["pb_before"], ch["pb_after"]
        delta = sum(s0) + n - sum(s1)
        dpb = pb0 + n - pb1
        print(f"== {n} = {'·'.join(map(str, common.factor(n)))}, P = {P}, c = {n // P}; recorded {sum(s0)} -> {sum(s1)}"
              f" ({'chain' if n <= 5060 else 'best-known'}); PB {pb0} -> {pb1}; delta {delta}, delta_PB {dpb}, "
              f"rise {delta - dpb}")
        print(f"  game    D: {fmt(D, lab)}")
        print(f"          A: {fmt(A, lab)}   (sum D - sum A = {sum(D) - sum(A)})")
        I0, I1 = sets[(n, n - 1, "near_game")], sets[(n, n, "near_prev")]
        Dp, Ap = I0 - I1, I1 - I0 - {n}
        print(f"  parity  D: {fmt(Dp, lab)}")
        print(f"          A: {fmt(Ap, lab)}   (sum = {sum(Dp) - sum(Ap)}; I(n-1) -> I(n))")
        print(f"  equal to the game's change: {(Dp, Ap) == (D, A)}; parity only {fmt((Dp - D) | (Ap - A), lab)}; "
              f"game only {fmt((D - Dp) | (A - Ap), lab)}")
        for m in (n - 1, n):
            parts = []
            for x, hold, avoid in forced[(n, m)]:
                kind = "D" if x in D else ("A" if x in A else "n")
                parts.append(f"{kind}{x}:{'all' if not avoid else ('none' if not hold else 'some')}")
            print(f"  heaviest sets of {m} holding each cell: " + " ".join(parts))
        print(f"  game's change on a heaviest set of n - 1: W(n-1) = PB(n-1) {ch['before_with_change'] - pb0:+d}; "
              f"J independent on n: {ch['after_change_independent']}, J = PB(n) {ch['after_change_value'] - pb1:+d}; "
              f"heaviest set of n with A + n forced and D barred: PB(n) {ch['after_best_with_change'] - pb1:+d}")
        W = sets[(n, n - 1, "with_change")]
        if I0 != W:
            print(f"  at n - 1, I(n-1) against W(n-1) (worth {sum(I0) - sum(W)}): I only {fmt(I0 - W, lab)}  |  "
                  f"W only {fmt(W - I0, lab)}")
        J = (W - D) | A | {n}
        K = sets[(n, n, "near_change")]
        out_, in_ = J - K, K - J
        print(f"  beyond the game's change (J -> K, worth {sum(in_) - sum(out_)}):")
        print(f"     out {fmt(out_, lab)}")
        print(f"     in  {fmt(in_, lab)}")
        if out_ or in_:
            print(f"     by column: out {by_prime(out_)}  ||  in {by_prime(in_)}")
        for m, key in ((n - 1, (n, n - 1, "near_game")), (n, (n, n, "near_game"))):
            I, S = sets[key], recorded(m)
            print(f"  defect of {m} (PB - recorded = {sum(I) - sum(S)}): parity only {fmt(I - S, lab)}")
            print(f"        recorded only {fmt(S - I, lab)}")
        for y in sorted(in_):
            for name, m, base in (("J on n", n, J), ("W(n-1) on n - 1", n - 1, W)):
                if y > m:
                    continue
                for parity in (0, 1):
                    c = oc.circuit(m, base - {y}, y, parity) if y in base else oc.circuit(m, base, y, parity)
                    print(f"  circuit of {lab(y)} at parity {parity} in {name}: "
                          + ("none" if c is None else f"{len(c)} members: {fmt(c, lab)}"))
        if out_ or in_:
            if out_ <= s1 and not (in_ & s1):
                probe(n, s1, out_, in_, lab)
            else:
                print(f"  probe: the exchange does not apply to the recorded set of {n} as it stands (out not held: "
                      f"{fmt(out_ - s1, lab)}; in already held: {fmt(in_ & s1, lab)}); applied to what applies:")
                probe(n, s1, out_ & s1, in_ - s1, lab)
        print()


def probe(m, S, out, inn, lab):
    T = (S - set(out)) | set(inn)
    ind, why = oc.independent(m, T)
    print(f"  probe on the recorded set of {m}: - {sorted(out)} + {sorted(inn)} (worth {sum(inn) - sum(out):+d}): "
          f"independent at both parities {ind}")
    core, lists = oc.minimal_core(T)
    if not core:
        order = common.legal_order(T, m, spf)
        print(f"     PLAYABLE: a game of {m} worth {sum(T)}" + (f", replayed: {order is not None}"))
        return
    print(f"     a minimal core, {'odd' if oc.is_odd(lists) else 'not odd'}, {len(core)} members, by column: "
          f"{by_prime(core)}")
    listed = Counter(f for fs in lists.values() for f in fs)
    print(f"     factors its members list, with the number of members listing each: "
          + " ".join(f"{lab(f)}x{k}" for f, k in sorted(listed.items())))


if __name__ == "__main__":
    main()
