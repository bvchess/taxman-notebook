#!/usr/bin/env python3
"""E5: the parity bound's own cascade against the game's, in cell form.

    nice -n 19 python3 -I e5/analyze.py > e5/analyze_out.txt      # from the loops folder, after paritydump

Reads e5/paritydump.jsonl (the prover's example paritydump, see README.md) and the committed chain.  Words are the
study's (study-report.md, Section 1): P = P_0 the largest prime of n, c = n/P, the cell (k, j) = k·P_j; D, A the
recorded change from n - 1 to n (moves given up, moves taken up besides n); rise = delta - delta_PB.  The parity sets:

  I(n-1)   near_game on board n - 1: a heaviest set independent at both parities, nearest the recorded set of n - 1
  I(n)     near_prev on board n: a heaviest set of n nearest I(n-1), the parity bound's own change
  W(n-1)   with_change: the heaviest set of n - 1 holding D and avoiding A
  J        W(n-1) - D + A + n, the game's change applied to it; K(n) the heaviest set of n nearest J

The window is the cells with 0 <= j <= 3 (all rows).  The residual of a set is that of its own instance (P5): empty iff
playable, and for a set independent at both parities the union of its cores, all odd.
"""
import csv
import json
import os
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
import patterns  # noqa: E402
import predict  # noqa: E402

common, spf = predict.common, predict.spf
HERE = os.path.dirname(os.path.abspath(__file__))
WINDOW = 3


def cell(w, pj):
    lab = patterns.label(w, pj)
    return lab


def fmt(ws, pj):
    out = []
    for w in sorted(ws, key=lambda w: (cell(w, pj) is None, cell(w, pj) or (0, 0), w)):
        lab = cell(w, pj)
        out.append(f"({lab[0]},{lab[1]})={w}" if lab else str(w))
    return " ".join(out) or "-"


def in_window(w, pj):
    lab = cell(w, pj)
    return lab is not None and 0 <= lab[1] <= WINDOW


def window_part(ws, pj):
    return {w for w in ws if in_window(w, pj)}


def main():
    rows = [json.loads(t) for t in open(os.path.join(HERE, "paritydump.jsonl")) if t.strip()]
    sets, change = {}, {}
    for r in rows:
        if r["variant"] == "game_change":
            change[r["n"]] = r
        else:
            sets[(r["n"], r["m"], r["variant"])] = set(r["set"])
    settle = {int(r["n"]): r for r in csv.DictReader(open("/home/brian/taxman_work/lab/work/succession/settle.csv"))}
    res = common.results()
    summary = []
    for n in change:
        P = common.factor(n)[-1]
        c = n // P
        pj = patterns.primes_around(P)
        depth = patterns.clean_depth(n)
        s0, s1 = set(res[n - 1]["moves"]), set(res[n]["moves"])
        D, A = s0 - s1, s1 - s0 - {n}
        st = settle[n]
        delta, rise = int(st["delta"]), int(st["rise"])
        ch = change[n]
        pb0, pb1 = ch["pb_before"], ch["pb_after"]
        I0, I1 = sets[(n, n - 1, "near_game")], sets[(n, n, "near_prev")]
        Dp, Ap = I0 - I1, I1 - I0 - {n}
        assert n in I1
        print(f"== {n} = {c}·{P}  P1..P4 = {pj[1]}, {pj[2]}, {pj[3]}, {pj[4]}; clean to depth {depth}; {st['step']}; "
              f"delta {delta}, delta_PB {delta - rise}, rise {rise}")
        print(f"  game    D: {fmt(D, pj)}  |  A: {fmt(A, pj)}   (sum D - sum A = {sum(D) - sum(A)})")
        print(f"  parity  D: {fmt(Dp, pj)}  |  A: {fmt(Ap, pj)}   (sum = {sum(Dp) - sum(Ap)}; I(n-1) -> I(n))")
        full = (Dp, Ap) == (D, A)
        win = (window_part(Dp, pj), window_part(Ap, pj)) == (window_part(D, pj), window_part(A, pj))
        print(f"  equal: whole board {full}, on the window (0 <= j <= {WINDOW}) {win}")
        for m, key in ((n - 1, "plain"), (n, "plain")):
            other = sets[(n, m, "near_game")]
            print(f"  ties: Meet's plain set of {m} differs from the one nearest the game in "
                  f"{len(sets[(n, m, key)] ^ other)} members")
        w0 = sets.get((n, n - 1, "with_change"))
        print(f"  game's change on a heaviest set of n - 1: W(n-1) weighs PB(n-1) {ch['before_with_change'] - pb0:+d}; "
              f"J independent on n: {ch['after_change_independent']}, weighs PB(n) {ch['after_change_value'] - pb1:+d}; "
              f"heaviest set of n with A + n forced and D barred: PB(n) {ch['after_best_with_change'] - pb1:+d}")
        if w0 is not None:
            out0, in0 = I0 - w0, w0 - I0
            if out0 or in0:
                print(f"  at n - 1, the heaviest sets I(n-1) against W(n-1) (what the game's change forbids, worth "
                      f"{sum(out0) - sum(in0)}): I only: {fmt(out0, pj)}  |  W only: {fmt(in0, pj)}")
            J = (w0 - D) | A | {n}
            K = sets[(n, n, "near_change")]
            outk, ink = J - K, K - J
            if outk or ink:
                print(f"  at n, beyond the game's change (worth {sum(ink) - sum(outk)}): J only: {fmt(outk, pj)}  |  "
                      f"K(n) only: {fmt(ink, pj)}")
        for m, I, S in ((n - 1, I0, s0), (n, sets[(n, n, "near_game")], s1)):
            R = common.residual(I, spf)
            print(f"  gap of {m}: PB - opt = {sum(I) - sum(S)}; nearest heaviest set vs the recorded set: "
                  f"parity only {fmt(I - S, pj)}  |  recorded only {fmt(S - I, pj)}")
            print(f"    residual of the heaviest set (its odd cores): {len(R)} members: {fmt(R, pj)}")
        summary.append((n, c, depth, rise, full, win, ch["after_change_independent"],
                        ch["before_with_change"] - pb0, ch["after_change_value"] - pb1))
        print()
    print("== Summary: n, cofactor, clean depth, rise, parity change = game's (whole board, window), game's change "
          "independent on n, W(n-1) - PB(n-1), J - PB(n)")
    for row in summary:
        print("  " + " ".join(map(str, row)))


if __name__ == "__main__":
    main()
